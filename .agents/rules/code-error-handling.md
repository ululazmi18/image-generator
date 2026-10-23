---
trigger: model_decision
description: Aktif saat mengimplementasikan penanganan galat (error handling defensif), blok try-catch, spesifikasi tipe exception, atau operasi I/O, API jaringan, dan query database.
---

# PENANGANAN GALAT DEFENSIF (ERROR HANDLING)

Pedoman ini mengatur implementasi penanganan error komprehensif, tangkapan tipe exception spesifik, dan pencegahan unhandled rejection pada seluruh operasi kritis.

---

## 1. Cakupan Wajib Error Handling
Blok penanganan galat defensif (`try-catch`, error propagation) **wajib diterapkan** pada:
- Seluruh fungsi *asynchronous* (`async/await`, Promise chains).
- Operasi I/O sistem (membaca, menulis, membuat, atau menghapus berkas dan direktori lokal).
- Pemanggilan jaringan, integrasi HTTP client, dan panggilan API pihak ketiga.
- Eksekusi kueri, transaksi, dan manipulasi basis data.

---

## 2. Spesifisitas Tipe Exception
- Tangkap tipe *exception* secara spesifik sesuai hierarki bahasa pemrograman (misalnya: `FileNotFoundError`, `HttpError`, `ValidationError`).
- Hindari penangkapan exception generik kosong (seperti `catch (e) {}` atau `except: pass`) tanpa penanganan atau pencatatan yang jelas.
- Berikan pesan kesalahan kontekstual yang informatif untuk memudahkan debugging tanpa membocorkan data sensitif pengguna.
