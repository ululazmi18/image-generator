# Google Flow Image Generator 🎨⚡

> **Generator gambar AI cerdas, cepat, dan 100% senyap di latar belakang (*silent background*) bertenaga antarmuka Google Flow.**  
> *Bebas kuota berbayar, resolusi asli 1K, dan zero cursor hijacking.*

---

## 💎 Keunggulan & Manfaat Utama

- 🆓 **100% Free & Unlimited:** Buat gambar AI sepuasnya tanpa biaya langganan, tanpa token berbayar, dan tanpa batas kuota API.
- 🥷 **Zero Cursor Hijacking (100% Senyap):** Bekerja murni di latar belakang tanpa menggerakkan kursor mouse fisik, tanpa mengambil alih keyboard, dan tanpa mencuri fokus jendela. Anda tetap bebas mengetik, bekerja, atau bermain game tanpa gangguan.
- 🖼️ **Unduh Otomatis Resolusi Asli (1K):** Setiap gambar yang dibuat langsung diunduh dalam resolusi penuh dan disimpan rapi ke folder tujuan Anda.
- 🧹 **Pembersihan Kanvas Mandiri (*Auto Canvas Cleaner*):** Secara otomatis menghapus tile hasil render dari kanvas (*Pindahkan ke sampah*) setelah berkas berhasil disimpan di komputer lokal.
- 🛡️ **Proteksi & Pemulihan Cerdas (*Self-Healing*):** Mendeteksi kegagalan render atau status batas sementara secara otomatis, mereset kanvas, dan mencoba kembali hingga gambar berhasil dibuat.

---

## ✨ Fitur-Fitur Andalan

### 1. Multi-Model AI Engine
Pilih model AI sesuai kebutuhan estetika dan detail gambar:
- **`pro` (Nano Banana Pro — Default):** Kualitas visual tertinggi, rendering detail presisi, dan pencahayaan sinematik.
- **`lite` (Nano Banana 2 Lite):** Generasi cepat dan efisien untuk eksplorasi konsep.
- **`2.1` (Nano Banana 2.1):** Model mutakhir dengan kepatuhan prompt yang tajam.

### 2. Beragam Pilihan Aspek Rasio
Dukungan penuh untuk seluruh kebutuhan media sosial dan format desain:
| Rasio | Dimensi Resolusi | Orientasi | Cocok Untuk |
| :---: | :---: | :---: | :--- |
| **`16:9`** | `1376 × 768` px | Landscape Sinematik | YouTube Thumbnail, Banner Web, Desktop Wallpaper |
| **`4:3`** | `1152 × 896` px | Landscape Klasik | Slide Presentasi, Media Cetak Standar |
| **`1:1`** | `1024 × 1024` px | Square Persegi | Instagram Feed, Avatar Profil, Logo, Merchandise |
| **`3:4`** | `896 × 1152` px | Portrait Formal | Foto Portofolio, Poster Vertikal |
| **`9:16`** | `768 × 1376` px | Portrait Layar Penuh | TikTok, Instagram Stories, YouTube Shorts, Reels |

### 3. Kontrol Jumlah Variasi Gambar
Hasilkan **1 hingga 4 variasi gambar** sekaligus dalam satu kali perintah menggunakan opsi `-c` atau `--count`.

### 4. Antarmuka Terminal Modern & Responsif
Ditenagai Rich Terminal UI dengan tabel konfigurasi visual, progress bar / spinner dinamis, notifikasi status berwarna, dan menu bantuan interaktif.

### 5. Fleksibel: CLI Runner & Modul Python
Dapat dijalankan langsung melalui double-click runner Windows (`run.bat`), baris perintah terminal (CLI), atau diimpor langsung ke skrip Python lain.

---

## ⚡ Instalasi Cepat Otomatis (1 Baris Perintah PowerShell)

Cukup buka terminal PowerShell di direktori mana pun yang Anda inginkan, lalu salin dan jalankan **1 baris perintah** berikut:

```powershell
irm https://raw.githubusercontent.com/ululazmi18/image-generator/main/install.ps1 | iex
```
> **Apa yang dilakukan skrip otomatis ini?**
> 1. Memeriksa ketersediaan **Python**, **Git**, dan **7-Zip** (otomatis memasangnya via winget jika belum ada).
> 2. Mengkloning repositori `image-generator`.
> 3. Memasang seluruh pustaka Python (`requirements.txt`).
> 4. Mengunduh dan mengonfigurasi **Firefox Portable** serta profil stealth anti-deteksi bot.
> 5. Membuka jendela login akun Google Flow sekali saja, dan generator langsung siap pakai!

