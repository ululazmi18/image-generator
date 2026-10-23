---
trigger: model_decision
description: Aktif saat pengguna meminta membuat, merombak, atau mengedit foto menjadi pas foto formal melamar kerja (standar latar merah/biru, setelan jas/kemeja, rasio 3:4).
---

# Golden Standard Passport Photo Protocol (Paket 6 Pas Foto Karir)

Protokol ini berlaku mutlak pada sesi aktif maupun seluruh sesi percakapan mandiri di masa mendatang setiap kali pengguna meminta membuat, merombak, atau mengedit foto biasa (full body atau setengah badan) menjadi pas foto resmi untuk melamar pekerjaan.

---

## 🎯 STANDAR MUTU MINIMUM (BASELINE BENCHMARK)

1. **Benchmark Mutu Mutlak:**
   - Kualitas pas foto yang dihasilkan **WAJIB BERSTANDAR STUDIO PROFESIONAL** setara benchmark arsip resmi identitas pelamar:
     `applications/profile_assets/01_Identitas/Pas_Foto_Formal_Jas_Latar_Merah_[Nama_Lengkap].jpg`
2. **Preservasi Identitas Otentik (Zero Facial Distortion):**
   - Fitur wajah asli pengguna (mata, bentuk kacamata, hidung, bibir, tahi lalat/tanda lahir, bentuk telinga, gaya rambut, dan warna kulit) **100% WAJIB IDENTIK OTENTIK** tanpa distorsi wajah atau perubahan proporsi wajah.
3. **Pencahayaan & Komposisi Studio:**
   - Pencahayaan studio profesional merata, kontras natural, tanpa bayangan mengganggu (*drop shadow*), dan beresolusi tinggi.
   - Framing bust-up / chest-up proporsional dengan rasio standar pas foto **3:4** (posisi kepala mengisi 70–80% tinggi frame).

---

## 👔 PAKET LENGKAP 6 BERKAS PAS FOTO (3 GAYA BUSANA x 2 WARNA LATAR)

Setiap kali pengguna meminta perombakan foto, AI Agent secara otomatis menghasilkan **paket lengkap 6 berkas pas foto**:

### A. 3 Gaya Busana Kerja Profesional:
1. **Gaya 1 (Full Formal Eksekutif):**
   - Setelan jas/blazer hitam formal berkualitas premium, kemeja putih berkerah rapi, dan dasi hitam elegan.
2. **Gaya 2 (Formal Smart-Casual / Corporate):**
   - Kemeja formal putih atau biru muda berkerah rapi berdasi (tanpa jas luar) untuk tampilan korporat modern yang bersih.
3. **Gaya 3 (Formal Modern / Work-Shirt):**
   - Kemeja formal berkerah kancing tegak, kemeja batik sutra formal, atau kemeja operasional kerja rapi.

### B. 2 Warna Latar Belakang Standar Resmi Indonesia:
1. **Latar Belakang MERAH (Solid Red Hex `#D80000`):**
   - Standar resmi Ditjen Dukcapil dan instansi pemerintah Indonesia untuk pelamar yang lahir pada **tahun ganjil**, seleksi BKN/CPNS, dan BUMN.
2. **Latar Belakang BIRU (Solid Royal Blue Hex `#0055A5`):**
   - Standar umum perusahaan swasta, industri manufaktur, perbankan, dan standar resmi untuk pelamar yang lahir pada **tahun genap**.

---

## 📁 PEMBERKESAN & PENAMAAN BAKU ARSIP

Seluruh 6 berkas pas foto wajib otomatis disimpan ke direktori:
`applications/profile_assets/01_Identitas/`

Format penamaan baku:
1. `Pas_Foto_Formal_Jas_Latar_Merah_[Nama_Lengkap].jpg`
2. `Pas_Foto_Formal_Jas_Latar_Biru_[Nama_Lengkap].jpg`
3. `Pas_Foto_Formal_Kemeja_Latar_Merah_[Nama_Lengkap].jpg`
4. `Pas_Foto_Formal_Kemeja_Latar_Biru_[Nama_Lengkap].jpg`
5. `Pas_Foto_Formal_Modern_Latar_Merah_[Nama_Lengkap].jpg`
6. `Pas_Foto_Formal_Modern_Latar_Biru_[Nama_Lengkap].jpg`

---

## 🔄 SINKRONISASI MEMORI OTOMATIS

Setelah seluruh variasi pas foto selesai dibuat:
1. Perbarui checklist ketersediaan berkas di `applications/MASTER_PROFILE.md`.
2. Perbarui daftar inventaris terarsip di `applications/profile_assets/README.md`.
