---
trigger: model_decision
description: Aktif saat memilih tool generasi multimedia AI, sintesis video, gambar, audio, atau pencegahan konsumsi kuota/kredit berbayar (kebijakan zero-cost unlimited).
---

# KEBIJAKAN ZERO-COST & JALUR GENERASI FULL-FREE UNLIMITED

Aturan ini bersifat mutlak untuk memastikan seluruh generasi multimedia (video, gambar, audio) beroperasi pada jalur 100% gratis (*zero-cost*) dan tanpa batasan kuota berbayar (*unlimited*).

---

## 1. Mandat Mutlak Zero-Cost & Anti-Pemotongan Kredit
- **Dilarang Keras Memotong Saldo/Kredit Berbayar:** Agen dilarang memanggil endpoint atau tool berbayar (seperti generasi Higgsfield berbayar, Runway berbayar, dll.) yang menghabiskan saldo kredit akun pengguna tanpa instruksi tertulis eksplisit.
- **Prinsip Operasional Bebas Biaya:** Seluruh kebutuhan aset visual, animasi, suara, dan video wajib dialihkan ke ekosistem yang terverifikasi *full-free* dan *unlimited*.

---

## 2. Peta Jalur Generasi Full-Free & Unlimited Terpilih

| Kebutuhan Aset | Jalur Utama (Full Free & Unlimited) | Jalur Alternatif Bebas Biaya |
| :--- | :--- | :--- |
| **Generasi Video AI** | **`pollinations.generateVideo`** (Generasi video AI tanpa kuota kredit) | Perakitan sekuens gambar ke video secara lokal via **Python + FFmpeg** |
| **Generasi Gambar AI** | **Native `generate_image`** (Model Imagen bawaan IDE, tanpa kuota) | **`pollinations.generateImage`** (Pilihan model beragam tanpa API key berbayar) |
| **Generasi Audio & TTS** | **`pollinations.generateAudio`** (Sintesis suara bebas biaya) | TTS lokal (Python `pyttsx3` / `gTTS` / model offline) |
| **Transkripsi Suara** | **`pollinations.transcribeAudio`** | Model lokal Whisper |
| **Editing & Pascaproduksi** | **FFmpeg & Skrip Python Lokal** (Rendering, cut, kompresi, overlay teks) | Otomasi shell lokal tanpa batas |

---

## 3. Tata Kelola Tool Berbayar / Berbasis Kredit (Higgsfield / Runway)
- Perlakukan Higgsfield dan Runway sebagai alat sekunder/cadangan khusus.
- **Hanya boleh dieksekusi jika:**
  1. Pengguna sedang mengaktifkan masa promo/trial 100% *free unlimited* yang terkonfirmasi aktif tanpa memotong saldo berbayar; ATAU
  2. Pengguna memberikan perintah tertulis eksplisit yang secara sadar mengizinkan pemotongan kredit berbayar.
- Di luar dua kondisi di atas, agen **wajib secara otomatis menggunakan jalur `pollinations` dan `generate_image`**.
