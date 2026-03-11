"""
Discovery pipeline
Tüm kaynakları birleştirip marka listesi üretir.
Google/Agency için domain'den marka adı türetir (uzun sayfa başlıkları yerine).
"""

import logging
from typing import Optional

from .agency_scraper import scrape_agency_references
from .csv_importer import import_from_csv
from .google_search import search_companies
from .website_enricher import _domain_to_name

_logger = logging.getLogger(__name__)


def _apply_domain_names(items: list[dict], source: str) -> list[dict]:
    """Google ve Agency kaynaklarında domain'den marka adı kullan (trendyol.com → Trendyol)."""
    if source not in ("google", "agency"):
        return items
    for item in items:
        domain = item.get("domain")
        if domain:
            item["name"] = _domain_to_name(domain)
    return items


def _deduplicate_by_domain(items: list[dict]) -> list[dict]:
    """Domain üzerinden tekrarları kaldırır, ilk geleni tutar."""
    seen = set()
    result = []
    for item in items:
        domain = (item.get("domain") or "").lower()
        if not domain or domain in seen:
            continue
        seen.add(domain)
        result.append(item)
    return result


def run_discovery(
    source: str,
    query: Optional[str] = None,
    agency_url: Optional[str] = None,
    csv_content: Optional[str] = None,
    max_results: int = 150,
) -> list[dict]:
    """
    Kaynağa göre discovery çalıştırır.
    source: "google" | "agency" | "csv"
    """
    items: list[dict] = []

    if source == "google":
        if not query or not query.strip():
            _logger.warning("Google araması için query gerekli")
            return []
        items = search_companies(query.strip(), max_results)

    elif source == "agency":
        if not agency_url or not agency_url.strip():
            _logger.warning("Ajans scrape için agency_url gerekli")
            return []
        items = scrape_agency_references(agency_url.strip(), max_results)

    elif source == "csv":
        if not csv_content:
            _logger.warning("CSV import için csv_content gerekli")
            return []
        items = import_from_csv(csv_content)

    else:
        _logger.warning("Bilinmeyen kaynak: %s", source)
        return []

    items = _apply_domain_names(items, source)
    return _deduplicate_by_domain(items)
