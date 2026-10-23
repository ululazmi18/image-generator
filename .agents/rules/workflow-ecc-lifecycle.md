---
description: Aktif saat koding, refactoring, bugfix, pengujian, atau audit keamanan untuk secara otomatis dan mandiri mengadopsi standar spesialis ECC Vault di latar belakang tanpa menunggu instruksi atau pemanggilan eksplisit dari pengguna.
trigger: model_decision
globs: "**/*"
---

# WORKFLOW ECC HARNESS LIFECYCLE (AUTONOMOUS ENFORCEMENT)

Aturan ini mewajibkan agen untuk **secara otomatis, proaktif, dan senyap** mengadopsi metodologi terbaik dari **Everything Claude Code (ECC)** pada setiap tugas rekayasa perangkat lunak, **tanpa perlu diminta atau dipanggil secara manual oleh pengguna**.

---

## 1. Prinsip Mandat Otonom (Anti-Pasif)

1. **Pengguna Bebas Beban Perintah:** Pengguna tidak perlu menyebut kata "ECC", "TDD", atau nama spesialis tertentu. Cukup berikan instruksi tugas koding biasa, dan agen wajib langsung menerapkan standar terbaik di balik layar.
2. **Eksekusi Senyap & Alami:** Agen tidak perlu memamerkan proses internal (misal: "Saya sedang membuka modul ECC..."). Agen cukup langsung menyajikan kode yang sudah teruji, aman, dan berstandar industri tinggi.
3. **Kepatuhan Siklus Disiplin (5 Tahap):**
   $$\text{PLAN} \longrightarrow \text{TEST-FIRST} \longrightarrow \text{IMPLEMENT} \longrightarrow \text{REVIEW} \longrightarrow \text{VERIFY}$$

---

## 2. Matriks Pemetaan Otomatis (Tugas ──► Modul ECC)

Setiap kali menerima tugas koding, agen wajib secara mandiri merujuk modul terkait di `D:/Tools/ECC-Reference/ECC-main/`:

| Jenis Tugas Pengguna | Aksi Otomatis di Latar Belakang | Modul Spesialis ECC yang Dirujuk |
| :--- | :--- | :--- |
| **Fitur Baru / Perbaikan Bug** | Menerapkan siklus Test-First (buat test sebelum fix logika). | `skills/tdd-workflow/SKILL.md` |
| **Pasca Menulis / Mengedit Kode** | Audit kualitas kode, keterbacaan, dan simplifikasi logika. | `agents/code-reviewer.md` & `agents/code-simplifier.md` |
| **API, Login, Auth, Input User** | Audit celah keamanan, sanitasi batas, dan pencegahan injeksi. | `agents/security-auditor.md` & `skills/agent-security-hardening/SKILL.md` |
| **Kueri Database / Skema Data** | Validasi efisiensi kueri, indexing, dan pencegahan N+1. | `agents/database-reviewer.md` |
| **Error Kompilasi / Build Rusak** | Analisis akar masalah build dan perbaikan bedah minimalis. | `agents/build-error-resolver.md` |
| **Arsitektur Sistem / Modul Baru** | Pemetaan keputusan arsitektur dan modularitas. | `agents/architect.md` & `skills/api-design/SKILL.md` |

---

## 3. Checklist Verifikasi Mandiri Sebelum Menyerahkan Kode

Sebelum menyatakan tugas selesai kepada pengguna, agen wajib memverifikasi secara mandiri:
- [ ] Apakah logika kode sudah teruji dan bebas dari potensi regresi?
- [ ] Apakah fungsi dibuat fokus (*single-responsibility*) dan tidak over-engineered?
- [ ] Apakah tidak ada API key, kata sandi, atau data rahasia yang tertanam langsung?
- [ ] Apakah seluruh masukan pengguna telah divalidasi dengan aman di batas sistem?
- [ ] Apakah perubahan kode dapat dijalankan dengan sukses (*zero-error*)?
