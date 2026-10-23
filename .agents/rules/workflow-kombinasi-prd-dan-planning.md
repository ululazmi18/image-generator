---
trigger: model_decision
description: Aktif saat memulai pembuatan aplikasi atau skrip baru dari nol, memandu alur Tiga Pilar Blueprint (PRD.md, DESIGN.md Anti-Slop, task.md) dan eksekusi koding inkremental agent.
---

# PROTOKOL KOMBINASI PRD PIPELINE & NATIVE AGENT PLANNING

Pedoman ini mengatur sinergi baku antara perencanaan produk (PRD Multi-Stage Pipeline), perancangan antarmuka Anti-Slop (DESIGN.md), dan eksekusi implementasi teknis (Native Agent Planning) setiap kali membangun aplikasi, modul, atau skrip baru.

---

## 1. Alur Dua Fase Terintegrasi (The Holy Trinity)

Setiap permintaan pembuatan aplikasi atau skrip baru dari nol wajib melewati dua fase terpadu:

### Fase A: Perancangan Produk & Blueprint Teknis (The Holy Trinity)
Sebelum menulis kode implementasi berkas, susun tiga pilar blueprint:
1. **Validasi Kebutuhan:** Jika ide masih singkat (< 3 kalimat) atau terdapat ambiguitas, lakukan sesi wawancara eksplorasi mendalam tanpa batas pertanyaan untuk memetakan seluruh parameter fungsional dan teknis secara komprehensif.
2. **`.agents/memory/PRD.md` (7 Bagian Kanonikal):** Susun ringkasan arsitektur (Overview, Requirements, Core Features MVP, User Flow, Architecture Mermaid, Database Schema, Constraints).
3. **`.agents/memory/DESIGN.md` (Kontrak Visual Anti-Slop):** Pilih 1 dari 19 Curated Foundations (Ramp, Raycast, Intercom, Railway, Attio, Cal.com, dsb.), tetapkan 18 CSS tokens, 4 Quality Gates (Hierarchy, Spacing, Type, States), dan aturan Anti-Slop (flat 1px borders, tabular-nums).
4. **`.agents/memory/task.md` (Dekomposisi Task Atomik):** Pecah fitur menjadi unit tugas koding terisolasi dengan prioritas terarah dan prompt siap-tempel. Seluruhnya tersimpan rapi di `.agents/memory/`.

### Fase B: Eksekusi Native Agentic Inkremental
Setelah blueprint disepakati:
1. **Frontend-First on Stub Data:** Bangun antarmuka pengguna (UI/CLI/TUI) menggunakan mock/dummy data terlebih dahulu agar visual dan interaksi dapat divalidasi langsung di browser atau terminal.
2. **Checkpoint Layer:** Lakukan verifikasi hasil layer antarmuka dan kesesuaian token `DESIGN.md` sebelum mengintegrasikan database atau logika backend yang rumit.
3. **Backend & Persistence Wiring:** Sambungkan ke database, API nyata, atau integrasi pihak ketiga secara inkremental.
4. **Verifikasi Runtime:** Jalankan build, lint, dan uji fungsional lokal bebas galat (zero-error).

---

## 2. Prinsip Anti-Bloat & Kualitas Kode
- **Single-Task Focus:** Kerjakan satu tugas per satu secara terisolasi untuk menjaga ketajaman konteks token.
- **Kedaulatan Lokal:** Seluruh pengujian dan git commit dilakukan secara lokal (`feat(scope): deskripsi`).
