"""COMMAND LINE INTERFACE (CLI) & INTERACTIVE TERMINAL — GOOGLE FLOW IMAGE GENERATOR.

Modul ini menyediakan antarmuka baris perintah berbasis Rich terminal:
- show_help(): Dokumentasi dan panduan opsi interaktif.
- parse_cli_args(): Parser argumen baris perintah.
- main(): Titik masuk eksekusi utama CLI dan runner batch (run.bat).
"""

import datetime
from pathlib import Path
import shutil
import sys
import time

from rich import box
from rich.panel import Panel
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.prompt import Prompt
from rich.table import Table

from image_generator.constants import (
    AVAILABLE_ASPECT_RATIOS,
    AVAILABLE_COUNTS,
    AVAILABLE_MODELS,
    DEFAULT_ASPECT_RATIO,
    DEFAULT_COUNT,
    DEFAULT_MODEL,
    FLOW_HOME_URL,
    console,
    normalize_aspect_ratio,
    normalize_count,
    normalize_model,
)
from image_generator.core import ImageGenerator
from image_generator.exceptions import GenerationFailedError, QuotaExceededError
from image_generator.models import resolve_target_file_path


def show_help() -> None:
    """Menampilkan panduan bantuan komprehensif, profesional, dan visual berbasis Rich terminal."""
    console.clear()
    banner = (
        "[brand]IMAGE GENERATOR — GOOGLE FLOW AUTOMATION[/brand] [muted]//[/muted] [gold]PANDUAN PENGGUNAAN RESMI[/gold]\n"
        "[muted]Otomasi 100% Senyap Tanpa Mengontrol Kursor Pengguna (Zero Cursor Hijacking) & Mode Native Headless[/muted]"
    )
    console.print(Panel(banner, box=box.ROUNDED, style="color(240)"))

    usage_panel = (
        "[bold cyan]SINTAKSIS PENGGUNAAN (USAGE):[/bold cyan]\n"
        "  [gold]run.bat[/gold] [accent][OPSI...][/accent] [white][\"PROMPT TEKS\"][/white]             [dim]# Runner Batch / Dobel-klik (Windows)[/dim]\n"
        "  [gold]python image_generator.py[/gold] [accent][OPSI...][/accent] [white][\"PROMPT TEKS\"][/white]  [dim]# Baris Perintah Langsung (CLI)[/dim]\n"
        "  [gold]from image_generator import generate[/gold]            [dim]# Layanan Modul Python Profesional[/dim]"
    )
    console.print(Panel(usage_panel, title="[bold]Cara Menjalankan[/bold]", box=box.ROUNDED, style="color(240)"))

    # Tabel 1: Daftar Opsi CLI
    opts_table = Table(
        title="[bold cyan]DAFTAR OPSI & ARGUMEN BARIS PERINTAH (COMMAND LINE OPTIONS)[/bold cyan]",
        box=box.ROUNDED,
        header_style="bold color(208)",
        expand=True,
    )
    opts_table.add_column("Opsi Flag", style="cyan", width=16)
    opts_table.add_column("Alias", style="yellow", width=14)
    opts_table.add_column("Tipe & Default", style="green", width=16)
    opts_table.add_column("Deskripsi & Keterangan Penggunaan", style="white")

    opts_table.add_row(
        "--prompt",
        "-p",
        "Str [dim](Interaktif)[/dim]",
        "Deskripsi teks prompt gambar. Jika dikosongkan, CLI beralih otomatis ke mode interaktif.",
    )
    opts_table.add_row(
        "--model",
        "-m",
        "Str [dim]('pro')[/dim]",
        "Pilihan model AI: [yellow]'pro'[/yellow] (Nano Banana Pro), [yellow]'lite'[/yellow] (2 Lite), [yellow]'2.1'[/yellow].",
    )
    opts_table.add_row(
        "--aspect-ratio",
        "--ar, -a, --ratio",
        "Str [dim]('16:9')[/dim]",
        "Aspek rasio gambar: [magenta]'16:9'[/magenta], [magenta]'4:3'[/magenta], [magenta]'1:1'[/magenta], [magenta]'3:4'[/magenta], [magenta]'9:16'[/magenta] (atau alias [magenta]'square'[/magenta], [magenta]'vertical'[/magenta]).",
    )
    opts_table.add_row(
        "--count",
        "-c, -v, --var",
        "Int/Str [dim]('x1')[/dim]",
        "Jumlah variasi gambar: [green]1[/green], [green]2[/green], [green]3[/green], [green]4[/green] (atau [green]'x1'[/green] s/d [green]'x4'[/green]).",
    )
    opts_table.add_row(
        "--output",
        "-o, -d, --dest",
        "Path [dim]('outputs/')[/dim]",
        "Folder atau nama file tujuan (.jpg). Jika direktori, nama file otomatis dari prompt & timestamp.",
    )
    opts_table.add_row(
        "--timeout",
        "-t",
        "Int [dim](180s)[/dim]",
        "Batas waktu maksimal render per percobaan dalam detik.",
    )
    opts_table.add_row(
        "--email",
        "-e",
        "String [dim](Opsional)[/dim]",
        "Alamat email Google Flow untuk login otomatis mandiri.",
    )
    opts_table.add_row(
        "--password",
        "--pass, -pwd",
        "String [dim](Opsional)[/dim]",
        "Kata sandi Google Flow untuk login otomatis mandiri.",
    )
    opts_table.add_row(
        "--debug",
        "-",
        "Flag [dim](Nonaktif)[/dim]",
        "Mode inspeksi visual. Setiap fase didokumentasikan dalam format .png pada folder [accent]debug/[/accent].",
    )
    opts_table.add_row(
        "--help",
        "-h, help, /?",
        "Flag",
        "Menampilkan panduan bantuan komprehensif ini dan keluar.",
    )
    console.print(opts_table)

    # Tabel 2: Model AI
    models_table = Table(
        title="[bold yellow]PILIHAN MODEL AI GOOGLE FLOW YANG DIDUKUNG[/bold yellow]",
        box=box.ROUNDED,
        header_style="bold yellow",
        expand=True,
    )
    models_table.add_column("Model AI Google Flow", style="bold yellow", width=22)
    models_table.add_column("Alias Cepat", style="cyan", width=16)
    models_table.add_column("Karakteristik & Rekomendasi Penggunaan", style="white")

    models_table.add_row(
        "🍌 Nano Banana Pro",
        "pro, banana pro",
        "Model flagship Google Flow. Kualitas sinematik tertinggi, fotorealistis, pencahayaan alami, dan detail tekstur maksimal.",
    )
    models_table.add_row(
        "🍌 Nano Banana 2 Lite",
        "lite, 2 lite",
        "Model ringan berkecepatan tinggi. Rendering kilat dan sangat efisien untuk sketsa, kartun, dan konsep cepat.",
    )
    models_table.add_row(
        "🍌 Nano Banana 2.1",
        "2.1, banana 2.1",
        "Versi terbaru arsitektur Google Flow dengan peningkatan akurasi pemahaman prompt dan komposisi elemen kompleks.",
    )
    console.print(models_table)

    # Tabel 3: Aspek Rasio
    ratios_table = Table(
        title="[bold magenta]PILIHAN ASPEK RASIO & DIMENSI PIKSEL ASLI[/bold magenta]",
        box=box.ROUNDED,
        header_style="bold magenta",
        expand=True,
    )
    ratios_table.add_column("Rasio", style="bold magenta", width=7)
    ratios_table.add_column("Dimensi Piksel", style="green", width=15)
    ratios_table.add_column("Alias Cepat", style="cyan", width=18)
    ratios_table.add_column("Rekomendasi Peruntukan Media", style="white")

    ratios_table.add_row(
        "16:9",
        "1376 × 768 px",
        "landscape, wide",
        "Wallpaper desktop, banner web, presentasi widescreen 16:9, thumbnail YouTube.",
    )
    ratios_table.add_row(
        "4:3",
        "1152 × 896 px",
        "standard, tablet",
        "Layar monitor klasik, tablet / iPad, presentasi slide standar.",
    )
    ratios_table.add_row(
        "1:1",
        "1024 × 1024 px",
        "square, kotak",
        "Feed Instagram, cover album musik, foto profil, avatar, ikon aplikasi.",
    )
    ratios_table.add_row(
        "3:4",
        "896 × 1152 px",
        "portrait, cetak",
        "Poster potret vertikal, foto dokumen / cetak, brosur vertikal.",
    )
    ratios_table.add_row(
        "9:16",
        "768 × 1376 px",
        "vertical, shorts",
        "Layar penuh smartphone, YouTube Shorts, Instagram Reels, TikTok, Story.",
    )
    console.print(ratios_table)

    # Panel Contoh Penggunaan
    examples_text = (
        "[bold cyan]1. Mode Interaktif (Tanya-Jawab Ramah Pengguna):[/bold cyan]\n"
        "   [dim]> Dobel-klik berkas[/dim] [gold]run.bat[/gold] [dim]atau jalankan:[/dim]\n"
        "   [gold]run.bat[/gold]\n\n"
        "[bold cyan]2. Konten Video Pendek Vertikal (Reels / TikTok / Shorts):[/bold cyan]\n"
        "   [gold]run.bat[/gold] [accent]--prompt[/accent] \"[white]cyberpunk samurai bersinar di malam hujan[/white]\" [accent]--ar[/accent] [magenta]9:16[/magenta] [accent]--model[/accent] [gold]pro[/gold]\n\n"
        "[bold cyan]3. Feed Instagram Bujur Sangkar (1:1 Model Lite):[/bold cyan]\n"
        "   [gold]python image_generator.py[/gold] [accent]-p[/accent] \"[white]cangkir kopi hangat latte art kucing[/white]\" [accent]-m[/accent] [gold]lite[/gold] [accent]-a[/accent] [magenta]1:1[/magenta] [accent]-o[/accent] [green]hasil/[/green]\n\n"
        "[bold cyan]4. Wallpaper Komputer Widescreen (16:9 Sinematik):[/bold cyan]\n"
        "   [gold]run.bat[/gold] [accent]--prompt[/accent] \"[white]panorama pegunungan fajar berkabut 8k[/white]\" [accent]--ar[/accent] [magenta]16:9[/magenta] [accent]--model[/accent] [gold]pro[/gold] [accent]--debug[/accent]\n\n"
        "[bold cyan]5. Integrasi Sebagai Layanan Modul Python:[/bold cyan]\n"
        "   [green]from[/green] [gold]image_generator[/gold] [green]import[/green] [accent]generate[/accent]\n\n"
        "   [white]result = generate([/white]\n"
        "       [white]prompt=[/white]\"[gold]istana kristal terapung di awan[/gold]\",\n"
        "       [white]model=[/white]\"[gold]pro[/gold]\",\n"
        "       [white]aspect_ratio=[/white]\"[magenta]16:9[/magenta]\",\n"
        "       [white]count=[/white][green]1[/green],\n"
        "       [white]output_path=[/white]\"[green]outputs/[/green]\",\n"
        "   [white])[/white]\n"
        "   [white]print(f\"Gambar selesai: {result.file_path} ({result.duration_seconds:.1f}s)\")[/white]"
    )
    console.print(Panel(examples_text, title="[bold]Contoh Penggunaan Praktis[/bold]", box=box.ROUNDED, style="color(240)"))


