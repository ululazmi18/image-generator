"""SETUP BROWSER CLI — AUTOMATED FIREFOX PORTABLE BOOTSTRAPPER.

Modul ini bertanggung jawab mengunduh, mengekstrak, dan mengonfigurasi
Mozilla Firefox Portable Edition secara otomatis dari baris perintah (CLI),
memungkinkan proyek untuk dijalankan dari awal (clean install) di mesin mana pun
saat di-clone dari repositori GitHub.
"""

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import requests
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from rich.table import Table

console = Console()

WORKSPACE_DIR = Path(__file__).resolve().parent
DEFAULT_PORTABLE_DIR = WORKSPACE_DIR / "firefox_portable"
DEFAULT_PROFILE_DIR = WORKSPACE_DIR / "browser_profile"
FALLBACK_SYSTEM_FF = Path(r"D:\FirefoxPortable\App\Firefox64\firefox.exe")

OFFICIAL_DOWNLOAD_URL = (
    "https://download2.portableapps.com/portableapps/FirefoxPortable/FirefoxPortable_158.0_English.paf.exe"
)


def get_firefox_executable(portable_dir: Path | None = None) -> Path | None:
    """Mencari jalur berkas firefox.exe portable yang tersedia.

    Args:
        portable_dir (Path | None): Direktori instalasi lokal firefox_portable.

    Returns:
        Path | None: Jalur absolut firefox.exe jika ditemukan, atau None.
    """
    target_dir = portable_dir or DEFAULT_PORTABLE_DIR
    candidates = [
        target_dir / "App" / "Firefox64" / "firefox.exe",
        target_dir / "App" / "Firefox" / "firefox.exe",
        FALLBACK_SYSTEM_FF,
    ]
    for path in candidates:
        if path.exists() and path.is_file():
            return path.resolve()
    return None


def download_file(url: str, dest_path: Path) -> bool:
    """Mengunduh berkas biner dari URL langsung dengan visual progress bar Rich.

    Args:
        url (str): URL sumber pengunduhan.
        dest_path (Path): Jalur berkas lokal tujuan penyimpanan.

    Returns:
        bool: True jika berhasil diunduh dan ukuran valid.
    """
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = dest_path.with_suffix(".downloading")

    console.print(f"[info]ℹ[/info] Menghubungi server CDN: [cyan]{url}[/cyan]")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    try:
        with requests.get(url, headers=headers, stream=True, allow_redirects=True, timeout=30) as resp:
            resp.raise_for_status()
            total_size = int(resp.headers.get("content-length", 0))

            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(bar_width=40),
                DownloadColumn(),
                TransferSpeedColumn(),
                TimeRemainingColumn(),
                console=console,
            ) as progress:
                task = progress.add_task("Mengunduh Firefox Portable...", total=total_size)
                with open(temp_path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=65536):
                        if chunk:
                            f.write(chunk)
                            progress.update(task, advance=len(chunk))

        if temp_path.exists() and temp_path.stat().st_size > 10 * 1024 * 1024:
            if dest_path.exists():
                dest_path.unlink()
            temp_path.rename(dest_path)
            console.print(f"[success]✓ Pengunduhan selesai:[/success] {dest_path.name} ({dest_path.stat().st_size // (1024*1024)} MB)")
            return True
        else:
            console.print("[error]✗ Unduhan tidak lengkap atau ukuran berkas tidak valid.[/error]")
            if temp_path.exists():
                temp_path.unlink()
            return False

    except Exception as err:
        console.print(f"[error]✗ Galat saat mengunduh berkas:[/error] {err}")
        if temp_path.exists():
            temp_path.unlink()
        return False


def install_portable_package(installer_path: Path, target_dir: Path) -> bool:
    """Mengekstrak paket instalasi PortableApps (.paf.exe) secara senyap tanpa dialog GUI.

    Args:
        installer_path (Path): Lokasi berkas installer .paf.exe.
        target_dir (Path): Direktori tujuan instalasi.

    Returns:
        bool: True jika biner firefox.exe berhasil terpasang di target.
    """
    console.print(f"[info]ℹ[/info] Mengekstrak paket instalasi ke: [cyan]{target_dir}[/cyan]...")
    target_dir.mkdir(parents=True, exist_ok=True)

    # Flag NSIS PortableApps: /S = Silent, /D=<path> = Directory tujuan (tanpa tanda kutip)
    cmd = [str(installer_path.resolve()), "/S", f"/D={target_dir.resolve()}"]

    try:
        proc = subprocess.run(cmd, timeout=300, capture_output=True)
        time.sleep(2.0)  # Beri jeda proses ekstraksi I/O Windows selesai
    except Exception as err:
        console.print(f"[error]✗ Kegagalan saat mengeksekusi installer:[/error] {err}")
        return False

    ff_bin = get_firefox_executable(target_dir)
    if ff_bin and ff_bin.exists():
        console.print(f"[success]✓ Firefox Portable berhasil dipasang:[/success] [cyan]{ff_bin}[/cyan]")
        return True
    else:
        console.print(f"[error]✗ Berkas biner firefox.exe tidak ditemukan di {target_dir} pasca-instalasi.[/error]")
        return False


