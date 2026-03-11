# LeadRadar

B2B Lead Intelligence Platformu — E-ticaret markalarını keşfet, yetkilileri bul, satış sürecini takip et.

## Proje Yapısı

```
leadradar/
├── backend/          # FastAPI
├── frontend/         # Next.js 14 App Router
├── supabase/         # SQL migrations
└── README.md
```

## Kurulum

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env     # Değerleri doldur
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local  # NEXT_PUBLIC_* değişkenleri
npm run dev
```

### Supabase

1. [Supabase](https://supabase.com) projesi oluştur
2. `supabase/migrations/001_initial_schema.sql` dosyasını SQL Editor'da çalıştır
3. Realtime'ı `leads` tablosu için Dashboard'dan etkinleştir

## Ortam Değişkenleri

**Backend (.env)**
- `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`
- `APOLLO_API_KEY`

**Frontend (.env.local)**
- `NEXT_PUBLIC_API_URL` (örn: http://localhost:8000)
- `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`

## Geliştirme Adımları

- **B1** ✅ Proje iskeleti ve models.py
- **B2** Discovery (Google, ajans, CSV) implement
- **B3** Enrichment (Apollo + kuyruk worker)
- **B4** CRM UI (lead listesi, durum, timeline)
- **B5** Deploy (Vercel + Railway)
