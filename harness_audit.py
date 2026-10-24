"""QA AUTOMATION & BROWSER FINGERPRINT AUDIT HARNESS.

Harness pengujian otomatis menyeluruh untuk mengaudit jejak otomasi dan fingerprinting
peramban pada 15 situs benchmark bot detection terkemuka.
Menyimpan hasil tangkapan layar (screenshot full-page), data JSON terstruktur,
dan laporan perbandingan multi-run di direktori /reports/<run_id>/.
"""

import argparse
import datetime
import json
import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

console = Console()

WORKSPACE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = WORKSPACE_DIR / "reports"
PROFILE_DIR = WORKSPACE_DIR / "browser_profile"


# ==============================================================================
# DAFTAR SITUS UJI BENCHMARK DETEKSI BOT & FINGERPRINTING
# ==============================================================================
TEST_SITES = [
    {
        "id": "sannysoft",
        "category": "bot_detection",
        "name": "SannySoft Bot Test",
        "url": "https://bot.sannysoft.com",
        "wait_seconds": 6,
    },
    {
        "id": "antoinevastel_headless",
        "category": "bot_detection",
        "name": "Antoine Vastel AreYouHeadless",
        "url": "https://arh.antoinevastel.com/bots/areyouheadless",
        "wait_seconds": 5,
    },
    {
        "id": "rebrowser_bot_detector",
        "category": "bot_detection",
        "name": "Rebrowser Bot Detector",
        "url": "https://bot-detector.rebrowser.net",
        "wait_seconds": 8,
    },
    {
        "id": "browserscan_bot",
        "category": "bot_detection",
        "name": "BrowserScan Bot Detection",
        "url": "https://www.browserscan.net/id/bot-detection",
        "wait_seconds": 12,
    },
    {
        "id": "deviceandbrowserinfo",
        "category": "bot_detection",
        "name": "Device & Browser Info (Are You a Bot)",
        "url": "https://deviceandbrowserinfo.com/are_you_a_bot",
        "wait_seconds": 10,
    },
    {
        "id": "simon_frey_bottest",
        "category": "bot_detection",
        "name": "Simon Frey Bot Test",
        "url": "https://simon-frey.com/bottest/",
        "wait_seconds": 6,
    },
    {
        "id": "incolumitas_bot",
        "category": "bot_detection",
        "name": "Incolumitas Bot Test",
        "url": "https://bot.incolumitas.com",
        "wait_seconds": 10,
    },
    {
        "id": "ipfighter_bot",
        "category": "bot_detection",
        "name": "IP Fighter Bot Detection",
        "url": "https://ipfighter.com/bot-detection",
        "wait_seconds": 8,
    },
    {
        "id": "send_win_bot",
        "category": "bot_detection",
        "name": "Send.win Bot Detection Test",
        "url": "https://send.win/tools/bot-detection-test/",
        "wait_seconds": 8,
    },
    {
        "id": "apivoid_bot",
        "category": "bot_detection",
        "name": "APIVoid Bot Detection Test",
        "url": "https://www.apivoid.com/tools/bot-detection-test/",
        "wait_seconds": 8,
    },
    {
        "id": "creepjs",
        "category": "fingerprint",
        "name": "CreepJS Deep Fingerprinting",
        "url": "https://abrahamjuliot.github.io/creepjs/",
        "wait_seconds": 15,
    },
    {
        "id": "pixelscan",
        "category": "fingerprint",
        "name": "Pixelscan Fingerprint Consistency",
        "url": "https://pixelscan.net",
        "wait_seconds": 12,
    },
    {
        "id": "browserleaks_canvas",
        "category": "fingerprint",
        "name": "BrowserLeaks (Canvas & Fingerprint)",
        "url": "https://browserleaks.com/canvas",
        "wait_seconds": 7,
    },
    {
        "id": "browserleaks_webgl",
        "category": "fingerprint",
        "name": "BrowserLeaks WebGL Test",
        "url": "https://browserleaks.com/webgl",
        "wait_seconds": 7,
    },
    {
        "id": "browserleaks_webrtc",
        "category": "leak",
        "name": "BrowserLeaks WebRTC Leak Test",
        "url": "https://browserleaks.com/webrtc",
        "wait_seconds": 7,
    },
    {
        "id": "coveryourtracks",
        "category": "fingerprint",
        "name": "EFF Cover Your Tracks",
        "url": "https://coveryourtracks.eff.org",
        "wait_seconds": 10,
    },
    {
        "id": "amiunique",
        "category": "fingerprint",
        "name": "AmIUnique Fingerprint Test",
        "url": "https://amiunique.org/fingerprint",
        "wait_seconds": 10,
    },
]


