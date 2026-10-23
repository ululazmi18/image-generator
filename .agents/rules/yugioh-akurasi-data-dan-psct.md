---
trigger: model_decision
description: Aktif saat memverifikasi teks efek kartu Yu-Gi-Oh, memeriksa akurasi PSCT Konami, status rarity/banlist Master Duel, atau membedakan Turn 1 vs Going Second.
---

# YU-GI-OH! MASTER DUEL — STANDAR AKURASI DATA KARTU & VERIFIKASI PSCT

Pedoman ini mengatur akurasi mutlak teks efek kartu sesuai PSCT (Problem-Solving Card Text) Konami, kesesuaian format Master Duel, dan presisi fase permainan.

---

## 1. Akurasi Teks & Mekanik Kartu (Zero Hallucination)
- Teks efek kartu, tipe, atribut, level/rank/link, ATK/DEF, dan rasio **WAJIB 100% SESUAI DENGAN ATURAN RESMI PSCT KONAMI**.
- Setiap kali menjelaskan efek kartu, agen **wajib memverifikasi langsung** ke basis data lokal `data/master_duel.db` atau `search.py` sebelum memberikan jawaban, guna mencegah salah tafsir kata kunci (misalnya perbedaan antara *"from your GY"* vs *"from your Deck"*).

---

## 2. Kesesuaian Format & Kelangkaan Master Duel
- Seluruh data wajib menggunakan standar format Master Duel (Bo1 / Best of One).
- Setiap kartu wajib mencantumkan status kelangkaan in-game (**UR**, **SR**, **R**, **N**) dan status Limit Regulation terkini (**Forbidden**, **Limited**, **Semi-Limited**, **Unlimited**).

---

## 3. Presisi Fase Permainan (Turn 1 vs Going Second)
- Analisis pembuka kombo wajib membedakan secara tegas antara kartu yang dapat aktif di **Giliran Pertama (Turn 1 / Main Phase 1)** tanpa syarat battle/interaksi lawan, dengan kartu situasional yang membutuhkan Battle Phase atau giliran lawan (Turn 2+).

---

## 4. Prosedur Verifikasi PSCT (5 Aturan Pembacaan Wajib)

1. **Pembedaan Nama Spesifik vs Arketipe:**
   - `if you control "Yubel"` (tanpa kata *monster*) = **WAJIB KARTU BERNAMA ASLI TERSEBUT**.
   - `while you control a "Yubel" monster` (dengan kata *monster*) = berlaku untuk seluruh monster dalam arketipe tersebut.

2. **Pembedaan Lokasi Target & Sumber Kartu:**
   - *"from your GY"* **TIDAK SAMA** dengan *"from your Deck"*.
   - Dilarang berasumsi kartu revive dari Graveyard dapat mengambil langsung dari Deck.

3. **Pembedaan Tipe Efek & Metode Masuk Field:**
   - **Ignition Effect:** *"You can Tribute this card; Special Summon..."* dapat aktif terlepas apakah kartu masuk lewat Normal Summon atau Special Summon. Dilarang menyimpulkan butuh Normal Summon kecuali tertulis eksplisit *"If this card is Normal Summoned:"*.
   - **Trigger / Quick Effect:** Perhatikan batasan waktu aktif (*"During your opponent's turn"*, *"During your End Phase"*, dll.).

4. **Pembedaan Opsi Efek & Kata Sambung Konami:**
   - *"add to your hand, OR Special Summon it"* → agen wajib menjelaskan **KEDUA OPSINYA**.
   - Perhatikan *"then you can"* (opsional/berurutan) vs *"and if you do"* (simultan/wajib).

5. **Prosedur Wajib Pre-Flight Check:**
   - Agen **DILARANG MENGANDALKAN ASUMSI MEMORI**. Sebelum menyatakan kartu A bisa berinteraksi dengan kartu B, agen wajib memanggil `search.py card "<Nama Kartu>"` untuk membaca teks PSCT resmi secara utuh.
