---
trigger: model_decision
description: Aktif saat menangani path berkas, impor modul lokal, pemuatan aset/profil, atau memastikan skrip berjalan universal tanpa hardcoded drive saat di-clone di mana pun.
---

# PORTABILITAS UNIVERSAL & RESOLUSI PATH RELATIF

Pedoman ini mengatur larangan mutlak jalur (*path*) hardcoded lokal dan menegakkan arsitektur path dinamis agar repositori, modul, atau skrip dapat di-clone dan dijalankan di mesin, drive, maupun sistem operasi mana pun tanpa galat.

---

## 1. Larangan Mutlak Hardcoded Path & Drive
- **DILARANG KERAS menanamkan (*hardcode*) huruf drive lokal (`C:\`, `D:\`), direktori profil sistem spesifik (`C:\Users\...`), atau nama folder mesin lokal (`D:\New folder\...`) ke dalam skrip atau modul kode.**
- Jangan pernah mengasumsikan kode selalu dieksekusi dari drive atau direktori kerja tertentu.

---

## 2. Jangkar Relatif Dinamis (*Dynamic Root Anchoring*)
- Seluruh rujukan berkas internal, aset biner, profil peramban, modul subrepo, maupun skrip tetangga wajib dijangkarkan secara dinamis relatif terhadap lokasi berkas pemanggil:
  - **Python:** Gunakan `pkg_root = Path(__file__).resolve().parent.parent` atau `Path(__file__).resolve().parent`.
  - **Node.js:** Gunakan `path.resolve(__dirname, '..')` atau `new URL('.', import.meta.url)`.
  - **Windows Batch / PowerShell:** Gunakan `%~dp0` atau `$PSScriptRoot`.
- Dengan pendekatan ini, proyek dapat di-clone atau dipindahkan ke drive maupun folder apa pun dan seluruh aset internal tetap terdeteksi 100% akurat.

---

## 3. Fleksibilitas Direktori Kerja (*Workspace Agnostic*)
- Sediakan opsi parameter direktori kerja (misal: `workspace_dir: Path | None = None`) dengan nilai bawaan dinamis (seperti `Path.cwd()` atau `pkg_root`).
- Modul internal harus dapat diimpor dan dipanggil secara modular oleh proyek atau workspace lain tanpa memicu galat aset hilang atau *FileNotFoundError*.

---

## 4. Deteksi Komponen Sistem Lintas Platform
- **Eksekutabel & Driver Sistem:** Gunakan `shutil.which("nama_biner")` untuk mendeteksi ketersediaan aplikasi di PATH sistem alih-alih mengasumsikan biner selalu berada di folder tertentu.
- **Direktori Pengguna Standar:** Gunakan `Path.home()` untuk lokasi berkas pengguna (seperti `Path.home() / "Downloads"`), dan gunakan variabel lingkungan (`os.environ.get(...)`) dengan nilai fallback yang aman dan fleksibel.
