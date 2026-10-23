---
trigger: model_decision
description: Aktif saat membuat halaman antarmuka web/frontend, komponen visual, tata letak terminal CLI/TUI, integrasi aset gambar, atau pengujian tampilan antarmuka pengguna.
---

# ALUR PERANCANGAN UI / FRONTEND & TERMINAL UI (VISUAL & UI PROTOCOL)

Pedoman ini mengatur tahapan pembuatan antarmuka web, tata letak mobile, tata letak terminal CLI/TUI, dan integrasi aset visual nyata.

---

## Tahap Pelaksanaan UI & Visual

1. **Tahap 1 (Perancangan Komponen & Penarikan UI Skills):**
   - Wajib memanggil MCP `ui-skills` secara mandiri untuk mengambil panduan desain terkait (`baseline-ui`, `fixing-accessibility`, `fixing-motion-performance`, dsb.).
   - Pecah antarmuka atau tata letak TUI menjadi komponen-komponen modular yang terstruktur dan ergonomis.

2. **Tahap 2 (Penyelarasan Warna, Ikon & Emoji):**
   - Terapkan palet warna harmonis (*semantic color tokens*) dengan kontras tinggi sesuai standar WCAG 2.2.
   - Pilih ikon semantik yang sesuai konteks dan atur penempatan emoji secara proporsional (*anti-emoji slop*).

3. **Tahap 3 (Aksesibilitas, Tipografi & Motion):**
   - Terapkan aksesibilitas ramah keyboard/screen-reader, animasi ringan berbasis GPU compositor $\le 200\text{ ms}$, dan tipografi seimbang (`text-balance`, `tabular-nums`).
   - Manfaatkan `generate_image` secara proaktif jika memerlukan gambar nyata (dilarang *placeholder* kosong).

4. **Tahap 4 (Verifikasi Visual & Commit):**
   - Validasi tampilan visual antarmuka atau keterbacaan layout CLI/TUI, lalu buat commit lokal `feat(ui): <nama_komponen>`.
