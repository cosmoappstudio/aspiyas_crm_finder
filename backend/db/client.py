"""
Supabase veritabanı istemcisi
Tüm DB işlemleri bu modül üzerinden.
"""

import os
from typing import Optional

from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_supabase: Optional[Client] = None


def get_supabase() -> Client:
    """Supabase client singleton — env'den URL ve key alır."""
    global _supabase
    if _supabase is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL ve SUPABASE_SERVICE_KEY (veya SUPABASE_ANON_KEY) env'de tanımlı olmalı")
        _supabase = create_client(url, key)
    return _supabase
