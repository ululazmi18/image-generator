---
trigger: model_decision
description: Aktif saat menangani laporan bug, error runtime, crash aplikasi, analisis akar masalah (root cause analysis), serta penyusunan laporan perbaikan dalam format 3 poin wajib.
---

# INVESTIGASI AKAR MASALAH (RCA) & PERBAIKAN BUG

Pedoman ini mengatur tahapan penelusuran akar masalah (*root cause analysis*), perbaikan presisi (*surgical fix*), dan format laporan wajib 3 poin.

---

## 1. Tahapan Perbaikan Bug & Error

1. **Tahap 1 (Investigasi Akar Masalah / RCA):** Analisis berkas log dan jejak tumpukan (*stack trace*), telusuri alur eksekusi kode, dan temukan *root cause* utama. Jangan menerapkan perbaikan tambal sulam tanpa memahami sumber masalahnya.
2. **Tahap 2 (Isolasi & Reproduksi):** Buat skenario pengujian terisolasi untuk mereproduksi bug secara konsisten.
3. **Tahap 3 (Perbaikan Presisi):** Terapkan perbaikan kode presisi (*surgical fix*) tanpa merusak fungsionalitas pendukung lain (*prevent regression*).
4. **Tahap 4 (Validasi Ulang):** Jalankan pengujian ulang hingga *zero error*.
5. **Tahap 5 (Commit & Laporan):** Hapus berkas debugging sementara, buat commit lokal `fix: <deskripsi_bug>`, dan berikan laporan dalam format 3 poin.

---

## 2. Format Laporan Wajib 3 Poin
Setiap perbaikan bug wajib dilaporkan dalam format ringkas:
1. **Akar Masalah:** Penjelasan sumber masalah teknis penyebab terjadinya galat.
2. **Solusi:** Pendekatan dan logika teknis yang diterapkan untuk menuntaskan masalah secara permanen.
3. **File yang Diubah:** Daftar berkas beserta ringkasan baris atau komponen yang diperbarui.
