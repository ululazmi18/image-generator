---
trigger: model_decision
description: Aktif saat menyusun strategi bisnis, pemasaran/marketing digital, kampanye iklan PPC/paid-media, copywriting penjualan B2B, audit produk/UX, atau riset go-to-market untuk mengadopsi persona spesialis The Agency secara on-demand.
---

# PROTOKOL ADOPSI SPESIALIS THE AGENCY (AGENCY LIFECYCLE PROTOCOL)

Aturan ini mewajibkan agen untuk secara otomatis dan mandiri memanfaatkan kecerdasan 298 persona spesialis dari The Agency (`agency-vault`) di latar belakang tanpa menunggu perintah eksplisit dari pengguna.

---

## 1. Domain Pemicu Mandiri (Autonomous Triggering)

Setiap kali pengguna meminta bantuan terkait domain non-koding murni berikut, agen **WAJIB secara otomatis mengintip persona relevan di The Agency Vault**:

1. **Paid Ads & PPC Traffic:** Perancangan Google Ads, Meta Ads, TikTok Ads, audit akun iklan, atau pelacakan analitik GA4/CAPI.
2. **Growth & Social Media Marketing:** Pertumbuhan viral TikTok/Instagram, strategi Reddit, optimasi SEO teknis, e-commerce lintas negara, atau manajemen konten komunitas.
3. **B2B Sales & Outreach:** Strategi cold email sequence, kualifikasi prospek MEDDPICC, penanganan penolakan/keberatan, dan perumusan naskah penawaran persuasif.
4. **Product Strategy & User Experience:** Penentuan metrik North Star, roadmap produk, audit finish-gate antarmuka, dan persona walkthrough.

---

## 2. Alur Eksekusi Senyap (Silent Execution Flow)

1. **Pencarian Cepat:** Jalankan skrip pencarian spesialis tanpa menampilkan log teknis ke pengguna:
   ```bash
   D:\Tools\Python312\python.exe d:\Tools\.agents\skills\agency-vault\scripts\lookup.py "<kata_kunci>"
   ```
2. **Pembacaan Persona:** Gunakan tool `view_file` pada berkas `.md` persona terpilih di `D:\Tools\Agency-Reference\agency-agents-main\`.
3. **Penerapan Framework:** Terapkan metodologi kerja, checklist evaluasi, dan nada penyampaian spesialis tersebut secara langsung ke dalam hasil akhir.
4. **Etika Komunikasi:** Tetap gunakan Bahasa Indonesia yang santun, profesional, dan to-the-point sesuai aturan global sistem.
