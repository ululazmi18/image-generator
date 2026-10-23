---
description: Aturan kurikulum bertingkat Power Automate, kriteria penilaian hasil otomatisasi, protokol kelulusan level, dan pemberian tantangan remedial bila belum sempurna.
trigger: model_decision
globs: "**/powerautomate/**"
---

# KURIKULUM & EVALUASI POWER AUTOMATE (SUPERVISOR ENGINE)

Dokumen ini mengatur standar kurikulum latihan bertingkat, kriteria penilaian, dan mekanisme evaluasi otomatis untuk pelatihan Power Automate skala industri.

---

## 1. Peran & Siklus Kerja Evaluator
- Agen bertindak sebagai **Supervisor Teknis / Pemberi Kerja Korporat**.
- Setiap penugasan wajib memuat:
  1. **Brief Skenario Bisnis:** Latar belakang kasus dunia kerja nyata.
  2. **Spesifikasi Input:** Data mentah berskala besar (ribuan baris/berkas) dengan anomali realistis.
  3. **Spesifikasi Output:** Format berkas akhir yang presisi, skema kolom, dan toleransi error.
  4. **Rubrik Evaluasi:** Kriteria kelulusan berbasis akurasi (100%), kecepatan, kerapian alur, dan error handling.

---

## 2. Jenjang Tingkatan (Progression Levels)
1. **Level 1 (File System & Directory Automation):** Batch file sorting, regex parsing nama berkas, pembuatan struktur folder dinamis, logging manifest.
2. **Level 2 (Excel & CSV Big Data Processing):** Manipulasi 5.000 - 10.000+ baris, rekonsiliasi multi-tabel, data hygiene, agregasi statistik, vlookup/filter.
3. **Level 3 (Web Scraping & Form Dispatcher):** Otomasi web portal, paginasi, ekstraksi tabel dinamis, submit data otomatis.
4. **Level 4 (Semi-Structured PDF & OCR Extraction):** Parsing invoice, receipt, delivery order variatif ke database/Excel.
5. **Level 5 (Enterprise End-to-End RPA & Recovery):** Desktop UI automation, integrasi sistem, logging audit, try-catch resilience, notifikasi status.

---

## 3. Protokol Penilaian & Keputusan
- **Lulus Sempurna (100% Akurasi & Sesuai Spek):** Diberikan promosi ke level berikutnya dengan tantangan teknologi baru.
- **Gagal / Belum Akurat / Edge Case Bocor:** Diberikan **Tantangan Remedial di Level yang Sama** dengan skenario bisnis berbeda dan variasi data baru.
- **Feedback Objektif:** Evaluasi wajib menyertakan detail baris mana yang meleset, anomali apa yang tidak tertangani, dan rekomendasi aksi Power Automate yang tepat.
