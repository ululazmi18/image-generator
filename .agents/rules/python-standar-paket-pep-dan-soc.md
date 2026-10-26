---
trigger: model_decision
description: Aktif saat membuat, merancang, atau menyempurnakan skrip dan modul Python, menegakkan standar modern packaging PEP 517/518/621 (pyproject.toml), arsitektur modular Separation of Concerns (SoC), eliminasi duplikasi logika (DRY), dan standar expert.
---

# STANDAR PENGEMBANGAN MODUL & PAKET PYTHON EXPERT (PEP 517/518/621 & SOC)

Aturan ini mengikat secara mutlak setiap kali merancang, membuat, menyempurnakan, atau merefaktor proyek/skrip berbahasa Python agar selalu beroperasi pada standar rekayasa perangkat lunak tingkat profesional (*production-grade/expert*).

---

## 1. Standar Modern Packaging PEP 517, PEP 518 & PEP 621
- **Kedaulatan `pyproject.toml`:** Setiap repositori atau modul Python wajib menyertakan `pyproject.toml` sebagai standar metadata terpadu (PEP 621) dan deklarasi build system (PEP 517/518). Dilarang mengandalkan skrip instalasi manual `setup.py` gaya lama tanpa deklarasi modern.
- **Kesiapan Instalasi Editable:** Paket wajib dapat dipasang secara modular melalui `pip install -e .` dengan deklarasi `dependencies`, `requires-python`, `authors`, dan `classifiers` yang valid.
- **Paket Terdistribusi & Terstruktur:** Seluruh kode pustaka inti wajib ditempatkan di dalam folder paket (misal `pkg_name/`) yang dilengkapi `__init__.py` bersih, mengekspor `__version__`, `__all__`, dan simbol publik tingkat tinggi.

---

## 2. Arsitektur Separation of Concerns (SoC) Multi-Lapisan
Dilarang keras menyatukan seluruh logika dalam satu berkas monolitik (*spaghetti code*). Setiap proyek Python wajib didekomposisi ke dalam modul-modul fungsional yang terisolasi:
1. **Lapisan Eksepsi (`exceptions.py`):**
   - Mendefinisikan hierarki kelas eksepsi khusus turunan basis domain (misal `PackageError -> ConnectionError / TimeoutError / NotFoundError`).
   - Dilarang melempar eksepsi mentah generik seperti `RuntimeError` atau `Exception` langsung pada alur logika bisnis.
2. **Lapisan Driver / Klien Protokol (`driver.py` / `client.py`):**
   - Bertanggung jawab murni atas pertukaran pesan tingkat rendah, I/O jaringan, atau protokol kawat (wire protocol) dengan type-hints lengkap.
3. **Lapisan Manajemen Siklus Hidup Proses (`browser.py` / `lifecycle.py`):**
   - Mengelola eksekusi biner, subprocess, sinyal shutdown, port readiness polling, dan perlindungan *resource leak*.
4. **Lapisan Konfigurasi & Persistensi Data (`profile.py` / `storage.py`):**
   - Mengisolasi pembacaan/penulisan berkas konfigurasi, database I/O, migrasi, dan pengamanan lock data.

---

## 3. Prinsip Anti-Duplikasi Logika (DRY) & High-Level Facade
- **Eliminasi Redundansi Eksekusi:** Dilarang menduplikasi kode peluncuran subprocess, inisialisasi lingkungan, polling kesiapan soket, atau konfigurasi driver di berbagai berkas CLI atau skrip pengguna.
- **Dukungan Context Manager Mutlak:** Setiap resource yang memerlukan alokasi dan terminasi (soket, subprocess peramban, koneksi database) **wajib mengimplementasikan protokol context manager Pythonik** (`__enter__` dan `__exit__`), sehingga aman digunakan dalam blok:
  ```python
  with MainClass(...) as resource:
      resource.do_action()
  ```
- **High-Level Facade:** Sediakan kelas orkestrasi utama yang menyediakan metode langsung (*convenience methods*) untuk kebutuhan umum tanpa memaksa pengguna mengontrol detail teknis tingkat rendah secara manual.

---

## 4. Preservasi Kompatibilitas Mundur (Backward-Compatible Shims)
- Saat mengubah berkas skrip datar (*flat script*) menjadi struktur paket modular, **wajib menyediakan berkas shim kompatibilitas di root repositori** (misal `marionette_driver.py` yang me-re-export `firefox_stealth`).
- Hal ini menjamin seluruh otomasi eksisting, impor lama, dan alur kerja pengguna tetap berfungsi 100% tanpa adanya *breaking change*.

---

## 5. Pengujian Unit Terotomasi (Unit Testing & Quality Assurance)
- Setiap modul Python wajib dilengkapi dengan direktori `tests/` yang memverifikasi:
  1. Hierarki dan instansiasi eksepsi khusus.
  2. Logika framing, serialisasi, dan deserialisasi protokol.
  3. Konfigurasi default dan isolasi data.
- Pengujian harus kompatibel dengan modul bawaan `unittest` (`python -m unittest discover tests`) dan `pytest` dengan status eksekusi hijau (100% PASS).
