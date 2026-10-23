# IMPLEMENTATION TASK LIST (task.md)

- [x] Persiapan Profil Peramban & Skrip Peluncur Langsung
  - [x] Susun aturan master D:\.agents\rules dan inisialisasi .gitignore
  - [x] Rancang blueprint kanonikal (.agents/memory/PRD.md, DESIGN.md, task.md)
  - [x] Kloning profil `ulul_azmi` dari `D:\FirefoxPortable\Data\profiles\ulul_azmi` ke `browser_profile` (tanpa parent.lock & cache2)
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
