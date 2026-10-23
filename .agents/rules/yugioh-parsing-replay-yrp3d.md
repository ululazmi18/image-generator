---
trigger: model_decision
description: Aktif saat mengekstrak replay MDPro3 (.yrp3d), parsing struktur biner duel, pemetaan offset memori, atau mengonversi replay menjadi alur kombo JSON.
---

# YU-GI-OH! MASTER DUEL — PARSING REPLAY MDPRO3 (.YRP3D)

Pedoman ini mengatur proses reverse engineering berkas replay MDPro3 (`.yrp3d`), pemetaan offset memori, dan alur integrasi hasil parsing ke struktur data proyek.

---

## 1. Struktur Biner & Pemetaan Memori `.yrp3d`
- **Player Metadata:** Player 0 (Pengguna) berada pada offset `0x80` (UTF-16LE, 40 byte); Player 1 (Lawan/Bot) pada offset `0x148` (UTF-16LE, 40 byte).
- **Extra Deck (15 Kartu):** Tersimpan dalam 15 blok terstruktur masing-masing 80 byte (0x50) mulai dari offset `0x0274` hingga `0x0724`. Passcode kartu 4-byte little-endian terletak pada offset blok `+0x13`.
- **Packet Stream & Zona:** Aliran event duel dimulai dari offset `0x0720` ke atas. Nilai lokasi mengikuti standar OCGCore:
  - `0x01` : `DECK` | `0x02` : `HAND` | `0x04` : `MZONE` | `0x08` : `SZONE`
  - `0x10` : `GRAVE` | `0x20` : `BANISH` | `0x40` : `EXTRA` | `0x80` : `OVERLAY`

---

## 2. Isolasi Turn 1 Pemain (User-Made Combo Line)
- Batasi ekstraksi langkah hanya pada pergerakan `Controller 0` (P0) sebelum aksi interaktif pertama lawan (`Controller 1`) di Main/Battle Phase giliran kedua.
- Ambil seluruh urutan aktivasi, pemanggilan material, cost discard/tribute, dan peletakan kartu di zona yang tepat.

---

## 3. Pemanfaatan Parser Otomatis Proyek
- Selalu gunakan skrip `scripts/parse_yrp3d.py` untuk mengekstrak dan membedah berkas `.yrp3d`:
  ```bash
  python scripts/parse_yrp3d.py "<path_to_replay.yrp3d>"
  ```

---

## 4. Alur Integrasi Otomatis ke Deck
- Buat berkas JSON kombo baru di `data/combos/<deck_id>/`.
- Daftarkan kombo ke `data/combos/registry.json`.
- Jalankan `python scripts/build_combo_registry.py` untuk mengompilasi aset ke `app/js/combo_registry.js`.
- Sinkronkan entri ke SQLite `data/master_duel.db` dan `data/master_duel_combos.json`.