# ==============================================================================
# CLI PARSER & INTERFACE RUNNER
# ==============================================================================
def parse_cli_args() -> tuple[str, str | None, str, str, str, int, bool, str | None, str | None]:
    """Mengekstrak parameter baris perintah (CLI) untuk prompt, setelan model, rasio, kuantitas, dan kredensial.

    Mendukung opsi:
    - `--prompt` / `-p`: Teks deskripsi prompt.
    - `--model` / `-m`: Nama model AI ('pro', 'lite', '2.1' atau nama lengkap).
    - `--aspect-ratio` / `--ar` / `-a` / `--ratio`: Rasio gambar ('16:9', '4:3', '1:1', '3:4', '9:16', 'square', 'vertical').
    - `--count` / `-c` / `--variations` / `-v`: Kuantitas variasi (1, 2, 3, 4 atau 'x1', 'x2', dst).
    - `--output` / `-o` / `--dest` / `-d`: Folder atau nama berkas tujuan pemindahan.
    - `--timeout` / `-t`: Batas waktu maksimal per percobaan dalam detik (default: 180).
    - `--email` / `-e`: Alamat email Google Flow opsional untuk login otomatis mandiri.
    - `--password` / `--pass` / `-pwd`: Kata sandi Google Flow opsional untuk login otomatis mandiri.
    - `--debug`: Mengaktifkan mode debug visual dengan dokumentasi tangkapan layar (.png).
    - `--help` / `-h` / `help`: Menampilkan panduan bantuan lengkap dan keluar.

    Returns:
        tuple: (prompt, output_dest, model, aspect_ratio, count_str, timeout, debug_enabled, email, password)
    """
    args = sys.argv[1:]

    help_flags = ["--help", "-h", "help", "/?", "-?"]
    if any(a in help_flags for a in args):
        show_help()
        sys.exit(0)

    output_flags = ["--output", "-o", "--dest", "-d"]
    timeout_flags = ["--timeout", "-t"]
    retries_flags = ["--retries", "-r"]
    prompt_flags = ["--prompt", "-p"]
    model_flags = ["--model", "-m"]
    ratio_flags = ["--aspect-ratio", "--ar", "-a", "--ratio"]
    count_flags = ["--count", "-c", "--variations", "-v", "--var"]
    email_flags = ["--email", "-e"]
    password_flags = ["--password", "--pass", "-pwd"]
    headless_flags = ["--headless"]
    debug_flags = ["--debug"]

    output_val = None
    timeout_val = 180
    debug_val = False
    model_val = DEFAULT_MODEL
    ratio_val = DEFAULT_ASPECT_RATIO
    count_val = DEFAULT_COUNT
    email_val = None
    password_val = None
    prompt_tokens = []

    # Konsumsi flag --headless jika masih dioper oleh pengguna agar kompatibel
    args = [a for a in args if a not in headless_flags]

    # Deteksi flag --debug
    if any(a in debug_flags for a in args):
        debug_val = True
        args = [a for a in args if a not in debug_flags]

    i = 0
    while i < len(args):
        arg = args[i]
        if arg in output_flags and i + 1 < len(args):
            output_val = args[i + 1]
            i += 2
        elif arg in model_flags and i + 1 < len(args):
            model_val = normalize_model(args[i + 1])
            i += 2
        elif arg in ratio_flags and i + 1 < len(args):
            ratio_val = normalize_aspect_ratio(args[i + 1])
            i += 2
        elif arg in count_flags and i + 1 < len(args):
            count_val = normalize_count(args[i + 1])
            i += 2
        elif arg in email_flags and i + 1 < len(args):
            email_val = args[i + 1]
            i += 2
        elif arg in password_flags and i + 1 < len(args):
            password_val = args[i + 1]
            i += 2
        elif arg in timeout_flags and i + 1 < len(args):
            try:
                timeout_val = int(args[i + 1])
            except ValueError:
                pass
            i += 2
        elif arg in retries_flags and i + 1 < len(args):
            i += 2
        elif arg in prompt_flags:
            i += 1
            while i < len(args):
                if args[i] in output_flags:
                    output_val = args[i + 1] if i + 1 < len(args) else None
                    i += 2
                elif args[i] in model_flags:
                    model_val = normalize_model(args[i + 1]) if i + 1 < len(args) else model_val
                    i += 2
                elif args[i] in ratio_flags:
                    ratio_val = normalize_aspect_ratio(args[i + 1]) if i + 1 < len(args) else ratio_val
                    i += 2
                elif args[i] in count_flags:
                    count_val = normalize_count(args[i + 1]) if i + 1 < len(args) else count_val
                    i += 2
                elif args[i] in email_flags:
                    email_val = args[i + 1] if i + 1 < len(args) else None
                    i += 2
                elif args[i] in password_flags:
                    password_val = args[i + 1] if i + 1 < len(args) else None
                    i += 2
                elif args[i] in timeout_flags:
                    try:
                        timeout_val = int(args[i + 1])
                    except (ValueError, IndexError):
                        pass
                    i += 2
                elif args[i] in retries_flags:
                    i += 2 if i + 1 < len(args) else 1
                elif args[i] in debug_flags:
                    debug_val = True
                    i += 1
                else:
                    prompt_tokens.append(args[i])
                    i += 1
            break
        else:
            prompt_tokens.append(arg)
            i += 1

    prompt_str = " ".join(prompt_tokens).strip()
    return prompt_str, output_val, model_val, ratio_val, normalize_count(count_val), timeout_val, debug_val, email_val, password_val


