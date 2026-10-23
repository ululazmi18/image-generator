---
trigger: model_decision
description: Aktif saat membuat pesan git commit, menerapkan prinsip atomic commit per tugas terisolasi, atau menggunakan format penulisan conventional commits (feat, fix, refactor).
---

# ATOMIC COMMITS & CONVENTIONAL COMMITS

Pedoman ini mengatur prinsip commit atomik dan format pesan git standar industri pada setiap penyelesaian tugas.

---

## 1. Prinsip Atomic Commit
- Setiap *commit* harus bersifat atomik: terisolasi dan hanya mencakup satu tanggung jawab atau unit kerja spesifik.
- Dilarang keras mencampuradukkan perubahan yang tidak saling berhubungan (misalnya menggabungkan refactoring dengan perbaikan bug) ke dalam satu *commit*.

---

## 2. Format Conventional Commits
Tulis pesan commit dengan format standar:
- `feat:` Penambahan fitur atau kapabilitas baru.
- `fix:` Perbaikan kutu (*bug*) atau galat kode.
- `refactor:` Restrukturisasi kode tanpa mengubah perilaku eksternal.
- `docs:` Pembaruan atau penambahan dokumentasi.
- `style:` Perapian format, spasi, *indentation* (tanpa perubahan logika).
- `chore:` Pemeliharaan dependensi, berkas build, atau alat penunjang.
- `test:` Penambahan atau perbaikan pengujian unit/integrasi.
