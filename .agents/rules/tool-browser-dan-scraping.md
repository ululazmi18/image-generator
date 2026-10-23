---
trigger: model_decision
description: Aktif saat membutuhkan riset web terkini, navigasi live scraping interaktif via browser_subagent, pencarian dokumentasi web mutakhir, atau ekstraksi halaman web.
---

# FITUR BAWAAN: OTOMASI BROWSER & RISET WEB

Pedoman ini mengatur pemanfaatan browser bawaan (`browser_subagent`), penelusuran web (`search_web`), dan pengunduh konten (`read_url_content`).

---

## 1. Otomasi Browser & Live Dynamic Scraping (`browser_subagent`)
Manfaatkan browser interaktif secara proaktif untuk:
- Menjelajahi situs dinamis modern (SPA, JavaScript-rendered) yang memerlukan interaksi nyata (klik tombol, navigasi, pengisian formulir).
- Pengujian tampilan antarmuka nyata (*frontend testing*), inspeksi DOM langsung, dan verifikasi alur aplikasi web.

---

## 2. Riset Web & Scraping Konten Terkini
- **Prinsip Relevansi Mutlak:** Utamakan pencarian web (`search_web`) dan pembaca konten (`read_url_content`) pada kebutuhan data dinamis:
  - Dokumentasi API resmi, framework, atau SDK yang rentan terhadap *breaking changes* atau pembaruan versi terbaru.
  - Penelusuran akar masalah (*root cause analysis*) pada error yang melibatkan ekosistem eksternal.
  - Fakta eksternal atau tren industri yang dinamis.
- **Efisiensi Tugas Lokal:** Dilarang melakukan pencarian web yang tidak perlu (*redundant search*) untuk logika utilitas mandiri, algoritma dasar, atau kode yang konteksnya sudah jelas di proyek lokal.
