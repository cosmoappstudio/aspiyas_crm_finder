"""
Ajans referans sayfası scraper
Rakip ajans sitesinin referanslar bölümünden marka listesi çeker.
"""

import logging
import re
import time
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

_logger = logging.getLogger(__name__)

REQUEST_DELAY = 1.5


def _extract_domain(url: str):
    """URL'den domain çıkarır."""
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


def _is_valid_domain(domain: str, agency_domain: str) -> bool:
    """Kendi sitesi, sosyal medya, mailto vb. filtrele."""
    if not domain or len(domain) < 4:
        return False
    # Ajansın kendi domain'i
    if agency_domain in domain or domain in agency_domain:
        return False
    skip = [
        "google.", "youtube.", "facebook.", "instagram.", "twitter.",
        "linkedin.", "wikipedia.", "amazon.", "ebay.", "apple.",
        "microsoft.", "github.", "wikipedia.", "youtu.be",
        "mail.", "email.", "cdn.", "static.", "img.", "image.",
    ]
    return not any(d in domain for d in skip)


def scrape_agency_references(agency_url: str, max_results: int = 200) -> list[dict]:
    """
    Ajans sitesinin referanslar sayfasını scrape eder.
    Sayfadaki harici linkleri toplar, domain'leri marka olarak döner.
    Her öğe: {name, domain, website_url, source: "agency", source_metadata}
    """
    if not agency_url or not agency_url.strip():
        return []

    url = agency_url.strip()
    if not url.startswith("http"):
        url = "https://" + url

    agency_domain = _extract_domain(url) or ""

    try:
        time.sleep(REQUEST_DELAY)
        resp = httpx.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            },
            timeout=15,
            follow_redirects=True,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        seen = set()
        results = []

        # Tüm harici linkleri tara
        for a in soup.find_all("a", href=True):
            if len(results) >= max_results:
                break
            href = a.get("href", "").strip()
            if not href or href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
                continue

            full_url = urljoin(url, href)
            if not full_url.startswith("http"):
                continue

            domain = _extract_domain(full_url)
            if not domain or domain in seen:
                continue
            if not _is_valid_domain(domain, agency_domain):
                continue

            seen.add(domain)
            # İsim: link metni veya domain
            name = a.get_text(strip=True) or domain
            if len(name) > 100:
                name = domain

            results.append({
                "name": name,
                "domain": domain,
                "website_url": full_url,
                "source": "agency",
                "source_metadata": {"agency_url": url},
            })

        _logger.info("✅ Ajans scrape: %d marka bulundu (%s)", len(results), url)
        return results
    except Exception as e:
        _logger.exception("❌ Ajans scrape hatası: %s", e)
        return []
