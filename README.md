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
│   ├── open_browser.bat       # Script peluncur utama peramban profil (kelola akun / GUI)
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
# 1. Menghasilkan gambar dengan prompt langsung (100% otomatis headless & retry tanpa batas)
.\run.bat --prompt pemandangan danau pegunungan saat fajar berkabut

# 2. Menentukan direktori/nama file tujuan (-o / --output)
.\run.bat --prompt kucing lucu di taman bunga sakura -o outputs/

# 3. Kustomisasi batas waktu per percobaan (timeout dalam detik)
.\run.bat --timeout 240 --prompt kastil megah fantasi di puncak tebing bersalju
```

---

## 3. Penggunaan Sebagai Modul Python (*Callable API*)

Modul [image_generator.py](file:///d:/Documents/Image%20Generator/image_generator.py) memiliki dokumentasi tipe dan docstrings lengkap (*hover tooltip* di editor IDE). Dapat diimpor langsung oleh skrip atau modul lain, dan secara permanen selalu berjalan dalam mode native headless di latar belakang dengan dukungan pemulihan mandiri tanpa batas (*unlimited self-healing auto-retry*):

```python
from image_generator import generate_image

# 1. Simpan otomatis ke folder default (outputs/) — 100% native headless & auto-retry tanpa batas
file_gambar = generate_image("pemandangan matahari terbenam di pantai tropis")
print("Tersimpan di:", file_gambar)

# 2. Kustomisasi folder tujuan dan batas timeout per percobaan
file_kustom = generate_image(
    prompt="cyberpunk neon city futuristic car",
    output_path="D:/Project/assets/hero.jpg",
    timeout=200,
)
```

---

## 4. Keunggulan Arsitektur Silent Background

1. **Auto-Retry Tanpa Batas & Self-Healing:**
   Google Flow terkadang gagal merender (misal: "Anda telah mencapai batas penggunaan" atau server error). Skrip mendeteksi tile kegagalan secara instan dalam 1–2 detik, membersihkannya dari kanvas, melakukan cooldown dan penyegaran halaman berkala, serta mengulang proses secara mandiri tanpa batasan (*unlimited loop*) sampai berkas gambar 100% berhasil dihasilkan dan diunduh.
2. **Zero Cursor Hijacking (0% Interupsi Kursor):**
   Tidak menyentuh mouse kursor fisik Windows, clipboard OS, atau keyboard hardware. Pengguna bebas mengetik, bekerja, atau bermain game tanpa interupsi.
3. **100% Native Headless Mode:**
   Peramban Firefox Portable diluncurkan secara permanen dalam mode `-headless` murni di latar belakang tanpa jendela GUI sama sekali di layar, tanpa perlu mengonfigurasi opsi tambahan.
4. **Stealth DOM & Gecko Bridge:**
   Injeksi prompt menggunakan ProseMirror DOM event, klik tombol generate menggunakan Gecko C++ native click (`WebDriver:ElementClick`), dan navigasi menu unduhan resolusi 1K menggunakan Angular CDK overlay event.
5. **Pembersihan Otomatis Kanvas:**
   Setelah berkas gambar 1K berhasil diunduh dan dipindahkan ke direktori tujuan, gambar di kanvas Google Flow langsung dihapus (**Pindahkan ke sampah**).
