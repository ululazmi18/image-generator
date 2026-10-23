---
trigger: model_decision
description: Aktif saat menerima, mengunggah, mengekstrak, mengorganisir, atau menamai berkas fisik pelamar di applications/profile_assets/ (KTP, KK, Ijazah, Paklaring, SKCK, MCU).
---

# Physical Profile Assets Management & Ingestion Protocol

Protokol ini mengatur alur penerimaan, ekstraksi data otomatis, penataan subfolder arsip fisik, dan konvensi penamaan baku berkas dokumen pendukung karir pelamar kerja.

---

## ⚡ PROTOKOL FAST-TRACK INGESTION (PENERIMAAN BERKAS OTOMATIS)

Untuk mempersingkat waktu dan memudahkan pengguna dalam melengkapi profil karir:

1. **Permintaan Berkas Proaktif:**
   - Sebelum interogasi manual dari nol, AI Agent dapat secara proaktif menawarkan pengguna untuk mengirimkan berkas fisik yang dimiliki (berupa zip, pdf, jpg, png, docx).
   - Dokumen meliputi: KTP, Kartu Keluarga, Akta Kelahiran, Kartu AK-1, Ijazah, Transkrip Nilai, Surat Pengalaman Kerja, Surat Keterangan Kinerja, Sertifikat Pelatihan/K3, SKCK, dan Hasil MCU.
2. **Ekstraksi Data Otomatis ke `MASTER_PROFILE.md`:**
   - AI Agent membaca isi berkas, melakukan parsing komprehensif (kredensial, tanggal, nomor registrasi, nilai, IPK, catatan medis, metrik kinerja), dan langsung menyalinnya ke `applications/MASTER_PROFILE.md`.
3. **Pemberkasan & Penataan ke 5 Subfolder Resmi:**
   - Seluruh berkas fisik wajib disimpan terorganisir ke dalam:
     ```
     applications/profile_assets/
     ├── 01_Identitas/              # KTP, KK, Akta Kelahiran, SIM, AK-1, Pas Foto
     ├── 02_Pendidikan/             # Ijazah D3/S1, Transkrip Akademik, Ijazah & SKHUN SMA/SMK
     ├── 03_Pengalaman_Kerja/       # Surat Pengalaman Kerja, Surat Keterangan Kinerja, CV Lama
     ├── 04_Sertifikasi_Pelatihan/  # Sertifikat K3, Pelatihan BLK, Lisensi Teknis, MOS Excel
     └── 05_Legalitas_Kesehatan/    # SKCK, Surat Keterangan MCU, Hasil Rontgen, Hasil Lab
     ```

---

## 🏷️ ATURAN BAKU PENAMAAN BERKAS (CONTENT-ACCURATE NAMING)

Nama berkas dokumen fisik **WAJIB SECARA PRESISI** mencerminkan **judul resmi dokumen fisik dan isinya**:

1. **Prinsip Utama:**
   - **Dilarang Singkatan Ambigu:** Jangan gunakan singkatan tanpa kepanjangan resmi (misal: gunakan `Kartu_Keluarga`, bukan sekadar `KK`).
   - **Dilarang Istilah Non-Resmi:** Jangan gunakan istilah serapan informal seperti `Paklaring` jika judul fisik dokumennya adalah `Surat_Pengalaman_Kerja`, atau `Sertifikat` jika dokumennya berupa `Surat_Keterangan_Penilaian_Kinerja`.
2. **Formula Standar Penamaan:**
   `[Judul_Dokumen_Resmi]_[Instansi_Atau_Keterangan_Spesifik]_[Nama_Lengkap].ext`

3. **Daftar Contoh Penamaan Baku Berkas Arsip (Template Universal):**
   - **01 Identitas:**
     * `01_Identitas/Kartu_Keluarga_[Nama_Lengkap].jpg`
     * `01_Identitas/Kartu_Pencari_Kerja_AK1_[Disnaker]_[Nama_Lengkap].jpg`
     * `01_Identitas/Kutipan_Akta_Kelahiran_[Nama_Lengkap].jpg`
   - **02 Pendidikan:**
     * `02_Pendidikan/Ijazah_[Jenjang]_[Jurusan]_[Instansi]_[Nama_Lengkap].jpg`
     * `02_Pendidikan/Transkrip_Akademik_[Jenjang]_[Jurusan]_[Instansi]_[Nama_Lengkap].jpg`
   - **03 Pengalaman Kerja:**
     * `03_Pengalaman_Kerja/Surat_Pengalaman_Kerja_[Nama_Perusahaan]_[Nama_Lengkap].jpg`
     * `03_Pengalaman_Kerja/Surat_Keterangan_Penilaian_Kinerja_[Nama_Perusahaan]_[Nama_Lengkap].jpg`
   - **05 Legalitas & Kesehatan:**
     * `05_Legalitas_Kesehatan/Surat_Keterangan_Catatan_Kepolisian_SKCK_[Polsek/Polres]_[Nama_Lengkap].jpg`
     * `05_Legalitas_Kesehatan/Surat_Keterangan_Medical_Check_Up_MCU_[Nama_RS]_[Nama_Lengkap].jpg`
     * `05_Legalitas_Kesehatan/Hasil_Pemeriksaan_Rontgen_Thorax_[Nama_RS]_[Nama_Lengkap].jpg`
     * `05_Legalitas_Kesehatan/Hasil_Pemeriksaan_Laboratorium_Hematologi_[Nama_RS]_[Nama_Lengkap].jpg`
     * `05_Legalitas_Kesehatan/Hasil_Pemeriksaan_Laboratorium_Urinalisa_[Nama_RS]_[Nama_Lengkap].jpg`

---

## 📦 ONE-CLICK BUNDLING SAAT MELAMAR PEKERJAAN

Ketika pengguna melamar ke lowongan kerja tertentu yang mensyaratkan lampiran dokumen (misal: "Kirimkan CV, Ijazah, Transkrip, Surat Pengalaman Kerja, dan SKCK"):
1. AI Agent langsung mengidentifikasi dan mengambil berkas terkait dari subfolder `profile_assets/`.
2. AI Agent membuat daftar cek dokumen lampiran dan menautkan berkas-berkas tersebut ke berkas aplikasi target di `applications/<nama-posisi-atau-perusahaan>/`.