def setup_clean_profile(profile_dir: Path | None = None) -> Path:
    """Menginisialisasi direktori profil peramban terisolasi dengan setelan dasar.

    Args:
        profile_dir (Path | None): Direktori profil peramban.

    Returns:
        Path: Direktori profil yang siap digunakan.
    """
    p_dir = profile_dir or DEFAULT_PROFILE_DIR
    p_dir.mkdir(parents=True, exist_ok=True)

    user_js = p_dir / "user.js"
    base_prefs = """// KONFIGURASI OTOMASI MARIONETTE BASELINE
user_pref("marionette.enabled", true);
user_pref("marionette.port", 2828);
user_pref("dom.webdriver.enabled", false);
user_pref("toolkit.telemetry.enabled", false);
user_pref("toolkit.telemetry.reportingpolicy.firstRun", false);
user_pref("browser.sessionstore.resume_from_crash", false);

// HARDENING WEBRTC & PRIVASI JARINGAN (ITERASI 2)
user_pref("media.peerconnection.enabled", false);
user_pref("media.peerconnection.ice.no_host", true);
user_pref("media.peerconnection.ice.default_address_only", true);
"""
    if not user_js.exists():
        user_js.write_text(base_prefs, encoding="utf-8")
        console.print(f"[success]✓ Berkas profil dasar dibuat:[/success] {user_js}")
    return p_dir


def main() -> int:
    """Fungsi titik masuk CLI bootstrapper browser."""
    parser = argparse.ArgumentParser(
        description="Firefox Portable Automatic Bootstrapper & Environment Provisioner."
    )
    parser.add_argument("--download", action="store_true", help="Paksa download ulang Firefox Portable resmi")
    parser.add_argument("--force", action="store_true", help="Timpa instalasi lama jika sudah ada")
    parser.add_argument("--status", action="store_true", help="Periksa status ketersediaan Firefox Portable saat ini")

    args = parser.parse_args()

    console.print(
        Panel.fit(
            "[bold cyan]FIREFOX PORTABLE BOOTSTRAPPER — IMAGE GENERATOR[/bold cyan]\n"
            "[muted]Otomasi Penyediaan Lingkungan Peramban Mandiri Tanpa Ketergantungan Eksternal[/muted]",
            box=box.ROUNDED,
        )
    )

    current_bin = get_firefox_executable()

    if args.status:
        table = Table(box=box.ROUNDED)
        table.add_column("Komponen", style="cyan")
        table.add_column("Status / Lokasi", style="bold green" if current_bin else "bold red")
        table.add_row("Firefox Portable Biner", str(current_bin) if current_bin else "Belum Terpasang")
        table.add_row("Direktori Profil", str(DEFAULT_PROFILE_DIR))
        console.print(table)
        return 0 if current_bin else 1

    if current_bin and not args.download and not args.force:
        console.print(f"[success]✓ Firefox Portable sudah siap digunakan di:[/success] [cyan]{current_bin}[/cyan]")
        setup_clean_profile()
        return 0

    # Unduh dan pasang
    installer_file = WORKSPACE_DIR / "temp_firefox_installer.paf.exe"
    ok = download_file(OFFICIAL_DOWNLOAD_URL, installer_file)
    if not ok:
        console.print("[error]✗ Gagal mengunduh installer. Periksa koneksi internet Anda.[/error]")
        return 1

    installed = install_portable_package(installer_file, DEFAULT_PORTABLE_DIR)

    # Bersihkan file installer sementara
    if installer_file.exists():
        try:
            installer_file.unlink()
        except Exception:
            pass

    if installed:
        setup_clean_profile()
        console.print(
            Panel(
                "[bold green]INSTALASI FIREFOX PORTABLE SELESAI & LENGKAP![/bold green]\n"
                f"Lokasi Biner : [cyan]{get_firefox_executable(DEFAULT_PORTABLE_DIR)}[/cyan]\n"
                f"Folder Profil: [cyan]{DEFAULT_PROFILE_DIR}[/cyan]\n"
                "[muted]Siap digunakan untuk otomasi tanpa perlu konfigurasi manual.[/muted]",
                box=box.ROUNDED,
            )
        )
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
