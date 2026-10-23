---
trigger: model_decision
description: Aktif saat menangani API key, token rahasia, kredensial autentikasi, konfigurasi variabel lingkungan (.env, .env.example), atau pengelolaan file rahasia di .gitignore.
---

# KEAMANAN KREDENSIAL & PENGELOLAAN VARIABEL LINGKUNGAN (.ENV)

Pedoman ini mengatur perlindungan rahasia, pencegahan kebocoran kredensial, dan tata kelola variabel lingkungan pada setiap proyek.

---

## 1. Larangan Mutlak Hardcoding Rahasia
- **Dilarang keras** menanamkan (*hardcode*) API Key, token otentikasi, kata sandi, *private key*, sertifikat rahasia, atau data sensitif ke dalam kode sumber, berkas konfigurasi publik, ataupun riwayat commit git.

---

## 2. Pengelolaan Variabel Lingkungan (.env)
- Simpan seluruh nilai rahasia di dalam berkas variabel lingkungan (`.env`) atau manfaatkan layanan *secret manager*.
- Sediakan berkas percontohan `.env.example` yang hanya memuat nama kunci tanpa nilai rahasia untuk memudahkan penyiapan lingkungan kerja baru.
- Pastikan berkas `.env`, token lokal, dan berkas privat selalu terdaftar di dalam `.gitignore`.
