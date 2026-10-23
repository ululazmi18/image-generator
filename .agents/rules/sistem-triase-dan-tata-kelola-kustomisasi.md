---
trigger: model_decision
description: Aktif saat menganalisis permintaan pembuatan rule, instalasi MCP, penambahan skill, atau menentukan penempatan kustomisasi agar token tetap optimal.
---

# SISTEM TRIASE PENEMPATAN KUSTOMISASI (RULES VS SKILL VS MCP)

Pedoman ini mengatur kewajiban agen untuk menganalisis, memeriksa, dan menentukan wadah penempatan yang paling optimal (Rule, Skill, atau MCP) pada setiap instruksi baru agar konsumsi token tetap ramping.

---

## 1. Mandat Triase Otomatis & Anti-Salah Kamar
Ketika pengguna memberikan instruksi (misal: "buatkan rule...", "terapkan mcp...", "tambahkan alat..."), agen **dilarang menuruti wadah yang disebutkan secara mentah-mentah jika terbukti tidak optimal bagi token**. 
Agen wajib melakukan evaluasi karakteristik:

1. **Apakah ini Batasan Perilaku / Policy / Guardrail?**
   - **Wadah: RULE (`.agents/rules/` & `D:\.agents\rules/`)**
   - Contoh: Standar git lokal, pencegahan kebocoran env, etika bahasa, hirarki prioritas tool.
2. **Apakah ini Prosedur / Runbook / Langkah Kerja / Formula / Tool Periodik?**
   - **Wadah: SKILL ON-DEMAND (`skills/<name>/SKILL.md`)**
   - Contoh: Ekstraksi dokumen, formula prompt generative art, parsing format data tertentu, API sesekali (suara, video, crawling).
   - Manfaat: Memanfaatkan *Progressive Disclosure* (~0 token saat tidur).
3. **Apakah ini Layanan Dua Arah Real-Time Berfrekuensi Tinggi?**
   - **Wadah: SERVER MCP (`mcp_config.json`)**
   - Contoh: Validasi docs real-time (`context7`), standar craft desain (`ui-skills`).
   - Syarat: Hanya jika tool tersebut mutlak dipanggil terus-menerus selama menulis kode.

---

## 2. Protokol Respon Terhadap Pengguna
Jika ada penyesuaian wadah (misalnya pengguna meminta "buatkan rule untuk cara ekstrak ZIP", tetapi agen menempatkannya sebagai Skill On-Demand), agen wajib:
1. Langsung mengeksekusi penempatan di wadah yang benar (Skill).
2. Menginformasikan secara singkat dan santun bahwa materi tersebut ditempatkan sebagai Skill agar token percakapan tetap optimal dan tidak membebani giliran chat lainnya.
