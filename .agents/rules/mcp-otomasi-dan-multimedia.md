---
trigger: model_decision
description: Aktif saat pengujian antarmuka browser, ekstraksi web mendalam via firecrawl, atau generasi multimedia AI (suara, video, gambar).
---

# PROTOKOL OTOMASI BROWSER & MULTIMEDIA GENERATIF AI

Pedoman ini mengatur pemanfaatan alat untuk pengujian peramban dan generasi aset multimedia secara hemat token.

---

## 1. Otomasi Browser & Pengujian Frontend
- **Wajib Utamakan Natif `browser_subagent`:**
  - Isolasi interaksi browser (klik, ketik, navigasi, verifikasi visual) di sub-agen terpisah untuk mencegah pembengkakan snapshot DOM di chat utama.
  - Jangan menjalankan Playwright langsung di jendela obrolan utama.

---

## 2. Ekstraksi Web & Deep Crawling
- **Natif `read_url_content`:** Gunakan untuk 95% kebutuhan membaca artikel/halaman tunggal.
- **Skill `firecrawl-crawler`:** Panggil on-demand untuk situs yang terproteksi Cloudflare/JS-heavy atau saat butuh merayapi (*crawl*) puluhan sub-halaman satu domain.

---

## 3. Multimedia Generatif AI (On-Demand & Zero-Cost)
- **Generasi Gambar & Suara Gratis:** Gunakan skill on-demand `pollinations-media` atau natif `generate_image`.
- **Narasi Suara Manusiawi:** Gunakan skill on-demand `elevenlabs-audio`.
- **Generasi Video Sinematik:** Gunakan skill on-demand `ai-video-gen` dengan mematuhi kebijakan zero-cost (dilarang memotong kredit berbayar tanpa izin tertulis).
