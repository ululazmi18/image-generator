---
trigger: model_decision
description: Aktif saat menulis implementasi kode baru, mencegah over-engineering, menolak spekulasi fitur/konfigurasi yang tidak diminta, dan menegakkan solusi minimalis sederhana.
---

# STANDAR MINIMALISME KODE (ANTI-OVERENGINEERING)

Pedoman ini menegakkan prinsip *Simplicity First* ala Andrej Karpathy untuk mencegah kode membengkak dan spekulatif.

---

## 1. Solusi Minimalis & Bebas Spekulasi
- Tulis kode seminimal mungkin yang menyelesaikan masalah secara tuntas.
- **Dilarang menambahkan fitur** di luar apa yang secara eksplisit diminta oleh pengguna.
- **Dilarang membuat abstraksi berlebih** (kelas generic, interfaces, factories, helper kompleks) untuk kode yang hanya digunakan satu kali (*single-use*).
- **Dilarang menambahkan opsi fleksibilitas atau konfigurabilitas** spekulatif yang tidak dibutuhkan saat ini.

---

## 2. Penanganan Galat Proporsional
- Jangan membuat penanganan galat (*error handling*) berlebihan untuk skenario yang secara teknis mustahil terjadi.
- Fokuskan penanganan galat pada titik-titik rentan yang realistis (I/O, jaringan, input pengguna, parsing data eksternal).

---

## 3. Uji Kesederhanaan
- Tanyakan pada diri sendiri: *"Apakah engineer senior akan menganggap implementasi ini terlalu rumit?"* Jika ya, sederhanakan.
- Jika suatu solusi dapat ditulis secara bersih dan mudah dipahami dalam 50 baris, **dilarang menulisnya menjadi 200 baris**.
