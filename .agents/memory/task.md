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
  - [x] Buat driver soket Marionette native zero-dependency di `automate_flow.py`
  - [x] Implementasi parser CLI `--prompt` tanpa wajib tanda petik (contoh: `--prompt gambar produk hidup`)
  - [x] Implementasi pemindai otomatis tab Google Flow (`aisandbox-root` / `flow-project-shell`)
  - [x] Implementasi pengisian prompt ke area editor Xpath via `document.execCommand('insertText')`
  - [x] Implementasi pemicuan tombol eksekusi Xpath dan event keyboard Enter
  - [x] Buat batch wrapper `flow.bat` untuk eksekusi mudah di terminal
  - [x] Uji unit parser dan sintaksis kode
  - [x] Sinkronisasi AST/Memori via agent-memory

- [ ] Lanjutan: Deteksi Status Generasi (Bersambung)
  - [ ] Pemantauan status proses generasi (InProgress / Rendering)
  - [ ] Verifikasi hasil output gambar selesai (Completed)
  - [ ] Penanganan kondisi error / limit kuota (Failed)
