"""
tests/test_streaming.py
Full pytest suite for core/streaming.py.

Tests every public symbol and both v2 resilience features:
  - SSE event IDs for resumable streams
  - Heartbeat comment to prevent proxy/sidecar timeouts

All external dependencies (criticality_monitor, noosphere) are
stubbed with unittest.mock so the suite runs fully offline.
"""

import json
import pytest
from unittest.mock import MagicMock, patch

from core.streaming import (
    StreamToken,
    format_sse_event,
    stream_gaia_response,
    stream_error,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

async def collect(async_gen) -> list[str]:
    """Drain an async generator into a plain list."""
    results = []
    async for item in async_gen:
        results.append(item)
    return results


def parse_data_event(raw: str) -> dict:
    """Extract the JSON payload from a 'data: {...}\\n\\n' SSE line."""
    for line in raw.splitlines():
        if line.startswith("data: "):
            return json.loads(line[6:])
    raise ValueError(f"No data: line found in SSE event: {raw!r}")


def get_id_line(raw: str) -> str | None:
    """Return the 'id: N' line from an SSE event, or None if absent."""
    for line in raw.splitlines():
        if line.startswith("id: "):
            return line
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Shared mock fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def mock_monitor():
    """Stub criticality_monitor so tests run without the full GAIA runtime."""
    mock = MagicMock()
    mock.get_current_state.return_value.value = "NOMINAL"
    with patch("core.streaming.get_monitor", return_value=mock):
        yield mock


@pytest.fixture(autouse=True)
def mock_noosphere():
    """Stub noosphere so tests run without ChromaDB or vector store."""
    mock = MagicMock()
    mock.get_resonance_label.return_value = None
    with patch("core.streaming.get_noosphere", return_value=mock):
        yield mock


# ─────────────────────────────────────────────────────────────────────────────
# format_sse_event()
# ─────────────────────────────────────────────────────────────────────────────

class TestFormatSseEvent:

    def test_basic_payload_shape(self):
        token = StreamToken(text="hello", is_final=False)
        raw = format_sse_event(token)
        payload = parse_data_event(raw)
        assert payload["text"] == "hello"
        assert payload["is_final"] is False

    def test_ends_with_double_newline(self):
        token = StreamToken(text="x", is_final=False)
        raw = format_sse_event(token)
        assert raw.endswith("\n\n")

    def test_optional_fields_absent_when_none(self):
        token = StreamToken(text="hi", is_final=False)
        raw = format_sse_event(token)
        payload = parse_data_event(raw)
        assert "canon_citation" not in payload
        assert "epistemic_label" not in payload
        assert "noosphere_resonance" not in payload
        assert "criticality_state" not in payload

    def test_optional_fields_present_when_set(self):
        token = StreamToken(
            text="hi",
            is_final=False,
            canon_citation="C27",
            epistemic_label="ESTABLISHED",
            noosphere_resonance="Resonates with 3 sessions",
            criticality_state="NOMINAL",
        )
        raw = format_sse_event(token)
        payload = parse_data_event(raw)
        assert payload["canon_citation"] == "C27"
        assert payload["epistemic_label"] == "ESTABLISHED"
        assert payload["noosphere_resonance"] == "Resonates with 3 sessions"
        assert payload["criticality_state"] == "NOMINAL"

    # ── v2: Event ID tests ────────────────────────────────────────────────────────────────

    def test_no_event_id_by_default(self):
        """event_id=None must not produce an id: line."""
        token = StreamToken(text="hi", is_final=False)
        raw = format_sse_event(token)
        assert get_id_line(raw) is None

    def test_event_id_zero_produces_id_line(self):
        token = StreamToken(text="hi", is_final=False)
        raw = format_sse_event(token, event_id=0)
        assert get_id_line(raw) == "id: 0"

    def test_event_id_positive_produces_id_line(self):
        token = StreamToken(text="hi", is_final=False)
        raw = format_sse_event(token, event_id=42)
        assert get_id_line(raw) == "id: 42"

    def test_id_line_appears_before_data_line(self):
        """SSE spec: id: must precede data: in the event block."""
        token = StreamToken(text="hi", is_final=False)
        raw = format_sse_event(token, event_id=7)
        lines = [l for l in raw.splitlines() if l.strip()]
        id_pos = next(i for i, l in enumerate(lines) if l.startswith("id:"))
        data_pos = next(i for i, l in enumerate(lines) if l.startswith("data:"))
        assert id_pos < data_pos


# ─────────────────────────────────────────────────────────────────────────────
# stream_gaia_response()
# ─────────────────────────────────────────────────────────────────────────────

class TestStreamGaiaResponse:

    @pytest.mark.asyncio
    async def test_first_event_is_heartbeat(self):
        """v2: heartbeat comment must be the very first yield."""
        events = await collect(
            stream_gaia_response("hello world", token_delay_ms=0)
        )
        assert events[0] == ": heartbeat\n\n"

    @pytest.mark.asyncio
    async def test_sequential_event_ids(self):
        """After the heartbeat, each token event must carry a sequential id."""
        events = await collect(
            stream_gaia_response("one two three", token_delay_ms=0)
        )
        # events[0] = heartbeat, events[1..N] = tokens, events[-1] = done
        token_events = [e for e in events[1:] if not e.startswith(":")]
        for expected_id, raw in enumerate(token_events):
            id_line = get_id_line(raw)
            assert id_line == f"id: {expected_id}", (
                f"Expected id: {expected_id}, got {id_line!r} in {raw!r}"
            )

    @pytest.mark.asyncio
    async def test_final_done_event_id_equals_word_count(self):
        """Done event id must be len(words) — sorts after all token IDs."""
        text = "alpha beta gamma"
        word_count = len(text.split())
        events = await collect(stream_gaia_response(text, token_delay_ms=0))
        done_event = events[-1]
        assert get_id_line(done_event) == f"id: {word_count}"

    @pytest.mark.asyncio
    async def test_single_word_produces_at_least_three_events(self):
        """
        Single word → heartbeat + ≥1 BPE token event(s) + 1 done event ≥ 3 total.

        Under BPE (tiktoken cl100k_base) a single English word may tokenize
        into multiple subword tokens (e.g. 'GAIA' → ['GA', 'IA']).  We
        assert the minimum structural invariants rather than a fixed count:
          - at least 3 events total
          - first event is the heartbeat
          - last data event is the done sentinel (is_final=True)
          - concatenating all non-final token texts reconstructs the original
        """
        text = "GAIA"
        events = await collect(
            stream_gaia_response(text, token_delay_ms=0)
        )
        # Structural minimum: heartbeat + ≥1 token + done
        assert len(events) >= 3
        assert events[0] == ": heartbeat\n\n"
        data_events = [parse_data_event(e) for e in events if e.startswith("data:")]
        assert data_events[-1]["is_final"] is True
        # Lossless reconstruction
        reconstructed = "".join(d["text"] for d in data_events[:-1])
        assert reconstructed == text

    @pytest.mark.asyncio
    async def test_token_count_matches_word_count_plus_done(self):
        text = "the quick brown fox"
        word_count = len(text.split())  # 4
        events = await collect(stream_gaia_response(text, token_delay_ms=0))
        # heartbeat + word_count tokens + 1 done
        assert len(events) == 1 + word_count + 1

    @pytest.mark.asyncio
    async def test_is_final_only_on_done_event(self):
        events = await collect(
            stream_gaia_response("one two three", token_delay_ms=0)
        )
        data_events = [parse_data_event(e) for e in events if e.startswith("data:")]
        # All except the last should have is_final=False
        for event in data_events[:-1]:
            assert event["is_final"] is False
        assert data_events[-1]["is_final"] is True

    @pytest.mark.asyncio
    async def test_canon_citation_on_first_and_last_tokens_only(self):
        events = await collect(
            stream_gaia_response(
                "alpha beta gamma delta",
                canon_citations=["C01", "C21"],
                token_delay_ms=0,
            )
        )
        data_events = [
            parse_data_event(e) for e in events if e.startswith("data:")
        ]
        # First token (index 0) should have citation
        assert "canon_citation" in data_events[0]
        # Middle tokens (index 1, 2) should NOT have citation
        assert "canon_citation" not in data_events[1]
        assert "canon_citation" not in data_events[2]
        # Final done event (last) should have citation
        assert "canon_citation" in data_events[-1]

    @pytest.mark.asyncio
    async def test_no_citation_when_none_provided(self):
        events = await collect(
            stream_gaia_response("hello world", token_delay_ms=0)
        )
        data_events = [parse_data_event(e) for e in events if e.startswith("data:")]
        for event in data_events:
            assert "canon_citation" not in event

    @pytest.mark.asyncio
    async def test_bpe_tokens_reconstruct_correctly(self):
        """
        BPE (cl100k_base) tokenization: the space is part of the *following*
        token (e.g. 'hello world' → ['hello', ' world']), not appended to
        the prior token.  Assert that joining all non-final token texts
        losslessly reconstructs the original string regardless of how the
        encoder splits it.
        """
        text = "hello world"
        events = await collect(
            stream_gaia_response(text, token_delay_ms=0)
        )
        data_events = [parse_data_event(e) for e in events if e.startswith("data:")]
        token_texts = [d["text"] for d in data_events[:-1]]
        assert "".join(token_texts) == text

    @pytest.mark.asyncio
    async def test_noosphere_resonance_on_first_token_only(self, mock_noosphere):
        mock_noosphere.get_resonance_label.return_value = "Resonates with 4 sessions [C43]"
        events = await collect(
            stream_gaia_response("one two three", topic_cluster="alchemy", token_delay_ms=0)
        )
        data_events = [parse_data_event(e) for e in events if e.startswith("data:")]
        assert "noosphere_resonance" in data_events[0]
        assert "noosphere_resonance" not in data_events[1]


# ─────────────────────────────────────────────────────────────────────────────
# stream_error()
# ─────────────────────────────────────────────────────────────────────────────

class TestStreamError:

    @pytest.mark.asyncio
    async def test_yields_exactly_two_events(self):
        events = await collect(stream_error("something went wrong"))
        assert len(events) == 2

    @pytest.mark.asyncio
    async def test_second_event_is_error_payload(self):
        events = await collect(stream_error("something went wrong"))
        payload = parse_data_event(events[1])
        assert payload["error"] is True
        assert payload["is_final"] is True
        assert payload["message"] == "something went wrong"

    @pytest.mark.asyncio
    async def test_default_error_code(self):
        events = await collect(stream_error("oops"))
        payload = parse_data_event(events[1])
        assert payload["error_code"] == "GAIA_ERROR"

    @pytest.mark.asyncio
    async def test_custom_error_code_preserved(self):
        events = await collect(stream_error("oops", error_code="CANON_VIOLATION"))
        payload = parse_data_event(events[1])
        assert payload["error_code"] == "CANON_VIOLATION"

    @pytest.mark.asyncio
    async def test_first_event_has_event_id_zero(self):
        """First event of stream_error must carry id: 0."""
        events = await collect(stream_error("oops"))
        assert get_id_line(events[0]) == "id: 0"
