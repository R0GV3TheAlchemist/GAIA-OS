"""
GAIA Core API Server — FastAPI bridge between the Tauri UI and the Python constitutional core.

Exposes REST endpoints for:
  - Constitutional status
  - Canon loader (C-series documents, search, lazy hydration)
  - Memory governance (MemoryStore)
  - Consent lifecycle (ConsentLedger)
  - Action gating (ActionGate)
  - ATLAS Earth Intelligence (Google Earth Engine)
  - Query streaming (SSE — Perplexity-style: canon-first + real LLM synthesis)
  - Web search (CAP-012, multi-provider: Brave / Tavily / DuckDuckGo)

LLM Providers (auto-detected via .env):
  OPENAI_API_KEY      → OpenAI gpt-4o-mini
  ANTHROPIC_API_KEY   → Claude 3 Haiku
  OLLAMA_MODEL        → Local Ollama (e.g. mistral)
  (none)              → Rule-based fallback (always works)

Search Providers (auto-detected via .env):
  BRAVE_API_KEY       → Brave Search (recommended)
  TAVILY_API_KEY      → Tavily (AI-optimised)
  (none)              → DuckDuckGo (zero cost, no key)

Runs locally on http://127.0.0.1:8008 for desktop.
Deploy via Docker to Google Cloud Run for mobile/web.

Epistemic Status: ESTABLISHED
Canon Ref: C01 (Master), C15 (Runtime & Permissions), C17 (Memory & Identity),
           C20 (Source Triage), C21 (Interface & Shell Grammar)
"""

import asyncio
import json
import logging
import os
import sys
import time
from typing import AsyncGenerator, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import CanonLoader, ActionGate, RiskTier, ConsentLedger, MemoryStore
from core.web_search import search_web_async, synthesise_sources, detect_search_provider
from core.scraper import fetch_top_sources
from core.synthesizer import stream_synthesis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GAIA Core API",
    description="Constitutional AI governance layer for GAIA-APP — Perplexity-style answer engine",
    version="0.4.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------ #
#  Constitutional System Initialisation                                #
# ------------------------------------------------------------------ #

canon = CanonLoader()
try:
    canon.load()
except Exception as e:
    logger.warning(f"Canon load error (non-fatal during dev): {e}")

gate = ActionGate()
ledger = ConsentLedger()
memory = MemoryStore()


# ------------------------------------------------------------------ #
#  Pydantic Models                                                     #
# ------------------------------------------------------------------ #

class MemoryAddRequest(BaseModel):
    content: str
    source: str = "explicit"
    purposes: list = ["general"]
    confidence: float = 1.0

class ConsentGrantRequest(BaseModel):
    party_id: str
    purpose: str
    duration_days: int = 365

class ConsentRevokeRequest(BaseModel):
    party_id: str
    purpose: str

class ActionEvaluateRequest(BaseModel):
    action_type: str
    description: str
    tier: str = "yellow"
    payload: dict = {}

class QueryRequest(BaseModel):
    query: str
    max_canon_refs: int = 3
    enable_web_search: bool = True
    enable_scraping: bool = True        # fetch full page content for richer synthesis
    llm_provider: Optional[str] = None  # force provider: openai/anthropic/ollama/fallback
    sovereign_id: Optional[str] = None

class WebSearchRequest(BaseModel):
    query: str
    max_results: int = 6


# ------------------------------------------------------------------ #
#  Status                                                              #
# ------------------------------------------------------------------ #

@app.get("/status")
def status():
    """Constitutional health check."""
    return {
        "core": "active",
        "sovereignty": "enforced",
        "t1_floor": "held",
        "canon_status": canon.status,
        "canon_loaded": canon.is_loaded,
        "canon_doc_count": len(canon.list_documents()),
        "canon_docs": canon.list_documents(),
        "search_provider": detect_search_provider(),
        "capabilities": {
            "CAP-011": "active",
            "CAP-012": "active — multi-provider (Brave/Tavily/DDG)",
            "CAP-013": "active — LLM synthesis (auto-detect provider)",
            "CAP-014": "active — web scraping (trafilatura)",
            "CAP-015": "active",
            "CAP-016": "active",
            "CAP-017": "active",
            "CAP-020": "active",
        },
        "version": "0.4.0"
    }


# ------------------------------------------------------------------ #
#  Canon Endpoints                                                     #
# ------------------------------------------------------------------ #

