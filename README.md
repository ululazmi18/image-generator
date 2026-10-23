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

## 4. Dua Versi Modul Otomasi

### A. Versi 2 (Default): `image_generator.py` (Silent Background Edition)
- **Zero Cursor Hijacking:** 100% bebas dari pergerakan mouse kursor fisik Windows, keyboard hardware, atau clipboard OS. Pengguna bebas mengetik, bekerja, atau bermain game tanpa interupsi sedikit pun.
- **Berjalan di Latar Belakang (Minimized / Headless):** Jendela browser dibuka secara terminimalkan (`SW_SHOWMINNOACTIVE`) tanpa mencuri fokus jendela, atau mode `--headless` murni tanpa GUI.
- **Stealth DOM & Gecko Bridge:** Injeksi prompt via ProseMirror DOM event, klik tombol generate via Gecko C++ native click, navigasi menu opsi & resolusi 1K via Angular CDK overlay events.
- **Pembersihan Otomatis:** Setelah berkas 1K diunduh dan dipindahkan ke direktori tujuan, gambar di kanvas Google Flow otomatis dipindahkan ke sampah (*trash*).

### B. Versi 1 (Legacy / Arsip): `image_generator_v1.py` (Native OS Input Edition)
- Menggunakan pergerakan kursor mouse fisik Windows (`win32api.SetCursorPos`, `mouse_event`), clipboard OS (`win32clipboard`), hardware keystrokes `Ctrl+V`, dan aktivasi jendela foreground.
- Dipertahankan untuk kebutuhan audit, perbandingan metode, atau demonstrasi visual bertahap (`test_step_by_step.py`).

---

## 5. Parameter CLI & Opsi Baris Perintah
```powershell
# 1. Mode Senyap Standar (Minimized Background)
python image_generator.py --prompt gambar pemandangan danau bersalju -o outputs/

# 2. Mode Headless (Murni Tanpa Antarmuka GUI)
python image_generator.py --headless --prompt robot kucing futuristik di kota tokyo

# 3. Kustomisasi Batas Waktu & Direktori
python image_generator.py --timeout 240 --dest D:\Assets\AI\ --prompt kastil fantasi megah

# 4. Menjalankan Versi 1 (Native OS Cursor)
python image_generator_v1.py --prompt pemandangan pantai tropis
```
