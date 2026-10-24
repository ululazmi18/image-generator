# Google Flow Image Generator 🎨🚀

> **Autonomous AI Image Generator with Native Headless Gecko Engine, Stealth Bypass, and Full Studio Settings.**  
> *100% Gratis, Tanpa Kuota Berbayar, Tanpa Mengganggu Kursor Pengguna (Zero Cursor Hijacking).*

---

## 🌟 Fitur Unggulan

- 💎 **100% Free & Unlimited:** Memanfaatkan platform Google Flow tanpa memerlukan langganan API berbayar atau kuota kredit.
- 🥷 **Silent Background & Zero Cursor Hijacking:** Berjalan 100% di latar belakang menggunakan mode `-headless` native Gecko via soket Marionette. Anda bebas mengetik, bekerja, atau bermain game tanpa kursor mouse terganggu.
- 📐 **Setelan Aspek Rasio Lengkap:** Mendukung 5 rasio native Google Flow:
  - `16:9` Widescreen Cinematic (`1376 × 768` px)
  - `4:3` Klasik / Standard Landscape (`1152 × 896` px)
  - `1:1` Square Persegi (`1024 × 1024` px)
  - `3:4` Dokumen / Formal Portrait (`896 × 1152` px)
  - `9:16` Smartphone Vertical / Shorts / Reels / TikTok (`768 × 1376` px)
- 🧠 **Multi-Model AI Selection:** Pilih model engine: `pro` (Nano Banana Pro), `lite` (Nano Banana 2 Lite), atau `2.1` (Nano Banana 2.1).
- 🔢 **Variasi Gambar Fleksibel:** Menghasilkan 1 hingga 4 variasi gambar per eksekusi (`x1`, `x2`, `x3`, `x4`).
- 🛡️ **Self-Healing & Auto-Retry Cerdas:** Mendeteksi kendala jaringan, server error, atau status batas penggunaan harian secara otomatis. Melakukan pembersihan kanvas (*clean slate*), cooldown, dan perulangan mandiri hingga gambar berhasil diunduh.
- 🧹 **Pembersihan Kanvas Otomatis:** Setelah gambar 1K berhasil disimpan ke direktori lokal, tile kanvas langsung dihapus (*Pindahkan ke sampah*) agar ruang kerja proyek tetap bersih dan ringan.
- 💻 **Antarmuka Terminal Modern:** Ditenagai oleh Rich Terminal UI lengkap dengan progress spinner, tabel konfigurasi, panel ringkasan, dan menu `--help` yang interaktif.
- 🔌 **Layanan Modul Python Kelas Perusahaan:** Dapat diimpor langsung (`from image_generator import generate, generate_image`) dengan type hints lengkap dan metadata keluaran `GenerationResult`.

---

## 📂 Struktur Repositori

```text
Image Generator/
├── .agents/                    # Konfigurasi memori & tata kelola agen AI
├── browser_profile/            # Direktori profil Firefox Portable terisolasi (diabaikan Git)
├── debug/                      # Direktori tangkapan layar saat mode --debug aktif
│   └── .gitkeep
├── outputs/                    # Direktori penyimpanan hasil gambar yang diunduh
│   └── .gitkeep
├── stealth_addon/              # Native WebExtension Stealth Bridge (bypass deteksi bot)
│   ├── manifest.json           # Manifest WebExtension V2
│   └── stealth.js              # Injeksi exportFunction/cloneInto Navigator.prototype
├── image_generator.py          # Modul inti Python & CLI Generator Gambar v1.0
├── setup_browser.py            # CLI bootstrapper & pengelola login akun Google
├── run.bat                     # Runner batch Windows (klik ganda atau CLI)
├── requirements.txt            # Dependensi pustaka Python resmi
├── LICENSE                     # Lisensi open-source MIT
├── .gitignore                  # Konfigurasi proteksi privasi profil & artefak
└── README.md                   # Dokumentasi resmi proyek
```

---

## 🚀 Panduan Memulai Cepat (Quick Start)

### 1. Prasyarat Sistem
- **Sistem Operasi:** Windows 10/11 (64-bit).
- **Python:** Versi 3.10 atau yang lebih baru.
- **Mozilla Firefox Portable:** Diunduh dan dikonfigurasi secara otomatis oleh skrip.

### 2. Instalasi Dependensi
Buka terminal (Command Prompt / PowerShell) di folder proyek, lalu jalankan:

```powershell
pip install -r requirements.txt
```

### 3. Setup Browser & Login Akun Google (Sekali Saja)
Sebelum menjalankan generasi pertama kali, masuk (*login*) ke akun Google Anda pada profil peramban terisolasi:

