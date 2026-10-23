---
description: Aktif saat penambahan, pencarian, atau pengelolaan bookmark di Firefox Portable, menegakkan penempatan di Bilah Alat Markah (Bookmarks Toolbar) flat dan eksekusi via ManageBookmarks.py.
globs: "**/*"
trigger: model_decision
---

# FIREFOX PORTABLE BOOKMARK WORKFLOW RULES

Aturan ini menegakkan standar arsitektur Bilah Alat Markah (*Bookmarks Toolbar*), struktur flat tanpa subfolder, dan otomasi sinkronisasi lintas profil di Firefox Portable.

---

## 1. Pusat Utama Bilah Alat Markah (Toolbar-First)
- **Lokasi Utama di Bilah Atas:** Seluruh bookmark dipusatkan di **Bilah Alat Markah (*Bookmarks Toolbar*)** agar tampil langsung di tab/bilah atas peramban dan mudah diakses dalam 1 klik.
- **Struktur Flat Tanpa Subfolder:** Bookmark ditata ke dalam **38 folder flat tematik** tanpa subfolder bersarang. Periksa via CLI `list-folders` atau dokumen referensi [TAXONOMY.md](file:///D:/Documents/FirefoxPortable/.agents/skills/firefox-bookmarks/references/TAXONOMY.md).
- **Format Judul Standar:** Wajib `Nama Layanan (Deskripsi Fungsional Singkat)`, contoh: `Google Flow (AI Creative Studio & Video)`, `Gemini (Google AI & LLM Assistant)`.

---

## 2. Perintah Tunggal Eksekusi (One-Command Fast Run)
Tambahkan bookmark baru langsung dengan CLI otomasi:

```powershell
python D:\FirefoxPortable\Sync\ManageBookmarks.py add "<URL>" --title "<Nama (Fungsi)>" --folder "<Nama Folder Flat>"
```

Skrip ini otomatis:
1. Memvalidasi duplikasi URL.
2. Memverifikasi keberadaan folder di Bilah Alat Markah.
3. Mencadangkan data master dan basis data seluruh profil.
4. Memperbarui checksum SHA-256 master `bookmarks.json`.
5. Menyuntikkan bookmark ke seluruh profil (`ulul_azmi`, `cecep_haykal`, `lia_nurjanah`, `moba_ml`).
6. Memperbarui `state.json` agar seluruh profil sinkron tanpa konflik.

---

## 3. Utilitas Pendukung
- **Daftar Folder di Toolbar:** `python D:\FirefoxPortable\Sync\ManageBookmarks.py list-folders`
- **Pencarian Bookmark/Folder:** `python D:\FirefoxPortable\Sync\ManageBookmarks.py search "<kata_kunci>"`
- **Status Sinkronisasi Profil:** `python D:\FirefoxPortable\Sync\ManageBookmarks.py status`
