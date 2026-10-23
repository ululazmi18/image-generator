# Image Generator — Workspace Environment

Lingkungan pengembangan dan otomasi *image generation* berbasis peramban (Perchance, Flux, Midjourney, dan model AI lainnya) dengan profil browser terisolasi.

---

## 1. Topologi & Struktur Direktori

```text
Image Generator/
├── .agents/
│   ├── memory/
│   │   ├── PRD.md             # Blueprint kebutuhan & arsitektur
│   │   ├── DESIGN.md          # Standar visual terminal & desain
│   │   └── task.md            # Status pelacakan tugas implementasi
│   └── rules/                 # Aturan proyek termirror dari D:\.agents\rules
├── browser_profile/           # Direktori profil Firefox Portable terisolasi (diabaikan Git)
│   ├── starter.bat            # Script peluncur utama langsung di dalam folder profil
│   ├── start_browser.bat      # Alias peluncur cepat
│   ├── starter.py             # Peluncur alternatif berbasis Python Rich
│   └── [data profil Firefox]  # Bookmarks, logins, extensions, storage
├── .gitignore                 # Konfigurasi proteksi privasi profil & cache
├── README.md                  # Panduan pengoperasian modul
└── start_browser.bat          # Pintasan peluncur di root workspace
```

---

## 2. Cara Menjalankan Profil Browser

### Opsi A: Langsung dari Dalam Folder Profil (Rekomendasi Utama)
1. Buka folder [browser_profile](file:///d:/Documents/Image%20Generator/browser_profile).
2. Klik ganda berkas [starter.bat](file:///d:/Documents/Image%20Generator/browser_profile/starter.bat) (atau [start_browser.bat](file:///d:/Documents/Image%20Generator/browser_profile/start_browser.bat)).

### Opsi B: Dari Root Workspace
Klik ganda [start_browser.bat](file:///d:/Documents/Image%20Generator/start_browser.bat) di direktori utama `Image Generator`.

### Opsi C: Dari Terminal (Batch / Python)
```powershell
# Melalui script batch
.\browser_profile\starter.bat

# Melalui script Python Rich
python .\browser_profile\starter.py
```

---

## 3. Fitur & Keunggulan
- **Isolasi Penuh (`-no-remote`):** Berjalan berdampingan dengan profil Firefox lain tanpa bentrok sesi.
- **Sesi Persisten:** Bookmark, ekstensi, dan cookie tersimpan mandiri di dalam folder `browser_profile`.
- **Anti-Telemetry:** Menonaktifkan Mozilla Crash Reporter untuk mencegah penulisan log sampah ke drive sistem `C:\`.
- **Auto-Healing Lock:** Otomatis membersihkan `parent.lock` jika sesi sebelumnya terhenti tiba-tiba (*crash/force-close*).
