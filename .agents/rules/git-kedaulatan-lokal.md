---
trigger: model_decision
description: Aktif saat mengeksekusi operasi git terminal, menjalankan git commit lokal, atau mengelola integrasi repository tanpa izin push ke remote upstream.
---

# KEDAULATAN LOKAL GIT (LOCAL COMMITS ONLY)

Pedoman ini mengatur batasan operasi version control yang strictly local untuk melindungi repositori dan integritas kerja pengguna.

---

## 1. Commit Hanya Secara Lokal
- Seluruh *commit* git wajib dieksekusi secara lokal pada mesin pengguna per unit pekerjaan yang tuntas.

---

## 2. Larangan Keras Git Push & Remote Baru
- **DILARANG KERAS** menjalankan perintah `git push` ke repositori jarak jauh (*remote upstream*) tanpa izin tertulis eksplisit dari pengguna.
- **DILARANG KERAS** menambahkan atau mengubah konfigurasi `git remote` tanpa instruksi langsung dari pengguna.
- Seluruh keputusan sinkronisasi ke server jarak jauh adalah hak prerogatif pengguna sepenuhnya.
