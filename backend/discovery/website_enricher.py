"""
Website enricher
Domain/URL'den marka adı ve ek bilgi çıkarır.
"""

import logging
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

_logger = logging.getLogger(__name__)


def _extract_domain(url_or_domain: str):
    """URL veya domain'den domain çıkarır."""
    s = (url_or_domain or "").strip().lower()
    if not s:
        return None
    if "://" in s:
        parsed = urlparse(s)
        domain = parsed.netloc or ""
    else:
        domain = s
    if domain.startswith("www."):
        domain = domain[4:]
    return domain if domain and "." in domain else None


def _domain_to_name(domain: str) -> str:
    """Domain'den fallback marka adı üretir (örn: marka.com -> Marka)."""
    if not domain:
        return "Bilinmeyen"
    base = domain.split(".")[0]
    return base.replace("-", " ").replace("_", " ").title()


def enrich_from_website(url_or_domain: str) -> dict:
    """
    URL veya domain'den marka bilgisi zenginleştirir.
    Sayfa title/meta'dan isim çeker, yoksa domain'den üretir.
    Döner: {name, domain, website_url} veya boş dict (hata durumunda)
    """
    if not url_or_domain or not url_or_domain.strip():
        return {}

    raw = url_or_domain.strip()
    domain = _extract_domain(raw)
    if not domain:
        return {}

    website_url = raw if raw.startswith("http") else f"https://{domain}"

    try:
        resp = httpx.get(
            website_url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; LeadRadar/1.0)"},
            timeout=10,
            follow_redirects=True,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        name = None
        # Önce og:site_name
        og = soup.find("meta", property="og:site_name")
        if og and og.get("content"):
            name = og["content"].strip()[:200]
        # Sonra title
        if not name and soup.title and soup.title.string:
            title = soup.title.string.strip()
            # "Marka Adı | Slogan" veya "Marka - Ana Sayfa" formatları
            for sep in [" | ", " – ", " - ", " — "]:
                if sep in title:
                    title = title.split(sep)[0].strip()
            if title and len(title) < 150:
                name = title[:200]
        # Fallback
        if not name:
            name = _domain_to_name(domain)

        return {
            "name": name,
            "domain": domain,
            "website_url": website_url,
        }
    except Exception as e:
        _logger.debug("Website enrich atlandı (%s): %s", domain, e)
        return {
            "name": _domain_to_name(domain),
            "domain": domain,
            "website_url": website_url,
        }
