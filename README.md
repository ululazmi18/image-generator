# Image Generator — Workspace Environment

Lingkungan pengembangan dan otomasi *image generation* berbasis peramban (Google Flow, Perchance, Flux, Midjourney, dan model AI lainnya) dengan profil browser terisolasi.

---

## 1. Topologi & Struktur Direktori

```text
Image Generator/
├── .agents/
│   ├── memory/
│   │   ├── PRD.md             # Blueprint kebutuhan & arsitektur
│   │   ├── DESIGN.md          # Standar visual terminal & desain
│   │   ├── task.md            # Status pelacakan tugas implementasi
│   │   └── memory.db          # Basis data memori SQLite FTS5
│   └── rules/                 # Aturan proyek termirror dari D:\.agents\rules
├── browser_profile/           # Direktori profil Firefox Portable terisolasi (diabaikan Git)
│   ├── starter.bat            # Script peluncur utama langsung di dalam folder profil
│   ├── start_browser.bat      # Alias peluncur cepat di dalam folder profil
│   ├── starter.py             # Peluncur alternatif berbasis Python Rich
│   ├── user.js                # Konfigurasi port otomasi Marionette permanen (2828)
│   └── [data profil Firefox]  # Bookmarks, logins, extensions, storage
├── image_generator.py         # Modul inti & fungsi otomasi Google Flow
├── Image Generator.py         # Entrypoint alternatif bernama "Image Generator"
├── image_generator.bat        # Pintasan runner batch utama
├── Image Generator.bat        # Pintasan runner batch bernama "Image Generator"
├── flow.bat                   # Alias runner batch
├── .gitignore                 # Konfigurasi proteksi privasi profil & cache
└── README.md                  # Panduan pengoperasian modul
```

---

## 2. Cara Menjalankan Profil Browser

Buka folder [browser_profile](file:///d:/Documents/Image%20Generator/browser_profile), lalu klik ganda [starter.bat](file:///d:/Documents/Image%20Generator/browser_profile/starter.bat) (atau [start_browser.bat](file:///d:/Documents/Image%20Generator/browser_profile/start_browser.bat)).

---

## 3. Otomasi Google Flow

### A. Penggunaan dari Skrip Python Lain (*Callable Function*)
Skrip ini dirancang khusus agar sangat mudah diimpor dan dipanggil oleh modul/skrip Python lain:

```python
from image_generator import generate_image

# 1. Simpan otomatis ke folder default (outputs/)
file_gambar = generate_image("gambar produk hidup")
print("Tersimpan di:", file_gambar)

# 2. Atau tentukan folder/nama file tujuan secara fleksibel
file_kustom = generate_image(
    prompt="pemandangan futuristik neon cyberpunk",
    output_path="D:/Project/assets/cyberpunk.jpg",
    timeout=180
)
```

### B. Penggunaan Melalui Terminal / CLI
Argumen prompt dapat diketik langsung tanpa tanda petik (spasi otomatis digabungkan):

```powershell
# 1. Eksekusi cepat via batch
.\image_generator.bat --prompt gambar produk hidup

# 2. Menentukan folder/nama file pemindahan output (-o / --output)
.\image_generator.bat --prompt gambar produk hidup -o hasil_gambar/

# 3. Eksekusi via Python langsung
python image_generator.py --prompt gambar produk hidup -o D:\Project\images\
# Atau
python "Image Generator.py" --prompt gambar produk hidup
```

---

## 4. Alur Kerja Otomasi & Teknologi Anti-Deteksi (Solusi 1: Native OS Input)
1. **Stealth Driver Mode:** Browser dijalankan dengan `dom.webdriver.enabled = false` di `user.js`, sehingga `navigator.webdriver` bernilai `undefined` (sama seperti peramban manusia biasa tanpa tanda robot).
2. **Aktivasi & Fokus Jendela:** Mengaktifkan jendela Firefox ke garis depan dan membypass pembatasan Windows foreground lock.
3. **Injeksi Prompt Native OS:** Teks prompt disalin ke Windows Clipboard (`win32clipboard`), kursor diposisikan di editor prompt, lalu dikirimkan hardware keystrokes asli (`Ctrl+V` dan `Enter` fisik via Windows API `keybd_event`) sehingga `event.isTrusted === true`.
4. **Hover & Deteksi Selesai:** Kursor mouse fisik digerakkan ke atas tile gambar (`flow-grid-tile-container[1]`) dan memantau ketersediaan hotbar tombol 3 (`flow-image-hotbar button[3]/mat-icon`) sebagai indikator render selesai.
5. **Buka Menu Opsi:** Mengeklik tombol 3 pada hotbar secara fisik untuk membuka context menu overlay.
6. **Akses Submenu Download:** Mengarahkan mouse ke menu item ke-5, lalu mengeklik submenu item ke-2 secara fisik untuk memicu unduhan.
7. **Pemantauan Unduhan:** Memantau kemunculan berkas `.jpg` baru di direktori unduhan (`D:\Downloads`) hingga selesai (tidak ada berkas sementara `.part`).
8. **Pemindahan Fleksibel:** Memindahkan berkas ke direktori yang diinginkan (default ke folder `outputs/` atau sesuai parameter pemanggil).
