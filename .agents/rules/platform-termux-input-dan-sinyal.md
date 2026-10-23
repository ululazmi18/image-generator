---
trigger: model_decision
description: Aktif saat mengimplementasikan input keyboard non-blocking POSIX di Termux, penanganan sinyal SIGINT/SIGTERM Android, atau SQLite WAL di lingkungan mobile.
---

# INPUT NON-BLOCKING, SINYAL POSIX & SQLITE WAL DI TERMUX

Pedoman ini mengatur implementasi input keyboard non-blocking yang kompatibel lintas-platform, penanganan sinyal Android, dan keandalan penyimpanan SQLite WAL pada Termux.

---

## 1. Input Non-Blocking & Interaksi Tombol
- **Dilarang bergantung hanya pada `msvcrt`:** Pustaka `msvcrt` hanya ada di Windows dan akan menyebabkan aplikasi macet total (*freeze*) di Termux.
- **Implementasi Universal POSIX:** Untuk input interaktif tanpa jeda (*non-blocking keyboard listener* di dalam loop `Rich.Live`), wajib menggunakan `termios`, `tty.setcbreak`, dan `select.select([sys.stdin], ...)` di lingkungan non-Windows.
- **Pemulihan Terminal:** Sediakan pemulihan terminal (*terminal state restore*) secara defensif di dalam blok `finally` agar terminal Termux tidak rusak (*glitched echo*) saat skrip ditutup.

---

## 2. Penanganan Sinyal (Android Lifecycle & Battery)
- Pasang penangan sinyal `signal.SIGINT` dan `signal.SIGTERM` agar saat proses ditutup oleh Android Task Manager atau notifikasi Termux, berkas database SQLite (mode WAL) dan antrean memori di-*flush* dengan aman (*graceful shutdown*).

---

## 3. Penyimpanan SQLite WAL di Android
- Simpan database SQLite di direktori lokal proyek (bukan di `/sdcard/` FAT32 yang tidak mendukung POSIX file locks).
- Pertahankan mode `PRAGMA journal_mode=WAL;` dan `PRAGMA synchronous=NORMAL;`.

---

## 4. Dependensi Ringan (Lightweight Dependencies)
- Jaga dependensi pihak ketiga tetap minimal, ringan, dan mudah dipasang di Termux tanpa memerlukan kompilasi C/C++ yang berat.
- Setiap paket eksternal baru wajib didaftarkan ke `requirements.txt` dan dipastikan kompatibel dengan `pkg install python && pip install`.
