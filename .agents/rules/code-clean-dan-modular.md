---
trigger: model_decision
description: Aktif saat menulis atau mereview kode program, menerapkan Clean Code, fungsi fokus non-monolitik, Separation of Concerns (SoC), type-safety ketat, dan konvensi penamaan teknis.
---

# STANDAR KUALITAS KODE (CLEAN CODE & TYPE-SAFETY)

Pedoman ini mengatur kerapian, kebersihan, struktur modular, kejelasan tipe data, dan konvensi penamaan dalam penulisan kode program.

---

## 1. Clean Code & Separation of Concerns (SoC)
- Tulis kode yang bersih, mudah dibaca, serta terstruktur dalam modul-modul logis yang terisolasi.
- Terapkan prinsip *Separation of Concerns* (SoC): setiap berkas, modul, kelas, atau fungsi hanya bertanggung jawab atas satu domain tugas spesifik (*Single Responsibility Principle*).
- Hindari fungsi monolitik (fungsi yang terlalu panjang dan mengerjakan banyak hal sekaligus). Pecah menjadi fungsi utilitas pembantu yang lebih kecil dan fokus.
- Gunakan teknik *early return* / *guard clauses* untuk menghindari percabangan bersarang yang dalam (*deep nesting*).

---

## 2. Kejelasan Tipe Data Ketat (*Strict Type-Safety*)
- Terapkan sistem tipe data yang ketat (*fully type-safe*) pada bahasa yang mendukung (seperti TypeScript, Python type hints via `typing`, Dart, Go, dsb.).
- Hindari penggunaan tipe longgar (seperti `any` di TypeScript atau `dynamic` tanpa alasan) guna mencegah kesalahan runtime tipe data (*type confusion*).
- Berikan type hints eksplisit pada seluruh parameter fungsi, nilai kembalian (*return types*), dan atribut kelas.

---

## 3. Konvensi Penamaan & Bahasa
- **Identifikator Teknis:** Nama variabel, fungsi, metode, kelas, konstanta, berkas, tabel, dan kolom basis data **wajib menggunakan Bahasa Inggris** untuk menjaga standar industri dan interoperabilitas.
- **Komentar & Penjelasan:** Komentar kode (*docstrings* & *inline comments*) **wajib menggunakan Bahasa Indonesia** yang jelas, edukatif, dan lugas.

---

## 4. Kepatuhan Portabilitas & Arsitektur
- Seluruh penanganan path berkas, aset biner, dan modul internal wajib mematuhi aturan portabilitas dinamis bebas hardcoded drive pada [code-portabilitas-dan-path-universal.md](file:///d:/Tools/.agents/rules/code-portabilitas-dan-path-universal.md).
- Perancangan modul kemasan dan titik masuk antarmuka wajib mematuhi pola modular pada [code-arsitektur-dan-rencana.md](file:///d:/Tools/.agents/rules/code-arsitektur-dan-rencana.md).
