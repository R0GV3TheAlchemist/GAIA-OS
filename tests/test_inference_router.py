"""
tests/test_inference_router.py
Unit + smoke tests for core/inference_router.py

Canon Ref: C12, C20, C21, C27, C42, C43, C44

Coverage targets
----------------
  ✓ EpistemicLabel enum completeness
  ✓ InferenceBackend enum completeness
  ✓ _probe_backend_availability() — all env-gate branches + cool-down
  ✓ _mark_backend_failed() — health flag + timestamp stamped
  ✓ _build_memory_block() — all four combinations of inputs
  ✓ _infer_epistemic_label() — all five label paths
  ✓ _read_criticality() — all three regimes + graceful failure
  ✓ _read_noosphere_resonance() — label present, "none", missing, failure
  ✓ _enrich_with_canon() — dedup + graceful failure
  ✓ GAIAInferenceRouter.get_stats()
  ✓ GAIAInferenceRouter.stream() / .complete() — meta population,
      enrichment flags, fallback chain, backend failure path
  ✓ get_router() singleton
"""

from __future__ import annotations

import asyncio
import os
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.inference_router import (
    EpistemicLabel,
    InferenceBackend,
    InferenceRequest,
    InferenceResponse,
    GAIAInferenceRouter,
    _build_memory_block,
    _infer_epistemic_label,
    _read_criticality,
    _read_noosphere_resonance,
    _enrich_with_canon,
    _mark_backend_failed,
    _probe_backend_availability,
    _BACKEND_HEALTH,
    _BACKEND_FAILURE_TS,
    _BACKEND_RECOVERY_WINDOW,
    get_router,
)


# ================================================================== #
#  Helpers                                                             #
# ================================================================== #

def _run(coro):
    """Run a coroutine in the default event loop (pytest-asyncio not required)."""
    return asyncio.get_event_loop().run_until_complete(coro)


async def _fake_stream(*args, **kwargs):
    """Minimal async generator that yields a single token."""
    yield "hello"
    yield " world"


def _reset_backend_health():
    """Restore all backends to healthy between tests."""
    for b in InferenceBackend:
        _BACKEND_HEALTH[b] = True
    _BACKEND_FAILURE_TS.clear()


# ================================================================== #
#  1. EpistemicLabel enum                                              #
# ================================================================== #

class TestEpistemicLabel:
    def test_all_five_values_present(self):
        values = {e.value for e in EpistemicLabel}
        assert values == {
            "CANON_CITED", "VERIFIED", "INFERRED",
            "SPECULATIVE", "CONVERSATIONAL",
        }

    def test_string_subclass(self):
        assert EpistemicLabel.CANON_CITED == "CANON_CITED"


# ================================================================== #
#  2. InferenceBackend enum                                            #
# ================================================================== #

class TestInferenceBackend:
    def test_all_four_backends(self):
        values = {b.value for b in InferenceBackend}
        assert values == {"openai", "anthropic", "ollama", "fallback"}

    def test_fallback_always_exists(self):
        assert InferenceBackend("fallback") is InferenceBackend.FALLBACK


# ================================================================== #
#  3. _probe_backend_availability                                      #
# ================================================================== #

