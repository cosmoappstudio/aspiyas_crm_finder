/**
 * Backend API istemcisi
 * FastAPI endpoint'lerine istek atar
 */

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ApiResponse<T = unknown> {
  success: boolean;
  message?: string;
  data?: T;
}

export async function fetchApi<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "API hatası");
  }
  return res.json();
}

// Discovery
export async function discoveryGoogle(query: string, maxResults = 150) {
  return fetchApi<ApiResponse<{ id: string }[]>>("/api/discovery/google", {
    method: "POST",
    body: JSON.stringify({ query, max_results: maxResults }),
  });
}

export async function discoveryAgency(agencyUrl: string, maxResults = 200) {
  return fetchApi<ApiResponse<{ id: string }[]>>("/api/discovery/agency", {
    method: "POST",
    body: JSON.stringify({ agency_url: agencyUrl, max_results: maxResults }),
  });
}

export async function discoveryCsv(csvContent: string) {
  return fetchApi<ApiResponse<{ id: string }[]>>("/api/discovery/csv", {
    method: "POST",
    body: JSON.stringify({ csv_content: csvContent }),
  });
}

// Companies
export async function getCompanies(limit = 200, offset = 0) {
  const res = await fetchApi<ApiResponse<import("@/types").Company[]>>(
    `/api/companies?limit=${limit}&offset=${offset}`
  );
  return (res.data ?? []) as import("@/types").Company[];
}

export interface DiscoveryItem {
  name: string;
  domain?: string | null;
  website_url?: string | null;
  source: string;
  source_metadata?: Record<string, unknown> | null;
}

export async function addCompaniesToBulk(items: DiscoveryItem[]) {
  return fetchApi<ApiResponse<{ id: string }[]>>("/api/companies/bulk", {
    method: "POST",
    body: JSON.stringify({ items }),
  });
}

export async function updateCompany(
  id: string,
  data: { name?: string; domain?: string; website_url?: string }
) {
  return fetchApi<ApiResponse<import("@/types").Company>>(
    `/api/companies/${id}`,
    {
      method: "PATCH",
      body: JSON.stringify(data),
    }
  );
}

export async function deleteCompany(id: string) {
  return fetchApi<ApiResponse<null>>(`/api/companies/${id}`, {
    method: "DELETE",
  });
}

// Enrichment
export async function bulkEnrich(companyIds: string[]) {
  return fetchApi<ApiResponse<{ added: number }>>("/api/enrichment/bulk", {
    method: "POST",
    body: JSON.stringify({ company_ids: companyIds }),
  });
}
