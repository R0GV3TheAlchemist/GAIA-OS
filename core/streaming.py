"""
GAIA Streaming Response Engine
Governs: C21 (Interface Grammar), C44 (Programming Languages Doctrine)

Purpose: Server-Sent Events (SSE) streaming for token-by-token response delivery.
This gives GAIA the Perplexity-feel: responses arrive live, not in a block.

Architecture:
- FastAPI endpoint yields SSE events
- Each event carries: token, canon_citation, epistemic_label
- Frontend consumes SSE stream and renders inline citation cards
- Criticality monitor is consulted per response to flag drift

Resilience features (v2):
- Event IDs: every event carries id: N so EventSource can resume
  from the last received token after a dropped connection, using
  the Last-Event-ID request header on reconnect.
- Heartbeat: a SSE comment is emitted before inference starts so
  proxies and load balancers do not close the connection while
  waiting for slow models (e.g. qwen2.5:32b) to produce token 0.
"""

import asyncio
import json
import logging
from typing import AsyncGenerator, Optional
from dataclasses import dataclass

from core.criticality_monitor import get_monitor, CriticalityState
from core.noosphere import get_noosphere

logger = logging.getLogger("gaia.streaming")


@dataclass
class StreamToken:
    text: str
    is_final: bool = False
    canon_citation: Optional[str] = None    # e.g. "C27", "C42"
    epistemic_label: Optional[str] = None  # e.g. "ESTABLISHED", "EXPERIMENTAL"
    noosphere_resonance: Optional[str] = None  # e.g. "Resonates with 5 sessions [C43]"
    criticality_state: Optional[str] = None    # current processing state


def format_sse_event(token: StreamToken, event_id: Optional[int] = None) -> str:
    """
    Format a StreamToken as a Server-Sent Events data line.

    If event_id is provided, an `id:` field is prepended so the
    browser EventSource can track the last received event and send
    Last-Event-ID on reconnect, enabling resumable streams.

    Frontend parses the JSON payload for rendering.
    """
    payload = {
        "text": token.text,
        "is_final": token.is_final,
    }
    if token.canon_citation:
        payload["canon_citation"] = token.canon_citation
    if token.epistemic_label:
        payload["epistemic_label"] = token.epistemic_label
    if token.noosphere_resonance:
        payload["noosphere_resonance"] = token.noosphere_resonance
    if token.criticality_state:
        payload["criticality_state"] = token.criticality_state

    id_line = f"id: {event_id}\n" if event_id is not None else ""
    return f"{id_line}data: {json.dumps(payload)}\n\n"


async def stream_gaia_response(
    response_text: str,
    canon_citations: Optional[list[str]] = None,
    topic_cluster: Optional[str] = None,
    token_delay_ms: int = 15,
) -> AsyncGenerator[str, None]:
    """
    Stream a GAIA response token by token via SSE.

    Each token is yielded as an SSE event with:
    - A sequential event ID for resumable reconnection
    - The text fragment
    - Any canon citation relevant to this fragment
    - Epistemic label if applicable
    - Noosphere resonance if the topic has collective patterns
    - Current criticality state

    A heartbeat comment is emitted first to prevent proxy timeouts
    while waiting for the model to produce its first token.

    Args:
        response_text: Full response text to stream
        canon_citations: List of C-series doc IDs cited in this response
        topic_cluster: Topic for noosphere resonance lookup
        token_delay_ms: Milliseconds between tokens (default 15ms for natural feel)
    """
    monitor = get_monitor()
    noosphere = get_noosphere()

    # Heartbeat: keeps the connection alive through proxy/LB idle timeouts
    # while the model is generating. SSE comments are invisible to EventSource.
    yield ": heartbeat\n\n"

    # Check noosphere resonance for this topic
    resonance_label = None
    if topic_cluster:
        resonance_label = noosphere.get_resonance_label(topic_cluster)

    # Current criticality state
    crit_state = monitor.get_current_state().value

    # Split response into tokens (simple word-level for Phase 1)
    # Phase 2: replace with actual tokenizer from the inference model
    words = response_text.split(" ")

    for i, word in enumerate(words):
        is_final = (i == len(words) - 1)

        # Attach citation to first token of response, and to final token
        citation = None
        if canon_citations:
            if i == 0 or is_final:
                citation = ", ".join(f"[{c}]" for c in canon_citations)

        token = StreamToken(
            text=word + (" " if not is_final else ""),
            is_final=is_final,
            canon_citation=citation,
            noosphere_resonance=resonance_label if i == 0 else None,
            criticality_state=crit_state if i == 0 else None,
        )

        yield format_sse_event(token, event_id=i)
        await asyncio.sleep(token_delay_ms / 1000.0)

    # Final done event — event_id is len(words) so it sorts after all tokens
    done_token = StreamToken(
        text="",
        is_final=True,
        criticality_state=monitor.get_current_state().value,
    )
    yield format_sse_event(done_token, event_id=len(words))
    logger.debug(f"[streaming] Response streamed: {len(words)} tokens, topic={topic_cluster}")


async def stream_error(error_message: str, error_code: str = "GAIA_ERROR") -> AsyncGenerator[str, None]:
    """
    Stream an error event to the frontend.
    Errors are never suppressed — they are surfaced with their error code.
    Error events use event_id=0 (single event, no resume semantics needed).
    """
    payload = {
        "error": True,
        "error_code": error_code,
        "message": error_message,
        "is_final": True,
    }
    yield format_sse_event(
        StreamToken(text="", is_final=True),
        event_id=0,
    )
    # Yield the actual error payload as a separate data line
    yield f"data: {json.dumps(payload)}\n\n"
