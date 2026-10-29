---
trigger: model_decision
description: Aktif saat merancang arsitektur perangkat lunak, perancangan modul/CLI hybrid, konfigurasi packaging standar (PEP 621/npm), atau menyusun rencana refactoring terisolasi.
---

# ARSITEKTUR SISTEM & PERENCANAAN MODULAR

Pedoman ini mengatur perancangan sistem modular yang dapat diuji (*testable*), pola desain modul/CLI hybrid, standarisasi kemasan (*packaging*), dan tata kelola rencana refactoring terisolasi.

---

## 1. Arsitektur Modular & Loose Coupling
- Rancang struktur kode yang terisolasi secara modular sehingga setiap komponen dapat diuji (*unit-testable*) secara independen tanpa ketergantungan erat (*loose coupling*).
- Hindari ketergantungan kaku (*hardcoded dependency*); gunakan teknik injeksi dependensi (*dependency injection*) atau modularisasi parameter agar implementasi mudah di-mock dan diganti.
- Pisahkan secara tegas antara lapisan antarmuka pengguna (CLI/TUI/Web), lapisan logika inti (*domain core/services*), dan lapisan akses driver/infrastruktur.

---

## 2. Pola Desain Dual-Role (Modul Pustaka & CLI Hybrid)
- Setiap kali membangun pustaka atau alat otomasi, rancang arsitektur dengan kapabilitas ganda:
  1. **Layanan Modul Terprogram (*Importable Library*):** Sediakan antarmuka programatik yang bersih, mudah diimpor, dan mengekspos fungsi tingkat tinggi (`from module import ServiceClient`).
  2. **Antarmuka Baris Perintah (*Executable CLI*):** Sediakan titik masuk eksekusi langsung via terminal (CLI) berbasis antarmuka visual yang informatif.
- Pastikan logika inti berada di dalam modul independen sehingga antarmuka CLI hanya bertindak sebagai *thin wrapper* di atas modul tersebut.

---

## 3. Berkas Konfigurasi & Standarisasi Kemasan Proyek
- Setiap modul mandiri wajib menyediakan deklarasi konfigurasi standar modern (seperti `pyproject.toml` berstandar PEP 517/518/621 untuk Python, `package.json` untuk Node.js, atau `pubspec.yaml` untuk Dart).
- Daftarkan skrip titik masuk CLI secara resmi (misal: `[project.scripts]` pada `pyproject.toml`) agar modul dapat langsung dipasang dan dijalankan secara global/lokal via `pip install -e .` atau `npm link`.
- Sediakan konfigurasi standar pengujian dan pemformatan (*linter/formatter*) seperti `pyproject.toml`, `.eslintrc`, atau `analysis_options.yaml`.

---

## 4. Protokol Rencana Kerja & Refactoring Terisolasi
- Sebelum melakukan perombakan arsitektur besar, penambahan modul kompleks, atau refactoring berisiko tinggi, susun rencana implementasi terisolasi secara tertulis.
- **Lokasi Penyimpanan Rencana:** Rencana kerja **wajib disajikan di respon percakapan atau dibuat sebagai artifak internal IDE** di `<appDataDir>\brain\<conversation-id>/`. **DILARANG KERAS meletakkan berkas laporan seperti `implementation_plan.md` langsung di ruang kerja proyek.**
- Tunggu persetujuan tertulis pengguna sebelum melakukan modifikasi berkas arsitektur secara masif.
