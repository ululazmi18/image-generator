---
trigger: model_decision
description: Aktif saat memperbarui versi dependensi pustaka, pemeliharaan sistem runtime, audit breaking changes framework baru, atau upgrade lingkungan perangkat lunak.
---

# ALUR PEMELIHARAAN SISTEM & UPGRADE DEPENDENSI (MAINTENANCE PROTOCOL)

Pedoman ini mengatur tahapan pembaruan paket dependensi secara aman, audit *breaking changes*, dan pengujian operasional build sistem.

---

## Tahap Pelaksanaan Pemeliharaan & Upgrade

1. **Tahap 1 (Audit Kompatibilitas & Breaking Changes):**
   - Tinjau catatan rilis (*release notes*) dan daftar *breaking changes* dari versi baru dependensi atau framework yang akan diperbarui.

2. **Tahap 2 (Pembaruan Bertahap Inkremental):**
   - Perbarui dependensi secara bertahap satu per satu atau per kelompok kecil. Hindari merombak seluruh dependensi sekaligus demi mencegah konflik dependensi silang yang rumit.

3. **Tahap 3 (Uji Operasional & Build):**
   - Jalankan proses build proyek dan pengujian operasional untuk memastikan aplikasi tetap berjalan normal pasca-upgrade.

4. **Tahap 4 (Commit):**
   - Buat commit lokal `chore(deps): <deskripsi_update>` dan catat perubahan versi yang dilakukan.