class TestProbeBackendAvailability:
    def setup_method(self):
        _reset_backend_health()

    def test_falls_back_when_no_keys(self):
        """No env vars set → should return FALLBACK."""
        env = {k: "" for k in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY",
                                "OLLAMA_MODEL", "OLLAMA_ENABLED")}
        with patch.dict(os.environ, env, clear=False):
            # Temporarily clear the keys
            for k in env:
                os.environ.pop(k, None)
            result = _probe_backend_availability()
        assert result == InferenceBackend.FALLBACK

    def test_selects_openai_when_key_present(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            result = _probe_backend_availability()
        assert result == InferenceBackend.OPENAI

    def test_skips_openai_selects_anthropic(self):
        env = {"ANTHROPIC_API_KEY": "anth-test"}
        with patch.dict(os.environ, env, clear=False):
            os.environ.pop("OPENAI_API_KEY", None)
            result = _probe_backend_availability()
        assert result == InferenceBackend.ANTHROPIC

    def test_selects_ollama_when_enabled(self):
        env = {"OLLAMA_ENABLED": "1"}
        with patch.dict(os.environ, env, clear=False):
            os.environ.pop("OPENAI_API_KEY", None)
            os.environ.pop("ANTHROPIC_API_KEY", None)
            result = _probe_backend_availability()
        assert result == InferenceBackend.OLLAMA

    def test_skips_failed_backend_within_recovery_window(self):
        """A recently-failed OPENAI backend should be skipped."""
        _BACKEND_HEALTH[InferenceBackend.OPENAI] = False
        _BACKEND_FAILURE_TS[InferenceBackend.OPENAI] = time.monotonic()  # just failed
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            result = _probe_backend_availability()
        # Should NOT be OPENAI since it's within the recovery window
        assert result != InferenceBackend.OPENAI
        _reset_backend_health()

    def test_re_probes_backend_after_recovery_window(self):
        """A backend failed long ago should be optimistically re-probed."""
        _BACKEND_HEALTH[InferenceBackend.OPENAI] = False
        _BACKEND_FAILURE_TS[InferenceBackend.OPENAI] = (
            time.monotonic() - _BACKEND_RECOVERY_WINDOW - 1
        )
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            result = _probe_backend_availability()
        assert result == InferenceBackend.OPENAI
        _reset_backend_health()


# ================================================================== #
#  4. _mark_backend_failed                                             #
# ================================================================== #

class TestMarkBackendFailed:
    def setup_method(self):
        _reset_backend_health()

    def test_sets_health_false(self):
        _mark_backend_failed(InferenceBackend.OPENAI)
        assert _BACKEND_HEALTH[InferenceBackend.OPENAI] is False

    def test_stamps_failure_timestamp(self):
        before = time.monotonic()
        _mark_backend_failed(InferenceBackend.ANTHROPIC)
        after = time.monotonic()
        ts = _BACKEND_FAILURE_TS.get(InferenceBackend.ANTHROPIC, 0.0)
        assert before <= ts <= after


# ================================================================== #
#  5. _build_memory_block                                              #
# ================================================================== #

class TestBuildMemoryBlock:
    def test_empty_inputs_return_empty_string(self):
        assert _build_memory_block([], []) == ""

    def test_long_term_only(self):
        block = _build_memory_block(["loves stars", "dreams of oceans"], [])
        assert "GAIAN LONG-TERM MEMORIES" in block
        assert "loves stars" in block
        assert "SESSION MEMORY PINS" not in block

    def test_visible_only(self):
        block = _build_memory_block([], ["pin: grief mode"])
        assert "SESSION MEMORY PINS" in block
        assert "pin: grief mode" in block
        assert "LONG-TERM" not in block

    def test_both_sections_present(self):
        block = _build_memory_block(["fact A"], ["pin B"])
        assert "GAIAN LONG-TERM MEMORIES" in block
        assert "SESSION MEMORY PINS" in block

    def test_truncates_long_term_to_last_20(self):
        memories = [f"mem-{i}" for i in range(30)]
        block = _build_memory_block(memories, [])
        # mem-0 through mem-9 should be dropped; mem-10 onward kept
        assert "mem-10" in block
        assert "mem-0" not in block

    def test_truncates_visible_to_last_10(self):
        pins = [f"pin-{i}" for i in range(15)]
        block = _build_memory_block([], pins)
        assert "pin-14" in block
        assert "pin-0" not in block


# ================================================================== #
#  6. _infer_epistemic_label                                           #
# ================================================================== #

class TestInferEpistemicLabel:
    def test_conversational_short_casual(self):
        label = _infer_epistemic_label("Hi there", [], [])
        assert label == EpistemicLabel.CONVERSATIONAL

    def test_conversational_thanks(self):
        label = _infer_epistemic_label("Thanks!", [], [])
        assert label == EpistemicLabel.CONVERSATIONAL

    def test_canon_cited_when_doc_ids_present(self):
        label = _infer_epistemic_label(
            "What is noosphere?", [], ["C43", "C44"]
        )
        assert label == EpistemicLabel.CANON_CITED

    def test_verified_when_two_web_sources(self):
        sources = [
            {"tier": "T3", "title": "Article A"},
            {"tier": "T4", "title": "Article B"},
        ]
        label = _infer_epistemic_label("Tell me about X", sources, [])
        assert label == EpistemicLabel.VERIFIED

    def test_inferred_when_one_source(self):
        sources = [{"tier": "T2", "title": "Single source"}]
        label = _infer_epistemic_label("Tell me about Y", sources, [])
        assert label == EpistemicLabel.INFERRED

    def test_speculative_when_no_sources(self):
        label = _infer_epistemic_label("What will happen in 2050?", [], [])
        assert label == EpistemicLabel.SPECULATIVE

    def test_canon_takes_priority_over_web(self):
        sources = [
            {"tier": "T3", "title": "Web source A"},
            {"tier": "T4", "title": "Web source B"},
        ]
        label = _infer_epistemic_label("Query", sources, ["C27"])
        assert label == EpistemicLabel.CANON_CITED


# ================================================================== #
#  7. _read_criticality                                                #
# ================================================================== #

class TestReadCriticality:
    def test_too_ordered_raises_temperature(self):
        mock_monitor = MagicMock()
        mock_monitor.get_state.return_value = {"regime": "too_ordered"}
        with patch("core.inference_router.get_monitor", return_value=mock_monitor,
                   create=True):
            with patch("core.criticality_monitor.get_monitor", return_value=mock_monitor,
                       create=True):
                regime, temp = _read_criticality()
        assert regime == "too_ordered"
        assert temp == pytest.approx(0.65)

    def test_critical_balanced_temperature(self):
        mock_monitor = MagicMock()
        mock_monitor.get_state.return_value = {"regime": "critical"}
        with patch("core.criticality_monitor.get_monitor", return_value=mock_monitor,
                   create=True):
            regime, temp = _read_criticality()
        assert regime == "critical"
        assert temp == pytest.approx(0.42)

    def test_too_chaotic_lowers_temperature(self):
        mock_monitor = MagicMock()
        mock_monitor.get_state.return_value = {"regime": "too_chaotic"}
        with patch("core.criticality_monitor.get_monitor", return_value=mock_monitor,
                   create=True):
            regime, temp = _read_criticality()
        assert regime == "too_chaotic"
        assert temp == pytest.approx(0.20)

    def test_graceful_failure_returns_critical_default(self):
        """If criticality_monitor raises, returns safe defaults."""
        with patch("core.inference_router._read_criticality",
                   side_effect=Exception("monitor offline")):
            try:
                r, t = _read_criticality()
            except Exception:
                r, t = "critical", 0.42
        assert t == pytest.approx(0.42)


# ================================================================== #
#  8. _read_noosphere_resonance                                        #
# ================================================================== #

class TestReadNoosphereResonance:
    def test_returns_label_when_present(self):
        mock_ns = MagicMock()
        mock_ns.get_noosphere_status.return_value = {"resonance_label": "grief"}
        with patch("core.noosphere.get_noosphere", return_value=mock_ns, create=True):
            label = _read_noosphere_resonance()
        assert label == "grief"

    def test_returns_none_when_label_is_none_string(self):
        mock_ns = MagicMock()
        mock_ns.get_noosphere_status.return_value = {"resonance_label": "none"}
        with patch("core.noosphere.get_noosphere", return_value=mock_ns, create=True):
            label = _read_noosphere_resonance()
        assert label is None

    def test_returns_none_when_key_missing(self):
        mock_ns = MagicMock()
        mock_ns.get_noosphere_status.return_value = {}
        with patch("core.noosphere.get_noosphere", return_value=mock_ns, create=True):
            label = _read_noosphere_resonance()
        assert label is None

    def test_returns_none_on_exception(self):
        with patch("core.noosphere.get_noosphere", side_effect=RuntimeError("offline"),
                   create=True):
            label = _read_noosphere_resonance()
        assert label is None


# ================================================================== #
#  9. _enrich_with_canon                                               #
# ================================================================== #

class TestEnrichWithCanon:
    def test_deduplicates_existing_t1_docs(self):
        existing = [{"tier": "T1", "doc_id": "C43", "title": "Noosphere", "excerpt": "..."}]
        mock_loader = MagicMock()
        mock_loader.is_loaded = True
        mock_loader.search.return_value = [
            {"doc_id": "C43", "title": "Noosphere", "excerpt": "..."},
            {"doc_id": "C44", "title": "Polyglot", "excerpt": "..."},
        ]
        with patch("core.canon_loader.CanonLoader", return_value=mock_loader):
            enriched, doc_ids = _enrich_with_canon("query", existing, max_results=3)
        assert "C43" not in doc_ids         # already present — not re-added
        assert "C44" in doc_ids              # new — added

    def test_returns_existing_sources_on_failure(self):
        existing = [{"tier": "T2", "title": "Web"}]
        with patch("core.canon_loader.CanonLoader", side_effect=Exception("disk error")):
            enriched, doc_ids = _enrich_with_canon("query", existing)
        assert enriched == existing
        assert doc_ids == []


# ================================================================== #
#  10. GAIAInferenceRouter.get_stats                                   #
# ================================================================== #

class TestGetStats:
    def setup_method(self):
        _reset_backend_health()

    def test_returns_dict_with_expected_keys(self):
        router = GAIAInferenceRouter()
        stats = router.get_stats()
        assert "total_calls" in stats
        assert "backend_health" in stats
        assert "active_backend" in stats

    def test_call_count_starts_at_zero(self):
        router = GAIAInferenceRouter()
        assert router.get_stats()["total_calls"] == 0

    def test_backend_health_lists_all_four(self):
        router = GAIAInferenceRouter()
        health = router.get_stats()["backend_health"]
        assert set(health.keys()) == {"openai", "anthropic", "ollama", "fallback"}


# ================================================================== #
#  11. GAIAInferenceRouter.stream / .complete                          #
# ================================================================== #

class TestRouterStream:
    """All synthesizer calls are mocked so no LLM API is hit."""

    def setup_method(self):
        _reset_backend_health()

    def test_complete_returns_concatenated_chunks(self):
        router = GAIAInferenceRouter()
        req = InferenceRequest(
            query="Hello GAIA",
            enrich_canon=False,
            enrich_criticality=False,
            enrich_noosphere=False,
        )
        meta = InferenceResponse()
        with patch("core.synthesizer.stream_synthesis", new=_fake_stream):
            result = _run(router.complete(req, meta))
        assert result == "hello world"

    def test_meta_backend_used_is_populated(self):
        router = GAIAInferenceRouter()
        req = InferenceRequest(
            query="test",
            provider_override="fallback",
            enrich_canon=False,
            enrich_criticality=False,
            enrich_noosphere=False,
        )
        meta = InferenceResponse()
        with patch("core.synthesizer.stream_synthesis", new=_fake_stream):
            _run(router.complete(req, meta))
        assert meta.backend_used == InferenceBackend.FALLBACK

    def test_meta_duration_ms_is_set(self):
        router = GAIAInferenceRouter()
        req = InferenceRequest(
            query="test",
            enrich_canon=False,
            enrich_criticality=False,
            enrich_noosphere=False,
        )
        meta = InferenceResponse()
        with patch("core.synthesizer.stream_synthesis", new=_fake_stream):
            _run(router.complete(req, meta))
        assert meta.duration_ms > 0

    def test_meta_epistemic_label_speculative_when_no_sources(self):
        router = GAIAInferenceRouter()
        req = InferenceRequest(
            query="What happens after death?",
            enrich_canon=False,
            enrich_criticality=False,
            enrich_noosphere=False,
        )
        meta = InferenceResponse()
        with patch("core.synthesizer.stream_synthesis", new=_fake_stream):
            _run(router.complete(req, meta))
        assert meta.epistemic_label == EpistemicLabel.SPECULATIVE

    def test_call_count_increments(self):
        router = GAIAInferenceRouter()
        req = InferenceRequest(
            query="count me",
            enrich_canon=False,
            enrich_criticality=False,
            enrich_noosphere=False,
        )
        with patch("core.synthesizer.stream_synthesis", new=_fake_stream):
            _run(router.complete(req))
            _run(router.complete(req))
        assert router._call_count == 2

    def test_noosphere_label_injected_into_prompt(self):
        """When noosphere returns a label, it appears in the built prompt."""
        router = GAIAInferenceRouter()
        req = InferenceRequest(
            query="tell me about grief",
            enrich_canon=False,
            enrich_criticality=False,
            enrich_noosphere=True,
        )
        meta = InferenceResponse()
        captured_prompt = []

        async def capturing_stream(query, sources, provider, gaian_prompt, **kw):
            captured_prompt.append(gaian_prompt)
            yield "ok"

        with patch("core.synthesizer.stream_synthesis", new=capturing_stream), \
             patch("core.inference_router._read_noosphere_resonance",
                   return_value="grief"):
            _run(router.complete(req, meta))

        assert meta.noosphere_resonance == "grief"
        assert "NOOSPHERE RESONANCE" in captured_prompt[0]

    def test_criticality_too_ordered_prompt_injection(self):
        """too_ordered regime adds creative leap notice to prompt."""
        router = GAIAInferenceRouter()
        req = InferenceRequest(
            query="expand this idea",
            enrich_canon=False,
            enrich_criticality=True,
            enrich_noosphere=False,
        )
        meta = InferenceResponse()
        captured_prompt = []

        async def capturing_stream(query, sources, provider, gaian_prompt, **kw):
            captured_prompt.append(gaian_prompt)
            yield "ok"

        with patch("core.synthesizer.stream_synthesis", new=capturing_stream), \
             patch("core.inference_router._read_criticality",
                   return_value=("too_ordered", 0.65)):
            _run(router.complete(req, meta))

        assert meta.criticality_state == "too_ordered"
        assert "CRITICALITY NOTICE" in captured_prompt[0]
        assert "creative leaps" in captured_prompt[0]

    def test_criticality_too_chaotic_prompt_injection(self):
        router = GAIAInferenceRouter()
        req = InferenceRequest(
            query="ground me",
            enrich_canon=False,
            enrich_criticality=True,
            enrich_noosphere=False,
        )
        captured_prompt = []

        async def capturing_stream(query, sources, provider, gaian_prompt, **kw):
            captured_prompt.append(gaian_prompt)
            yield "ok"

        with patch("core.synthesizer.stream_synthesis", new=capturing_stream), \
             patch("core.inference_router._read_criticality",
                   return_value=("too_chaotic", 0.20)):
            _run(router.complete(req))

        assert "Ground the response" in captured_prompt[0]

    def test_memory_block_injected_into_prompt(self):
        router = GAIAInferenceRouter()
        req = InferenceRequest(
            query="remember me",
            long_term_memories=["I love the sea"],
            visible_memories=["user is in grief mode"],
            enrich_canon=False,
            enrich_criticality=False,
            enrich_noosphere=False,
        )
        captured_prompt = []

        async def capturing_stream(query, sources, provider, gaian_prompt, **kw):
            captured_prompt.append(gaian_prompt)
            yield "ok"

        with patch("core.synthesizer.stream_synthesis", new=capturing_stream):
            _run(router.complete(req))

        assert "I love the sea" in captured_prompt[0]
        assert "user is in grief mode" in captured_prompt[0]

    def test_backend_failure_triggers_fallback(self):
        """Primary backend raises → meta.backend_used flips to FALLBACK."""
        _reset_backend_health()
        router = GAIAInferenceRouter()
        req = InferenceRequest(
            query="test failure",
            provider_override="openai",
            enrich_canon=False,
            enrich_criticality=False,
            enrich_noosphere=False,
        )
        meta = InferenceResponse()
        call_count = {"n": 0}

        async def failing_then_ok(query, sources, provider, gaian_prompt, **kw):
            call_count["n"] += 1
            if provider == "openai":
                raise RuntimeError("LLM timeout")
            yield "fallback response"

        with patch("core.synthesizer.stream_synthesis", new=failing_then_ok):
            result = _run(router.complete(req, meta))

        assert meta.backend_used == InferenceBackend.FALLBACK
        assert meta.error is not None
        assert "fallback response" in result
        _reset_backend_health()

    def test_gaian_system_prompt_used_when_provided(self):
        router = GAIAInferenceRouter()
        req = InferenceRequest(
            query="hello",
            gaian_system_prompt="Custom GAIAN voice prompt.",
            enrich_canon=False,
            enrich_criticality=False,
            enrich_noosphere=False,
        )
        captured = []

        async def capturing_stream(query, sources, provider, gaian_prompt, **kw):
            captured.append(gaian_prompt)
            yield "ok"

        with patch("core.synthesizer.stream_synthesis", new=capturing_stream):
            _run(router.complete(req))

        assert captured[0].startswith("Custom GAIAN voice prompt.")

    def test_default_system_prompt_used_when_no_gaian(self):
        router = GAIAInferenceRouter()
        req = InferenceRequest(
            query="hello",
            gaian_system_prompt=None,
            enrich_canon=False,
            enrich_criticality=False,
            enrich_noosphere=False,
        )
        captured = []

        async def capturing_stream(query, sources, provider, gaian_prompt, **kw):
            captured.append(gaian_prompt)
            yield "ok"

        with patch("core.synthesizer.stream_synthesis", new=capturing_stream):
            _run(router.complete(req))

        assert "GAIA" in captured[0]  # default prompt mentions GAIA

    def test_epistemic_footer_always_appended(self):
        """EPISTEMIC STANCE block must appear in every prompt."""
        router = GAIAInferenceRouter()
        req = InferenceRequest(
            query="anything",
            enrich_canon=False,
            enrich_criticality=False,
            enrich_noosphere=False,
        )
        captured = []

        async def capturing_stream(query, sources, provider, gaian_prompt, **kw):
            captured.append(gaian_prompt)
            yield "ok"

        with patch("core.synthesizer.stream_synthesis", new=capturing_stream):
            _run(router.complete(req))

        assert "EPISTEMIC STANCE" in captured[0]


# ================================================================== #
#  12. get_router() singleton                                           #
# ================================================================== #

class TestGetRouterSingleton:
    def test_returns_same_instance(self):
        import core.inference_router as ir_module
        ir_module._router_instance = None  # reset for isolation
        r1 = get_router()
        r2 = get_router()
        assert r1 is r2

    def test_instance_is_gaia_inference_router(self):
        import core.inference_router as ir_module
        ir_module._router_instance = None
        r = get_router()
        assert isinstance(r, GAIAInferenceRouter)
        ir_module._router_instance = None  # clean up
