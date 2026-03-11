"""
Enrichment kuyruk worker
Startup'ta başlar, sürekli kuyruğu dinler.
Her marka için Apollo enrichment → Supabase'e lead kaydet → Realtime push.
"""

import logging
import threading
from typing import Optional

# TODO: B3'te tam implement
# - Supabase enrichment_queue tablosundan pending al
# - Apollo enrich_company çağır
# - Lead'leri Supabase leads tablosuna yaz
# - Realtime otomatik frontend'e push eder

_logger = logging.getLogger(__name__)
_worker_thread: Optional[threading.Thread] = None
_stop_event: Optional[threading.Event] = None


def _run_worker():
    """Worker döngüsü — arka planda çalışır."""
    _logger.info("🔄 Enrichment worker başlatıldı")
    while _stop_event and not _stop_event.is_set():
        try:
            # TODO: Kuyruktan bir öğe al, işle
            _stop_event.wait(timeout=5)  # 5 sn bekleyip tekrar kontrol
        except Exception as e:
            _logger.exception("❌ Worker hatası: %s", e)


def start_queue_worker():
    """Worker thread'ini başlatır."""
    global _worker_thread, _stop_event
    _stop_event = threading.Event()
    _worker_thread = threading.Thread(target=_run_worker, daemon=True)
    _worker_thread.start()
    _logger.info("📋 Enrichment kuyruğu dinleniyor")


def stop_queue_worker():
    """Worker'ı durdurur."""
    global _stop_event
    if _stop_event:
        _stop_event.set()
        _logger.info("📋 Enrichment worker durduruldu")
