"""
Apollo.io REST API entegrasyonu
Company search + People search ile yetkili bulma.
Rate limit: istekler arası min 1.2 saniye.
"""

import os
import time
from typing import Optional

import httpx
from dotenv import load_dotenv

load_dotenv()

APOLLO_BASE = "https://api.apollo.io/v1"
RATE_LIMIT_DELAY = 1.2  # saniye

# Aranacak unvanlar
TARGET_TITLES = [
    "Owner", "Co-Founder", "CMO",
    "Pazarlama Müdürü", "Marketing Manager",
    "Head of Marketing", "Digital Marketing Manager",
]


def _get_api_key() -> str:
    """Apollo API key — env'den."""
    key = os.getenv("APOLLO_API_KEY")
    if not key:
        raise ValueError("APOLLO_API_KEY env'de tanımlı olmalı")
    return key


def _rate_limit():
    """İstekler arası bekleme."""
    time.sleep(RATE_LIMIT_DELAY)


def search_company(domain: str) -> Optional[dict]:
    """
    Domain ile Apollo'da şirket arar.
    Bulunursa şirket bilgisi döner, yoksa None.
    """
    # TODO: B3'te implement
    _rate_limit()
    return None


def search_people(domain: str, limit: int = 10) -> list[dict]:
    """
    Domain'e göre Apollo'da kişi arar.
    TARGET_TITLES ile filtreler.
    Her öğe: {name, email, phone, linkedin_url, title}
    """
    # TODO: B3'te implement
    _rate_limit()
    return []


def enrich_company(domain: str) -> list[dict]:
    """
    Bir marka için tam enrichment: company + people.
    Bulunan yetkilileri liste olarak döner.
    """
    company = search_company(domain)
    if not company:
        return []
    people = search_people(domain)
    return people
