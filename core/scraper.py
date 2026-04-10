"""
GAIA Web Scraper — CAP-012 Content Fetcher

Fetches and cleans full page content from URLs returned by web search.
Used by the synthesizer to ground LLM responses in real source text.

Strategy:
  1. Fetch HTML via httpx (async, timeout-safe)
  2. Parse with trafilatura for main-content extraction
  3. Fallback to BeautifulSoup paragraph extraction
  4. Return cleaned plain text capped at max_chars

Canon Ref: C20 (Source Triage and Evidence Policy)
"""

import asyncio
import re
from typing import Optional

try:
    import httpx
    _HTTPX_AVAILABLE = True
except ImportError:
    _HTTPX_AVAILABLE = False

try:
    import trafilatura
    _TRAFILATURA_AVAILABLE = True
except ImportError:
    _TRAFILATURA_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    _BS4_AVAILABLE = True
except ImportError:
    _BS4_AVAILABLE = False


HEADERS = {
    "User-Agent": "GAIA-APP/0.3 (constitutional AI research; +https://github.com/R0GV3TheAlchemist/GAIA-APP)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def _extract_with_trafilatura(html: str) -> Optional[str]:
    if not _TRAFILATURA_AVAILABLE:
        return None
    return trafilatura.extract(
        html,
        include_comments=False,
        include_tables=True,
        no_fallback=False,
    )


def _extract_with_bs4(html: str) -> Optional[str]:
    if not _BS4_AVAILABLE:
        return None
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    paragraphs = soup.find_all("p")
    text = " ".join(p.get_text(" ", strip=True) for p in paragraphs)
    return text if len(text) > 100 else None


def _clean_text(text: str, max_chars: int = 2000) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]


async def fetch_page_content(url: str, max_chars: int = 2000, timeout: float = 8.0) -> str:
    """
    Async: fetch and extract main text content from a URL.
    Returns cleaned plain text, or an empty string on failure.
    """
    if not url or not url.startswith("http"):
        return ""
    if not _HTTPX_AVAILABLE:
        return ""  # httpx not installed — skip scraping

    try:
        async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=timeout) as client:
            response = await client.get(url)
            if response.status_code != 200:
                return ""
            html = response.text
    except Exception:
        return ""

    text = _extract_with_trafilatura(html) or _extract_with_bs4(html) or ""
    return _clean_text(text, max_chars)


async def fetch_top_sources(
    urls: list[str],
    max_per_source: int = 1500,
    max_sources: int = 4,
    timeout: float = 6.0,
) -> list[dict]:
    """
    Concurrently fetch content from up to `max_sources` URLs.
    Returns list of {url, content} dicts (empty content = failed fetch).
    """
    selected = [u for u in urls if u and u.startswith("http")][:max_sources]
    tasks = [fetch_page_content(u, max_chars=max_per_source, timeout=timeout) for u in selected]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [
        {"url": url, "content": content if isinstance(content, str) else ""}
        for url, content in zip(selected, results)
    ]