```powershell
python setup_browser.py --login
```
Peramban Firefox Portable akan terbuka. Silakan login ke akun Google Anda dan pastikan dapat membuka layanan [Google Flow](https://labs.google/fx/tools/flow). Setelah selesai, tutup jendela peramban. Profil dan sesi tersimpan aman secara lokal di folder `browser_profile/` (otomatis diabaikan oleh Git).

---

## 🎯 Cara Penggunaan

Tersedia 3 cara pemanfaatan sesuai kebutuhan Anda:

### Lini 1: Runner Windows (`run.bat`)
Cara termudah bagi pengguna desktop:
1. **Klik ganda (*Double Click*)** berkas [run.bat](file:///d:/Documents/Image%20Generator/run.bat).
2. Masukkan teks prompt ketika diminta pada antarmuka terminal.
3. Generator akan bekerja secara otomatis di latar belakang dan menyimpan gambar ke folder `outputs/`.

Atau jalankan `run.bat` melalui terminal dengan argumen langsung:
```powershell
.\run.bat -p "lukisan cat minyak pemandangan pegunungan fajar" -a 16:9 -m pro
```

---

### Lini 2: Baris Perintah Terminal (CLI)

Gunakan perintah `python image_generator.py` dengan opsi fleksibel:

```powershell
# 1. Bantuan Lengkap (Help Menu)
python image_generator.py --help

# 2. Generasi Standar (Nano Banana Pro, Rasio 16:9, Variasi 1)
python image_generator.py -p "kucing putih berbulu lebat di taman bunga sakura"

# 3. Kustomisasi Aspek Rasio (16:9, 1:1, 9:16, 4:3, 3:4)
python image_generator.py -p "cangkir kopi latte art bunga teratai" -a 1:1

# 4. Kustomisasi Model AI (pro, lite, 2.1)
python image_generator.py -p "mobil sport futuristik di kota neon cyberpunk" -m pro -a 16:9

# 5. Kustomisasi Variasi Gambar (1 sampai 4)
python image_generator.py -p "kastil fantasi di atas awan senja" -c 2

# 6. Menentukan Folder / Nama File Tujuan (-o / --output)
python image_generator.py -p "astronot menjelajahi gua kristal mars" -o "outputs/mars_hero.jpg"

# 7. Mode Debug (Menyimpan tangkapan layar setiap fase ke folder debug/)
python image_generator.py -p "potret close-up burung merak emas" --debug
```

#### Tabel Opsi CLI

| Opsi Singkat | Opsi Panjang | Nilai Default | Deskripsi |
| :--- | :--- | :--- | :--- |
| `-p` | `--prompt` | *None* (Interaktif) | Teks prompt gambar (Bahasa Indonesia / Inggris) |
| `-m` | `--model` | `pro` | Pilihan model: `pro` (Banana Pro), `lite` (Banana 2 Lite), `2.1` |
| `-a` | `--aspect-ratio`| `16:9` | Pilihan rasio: `16:9`, `4:3`, `1:1`, `3:4`, `9:16` |
| `-c` | `--count` | `1` | Jumlah variasi gambar: `1`, `2`, `3`, atau `4` |
| `-o` | `--output` | `outputs/` | Direktori atau nama berkas tujuan penyimpanan |
| `-t` | `--timeout` | `180` | Batas waktu tunggu render per percobaan (detik) |
| | `--headless` | `True` | Berjalan di latar belakang (gunakan `--no-headless` untuk melihat GUI) |
| | `--debug` | `False` | Simpan visual audit setiap langkah ke folder `debug/` |
| `-h` | `--help` | | Menampilkan antarmuka bantuan Rich lengkap |

---

### Lini 3: Modul Python (*Callable API*)

Modul [image_generator.py](file:///d:/Documents/Image%20Generator/image_generator.py) dapat diimpor langsung ke dalam proyek Python Anda:

```python
from image_generator import generate, generate_image

# -------------------------------------------------------------
# Contoh 1: generate_image() — Mengembalikan Path berkas lokal
# -------------------------------------------------------------
image_path = generate_image(
    prompt="pemandangan matahari terbenam di pantai tropis dengan siluet kelapa",
    aspect_ratio="16:9",
    model="pro",
    output_path="outputs/sunset.jpg"
)
print(f"Gambar berhasil dibuat: {image_path}")

# -------------------------------------------------------------
# Contoh 2: generate() — Mengembalikan objek GenerationResult
# -------------------------------------------------------------
result = generate(
    prompt="robot koki memasak sushi di dapur futuristik",
    aspect_ratio="1:1",
    model="pro",
    count=1,
    debug=False
)

if result.success:
    print(f"Status: Sukses ({result.duration_seconds:.1f} detik)")
    print(f"File: {result.image_path}")
    print(f"Dimensi/Ukuran: {result.aspect_ratio} ({result.file_size_human})")
    print(f"Model Engine: {result.model_name}")
else:
    print(f"Gagal: {result.error_message}")
```

---

## 📊 Matriks Aspek Rasio & Resolusi Google Flow

| Aspek Rasio | Dimensi Resolusi | Orientasi | Cocok Untuk |
| :---: | :---: | :---: | :--- |
| **`16:9`** | `1376 × 768` px | Landscape Widescreen | YouTube Thumbnail, Wallpaper Desktop, Banner Web |
| **`4:3`** | `1152 × 896` px | Klasik Landscape | Presentasi Slides, Foto Cetak Standar |
| **`1:1`** | `1024 × 1024` px | Square Persegi | Feed Instagram, Avatar Profil, Logo, Merchandise |
| **`3:4`** | `896 × 1152` px | Klasik Portrait | Foto Portofolio, Dokumen Vertikal |
| **`9:16`** | `768 × 1376` px | Vertical Fullscreen | Instagram Stories, TikTok, YouTube Shorts, Reels |

---

## 🛠️ Keamanan & Privasi

1. **Isolasi Profil Browser:** Seluruh kredensial akun, cookies, dan token otentikasi disimpan di dalam folder lokal `browser_profile/` dan secara tegas dikecualikan oleh [.gitignore](file:///d:/Documents/Image%20Generator/.gitignore).
2. **Kedaulatan Git:** Repositori ini tidak akan pernah menyertakan kredensial rahasia atau berkas riwayat sesi pribadi Anda.
3. **Tanpa Telemetri Pihak Ketiga:** Tidak ada pengiriman data ke server luar selain komunikasi langsung ke domain resmi Google.

---

## 📄 Lisensi

Proyek ini dilisensikan di bawah lisensi open-source [MIT License](file:///d:/Documents/Image%20Generator/LICENSE). Bebas digunakan, dimodifikasi, dan didistribusikan untuk keperluan pribadi maupun komersial.
