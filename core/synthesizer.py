"""
GAIA Synthesizer — Perplexity-Style LLM Answer Engine

Takes a user query + ranked sources (canon T1 + web T2-T5) and
produces a streamed, cited, markdown-formatted answer via an LLM.

Provider priority (configure via .env):
  1. OpenAI  (OPENAI_API_KEY)
  2. Anthropic Claude  (ANTHROPIC_API_KEY)
  3. Ollama  (OLLAMA_MODEL, default: mistral — runs 100% locally)
  4. Fallback: rule-based text assembly (no LLM — always works)

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

def build_system_prompt() -> str:
    return """You are GAIA — a constitutional AI answer engine.
You synthesize information from verified sources into clear, accurate, cited answers.

Rules:
- Cite every factual claim with [N] where N is the source number from the provided sources list.
- Use markdown: **bold** for key terms, bullet lists for enumerations, code blocks for code.
- Keep answers concise but complete. Aim for 150-350 words.
- Lead with the direct answer, then provide supporting detail.
- If sources are insufficient, say so clearly rather than speculating.
- Never fabricate citations or claim certainty you don't have.
- Constitutional canon sources (T1) take precedence over web sources."""


def build_user_prompt(query: str, sources: list[dict]) -> str:
    sources_text = "\n".join(
        f"[{i+1}] ({s.get('tier','T4')}) {s.get('title','Source')}\n{s.get('excerpt') or s.get('snippet') or s.get('content','')[:400]}"
        for i, s in enumerate(sources)
    )
    return f"""Sources:
{sources_text}

Question: {query}

Answer (cite inline with [N]):"""


# ------------------------------------------------------------------ #
#  Provider: OpenAI                                                    #
# ------------------------------------------------------------------ #

async def _stream_openai(
    system_prompt: str,
    user_prompt: str,
    model: str = "gpt-4o-mini",
) -> AsyncGenerator[str, None]:
    try:
        from openai import AsyncOpenAI
    except ImportError:
        yield "[OpenAI not installed. Run: pip install openai]"
        return

    client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    try:
        stream = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=True,
            temperature=0.3,
            max_tokens=600,
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
    model: str = "claude-3-haiku-20240307",
) -> AsyncGenerator[str, None]:
    try:
        import anthropic
    except ImportError:
        yield "[Anthropic not installed. Run: pip install anthropic]"
        return

    client = anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    try:
        async with client.messages.stream(
            model=model,
            max_tokens=600,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
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
    model: str = "mistral",
) -> AsyncGenerator[str, None]:
    try:
        import httpx
    except ImportError:
        yield "[httpx not installed. Run: pip install httpx]"
        return

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": True,
    }
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
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
#  Fallback: Rule-Based Assembly (no LLM required)                     #
# ------------------------------------------------------------------ #

async def _stream_fallback(
    query: str,
    sources: list[dict],
) -> AsyncGenerator[str, None]:
    """
    When no LLM provider is configured, assemble a basic cited answer
    from source snippets. Always functional, zero API cost.
    """
    canon_sources = [s for s in sources if s.get("tier") == "T1"]
    web_sources = [s for s in sources if s.get("tier") in ("T2", "T3")]

    if canon_sources:
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
#  Provider Router                                                     #
# ------------------------------------------------------------------ #

def _detect_provider() -> str:
    """Auto-detect which LLM provider to use based on env vars."""
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.environ.get("OLLAMA_MODEL") or os.environ.get("OLLAMA_ENABLED"):
        return "ollama"
    return "fallback"


async def stream_synthesis(
    query: str,
    sources: list[dict],
    provider: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    """
    Main entry point. Streams LLM-synthesized answer chunks.

    Args:
        query:    The user's search question.
        sources:  Ranked list of source dicts with tier, title, excerpt/snippet.
        provider: Force a provider ("openai", "anthropic", "ollama", "fallback").
                  If None, auto-detects from environment.

    Yields:
        str chunks of the answer (for SSE token events)
    """
    if provider is None:
        provider = _detect_provider()

    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(query, sources)

    if provider == "openai":
        model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        async for chunk in _stream_openai(system_prompt, user_prompt, model):
            yield chunk
    elif provider == "anthropic":
        model = os.environ.get("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
        async for chunk in _stream_anthropic(system_prompt, user_prompt, model):
            yield chunk
    elif provider == "ollama":
        model = os.environ.get("OLLAMA_MODEL", "mistral")
        async for chunk in _stream_ollama(system_prompt, user_prompt, model):
            yield chunk
    else:
        async for chunk in _stream_fallback(query, sources):
            yield chunk


async def synthesize_to_string(
    query: str,
    sources: list[dict],
    provider: Optional[str] = None,
) -> str:
    """Non-streaming version — collects full answer as a string."""
    chunks = []
    async for chunk in stream_synthesis(query, sources, provider):
        chunks.append(chunk)
    return "".join(chunks)
