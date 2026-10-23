---
trigger: model_decision
description: Aktif saat menjalankan perintah shell/terminal via run_command, verifikasi runtime lingkungan, instalasi dependensi, build proyek, atau inspeksi database SQLite lokal.
---

# FITUR BAWAAN: TERMINAL SHELL & SISTEM OPERASI

Pedoman ini mengatur pemanfaatan proaktif terminal shell (`run_command`) dan eksekusi runtime lokal bawaan IDE.

---

## 1. Pemanfaatan Proaktif Terminal (`run_command`)
- Gunakan terminal shell secara mandiri dan proaktif untuk:
  - Memverifikasi status lingkungan runtime dan keberadaan alat bantu (*toolchains*).
  - Menjalankan linter, formatter, dan *type checker*.
  - Membangun (*build*) proyek dan menguji eksekusi skrip secara nyata.
  - Memasang dependensi atau paket pustaka yang dibutuhkan.
- Jangan menunggu instruksi manual jika verifikasi terminal diperlukan untuk memastikan kebenaran pekerjaan.

---

## 2. Pengelolaan Database Lokal & SQLite
- Manfaatkan modul Python `sqlite3` atau driver proyek yang relevan via terminal untuk memeriksa skema, menguji kueri, dan memanipulasi database SQLite lokal secara dinamis sesuai lokasi proyek yang aktif.
