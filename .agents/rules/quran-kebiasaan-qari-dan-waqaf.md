---
description: Aktif saat memproses audio reciter Quran, segmentasi subtitel per tarikan napas (waqaf), sinkronisasi ASS, atau menangani profil tempo qari (Ibrahim Akhdar, Ali Al-Hudhaify, Aziz Alili) agar akurat tanpa regresi timing.
trigger: model_decision
globs: "tools/**"
---

# PANDUAN KARAKTERISTIK, KEBIASAAN NAFAS & WAQAF QARI

Dokumen ini adalah standar rujukan profil tempo, kapasitas nafas, dan kebiasaan waqaf empiris dari 3 qari inti Quran Video Studio untuk memastikan segmentasi subtitel ayat panjang selalu selaras 100% dengan lantunan audio aktual tanpa regresi.

---

## 1. Karakteristik & Kebiasaan 3 Qari Inti

### A. Syaikh Ibrahim Al-Akhdar (`ibrahim_akhdar`)
- **Gaya Lantunan:** Murattal tartil khusyuk, tempo lambat-tenang, artikulasi *makhraj* sangat tegas, dan mad dibaca sempurna 4–5 harakat.
- **Profil Durasi (Contoh Ayat Kursi 2:255):** ~70.1 detik (paling panjang di antara ketiganya).
- **Karakteristik Hembusan Nafas & Waqaf:**
  - Sangat patuh pada setiap tanda waqaf resmi Mushaf Madinah (*Jaiz, Thaha, Qif, Shala*).
  - Pada klausa penutup ayat panjang, beliau **menggabungkan 2 klausa terakhir dalam 1 hembusan nafas** (misal: `وَلَا يَـُٔودُهُۥ حِفْظُهُمَا ۚ` langsung disambung ke `وَهُوَ ٱلْعَلِىُّ ٱلْعَظِيمُ` selama ~10.2 detik).
  - Total tarikan nafas pada Ayat Kursi: **8 segmen**.
  - Jeda hening antar-tarikan nafas rata-rata: `0.35s – 0.48s`.
  - Lead-in vokal awal audio: `~0.20s – 0.28s`, jeda senyap penutup (lead-out): `~0.85s`.

### B. Syaikh Ali Al-Hudhaify (`hudhaify`)
- **Gaya Lantunan:** Murattal klasik Masjid Nabawi, tempo sedang-stabil, ketukan tajwid sangat teratur (*metric rhythm*).
- **Profil Durasi (Contoh Ayat Kursi 2:255):** ~58.5 detik.
- **Karakteristik Hembusan Nafas & Waqaf:**
  - Kapasitas nafas menengah dengan jeda tegas dan rapi.
  - Pada Ayat Kursi, beliau menyambung Unit 6 dan Unit 7 (`وَسِعَ كُرْسِيُّهُ ٱلسَّمَـٰوَٰتِ وَٱلْأَرْضَ ۖ` + `وَلَا يَـُٔودُهُۥ حِفْظُهُمَا ۚ`) dalam satu nafas (detik 45.8s – 53.2s), lalu berhenti sejenak, baru menutup Unit 8 (`وَهُوَ ٱلْعَلِىُّ ٱلْعَظِيمُ`) secara terpisah di detik 53.8s – 58.1s.
  - Total tarikan nafas pada Ayat Kursi: **8 segmen**.
  - Jeda antar napas: `0.40s – 0.60s`.

### C. Qari Aziz Alili (`aziz_alili`)
- **Gaya Lantunan:** Murattal modern dinamis, gaya khas qari Eropa/Balkan, mengalir (*fluent flow*), dengan tarikan nafas yang sangat panjang.
- **Profil Durasi (Contoh Ayat Kursi 2:255):** ~53.5 detik (paling singkat dan cepat).
- **Karakteristik Hembusan Nafas & Waqaf:**
  - Nafas sangat panjang; beliau kerap menyambung dua klausa yang bertalian makna meskipun di antaranya terdapat tanda waqaf jaiz.
  - Pada Ayat Kursi:
    - Menggabungkan Unit 4 dan Unit 5 (`يَعْلَمُ مَا بَيْنَ أَيْدِيهِمْ وَمَا خَلْفَهُمْ ۖ` + `وَلَا يُحِيطُونَ بِشَىْءٍ مِّنْ عِلْمِهِۦٓ إِلَّا بِمَا شَآءَ ۚ`) dalam 1 hembusan nafas panjang ~13.9 detik (detik 25.7s – 39.6s).
    - Menggabungkan 2 klausa penutup Unit 7 dan Unit 8 (`وَلَا يَـُٔودُهُۥ حِفْظُهُمَا ۚ` + `وَهُوَ ٱلْعَلِىُّ ٱلْعَظِيمُ`) di detik 45.6s – 52.5s.
  - Total tarikan nafas pada Ayat Kursi: hanya **7 segmen** (paling sedikit).

---

## 2. Aturan Baku Segmentasi Subtitel (`tools/waqaf_helper.py`)

1. **Hukum Larangan Pemotongan Sembarangan:**
   - Dilarang memotong subtitel hanya berdasarkan jumlah kata/karakter tanpa mencocokkan jeda hening hembusan nafas (*speech pauses / RMS*) qari target.
2. **Penanda Nomor Ayat BiDi-Safe:**
   - Ornamen nomor ayat `format_ayah_marker(ayah_no)` (`\u200f\ufd3f{num}\ufd3e\u200f`) **HANYA BOLEH disematkan pada segmen paling akhir dari ayat**. Segmen awal dan pertengahan tidak boleh diberi nomor ayat.
3. **Penyambungan Tanda Baca (Punctuation Smoothing):**
   - Ketika dua unit teks digabung (`combine_with`):
     - Bersihkan tanda titik koma (`;`) dan titik (`.`) di akhir klausa pertama.
     - Ubah awalan huruf kapital pada kata sambung klausa kedua (seperti *"Dan "* menjadi *"dan "*).
4. **Prinsip Satu Baris Terpusat:**
   - Setiap segmen waqaf wajib dirancang agar muat dalam 1 baris di kanvas 1080p dengan alignment tengah (*Alignment 8*). Gunakan `ArabicLong` jika teks Arab > 60 karakter.
