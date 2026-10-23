---
trigger: model_decision
description: Aktif saat memodifikasi kode yang sudah ada, mencegah regresi logika stabil (anti-regression), atau menjaga konsistensi kontrak fungsi bersama dan utilitas sistem.
---

# PRESERVASI FUNGSIONALITAS SISTEM (ANTI-REGRESSION)

Pedoman ini mengatur proteksi logika stabil, pencegahan regresi, dan konsistensi kontrak antar-komponen saat melakukan modifikasi kode sumber.

---

## 1. Larangan Perusakan Logika Stabil
- **Dilarang keras** mengubah, menghapus, atau merombak fungsionalitas, logika bisnis, modul, atau utilitas yang sudah berjalan stabil dan teruji.
- Pengecualian hanya berlaku jika pengguna memberikan instruksi tertulis eksplisit untuk melakukan penggantian arsitektur atau mutlak diperlukan untuk perbaikan bug yang terisolasi.

---

## 2. Konsistensi Kontrak Antarmuka (Interface Contracts)
- Modifikasi pada modul utilitas bersama (*shared helpers*) tidak boleh merusak fungsionalitas komponen lain yang bergantung padanya (*prevent regression*).
- Jika perlu mengubah tanda tangan fungsi (*function signature*), pastikan kompatibilitas ke belakang (*backward compatibility*) tetap terjaga atau perbarui seluruh pemanggilnya secara sinkron.
