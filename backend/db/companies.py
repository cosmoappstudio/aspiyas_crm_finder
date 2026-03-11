"""
Companies tablosu işlemleri
"""

import logging
from datetime import datetime, timezone
from uuid import UUID

from models import CompanySource, EnrichmentStatus

from .client import get_supabase

_logger = logging.getLogger(__name__)


def create_company(
    name: str,
    source: str,
    domain=None,
    website_url=None,
    source_metadata=None,
):
    """
    Yeni marka oluşturur, Supabase'e kaydeder.
    Başarılıysa kayıt dict döner, hata varsa None.
    """
    try:
        sb = get_supabase()
        data = {
            "name": name,
            "domain": domain,
            "website_url": website_url,
            "source": source,
            "source_metadata": source_metadata,
            "enrichment_status": EnrichmentStatus.PENDING.value,
        }
        result = sb.table("companies").insert(data).execute()
        if result.data and len(result.data) > 0:
            _logger.info("🏢 Marka kaydedildi: %s", name)
            return result.data[0]
    except Exception as e:
        _logger.exception("❌ Marka kaydetme hatası: %s", e)
    return None


def create_companies_bulk(items: list[dict]) -> list[dict]:
    """
    Toplu marka kaydı. Her öğe: {name, domain?, website_url?, source, source_metadata?}
    Mevcut domain'leri atlar (duplicate check).
    """
    if not items:
        return []

    try:
        sb = get_supabase()
        # Mevcut domain'leri al
        domains = [i.get("domain") for i in items if i.get("domain")]
        existing = set()
        if domains:
            r = sb.table("companies").select("domain").in_("domain", domains).execute()
            existing = {row["domain"] for row in (r.data or []) if row.get("domain")}

        to_insert = []
        for item in items:
            domain = item.get("domain")
            if domain and domain in existing:
                continue
            if domain:
                existing.add(domain)
            to_insert.append({
                "name": item.get("name", "Bilinmeyen"),
                "domain": domain,
                "website_url": item.get("website_url"),
                "source": item.get("source", "csv"),
                "source_metadata": item.get("source_metadata"),
                "enrichment_status": EnrichmentStatus.PENDING.value,
            })

        if not to_insert:
            return []

        result = sb.table("companies").insert(to_insert).execute()
        created = result.data or []
        _logger.info("✅ %d marka kaydedildi", len(created))
        return created
    except Exception as e:
        _logger.exception("❌ Toplu marka kaydetme hatası: %s", e)
        return []


def list_companies(limit: int = 200, offset: int = 0) -> list[dict]:
    """Tüm markaları listeler."""
    try:
        sb = get_supabase()
        r = (
            sb.table("companies")
            .select("*")
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return r.data or []
    except Exception as e:
        _logger.exception("❌ Marka listeleme hatası: %s", e)
        return []


def get_company_by_id(company_id: UUID):
    """ID ile marka getirir."""
    try:
        sb = get_supabase()
        r = sb.table("companies").select("*").eq("id", str(company_id)).execute()
        if r.data and len(r.data) > 0:
            return r.data[0]
    except Exception as e:
        _logger.exception("❌ Marka getirme hatası: %s", e)
    return None


def update_company(company_id: UUID, name=None, domain=None, website_url=None):
    """
    Marka günceller. Verilen alanlar güncellenir.
    """
    try:
        sb = get_supabase()
        data = {}
        if name is not None:
            data["name"] = name
        if domain is not None:
            data["domain"] = domain
        if website_url is not None:
            data["website_url"] = website_url
        if not data:
            return get_company_by_id(company_id)
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        r = sb.table("companies").update(data).eq("id", str(company_id)).execute()
        if r.data and len(r.data) > 0:
            _logger.info("🏢 Marka güncellendi: %s", company_id)
            return r.data[0]
    except Exception as e:
        _logger.exception("❌ Marka güncelleme hatası: %s", e)
    return None


def delete_company(company_id: UUID) -> bool:
    """Markayı siler. Cascade ile lead'ler ve kuyruk kayıtları da silinir."""
    try:
        sb = get_supabase()
        sb.table("companies").delete().eq("id", str(company_id)).execute()
        _logger.info("🏢 Marka silindi: %s", company_id)
        return True
    except Exception as e:
        _logger.exception("❌ Marka silme hatası: %s", e)
    return False
