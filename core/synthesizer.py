"""
GAIA Synthesizer — LLM Answer Engine

Takes a user query + ranked sources (canon T1 + web T2-T5) and
produces a streamed, cited, markdown-formatted answer via an LLM.

Provider priority (configure via .env):
  1. Perplexity  (PERPLEXITY_API_KEY)   — sonar-pro, live web + citations
  2. OpenAI      (OPENAI_API_KEY)        — gpt-4o-mini (or OPENAI_MODEL)
  3. Anthropic   (ANTHROPIC_API_KEY)     — claude-3-haiku (or ANTHROPIC_MODEL)
  4. Ollama      (OLLAMA_MODEL)          — mistral, runs 100% locally
  5. Fallback    — rule-based text assembly (no LLM, always works)

Citation format: [1], [2], [3] inline, matching sources list index.
Streaming: yields token chunks via async generator for SSE.

Canon Ref: C20 (Source Triage), C21 (Interface & Shell Grammar)
"""

import asyncio
import json
import os
from typing import AsyncGenerator, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ------------------------------------------------------------------ #
#  System Prompt Builder                                               #
# ------------------------------------------------------------------ #

def build_system_prompt(
    gaian_prompt: Optional[str] = None,
    conversation_context: Optional[str] = None,
) -> str:
    """
    Build the system prompt. If a GAIAN is active, use its personality
    and identity as the base. Otherwise use the default GAIA voice.
    """
    if gaian_prompt:
        base = gaian_prompt
    else:
        base = """You are GAIA — a constitutional AI companion and answer engine.
You are grounded, curious, and warm. You speak clearly and directly.
You care about truth, about the person you're speaking with, and about the world.
You are not a search engine — you are a thinking companion who happens to have access to sources."""

    citation_rules = """

Answer guidelines:
- Respond naturally and conversationally, as if thinking alongside the person.
- Cite factual claims with [N] where N matches the source number provided.
- Use **bold** for key terms, bullet lists for enumerations.
- For casual messages (greetings, thanks, simple chat), respond warmly and briefly without citations.
- For knowledge questions, lead with the direct answer then provide depth.
- If sources are insufficient, say so honestly and share what you do know.
- Never fabricate citations. Constitutional canon sources (T1) take precedence.
- Aim for 100-400 words depending on question complexity."""

    context_block = ""
    if conversation_context:
        context_block = f"\n\n{conversation_context}"

    return base + citation_rules + context_block


def build_user_prompt(query: str, sources: list[dict]) -> str:
    if not sources:
        return f"Question: {query}\n\nAnswer:"

    sources_text = "\n".join(
        f"[{i+1}] ({s.get('tier','T4')}) {s.get('title','Source')}\n{s.get('excerpt') or s.get('snippet') or s.get('content','')[:400]}"
        for i, s in enumerate(sources)
    )
    return f"""Sources:
{sources_text}

Question: {query}

Answer (cite inline with [N]):"""


# ------------------------------------------------------------------ #
#  Provider: Perplexity  (sonar-pro — live web search + citations)    #
# ------------------------------------------------------------------ #

async def _stream_perplexity(
    system_prompt: str,
    user_prompt: str,
    conversation_history: Optional[list[dict]] = None,
    model: str = "sonar-pro",
) -> AsyncGenerator[str, None]:
    """
    Perplexity Search API — OpenAI-compatible endpoint.
    Yields streamed token chunks. Perplexity appends live web citations
    automatically; these arrive in the final non-streamed chunk's
    `citations` field which we expose via a trailing [SOURCES] block.

    Env vars:
        PERPLEXITY_API_KEY  — required
        PERPLEXITY_MODEL    — optional, default: sonar-pro
                              options: sonar, sonar-pro, sonar-reasoning-pro
    """
    try:
        from openai import AsyncOpenAI
    except ImportError:
        yield "[Perplexity unavailable: openai package not installed. Run: pip install openai]"
        return

    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        yield "[Perplexity unavailable: PERPLEXITY_API_KEY not set]"
        return

    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://api.perplexity.ai",
    )

    messages = [{"role": "system", "content": system_prompt}]
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_prompt})

    try:
        stream = await client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            temperature=0.4,
            max_tokens=800,
        )

        citations: list[str] = []
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
            # Perplexity exposes citations on the final chunk
            if hasattr(chunk, "citations") and chunk.citations:
                citations = chunk.citations

        # Append citations as a clean source block if present
        if citations:
            yield "\n\n**Sources:**\n"
            for i, url in enumerate(citations, 1):
                yield f"[{i}] {url}\n"

    except Exception as e:
        yield f"[Perplexity error: {str(e)[:200]}]"


# ------------------------------------------------------------------ #
#  Provider: OpenAI                                                    #
# ------------------------------------------------------------------ #

async def _stream_openai(
    system_prompt: str,
    user_prompt: str,
    conversation_history: Optional[list[dict]] = None,
    model: str = "gpt-4o-mini",
) -> AsyncGenerator[str, None]:
    try:
        from openai import AsyncOpenAI
    except ImportError:
        yield "[OpenAI not installed. Run: pip install openai]"
        return

    client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    messages = [{"role": "system", "content": system_prompt}]
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_prompt})

    try:
        stream = await client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            temperature=0.4,
            max_tokens=700,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
    except Exception as e:
        yield f"[OpenAI error: {str(e)[:120]}]"


