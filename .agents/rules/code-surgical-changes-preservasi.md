---
trigger: model_decision
description: Aktif saat mengedit atau memodifikasi berkas kode eksisting, menegakkan perubahan bedah (surgical changes), dan melarang perapian/refactoring siluman pada kode sekitar.
---

# PERUBAHAN BEDAH PRESISI (SURGICAL CHANGES PROTOCOL)

Pedoman ini mengatur disiplin modifikasi kode eksisting (*Surgical Changes*) untuk menjaga kebersihan diff dan mencegah efek samping yang tidak diinginkan.

---

## 1. Prinsip Modifikasi Terfokus
- **Hanya sentuh baris yang wajib diubah.** Setiap baris kode yang diubah wajib memiliki korelasi langsung dengan permintaan pengguna.
- **Larangan Refactoring Siluman (*No Drive-By Refactoring*):** Jangan "merapikan", memformat ulang, atau mengubah gaya kode, komentar, maupun indentasi di area sekitar yang tidak diminta.
- Jangan merefaktor kode yang tidak rusak atau sedang berjalan stabil.
- Sesuaikan gaya penulisan dengan kode yang sudah ada (*match existing style*), meskipun Anda memiliki preferensi penulisan yang berbeda.

---

## 2. Penanganan Kode Yatim (*Orphaned Code*)
- Jika perubahan Anda membuat impor, variabel, atau fungsi menjadi tidak lagi terpakai, bersihkan entitas tersebut (*clean up your own mess*).
- **Jangan menghapus kode mati pra-eksisting** milik pengguna yang sudah ada sebelumnya kecuali diinstruksikan. Cukup laporkan secara terpisah jika relevan.
