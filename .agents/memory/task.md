# IMPLEMENTATION TASK LIST (task.md)

- [x] Persiapan Profil Peramban & Skrip Peluncur Langsung
  - [x] Susun aturan master D:\.agents\rules dan inisialisasi .gitignore
  - [x] Rancang blueprint kanonikal (.agents/memory/PRD.md, DESIGN.md, task.md)
  - [x] Kloning profil `lia_nurjanah` dari `D:\FirefoxPortable\Data\profiles\lia_nurjanah` ke `browser_profile` (bersih dari lock/cache, menggantikan profil sebelumnya yang terdeteksi)
  - [x] Buat starter script langsung di dalam folder profil (`browser_profile\starter.bat` & `browser_profile\start_browser.bat`)
  - [x] Buat starter script berbasis Python/Rich (`browser_profile\starter.py`)
  - [x] Hapus root `start_browser.bat` sesuai permintaan pengguna
  - [x] Buat dokumentasi README.md panduan penggunaan
  - [x] Uji sintaksis starter script

- [x] Otomasi Google Flow (Tahap Input & Eksekusi Prompt)
  - [x] Konfigurasi port Marionette permanen (`browser_profile\user.js` & `-marionette` flag)
  - [x] Buat driver soket Marionette native zero-dependency
  - [x] Implementasi parser CLI `--prompt` tanpa wajib tanda petik (contoh: `--prompt gambar produk hidup`)
  - [x] Implementasi pemindai otomatis tab Google Flow (`aisandbox-root` / `flow-project-shell`)
  - [x] Implementasi pengisian prompt ke area editor Xpath via `document.execCommand('insertText')`
  - [x] Implementasi pemicuan tombol eksekusi Xpath dan event keyboard Enter

- [x] Alur Download & Pemindahan Berkas Otomatis
  - [x] Hover pada tile gambar pertama (`flow-grid-tile-container[1]`)
  - [x] Pemantauan hotbar button 3 (`flow-image-hotbar button[3]/mat-icon`) sebagai indikator render selesai
  - [x] Klik hotbar button 3 untuk membuka context menu
  - [x] Hover menu item ke-5 (`flow-menu-item[5]`) untuk membuka submenu download
  - [x] Klik submenu download ke-2 (`flow-menu-item[2]`) untuk mengunduh gambar asli
  - [x] Pemantauan direktori unduhan sampai berkas `.jpg` selesai (tidak ada berkas `.part`)
  - [x] Pemindahan berkas fleksibel ke path pemanggil atau default `outputs/`
  - [x] Sediakan fungsi callable `generate_image(prompt, output_path=None)` untuk diimpor skrip lain
  - [x] Penamaan modul `image_generator.py` dan entri `Image Generator.py` serta runner `.bat`

- [x] Solusi 1: Native OS Input & Stealth Anti-Deteksi
  - [x] Injeksi stealth pref `dom.webdriver.enabled = false` ke `browser_profile/user.js` (menghapus deteksi `navigator.webdriver`)
  - [x] Implementasi `NativeOSController` (Windows Clipboard `win32clipboard`, `SetProcessDpiAwareness`, `SetThreadDesktop`)
  - [x] Aktivasi dan pemfokusan jendela Firefox ke garis depan (bypassing Windows foreground lock)
  - [x] Pengiriman input prompt via Clipboard OS dan tombol hardware (`Ctrl+V` + `Enter` fisik via `win32api.keybd_event`) agar `event.isTrusted === true`
  - [x] Pengiriman event pergerakan kursor mouse dan klik fisik (`win32api.mouse_event`) berbasis koordinat layar `window.mozInnerScreenX`
  - [x] Self-healing pembersihan otomatis file lock yatim `parent.lock` saat Firefox tidak berjalan

- [x] Pengujian Browser Natif & Integrasi Hasil Empiris ke Profil Lokal
  - [x] Eksekusi uji coba end-to-end pada browser natif di proyek `https://flow.google.com/project/8eed2cd9-e563-46d8-9ad2-395e53901db4` (100% Berhasil)
  - [x] Temuan krusial alur unduhan: Menu "Download" membuka submenu sekunder yang mewajibkan klik pada opsi "1K (Ukuran asli)"
  - [x] Rekam bukti video interaksi web: `test_flow_e2e_1792775506146.webp` dan screenshot unduhan berhasil
  - [x] Perbarui selector dan logika `click_hotbar_and_download()` pada `image_generator.py` dan `test_step_by_step.py` agar memilih opsi "1K (Ukuran asli)"
  - [x] Implementasi tangkapan layar murni halaman web (`driver.take_screenshot()`) tanpa frame Windows desktop
  - [x] Modifikasi `userChrome.css` untuk menghapus garis merah bergaris dan ikon robot peramban
  - [x] Validasi sintaksis dan sinkronisasi basis data memori AST (77 entitas)

