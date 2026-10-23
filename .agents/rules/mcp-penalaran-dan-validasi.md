---
trigger: model_decision
description: Aktif saat menganalisis masalah kompleks dengan sequential-thinking, merancang arsitektur bertahap, atau memvalidasi dokumentasi library pihak ketiga via context7.
---

# SERVER MCP: PENALARAN BERTAHAP & VALIDASI DOKUMENTASI

Pedoman ini mengatur pemanfaatan server MCP `sequential-thinking` untuk pemecahan masalah kompleks dan `context7` untuk validasi dokumentasi terkini.

---

## 1. Penalaran Bertahap (`sequential-thinking`)
- **Wajib dipanggil secara aktif dan mandiri** pada:
  - Tugas dengan tingkat kompleksitas arsitektur tinggi.
  - Penelusuran akar masalah (*root cause analysis*) pada error rumit.
  - Perencanaan perubahan berskala besar dengan multi-tahap eksekusi.
- Tujuannya adalah menstrukturkan alur pemikiran, hipotesis, dan validasi sebelum kode diubah.

---

## 2. Validasi Pustaka & Dokumentasi Terkini (`context7`)
- **Wajib dipanggil secara proaktif** sebelum menulis kode yang mengintegrasikan framework, pustaka, atau SDK pihak ketiga.
- Pastikan nama fungsi, sintaks, tipe parameter, dan berkas konfigurasi akurat sesuai dokumentasi versi terbaru.
- Dilarang keras mengandalkan asumsi atau memori usang yang rentan memicu *breaking changes*.
