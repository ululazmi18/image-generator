---
trigger: model_decision
description: Aktif saat menentukan inisiatif pemilihan tool/MCP secara mandiri (prinsip anti-pasif) atau mengevaluasi perbandingan kapabilitas fitur bawaan IDE versus server MCP.
---

# PRINSIP ANTI-PASIF & EVALUASI KOMPARATIF TOOL/MCP

Pedoman ini mengatur keharusan mengambil inisiatif mandiri dalam penggunaan tool serta kriteria evaluasi fitur bawaan versus server MCP.

---

## 1. Prinsip Inisiatif Mandiri Mutlak (*Autonomous Proactive Tooling*)
- **Dilarang Keras Menunggu Perintah:** Agen tidak boleh pasif. Jika suatu tugas dapat ditingkatkan kualitas, akurasi, atau keandalannya dengan memanggil MCP/tool yang ada, agen **wajib langsung mengeksekusinya atas inisiatif sendiri**.
- **Dilarang Menolak / Mengabaikan Kapabilitas:** Dilarang menyatakan tidak memiliki kemampuan jika alat bawaan atau MCP terkait sudah aktif dan terkonfigurasi di lingkungan kerja.

---

## 2. Evaluasi Komparatif Fitur Bawaan vs Server MCP
- **Eliminasi Redundansi (Sama atau Lebih Rendah):** Jika kemampuan MCP terbukti sama atau lebih rendah dibandingkan alat bawaan IDE, utamakan alat bawaan demi kecepatan startup dan efisiensi memori.
- **Adopsi Keunggulan Spesifik (Lebih Superior):** Jika MCP menawarkan kapabilitas spesialisasi khusus yang tidak dapat ditandingi alat bawaan (misal: *ui-skills* untuk standardisasi desain, *context7* untuk basis data dokumen real-time), maka MCP tersebut **wajib dipertahankan dan diutamakan**.
