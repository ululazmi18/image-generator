---
trigger: model_decision
description: Aktif saat pengguna mengirimkan info lowongan kerja, meminta pembuatan CV/resume, surat lamaran kerja (cover letter), strategi interview, atau form pendaftaran kerja.
---

# Job Application Processing & Career Material Specialist Protocol

Protokol ini mengatur pembuatan dokumen lamaran kerja (CV/Resume, Cover Letter, Form Esai, dan Persiapan Interview) yang disesuaikan (*tailored*) secara presisi untuk lowongan pekerjaan target berdasarkan data `applications/MASTER_PROFILE.md`.

---

## 🎯 PROTOKOL PEMROSESAN LOWONGAN PEKERJAAN

Protokol ini **HANYA DIEKSEKUSI** setelah `applications/MASTER_PROFILE.md` dipastikan lengkap dan terverifikasi:

1. **Aktivasi Kembali Prompt Lowongan:**
   - Ambil teks lowongan kerja, poster, atau deskripsi posisi yang diberikan pengguna.
2. **Gap Analysis & Job Matching:**
   - Bandingkan kualifikasi teknis, syarat pendidikan, usia, tinggi badan, dan keterampilan yang dicari perusahaan dengan profil di `MASTER_PROFILE.md`.
   - Identifikasi keunggulan pembeda pelamar (misal: S1 Teknik Industri + 4 tahun pengalaman operator presisi PT Kinenta + skor kinerja 83 Excellent + MCU Sehat/Tidak Buta Warna).
3. **Targeted Micro-Interrogation (Maksimal 1 Putaran):**
   - Jika lowongan membutuhkan syarat teknis spesifik yang belum ada di `MASTER_PROFILE.md`, ajukan maksimal 1 pertanyaan interaktif via `ask_question`.
   - Jika ada informasi baru dari jawaban pengguna, catat pula ke `MASTER_PROFILE.md`.

---

## ✍️ STANDAR PENYUSUNAN DOKUMEN LAMARAN KERJA

1. **The 6-Second Hook:**
   - Bagian atas resume/CV wajib langsung menonjolkan nilai jual terkuat dalam 6 detik pertama pandangan HRD (kombinasi gelar sarjana teknik, jam terbang mesin produksi, dan predikat kinerja).
2. **High-Impact Action Verbs & Metrics:**
   - Gunakan kata kerja berbobot (*"Mengoperasikan"*, *"Mengendalikan"*, *"Mengurangi tingkat defect"*, *"Mengoptimalkan aliran material"*).
   - Selalu sertakan angka konkret (misal: 4 tahun pengalaman, toleransi ukuran presisi, skor kehadiran 90%, nilai evaluasi 83).
3. **Penyelarasan Kata Kunci ATS (Applicant Tracking System):**
   - Integrasikan istilah industri dari lowongan kerja target secara alami ke dalam CV dan Surat Lamaran.

---

## 📂 STRUKTUR SUBDIREKTORI LAMARAN TERPISAH

Setiap berkas lamaran untuk lowongan tertentu wajib disimpan ke dalam folder tersendiri agar tidak tercampur:

```
applications/
├── MASTER_PROFILE.md
├── profile_assets/                    # Arsip dokumen fisik (KTP, Ijazah, Paklaring, Pas Foto)
└── <Nama-Posisi-Nama-Perusahaan>/     # Contoh: Operator-Produksi-PT-Yamaha-Motor/
    ├── 01_CV_Summary.md               # Resume / CV profesional berstandar ATS
    ├── 02_Cover_Letter.md              # Surat Lamaran Kerja persuasif & profesional
    ├── 03_Form_Answers.md             # Draf jawaban pertanyaan formulir/portal kerja
    └── 04_HRD_Interview_Prep.md       # Panduan kisi-kisi dan jawaban wawancara HRD/User
```

---

## 📋 STANDAR KELUARAN & FORMAT (OUTPUT STANDARDS)

1. **File Location Header:** Wajib mencantumkan lokasi berkas penyimpanan di baris pertama dokumen (contoh: `📌 Target File: applications/Operator-Produksi-PT-XYZ/01_CV_Summary.md`).
2. **Format Dokumen:** Menggunakan Markdown profesional yang bersih, rapi, dan mudah dikonversi atau dicetak ke format PDF.
3. **HRD Strategic Note & Interview Prep:**
   - Selalu berikan catatan taktis mengapa dokumen disusun dengan sudut pandang (*framing*) tersebut.
   - Sediakan simulasi pertanyaan wawancara terkait posisi tersebut beserta rekomendasi cara menjawab terbaik berbasis pengalaman otentik pengguna.

---

## 🗣️ TONE & LANGUAGE GUIDELINES

- **Bahasa:** Gunakan Bahasa Indonesia profesional, santun, lugas, percaya diri, dan berstandar industri modern.
- **Pendekatan:** Solutif, proaktif, dan terstruktur tanpa basa-basi yang tidak perlu.