@app.get("/canon/status")
def canon_status():
    return {
        "status": canon.status,
        "loaded_count": len(canon.list_documents()),
        "manifest_count": len(canon.list_manifest()),
        "floor_documents": ["00_Documentation_Index", "01_GAIA_Master_Document"],
        "message": {
            "green": "Constitutional floor held. Canon is active.",
            "yellow": "Canon loading or degraded. Some documents unavailable.",
            "red": "CONSTITUTIONAL FLOOR MISSING. System running without canon."
        }.get(canon.status, "Unknown")
    }

@app.get("/canon/list")
def canon_list():
    docs = []
    for doc_id in canon.list_documents():
        doc = canon.get(doc_id)
        if doc:
            docs.append({
                "id": doc_id,
                "title": doc.get("title", doc_id),
                "source": doc.get("source", "unknown"),
                "loaded_at": doc.get("loaded_at"),
            })
    return {"count": len(docs), "documents": docs, "manifest_registry": canon.list_manifest()}

@app.get("/canon/get/{doc_id}")
def canon_get(doc_id: str):
    doc = canon.get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Canon document '{doc_id}' not found.")
    return doc

@app.get("/canon/search")
def canon_search(q: str, max_results: int = 5):
    if not q or len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters.")
    results = canon.search(q, max_results=max_results)
    return {"query": q, "result_count": len(results), "results": results}


# ------------------------------------------------------------------ #
#  Web Search Endpoint (CAP-012)                                       #
# ------------------------------------------------------------------ #

@app.post("/search/web")
async def web_search(req: WebSearchRequest):
    """
    CAP-012: Multi-provider web search with C20 source triage.
    Provider auto-detected: Brave → Tavily → DuckDuckGo.
    """
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    canon_refs = canon.search(query, max_results=3)
    web_results = await search_web_async(query, max_results=req.max_results)
    sources = synthesise_sources(canon_refs, web_results)

    return {
        "query": query,
        "sources": sources,
        "canon_status": canon.status,
        "search_provider": detect_search_provider(),
        "triage_policy": "C20 — canon first, web second",
        "timestamp": time.time(),
    }


# ------------------------------------------------------------------ #
#  Query Streaming — Perplexity-Style with Real LLM Synthesis          #
# ------------------------------------------------------------------ #

