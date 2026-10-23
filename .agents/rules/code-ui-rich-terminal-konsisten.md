---
trigger: model_decision
description: Aktif saat membuat atau memodifikasi antarmuka terminal/CLI/TUI di Python, mewajibkan penggunaan Rich secara maksimal untuk seluruh elemen visual, tabel, panel, status, input prompt, serta indikator loading Progress bar konsisten.
---

# STANDAR KONSISTENSI ANTARMUKA TERMINAL & CLI BERBASIS RICH (TERMINAL UI RICH PROTOCOL)

Aturan ini mewajibkan seluruh aplikasi antarmuka terminal, CLI, dan TUI menggunakan pustaka `rich` secara maksimal dan menyeluruh pada setiap detail interaksi dan visualisasi konsol tanpa terkecuali.

---

## 1. Mandatori Rich Console (Larangan Plain Print)
- **Zero Plain `print`:** Dilarang keras menggunakan fungsi bawaan `print()` polos tanpa format untuk mencetak status, menu, log interaktif, atau tampilan antarmuka ke terminal.
- **Konsol Terpusat & Tema Standar:** Wajib menggunakan instance `rich.console.Console` terpusat dengan palet warna `Theme` konsisten:
  ```python
  from rich.console import Console
  from rich.theme import Theme

  CUSTOM_THEME = Theme({
      "info": "cyan",
      "success": "bold green",
      "warning": "bold yellow",
      "error": "bold red",
      "accent": "bold magenta",
      "muted": "dim white",
      "gold": "bold yellow",
  })
  console = Console(theme=CUSTOM_THEME)
  ```
- **Ikon & Indikator Semantik Konsisten:** Setiap pesan status sekecil apa pun wajib memiliki styling dan simbol pembeda:
  - Sukses: `[bold green]✓[/bold green] <pesan>`
  - Gagal/Error: `[bold red]✗[/bold red] <pesan>`
  - Peringatan: `[bold yellow]⚠[/bold yellow] <pesan>`
  - Informasi: `[bold cyan]ℹ[/bold cyan] <pesan>`

---

## 2. Struktur Tampilan Antarmuka (Panel, Table & Box)
- **`Panel` untuk Bingkai Header & Kartu Informasi:**
  - Banner aplikasi, header seksi (*section header*), kotak informasi sistem, notifikasi penting, dan kartu ringkasan wajib dibingkai menggunakan `rich.panel.Panel` dengan sudut membulat rapi (`box.ROUNDED`).
- **`Table` untuk Semua Data Terstruktur & Menu:**
  - Seluruh menu navigasi, opsi perintah, daftar akun, statistik saldo, dan matriks data wajib disajikan dalam `rich.table.Table`.
  - Berikan styling garis (`box.ROUNDED` atau `box.SIMPLE_HEAVY`), penataan kolom proporsional, serta warna *header* kontras.
- **`Prompt` & `Confirm` untuk Input Pengguna:**
  - Masukan pengguna wajib ditangani via `rich.prompt.Prompt`, `IntPrompt`, `FloatPrompt`, atau `Confirm.ask` agar input divalidasi rapi dan serasi dengan tema UI.

---

## 3. Standar Wajib Loading Progress Bar
- **Mandatori `rich.progress.Progress`:** Setiap proses tunggu atau operasi yang memakan waktu (eksekusi request HTTP, batch worker, loop data, sinkronisasi file, inspeksi, atau delay jeda waktu) **wajib** menampilkan indikator loading `Progress`.
- **Komposisi Kolom Standar:**
  ```python
  from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

  with Progress(
      SpinnerColumn(),
      TextColumn("[progress.description]{task.description}"),
      BarColumn(),
      TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
      TimeElapsedColumn(),
      console=console,
  ) as progress:
      task = progress.add_task("[cyan]Memproses data...", total=100)
      ...
  ```
- **Inline Table Progress Bar:** Untuk indikator progress di dalam sel `Table`, wajib gunakan karakter blok Unicode representatif (`█` dan `░`) dengan kalkulasi persentase yang jelas.

---

## 4. Pembaruan Real-Time (Live Dashboard)
- Untuk monitoring data yang bergerak dinamis (seperti auto-trader, sniper bot, watcher log, atau status koneksi), gunakan `rich.live.Live` bersama `rich.console.Group`.
- Tetapkan refresh rate yang stabil (contoh: 2–4 FPS) dengan parameter `auto_refresh=True` agar layar diperbarui secara mulus tanpa kedip (*flicker*) atau baris terduplikasi.

---

## 5. Standar Encoding & Portabilitas Layar
- Sematkan konfigurasi UTF-8 di awal berkas entrypoint utama untuk menjamin kelancaran emoji dan simbol Unicode:
  ```python
  try:
      sys.stdout.reconfigure(encoding="utf-8")
      sys.stderr.reconfigure(encoding="utf-8")
  except Exception:
      pass
  ```
- Pembersihan layar wajib menggunakan `console.clear()` dari `rich`.
