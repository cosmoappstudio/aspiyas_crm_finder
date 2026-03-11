/**
 * LeadRadar — Frontend tipleri
 * Backend models.py ile uyumlu
 */

export type CompanySource = "google" | "agency" | "csv";

export type EnrichmentStatus =
  | "pending"
  | "processing"
  | "completed"
  | "failed";

export type LeadStatus =
  | "ulasilmadi"
  | "ulasildi"
  | "beklemede"
  | "ilgileniyor"
  | "kapandi";

export type ActivityType = "status_change" | "note";

export interface Company {
  id: string;
  name: string;
  domain: string | null;
  website_url: string | null;
  source: CompanySource;
  source_metadata: Record<string, unknown> | null;
  enrichment_status: EnrichmentStatus;
  created_at: string;
  updated_at: string;
}

export interface Lead {
  id: string;
  company_id: string;
  name: string;
  email: string | null;
  phone: string | null;
  linkedin_url: string | null;
  title: string | null;
  status: LeadStatus;
  created_at: string;
  updated_at: string;
}

export interface LeadActivity {
  id: string;
  lead_id: string;
  activity_type: ActivityType;
  old_status: LeadStatus | null;
  new_status: LeadStatus | null;
  note: string | null;
  created_at: string;
}