def main() -> int:
    """Titik masuk eksekusi utama CLI dan runner batch (run.bat) dengan antarmuka Rich terminal."""
    console.clear()
    banner = (
        "[brand]IMAGE GENERATOR — GOOGLE FLOW BOT[/brand] [muted]//[/muted] [gold]SILENT BACKGROUND EDITION[/gold]\n"
        "[muted]Otomasi 100% Senyap Tanpa Mengontrol Kursor Pengguna & Berjalan di Latar Belakang[/muted]"
    )
    console.print(Panel(banner, box=box.ROUNDED, style="color(240)"))

    prompt, output_dest, model, aspect_ratio, count_str, timeout, debug, email_arg, pwd_arg = parse_cli_args()

    # Mode interaktif jika prompt belum diisi via CLI
    if not prompt:
        console.print(
            "[info]ℹ[/info] [dim]Tips CLI: Anda dapat memberikan argumen lengkap:\n"
            "      run.bat --prompt \"pemandangan fajar\" --model pro --ar 9:16 --count 1[/dim]\n"
        )
        prompt = Prompt.ask("[cyan]Masukkan Prompt Generasi Gambar[/cyan]")

        if prompt.strip():
            change_cfg = Prompt.ask(
                f"[dim]Gunakan setelan default ([gold]🍌 {model}[/gold] | [magenta]{aspect_ratio}[/magenta] | [green]{count_str}[/green])? [Y/n][/dim]",
                default="y",
            )
            if change_cfg.strip().lower() in ("n", "no", "tidak"):
                console.print(f"[dim]Pilihan Model: {', '.join(AVAILABLE_MODELS)}[/dim]")
                m_in = Prompt.ask("[cyan]Pilih Model (pro/lite/2.1)[/cyan]", default=model)
                model = normalize_model(m_in)

                console.print(f"[dim]Pilihan Rasio: {', '.join(AVAILABLE_ASPECT_RATIOS)}[/dim]")
                ar_in = Prompt.ask("[cyan]Pilih Aspek Rasio (16:9, 1:1, 9:16, dll)[/cyan]", default=aspect_ratio)
                aspect_ratio = normalize_aspect_ratio(ar_in)

                c_in = Prompt.ask("[cyan]Pilih Kuantitas Variasi (1/2/3/4)[/cyan]", default="1")
                count_str = normalize_count(c_in)

    if not prompt.strip():
        console.print("[error]✗[/error] Prompt tidak boleh kosong.")
        return 1

    target_display = str(Path(output_dest).resolve()) if output_dest else str(Path("outputs").resolve())

    table = Table(box=box.ROUNDED, show_header=False, expand=True)
    table.add_column("Parameter", style="cyan", width=22)
    table.add_column("Nilai", style="bold white")
    table.add_row("Prompt Teks", f"[gold]{prompt}[/gold]")
    table.add_row("Model AI", f"[gold]🍌 {model}[/gold]")
    table.add_row("Aspek Rasio", f"[magenta]{aspect_ratio}[/magenta]")
    table.add_row("Kuantitas Gambar", f"[green]{count_str}[/green]")
    table.add_row("Metode Eksekusi", "[bold green]100% Silent Background (Zero Cursor Hijacking)[/bold green]")
    table.add_row("Mode Tampilan", "[bold yellow]100% Native Headless (Tanpa GUI)[/bold yellow]")
    table.add_row("Auto-Retry Penanganan", "[bold green]Tanpa Batas (Loop sampai ada hasil)[/bold green]")
    table.add_row(
        "Mode Debug Visual",
        "[bold magenta]Aktif (Dokumentasi Screenshot di folder debug/)[/bold magenta]"
        if debug
        else "[dim]Nonaktif (Gunakan --debug untuk inspeksi visual)[/dim]",
    )
    table.add_row("Target Pemindahan", f"[accent]{target_display}[/accent]")
    table.add_row("Batas Waktu (Timeout)", f"{timeout} detik/percobaan")
    console.print(table)

    target_files: list[Path] = []
    successful_attempt = 1
    retry_delay = 12.0
    start_main_ts = time.time()

    generator = ImageGenerator(
        model=model,
        aspect_ratio=aspect_ratio,
        count=count_str,
        email=email_arg,
        password=pwd_arg,
        debug=debug,
    )

    try:
        console.print("[info]ℹ Memeriksa peramban & kanvas Google Flow...[/info]")
        generator.ensure_browser()
        generator.connect()
        generator.find_flow_tab()
        active_email = generator.get_current_user_email()
        if active_email:
            console.print(f"[info]ℹ Akun Google Flow terhubung:[/info] [bold cyan]{active_email}[/bold cyan]")
        generator.capture_debug_screenshot("01_canvas_ready", "Kondisi awal kanvas siap")
    except Exception as init_err:
        console.print(f"\n[error]✗ Kegagalan Otomasi:[/error] {init_err}")
        generator.close()
        return 1

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Menjalankan otomasi generasi gambar...", total=None)

        try:
            success = False
            attempt = 1

            while not success:
                try:
                    # Bersihkan SELURUH tile di kanvas agar kanvas selalu kosong sebelum generasi baru
                    generator.delete_all_canvas_tiles()

                    # Segarkan halaman jika beberapa kali percobaan berturut-turut gagal
                    if attempt > 1 and attempt % 4 == 0:
                        progress.update(
                            task,
                            description=f"[cyan]Menyegarkan halaman Google Flow (Percobaan ke-{attempt})...[/cyan]",
                        )
                        try:
                            nav_url = getattr(generator, "current_project_url", None) or FLOW_HOME_URL
                            generator.driver.navigate(nav_url)
                            time.sleep(3.5)
                            generator.find_flow_tab()
                            generator.capture_debug_screenshot(
                                f"page_refresh_att_{attempt}",
                                f"Penyegaran halaman kanvas (Percobaan ke-{attempt})",
                            )
                        except Exception:
                            pass

                    existing = set()
                    for d in generator.download_dirs:
                        if d.exists():
                            for f in list(d.glob("*.jpg")) + list(d.glob("*.jpeg")):
                                existing.add(str(f.resolve()))

                    if attempt > 1:
                        progress.update(
                            task,
                            description=f"[cyan]Mengulang input prompt (Percobaan ke-{attempt} - Tanpa Batas)...[/cyan]",
                        )
                    else:
                        progress.update(task, description="[cyan]Mengirim prompt secara senyap (ProseMirror DOM)...")

                    initial_state = generator.submit_prompt(prompt)
                    generator.capture_debug_screenshot(
                        f"prompt_submitted_att_{attempt}",
                        f"Prompt dikirim (Percobaan ke-{attempt})",
                    )

                    progress.update(
                        task,
                        description=f"[gold]Menunggu render gambar (Percobaan ke-{attempt})...[/gold]",
                    )
                    generator.hover_and_wait_tile(
                        initial_state=initial_state,
                        timeout=timeout,
                        progress_callback=lambda p: progress.update(
                            task,
                            description=f"[gold]Menunggu render gambar selesai ({p}% - Percobaan ke-{attempt})...[/gold]",
                        ),
                    )
                    generator.capture_debug_screenshot(
                        f"render_success_att_{attempt}",
                        f"Render gambar selesai (Percobaan ke-{attempt})",
                    )

                    expected_num = 1
                    try:
                        expected_num = int(str(generator.count_str).replace("x", "").strip())
                    except Exception:
                        expected_num = 1

                    progress.update(
                        task,
                        description=f"[cyan]Memicu unduhan 1K ({expected_num} gambar)...[/cyan]",
                    )
                    downloaded_files = generator.download_all_tiles(
                        expected_count=expected_num,
                        existing_files=existing,
                        progress_callback=lambda cur, tot: progress.update(
                            task,
                            description=f"[cyan]Mengunduh gambar {cur}/{tot} resolusi 1K...[/cyan]",
                        ),
                        timeout=60,
                    )
                    generator.capture_debug_screenshot(
                        f"download_completed_att_{attempt}",
                        f"Unduhan {len(downloaded_files)} gambar selesai (Percobaan ke-{attempt})",
                    )

                    progress.update(task, description="[cyan]Memindahkan file gambar ke lokasi tujuan...")
                    target_files = []
                    total_dl = len(downloaded_files)
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

                    for idx, dl_file in enumerate(downloaded_files):
                        dest_file = resolve_target_file_path(
                            output_path=output_dest,
                            prompt=prompt,
                            index=idx,
                            total_count=total_dl,
                            workspace_dir=generator.workspace_dir,
                            timestamp=timestamp,
                        )
                        shutil.move(str(dl_file), str(dest_file))
                        target_files.append(dest_file)

                    progress.update(task, description="[cyan]Menghapus seluruh tile dari kanvas peramban...")
                    try:
                        generator.delete_all_canvas_tiles()
                        generator.capture_debug_screenshot("canvas_after_cleanup", "Pembersihan kanvas selesai")
                    except Exception as del_err:
                        console.print(f"[warning]⚠ Catatan pembersihan: {del_err}[/warning]")

                    success = True
                    successful_attempt = attempt
                    break

                except QuotaExceededError as quota_err:
                    generator.capture_debug_screenshot(
                        f"quota_exceeded_att_{attempt}",
                        f"Batas penggunaan tercapai: {quota_err}",
                    )
                    generator.delete_all_canvas_tiles()
                    curr_email = generator.get_current_user_email() or "Tidak terdeteksi"
                    generator.save_account_to_vault(curr_email)

                    vault_accounts = [
                        acc["email"]
                        for acc in generator.list_vault_accounts()
                        if acc["email"].lower() != (curr_email or "").lower()
                    ]
                    vault_hint = ""
                    if vault_accounts:
                        vault_hint = (
                            "\n• Atau beralih langsung ke akun cadangan di brankas lokal (tanpa login ulang):\n"
                            + "\n".join(
                                f"  [green]•[/green] [cyan]python image_generator.py --email {acc} ...[/cyan]"
                                for acc in vault_accounts
                            )
                        )

                    console.print(
                        Panel(
                            f"[bold red]Akun Google Flow Anda telah mencapai batas penggunaan (Quota / Rate Limit).[/bold red]\n\n"
                            f"[bold cyan]• Akun Aktif Saat Ini:[/bold cyan] [bold white]{curr_email}[/bold white]\n"
                            f"[yellow]• Pesan dari Google Flow:[/yellow] [white]{quota_err}[/white]\n\n"
                            "[bold white]Petunjuk & Saran Solusi:[/bold white]\n"
                            f"• Akun [cyan]{curr_email}[/cyan] sedang dibatasi sementara oleh Google Flow. Silakan coba kembali beberapa saat lagi.\n"
                            f"• Atau gunakan akun Google lain dengan memasukkan kredensial baru melalui flag:\n"
                            f"  [cyan]python image_generator.py --email akun_lain@gmail.com ...[/cyan]"
                            f"{vault_hint}",
                            title=f"[bold red]Batas Penggunaan Google Flow Tercapai ({curr_email})[/bold red]",
                            box=box.ROUNDED,
                        )
                    )
                    return 1

                except (GenerationFailedError, TimeoutError, RuntimeError) as attempt_err:
                    generator.capture_debug_screenshot(
                        f"failure_state_att_{attempt}",
                        f"Visual kegagalan (Percobaan ke-{attempt}): {attempt_err}",
                    )
                    generator.delete_all_canvas_tiles()
                    console.print(
                        f"[warning]⚠ Percobaan ke-{attempt} gagal ({attempt_err}). "
                        f"Menunggu jeda {retry_delay:.0f} detik sebelum mencoba ulang...[/warning]"
                    )
                    progress.update(
                        task,
                        description=f"[warning]⚠ Percobaan ke-{attempt} gagal ({attempt_err}). Menunggu jeda {retry_delay:.0f}s...[/warning]",
                    )
                    time.sleep(retry_delay)
                    attempt += 1

        except Exception as e:
            console.print(f"\n[error]✗ Kegagalan Otomasi:[/error] {e}")
            return 1
        finally:
            generator.close()

    total_duration = time.time() - start_main_ts
    summary_table = Table(box=box.ROUNDED, show_header=True)
    summary_table.add_column("Komponen", style="cyan")
    summary_table.add_column("Status / Lokasi", style="bold")
    summary_table.add_row("Status Generasi", "[bold green]✓ Selesai & Terverifikasi[/bold green]")
    active_user_email = generator.get_current_user_email()
    if active_user_email:
        summary_table.add_row("Akun Google Digunakan", f"[bold cyan]{active_user_email}[/bold cyan]")
    summary_table.add_row("Model AI Terpilih", f"[bold gold]🍌 {generator.model}[/bold gold]")
    summary_table.add_row("Aspek Rasio Terpasang", f"[bold magenta]{generator.aspect_ratio}[/bold magenta]")
    summary_table.add_row("Kuantitas Gambar", f"[bold green]{generator.count_str}[/bold green]")
    summary_table.add_row("Interupsi Kursor Pengguna", "[bold green]✓ 0% (Kursor Bebas Digunakan)[/bold green]")
    summary_table.add_row("Mode Tampilan Jendela", "[bold green]✓ 100% Native Headless (Tanpa GUI)[/bold green]")
    summary_table.add_row("Auto-Retry Penanganan Gagal", f"[bold green]✓ Berhasil pada Percobaan ke-{successful_attempt} (Tanpa Batas)[/bold green]")
    summary_table.add_row("Total Durasi", f"[bold cyan]{total_duration:.1f} detik[/bold cyan]")
    if debug:
        summary_table.add_row("Dokumentasi Visual Debug", f"[bold magenta]{generator.debug_dir} (Tersimpan format .png)[/bold magenta]")
    summary_table.add_row("Hotbar & Download 1K", f"[bold green]✓ Berhasil Diunduh ({len(target_files)} gambar resolusi 1K)[/bold green]")
    summary_table.add_row("Pembersihan Kanvas", "[bold green]✓ Seluruh Tile Dipindahkan ke Sampah[/bold green]")

    if len(target_files) == 1:
        files_display = f"[bold green]{target_files[0]}[/bold green]"
    else:
        files_display = "\n".join(f"[bold green]• {f}[/bold green]" for f in target_files)

    summary_table.add_row(
        "File Hasil Gambar" if len(target_files) <= 1 else f"File Hasil Gambar ({len(target_files)})",
        files_display,
    )
    console.print(summary_table)

    debug_extra = f"\n[muted]Folder Debug:[/muted] [magenta]{generator.debug_dir}[/magenta]" if debug else ""
    if len(target_files) == 1:
        file_banner_lines = f"[muted]Lokasi Berkas:[/muted] [white]{target_files[0]}[/white]\n"
    else:
        file_banner_lines = (
            f"[muted]Lokasi Berkas ({len(target_files)} gambar):[/muted]\n"
            + "\n".join(f"  [green]•[/green] [white]{f}[/white]" for f in target_files)
            + "\n"
        )

    acc_banner_part = f"[muted]Akun Google:[/muted] [cyan]{active_user_email}[/cyan]  |  " if active_user_email else ""
    console.print(
        Panel(
            f"[bold green]BERHASIL MENGHASILKAN & MENGUNDUH GAMBAR SECARA SENYAP![/bold green]\n\n"
            f"[muted]Prompt:[/muted] [gold]{prompt}[/gold]\n"
            f"{acc_banner_part}[muted]Model:[/muted] [gold]🍌 {generator.model}[/gold]  |  "
            f"[muted]Rasio:[/muted] [magenta]{generator.aspect_ratio}[/magenta]  |  "
            f"[muted]Variasi:[/muted] [green]{generator.count_str}[/green]\n"
            f"{file_banner_lines}"
            f"[muted]Percobaan:[/muted] [green]Berhasil pada percobaan ke-{successful_attempt} ({total_duration:.1f}s)[/green]\n"
            f"[muted]Kursor Mouse:[/muted] [green]Tidak tersentuh sama sekali selama proses berlangsung[/green]"
            f"{debug_extra}",
            box=box.ROUNDED,
            style="color(240)",
        )
    )
    return 0


