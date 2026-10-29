# PRODUCT REQUIREMENTS DOCUMENT (PRD)
## Image Generator — Browser Automation & Isolated Profile Environment

### 1. Overview
Workspace `Image Generator` dirancang untuk otomasi generasi gambar berbasis peramban (web-based AI image generation seperti Perchance, Midjourney, Flux, Leonardo, dsb.) dan utilitas terkait. Langkah fondasi pertama adalah menyiapkan lingkungan profil peramban terisolasi (`browser_profile`) berbasis Firefox Portable (`ulul_azmi`) dengan skrip peluncur (*starter*) langsung di dalam direktori profil.

### 2. Requirements & User Stories
- **Isolasi Penuh:** Pengguna membutuhkan profil peramban yang terisolasi dari instalasi utama agar sesi login, token, bookmark, dan ekstensi dapat digunakan khusus untuk proyek `Image Generator`.
- **In-Folder Starter:** Pengguna dapat langsung membuka folder profil dan mengeklik berkas starter (`starter.bat` / `start_browser.bat`) untuk meluncurkan peramban dengan parameter profil yang tepat (`-no-remote -profile "%~dp0"`).
- **Anti-Telemetry & Safe Run:** Menonaktifkan Mozilla Crash Reporter agar tidak menulis log atau membuang crash dump ke partisi `C:\`.

### 3. Core Features (v2.2 Architecture)
1. **Isolated Single-Profile Architecture with Account Vault (`browser_profile`):**
   - Satu direktori profil utama terisolasi (`browser_profile/`).
   - Sistem Account Vault ringan (`browser_profile/accounts/<sanitized_email>/cookies.sqlite`), berukuran hanya ~512 KB per akun (hemat 99% disk tanpa menggandakan profil).
   - Pergantian sesi akun instan via CLI `--email <email>` dan login akun baru via `--email` + `--password`.
2. **Quota Guard & Fast-Fail Notification:**
   - Deteksi dini batasan kuota Google Flow (`QuotaExceededError`).
   - Notifikasi Rich Panel yang menampilkan email akun aktif yang terkena batas, daftar akun alternatif yang tersedia di brankas, serta perintah satu klik untuk berganti akun.
3. **Self-Healing Canvas Recovery:**
   - Deteksi otomatis kanvas kadaluarsa atau status 404 (`404?reason=project`) dan editor ProseMirror yang hilang.
   - Pemulihan mandiri dengan navigasi ke `FLOW_HOME_URL` untuk membuka proyek yang valid atau membuat proyek baru.
4. **Multi-Model, Multi-Ratio & Multi-Resolution Generator:**
   - Mendukung model AI: `pro` (Nano Banana Pro), `lite` (Nano Banana 2 Lite), `2.1` (Nano Banana 2.1).
   - Mendukung aspek rasio: `16:9`, `4:3`, `1:1`, `3:4`, `9:16`.
   - Mendukung resolusi unduhan: `2k` (Default, resolusi ditingkatkan / upscaling otomatis) dan `1k` (ukuran asli tanpa jeda waktu upscaling).
   - Multi-tile unduhan otomatis (`-c 1..4`) dengan penamaan bertingkat (`-1, -2, -3, -4`).
   - Pembersihan kanvas massal otomatis (*Pindahkan ke sampah*) setelah seluruh gambar berhasil disimpan.
5. **Zero-Cursor Hijacking (100% Background Automation):**
   - Injeksi teks prompt via ProseMirror DOM (`document.execCommand` + `InputEvent`).
   - Klik tombol generate dan menu context via DOM event murni tanpa menggerakkan mouse fisik pengguna.
   - Dual-engine browser: Firefox Portable Stealth Edition dan fallback Chromium Playwright otomatis.

### 4. User Flow
1. Pengguna menjalankan runner [run.bat](run.bat) atau CLI `python image_generator.py -p "prompt" [-a rasio] [-m model] [-c count] [--res 2k|1k] [--email email]`.
2. Skrip memeriksa sesi akun Google di `browser_profile/cookies.sqlite`:
   - Jika argumen `--email` diberikan dan berbeda dari akun aktif di browser, sistem secara otomatis menukar file `cookies.sqlite` dari Account Vault.
   - Jika akun belum ada di vault, skrip memicu autentikasi CLI headless untuk menyimpannya.
3. Skrip memvalidasi kanvas Google Flow: jika proyek 404/rusak, otomatis dipulihkan ke proyek yang sehat dari beranda.
4. Skrip mengisi prompt, menekan Generate, memantau hingga tile render selesai, mengunduh gambar sesuai resolusi pilihan (default 2K upscaled atau 1K ukuran asli), dan membersihkan kanvas dari server.

### 5. Constraints & Guardrails
- Profil peramban, biner portabel, dan seluruh token sesi akun TIDAK BOLEH dilacak oleh Git (dilindungi ketat oleh `.gitignore`).
- Zero cursor hijacking: dilarang menggunakan fungsi Windows API yang menggerakkan kursor mouse atau keyboard fisik pengguna.
- Kedaulatan Git lokal: commit dilakukan secara lokal dengan pesan Conventional Commit deskriptif.
