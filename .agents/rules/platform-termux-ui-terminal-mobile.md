---
trigger: model_decision
description: Aktif saat mendesain tampilan terminal untuk ponsel Termux (60-80 kolom), mengatur tabel Rich responsif, atau membersihkan layar secara portabel.
---

# STANDAR ANTARMUKA TERMINAL PONSEL TERMUX (MOBILE CONSOLE UI)

Pedoman ini mengatur desain UI terminal yang responsif untuk layar ponsel Android sempit, tata letak tabel `Rich`, dan pembersihan layar portabel lintas-platform.

---

## 1. Ukuran Layar Standar Ponsel
- Asumsikan lebar terminal pengguna ponsel Android berkisar antara **60 hingga 80 kolom** (mode potret).
- Gunakan `shutil.get_terminal_size((80, 24))` secara dinamis untuk mendeteksi ukuran aktual.

---

## 2. Desain UI Responsif
- Jika lebar layar < 85 karakter, panel status horizontal panjang wajib otomatis dipecah menjadi susunan multi-baris ringkas (*stacked compact layout*) untuk mencegah teks meluber atau terpotong.
- Kolom tabel `Rich` harus menggunakan batasan lebar yang fleksibel (`max_width` terkontrol) agar tidak memicu pembungkus baris (*horizontal line wrapping*) yang merusak tampilan.

---

## 3. Pembersihan Layar Bebas Galat
- **Dilarang keras** menggunakan `os.system("cls")`.
- Wajib menggunakan `console.clear()` dari pustaka `rich`, atau perintah portabel `os.system("clear" if os.name != "nt" else "cls")`.
