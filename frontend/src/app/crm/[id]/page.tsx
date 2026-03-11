export default function LeadDetailPage({
  params,
}: {
  params: { id: string };
}) {
  return (
    <main className="min-h-screen p-8">
      <h1 className="text-2xl font-bold">Lead Detay</h1>
      <p className="mt-2 text-muted-foreground">ID: {params.id}</p>
      {/* TODO: B4 — Lead detay, timeline, not ekleme */}
    </main>
  );
}
