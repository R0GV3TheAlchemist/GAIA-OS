"""
GAIA Web Search Module — CAP-012 (v2)
Canon Ref: C20 (Canonical Source Triage and Evidence Policy)

Architecture:
  canon first (T1) → web second (T2-T5) → synthesis third

Search Providers (priority order, configured via .env):
  1. Brave Search API   (BRAVE_API_KEY)    — recommended, privacy-first
  2. Tavily API         (TAVILY_API_KEY)   — AI-optimised, best for RAG
  3. DuckDuckGo         (no key required)  — fallback, zero cost

Source Triage tiers (C20 §2):
  T1 CANONICAL  — GAIA canon documents (always shown first)
  T2 PRIMARY    — peer-reviewed papers, official datasets, gov sources
  T3 SECONDARY  — reputable news / encyclopaedia
  T4 TERTIARY   — blogs, general web
  T5 CONTESTED  — disputed, social media, user-generated content
"""

import asyncio
import json
import os
import re
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import httpx
    _HTTPX_AVAILABLE = True
except ImportError:
    _HTTPX_AVAILABLE = False


# ------------------------------------------------------------------ #
#  Data Models                                                         #
# ------------------------------------------------------------------ #

@dataclass
class WebResult:
    title: str
    url: str
    snippet: str
    source_tier: str          # T1–T5
    domain: str
    fetched_at: float
    provider: str = "unknown"

    def to_dict(self) -> dict:
        return asdict(self)


# ------------------------------------------------------------------ #
#  Source Tier Classifier (C20)                                        #
# ------------------------------------------------------------------ #

_T2_DOMAINS = {
    "arxiv.org", "pubmed.ncbi.nlm.nih.gov", "scholar.google.com",
    "nature.com", "science.org", "cell.com", "nejm.org", "thelancet.com",
    "nasa.gov", "noaa.gov", "usgs.gov", "epa.gov", "who.int",
    "un.org", "worldbank.org", "oecd.org", "europa.eu",
    "github.com", "docs.python.org", "developer.mozilla.org",
}

_T3_DOMAINS = {
    "wikipedia.org", "britannica.com", "reuters.com", "apnews.com",
    "bbc.com", "bbc.co.uk", "theguardian.com", "nytimes.com",
    "washingtonpost.com", "ft.com", "economist.com", "scientificamerican.com",
    "nationalgeographic.com", "smithsonianmag.com",
}

_T5_PATTERNS = [
    r"reddit\.com", r"twitter\.com", r"x\.com",
    r"tiktok\.com", r"facebook\.com", r"instagram\.com",
    r"quora\.com",
]


def classify_source(url: str) -> str:
    """Assign C20 source tier to a URL."""
    try:
        domain = urllib.parse.urlparse(url).netloc.lower().lstrip("www.")
    except Exception:
        return "T4"
    if any(re.search(p, url) for p in _T5_PATTERNS):
        return "T5"
    if domain in _T2_DOMAINS:
        return "T2"
    if domain in _T3_DOMAINS:
        return "T3"
    if domain.endswith(".gov") or domain.endswith(".edu"):
        return "T2"
    if domain.endswith(".org"):
        return "T3"
    return "T4"


# ------------------------------------------------------------------ #
#  Provider 1: Brave Search API                                        #
# ------------------------------------------------------------------ #

async def _brave_search(query: str, max_results: int = 6) -> list[WebResult]:
    """
    Brave Search API — privacy-first, no user tracking.
    Requires BRAVE_API_KEY in environment.
    Docs: https://api.search.brave.com/
    """
    api_key = os.environ.get("BRAVE_API_KEY", "")
    if not api_key or not _HTTPX_AVAILABLE:
        return []

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key,
    }
    params = {"q": query, "count": max_results, "safesearch": "moderate"}
    results = []
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers=headers,
                params=params,
            )
            data = resp.json()
        for item in data.get("web", {}).get("results", [])[:max_results]:
            url = item.get("url", "")
            results.append(WebResult(
                title=item.get("title", ""),
                url=url,
                snippet=item.get("description", "")[:400],
                source_tier=classify_source(url),
                domain=urllib.parse.urlparse(url).netloc.lstrip("www."),
                fetched_at=time.time(),
                provider="brave",
            ))
    except Exception:
        pass
    return results


# ------------------------------------------------------------------ #
#  Provider 2: Tavily Search API                                       #
# ------------------------------------------------------------------ #

