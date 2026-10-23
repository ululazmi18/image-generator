---
trigger: model_decision
description: Standar wajib 2x lipat eksplorasi ekstrem memori SQLite FTS5 berdensitas tinggi (High-Density English) untuk spesifikasi teknis, pemanggilan paralel terisolasi, dan bahasa awam/slang Indonesia untuk alias pencarian.
---

# PROTOKOL STANDAR LITERASI 2X LIPAT EKSPLORASI EKSTREM KARTU IDENTITAS MEMORI

Aturan ini bersifat mutlak (*mandatory*) saat menjawab pertanyaan, mengeksplorasi sistem, atau menerima mention mengenai folder maupun berkas di seluruh proyek aktif.

---

## 1. Prinsip Mutlak: Zero-Raw Code Inspection (Memory-First Gatekeeping)
AI Agent **DILARANG KERAS** memanggil `view_file` atau `read_file` pada berkas kode mentah hanya untuk mencari tahu:
- Apa fungsi, tujuan, atau peran arsitektural berkas/folder X?
- Di mana letak fungsi/simbol Y, apa signature, docstring, atau call graph-nya?
- Bagian baris skrip mana yang mengeksekusi logika atau algoritma Z?
- Apa skema kolom, distribusi kategori empiris, atau contoh sampel data pada berkas CSV/JSON?

**AI Agent WAJIB menggunakan Agent Memory Engine terlebih dahulu via MCP (`memory_batch_inspect`, `memory_find_by_intent`, `memory_get_phase_map`) atau CLI (`python -m agent_memory -q ... -f ... -i ... -b ...`)!**

---

## 2. Protokol Cognitive Read-Merge-Write & Granular Patching (Anti-Knowledge Regression)
Untuk menjamin **100% Zero Information Loss** saat memperkaya atau memperbarui memori jangka panjang:
1. **Pemeriksaan Sebelum Menulis (Read-Before-Write):**
   - Sebelum memperbarui kartu identitas atau simbol, AI **WAJIB membaca pengetahuan yang sudah ada terlebih dahulu** (`-q <target>` atau `-i <symbol>`).
2. **Penyatuan Kognitif Matang (Cognitive Synthesis):**
   - AI mengolah dan menggabungkan wawasan baru dengan pengetahuan lama menjadi narasi yang utuh, kohesif, dan matang, bukan menempelkan catatan mentah yang berantakan.
3. **Pembaruan Granular (Field-Level Patching):**
   - AI hanya mengirimkan bagian spesifik yang berubah (misal: hanya menambahkan 1 guardrail atau 1 alias baru). Engine database memori secara otomatis melakukan **Smart Merge (Set Union & Bullet Consolidation)** tanpa menimpa atau menghapus wawasan lama yang berharga.
4. **Safety Net Permanen:**
   - Setiap pembaruan memori otomatis dicatat ganda ke `knowledge_seed.json` sebagai cadangan permanen.

---

## 3. Protokol Eksekusi Paralel Terisolasi untuk Pemahaman Proyek Super Cepat (*Rapid Cognitive Ingestion*)
Prinsip pemanggilan paralel terisolasi berlaku untuk **DUA TUJUAN UTAMA**:
1. **Untuk Menjawab Pertanyaan Pengguna:** Menyajikan kartu identitas yang terpisah, rapi, dan tidak bercampur.
2. **UNTUK KEBUTUHAN INTERNAL AI AGENT SENDIRI (MANDAT INTI):**
   - Setiap kali AI menerima tugas koding, bugfix, refactoring, atau fitur baru, AI **WAJIB PROAKTIF mengeksekusi pemanggilan paralel terisolasi serentak** ke seluruh modul/berkas yang berada dalam radius kerja (*blast radius*).
   - AI menyerap seluruh arsitektur, gotchas, dan baris eksak dalam 1 detik secara utuh tanpa terpotong batas buffer terminal sebelum menyentuh kode.

---

## 4. Format Output Padat Horizontal (Zero Data Loss & Anti-Truncate)
Seluruh laporan kartu identitas disajikan dalam format **Kepadatan Horizontal Maksimal**:
- **Pilar 1 (Purpose):** Paragraf padat fungsi dan peran bisnis.
- **Pilar 2 (Architecture):** Relasi hulu (upstream) dan hilir (downstream) segaris.
- **Pilar 3 (Symbols & Contracts):** Setiap fungsi disajikan dalam 2–3 baris padat horizontal (Nama, baris eksak `#Lstart-Lend`, signature lengkap, fungsi yang dipanggil, efek samping, penanganan error, fase alur, dan alias) tanpa pemangkasan data.
- **Pilar 6 (Guardrails):** Batasan mutlak dan jebakan runtime.

---

## 5. Hukum Wajib Input Memori: High-Density Technical English & Pengecualian Alias Awam
1. **Spesifikasi Teknis Wajib High-Density English:**
   - Seluruh deskripsi teknis pada entitas, simbol, logic blocks, contracts, upstream/downstream dependencies, dan guardrails **WAJIB DIINPUTKAN DALAM BAHASA INGGRIS TEKNIS** yang ringkas, presisi, dan padat (menghemat 40-45% token).
2. **Pengecualian Mutlak: Kamus Istilah Awam & Slang Pengguna (Colloquial Aliases):**
   - Khusus pada bagian `aliases` dan `colloquial_aliases`, **WAJIB MEMUAT FRASA PERCAKAPAN, KEBIASAAN PERINTAH, DAN SLANG BAHASA INDONESIA SEHARI-HARI** yang sering dilontarkan pengguna (misal: "sambung audio", "potong ayat", "teks masuk duluan", "audio numpuk", "bismillah kepotong", "cek hak cipta", "render kilat").
   - Tujuannya: Memastikan pencarian intent pengguna via SQLite FTS5 selalu berhasil instan (*one-shot hit*).

---

## 6. Mandat Rujukan Sumber Eksak (Path, Baris Awal & Baris Akhir)
Setiap data teknis yang dicatat di memori maupun yang disampaikan kepada pengguna **WAJIB MENYERTAKAN RUJUKAN LOKASI EKSKLUSIF: PATH BERKAS, NOMOR BARIS AWAL, DAN NOMOR BARIS AKHIR**:
- **Format:** `[path/to/file.ext#L<start>-L<end>](file:///d:/path/to/file.ext#L<start>-L<end>)`
- **Contoh:** `[tools/create_fatihah_master_videos.py#L78-L120](file:///d:/Documents/quran-video-studio/tools/create_fatihah_master_videos.py#L78-L120)`

---

## 7. Larangan Keras Flat-File Dump & Walkthrough di Workspace
1. **Pemusnahan Flat-File Dump Usang:** Dilarang keras membuat atau memperbarui berkas flat-file seperti `CODE_SYMBOLS.md`, `PROJECT_STRUCTURE.md`, `digest.txt`, `repomix-output.xml`, `repomix.config.json`, atau `.gitingestignore`. Seluruh fungsi berkas tersebut telah 100% digantikan oleh database SQLite FTS5 `memory.db` secara selektif dan hemat token.
2. **Larangan Berkas Walkthrough / Catatan AI di Workspace:** Dilarang keras menulis berkas laporan eksekusi seperti `walkthrough.md`, `audit.md`, atau catatan internal di dalam workspace proyek. Seluruh rangkuman audit dan walkthrough wajib disampaikan langsung di antarmuka chat atau disimpan di direktori artifak IDE (`<appDataDir>\brain\<conversation-id>`).

