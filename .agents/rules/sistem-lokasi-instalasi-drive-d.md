---
trigger: model_decision
description: Aktif saat menginstal, mengonfigurasi, atau menempatkan runtime, package manager, SDK, CLI, dependensi, maupun aplikasi tambahan agar selalu dipasang di drive D:\.
---

# TATA KELOLA INSTALASI RUNTIME, TOOL, & APLIKASI DI DRIVE D:\

Pedoman ini mengatur standardisasi penempatan seluruh runtime bahasa pemrograman, package manager, SDK pengembang, toolchain, dan aplikasi tambahan di drive `D:\`.

---

## 1. Mandat Mutlak Penempatan di Drive D:\

1. **Larangan Instalasi di Drive C:\:**
   - Dilarang keras menginstal atau menumpuk runtime baru, aplikasi pihak ketiga, atau alat bantu eksternal di drive `C:\` (partisi sistem).
   - Seluruh dependensi, executable, SDK pengembang, dan binary pendukung **WAJIB** dialokasikan di partisi `D:\` (misalnya di bawah `D:\Tools\` atau direktori domain terkait).

2. **Struktur Direktori Standar Runtime (`D:\Tools\`):**
   - **Python:** `D:\Tools\Python312\` (beserta `D:\Tools\Python312\Scripts\`).
   - **Node.js & NPM:** `D:\Tools\Nodejs\` (beserta prefix `D:\Tools\npm\` dan cache `D:\Tools\npm-cache\`).
   - **Astral UV & UVX:** `D:\Tools\uv\` (beserta `D:\Tools\uv-cache\` dan `D:\Tools\uv-tools\`).

---

## 2. Standar Jalur Eksekusi (Environment & PATH)

- Setiap kali menambahkan biner atau tool baru di `D:\Tools\`, path eksekusinya wajib didaftarkan ke `PATH` (User Environment Variable) agar dapat dipanggil secara langsung oleh terminal maupun agent background task tanpa path absolut yang rapuh.
- Urutan prioritas PATH harus memastikan biner di `D:\Tools\` dieksekusi terlebih dahulu sebelum alias sistem bawaan WindowsApps.

---

## 3. Isolasi Cache & Paket Global

- **NPM / NPX:** Konfigurasi `npm config set prefix "D:\Tools\npm"` dan `npm config set cache "D:\Tools\npm-cache"` agar pengunduhan paket npx/npm global tidak mengotori direktori user di drive C.
- **UV / UVX:** Konfigurasi environment variable `UV_CACHE_DIR=D:\Tools\uv-cache`, `UV_TOOL_DIR=D:\Tools\uv-tools`, dan `UV_TOOL_BIN_DIR=D:\Tools\uv-tools\bin`.
- **PIP & HuggingFace Cache:** Konfigurasi `PIP_CACHE_DIR=D:\Tools\pip-cache` dan `HF_HOME=D:\Tools\hf-cache` agar unduhan wheel dan model AI terisolasi di drive D:\.
- **Vault Cadangan Konfigurasi Master:** Seluruh aset konfigurasi sistem Antigravity/Gemini wajib dicadangkan ke `D:\Tools\.gemini\` (`GEMINI.md`, `config\plugins\`, `skills\`) serta master rules/skills di `D:\.agents\`.

---

## 4. Portabilitas & Kompatibilitas Multi-Platform (Termux & Mobile First)

- **Standarisasi Versi:** Utamakan versi runtime yang paling stabil, matang, dan memiliki kompabilitas luas di seluruh ekosistem (termasuk arsitektur ARM64 / lingkungan Termux Android), seperti **Python 3.12**.
- **Ketersediaan Toolchain MCP:** Seluruh server Model Context Protocol (MCP) yang mengandalkan runner `npx` dan `uvx` harus berjalan menggunakan binary runtime yang berakar di drive `D:\`.