---

## 🛠️ Panduan Instalasi Manual Langkah demi Langkah (Alternatif)

Jika Anda ingin menyiapkan lingkungan kerja secara bertahap secara manual:

### Langkah 1: Kloning Repositori Image Generator & Pasang Dependensi
Buka terminal PowerShell pada direktori kerja Anda (misal `C:\Users\...\Documents`), lalu kloning dan pasang dependensinya:
```powershell
# 1. Kloning repositori image-generator
git clone https://github.com/ululazmi18/image-generator.git

# 2. Masuk ke direktori image-generator
cd image-generator

# 3. Pasang dependensi pustaka Python
pip install -r requirements.txt
```

---

### Langkah 2: Kloning & Siapkan Peramban Firefox Stealth
Di dalam direktori `image-generator`, siapkan peramban mandiri anti-deteksi:
```powershell
# 1. Pasang 7-Zip jika belum terpasang (agar ekstraksi berjalan 100% senyap otomatis)
winget install 7zip.7zip

# 2. Kloning repositori browser stealth di dalam folder proyek
git clone https://github.com/ululazmi18/firefox-stealth-automation.git

# 3. Masuk ke direktori firefox-stealth-automation
cd firefox-stealth-automation

# 4. Pasang dependensi dan unduh Firefox Portable otomatis
pip install -r requirements.txt
python setup_browser.py
```
*Skrip ini secara otomatis mengunduh Firefox Portable Edition resmi serta mengonfigurasi profil `browser_profile` yang telah di-hardening anti-deteksi bot.*

---

### Langkah 3: Salin Folder Profil & Biner ke `image-generator`
Kembali ke folder utama `image-generator`, lalu salin folder profil dan biner Firefox yang telah siap pakai:
```powershell
# 1. Kembali ke direktori utama image-generator
cd ..

# 2. Salin folder profil browser yang telah dikonfigurasi
Copy-Item -Path ".\firefox-stealth-automation\browser_profile" -Destination ".\" -Recurse -Force

# 3. Salin folder biner Firefox Portable
Copy-Item -Path ".\firefox-stealth-automation\firefox_portable" -Destination ".\" -Recurse -Force
```
> **Proteksi Keamanan Akun:** Folder `browser_profile/` dan `firefox_portable/` sudah otomatis terdaftar di [`.gitignore`](.gitignore). Kredensial, cookies login, maupun file biner peramban tidak akan pernah terdorong (*pushed*) ke repositori publik GitHub.

*(Tips: Setelah disalin, Anda dapat menghapus folder `firefox-stealth-automation` untuk menghemat ruang penyimpanan jika diinginkan).*

---

### Langkah 4: Login Akun Google & Buka Google Flow (Hanya Sekali)
Cukup jalankan runner login yang telah disediakan:
```powershell
.\login.bat
```
*(Atau cukup **Klik Ganda / Double-Click** berkas `login.bat` di File Explorer).*

