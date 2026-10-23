---
trigger: model_decision
description: Aktif saat menulis atau meninjau kode program, menerapkan prinsip Clean Code, Separation of Concerns (SoC), penamaan teknis Bahasa Inggris, atau pengetikan type-safety.
---

# STANDAR KUALITAS KODE (CLEAN CODE & TYPE-SAFETY)

Pedoman ini mengatur kerapian, kebersihan, struktur modular, dan kejelasan tipe data dalam penulisan kode program.

---

## 1. Clean Code & Separation of Concerns (SoC)
- Tulis kode yang bersih, mudah dibaca, serta terstruktur dalam modul-modul logis yang terisolasi.
- Terapkan prinsip *Separation of Concerns* (SoC): setiap berkas, modul, kelas, atau fungsi hanya bertanggung jawab atas satu domain tugas spesifik.
- Hindari fungsi monolithic (fungsi yang terlalu panjang dan mengerjakan banyak hal sekaligus). Pecah menjadi fungsi utilitas pembantu yang lebih kecil dan fokus.

---

## 2. Kejelasan Tipe Data (Type-Safety)
- Terapkan sistem tipe data yang ketat (*fully type-safe*) pada bahasa yang mendukung (seperti TypeScript, Python type hints via `typing`, Dart, Go, dsb.).
- Hindari penggunaan tipe longgar (seperti `any` di TypeScript atau `dynamic` tanpa alasan) guna mencegah kesalahan runtime tipe data (*type confusion*).

---

## 3. Konvensi Penamaan & Bahasa
- **Identifikator Teknis:** Nama variabel, fungsi, metode, kelas, konstanta, berkas, tabel, dan kolom basis data **wajib menggunakan Bahasa Inggris** untuk menjaga standar industri dan interoperabilitas.
- **Komentar & Penjelasan:** Komentar kode (*docstrings* & *inline comments*) **wajib menggunakan Bahasa Indonesia** yang jelas, edukatif, dan lugas.
