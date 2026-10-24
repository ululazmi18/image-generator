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

## 🚀 Panduan Penggunaan

### 1. Instalasi Dependensi
Cukup pasang dua pustaka pendukung minimal:
```powershell
pip install -r requirements.txt
```

---

### 2. Metode Runner Windows (`run.bat`)
Cara termudah bagi pengguna Windows desktop:
- **Klik Ganda (*Double Click*)** berkas [run.bat](file:///d:/Documents/Image%20Generator/run.bat).
- Masukkan teks prompt ketika diminta pada tampilan terminal.
- Gambar akan otomatis diproses di latar belakang dan disimpan ke folder `outputs/`.

Atau jalankan via PowerShell / Command Prompt dengan argumen langsung:
```powershell
.\run.bat -p "mobil sport futuristik di tengah kota cyberpunk fajar" -a 16:9 -m pro
```

---

### 3. Metode Baris Perintah Terminal (CLI)

Jalankan perintah `python image_generator.py` dengan fleksibilitas opsi penuh:

```powershell
# 1. Menampilkan Menu Bantuan Lengkap
python image_generator.py --help

# 2. Generasi Gambar Standar (Rasio 16:9, Model Pro)
python image_generator.py -p "kucing anggora bermain di taman sakura fajar"

# 3. Kustomisasi Aspek Rasio (16:9, 1:1, 9:16, 4:3, 3:4)
python image_generator.py -p "secangkir kopi latte art bunga teratai" -a 1:1

# 4. Kustomisasi Model AI (pro, lite, 2.1)
python image_generator.py -p "istana kristal megah di atas tebing salju" -m pro

# 5. Menghasilkan Beberapa Variasi Sekaligus (1 sampai 4 gambar)
python image_generator.py -p "robot koki menyiapkan hidangan mewah" -c 2

# 6. Menentukan Folder atau Nama Berkas Tujuan (-o / --output)
python image_generator.py -p "astronot menjelajahi gua kristal merah" -o "outputs/mars.jpg"

# 7. Mode Audit Visual (--debug)
python image_generator.py -p "elang emas hinggap di dahan pohon pinus" --debug
```

#### Tabel Opsi Parameter CLI

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

### 4. Metode Modul Python (*Callable API*)

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

Proyek ini dirilis secara bebas dan terbuka di bawah lisensi [MIT License](file:///d:/Documents/Image%20Generator/LICENSE).
