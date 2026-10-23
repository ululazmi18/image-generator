---
trigger: model_decision
description: Aktif saat melakukan refactoring kode sumber, pembersihan duplikasi logika (DRY), perapian struktur berbasis prinsip SOLID, atau restrukturisasi tanpa mengubah perilaku sistem.
---

# ALUR REFACTORING & OPTIMALISASI KODE (REFACTORING PROTOCOL - ECC HARMONIZED)

Pedoman ini mengatur tahapan restrukturisasi dan simplifikasi kode dengan perlindungan anti-regresi mutlak mengadopsi standar Everything Claude Code (ECC).

---

## Prinsip Besi: Dilarang Refactoring Tanpa Baseline Test
> **Aturan Mutlak:** Dilarang keras melakukan refactoring pada kode yang belum memiliki pengujian otomatis. Jika test belum ada, wajib buat baseline test terlebih dahulu untuk mengunci perilaku yang ada saat ini sebelum memodifikasi kode produksi.

---

## 5 Tahap Pelaksanaan Refactoring

1. **Tahap 1 (Audit Kode & Penguncian Baseline Test):**
   - Identifikasi duplikasi kode (*DRY*), kompleksitas siklomatik, atau inefisiensi algoritma/kueri.
   - Jalankan test suite eksisting untuk memverifikasi bahwa seluruh test lulus 100% (*Green*).
   - Jika cakupan test kurang, buat test baru untuk mengunci kontrak masukan dan keluaran sistem saat ini.

2. **Tahap 2 (Preservasi Kontrak & Perilaku 100%):**
   - Seluruh antarmuka eksternal (*public API/signatures*), format kembalian, dan efek samping sistem wajib identik 100%.
   - Dilarang menyisipkan perubahan fitur baru atau modifikasi logika bisnis saat melakukan refactoring.

3. **Tahap 3 (Restrukturisasi Bedah & Simplifikasi):**
   - Terapkan perubahan bedah (*surgical changes*); hanya ubah bagian yang menjadi target refaktor.
   - Adopsi standar *code-simplifier* ECC: hapus kode mati (*dead code*), sederhanakan percabangan bersarang, dan pecah modul besar menjadi fungsi utilitas modular.
   - Larang refactoring siluman (*stealth refactoring*) pada modul atau berkas di luar target tugas.

4. **Tahap 4 (Verifikasi Uji Regresi & Linter):**
   - Jalankan kembali seluruh baseline test. Wajib lulus 100% tanpa ada satu pun pengujian yang gagal atau terlewat.
   - Pastikan kode lolos linter (*zero lint errors*) dan aman dari kebocoran memori.

5. **Tahap 5 (Atomic Commit):**
   - Buat git commit lokal konvensional: `refactor: <deskripsi_refaktor>` yang mendokumentasikan alasan dan manfaat perapian.