# ------------------------------------------------------------------ #
#  Provider: Anthropic Claude                                          #
# ------------------------------------------------------------------ #

async def _stream_anthropic(
    system_prompt: str,
    user_prompt: str,
    conversation_history: Optional[list[dict]] = None,
    model: str = "claude-3-haiku-20240307",
) -> AsyncGenerator[str, None]:
    try:
        import anthropic
    except ImportError:
        yield "[Anthropic not installed. Run: pip install anthropic]"
        return

    client = anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    messages = []
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_prompt})

    try:
        async with client.messages.stream(
            model=model,
            max_tokens=700,
            system=system_prompt,
            messages=messages,
        ) as stream:
            async for text in stream.text_stream:
                yield text
    except Exception as e:
        yield f"[Anthropic error: {str(e)[:120]}]"


# ------------------------------------------------------------------ #
#  Provider: Ollama (local)                                            #
# ------------------------------------------------------------------ #

async def _stream_ollama(
    system_prompt: str,
    user_prompt: str,
    conversation_history: Optional[list[dict]] = None,
    model: str = "mistral",
) -> AsyncGenerator[str, None]:
    try:
        import httpx
    except ImportError:
        yield "[httpx not installed. Run: pip install httpx]"
        return

    messages = [{"role": "system", "content": system_prompt}]
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_prompt})

    payload = {"model": model, "messages": messages, "stream": True}
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                "http://localhost:11434/api/chat",
                json=payload,
            ) as response:
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        text = data.get("message", {}).get("content", "")
                        if text:
                            yield text
                        if data.get("done"):
                            break
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        yield f"[Ollama error: {str(e)[:120]}. Is Ollama running? Try: ollama serve]"


# ------------------------------------------------------------------ #
#  Fallback: Rule-Based Assembly                                       #
# ------------------------------------------------------------------ #

async def _stream_fallback(
    query: str,
    sources: list[dict],
) -> AsyncGenerator[str, None]:
    canon_sources = [s for s in sources if s.get("tier") == "T1"]

    if not sources:
        intro = f"I hear you asking about **{query}**. Let me think on that...\n\n"
    elif canon_sources:
        intro = f"Based on GAIA constitutional sources, here is what I found about **{query}**:\n\n"
    else:
        intro = f"Here is what I found about **{query}** from web sources:\n\n"

    for word in intro.split(" "):
        yield word + " "
        await asyncio.sleep(0.02)

    for i, src in enumerate(sources[:4]):
        snippet = src.get("excerpt") or src.get("snippet") or src.get("content") or ""
        if snippet:
            line = f"{snippet[:200].strip()} [{i+1}] "
            for word in line.split(" "):
                yield word + " "
                await asyncio.sleep(0.015)
            yield "\n\n"
            await asyncio.sleep(0.05)


# ------------------------------------------------------------------ #
#  Provider Detection                                                  #
# ------------------------------------------------------------------ #

def _detect_provider() -> str:
    if os.environ.get("PERPLEXITY_API_KEY"):
        return "perplexity"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.environ.get("OLLAMA_MODEL") or os.environ.get("OLLAMA_ENABLED"):
        return "ollama"
    return "fallback"


# ------------------------------------------------------------------ #
#  Main Entry Point                                                    #
# ------------------------------------------------------------------ #

async def stream_synthesis(
    query: str,
    sources: list[dict],
    provider: Optional[str] = None,
    gaian_prompt: Optional[str] = None,
    conversation_history: Optional[list[dict]] = None,
    conversation_context: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    """
    Main entry point. Streams LLM-synthesized answer chunks.

    Args:
        query:                 The user's question.
        sources:               Ranked source dicts (tier, title, excerpt/snippet).
        provider:              Force provider override. Auto-detects if None.
        gaian_prompt:          GAIAN system prompt (identity + personality).
        conversation_history:  Prior turns as [{role, content}] for context.
        conversation_context:  Optional text summary of recent conversation.

    Yields:
        str chunks of the answer (for SSE token events)
    """
    if provider is None:
        provider = _detect_provider()

    system_prompt = build_system_prompt(gaian_prompt, conversation_context)
    user_prompt = build_user_prompt(query, sources)

    if provider == "perplexity":
        model = os.environ.get("PERPLEXITY_MODEL", "sonar-pro")
        async for chunk in _stream_perplexity(system_prompt, user_prompt, conversation_history, model):
            yield chunk
    elif provider == "openai":
        model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        async for chunk in _stream_openai(system_prompt, user_prompt, conversation_history, model):
            yield chunk
    elif provider == "anthropic":
        model = os.environ.get("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
        async for chunk in _stream_anthropic(system_prompt, user_prompt, conversation_history, model):
            yield chunk
    elif provider == "ollama":
        model = os.environ.get("OLLAMA_MODEL", "mistral")
        async for chunk in _stream_ollama(system_prompt, user_prompt, conversation_history, model):
            yield chunk
    else:
        async for chunk in _stream_fallback(query, sources):
            yield chunk


async def synthesize_to_string(
    query: str,
    sources: list[dict],
    provider: Optional[str] = None,
    gaian_prompt: Optional[str] = None,
    conversation_history: Optional[list[dict]] = None,
) -> str:
    chunks = []
    async for chunk in stream_synthesis(query, sources, provider, gaian_prompt, conversation_history):
        chunks.append(chunk)
    return "".join(chunks)
