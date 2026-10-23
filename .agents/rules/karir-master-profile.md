---
trigger: model_decision
description: Aktif saat memeriksa, membuat, memperbarui applications/MASTER_PROFILE.md, atau interogasi profil karir pengguna. Gatekeeping mutlak sebelum memproses lowongan kerja.
---

# Gatekeeping & Master Career Profile Management Protocol

Protokol ini bersifat mutlak (*mandatory*) dan wajib dieksekusi secara berurutan untuk menjamin seluruh data pelamar terverifikasi dan tersimpan secara persisten sebelum berkas lamaran disusun.

---

## 🛑 PROTOKOL 0: ABSOLUTE GATEKEEPING (AUDIT MASTER PROFILE)

Setiap kali pengguna memulai percakapan baru atau memberikan prompt (berupa teks loker, link lowongan, maupun permintaan melamar pekerjaan):

1. **Abaikan Sementara Prompt Pengguna:**
   - AI Agent **DILARANG LANGSUNG MEMPROSES** teks lowongan atau langsung membuat berkas lamaran target.
   - Teks lowongan atau permintaan pengguna disimpan sementara dalam antrean kerja.
2. **Audit Berkas Master Profile:**
   - AI Agent **WAJIB TERLEBIH DAHULU MEMERIKSA** keberadaan dan isi berkas fisik:
     `applications/MASTER_PROFILE.md`
3. **Evaluasi Status Kelengkapan:**
   - **Kondisi A (Belum Ada / Belum Lengkap):** Jika berkas belum ada, masih kosong, atau minim informasi, AI Agent **WAJIB LANGSUNG MENGHENTIKAN ALUR REGULER** dan beralih penuh ke **Protokol Interogasi / Ingesti Berkas** untuk membangun profil master selengkap mungkin.
   - **Kondisi B (Sudah Lengkap):** HANYA jika `MASTER_PROFILE.md` sudah memuat data komprehensif (identitas, pendidikan, riwayat kerja/organisasi, keahlian, dan kondisi medis/fisik), AI Agent **BARU DIIZINKAN** melanjutkan ke pemrosesan lowongan kerja.

---

## 📋 PROTOKOL 1: GRADUAL & ADAPTIVE INTERROGATION (VIA NATIVE INTERACTIVE OPTIONS)

Jika pengguna belum memiliki berkas fisik atau memilih memberikan informasi melalui tanya jawab:

1. **Dilarang Formulir Monolitik:**
   - Dilarang keras menanyakan daftar panjang pertanyaan sekaligus di chat biasa.
   - Wajib menggunakan modal interaktif bawaan (*Interactive Options* via tool `ask_question`) putaran demi putaran.
2. **Sajian Opsi Cerdas:**
   - Setiap putaran menyajikan pilihan ganda yang terstruktur, realistis, dan relevan sesuai konteks karir industri manufaktur/umum, dilengkapi opsi bawaan untuk mengetikkan jawaban manual (*write-in option*).
3. **Pemberhentian Cerdas (Adaptive Stopping):**
   - Jika pengguna memilih opsi lewati (*Skip* / *"Lewati dulu"* / *"Tidak ada"*), jangan memaksa. AI Agent langsung lanjut ke dimensi data berikutnya atau memfinalisasi profil dengan data terbaik yang tersedia.

### 6 Dimensi Penggalian Data Karir:
- **Putaran 1: Data Diri & Kontak Dasar:** Nama lengkap, gelar, tempat/tanggal lahir, domisili, WhatsApp, email profesional.
- **Putaran 2: Target Posisi & Headline Karir:** Industri yang disasar, target jabatan (Operator, Leader, QC/QA, PPIC, Gudang), level pengalaman, dan nilai jual diri (*Value Proposition*).
- **Putaran 3: Pendidikan Formal & Sertifikasi:** Instansi/universitas, jenjang (SMK/D3/S1), jurusan, IPK, tahun kelulusan, dan fokus skripsi/tugas akhir.
- **Putaran 4: Pengalaman Kerja & Rekam Jejak Operasional:** Perusahaan, posisi, periode kerja, tanggung jawab teknis, dan **metrik pencapaian kunci** (skor evaluasi kinerja, kehadiran, efisiensi waktu).
- **Putaran 5: Keahlian Teknis (Hard Skills) & Tools:** Pengoperasian mesin pabrik, pembacaan gambar kerja, alat ukur/QC, software (Excel Expert, AutoCAD), dan metodologi industri (5S, K3, ARC).
- **Putaran 6: Soft Skills, Kemampuan Bahasa & Kesiapan Kerja:** Etos kerja, ketahanan fisik, kerja tim, bahasa (Indonesia, daerah, Inggris), kesiapan kerja shift (1, 2, 3), dan lembur.

---

## 💾 PROTOKOL 2: PERSISTENT MEMORY & SINGLE SOURCE OF TRUTH

1. **Memori Persisten Berkas Fisik:**
   - AI Agent **DILARANG KERAS** hanya mengandalkan memori sesi percakapan (*chat context*).
   - Seluruh data profil wajib langsung ditulis dan disimpan secara persisten ke dalam:
     `applications/MASTER_PROFILE.md`
2. **Struktur Standar `MASTER_PROFILE.md`:**
   - `# MASTER CAREER PROFILE & DATABASE`
   - `## 1. Identitas Pribadi & Informasi Kontak`
   - `## 2. Kondisi Fisik & Hasil Medical Check-Up (MCU)`
   - `## 3. Professional Summary & Value Proposition`
   - `## 4. Riwayat Pendidikan Formal & Sertifikasi`
   - `## 5. Riwayat Pengalaman Kerja Profesional`
   - `## 6. Pemetaan Keahlian & Kualifikasi (Hard & Soft Skills)`
   - `## 7. Rekomendasi Target Posisi & Jenjang Karir`
   - `## 8. Inventaris & Checklist Berkas Administrasi Fisik (profile_assets/)`
   - `## 9. Log Pembaruan Data (Update Log)`
3. **Sinkronisasi Berkelanjutan:**
   - Setiap ada informasi baru atau perubahan data dari pengguna, perbarui berkas master ini terlebih dahulu sebelum melangkah ke proses lamaran.
