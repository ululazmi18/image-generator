# Image Generator — Workspace Environment

Lingkungan pengembangan dan otomasi *image generation* berbasis peramban (Google Flow, Perchance, Flux, Midjourney, dan model AI lainnya) dengan profil browser terisolasi.

---

## 1. Topologi & Struktur Direktori

```text
Image Generator/
├── .agents/
│   ├── memory/
│   │   ├── PRD.md             # Blueprint kebutuhan & arsitektur
│   │   ├── DESIGN.md          # Standar visual terminal & desain
│   │   ├── task.md            # Status pelacakan tugas implementasi
│   │   └── memory.db          # Basis data memori SQLite FTS5
│   └── rules/                 # Aturan proyek termirror dari D:\.agents\rules
├── browser_profile/           # Direktori profil Firefox Portable terisolasi (diabaikan Git)
│   ├── starter.bat            # Script peluncur utama langsung di dalam folder profil
│   ├── start_browser.bat      # Alias peluncur cepat di dalam folder profil
│   ├── starter.py             # Peluncur alternatif berbasis Python Rich
│   ├── user.js                # Konfigurasi port otomasi Marionette permanen
│   └── [data profil Firefox]  # Bookmarks, logins, extensions, storage
├── automate_flow.py           # Skrip otomasi input & eksekusi Google Flow
├── flow.bat                   # Pintasan eksekusi cepat otomasi Google Flow
├── .gitignore                 # Konfigurasi proteksi privasi profil & cache
└── README.md                  # Panduan pengoperasian modul
```

---

## 2. Cara Menjalankan Profil Browser

Buka folder [browser_profile](file:///d:/Documents/Image%20Generator/browser_profile), lalu klik ganda [starter.bat](file:///d:/Documents/Image%20Generator/browser_profile/starter.bat) (atau [start_browser.bat](file:///d:/Documents/Image%20Generator/browser_profile/start_browser.bat)).

---

## 3. Otomasi Google Flow

Setelah peramban terbuka dan tab Google Flow aktif, jalankan otomasi input prompt:

### Melalui Batch Runner (`flow.bat`):
```powershell
# Input prompt tanpa kurung tanda petik (spasi otomatis digabung)
.\flow.bat --prompt gambar produk hidup
```

### Melalui Python (`automate_flow.py`):
```powershell
python automate_flow.py --prompt gambar produk hidup
```

*Jika dijalankan tanpa parameter `--prompt`, skrip akan menampilkan prompt interaktif di konsol.*

---

## 4. Fitur & Keunggulan
- **Isolasi Penuh (`-no-remote`):** Berjalan berdampingan dengan profil Firefox lain tanpa bentrok sesi.
- **Port Otomasi Marionette (`127.0.0.1:2828`):** Memungkinkan interaksi langsung ke DOM XPaths Google Flow secara native tanpa memerlukan `geckodriver.exe` eksternal.
- **Sesi Persisten:** Bookmark, ekstensi, dan cookie Google Flow tersimpan mandiri di dalam folder `browser_profile`.
- **Anti-Telemetry:** Menonaktifkan Mozilla Crash Reporter untuk mencegah penulisan log sampah ke drive sistem `C:\`.
- **Auto-Healing Lock:** Otomatis membersihkan `parent.lock` jika sesi sebelumnya terhenti tiba-tiba (*crash/force-close*).