1. Pada jendela Firefox yang terbuka, kunjungi situs [Google Flow](https://flow.google.com).
2. Lakukan login menggunakan akun Google Anda dan pastikan antarmuka kanvas Google Flow telah siap digunakan.
3. Setelah login berhasil, **tutup jendela peramban Firefox tersebut** (agar sesi profil tersimpan dan file lock dilepas).

---

### Langkah 5: Menjalankan Image Generator (Siap Pakai!)
Kini `image-generator` telah memiliki peramban mandiri dan siap memproses prompt secara 100% senyap di latar belakang.

Pilih salah satu metode eksekusi berikut:

#### Metode A: Windows Batch Runner (`run.bat`)
Cara termudah bagi pengguna desktop Windows:
- **Klik Ganda (*Double Click*)** berkas [run.bat](run.bat), lalu ketik prompt saat diminta di terminal.
- Atau jalankan langsung via PowerShell dengan parameter bebas:
```powershell
.\run.bat -a 16:9 -m pro -p "mobil sport futuristik di tengah kota cyberpunk fajar"
```

---

#### Metode B: Baris Perintah Terminal (CLI Python)
Jalankan perintah `python image_generator.py` dengan fleksibilitas opsi penuh:

```powershell
# 1. Menampilkan Menu Bantuan Lengkap
python image_generator.py --help

# 2. Generasi Gambar Standar (Rasio 16:9, Model Pro)
python image_generator.py -p "kucing anggora bermain di taman sakura fajar"

# 3. Kustomisasi Aspek Rasio (16:9, 1:1, 9:16, 4:3, 3:4)
python image_generator.py -a 1:1 -p "secangkir kopi latte art bunga teratai"

# 4. Kustomisasi Model AI (pro, lite, 2.1)
python image_generator.py -m pro -a 16:9 -p "istana kristal megah di atas tebing salju"

# 5. Menghasilkan Beberapa Variasi Sekaligus (1 sampai 4 gambar)
python image_generator.py -c 2 -p "robot koki menyiapkan hidangan mewah"

# 6. Menentukan Folder atau Nama Berkas Tujuan (-o / --output)
python image_generator.py -o "outputs/mars.jpg" -p "astronot menjelajahi gua kristal merah"

# 7. Mode Audit Visual Screenshot (--debug)
python image_generator.py --debug -p "elang emas hinggap di dahan pohon pinus"
```

##### Tabel Opsi Parameter CLI

| Opsi Singkat | Opsi Panjang | Nilai Default | Penjelasan |
| :--- | :--- | :--- | :--- |
| `-p` | `--prompt` | *None* (Interaktif) | Teks prompt deskripsi gambar yang ingin dibuat |
| `-m` | `--model` | `pro` | Pilihan model AI: `pro`, `lite`, atau `2.1` |
| `-a` | `--aspect-ratio`| `16:9` | Format rasio: `16:9`, `4:3`, `1:1`, `3:4`, `9:16` |
| `-c` | `--count` | `1` | Jumlah variasi gambar yang dihasilkan (`1` s/d `4`) |
| `-o` | `--output` | `outputs/` | Direktori atau nama berkas tujuan penyimpanan |
| `-t` | `--timeout` | `180` | Batas waktu tunggu maksimal per percobaan (detik) |
| | `--debug` | `False` | Menyimpan screenshot setiap tahap ke folder `debug/` |
| `-h` | `--help` | | Menampilkan antarmuka panduan bantuan Rich |

---

#### Metode C: Modul Python (*Callable API*)

Dapat diintegrasikan langsung ke dalam pipeline atau aplikasi Python Anda:

```python
from image_generator import generate, generate_image

# -------------------------------------------------------------
# Cara 1: generate_image() — Mengembalikan path berkas lokal
# -------------------------------------------------------------
image_path = generate_image(
    prompt="pemandangan matahari terbenam sinematik di pantai tropis",
    aspect_ratio="16:9",
    model="pro",
    output_path="outputs/sunset.jpg"
)
print(f"Gambar berhasil disimpan di: {image_path}")

# -------------------------------------------------------------
# Cara 2: generate() — Mengembalikan objek GenerationResult
# -------------------------------------------------------------
result = generate(
    prompt="lukisan cat minyak burung merak bercahaya",
    aspect_ratio="1:1",
    model="pro",
    count=1
)

if result.success:
    print(f"Sukses ({result.duration_seconds:.1f}s): {result.image_path}")
    print(f"Model: {result.model_name} | Rasio: {result.aspect_ratio}")
else:
    print(f"Gagal: {result.error_message}")
```

---

## 📂 Struktur Berkas Proyek

```text
Image Generator/
├── debug/                      # Direktori dokumentasi saat mode --debug aktif
│   └── .gitkeep
├── outputs/                    # Direktori penyimpanan hasil gambar resolusi 1K
│   └── .gitkeep
├── image_generator.py          # Modul otomasi Python & CLI Generator Gambar
├── run.bat                     # Runner batch Windows (klik ganda atau CLI)
├── requirements.txt            # Dependensi pustaka minimal (rich, Pillow)
├── LICENSE                     # Lisensi open-source MIT
├── .gitignore                  # Proteksi berkas lokal, cache, & output
└── README.md                   # Panduan & dokumentasi resmi
```

---

## 📄 Lisensi

Proyek ini dirilis secara bebas dan terbuka di bawah lisensi [MIT License](LICENSE).
