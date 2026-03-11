"""
LeadRadar — Veri modelleri
Pydantic modelleri ve enum tanımları.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field


# ============== Enums ==============


class CompanySource(str, Enum):
    """Marka kaynağı: Google arama, ajans referansı veya CSV."""
    GOOGLE = "google"
    AGENCY = "agency"
    CSV = "csv"


class EnrichmentStatus(str, Enum):
    """Enrichment kuyruğu durumu."""
    PENDING = "pending"      # Kuyrukta bekliyor
    PROCESSING = "processing"  # İşleniyor
    COMPLETED = "completed"   # Tamamlandı
    FAILED = "failed"        # Hata aldı


class LeadStatus(str, Enum):
    """Lead CRM durumu."""
    ULASILMADI = "ulasilmadi"      # Ulaşılmadı
    ULASILDI = "ulasildi"         # Ulaşıldı
    BEKLEMEDE = "beklemede"       # Beklemede
    ILGILENIYOR = "ilgileniyor"   # İlgileniyor
    KAPANDI = "kapandi"           # Kapandı


class ActivityType(str, Enum):
    """Lead aktivite tipi (timeline)."""
    STATUS_CHANGE = "status_change"
    NOTE = "note"


# ============== Base Schemas ==============


class CompanyBase(BaseModel):
    """Marka temel alanları."""
    name: str = Field(..., description="Marka adı")
    domain: Optional[str] = Field(None, description="Domain (örn: marka.com)")
    website_url: Optional[str] = Field(None, description="Tam website URL")
    source: CompanySource = Field(..., description="Kaynak")
    source_metadata: Optional[dict] = Field(None, description="Kaynak ek bilgisi (arama sorgusu, ajans URL vb)")


class CompanyCreate(CompanyBase):
    """Marka oluşturma."""
    pass


class Company(CompanyBase):
    """Marka — DB'den gelen tam model."""
    id: UUID
    enrichment_status: EnrichmentStatus = EnrichmentStatus.PENDING
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompanyInList(Company):
    """Marka listesi için — seçim bilgisi eklenebilir."""
    pass


# ============== Lead Schemas ==============


class LeadBase(BaseModel):
    """Lead temel alanları."""
    name: str = Field(..., description="İsim")
    email: Optional[str] = Field(None, description="E-posta")
    phone: Optional[str] = Field(None, description="Telefon")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profili")
    title: Optional[str] = Field(None, description="Unvan")


class LeadCreate(LeadBase):
    """Lead oluşturma — enrichment'dan gelir."""
    company_id: UUID


class Lead(LeadBase):
    """Lead — DB'den gelen tam model."""
    id: UUID
    company_id: UUID
    status: LeadStatus = LeadStatus.ULASILMADI
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeadUpdate(BaseModel):
    """Lead güncelleme — sadece status değişebilir."""
    status: Optional[LeadStatus] = None


# ============== Activity / Timeline ==============


class LeadActivityBase(BaseModel):
    """Aktivite temel alanları."""
    activity_type: ActivityType
    old_status: Optional[LeadStatus] = None
    new_status: Optional[LeadStatus] = None
    note: Optional[str] = None


class LeadActivityCreate(LeadActivityBase):
    """Aktivite oluşturma."""
    lead_id: UUID


class LeadActivity(LeadActivityBase):
    """Aktivite — timeline kaydı."""
    id: UUID
    lead_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ============== Enrichment Queue ==============


class EnrichmentQueueItemBase(BaseModel):
    """Kuyruk öğesi temel alanları."""
    company_id: UUID
    priority: int = Field(default=0, description="Öncelik (yüksek = önce)")


class EnrichmentQueueItemCreate(EnrichmentQueueItemBase):
    """Kuyruk öğesi oluşturma."""
    pass


class EnrichmentQueueItem(EnrichmentQueueItemBase):
    """Kuyruk öğesi — DB'den gelen tam model."""
    id: UUID
    status: EnrichmentStatus = EnrichmentStatus.PENDING
    created_at: datetime
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


# ============== API Request/Response ==============


class BulkEnrichRequest(BaseModel):
    """Toplu enrichment isteği — seçili marka ID'leri."""
    company_ids: list[UUID] = Field(..., min_length=1, description="Enrichment'a eklenecek marka ID'leri")


class ApiResponse(BaseModel):
    """Genel API yanıtı."""
    success: bool = True
    message: Optional[str] = None
    data: Optional[Union[dict, list]] = None
