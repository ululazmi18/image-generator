---
trigger: model_decision
description: Aktif saat memilih tool untuk eksekusi tugas, membaca berkas, scraping, otomasi browser, atau mengoptimalkan konsumsi token antara fitur natif vs MCP.
---

# PROTOKOL OPTIMASI TOKEN: HIRARKI NATIF VS SERVER MCP

Pedoman ini mengatur strategi pemilihan alat untuk mencapai efisiensi token maksimal tanpa mengurangi akurasi hasil kerja.

---

## 1. Hirarki Mutlak: Natif-First untuk Operasi Inti

Demi mencegah pembengkakan konteks (*context bloat*), agen wajib memprioritaskan alat natif untuk operasi harian:

1. **Terminal & Eksekusi Perintah:**
   - Wajib gunakan natif `run_command` + `manage_task`.
   - Hindari alur terminal multi-turn yang membutuhkan polling berulang dan memboroskan token.
2. **Otomasi Browser & Frontend Testing:**
   - Wajib utamakan natif `browser_subagent`.
   - Alasan: Sub-agen mengisolasi DOM dan interaksi di thread terpisah, sehingga tidak membanjiri jendela chat utama dengan snapshot DOM ribuan token.
3. **Membaca Web & Dokumentasi URL:**
   - Wajib gunakan natif `read_url_content` (otomatis konversi HTML ke Markdown tanpa biaya skema).
   - Gunakan `firecrawl` hanya jika memerlukan perayapan rekursif mendalam (*deep multi-page crawling*) pada satu domain utuh.
4. **Navigasi & Pencarian Kode:**
   - Wajib gunakan `grep_search` terarah dan pemotongan baris `view_file` (dengan `StartLine` dan `EndLine`).
   - Dilarang memuat seluruh file besar sekaligus jika hanya butuh memeriksa blok kode tertentu.
5. **Database Lokal (SQLite):**
   - Gunakan skrip Python atau CLI lokal via `run_command` dengan klausa `LIMIT` ketat alih-alih me-dump tabel secara massal.

---

## 2. Hirarki Mutlak: MCP & Skill On-Demand untuk Tugas Spesialis

Manfaatkan MCP dan Skill khusus untuk area yang tidak dapat ditandingi oleh alat natif:

1. **Dokumen Office & Dokumen Biner (PDF, Word, Excel, PPTX):**
   - Wajib gunakan skill on-demand `markitdown` via `uvx`.
   - Mengubah dokumen biner menjadi teks Markdown lokal, menghemat 70%–90%+ token dibandingkan multimodal vision.
2. **Validasi Pustaka & Dokumentasi Mutakhir:**
   - Wajib gunakan `context7` dan `gemini-api-docs` untuk menarik referensi API resmi yang ringkas, mencegah halusinasi sintaks dan revisi kode yang boros token.
3. **Standarisasi Antarmuka & UX:**
   - Panggil `ui-skills` secara granular (`get_skill`) saat merancang tata letak dan palet warna.
4. **Multimedia Generatif AI (Audio & Video):**
   - Gunakan jalur zero-cost `pollinations` sebagai pilihan utama, serta `ElevenLabs` / `Runway` / `Higgsfield` untuk kebutuhan audio/video sinematik spesifik.
