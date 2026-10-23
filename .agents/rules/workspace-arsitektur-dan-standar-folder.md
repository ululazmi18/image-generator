---
trigger: model_decision
description: Aktif saat mengorganisir, membuat folder baru, menata berkas, memindahkan file, atau mengelola struktur direktori di root workspace proyek aktif.
---

# STANDARISASI ARSITEKTUR & TATA KELOLA DIREKTORI WORKSPACE PROYEK

Pedoman ini mengatur tata kelola penataan berkas, struktur direktori, pemisahan domain fungsional, dan kebersihan direktori pada root workspace proyek aktif.

---

## 1. Prinsip Utama Arsitektur

1. **Pemisahan Tanggung Jawab Domain (*Domain Separation of Concerns*):**
   - Setiap folder di root workspace mewakili satu domain fungsi atau modul yang terisolasi.
   - Dilarang mencampuradukkan domain (misalnya menaruh berkas dokumen acak di folder modul logika, atau meletakkan file output media di luar direktori output resminya).
2. **Bebas Sampah di Root (*Zero Clutter on Root Rule*):**
   - Root workspace (direktori utama proyek) **HANYA** boleh memuat direktori domain resmi dan berkas tata kelola global (`.gitignore`, `README.md`, serta konfigurasi proyek seperti `package.json`, `pyproject.toml`, dsb.).
   - Dilarang keras membuat skrip pengujian sementara, meletakkan gambar lepasan, berkas catatan acak, atau folder sementara langsung di root workspace.
3. **Kemandirian Domain (*Self-Contained Domain*):**
   - Setiap folder modul atau domain proyek wajib bersifat mandiri: memiliki berkas `README.md` penjelas, mengelola asetnya sendiri, dan menyimpan seluruh berkas luaran (*outputs*) di dalam subdirektori terkait.

---

## 2. Pola Penataan Direktori Standar

### A. Direktori Tata Kelola Sistem (`.agents/`)
- Menyimpan seluruh instrumen memori cerdas SQLite FTS5 dan blueprint proyek di `.agents/memory/` (`memory.db`, `PRD.md`, `DESIGN.md`, `task.md`) demi menjaga root workspace 100% bersih dari berkas pendukung AI.
- **Larangan Keras File Dump Flat Memori & Artifak di Workspace:**
  - Dilarang keras membuat berkas dump teks usang seperti `CODE_SYMBOLS.md`, `PROJECT_STRUCTURE.md`, `digest.txt`, `repomix-output.xml`, `repomix.config.json`, atau `.gitingestignore`. Seluruh navigasi simbol dan topologi telah sepenuhnya digantikan oleh mesin `agent-memory` (`memory.db`).
  - Dilarang keras membuat berkas laporan operasional agen seperti `walkthrough.md`, `audit.md`, atau `implementation_plan.md` langsung di root/subdirektori workspace. Seluruh dokumen artifak/laporan wajib disimpan di direktori artifak IDE (`<appDataDir>\brain\<conversation-id>`) atau disampaikan di respon chat.
- Setiap aturan menggunakan nama `kebab-case` yang deskriptif dan frontmatter YAML yang terfokus.

### B. Direktori Domain Fungsional (Contoh Pola Umum)
- **`src/` atau `app/`:** Kode sumber inti aplikasi/sistem.
- **`applications/`:** Domain data profil, legalitas, dan berkas pelamaran kerja (jika workspace mengelola karir).
- **`studio/`:** Domain eksperimen media dan laboratorium multimedia generatif (jika workspace memuat modul media).
- **`docs/`:** Dokumentasi arsitektur, panduan teknis, dan spesifikasi sistem.
- **`scripts/` atau `tools/`:** Skrip otomasi atau utilitas operasional yang terisolasi.

---

## 3. Protokol Penambahan Folder Baru di Root

Jika pengguna meminta membuat domain, modul, atau fungsionalitas baru di root workspace:
1. **Penamaan Folder:**
   - Gunakan format huruf kecil ringkas (*kebab-case* atau kata tunggal deskriptif, contoh: `projects`, `docs`, `tools`, `research`).
   - Dilarang menggunakan spasi, huruf kapital, atau karakter non-ASCII.
2. **Kelengkapan Standar:**
   - Sediakan `README.md` lokal yang menjelaskan fungsi dan struktur folder tersebut.
   - Sediakan file `.gitignore` lokal jika folder menghasilkan artefak build, cache, atau data sensitif `.env`.
   - Siapkan subfolder terorganisir (misal: `src/` untuk kode, `outputs/` untuk hasil).
3. **Pembaruan Peta Workspace:**
   - Perbarui `README.md` pada root workspace proyek untuk mencatat modul baru tersebut pada bagan topologi direktori.

---

## 4. Standarisasi Bahasa & Kode
- **Identifikator Teknis:** Nama folder, berkas skrip, fungsi, dan variabel **wajib Bahasa Inggris** (contoh: `outputs`, `videos`, `main.py`).
- **Dokumentasi & Komentar:** Panduan `README.md`, catatan implementasi, dan komentar kode **wajib Bahasa Indonesia** yang profesional dan lugas.

---

## 5. Kebersihan Direktori (Hygiene)
- Seluruh berkas temporer, log debugging, dan cache pengujian wajib dibersihkan atau diabaikan oleh `.gitignore`.
- Jangan memindahkan atau menghapus berkas yang sudah ada tanpa memastikan seluruh data berharga telah dicadangkan.
