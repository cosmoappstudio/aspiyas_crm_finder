"use client";

import Link from "next/link";
import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  discoveryGoogle,
  discoveryAgency,
  discoveryCsv,
  addCompaniesToBulk,
  type DiscoveryItem,
} from "@/lib/api";

type Source = "google" | "agency" | "csv";

function domainToName(domain: string | null | undefined) {
  if (!domain) return "—";
  const base = domain.split(".")[0];
  return base.replace(/-/g, " ").replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function DiscoveryForm() {
  const [source, setSource] = useState<Source>("google");
  const [query, setQuery] = useState("");
  const [agencyUrl, setAgencyUrl] = useState("");
  const [csvContent, setCsvContent] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [results, setResults] = useState<DiscoveryItem[]>([]);
  const [selected, setSelected] = useState<Set<number>>(new Set());

  const queryClient = useQueryClient();
  const searchMutation = useMutation({
    mutationFn: async () => {
      if (source === "google") return discoveryGoogle(query, 150);
      if (source === "agency") return discoveryAgency(agencyUrl, 200);
      if (source === "csv") return discoveryCsv(csvContent);
      throw new Error("Kaynak seçilmedi");
    },
    onSuccess: (data) => {
      const items = (data?.data ?? []) as DiscoveryItem[];
      setResults(items);
      setSelected(new Set());
    },
  });

  const addMutation = useMutation({
    mutationFn: (items: DiscoveryItem[]) => addCompaniesToBulk(items),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["companies"] });
      setResults([]);
      setSelected(new Set());
    },
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) {
      setFile(f);
      const reader = new FileReader();
      reader.onload = () => setCsvContent(String(reader.result));
      reader.readAsText(f, "utf-8");
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (source === "google" && !query.trim()) return;
    if (source === "agency" && !agencyUrl.trim()) return;
    if (source === "csv" && !csvContent.trim()) return;
    searchMutation.mutate();
  };

  const toggleSelect = (idx: number) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(idx)) next.delete(idx);
      else next.add(idx);
      return next;
    });
  };

  const toggleAll = () => {
    if (selected.size === results.length) {
      setSelected(new Set());
    } else {
      setSelected(new Set(results.map((_, i) => i)));
    }
  };

  const handleAddToList = () => {
    const items = Array.from(selected).map((i) => results[i]);
    if (items.length === 0) return;
    addMutation.mutate(items);
  };

  return (
    <div className="space-y-6">
      <form onSubmit={handleSearch} className="space-y-4 rounded-lg border p-4">
        <div className="flex gap-2">
          {(["google", "agency", "csv"] as const).map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => setSource(s)}
              className={`rounded px-3 py-1.5 text-sm font-medium ${
                source === s
                  ? "bg-slate-800 text-white"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              {s === "google" && "Google Arama"}
              {s === "agency" && "Ajans Referans"}
              {s === "csv" && "CSV Yükle"}
            </button>
          ))}
        </div>

        {source === "google" && (
          <div>
            <label className="block text-sm font-medium text-slate-700">
              Arama sorgusu
            </label>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="tekstil e-ticaret markası"
              className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500"
            />
          </div>
        )}

        {source === "agency" && (
          <div>
            <label className="block text-sm font-medium text-slate-700">
              Ajans referans sayfası URL
            </label>
            <input
              type="url"
              value={agencyUrl}
              onChange={(e) => setAgencyUrl(e.target.value)}
              placeholder="https://ajans.com/referanslar"
              className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500"
            />
          </div>
        )}

        {source === "csv" && (
          <div>
            <label className="block text-sm font-medium text-slate-700">
              CSV dosyası (name, domain veya website_url)
            </label>
            <input
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="mt-1 block w-full text-sm text-slate-600 file:mr-4 file:rounded file:border-0 file:bg-slate-100 file:px-4 file:py-2 file:text-sm file:font-medium"
            />
            {file && (
              <p className="mt-1 text-xs text-slate-500">{file.name} yüklendi</p>
            )}
          </div>
        )}

        <button
          type="submit"
          disabled={searchMutation.isPending}
          className="rounded bg-slate-800 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-50"
        >
          {searchMutation.isPending ? "Aranıyor..." : "Marka Ara"}
        </button>

        {searchMutation.isError && (
          <p className="text-sm text-red-600">{String(searchMutation.error)}</p>
        )}
        {searchMutation.isSuccess && searchMutation.data?.message && (
          <p className="text-sm text-green-600">{searchMutation.data.message}</p>
        )}
      </form>

      {/* Sonuçlar — seçip listeye ekle */}
      {results.length > 0 && (
        <div className="space-y-4 rounded-lg border p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-slate-600">
              {results.length} sonuç • {selected.size} seçili
            </span>
            <button
              onClick={handleAddToList}
              disabled={selected.size === 0 || addMutation.isPending}
              className="rounded bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
            >
              {addMutation.isPending ? "Ekleniyor..." : "Listeye Ekle"}
            </button>
          </div>

          <div className="max-h-96 overflow-auto rounded border">
            <table className="min-w-full text-sm">
              <thead className="sticky top-0 bg-slate-50">
                <tr>
                  <th className="w-10 px-4 py-2 text-left">
                    <input
                      type="checkbox"
                      checked={selected.size === results.length && results.length > 0}
                      onChange={toggleAll}
                      className="rounded border-slate-300"
                    />
                  </th>
                  <th className="px-4 py-2 text-left font-medium">Marka</th>
                  <th className="px-4 py-2 text-left font-medium">Domain</th>
                  <th className="px-4 py-2 text-left font-medium">Kaynak</th>
                </tr>
              </thead>
              <tbody>
                {results.map((r, idx) => (
                  <tr
                    key={idx}
                    className="border-t border-slate-100 hover:bg-slate-50"
                  >
                    <td className="px-4 py-2">
                      <input
                        type="checkbox"
                        checked={selected.has(idx)}
                        onChange={() => toggleSelect(idx)}
                        className="rounded border-slate-300"
                      />
                    </td>
                    <td className="px-4 py-2 font-medium">
                      {domainToName(r.domain)}
                    </td>
                    <td className="px-4 py-2 text-slate-600">{r.domain ?? "—"}</td>
                    <td className="px-4 py-2 text-slate-600">{r.source}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {addMutation.isError && (
            <p className="text-sm text-red-600">{String(addMutation.error)}</p>
          )}
          {addMutation.isSuccess && addMutation.data?.message && (
            <p className="text-sm text-green-600">
              {addMutation.data.message}{" "}
              <Link
                href="/marka-listesi"
                className="font-medium underline hover:no-underline"
              >
                Marka Listesi →
              </Link>
            </p>
          )}
        </div>
      )}
    </div>
  );
}
