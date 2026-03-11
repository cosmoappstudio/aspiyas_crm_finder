import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen p-8">
      <h1 className="text-2xl font-bold">LeadRadar</h1>
      <p className="mt-2 text-muted-foreground">
        B2B Lead Intelligence Platformu
      </p>
      <nav className="mt-6 flex gap-4">
        <Link
          href="/companies"
          className="text-primary hover:underline"
        >
          Marka Keşfi
        </Link>
        <Link
          href="/marka-listesi"
          className="text-primary hover:underline"
        >
          Marka Listesi
        </Link>
        <Link
          href="/crm"
          className="text-primary hover:underline"
        >
          CRM
        </Link>
      </nav>
    </main>
  );
}
