"""
GAIA Web Search Module — CAP-012
Canon Ref: C20 (Canonical Source Triage and Evidence Policy)

Architecture:
  canon first → web second → synthesis third

Implementation uses DuckDuckGo Instant Answer API (no API key required,
no user tracking, no personal data sent). For production, swap
_ddg_search() with a Brave Search or SearXNG call.

Source Triage tiers (C20 §2):
  T1 CANONICAL  — GAIA canon documents (always shown first)
  T2 PRIMARY    — peer-reviewed papers, official datasets, gov sources
  T3 SECONDARY  — reputable news / encyclopaedia
  T4 TERTIARY   — blogs, social, user-generated content
  T5 CONTESTED  — disputed, not independently verified
"""

import asyncio
import json
import re
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict
from typing import Optional


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
    r"quora\.com", r"yahoo answers",
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
#  DuckDuckGo Instant Answer Search (no API key, no tracking)         #
# ------------------------------------------------------------------ #

def _ddg_search(query: str, max_results: int = 6) -> list[WebResult]:
    """
    Query DuckDuckGo Instant Answer API.
    Returns structured results with title, URL, snippet, and source tier.
    Falls back gracefully if the API is unavailable.
    """
    results: list[WebResult] = []
    try:
        encoded = urllib.parse.quote_plus(query)
        url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_redirect=1&no_html=1&skip_disambig=1"
        req = urllib.request.Request(url, headers={"User-Agent": "GAIA-APP/0.2 (constitutional AI)"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        # Abstract (top answer)
        if data.get("AbstractText") and data.get("AbstractURL"):
            u = data["AbstractURL"]
            results.append(WebResult(
                title=data.get("Heading", query),
                url=u,
                snippet=data["AbstractText"][:400],
                source_tier=classify_source(u),
                domain=urllib.parse.urlparse(u).netloc.lstrip("www."),
                fetched_at=time.time(),
            ))

        # Related topics
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
                ))
            if len(results) >= max_results:
                break

    except Exception as e:
        # Non-fatal — web search degraded, canon still serves
        results.append(WebResult(
            title="Web search unavailable",
            url="",
            snippet=f"Could not reach DuckDuckGo: {str(e)[:120]}. Canon results still available.",
            source_tier="T5",
            domain="",
            fetched_at=time.time(),
        ))

    return results


async def search_web_async(query: str, max_results: int = 6) -> list[WebResult]:
    """Async wrapper — runs blocking HTTP in a thread pool."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _ddg_search, query, max_results)


# ------------------------------------------------------------------ #
#  Synthesis: merge canon refs + web results into ranked source list   #
# ------------------------------------------------------------------ #

def synthesise_sources(
    canon_refs: list[dict],
    web_results: list[WebResult],
) -> dict:
    """
    Merge and rank all sources per C20 triage policy:
      T1 (canon) always first, then T2–T5 web in order.
    Returns a dict with 'canon' and 'web' keys for the SSE stream.
    """
    canon_sources = [
        {
            "tier": "T1",
            "doc_id": r["doc_id"],
            "title": r["title"],
            "excerpt": r["excerpt"][:250],
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
    }
