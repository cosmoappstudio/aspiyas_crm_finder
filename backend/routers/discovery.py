"""
Discovery API — marka keşfi endpoint'leri
"""

import logging

from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from db.companies import create_companies_bulk, delete_company, list_companies, update_company
from db.enrichment_queue import add_to_queue
from discovery.pipeline import run_discovery
from models import ApiResponse, BulkEnrichRequest

router = APIRouter(prefix="/api", tags=["discovery"])
_logger = logging.getLogger(__name__)


class DiscoveryGoogleRequest(BaseModel):
    """Google arama isteği."""
    query: str = Field(..., min_length=1, description="Arama sorgusu (örn: tekstil e-ticaret markası)")
    max_results: int = Field(default=150, ge=1, le=300, description="Minimum 150 unique domain hedeflenir")


class DiscoveryAgencyRequest(BaseModel):
    """Ajans scrape isteği."""
    agency_url: str = Field(..., min_length=1, description="Ajans referans sayfası URL")
    max_results: int = Field(default=200, ge=1, le=500)


class DiscoveryCsvRequest(BaseModel):
    """CSV import isteği."""
    csv_content: str = Field(..., description="CSV dosya içeriği")


@router.post("/discovery/google", response_model=ApiResponse)
async def discovery_google(req: DiscoveryGoogleRequest):
    """
    Google/DuckDuckGo'da kategori araması yapar.
    Sonuçları döner — kullanıcı seçip listeye ekler.
    """
    items = run_discovery(source="google", query=req.query, max_results=req.max_results)
    if not items:
        return ApiResponse(success=True, message="Sonuç bulunamadı", data=[])
    return ApiResponse(success=True, message=f"{len(items)} sonuç bulundu", data=items)


@router.post("/discovery/agency", response_model=ApiResponse)
async def discovery_agency(req: DiscoveryAgencyRequest):
    """
    Ajans referans sayfasını scrape eder.
    Sonuçları döner — kullanıcı seçip listeye ekler.
    """
    items = run_discovery(
        source="agency",
        agency_url=req.agency_url,
        max_results=req.max_results,
    )
    if not items:
        return ApiResponse(success=True, message="Sonuç bulunamadı", data=[])
    return ApiResponse(success=True, message=f"{len(items)} sonuç bulundu", data=items)


@router.post("/discovery/csv", response_model=ApiResponse)
async def discovery_csv(req: DiscoveryCsvRequest):
    """
    CSV içeriğini parse eder.
    Sonuçları döner — kullanıcı seçip listeye ekler.
    """
    items = run_discovery(source="csv", csv_content=req.csv_content)
    if not items:
        return ApiResponse(success=False, message="CSV parse edilemedi veya geçerli satır yok", data=[])
    return ApiResponse(success=True, message=f"{len(items)} sonuç bulundu", data=items)


class CompanyItemInput(BaseModel):
    """Discovery sonucu — listeye eklenecek marka."""
    name: str
    domain: Optional[str] = None
    website_url: Optional[str] = None
    source: str = "google"
    source_metadata: Optional[dict] = None


class AddCompaniesRequest(BaseModel):
    """Seçili markaları listeye ekleme."""
    items: List[CompanyItemInput] = Field(..., min_length=1)


@router.post("/companies/bulk", response_model=ApiResponse)
async def add_companies_bulk(req: AddCompaniesRequest):
    """
    Seçili markaları Marka Listesi'ne ekler.
    Discovery sonuçlarından seçilenler bu endpoint ile kaydedilir.
    """
    items = [i.model_dump() for i in req.items]
    created = create_companies_bulk(items)
    return ApiResponse(success=True, message=f"{len(created)} marka listeye eklendi", data=created)


@router.get("/companies", response_model=ApiResponse)
async def get_companies(limit: int = 200, offset: int = 0):
    """Tüm markaları listeler."""
    companies = list_companies(limit=limit, offset=offset)
    return ApiResponse(success=True, data=companies)


class CompanyUpdateRequest(BaseModel):
    """Marka güncelleme."""
    name: Optional[str] = None
    domain: Optional[str] = None
    website_url: Optional[str] = None


@router.patch("/companies/{company_id}", response_model=ApiResponse)
async def update_company_endpoint(company_id: str, req: CompanyUpdateRequest):
    """Marka günceller."""
    from uuid import UUID
    try:
        uid = UUID(company_id)
    except ValueError:
        return ApiResponse(success=False, message="Geçersiz ID")
    data = {k: v for k, v in req.model_dump().items() if v is not None}
    if not data:
        return ApiResponse(success=False, message="Güncellenecek alan yok")
    updated = update_company(uid, **data)
    if not updated:
        return ApiResponse(success=False, message="Marka bulunamadı veya güncellenemedi")
    return ApiResponse(success=True, message="Marka güncellendi", data=updated)


@router.delete("/companies/{company_id}", response_model=ApiResponse)
async def delete_company_endpoint(company_id: str):
    """Markayı siler."""
    from uuid import UUID
    try:
        uid = UUID(company_id)
    except ValueError:
        return ApiResponse(success=False, message="Geçersiz ID")
    ok = delete_company(uid)
    if not ok:
        return ApiResponse(success=False, message="Marka silinemedi")
    return ApiResponse(success=True, message="Marka silindi")


@router.post("/enrichment/bulk", response_model=ApiResponse)
async def bulk_enrich(req: BulkEnrichRequest):
    """
    Seçili markaları enrichment kuyruğuna ekler.
    Arka planda worker işleyecek.
    """
    added = add_to_queue(req.company_ids)
    return ApiResponse(
        success=True,
        message=f"{added} marka kuyruğa eklendi",
        data={"added": added},
    )
