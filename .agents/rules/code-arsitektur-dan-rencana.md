---
trigger: model_decision
description: Aktif saat merancang arsitektur sistem perangkat lunak, menyusun dokumen rencana kerja implementation_plan.md, atau membuat file konfigurasi standar linter/formatter.
---

# ARSITEKTUR SISTEM & PERENCANAAN TERTULIS

Pedoman ini mengatur perancangan sistem modular yang dapat diuji (*testable*), kewajiban penyusunan rencana implementasi tertulis, dan standardisasi konfigurasi proyek.

---

## 1. Arsitektur Modular & Testable
- Rancang struktur kode yang terisolasi secara modular sehingga setiap bagian dapat diuji (*unit-testable*) secara independen tanpa ketergantungan erat (*loose coupling*).
- Hindari *hardcoded dependency*; gunakan teknik *dependency injection* atau modularisasi parameter jika memungkinkan.

---

## 2. Kewajiban Rencana Tertulis (implementation_plan.md)
- Sebelum melakukan perombakan besar, penambahan fitur kompleks, atau refactoring berisiko tinggi, agen **wajib** menyusun rencana implementasi tertulis (`implementation_plan.md` dalam Bahasa Indonesia lengkap).
- **Lokasi Penyimpanan Rencana:** Rencana implementasi ini **wajib dibuat sebagai artifak IDE** di `<appDataDir>\brain\<conversation-id>/` atau disajikan di respon chat. **Dilarang keras meletakkan berkas `implementation_plan.md` langsung di root workspace.**
- Tunggu persetujuan tertulis pengguna sebelum melakukan modifikasi berkas proyek secara masif.

---

## 3. Berkas Konfigurasi Standar Proyek
- Buat berkas konfigurasi standar (*linter*, *formatter*, *type-checker* seperti `.eslintrc`, `prettier.config`, `pyproject.toml`, `analysis_options.yaml`, `tsconfig.json`) jika belum tersedia.
- Catat setiap penyesuaian parameter konfigurasi demi konsistensi lintas sesi kerja dan rekan tim.
