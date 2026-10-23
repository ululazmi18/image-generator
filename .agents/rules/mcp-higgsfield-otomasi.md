---
trigger: model_decision
description: Aktif saat pembuatan video iklan, video AI sinematik, UGC unboxing, translasi ad localizer, atau alur kerja Higgsfield on-demand.
---

# PANDUAN PENGGUNAAN HIGGSFIELD ON-DEMAND

Aturan ini mengatur standar operasional, efisiensi kredit, dan alur kerja pembuatan aset video menggunakan Higgsfield secara on-demand via skill `ai-video-gen`.

---

## 1. Identifikasi & Akses Layanan
- **Metode Eksekusi:** Dijalankan secara on-demand melalui skill `ai-video-gen` (tanpa server MCP standby).
- **Cakupan Kapabilitas:** Generasi video sinematik, format iklan/UGC, translasi ad localizer, dan rasio aspek multi-platform.

---

## 2. Kepatuhan Kebijakan Zero-Cost (Kredit Mandatori)
- **Larangan Pemotongan Saldo Berbayar:** Dilarang mengeksekusi generasi jika memotong kuota kredit reguler pengguna tanpa izin tertulis eksplisit.
- **Jalur Utama Harian:** Selalu gunakan sintesis bebas biaya atau rakit sekuens visual via Python + FFmpeg lokal.

---

## 3. Standar Rasio Aspek & Prompting Kamera
- Format vertikal (`9:16`): TikTok, Reels, Shorts. Format lanskap (`16:9`): YouTube, sinematik.
- Sertakan arah kamera eksplisit dalam bahasa Inggris (*dolly zoom, aerial drone, slow push-in*) dan pencahayaan (*golden hour, cinematic lighting*).
