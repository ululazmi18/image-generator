---
trigger: model_decision
description: Aktif saat memformat visualisasi papan duel Yu-Gi-Oh (playmat layout, zona EMZ/MMZ/STZ/FSZ), panel Extra Deck/GY/Banish, atau thumbnail kartu CDN.
---

# YU-GI-OH! MASTER DUEL — STANDAR VISUAL PAPAN DUEL (PLAYMAT LAYOUT)

Pedoman ini mengatur format visualisasi papan duel dalam dokumen kombo, termasuk tata letak playmat, panel zona, dan penggunaan thumbnail kartu.

---

## 1. Tabel Visual Kartu Utama
- Menampilkan gambar *thumbnail* kartu asli (CDN YGOPRODeck), aksi/peran, cost material, dan hasil pemanggilan.

---

## 2. Arsitektur Tata Letak Playmat (3-Flank System)

### A. Sayap Kiri (Left Flank) — Panel Visual Extra Deck
- Wajib berupa panel galeri visual langsung yang menampilkan kartu-kartu yang tersisa di Extra Deck secara dinamis real-time (`zone-card-strip` dengan thumbnail, counter badge, dan efek hover interaktif).

### B. Arena Tengah (Center Arena)
1. **Field Spell Zone (FSZ):** Terletak di sisi kiri sejajar baris MMZ/STZ. Jika Field Spell aktif, wajib menampilkan visual gambar kartu asli.
2. **Extra Monster Zone (EMZ 1 & EMZ 2):** Baris paling atas arena tengah.
3. **Main Monster Zone (MMZ 1 – MMZ 5):** Baris tengah arena utama.
4. **Spell & Trap Zone (STZ 1 – STZ 5):** Baris paling bawah arena utama dengan visual kartu asli.

### C. Sayap Kanan (Right Flank) — Panel Banish & GY
1. **Zona Banish (Banished):** Posisi paling atas, lengkap dengan counter badge dan thumbnail kartu terbanish.
2. **Graveyard (GY):** Posisi tepat di bawah Zona Banish, lengkap dengan counter badge dan thumbnail seluruh kartu di GY.

---

## 3. Standar Kunci Zona Board State
- Extra Monster Zone: `emz1` (kiri) dan `emz2` (kanan).
- Main Monster Zone: `mmz1` s/d `mmz5`.
- Spell & Trap Zone: `stz1` s/d `stz5`.
- Field Spell Zone: `fld`.

---

## 4. Status Lapangan Lengkap Per Langkah (Full Real-Time Board State)
- **Extra Deck (ED):** Jumlah total dan thumbnail kartu yang masih tersisa.
- **EMZ (Kiri & Kanan):** Status kedua slot beserta kartu aktif.
- **MMZ (Slot 1–5):** Posisi monster termasuk unit material Xyz.
- **STZ (Slot 1–5 & FSZ):** Status Backrow dan Field Spell dengan orientasi (*face-up* / *Set*).
- **Hand:** Jumlah dan nama kartu spesifik yang tersisa di tangan.
- **GY:** Jumlah total dan thumbnail seluruh kartu di Graveyard.
- **Banish:** Jumlah total dan thumbnail seluruh kartu yang ter-banish.

---

## 5. Larangan Bilah Teks Redundan
- Dilarang menggunakan bilah info teks terpisah di bagian bawah papan (`boardDetailsBar`); seluruh status kartu wajib terintegrasi langsung ke dalam struktur playmat visual.
- Dilarang menyertakan bagian *"Bukti Verifikasi Duel"* untuk kombo umum. Dokumentasi kombo wajib murni berfokus pada alur strategi teknis.
