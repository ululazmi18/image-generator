---
trigger: model_decision
description: Aktif saat menjalankan pengujian unit/integrasi inkremental, pembersihan berkas sementara/scratch hygiene, eksekusi berorientasi target, atau validasi kualitas zero-error.
---

# PENGUJIAN, VALIDASI KUALITAS & KEBERSIHAN LINGKUNGAN (SCRATCH HYGIENE)

Pedoman ini mengatur pelaksanaan pengujian berkala secara inkremental, validasi linter tanpa galat, eksekusi berorientasi target (*goal-driven*), dan disiplin pembersihan berkas sementara (*hygiene*).

---

## 1. Pengujian Inkremental & Terisolasi
- Lakukan pengujian secara bertahap dan berkala (*incremental testing*) per unit kerja atau fungsi yang baru diubah.
- Simpan skrip eksperimen atau berkas luaran uji sementara di direktori khusus yang terisolasi (misalnya direktori `scratch/`).

---

## 2. Pembersihan Lingkungan (Scratch Hygiene)
- **Wajib menghapus** seluruh berkas uji coba temporer, skrip debugging sementara, atau berkas *dummy* setelah proses validasi selesai.
- Jangan biarkan artefak uji coba sementara mencemari pohon repositori proyek utama.

---

## 3. Validasi Kualitas Otomatis (Zero Error)
- Seluruh kode yang dimodifikasi **wajib lolos linter dan static analyzer** otomatis (*zero error*) sebelum tugas dinyatakan selesai sepenuhnya.

---

## 4. Eksekusi Berorientasi Target & Loop Verifikasi (Goal-Driven Execution)
- Transformasikan setiap tugas menjadi target yang dapat diverifikasi secara objektif (misal: buat tes reproduksi bug -> perbaiki kode -> pastikan tes lulus).
- Untuk tugas multi-tahap, jalankan siklus mandiri: `[Langkah] -> Verifikasi: [Cek]` secara iteratif hingga seluruh target terkonfirmasi.
- **Dilarang keras** menyatakan tugas selesai hanya dengan asumsi tanpa menjalankan pengujian dan pemeriksaan hasil secara langsung.
