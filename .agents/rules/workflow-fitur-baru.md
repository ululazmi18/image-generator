---
trigger: model_decision
description: Aktif saat pengguna meminta penambahan fitur baru, pembuatan modul perangkat lunak baru, atau pengembangan kapabilitas aplikasi dari tahap analisis hingga commit.
---

# ALUR PENGEMBANGAN FITUR BARU (NEW FEATURE PROTOCOL - TDD HARMONIZED)

Pedoman ini mengatur 5 tahap eksekusi otomatis pengembangan modul atau fitur baru secara terstruktur, disiplin, dan terharmonisasi penuh dengan standar TDD Everything Claude Code (ECC).

---

## 5 Tahap Pelaksanaan Fitur Baru (TDD Cycle)

1. **Tahap 1 (Analisis Kebutuhan & Perancangan Spesifikasi):**
   - Tinjau batasan arsitektur sistem dan identifikasi modul-modul yang terdampak.
   - Tetapkan kontrak data, definisi tipe (*type definitions*), atau *interface*.
   - Terapkan prinsip YAGNI (*You Aren't Gonna Need It*) dan KISS (*Keep It Simple, Stupid*); tolak spekulasi fitur yang tidak diminta.

2. **Tahap 2 (Test-First / TDD Red Phase):**
   - **Wajib Test-First:** Tulis unit test atau skenario pengujian terlebih dahulu sebelum menulis logika implementasi.
   - Pastikan test mendefinisikan ekspektasi fungsional dan *edge cases* dengan jelas.
   - Verifikasi bahwa test gagal (*Red*) sebelum kode implementasi dibuat.

3. **Tahap 3 (Implementasi Minimal / Green Phase):**
   - Tulis kode implementasi minimal dan terfokus hanya untuk membuat seluruh pengujian lulus (*Green*).
   - Terapkan penanganan galat defensif (*error handling*) dan sanitasi input di setiap batas I/O atau API.
   - Larang over-engineering atau penambahan abstraksi prematur.

4. **Tahap 4 (Review Kualitas, Keamanan, & Refactor):**
   - Jalankan seluruh rangkaian test untuk memastikan *zero regression*.
   - Lakukan audit keamanan (tanpa hardcoded credentials, validasi batas input, pencegahan injection).
   - Rapikan struktur kode (*clean code*) dengan tetap menjaga status test 100% lulus.

5. **Tahap 5 (Finalisasi & Atomic Commit):**
   - Bersihkan seluruh berkas sementara (*scratch hygiene*).
   - Pastikan kode lolos linter/pemeriksaan tipe (*zero error*).
   - Buat git commit lokal konvensional: `feat: <deskripsi_fitur>`.
