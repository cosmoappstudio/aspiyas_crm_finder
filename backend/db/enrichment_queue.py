"""
Enrichment kuyruğu işlemleri
"""

import logging
from uuid import UUID

from models import EnrichmentStatus

from .client import get_supabase

_logger = logging.getLogger(__name__)


def add_to_queue(company_ids: list[UUID], priority: int = 0) -> int:
    """
    Markaları enrichment kuyruğuna ekler.
    Zaten kuyrukta veya işlenmiş olanları atlar.
    Eklenen öğe sayısını döner.
    """
    if not company_ids:
        return 0

    try:
        sb = get_supabase()

        # Zaten pending/processing olanları kontrol et
        ids_str = [str(cid) for cid in company_ids]
        r = (
            sb.table("enrichment_queue")
            .select("company_id")
            .in_("company_id", ids_str)
            .in_("status", ["pending", "processing"])
            .execute()
        )
        existing = {row["company_id"] for row in (r.data or [])}

        to_add = [cid for cid in company_ids if str(cid) not in existing]
        if not to_add:
            _logger.info("📋 Tüm markalar zaten kuyrukta")
            return 0

        items = [
            {"company_id": str(cid), "priority": priority, "status": EnrichmentStatus.PENDING.value}
            for cid in to_add
        ]
        result = sb.table("enrichment_queue").insert(items).execute()
        added = len(result.data or [])
        _logger.info("📋 %d marka kuyruğa eklendi", added)
        return added
    except Exception as e:
        _logger.exception("❌ Kuyruk ekleme hatası: %s", e)
        return 0