# ==============================================================================
# MARIONETTE DRIVER IMPORT ATAU FALLBACK
# ==============================================================================
try:
    from image_generator import MarionetteDriver
except ImportError:
    # Minimal Marionette Driver jika image_generator tidak langsung terimpor
    class MarionetteDriver:  # type: ignore
        def __init__(self, host: str = "127.0.0.1", port: int = 2828):
            self.host = host
            self.port = port
            self.sock: socket.socket | None = None
            self.msg_id = 0
            self.session_id: str | None = None

        def is_port_open(self, timeout: float = 1.0) -> bool:
            try:
                with socket.create_connection((self.host, self.port), timeout=timeout):
                    return True
            except OSError:
                return False

        def connect(self, timeout: float = 15.0) -> None:
            self.sock = socket.create_connection((self.host, self.port), timeout=timeout)
            self._read_response()
            res = self._send_command("WebDriver:NewSession", {"capabilities": {}})
            self.session_id = res.get("sessionId")

        def _send_command(self, name: str, params: dict | None = None) -> dict:
            self.msg_id += 1
            payload = [0, self.msg_id, name, params or {}]
            raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.sock.sendall(f"{len(raw)}:{raw.decode('latin-1')}".encode("latin-1"))
            return self._read_response()

        def _read_response(self) -> dict:
            buf = bytearray()
            while b":" not in buf:
                chunk = self.sock.recv(1)
                if not chunk:
                    raise ConnectionResetError("Soket Marionette terputus.")
                buf.extend(chunk)
            length_str = buf.split(b":", 1)[0].decode("ascii")
            length = int(length_str)
            data = bytearray()
            while len(data) < length:
                chunk = self.sock.recv(min(length - len(data), 65536))
                if not chunk:
                    raise ConnectionResetError("Soket terputus saat membaca data.")
                data.extend(chunk)
            msg = json.loads(data.decode("utf-8"))
            if isinstance(msg, list) and len(msg) >= 4 and msg[2] is not None:
                raise RuntimeError(f"Marionette error: {msg[2]}")
            return msg[3] if isinstance(msg, list) and len(msg) >= 4 else {}

        def navigate(self, url: str) -> None:
            self._send_command("WebDriver:Navigate", {"url": url})

        def execute_script(self, script: str, args: list | None = None) -> object:
            res = self._send_command(
                "WebDriver:ExecuteScript",
                {"script": script, "args": args or [], "newSandbox": False},
            )
            return res.get("value")

        def take_screenshot(self, full: bool = False) -> bytes:
            import base64
            res = self._send_command("WebDriver:TakeScreenshot", {"full": full})
            return base64.b64decode(res.get("value", ""))

        def close(self) -> None:
            try:
                if self.sock:
                    self.sock.close()
            except Exception:
                pass


