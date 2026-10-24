# Image Generator — Workspace Environment

Lingkungan pengembangan dan otomasi *image generation* berbasis peramban (Google Flow) dengan profil browser terisolasi, berjalan 100% senyap di latar belakang (*silent background*) tanpa mengontrol kursor pengguna (*zero cursor hijacking*).

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
│   ├── starter.bat            # Script peluncur utama browser profil
│   ├── start_browser.bat      # Alias peluncur cepat browser profil
│   ├── starter.py             # Peluncur alternatif berbasis Python Rich
│   ├── user.js                # Konfigurasi port otomasi Marionette permanen (2828)
│   └── [data profil Firefox]  # Bookmarks, logins, extensions, storage
├── image_generator.py         # Modul inti Python & CLI otomasi Google Flow (v2 Silent)
├── run.bat                    # Runner batch utama Windows (klik ganda atau via CLI)
├── outputs/                   # Folder hasil unduhan gambar (diabaikan Git)
├── .gitignore                 # Konfigurasi proteksi privasi profil, output, & cache
└── README.md                  # Panduan pengoperasian modul
```

---

## 2. Cara Menjalankan untuk Pengguna Windows

### A. Melalui Klik Ganda (*Double Click*)
Cukup klik ganda [run.bat](file:///d:/Documents/Image%20Generator/run.bat).
Skrip akan menampilkan banner antarmuka, meminta Anda memasukkan teks prompt, lalu memproses pembuatan dan pengunduhan gambar secara senyap di latar belakang tanpa mengganggu kursor atau aktivitas layar Anda.

### B. Melalui Terminal / Baris Perintah (CLI)
Argumen prompt dapat diketik langsung tanpa tanda petik:

```powershell
# 1. Menghasilkan gambar dengan prompt langsung
.\run.bat --prompt pemandangan danau pegunungan saat fajar berkabut

# 2. Menentukan direktori/nama file tujuan (-o / --output)
.\run.bat --prompt kucing lucu di taman bunga sakura -o outputs/

# 3. Mode Headless (murni tanpa antarmuka grafis di latar belakang)
.\run.bat --headless --prompt robot astronot di planet mars

# 4. Kustomisasi batas waktu (timeout dalam detik)
.\run.bat --timeout 240 --prompt kastil megah fantasi di puncak tebing bersalju
```

---

## 3. Penggunaan Sebagai Modul Python (*Callable API*)

Modul [image_generator.py](file:///d:/Documents/Image%20Generator/image_generator.py) memiliki dokumentasi tipe dan docstrings lengkap (*hover tooltip* di editor IDE). Dapat diimpor langsung oleh skrip atau modul lain:

```python
from image_generator import generate_image

# 1. Simpan otomatis ke folder default (outputs/)
file_gambar = generate_image("pemandangan matahari terbenam di pantai tropis")
print("Tersimpan di:", file_gambar)

# 2. Atau tentukan folder / nama berkas tujuan secara spesifik
file_kustom = generate_image(
    prompt="cyberpunk neon city futuristic car",
    output_path="D:/Project/assets/hero.jpg",
    headless=True,  # Mode tanpa GUI di latar belakang
    timeout=180     # Batas waktu maksimal dalam detik
)
```

---

## 4. Keunggulan Arsitektur Silent Background

1. **Zero Cursor Hijacking (0% Interupsi Kursor):**
   Tidak menyentuh mouse kursor fisik Windows, clipboard OS, atau keyboard hardware. Pengguna bebas mengetik, bekerja, atau bermain game tanpa interupsi.
2. **Background & Minimized Mode:**
   Peramban dijalankan dalam status terminimalkan (`SW_SHOWMINNOACTIVE`) tanpa mencuri fokus jendela aktif pengguna, atau mode `--headless` murni tanpa jendela.
3. **Stealth DOM & Gecko Bridge:**
   Injeksi prompt menggunakan ProseMirror DOM event, klik tombol generate menggunakan Gecko C++ native click (`WebDriver:ElementClick`), dan navigasi menu unduhan resolusi 1K menggunakan Angular CDK overlay event.
4. **Pembersihan Otomatis Kanvas:**
   Setelah berkas gambar 1K berhasil diunduh dan dipindahkan ke direktori tujuan, gambar di kanvas Google Flow langsung dihapus (**Pindahkan ke sampah**).
