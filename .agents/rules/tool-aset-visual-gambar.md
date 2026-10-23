---
trigger: model_decision
description: Aktif saat membutuhkan aset gambar, desain ilustrasi, mockup antarmuka visual, logo, ikon, banner dokumen, atau larangan penggunaan placeholder kosong.
---

# FITUR BAWAAN: GENERASI ASET GAMBAR & DESAIN VISUAL

Pedoman ini mengatur pemanfaatan fitur bawaan `generate_image` untuk menghasilkan aset grafis nyata dan larangan mutlak menggunakan kotak *placeholder* kosong.

---

## 1. Generasi Visual Mandiri (`generate_image`)
- Agen memiliki kapabilitas bawaan (*native tool*) untuk memproduksi (*text-to-image*) dan mengedit aset gambar secara langsung tanpa alat perantara.
- **Wajib digunakan secara proaktif** untuk:
  - Mockup desain antarmuka pengguna (UI layout & screens).
  - Pembuatan logo proyek, lambang, dan ikon grafis.
  - Ilustrasi pendukung, foto representatif, dan banner dokumen.

---

## 2. Larangan Mutlak Placeholder Kosong
- **Dilarang keras** menggunakan teks atau kotak *placeholder* kosong (seperti kotak abu-abu bertuliskan "Gambar Disini") jika gambar representatif dapat digenerasikan secara langsung.
- Gambar yang diproduksi otomatis tersimpan sebagai artefak dan siap disematkan langsung pada kode antarmuka.
