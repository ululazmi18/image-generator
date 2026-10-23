---
trigger: model_decision
description: Aktif saat merancang, memoles, atau membangun antarmuka UI/Frontend/TUI, menegakkan standar Anti-Slop (DESIGN.md), 18 CSS token, 4 quality gates, dan larangan gradien/bayangan kotor.
---

# STANDAR VISUAL DESIGN & ANTI-SLOP CONTRACT

Pedoman ini menetapkan tata kelola baku kualitas visual (Anti-Slop Craft) untuk seluruh perancangan antarmuka (Web, Mobile, Desktop, TUI/CLI) agar tidak terlihat generik, murahan, atau seperti buatan AI ceroboh (*AI Slop*).

---

## 1. Dokumen Kontrak Visual (`DESIGN.md`)
- Setiap proyek antarmuka wajib merujuk pada `DESIGN.md` yang menetapkan pilihan fondasi terkurasi (misal: Ramp, Raycast, Intercom, Railway, Cal.com) dan 18 token CSS baku (`--bg`, `--surface`, `--line`, `--ink`, `--muted`, `--accent`, `--radius`, `--font-display`, `--font-body`, dsb.).
- Dilarang menggunakan nilai warna atau ukuran ad-hoc (*magic numbers*) di luar token yang telah disepakati.

---

## 2. Empat Quality Gates Anti-Slop
1. **Hierarchy (Hierarki Visual):** Tepat 1 visual focal point per layar. Kontras ketat antara background kanvas, card surface, dan interactive control.
2. **Spacing (Ritme Ruang):** Wajib menggunakan skala kelipatan 4px/8px secara konsisten. Dilarang margin acak. Padding tombol dan kontrol form wajib simetris.
3. **Type (Tipografi Terstruktur):** Maksimal 2 keluarga font (Display + Sans serbaguna). Wajib menerapkan `tabular-nums` pada setiap data angka, jam, persentase, dan metrik finansial. Judul wajib menggunakan `text-balance`.
4. **States (Kelengkapan Status):** Setiap elemen interaktif wajib mendefinisikan 5 state: `default`, `hover`, `active/focus-visible`, `disabled`, dan `empty/loading`.

---

## 3. Larangan Mutlak AI Slop (Zero-Slop Policy)
- **Anti-Ornamental Gradients:** Dilarang memasang gradien ungu/violet melayang tanpa fungsi struktural.
- **Flat 1px Chrome:** Gantikan bayangan tebal multi-lapis (*dirty drop-shadows*) dengan garis tepi solid 1px tipis (`border: 1px solid var(--line)`).
- **Semantik Aksen:** Warna aksen hanya digunakan untuk aksi primer dan indikator status aktif, bukan latar belakang elemen umum.
- **State Kosong Bermakna:** Dilarang membiarkan tampilan tabel atau daftar kosong tanpa ilustrasi status atau instruksi pengisian awal (*empty state*).