- [x] Alur Penghapusan Gambar ('Pindahkan ke sampah')
  - [x] Pengujian empiris pada browser natif membuktikan `Pindahkan ke sampah` langsung menghapus tile gambar tanpa modal dialog konfirmasi
  - [x] Bukti video rekaman `test_delete_flow_1792796065753.webp` dan screenshot kanvas bersih `media_1792796119211.png`
  - [x] Integrasi method `delete_current_tile()` ke `ImageGenerator` pada `image_generator.py`
  - [x] Penambahan LANGKAH 11 ke `test_step_by_step.py` lengkap dengan screenshot kanvas bersih pasca penghapusan

- [x] Metode Silent Background Tanpa Mengontrol Kursor Pengguna (image_generator.py v2 & image_generator_v1.py)
  - [x] Salin dan preservasi versi stabil metode Native OS Input ke `image_generator_v1.py`
  - [x] Eliminasi seluruh panggilan `win32api.SetCursorPos`, `mouse_event`, `keybd_event`, dan `win32clipboard` pada `image_generator.py` v2
  - [x] Injeksi prompt via ProseMirror DOM (`document.execCommand('insertText')` + `InputEvent`) secara senyap
  - [x] Klik tombol generate via Gecko native `WebDriver:ElementClick` (0% pergerakan mouse kursor OS)
  - [x] Pelacakan status render tile gambar baru berbasis snapshot `initial_state` (`imgCount` & `firstImgSrc`) untuk mencegah false positive gambar lama
  - [x] Buka hotbar & navigasi menu unduhan resolusi 1K via DOM click pada Angular CDK overlay
  - [x] Penghapusan gambar otomatis dari kanvas ('Pindahkan ke sampah') setelah berkas tersimpan
  - [x] Dukungan peramban terminimalkan di latar belakang (`SW_SHOWMINNOACTIVE`) dan mode `--headless`
  - [x] Pengujian empiris end-to-end `image_generator.py` berhasil menghasilkan dan mengunduh gambar aurora borealis (1K) secara senyap dalam 37 detik tanpa menyentuh mouse pengguna

- [x] Standardisasi 2 Berkas Bersih & Dokumentasi Lengkap
  - [x] Hapus seluruh berkas v1 dan runner redundan (`image_generator_v1.py`, `Image Generator.bat`, `Image Generator.py`, `flow.bat`, `image_generator.bat`, `test_step_by_step.bat`, `test_step_by_step.py`)
  - [x] Sediakan satu runner Windows bersih `run.bat` dengan penanganan klik ganda (interactive prompt + pause) maupun CLI passthrough
  - [x] Tambahkan docstrings tingkat fungsi/metode lengkap dan mendalam pada `image_generator.py` (penjelasan, cara kerja di balik layar, Args, Returns, Raises, Example)
  - [x] Bersihkan unused imports (`win32con`, `win32gui`) dan selektor yang tidak terpakai
  - [x] Perbarui `README.md` dan sinkronisasi basis data memori AST (agent-memory)

- [x] Persiapan Rilis GitHub v1.0 & Pembersihan Bersih Workspace
  - [x] Pembersihan total folder dan berkas uji coba (`debug/*.png`, `reports/`, `deploy_staging/`, `REPORT.md`, `harness_audit.py`, `__pycache__/`)
  - [x] Preservasi struktur direktori bersih via `debug/.gitkeep` dan `outputs/.gitkeep`
  - [x] Konfigurasi `.gitignore` ketat (proteksi mutlak `browser_profile/`, kredensial, token, dan artefak output)
  - [x] Pembuatan berkas dependensi resmi `requirements.txt`
  - [x] Pembuatan berkas lisensi resmi `LICENSE` (MIT)
  - [x] Penulisan ulang `README.md` komprehensif berstandar kelas dunia (3 lini penggunaan: batch runner, CLI, Python module)
  - [x] Verifikasi zero-error py_compile dan Rich `--help` interface

- [x] Pemisahan Repositori Image Generator (Decoupling dari Repo Browser)
  - [x] Hapus modul setup peramban bawaan (`setup_browser.py` dan `stealth_addon/`) dari repo ini karena telah dideploy di Repo Browser
  - [x] Rampingkan `requirements.txt` khusus Image Generator (`rich`, `Pillow`)
  - [x] Tingkatkan `image_generator.py` untuk mendeteksi sesi peramban aktif dari Repo Browser via port Marionette (127.0.0.1:2828), environment variable, atau path tetangga
  - [x] Perbarui `README.md` dengan arsitektur ekosistem 2 repositori dan diagram koneksi ke Repo Browser