# ==============================================================================
# AUDIT HARNESS RUNNER CLASS
# ==============================================================================
class AuditHarness:
    """Pengontrol orkestrasi pengujian jejak otomasi dan ekstraksi metrik."""

    def __init__(self, profile_dir: Path | None = None, headless: bool = True):
        self.profile_dir = profile_dir or PROFILE_DIR
        self.headless = headless
        self.driver = MarionetteDriver()
        self.proc: subprocess.Popen | None = None
        self.ff_bin = self._find_ff_binary()

    def _find_ff_binary(self) -> Path:
        candidates = [
            WORKSPACE_DIR / "firefox_portable" / "App" / "Firefox64" / "firefox.exe",
            Path(r"D:\FirefoxPortable\App\Firefox64\firefox.exe"),
            Path(r"D:\FirefoxPortable\App\Firefox\firefox.exe"),
        ]
        for c in candidates:
            if c.exists():
                return c.resolve()
        raise FileNotFoundError("Biner Firefox Portable tidak ditemukan. Jalankan setup_browser.py terlebih dahulu.")

    def start_browser(self) -> None:
        """Meluncurkan proses Firefox Portable dan menghubungkan Marionette driver."""
        # Pastikan tidak ada proses headless atau lock file usang
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        lock = self.profile_dir / "parent.lock"
        if lock.exists():
            try:
                lock.unlink()
            except Exception:
                pass

        env = os.environ.copy()
        env["MOZ_CRASHREPORTER_DISABLE"] = "1"
        env["MOZ_CRASHREPORTER_NO_REPORT"] = "1"

        cmd = [
            str(self.ff_bin),
            "-no-remote",
            "-marionette",
            "-profile",
            str(self.profile_dir),
        ]
        if self.headless:
            cmd.insert(2, "-headless")

        console.print(f"[info]ℹ Meluncurkan Firefox ({'Headless' if self.headless else 'GUI'}):[/info] [dim]{' '.join(cmd)}[/dim]")
        self.proc = subprocess.Popen(cmd, env=env)

        # Tunggu port 2828 siap
        connected = False
        for _ in range(40):
            time.sleep(0.5)
            if self.driver.is_port_open(timeout=0.5):
                connected = True
                break

        if not connected:
            raise TimeoutError("Gagal terhubung ke port Marionette 2828 peramban.")

        self.driver.connect()
        console.print("[success]✓ Berhasil terhubung ke engine Firefox Marionette[/success]")

    def close(self) -> None:
        """Menghentikan sesi driver dan mematikan proses peramban."""
        self.driver.close()
        if self.proc is not None:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=5)
            except Exception:
                try:
                    self.proc.kill()
                except Exception:
                    pass
            self.proc = None

        # Bersihkan parent.lock
        lock = self.profile_dir / "parent.lock"
        if lock.exists():
            try:
                lock.unlink()
            except Exception:
                pass

    def run_single_site(self, site: dict, output_dir: Path) -> dict:
        """Menjalankan pengujian pada satu situs benchmark dan merekam artefaknya.

        Args:
            site (dict): Metadata situs uji.
            output_dir (Path): Direktori output laporan run saat ini.

        Returns:
            dict: Ringkasan hasil audit per situs.
        """
        site_id = site["id"]
        url = site["url"]
        wait_sec = site.get("wait_seconds", 8)

        result: dict = {
            "id": site_id,
            "name": site["name"],
            "url": url,
            "category": site["category"],
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "pending",
            "score": None,
            "failed_signals": [],
            "notes": "",
            "raw_title": "",
            "screenshot_path": None,
        }

        try:
            self.driver.navigate(url)
            time.sleep(wait_sec)

            # 1. Ambil screenshot
            screenshot_file = output_dir / f"{site_id}.png"
            try:
                png_bytes = self.driver.take_screenshot(full=False)
                screenshot_file.write_bytes(png_bytes)
                result["screenshot_path"] = str(screenshot_file.relative_to(WORKSPACE_DIR))
            except Exception as ss_err:
                result["notes"] += f"Screenshot error: {ss_err}; "

            # 2. Ambil data DOM & evaluasi sinyal spesifik
            eval_script = """
            return {
                title: document.title || '',
                bodyText: (document.body ? document.body.innerText : '').slice(0, 5000),
                webdriver: navigator.webdriver,
                userAgent: navigator.userAgent,
                languages: navigator.languages,
                hardwareConcurrency: navigator.hardwareConcurrency,
                platform: navigator.platform
            };
            """
            eval_data = self.driver.execute_script(eval_script) or {}
            result["raw_title"] = eval_data.get("title", "")
            body_text = eval_data.get("bodyText", "")

            # 3. Analisa spesifik per situs
            failed_signals = []

            # Sinyal universal navigator.webdriver
            if eval_data.get("webdriver") is True:
                failed_signals.append("navigator.webdriver == true")

            if site_id == "sannysoft":
                # Cari baris-baris merah atau gagal di SannySoft
                sanny_analysis = self.driver.execute_script("""
                var fails = [];
                var tables = document.querySelectorAll('table');
                tables.forEach(function(t) {
                    var rows = t.querySelectorAll('tr');
                    rows.forEach(function(r) {
                        var text = r.innerText || '';
                        if (r.classList.contains('failed') || r.classList.contains('result-failed') || text.includes('failed') || r.style.backgroundColor.includes('rgb(255, 0') || r.style.backgroundColor.includes('red')) {
                            fails.push(text.replace(/\\s+/g, ' ').trim());
                        }
                    });
                });
                return fails;
                """) or []
                for f in sanny_analysis:
                    if any(kw in f.lower() for kw in ["webdriver", "chrome", "broken", "phantom", "selenium", "headless", "eval"]):
                        failed_signals.append(f"SannySoft: {f[:60]}")
                result["score"] = f"{len(sanny_analysis)} failed checks"

            elif site_id == "antoinevastel_headless":
                if "you are headless" in body_text.lower():
                    failed_signals.append("TERDETEKSI HEADLESS: 'You are headless'")
                    result["score"] = "HEADLESS DETECTED"
                elif "you are not headless" in body_text.lower():
                    result["score"] = "PASSED (Not Headless)"
                else:
                    result["score"] = "UNCONFIRMED"

            elif site_id == "rebrowser_bot_detector":
                rebrowser_res = self.driver.execute_script("""
                var res = [];
                document.querySelectorAll('div, tr, li').forEach(function(el) {
                    if (el.innerText && (el.innerText.includes('DETECTION:') || el.innerText.includes('DETECTED') || el.innerText.includes('FAILED'))) {
                        res.push(el.innerText.replace(/\\s+/g, ' ').trim());
                    }
                });
                return res.slice(0, 5);
                """) or []
                for r in rebrowser_res:
                    failed_signals.append(f"Rebrowser: {r[:60]}")
                result["score"] = "FLAGS FOUND" if failed_signals else "CLEAN"

            elif site_id == "creepjs":
                # Ekstrak score trust CreepJS jika ada
                creep_info = self.driver.execute_script("""
                var el = document.querySelector('.trust-score') || document.querySelector('.score') || document.querySelector('#fingerprint-data');
                var lies = [];
                document.querySelectorAll('.lies, .alert, .warn').forEach(function(l) {
                    lies.push(l.innerText.replace(/\\s+/g, ' ').trim());
                });
                return {
                    score: el ? el.innerText.trim() : null,
                    lies: lies.slice(0, 5)
                };
                """) or {}
                result["score"] = creep_info.get("score") or "Score in screenshot"
                for lie in creep_info.get("lies", []):
                    failed_signals.append(f"CreepJS Lie: {lie[:60]}")

            elif site_id == "pixelscan":
                if "automated" in body_text.lower() or "bot" in body_text.lower():
                    if "not automated" not in body_text.lower() and "no automation" not in body_text.lower():
                        failed_signals.append("Pixelscan: Potensi terdeteksi automasi")
                result["score"] = "Inspeksi Visual Screenshot"

            elif site_id == "browserscan_bot":
                if "bot terdeteksi" in body_text.lower() or "bot detected" in body_text.lower():
                    failed_signals.append("BrowserScan: Bot terdeteksi")
                    result["score"] = "BOT DETECTED"
                else:
                    result["score"] = "Inspeksi Visual Screenshot"

            else:
                result["score"] = "Inspeksi Visual Screenshot"

            result["failed_signals"] = list(set(failed_signals))
            result["status"] = "failed" if failed_signals else "evaluated"
            result["notes"] = f"Title: {result['raw_title']}"

            # Simpan berkas JSON individual per situs
            site_json_file = output_dir / f"{site_id}.json"
            site_json_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

        except Exception as err:
            result["status"] = "error"
            result["notes"] += f"Eksepsi: {err}"
            console.print(f"[warning]⚠ Kendala pada situs {site_id}: {err}[/warning]")

        return result

    def run_full_suite(self, run_id: str) -> dict:
        """Menjalankan seluruh 15 situs uji dan menyusun rangkuman laporan run.

        Args:
            run_id (str): Identifikasi unik run (misal: 'baseline_run_1').

        Returns:
            dict: Rangkuman lengkap seluruh pengujian run ini.
        """
        output_dir = REPORTS_DIR / run_id
        output_dir.mkdir(parents=True, exist_ok=True)

        console.print(
            Panel(
                f"[bold cyan]MEMULAI AUDIT FINGERPRINT HARNESS[/bold cyan]\n"
                f"Run ID    : [yellow]{run_id}[/yellow]\n"
                f"Output Dir: [cyan]{output_dir}[/cyan]\n"
                f"Total Uji : [bold white]{len(TEST_SITES)} situs[/bold white]",
                box=box.ROUNDED,
            )
        )

        self.start_browser()

        summary: dict = {
            "run_id": run_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "browser_executable": str(self.ff_bin),
            "headless": self.headless,
            "total_sites": len(TEST_SITES),
            "results": {},
        }

        with Progress(
            SpinnerColumn(),
            TextColumn("[cyan]{task.description}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            for idx, site in enumerate(TEST_SITES, 1):
                task = progress.add_task(f"[{idx}/{len(TEST_SITES)}] Menguji {site['name']}...", total=None)
                site_res = self.run_single_site(site, output_dir)
                summary["results"][site["id"]] = site_res
                progress.remove_task(task)

        # Simpan ringkasan global run
        summary_file = output_dir / "summary.json"
        summary_file.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

        self.close()
        console.print(f"[success]✓ Audit harness run {run_id} selesai. Laporan tersimpan di:[/success] [cyan]{output_dir}[/cyan]")
        return summary


def run_baseline_cycle(iterations: int = 3) -> list[dict]:
    """Menjalankan siklus audit baseline sebanyak N iterasi berturut-turut.

    Args:
        iterations (int): Jumlah pengulangan run (default: 3).

    Returns:
        list[dict]: Kumpulan hasil dari setiap iterasi run.
    """
    all_runs = []
    for i in range(1, iterations + 1):
        run_id = f"baseline_run_{i}"
        console.print(f"\n[bold yellow]======================================================================[/bold yellow]")
        console.print(f"[bold yellow]EKSEKUSI SIKLUS BASELINE KE-{i} DARI {iterations}[/bold yellow]")
        console.print(f"[bold yellow]======================================================================[/bold yellow]\n")
        harness = AuditHarness(headless=True)
        try:
            run_data = harness.run_full_suite(run_id=run_id)
            all_runs.append(run_data)
        finally:
            harness.close()
        if i < iterations:
            console.print("[dim]Jeda 5 detik sebelum iterasi berikutnya...[/dim]")
            time.sleep(5)
    return all_runs


def generate_baseline_markdown_table(runs: list[dict], output_file: Path) -> str:
    """Menyusun tabel markdown komparatif hasil baseline dari seluruh iterasi.

    Args:
        runs (list[dict]): Data hasil run.
        output_file (Path): Lokasi berkas markdown tujuan.

    Returns:
        str: Isi tabel markdown.
    """
    lines = [
        "# TABEL BASELINE AUDIT JEJAK OTOMASI & FINGERPRINTING",
        "",
        f"*Tanggal Pelaksanaan:* {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"*Total Iterasi:* {len(runs)}x Run berturut-turut",
        "*Konfigurasi:* Mozilla Firefox Portable (Baseline Headless, marionette.port=2828)",
        "",
        "| No | Situs Uji | Kategori | Skor / Status | Sinyal Gagal / Terdeteksi | Catatan & Variasi |",
        "| :---: | :--- | :---: | :---: | :--- | :--- |",
    ]

    # Gabungkan data per situs lintas run
    for idx, site in enumerate(TEST_SITES, 1):
        site_id = site["id"]
        site_name = site["name"]
        cat = site["category"]

        # Kumpulkan sinyal gagal dari semua run
        aggregated_fails = set()
        scores = []
        for r in runs:
            s_data = r.get("results", {}).get(site_id, {})
            for f in s_data.get("failed_signals", []):
                aggregated_fails.add(f)
            if s_data.get("score"):
                scores.append(str(s_data["score"]))

        score_display = " / ".join(list(set(scores))) if scores else "N/A"
        fail_display = "<br>".join([f"`{f}`" for f in sorted(aggregated_fails)]) if aggregated_fails else "*Tidak ada sinyal eksplisit*"
        notes = "Konsisten 3x" if len(set(scores)) <= 1 else f"Bervariasi: {', '.join(scores)}"

        lines.append(f"| {idx} | [{site_name}]({site['url']}) | {cat} | {score_display} | {fail_display} | {notes} |")

    lines.append("")
    md_content = "\n".join(lines)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(md_content, encoding="utf-8")
    return md_content


def main() -> int:
    parser = argparse.ArgumentParser(description="QA Automation Fingerprint Audit Harness.")
    parser.add_argument("--iterations", type=int, default=3, help="Jumlah iterasi run baseline (default: 3)")
    parser.add_argument("--run-id", type=str, default=None, help="Jalankan single run dengan custom ID")
    parser.add_argument("--site", type=str, default=None, help="Hanya uji satu situs spesifik berdasarkan ID")

    args = parser.parse_args()

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    if args.site:
        target_site = next((s for s in TEST_SITES if s["id"] == args.site), None)
        if not target_site:
            console.print(f"[error]Situs dengan ID '{args.site}' tidak ditemukan.[/error]")
            return 1
        harness = AuditHarness(headless=True)
        out_dir = REPORTS_DIR / (args.run_id or "test_single")
        out_dir.mkdir(parents=True, exist_ok=True)
        try:
            harness.start_browser()
            res = harness.run_single_site(target_site, out_dir)
            console.print(f"[success]Hasil Uji {target_site['name']}:[/success] {res}")
        finally:
            harness.close()
        return 0

    if args.run_id:
        harness = AuditHarness(headless=True)
        try:
            harness.run_full_suite(run_id=args.run_id)
        finally:
            harness.close()
        return 0

    console.print(f"[info]Memulai pengujian baseline {args.iterations}x run berturut-turut...[/info]")
    runs = run_baseline_cycle(iterations=args.iterations)

    report_md_file = REPORTS_DIR / "BASELINE_REPORT.md"
    generate_baseline_markdown_table(runs, report_md_file)

    console.print(Panel(f"[bold green]SELURUH SIKLUS BASELINE SELESAI![/bold green]\nLaporan Markdown: [cyan]{report_md_file}[/cyan]", box=box.ROUNDED))
    return 0


if __name__ == "__main__":
    sys.exit(main())
