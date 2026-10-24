---
trigger: model_decision
description: Aktif saat operasi git, modifikasi berkas disk, mencegah hilangnya hasil kerja akibat git restore massal, atau menghindari konflik sinkronisasi buffer editor RAM vs disk.
---

# PROTEKSI BUFFER EDITOR & ANTI-REGRESSION GIT (ANTI-WIPEOUT PROTOCOL)

Aturan ini mengikat secara mutlak untuk mencegah hilangnya hasil kerja pengguna akibat desinkronisasi memori editor (*RAM buffer*) dengan penyimpanan (*disk*), maupun eksekusi Git yang ceroboh.

---

## 1. Larangan Keras Operasi Git Massal / Blanket
- **DILARANG KERAS** mengeksekusi perintah pemulihan massal seperti:
  - `git restore .`
  - `git checkout .`
  - `git reset --hard`
  - `git clean -fd`
- Pemulihan atau pembuangan perubahan **HANYA** boleh dilakukan secara bedah spesifik per-berkas tunggal (`git restore <path/to/file>`) atas persetujuan atau kebutuhan terisolasi.

---

## 2. Mitigasi Konflik Buffer Editor (RAM vs Disk)
- **Gejala Masalah:** Saat berkas sedang dibuka di editor, IDE menyimpan riwayat ketikan di RAM. Jika agen menulis file langsung ke disk (`replace_file_content`/`write_to_file`), IDE dapat mengalami konflik status (*dirty buffer race condition*) yang memicu penimpaan balik otomatis (*silent revert*) ke versi sebelum diedit.
- **Protokol Agen:**
  - Segera lakukan **atomic commit lokal Git** sesaat setelah menyelesaikan modifikasi berkas. Dengan commit tersimpan, riwayat tidak akan pernah hilang dan selalu dapat dipulihkan via Git (`git reflog`).
  - Jangan menimpa atau memodifikasi file yang baru saja diinformasikan sedang diedit manual oleh pengguna tanpa menyelaraskan kondisi terakhirnya.

---

## 3. Prosedur Penyelamatan / Self-Healing
- Jika terdeteksi adanya berkas yang kembali ke versi lama akibat konflik buffer IDE:
  - Periksa status commit terakhir via `git log -n 3 --oneline` atau `git reflog`.
  - Berikan panduan pemulihan instan dari Git HEAD kepada pengguna:
    ```powershell
    git checkout HEAD -- <nama_berkas>
    ```