async def _stream_query_response(
    query: str,
    canon_refs: list[dict],
    web_results: list,
    enable_scraping: bool = True,
    llm_provider: Optional[str] = None,
    sovereign_id: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    """
    Perplexity-style SSE stream:

      event: citation      — T1 canon card {doc_id, title, excerpt, tier}
      event: web_result    — T2-T5 web card {title, url, snippet, source_tier, domain}
      event: token         — single chunk of LLM response text
      event: suggestions   — follow-up question chips
      event: done          — stream complete with metadata

    Order enforced: canon citations → web result cards → LLM synthesis tokens.
    LLM is grounded in scraped full-text content for higher accuracy.
    """

    def sse(event: str, data: dict) -> str:
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"

    # 1. Canon citations (T1 — always first)
    for ref in canon_refs:
        yield sse("citation", {
            "tier": "T1",
            "doc_id": ref["doc_id"],
            "title": ref["title"],
            "excerpt": ref["excerpt"][:200],
        })
        await asyncio.sleep(0.04)

    # 2. Web result cards (T2-T5 — after canon)
    valid_web = [r for r in web_results if r.url]
    for result in valid_web:
        yield sse("web_result", {
            "tier": result.source_tier,
            "title": result.title,
            "url": result.url,
            "snippet": result.snippet[:250],
            "domain": result.domain,
            "provider": getattr(result, "provider", "unknown"),
        })
        await asyncio.sleep(0.05)

    # 3. Optionally scrape top web sources for full content
    scraped_content: dict[str, str] = {}
    if enable_scraping and valid_web:
        top_urls = [r.url for r in valid_web if r.source_tier in ("T2", "T3")][:3]
        if not top_urls:
            top_urls = [r.url for r in valid_web[:2]]
        try:
            fetched = await fetch_top_sources(top_urls, max_per_source=1200, max_sources=3)
            scraped_content = {item["url"]: item["content"] for item in fetched if item["content"]}
        except Exception as e:
            logger.warning(f"Scraping failed (non-fatal): {e}")

    # 4. Build unified source list for LLM (canon + web with scraped content)
    llm_sources: list[dict] = []
    for ref in canon_refs:
        llm_sources.append({
            "tier": "T1",
            "title": ref["title"],
            "excerpt": ref["excerpt"][:300],
        })
    for result in valid_web:
        content = scraped_content.get(result.url, result.snippet)
        llm_sources.append({
            "tier": result.source_tier,
            "title": result.title,
            "url": result.url,
            "snippet": content[:400],
        })

    # 5. Stream LLM synthesis tokens
    try:
        async for chunk in stream_synthesis(query, llm_sources, provider=llm_provider):
            yield sse("token", {"text": chunk})
    except Exception as e:
        yield sse("token", {"text": f"[Synthesis error: {str(e)[:100]}]"})

    # 6. Follow-up suggestions
    await asyncio.sleep(0.05)
    yield sse("suggestions", {"items": _generate_suggestions(query)})

    # 7. Done
    yield sse("done", {
        "canon_status": canon.status,
        "docs_searched": len(canon.list_documents()),
        "refs_found": len(canon_refs),
        "web_results": len(valid_web),
        "scraped_sources": len(scraped_content),
        "search_provider": detect_search_provider(),
        "timestamp": time.time(),
    })


def _generate_suggestions(query: str) -> list[str]:
    q = query.lower()
    if any(w in q for w in ["gaian", "twin", "human"]):
        return [
            "What are the 5 layers of a Gaian digital twin?",
            "How does the consent ledger protect the human sovereign?",
            "What is the difference between a Gaian and a GAIA node?"
        ]
    elif any(w in q for w in ["canon", "c01", "c00", "document"]):
        return [
            "Show me the full C-series document registry",
            "What is the GAIA Equation (D00)?",
            "Which canon document governs permissions?"
        ]
    elif any(w in q for w in ["atlas", "earth", "temperature", "ndvi", "climate"]):
        return [
            "What is the current air quality in San Antonio?",
            "Show me NDVI vegetation data for my location",
            "How does ATLAS connect to the GAIANS network?"
        ]
    elif any(w in q for w in ["search", "web", "news", "latest"]):
        return [
            "Search for the latest GAIA-related research",
            "What is the current state of planetary intelligence AI?",
            "Find recent papers on constitutional AI"
        ]
    else:
        return [
            "What is GAIA's constitutional foundation?",
            "How does the ActionGate protect sovereignty?",
            "What canon documents are loaded right now?"
        ]


@app.post("/query/stream")
async def query_stream(req: QueryRequest):
    """
    Perplexity-style canon-first streaming query with real LLM synthesis.

    Pipeline:
      1. Canon search (T1 citations emitted first)
      2. Multi-provider web search (Brave/Tavily/DDG)
      3. Web scraping of top sources (for grounded synthesis)
      4. LLM synthesis streamed as token events
      5. Follow-up suggestions + done metadata

    SSE event types: citation | web_result | token | suggestions | done
    Canon Ref: C20 (Source Triage), C21 (Shell Grammar)
    """
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    canon_refs = canon.search(query, max_results=req.max_canon_refs)

    web_results = []
    if req.enable_web_search:
        web_results = await search_web_async(query, max_results=5)

    return StreamingResponse(
        _stream_query_response(
            query,
            canon_refs,
            web_results,
            enable_scraping=req.enable_scraping,
            llm_provider=req.llm_provider,
            sovereign_id=req.sovereign_id,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "X-Canon-Status": canon.status,
            "X-Search-Provider": detect_search_provider(),
        },
    )


# ------------------------------------------------------------------ #
#  Memory                                                              #
# ------------------------------------------------------------------ #

@app.post("/memory/add")
def add_memory(req: MemoryAddRequest):
    entry = memory.add(req.content, req.source, req.purposes, req.confidence)
    return entry.to_dict()

@app.get("/memory/list")
def list_memory():
    return memory.list_all()

@app.put("/memory/{memory_id}")
def edit_memory(memory_id: str, new_content: str):
    success = memory.edit(memory_id, new_content)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found or frozen")
    return {"edited": True, "memory_id": memory_id}

@app.delete("/memory/{memory_id}")
def delete_memory(memory_id: str):
    success = memory.delete(memory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"deleted": True, "memory_id": memory_id}

@app.get("/memory/audit")
def memory_audit():
    return memory.get_audit_log()


# ------------------------------------------------------------------ #
#  Consent                                                             #
# ------------------------------------------------------------------ #

@app.post("/consent/grant")
def grant_consent(req: ConsentGrantRequest):
    record = ledger.grant(req.party_id, req.purpose, req.duration_days)
    return record.to_dict()

@app.post("/consent/revoke")
def revoke_consent(req: ConsentRevokeRequest):
    revoked = ledger.revoke(req.party_id, req.purpose)
    return {"revoked": revoked, "party_id": req.party_id, "purpose": req.purpose}

@app.get("/consent/active/{party_id}")
def active_consents(party_id: str):
    return ledger.get_active_consents(party_id)

@app.get("/consent/ledger")
def full_ledger():
    return ledger.get_ledger()


# ------------------------------------------------------------------ #
#  Action Gate                                                         #
# ------------------------------------------------------------------ #

@app.post("/action/evaluate")
def evaluate_action(req: ActionEvaluateRequest):
    tier_map = {"green": RiskTier.GREEN, "yellow": RiskTier.YELLOW, "red": RiskTier.RED}
    result = gate.evaluate({
        "type": req.action_type,
        "description": req.description,
        "tier": tier_map.get(req.tier, RiskTier.YELLOW),
        "payload": req.payload
    })
    return {
        **result,
        "tier": result["tier"].value if hasattr(result.get("tier"), "value") else req.tier
    }

@app.get("/action/audit")
def action_audit():
    return gate.get_audit_log()


# ------------------------------------------------------------------ #
#  ATLAS: Earth Intelligence                                           #
# ------------------------------------------------------------------ #

@app.get("/atlas/status")
def atlas_status():
    try:
        import ee
        ee.Initialize()
        return {"atlas": "connected", "source": "Google Earth Engine"}
    except Exception as e:
        return {"atlas": "unavailable", "reason": str(e), "action": "Run: earthengine authenticate"}

@app.get("/atlas/temperature")
def get_surface_temp(lat: float = 29.4241, lon: float = -98.4936):
    try:
        import ee
        ee.Initialize()
        point = ee.Geometry.Point([lon, lat])
        dataset = (ee.ImageCollection("MODIS/061/MOD11A1")
                   .filterDate("2026-01-01", "2026-04-09")
                   .select("LST_Day_1km"))
        temp_k = dataset.mean().sample(point, 1000).first().get("LST_Day_1km").getInfo()
        temp_c = round((temp_k * 0.02) - 273.15, 2) if temp_k else None
        return {"lat": lat, "lon": lon, "temperature_celsius": temp_c,
                "source": "MODIS/061/MOD11A1", "layer": "ATLAS"}
    except ImportError:
        raise HTTPException(status_code=503, detail="pip install earthengine-api")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"ATLAS unavailable: {str(e)}")