async def _tavily_search(query: str, max_results: int = 6) -> list[WebResult]:
    """
    Tavily — AI-optimised search with pre-extracted content.
    Best for RAG pipelines. Requires TAVILY_API_KEY in environment.
    Docs: https://docs.tavily.com/
    """
    api_key = os.environ.get("TAVILY_API_KEY", "")
    if not api_key or not _HTTPX_AVAILABLE:
        return []

    payload = {
        "api_key": api_key,
        "query": query,
        "max_results": max_results,
        "search_depth": "advanced",
        "include_answer": False,
        "include_raw_content": False,
    }
    results = []
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post("https://api.tavily.com/search", json=payload)
            data = resp.json()
        for item in data.get("results", [])[:max_results]:
            url = item.get("url", "")
            results.append(WebResult(
                title=item.get("title", ""),
                url=url,
                snippet=item.get("content", "")[:400],
                source_tier=classify_source(url),
                domain=urllib.parse.urlparse(url).netloc.lstrip("www."),
                fetched_at=time.time(),
                provider="tavily",
            ))
    except Exception:
        pass
    return results


# ------------------------------------------------------------------ #
#  Provider 3: DuckDuckGo (no API key, always available)              #
# ------------------------------------------------------------------ #

def _ddg_search(query: str, max_results: int = 6) -> list[WebResult]:
    results: list[WebResult] = []
    try:
        encoded = urllib.parse.quote_plus(query)
        url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_redirect=1&no_html=1&skip_disambig=1"
        req = urllib.request.Request(url, headers={"User-Agent": "GAIA-APP/0.3 (constitutional AI)"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if data.get("AbstractText") and data.get("AbstractURL"):
            u = data["AbstractURL"]
            results.append(WebResult(
                title=data.get("Heading", query),
                url=u,
                snippet=data["AbstractText"][:400],
                source_tier=classify_source(u),
                domain=urllib.parse.urlparse(u).netloc.lstrip("www."),
                fetched_at=time.time(),
                provider="duckduckgo",
            ))

        for topic in data.get("RelatedTopics", [])[:max_results - 1]:
            if not isinstance(topic, dict):
                continue
            first_url = topic.get("FirstURL", "")
            text = topic.get("Text", "")
            if first_url and text:
                results.append(WebResult(
                    title=text[:80],
                    url=first_url,
                    snippet=text[:300],
                    source_tier=classify_source(first_url),
                    domain=urllib.parse.urlparse(first_url).netloc.lstrip("www."),
                    fetched_at=time.time(),
                    provider="duckduckgo",
                ))
            if len(results) >= max_results:
                break

    except Exception as e:
        results.append(WebResult(
            title="Web search unavailable",
            url="",
            snippet=f"DuckDuckGo unavailable: {str(e)[:120]}. Canon results still active.",
            source_tier="T5",
            domain="",
            fetched_at=time.time(),
            provider="duckduckgo",
        ))
    return results


# ------------------------------------------------------------------ #
#  Multi-Provider Router                                               #
# ------------------------------------------------------------------ #

async def search_web_async(query: str, max_results: int = 6) -> list[WebResult]:
    """
    Search using the best available provider.
    Priority: Brave → Tavily → DuckDuckGo.
    """
    # Try Brave first
    if os.environ.get("BRAVE_API_KEY"):
        results = await _brave_search(query, max_results)
        if results:
            return results

    # Try Tavily second
    if os.environ.get("TAVILY_API_KEY"):
        results = await _tavily_search(query, max_results)
        if results:
            return results

    # DuckDuckGo fallback (always works, no key)
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _ddg_search, query, max_results)


def detect_search_provider() -> str:
    """Returns the name of the active search provider."""
    if os.environ.get("BRAVE_API_KEY"):
        return "brave"
    if os.environ.get("TAVILY_API_KEY"):
        return "tavily"
    return "duckduckgo"


# ------------------------------------------------------------------ #
#  Synthesis: merge canon refs + web results into ranked source list   #
# ------------------------------------------------------------------ #

def synthesise_sources(
    canon_refs: list[dict],
    web_results: list[WebResult],
) -> dict:
    """
    Merge and rank all sources per C20 triage policy.
    T1 (canon) always first, then T2-T5 web in tier order.
    """
    canon_sources = [
        {
            "tier": "T1",
            "doc_id": r["doc_id"],
            "title": r["title"],
            "excerpt": r["excerpt"][:300],
            "source_type": "canon",
        }
        for r in canon_refs
    ]
    web_sources = sorted(
        [r.to_dict() for r in web_results if r.url],
        key=lambda x: x["source_tier"]
    )
    return {
        "canon": canon_sources,
        "web": web_sources,
        "total": len(canon_sources) + len(web_sources),
        "policy": "C20 — canon first, web second",
        "provider": detect_search_provider(),
    }
