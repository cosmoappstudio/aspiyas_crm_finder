"use client";

import Link from "next/link";
import { CompaniesTable } from "@/components/companies/CompaniesTable";

export default function MarkaListesiPage() {
  return (
    <main className="min-h-screen bg-slate-50 p-8">
      <div className="mx-auto max-w-5xl">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Marka Listesi</h1>
            <p className="mt-1 text-slate-600">
              Keşfedilen markaları görüntüle, seç ve Yetkili Bul ile enrichment kuyruğuna ekle
            </p>
          </div>
          <div className="flex gap-4">
            <Link
              href="/companies"
              className="text-sm font-medium text-slate-600 hover:text-slate-900"
            >
              ← Marka Keşfi
            </Link>
            <Link
              href="/crm"
              className="text-sm font-medium text-slate-600 hover:text-slate-900"
            >
              CRM →
            </Link>
            <Link
              href="/"
              className="text-sm text-slate-600 hover:text-slate-900"
            >
              Ana sayfa
            </Link>
          </div>
        </div>

        <CompaniesTable />
      </div>
    </main>
  );
}
