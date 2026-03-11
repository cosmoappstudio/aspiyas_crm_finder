"""
CSV marka import
Kullanıcı CSV yükleyerek marka listesi oluşturur.
"""

import csv
import logging
from io import StringIO
from urllib.parse import urlparse

_logger = logging.getLogger(__name__)


def _extract_domain(url_or_domain: str):
    """URL veya domain'den temiz domain çıkarır."""
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


def _normalize_column(name: str) -> str:
    """Sütun adını normalize eder (name, domain, website_url, url)."""
    n = name.strip().lower().replace(" ", "_").replace("-", "_")
    mapping = {
        "name": "name", "isim": "name", "marka": "name", "company": "name",
        "domain": "domain", "domain_name": "domain", "site": "domain",
        "website_url": "website_url", "url": "website_url", "website": "website_url",
        "link": "website_url", "web": "website_url",
    }
    return mapping.get(n, n)


def import_from_csv(csv_content: str, encoding: str = "utf-8") -> list[dict]:
    """
    CSV içeriğini parse eder, marka listesi döner.
    Sütunlar: name, domain veya website_url (Türkçe/İngilizce varyasyonlar desteklenir)
    Her öğe: {name, domain?, website_url?, source: "csv"}
    """
    if not csv_content or not csv_content.strip():
        return []

    try:
        # Encoding denemesi
        try:
            content = csv_content.encode("utf-8").decode(encoding)
        except (UnicodeDecodeError, LookupError):
            content = csv_content

        reader = csv.DictReader(StringIO(content))
        if not reader.fieldnames:
            return []

        # Sütun eşlemesi
        col_map = {}
        for f in reader.fieldnames:
            norm = _normalize_column(f)
            if norm in ("name", "domain", "website_url"):
                col_map[norm] = f

        if "name" not in col_map and "domain" not in col_map and "website_url" not in col_map:
            _logger.warning("CSV'de name, domain veya website_url sütunu bulunamadı")
            return []

        results = []
        seen = set()

        for row in reader:
            name = ""
            domain = None
            website_url = None

            if "name" in col_map:
                name = (row.get(col_map["name"]) or "").strip()
            if "domain" in col_map:
                val = (row.get(col_map["domain"]) or "").strip()
                if val:
                    domain = _extract_domain(val) or val
            if "website_url" in col_map:
                val = (row.get(col_map["website_url"]) or "").strip()
                if val:
                    website_url = val if val.startswith("http") else f"https://{val}"
                    if not domain:
                        domain = _extract_domain(website_url)

            if not domain and not name:
                continue
            if not domain:
                domain = _extract_domain(name) or name
            if not name:
                name = domain

            # Dedupe
            key = domain.lower()
            if key in seen:
                continue
            seen.add(key)

            results.append({
                "name": name[:200],
                "domain": domain,
                "website_url": website_url or (f"https://{domain}" if domain else None),
                "source": "csv",
                "source_metadata": None,
            })

        _logger.info("✅ CSV import: %d marka yüklendi", len(results))
        return results
    except Exception as e:
        _logger.exception("❌ CSV import hatası: %s", e)
        return []
