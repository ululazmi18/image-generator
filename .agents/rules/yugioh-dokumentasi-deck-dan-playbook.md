---
trigger: model_decision
description: Aktif saat menyusun panduan deck Yu-Gi-Oh, dokumentasi arketipe, analisis variasi decklist, playbook kombo step-by-step, atau analisis matchup dan choke point.
---

# YU-GI-OH! MASTER DUEL — DOKUMENTASI DECK & PLAYBOOK KOMBO

Pedoman ini mengatur spesifikasi standar dokumentasi deck, panduan arketipe, variasi decklist, alur kombo step-by-step, dan analisis matchup.

---

## 1. Empat Pilar Dokumentasi Deck

### A. Kartu Pembuka (Starters & Evaluasi Probabilitas)
1. **1-Card Starters:** Kartu pembuka tunggal yang mampu menghasilkan full board secara mandiri.
2. **2-Card Starters / Extenders:** Kombinasi kartu pembuka sekunder yang tahan interupsi atau rute alternatif ketika kartu utama terkena counter.

### B. Papan Akhir (End Board Breakdown)
- Menguraikan seluruh monster negasi di field, kartu gangguan di Backrow, kartu di Graveyard yang memiliki efek aktif di giliran lawan, serta potensi gangguan di tangan.

### C. Alur Langkah demi Langkah (Step-by-Step Playbook)
- Penulisan langkah berurutan (*play-by-play*) dengan format bernomor yang jelas.
- Menyebutkan zona aktivasi (Hand, Field, GY, Banishment), cost pembayaran, target aktivasi, dan rantai chain (*Chain Link 1, 2, dst.*).

### D. Titik Lemah & Mitigasi Interupsi (Choke Points & Hand Trap Counters)
- Wajib mencantumkan secara spesifik titik rawan kombo terhadap hand trap utama (*Ash Blossom, Nibiru, Infinite Impermanence, Droll & Lock Bird, Maxx "C"*).
- Menjelaskan rute alternatif (*pivot line*) jika kartu utama terkena interupsi pada choke point tersebut.

---

## 2. Struktur Direktori Modul Arketipe
- Disimpan di folder khusus lowercase: `<nama_archetype>/`
- Berkas standar yang wajib ada:
  - `README.md` : Pengenalan, lore, mekanik dasar, dan direktori panduan.
  - `CARDS_CATALOG.md` : Katalog tabel kartu lengkap (nama, tipe, rarity MD, banlist, peran taktis).
  - `VARIANTS.md` : Analisis variasi kombinasi deck (decklist 40-42 kartu Main Deck & 15 Extra Deck).
  - `COMBOS_PLAYBOOK.md` : Panduan taktis kombo step-by-step.
  - `MATCHUPS_AND_CHOKEPOINTS.md` : Analisis cara mengalahkan deck meta lain dan cara meng-counter deck ini.

---

## 3. Direktori Global Proyek
- `data/master_duel.db` : Database SQLite terindeks (tabel `cards`, `banlist`, `combos`, dan FTS5).
- `data/master_duel_cards.json` : Arsip mentah seluruh kartu Master Duel.
- `data/master_duel_banlist.json` : Arsip status limit regulation aktif.
- `data/master_duel_combos.json` : Arsip JSON seluruh alur kombo.
- `catalogs/` : Katalog global (*BANLIST.md*, *STAPLES_AND_HANDTRAPS.md*, *ARCHETYPES_DIRECTORY.md*).

---

## 4. Sinkronisasi Database & Memori Otomatis
Setelah setiap pembuatan, pembaruan data kartu, atau penambahan variasi kombo baru:
1. **Sinkronisasi SQLite:** Masukkan atau perbarui entri baru ke tabel `combos` atau `cards` di `data/master_duel.db`.
2. **Sinkronisasi JSON:** Ekspor ulang dan simpan pembaruan ke `data/master_duel_combos.json`.
3. **Pembaruan Tautan Navigasi:** Tambahkan tautan dokumen baru ke `INDEX.md` dan `README.md`.
4. **Local Git Commit:** Lakukan atomic commit lokal dengan pesan terstruktur `feat: ...` atau `fix: ...` tanpa menjalankan remote push.
