---
description: Standar hierarki direktori latihan Power Automate, pemisahan folder input data ekstrem, folder output serahan pengguna, dan verifikasi integritas data otomatis.
trigger: model_decision
globs: "**/powerautomate/**"
---

# STRUKTUR WORKSPACE & DATA POWER AUTOMATE

Dokumen ini mendefinisikan arsitektur folder kerja, isolasi data uji ekstrim, dan penyerahan hasil tugas latihan Power Automate.

---

## 1. Hierarki Direktori Standar
Seluruh latihan diatur dalam struktur direktori modular:
```text
powerAutomae/
├── .agents/rules/               # Aturan operasional & kedaulatan proyek
├── progress_tracker.md          # Papan status capaian level pengguna
├── levels/
│   ├── level-01-file-system/
│   │   ├── README.md            # Brief instruksi tugas & rubrik
│   │   ├── input/               # Tempat supervisor menaruh data mentah ekstrim
│   │   ├── output/              # Tempat pengguna menyimpan hasil run otomatisasi
│   │   └── .benchmark/          # Kunci jawaban & script evaluasi internal
│   ├── level-02-excel-csv/
│   └── ...
```

---

## 2. Integritas Data Ekstrim
- Data input mentah di folder `input/` bersifat **Read-Only** bagi alur otomatisasi, kecuali skenario spesifik memindahkan/mengarsipkan berkas.
- Folder `output/` adalah zona bersih tempat pengguna menyerahkan produk akhir.
- Data wajib mencakup kasus nyata: format tanggal inkonsisten, karakter khusus/spasi liar, nilai null/kosong, duplikasi data, dan volume masif (ribuan data).
