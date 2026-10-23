# PRODUCT REQUIREMENTS DOCUMENT (PRD)
## Image Generator — Browser Automation & Isolated Profile Environment

### 1. Overview
Workspace `Image Generator` dirancang untuk otomasi generasi gambar berbasis peramban (web-based AI image generation seperti Perchance, Midjourney, Flux, Leonardo, dsb.) dan utilitas terkait. Langkah fondasi pertama adalah menyiapkan lingkungan profil peramban terisolasi (`browser_profile`) berbasis Firefox Portable (`ulul_azmi`) dengan skrip peluncur (*starter*) langsung di dalam direktori profil.

### 2. Requirements & User Stories
- **Isolasi Penuh:** Pengguna membutuhkan profil peramban yang terisolasi dari instalasi utama agar sesi login, token, bookmark, dan ekstensi dapat digunakan khusus untuk proyek `Image Generator`.
- **In-Folder Starter:** Pengguna dapat langsung membuka folder profil dan mengeklik berkas starter (`starter.bat` / `start_browser.bat`) untuk meluncurkan peramban dengan parameter profil yang tepat (`-no-remote -profile "%~dp0"`).
- **Anti-Telemetry & Safe Run:** Menonaktifkan Mozilla Crash Reporter agar tidak menulis log atau membuang crash dump ke partisi `C:\`.

### 3. Core Features (MVP)
1. **Isolated Browser Profile Folder (`browser_profile`):**
   - Kloning dari `D:\FirefoxPortable\Data\profiles\ulul_azmi`.
   - Konfigurasi permanen `user.js` untuk port Marionette `127.0.0.1:2828`.
   - Mengecualikan berkas kunci sementara (`parent.lock`) dan cache web berat (`cache2`).
2. **Direct In-Folder Starter (`browser_profile\starter.bat` & `start_browser.bat`):**
   - Meluncurkan `D:\FirefoxPortable\App\Firefox64\firefox.exe`.
   - Menggunakan parameter otomatis `-no-remote -marionette -profile "%~dp0"`.
3. **Image Generator Automation Module (`image_generator.py` & `Image Generator.py`):**
   - Klien protokol Marionette native (zero-dependency socket client).
   - Pemindai otomatis tab aktif Google Flow (`aisandbox-root` / `flow-project-shell`).
   - Ekstraktor argumen `--prompt {teks}` yang menggabungkan seluruh kata tanpa tanda petik.
   - Pemasukan prompt via `document.execCommand('insertText')` dan pemicuan eksekusi.
   - Hover pada tile gambar pertama (`flow-grid-tile-container[1]`) dan pemantauan hotbar button 3 sebagai sinyal selesai.
   - Pembukaan context menu opsi hotbar, hover submenu download ke-5, dan klik download ke-2.
   - Pemantauan unduhan berkas `.jpg` di direktori unduhan hingga selesai dan pemindahan fleksibel ke target pemanggil.
   - Fungsi callable: `generate_image(prompt, output_path=None, timeout=180) -> Path`.

### 4. User Flow
1. Pengguna membuka peramban melalui [browser_profile\starter.bat](file:///d:/Documents/Image%20Generator/browser_profile/starter.bat).
2. Pengguna membuka tab Google Flow ([https://labs.google/flow](https://labs.google/flow)) pada proyek yang diinginkan.
3. Skrip pemanggil mengeksekusi fungsi `generate_image(prompt)` atau via CLI `.\image_generator.bat --prompt ... -o ...`.
4. Skrip mengisi prompt, menekan Generate, men-hover tile hingga hotbar muncul, memicu unduhan gambar asli via context menu, dan memindahkan berkas `.jpg` ke lokasi yang ditentukan.

### 5. Architecture Diagram
```mermaid
graph TD
    A[Caller Script / User CLI] -->|generate_image / CLI| B[image_generator.py]
    B -->|Check / Auto-Launch| C[Firefox Portable -marionette]
    C -->|Port 127.0.0.1:2828| D[MarionetteDriver Socket]
    D -->|Find Tab & Switch| E[Tab Google Flow AISandbox]
    E -->|1. Inject Prompt & Enter| F[Rich Text Editor p]
    E -->|2. Hover & Wait Hotbar| G[flow-grid-tile-container 1]
    E -->|3. Click Hotbar & Context Menu| H[flow-menu-item 5 Hover]
    E -->|4. Trigger Download| I[flow-menu-item 2 Click]
    I -->|5. Monitor & Move File| J[Target Destination File .jpg]
```

### 6. File & Directory Layout
- `browser_profile/`: Direktori data profil Firefox (places, extensions, storage, prefs, logins).
- `browser_profile/starter.bat`: Peluncur langsung di dalam folder profil (-marionette).
- `browser_profile/start_browser.bat`: Alias peluncur untuk kenyamanan pengguna.
- `browser_profile/user.js`: Konfigurasi permanen port otomasi Marionette.
- `image_generator.py`: Modul inti dan callable function `generate_image`.
- `Image Generator.py`: Entrypoint alternatif bernama "Image Generator".
- `image_generator.bat` & `Image Generator.bat`: Pintasan runner batch.
- `flow.bat`: Alias runner batch.
- `.gitignore`: Mengabaikan `browser_profile/` dari pelacakan git.

### 7. Constraints & Guardrails
- Profil tidak boleh dilacak oleh Git karena berisi kredensial dan sesi peramban.
- Berkas `parent.lock` wajib dibersihkan agar tidak terjadi konflik multi-instance.
