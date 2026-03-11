"use client";

import Link from "next/link";
import { DiscoveryForm } from "@/components/companies/DiscoveryForm";

export default function CompaniesPage() {
  return (
    <main className="min-h-screen bg-slate-50 p-8">
      <div className="mx-auto max-w-5xl">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Marka Keşfi</h1>
            <p className="mt-1 text-slate-600">
              Google arama, ajans referansı veya CSV ile marka bul ve listeye ekle
            </p>
          </div>
          <div className="flex gap-4">
            <Link
              href="/marka-listesi"
              className="text-sm font-medium text-slate-600 hover:text-slate-900"
            >
              Marka Listesi →
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
              ← Ana sayfa
            </Link>
          </div>
        </div>

        <div className="mb-8">
          <DiscoveryForm />
        </div>

        <p className="text-sm text-slate-500">
          Arama yap → Sonuçlardan seç → &quot;Listeye Ekle&quot; ile Marka Listesi&apos;ne ekle.{" "}
          <Link href="/marka-listesi" className="text-slate-700 underline hover:text-slate-900">
            Marka Listesi
          </Link>{" "}
          sayfasından seçip &quot;Yetkili Bul&quot; ile enrichment kuyruğuna ekleyebilirsin.
        </p>
      </div>
    </main>
  );
}
