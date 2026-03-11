"""
Google kategori araması
"tekstil e-ticaret markası" gibi sorgularla marka bulur.
Serper API varsa kullanır, yoksa duckduckgo-search + çoklu sorgu varyasyonu.
Minimum 150 unique domain hedeflenir.
"""

import logging
import os
import time
from urllib.parse import urlparse

import httpx

_logger = logging.getLogger(__name__)

REQUEST_DELAY = 1.5
MIN_RESULTS = 150


def _extract_domain(url: str):
    """URL'den domain çıkarır (www. dahil değil)."""
    try:
        parsed = urlparse(url)
        if parsed.scheme and parsed.netloc:
            domain = parsed.netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
    except Exception:
        pass
    return None


def _search_serper_page(query: str, start: int, num: int) -> list:
    """Serper API — tek sayfa."""
    key = os.getenv("SERPER_API_KEY")
    if not key:
        return []

    try:
        resp = httpx.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": key, "Content-Type": "application/json"},
            json={"q": query, "num": num, "start": start},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        items = []
        for item in data.get("organic", []):
            link = item.get("link", "")
            domain = _extract_domain(link)
            if not domain:
                continue
            skip = any(
                d in domain
                for d in ["google.", "youtube.", "facebook.", "instagram.", "twitter.", "linkedin.", "wikipedia."]
            )
            if skip:
                continue
            items.append({
                "name": item.get("title", domain),
                "domain": domain,
                "website_url": link if link.startswith("http") else f"https://{link}",
                "source": "google",
                "source_metadata": {"query": query},
            })
        return items
    except Exception as e:
        _logger.warning("❌ Serper hatası: %s", e)
        return []


def _search_serper(query: str, max_results: int) -> list:
    """Serper API — sayfalama ile 150+ sonuç."""
    key = os.getenv("SERPER_API_KEY")
    if not key:
        return []

    target = max(max_results, MIN_RESULTS)
    seen = set()
    results = []
    start = 0
    page_size = 100

    while len(results) < target:
        items = _search_serper_page(query, start, page_size)
        if not items:
            break
        for item in items:
            domain = item.get("domain")
            if domain and domain not in seen:
                seen.add(domain)
                results.append(item)
                if len(results) >= target:
                    break
        if len(items) < page_size:
            break
        start += page_size
        time.sleep(REQUEST_DELAY)

    _logger.info("✅ Serper: %d unique domain bulundu", len(results))
    return results


def _query_variations(base_query: str) -> list[str]:
    """
    Ana sorguya varyasyonlar ekler — her biri farklı sonuçlar döner.
    DuckDuckGo/Bing tek sorguda ~10-15 döndüğü için çoklu arama gerekli.
    """
    return [
        base_query,
        f"{base_query} satın al",
        f"{base_query} marka",
        f"{base_query} online",
        f"{base_query} e-ticaret",
        f"{base_query} fiyat",
        f"{base_query} modelleri",
    ]


def _search_duckduckgo(query: str, max_results: int) -> list:
    """
    duckduckgo-search paketi ile arama.
    Tek sorgu ~10-30 sonuç döndüğü için çoklu sorgu varyasyonu kullanır.
    """
    try:
        from duckduckgo_search import DDGS

        target = max(max_results, MIN_RESULTS)
        seen = set()
        results = []
        queries = _query_variations(query)

        with DDGS() as ddgs:
            for q in queries:
                if len(results) >= target:
                    break
                time.sleep(REQUEST_DELAY)
                try:
                    for item in ddgs.text(q, region="tr-tr", max_results=80):
                        link = item.get("href") or item.get("url") or ""
                        if not link:
                            continue
                        domain = _extract_domain(link)
                        if not domain or domain in seen:
                            continue
                        skip = any(
                            d in domain
                            for d in ["duckduckgo.", "google.", "youtube.", "facebook.", "wikipedia.", "wikimedia."]
                        )
                        if skip:
                            continue
                        seen.add(domain)
                        title = item.get("title", domain)
                        results.append({
                            "name": title,
                            "domain": domain,
                            "website_url": link if link.startswith("http") else f"https://{link}",
                            "source": "google",
                            "source_metadata": {"query": q},
                        })
                        if len(results) >= target:
                            break
                except Exception as e:
                    _logger.warning("Sorgu hatası (%s): %s", q, e)
                    continue

        _logger.info("🔄 DuckDuckGo: %d unique domain bulundu (%d sorgu)", len(results), len(queries))
        return results
    except Exception as e:
        _logger.exception("❌ DuckDuckGo hatası: %s", e)
        return []


def search_companies(query: str, max_results: int = 150) -> list:
    """
    Kategori araması yapar, minimum 150 unique domain döner.
    SERPER_API_KEY varsa Serper, yoksa duckduckgo-search + çoklu sorgu kullanır.
    """
    if not query or not query.strip():
        return []

    target = max(max_results, MIN_RESULTS)
    results = _search_serper(query.strip(), target)
    if not results:
        results = _search_duckduckgo(query.strip(), target)

    return results
