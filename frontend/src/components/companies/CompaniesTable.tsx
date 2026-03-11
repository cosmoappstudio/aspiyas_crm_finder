"use client";

import Link from "next/link";
import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { getCompanies, bulkEnrich, updateCompany, deleteCompany } from "@/lib/api";
import { useSelectionStore } from "@/store/selection";
import type { Company } from "@/types";

const STATUS_LABELS: Record<string, string> = {
  pending: "Bekliyor",
  processing: "İşleniyor",
  completed: "Tamamlandı",
  failed: "Hata",
};

function domainToName(domain: string | null) {
  if (!domain) return "—";
  const base = domain.split(".")[0];
  return base.replace(/-/g, " ").replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function CompaniesTable() {
  const queryClient = useQueryClient();
  const { data: companies = [], isLoading } = useQuery({
    queryKey: ["companies"],
    queryFn: () => getCompanies(),
  });

  const {
    selectedCompanyIds,
    toggle,
    toggleAll,
    isSelected,
  } = useSelectionStore();

  const [enriching, setEnriching] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState({ name: "", domain: "", website_url: "" });
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const enrichMutation = useMutation({
    mutationFn: (ids: string[]) => bulkEnrich(ids),
    onSuccess: () => {
      useSelectionStore.getState().clear();
      setEnriching(false);
      queryClient.invalidateQueries({ queryKey: ["companies"] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: { name?: string; domain?: string; website_url?: string } }) =>
      updateCompany(id, data),
    onSuccess: () => {
      setEditingId(null);
      queryClient.invalidateQueries({ queryKey: ["companies"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteCompany(id),
    onSuccess: (_, id) => {
      setDeletingId(null);
      useSelectionStore.getState().toggle(id);
      queryClient.invalidateQueries({ queryKey: ["companies"] });
    },
  });

  const handleEnrich = () => {
    const ids = Array.from(selectedCompanyIds);
    if (ids.length === 0) return;
    setEnriching(true);
    enrichMutation.mutate(ids);
  };

  const openEdit = (c: Company) => {
    setEditingId(c.id);
    setEditForm({
      name: c.name || domainToName(c.domain),
      domain: c.domain ?? "",
      website_url: c.website_url ?? "",
    });
  };

  const saveEdit = () => {
    if (!editingId) return;
    const data: { name?: string; domain?: string; website_url?: string } = {};
    if (editForm.name.trim()) data.name = editForm.name.trim();
    if (editForm.domain.trim()) data.domain = editForm.domain.trim();
    if (editForm.website_url.trim()) data.website_url = editForm.website_url.trim();
    if (Object.keys(data).length === 0) {
      setEditingId(null);
      return;
    }
    updateMutation.mutate({ id: editingId, data });
  };

  const allIds = companies.map((c) => c.id);
  const allSelected = allIds.length > 0 && allIds.every((id) => isSelected(id));

  if (isLoading) {
    return <p className="p-4 text-slate-500">Yükleniyor...</p>;
  }

  if (companies.length === 0) {
    return (
      <p className="rounded-lg border border-dashed p-8 text-center text-slate-500">
        Henüz marka yok.{" "}
        <Link href="/companies" className="text-slate-700 underline hover:text-slate-900">
          Marka Keşfi
        </Link>{" "}
        sayfasından arama yaparak ekleyebilirsin.
      </p>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <span className="text-sm text-slate-600">
          {companies.length} marka • {selectedCompanyIds.size} seçili
        </span>
        <button
          onClick={handleEnrich}
          disabled={selectedCompanyIds.size === 0 || enriching}
          className="rounded bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
        >
          {enriching ? "Ekleniyor..." : "Yetkili Bul"}
        </button>
      </div>

      <div className="overflow-x-auto rounded-lg border">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="w-10 px-4 py-2 text-left">
                <input
                  type="checkbox"
                  checked={allSelected}
                  onChange={() => toggleAll(allIds)}
                  className="rounded border-slate-300"
                />
              </th>
              <th className="px-4 py-2 text-left font-medium">Marka</th>
              <th className="px-4 py-2 text-left font-medium">Domain</th>
              <th className="px-4 py-2 text-left font-medium">Kaynak</th>
              <th className="px-4 py-2 text-left font-medium">Durum</th>
              <th className="w-24 px-4 py-2 text-right font-medium">İşlem</th>
            </tr>
          </thead>
          <tbody>
            {companies.map((c) => (
              <tr
                key={c.id}
                className="border-t border-slate-100 hover:bg-slate-50"
              >
                <td className="px-4 py-2">
                  <input
                    type="checkbox"
                    checked={isSelected(c.id)}
                    onChange={() => toggle(c.id)}
                    className="rounded border-slate-300"
                  />
                </td>
                <td className="px-4 py-2 font-medium">
                  {editingId === c.id ? (
                    <input
                      type="text"
                      value={editForm.name}
                      onChange={(e) => setEditForm((f) => ({ ...f, name: e.target.value }))}
                      className="w-full rounded border border-slate-300 px-2 py-1 text-sm"
                      placeholder="Marka adı"
                    />
                  ) : (
                    domainToName(c.domain)
                  )}
                </td>
                <td className="px-4 py-2 text-slate-600">
                  {editingId === c.id ? (
                    <input
                      type="text"
                      value={editForm.domain}
                      onChange={(e) => setEditForm((f) => ({ ...f, domain: e.target.value }))}
                      className="w-full rounded border border-slate-300 px-2 py-1 text-sm"
                      placeholder="domain.com"
                    />
                  ) : (
                    c.domain ?? "—"
                  )}
                </td>
                <td className="px-4 py-2 text-slate-600">{c.source}</td>
                <td className="px-4 py-2">
                  <span
                    className={`rounded px-2 py-0.5 text-xs ${
                      c.enrichment_status === "completed"
                        ? "bg-emerald-100 text-emerald-800"
                        : c.enrichment_status === "failed"
                          ? "bg-red-100 text-red-800"
                          : c.enrichment_status === "processing"
                            ? "bg-amber-100 text-amber-800"
                            : "bg-slate-100 text-slate-700"
                    }`}
                  >
                    {STATUS_LABELS[c.enrichment_status] ?? c.enrichment_status}
                  </span>
                </td>
                <td className="px-4 py-2 text-right">
                  {editingId === c.id ? (
                    <div className="flex justify-end gap-1">
                      <button
                        onClick={saveEdit}
                        disabled={updateMutation.isPending}
                        className="rounded bg-emerald-600 px-2 py-1 text-xs text-white hover:bg-emerald-700 disabled:opacity-50"
                      >
                        Kaydet
                      </button>
                      <button
                        onClick={() => setEditingId(null)}
                        className="rounded bg-slate-200 px-2 py-1 text-xs text-slate-700 hover:bg-slate-300"
                      >
                        İptal
                      </button>
                    </div>
                  ) : deletingId === c.id ? (
                    <div className="flex justify-end gap-1">
                      <span className="text-xs text-slate-600">Silmek istediğine emin misin?</span>
                      <button
                        onClick={() => deleteMutation.mutate(c.id)}
                        disabled={deleteMutation.isPending}
                        className="rounded bg-red-600 px-2 py-1 text-xs text-white hover:bg-red-700 disabled:opacity-50"
                      >
                        Evet
                      </button>
                      <button
                        onClick={() => setDeletingId(null)}
                        className="rounded bg-slate-200 px-2 py-1 text-xs text-slate-700 hover:bg-slate-300"
                      >
                        Hayır
                      </button>
                    </div>
                  ) : (
                    <div className="flex justify-end gap-1">
                      <button
                        onClick={() => openEdit(c)}
                        className="rounded p-1 text-slate-500 hover:bg-slate-200 hover:text-slate-700"
                        title="Düzenle"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                        </svg>
                      </button>
                      <button
                        onClick={() => setDeletingId(c.id)}
                        className="rounded p-1 text-slate-500 hover:bg-red-100 hover:text-red-600"
                        title="Sil"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <polyline points="3 6 5 6 21 6" />
                          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                          <line x1="10" y1="11" x2="10" y2="17" />
                          <line x1="14" y1="11" x2="14" y2="17" />
                        </svg>
                      </button>
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {enrichMutation.isError && (
        <p className="text-sm text-red-600">{String(enrichMutation.error)}</p>
      )}
      {enrichMutation.isSuccess && enrichMutation.data?.message && (
        <p className="text-sm text-green-600">{enrichMutation.data.message}</p>
      )}
      {updateMutation.isError && (
        <p className="text-sm text-red-600">{String(updateMutation.error)}</p>
      )}
      {updateMutation.isSuccess && updateMutation.data?.message && (
        <p className="text-sm text-green-600">{updateMutation.data.message}</p>
      )}
      {deleteMutation.isError && (
        <p className="text-sm text-red-600">{String(deleteMutation.error)}</p>
      )}
      {deleteMutation.isSuccess && deleteMutation.data?.message && (
        <p className="text-sm text-green-600">{deleteMutation.data.message}</p>
      )}
    </div>
  );
}