@app.get("/atlas/ndvi")
def get_vegetation(lat: float = 29.4241, lon: float = -98.4936):
    try:
        import ee
        ee.Initialize()
        point = ee.Geometry.Point([lon, lat])
        dataset = (ee.ImageCollection("MODIS/061/MOD13A2")
                   .filterDate("2026-01-01", "2026-04-09")
                   .select("NDVI"))
        ndvi_val = dataset.mean().sample(point, 1000).first().get("NDVI").getInfo()
        return {"lat": lat, "lon": lon, "ndvi": ndvi_val,
                "ndvi_scaled": round(ndvi_val * 0.0001, 4) if ndvi_val else None,
                "source": "MODIS/061/MOD13A2", "layer": "ATLAS"}
    except ImportError:
        raise HTTPException(status_code=503, detail="pip install earthengine-api")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"ATLAS unavailable: {str(e)}")

@app.get("/atlas/air-quality")
def get_air_quality(lat: float = 29.4241, lon: float = -98.4936):
    try:
        import ee
        ee.Initialize()
        point = ee.Geometry.Point([lon, lat])
        dataset = (ee.ImageCollection("COPERNICUS/S5P/NRTI/L3_NO2")
                   .filterDate("2026-01-01", "2026-04-09")
                   .select("NO2_column_number_density"))
        no2 = dataset.mean().sample(point, 1000).first().get("NO2_column_number_density").getInfo()
        return {"lat": lat, "lon": lon, "no2_mol_per_m2": no2,
                "source": "Copernicus/Sentinel-5P", "layer": "ATLAS"}
    except ImportError:
        raise HTTPException(status_code=503, detail="pip install earthengine-api")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"ATLAS unavailable: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8008, log_level="info")
