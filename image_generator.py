"""Image Generator — Modul & CLI Otomasi Google Flow.

Dapat dipanggil langsung sebagai CLI atau diimpor sebagai fungsi Python:
    from image_generator import generate_image
    output_path = generate_image("gambar produk hidup", output_dir="hasil_gambar")
"""

import datetime
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

# Standar encoding UTF-8 untuk terminal Windows
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.prompt import Prompt
from rich.table import Table
from rich.theme import Theme

CUSTOM_THEME = Theme(
    {
        "info": "cyan",
        "success": "bold green",
        "warning": "bold yellow",
        "error": "bold red",
        "accent": "bold magenta",
        "muted": "dim white",
        "gold": "bold yellow",
        "brand": "bold color(208)",
    }
)
console = Console(theme=CUSTOM_THEME)

# ==============================================================================
# XPATH DEFINITIONS DARI SPESIFIKASI PENGGUNA
# ==============================================================================
XPATH_PROMPT_INPUT = (
    "/html/body/aisandbox-root/main/flow-project-shell/flow-project-page/div[2]/"
    "flow-project-sidenav-container/mat-sidenav-container/mat-sidenav-content/div/"
    "flow-prompt-box/flow-prompt-box-instruction-card-wrapper/div/div/div/"
    "flow-base-prompt-box/div/div[1]/flow-rich-text-editor/div/div/p"
)

XPATH_GENERATE_BUTTON = (
    "/html/body/aisandbox-root/main/flow-project-shell/flow-project-page/div[2]/"
    "flow-project-sidenav-container/mat-sidenav-container/mat-sidenav-content/div/"
    "flow-prompt-box/flow-prompt-box-instruction-card-wrapper/div/div/div/"
    "flow-base-prompt-box/div/div[2]/div/flow-generate-icon-button/button/span[2]"
)

XPATH_TILE_CONTAINER = (
    "/html/body/aisandbox-root/main/flow-project-shell/flow-project-page/div/"
    "flow-project-sidenav-container/mat-sidenav-container/mat-sidenav-content/div/div/div/"
    "cdk-virtual-scroll-viewport/div[1]/div[1]/div/flow-grid-tile-container[1]"
)

XPATH_HOTBAR_ICON = (
    "/html/body/aisandbox-root/main/flow-project-shell/flow-project-page/div/"
    "flow-project-sidenav-container/mat-sidenav-container/mat-sidenav-content/div/div/div/"
    "cdk-virtual-scroll-viewport/div[1]/div[1]/div/flow-grid-tile-container[1]/"
    "flow-tile-container/div/flow-image-tile/div/div[2]/div/flow-image-hotbar/"
    "flow-hotbar-container/div/button[3]/mat-icon"
)

XPATH_CONTEXT_MENU_ITEM_5 = (
    "/html/body/div[6]/div/div[2]/div/div/"
    "flow-image-context-menu-items/flow-media-context-menu-items/flow-menu-item[5]"
)

XPATH_SUBMENU_DOWNLOAD_ITEM_2 = (
    "/html/body/div[6]/div[2]/div/div/div/flow-menu-item[2]"
)


# ==============================================================================
# MARIONETTE PROTOCOL CLIENT (NATIVE FIREFOX DRIVER)
# ==============================================================================
class MarionetteDriver:
    """Klien soket native Marionette untuk Firefox Portable."""

    def __init__(self, host: str = "127.0.0.1", port: int = 2828):
        self.host = host
        self.port = port
        self.sock: socket.socket | None = None
        self.msg_id = 0
        self.session_id: str | None = None

    def is_port_open(self, timeout: float = 0.8) -> bool:
        """Memeriksa ketersediaan port Marionette."""
        try:
            with socket.create_connection((self.host, self.port), timeout=timeout):
                return True
        except (OSError, socket.timeout):
            return False

    def connect(self, timeout: float = 5.0) -> str:
        """Menghubungkan ke soket Marionette dan membuka sesi baru."""
        self.sock = socket.create_connection((self.host, self.port), timeout=timeout)
        hs_len = b""
        while True:
            ch = self.sock.recv(1)
            if ch == b":":
                break
            hs_len += ch
        self.sock.recv(int(hs_len.decode("ascii")))

        resp = self.send("WebDriver:NewSession", {})
        self.session_id = resp.get("sessionId")
        self.send("Marionette:SetContext", {"value": "content"})
        return self.session_id or ""

    def send(self, method: str, params: dict | None = None) -> any:
        """Mengirim pesan terenkapsulasi wire protocol ke Marionette."""
        if not self.sock:
            raise ConnectionError("Soket Marionette belum terhubung.")

        self.msg_id += 1
        payload = json.dumps([0, self.msg_id, method, params or {}])
        wire = f"{len(payload)}:{payload}".encode("utf-8")
        self.sock.sendall(wire)

        len_str = b""
        while True:
            ch = self.sock.recv(1)
            if ch == b":":
                break
            len_str += ch
        length = int(len_str.decode("ascii"))

        data = b""
        while len(data) < length:
            chunk = self.sock.recv(length - len(data))
            if not chunk:
                raise ConnectionError("Soket terputus saat membaca respons.")
            data += chunk

        parsed = json.loads(data.decode("utf-8"))
        if parsed[2] is not None:
            raise RuntimeError(f"Galat Marionette pada {method}: {parsed[2]}")
        return parsed[3]

    def execute_script(self, script: str, args: list | None = None) -> any:
        """Mengeksekusi JavaScript di halaman aktif."""
        res = self.send(
            "WebDriver:ExecuteScript",
            {"script": script, "args": args or []},
        )
        if isinstance(res, dict) and "value" in res:
            return res["value"]
        return res

    def get_window_handles(self) -> list[str]:
        """Mengambil seluruh handle tab/jendela peramban."""
        handles = self.send("WebDriver:GetWindowHandles")
        return handles if isinstance(handles, list) else []

    def switch_to_window(self, handle: str) -> None:
        """Beralih ke tab/jendela tertentu."""
        self.send("WebDriver:SwitchToWindow", {"handle": handle})

    def close(self) -> None:
        """Menutup koneksi soket."""
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None


# ==============================================================================
# IMAGE GENERATOR AUTOMATION CONTROLLER
# ==============================================================================
class ImageGenerator:
    """Pengontrol utama otomasi Google Flow Image Generator."""

    def __init__(self, workspace_dir: Path | None = None):
        if workspace_dir is None:
            self.workspace_dir = Path(__file__).resolve().parent
        else:
            self.workspace_dir = Path(workspace_dir).resolve()

        self.profile_dir = self.workspace_dir / "browser_profile"
        self.ff_bin = Path(r"D:\FirefoxPortable\App\Firefox64\firefox.exe")
        self.download_dir = self._detect_download_dir()
        self.driver = MarionetteDriver()

    def _detect_download_dir(self) -> Path:
        """Mendeteksi direktori unduhan peramban."""
        candidates = [
            Path(r"D:\Downloads"),
            Path.home() / "Downloads",
            self.workspace_dir / "downloads",
        ]
        for c in candidates:
            if c.exists():
                return c
        candidates[0].mkdir(parents=True, exist_ok=True)
        return candidates[0]

    def ensure_browser(self, auto_launch: bool = True) -> None:
        """Memastikan Firefox berjalan dengan Marionette aktif."""
        if self.driver.is_port_open(timeout=0.8):
            return

        lock_file = self.profile_dir / "parent.lock"
        if lock_file.exists():
            console.print(
                Panel(
                    "[warning]⚠ Firefox terdeteksi berjalan tanpa port otomasi Marionette (2828).[/warning]\n"
                    "Silakan tutup jendela Firefox tersebut sekali agar skrip dapat meluncurkannya dengan akses otomasi penuh.",
                    title="[gold]Port Otomasi Belum Aktif[/gold]",
                    box=box.ROUNDED,
                )
            )
            Prompt.ask("[cyan]Tekan Enter setelah menutup jendela Firefox...[/cyan]")

        if auto_launch:
            console.print("[info]ℹ[/info] Meluncurkan peramban dengan profil terisolasi...")
            env = os.environ.copy()
            env["MOZ_CRASHREPORTER_DISABLE"] = "1"
            env["MOZ_CRASHREPORTER_NO_REPORT"] = "1"

            cmd = [str(self.ff_bin), "-no-remote", "-marionette", "-profile", str(self.profile_dir)]
            subprocess.Popen(cmd, env=env)

            opened = False
            for _ in range(30):
                time.sleep(0.5)
                if self.driver.is_port_open(timeout=0.5):
                    opened = True
                    break

            if not opened:
                raise RuntimeError("Gagal terhubung ke port otomasi peramban (2828).")

    def connect(self) -> None:
        """Menghubungkan klien ke peramban."""
        self.driver.connect(timeout=5.0)

    def find_flow_tab(self) -> str:
        """Mencari dan beralih ke tab Google Flow."""
        handles = self.driver.get_window_handles()
        if not handles:
            raise RuntimeError("Tidak ada tab peramban yang terbuka.")

        detection_script = """
        return {
            url: window.location.href,
            title: document.title,
            hasFlow: !!document.querySelector('aisandbox-root, flow-project-shell, flow-prompt-box, flow-rich-text-editor')
        };
        """

        for handle in handles:
            try:
                self.driver.switch_to_window(handle)
                info = self.driver.execute_script(detection_script)
                if not isinstance(info, dict):
                    continue

                url = (info.get("url") or "").lower()
                title = (info.get("title") or "").lower()
                has_flow = info.get("hasFlow")

                if has_flow or "flow" in url or "flow" in title or "aisandbox" in url:
                    return handle
            except Exception:
                continue

        raise RuntimeError("Tab Google Flow tidak ditemukan. Pastikan halaman proyek Google Flow sudah terbuka di peramban.")

    def submit_prompt(self, prompt_text: str) -> bool:
        """Memasukkan teks prompt dan menekan tombol Generate / Enter."""
        script = """
        const inputXpath = arguments[0];
        const buttonXpath = arguments[1];
        const promptText = arguments[2];

        function getByXPath(xpath) {
            try {
                return document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            } catch (e) {
                return null;
            }
        }

        // 1. Cari elemen editor input
        let editorEl = getByXPath(inputXpath);
        if (!editorEl) {
            editorEl = document.querySelector('flow-rich-text-editor div[contenteditable="true"]') ||
                       document.querySelector('flow-rich-text-editor div div p') ||
                       document.querySelector('flow-rich-text-editor p') ||
                       document.querySelector('flow-prompt-box [contenteditable="true"]');
        }

        if (!editorEl) {
            return { success: false, error: 'Elemen input prompt tidak ditemukan.' };
        }

        // 2. Fokus dan isi konten teks
        editorEl.focus();
        const sel = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(editorEl);
        sel.removeAllRanges();
        sel.addRange(range);

        let inserted = document.execCommand('insertText', false, promptText);
        if (!inserted || !editorEl.innerText.includes(promptText.trim())) {
            editorEl.innerText = promptText;
            editorEl.dispatchEvent(new Event('input', { bubbles: true }));
            editorEl.dispatchEvent(new Event('change', { bubbles: true }));
        }

        // 3. Cari tombol generate
        let btnEl = getByXPath(buttonXpath);
        if (!btnEl) {
            btnEl = document.querySelector('flow-generate-icon-button button') ||
                    document.querySelector('flow-generate-icon-button') ||
                    document.querySelector('flow-base-prompt-box button.generate-button') ||
                    document.querySelector('flow-base-prompt-box button[aria-label*="Generate"]');
        }

        // 4. Klik tombol dan dispatch Enter
        if (btnEl) {
            const clickable = btnEl.closest ? (btnEl.closest('button') || btnEl) : btnEl;
            clickable.click();
        }

        editorEl.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }));
        editorEl.dispatchEvent(new KeyboardEvent('keypress', { key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }));
        editorEl.dispatchEvent(new KeyboardEvent('keyup', { key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }));

        return { success: true };
        """
        res = self.driver.execute_script(script, [XPATH_PROMPT_INPUT, XPATH_GENERATE_BUTTON, prompt_text])
        if not isinstance(res, dict) or not res.get("success"):
            raise RuntimeError(f"Gagal memasukkan prompt: {res}")
        return True

    def hover_and_wait_tile(self, timeout: int = 180) -> bool:
        """Memeriksa dan men-hover tile gambar sampai hotbar tombol opsi muncul (tanda selesai)."""
        check_script = """
        const tileXpath = arguments[0];
        const hotbarXpath = arguments[1];

        function getByXPath(xpath) {
            try {
                return document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            } catch (e) {
                return null;
            }
        }

        // 1. Cari Tile Container
        let tileEl = getByXPath(tileXpath);
        if (!tileEl) {
            tileEl = document.querySelector('cdk-virtual-scroll-viewport flow-grid-tile-container') ||
                     document.querySelector('flow-grid-tile-container');
        }

        if (tileEl) {
            // Picu mouse hover event
            tileEl.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true, cancelable: true }));
            tileEl.dispatchEvent(new MouseEvent('mouseover', { bubbles: true, cancelable: true }));
            tileEl.dispatchEvent(new MouseEvent('mousemove', { bubbles: true, cancelable: true }));
        }

        // 2. Periksa apakah Hotbar Button [3] / mat-icon sudah tersedia
        let hotbarEl = getByXPath(hotbarXpath);
        if (!hotbarEl) {
            hotbarEl = document.querySelector('flow-grid-tile-container flow-image-hotbar button:nth-child(3) mat-icon') ||
                       document.querySelector('flow-image-hotbar button:nth-child(3)') ||
                       document.querySelector('flow-image-hotbar button mat-icon[data-mat-icon-name*="more"], flow-image-hotbar button mat-icon');
        }

        return {
            tileFound: !!tileEl,
            hotbarReady: !!hotbarEl
        };
        """

        start_time = time.time()
        while time.time() - start_time < timeout:
            res = self.driver.execute_script(check_script, [XPATH_TILE_CONTAINER, XPATH_HOTBAR_ICON])
            if isinstance(res, dict) and res.get("hotbarReady"):
                return True
            time.sleep(1.5)

        raise TimeoutError(f"Waktu tunggu generasi gambar habis ({timeout} detik). Gambar belum selesai dirender.")

    def click_hotbar_and_download(self, timeout: int = 20) -> bool:
        """Mengeklik hotbar opsi, men-hover menu item 5, lalu mengeklik tombol download."""
        download_script = """
        const hotbarXpath = arguments[0];
        const menu5Xpath = arguments[1];
        const downloadXpath = arguments[2];

        function getByXPath(xpath) {
            try {
                return document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            } catch (e) {
                return null;
            }
        }

        // 1. Klik Hotbar Icon (tombol opsi gambar)
        let hotbarBtn = getByXPath(hotbarXpath);
        if (!hotbarBtn) {
            hotbarBtn = document.querySelector('flow-grid-tile-container flow-image-hotbar button:nth-child(3)') ||
                        document.querySelector('flow-image-hotbar button:nth-child(3)');
        }

        if (!hotbarBtn) {
            return { success: false, step: 'hotbar', error: 'Tombol hotbar tidak ditemukan.' };
        }

        const clickable = hotbarBtn.closest ? (hotbarBtn.closest('button') || hotbarBtn) : hotbarBtn;
        clickable.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true }));
        clickable.click();
        clickable.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true }));

        return { success: true, step: 'hotbar_clicked' };
        """

        # Klik icon hotbar
        res = self.driver.execute_script(download_script, [XPATH_HOTBAR_ICON, XPATH_CONTEXT_MENU_ITEM_5, XPATH_SUBMENU_DOWNLOAD_ITEM_2])
        if not isinstance(res, dict) or not res.get("success"):
            raise RuntimeError(f"Gagal membuka menu opsi hotbar: {res}")

        time.sleep(0.8)

        # 2. Hover menu item 5
        hover_menu_script = """
        const menu5Xpath = arguments[0];
        function getByXPath(xpath) {
            try { return document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue; } catch (e) { return null; }
        }

        let menu5 = getByXPath(menu5Xpath);
        if (!menu5) {
            const allItems = document.querySelectorAll('flow-image-context-menu-items flow-menu-item, flow-media-context-menu-items flow-menu-item');
            if (allItems.length >= 5) {
                menu5 = allItems[4]; // 0-indexed
            }
        }

        if (!menu5) {
            return { success: false, error: 'Menu item 5 tidak ditemukan.' };
        }

        menu5.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true, cancelable: true }));
        menu5.dispatchEvent(new MouseEvent('mouseover', { bubbles: true, cancelable: true }));
        menu5.dispatchEvent(new MouseEvent('mousemove', { bubbles: true, cancelable: true }));
        return { success: true };
        """

        res_hover = self.driver.execute_script(hover_menu_script, [XPATH_CONTEXT_MENU_ITEM_5])
        time.sleep(0.8)

        # 3. Klik tombol download di submenu
        click_download_script = """
        const downloadXpath = arguments[0];
        function getByXPath(xpath) {
            try { return document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue; } catch (e) { return null; }
        }

        let dlItem = getByXPath(downloadXpath);
        if (!dlItem) {
            const overlays = document.querySelectorAll('div.cdk-overlay-pane flow-menu-item, flow-menu-item');
            for (let el of overlays) {
                if ((el.innerText || '').toLowerCase().includes('download') || (el.innerText || '').toLowerCase().includes('unduh')) {
                    dlItem = el;
                    break;
                }
            }
            if (!dlItem && overlays.length >= 2) {
                dlItem = overlays[1];
            }
        }

        if (!dlItem) {
            return { success: false, error: 'Tombol download submenu tidak ditemukan.' };
        }

        dlItem.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true }));
        dlItem.click();
        dlItem.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true }));
        return { success: true };
        """

        res_dl = self.driver.execute_script(click_download_script, [XPATH_SUBMENU_DOWNLOAD_ITEM_2])
        if not isinstance(res_dl, dict) or not res_dl.get("success"):
            raise RuntimeError(f"Gagal mengeklik menu download: {res_dl}")

        return True

    def wait_for_downloaded_file(self, existing_files: set[str], timeout: int = 60) -> Path:
        """Memantau folder download sampai file .jpg baru selesai diunduh."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            current_files = list(self.download_dir.glob("*.jpg")) + list(self.download_dir.glob("*.jpeg"))
            new_files = [f for f in current_files if str(f.resolve()) not in existing_files]

            if new_files:
                latest_file = max(new_files, key=lambda f: f.stat().st_mtime)

                # Pastikan tidak ada file sementara .part
                part_files = list(self.download_dir.glob(f"{latest_file.name}.part"))
                if not part_files:
                    size1 = latest_file.stat().st_size
                    time.sleep(0.5)
                    size2 = latest_file.stat().st_size
                    if size1 == size2 and size1 > 0:
                        return latest_file

            time.sleep(1.0)

        raise TimeoutError(f"File .jpg hasil unduhan tidak terdeteksi di {self.download_dir} dalam {timeout} detik.")

    def close(self) -> None:
        """Menutup koneksi driver."""
        self.driver.close()


# ==============================================================================
# HIGH-LEVEL CALLABLE FUNCTION (UNTUK DIPANGGIL SKRIP LAIN)
# ==============================================================================
def generate_image(
    prompt: str,
    output_path: str | Path | None = None,
    timeout: int = 180,
    auto_launch: bool = True,
) -> Path:
    """Fungsi utama untuk menghasilkan dan mengunduh gambar dari Google Flow.

    Args:
        prompt: Teks deskripsi gambar yang akan digenerate.
        output_path: Jalur folder atau berkas tujuan pemindahan gambar.
                     Jika None, disimpan otomatis di folder 'outputs/' dengan nama slug prompt.
        timeout: Waktu tunggu maksimal generasi gambar (detik).
        auto_launch: Luncurkan Firefox Portable secara otomatis jika belum berjalan.

    Returns:
        Path: Lokasi absolut berkas gambar .jpg yang telah dipindahkan.
    """
    generator = ImageGenerator()

    try:
        generator.ensure_browser(auto_launch=auto_launch)
        generator.connect()

        existing = {str(f.resolve()) for f in list(generator.download_dir.glob("*.jpg")) + list(generator.download_dir.glob("*.jpeg"))}
        generator.find_flow_tab()
        generator.submit_prompt(prompt)
        generator.hover_and_wait_tile(timeout=timeout)
        generator.click_hotbar_and_download()
        downloaded_file = generator.wait_for_downloaded_file(existing_files=existing, timeout=60)

        # Pemindahan berkas yang fleksibel
        if output_path is None:
            dest_dir = generator.workspace_dir / "outputs"
            dest_dir.mkdir(parents=True, exist_ok=True)
            slug = re.sub(r"[^\w\s-]", "", prompt)[:30].strip().replace(" ", "_")
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            target_file = dest_dir / f"{slug}_{timestamp}.jpg"
        else:
            target_path = Path(output_path).resolve()
            if target_path.is_dir() or (not target_path.suffix and not target_path.exists()):
                target_path.mkdir(parents=True, exist_ok=True)
                slug = re.sub(r"[^\w\s-]", "", prompt)[:30].strip().replace(" ", "_")
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                target_file = target_path / f"{slug}_{timestamp}.jpg"
            else:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_file = target_path

        shutil.move(str(downloaded_file), str(target_file))
        return target_file

    finally:
        generator.close()


# ==============================================================================
# CLI PARSER & INTERFACE
# ==============================================================================
def parse_cli_args() -> tuple[str, str | None, int]:
    """Mengekstrak prompt tanpa wajib tanda petik, output path, dan timeout."""
    args = sys.argv[1:]
    output_flags = ["--output", "-o", "--dest", "-d"]
    timeout_flags = ["--timeout", "-t"]
    prompt_flags = ["--prompt", "-p"]

    output_val = None
    timeout_val = 180
    prompt_tokens = []

    i = 0
    while i < len(args):
        arg = args[i]
        if arg in output_flags and i + 1 < len(args):
            output_val = args[i + 1]
            i += 2
        elif arg in timeout_flags and i + 1 < len(args):
            try:
                timeout_val = int(args[i + 1])
            except ValueError:
                pass
            i += 2
        elif arg in prompt_flags:
            i += 1
            while i < len(args):
                if args[i] in output_flags:
                    output_val = args[i + 1] if i + 1 < len(args) else None
                    i += 2
                elif args[i] in timeout_flags:
                    try:
                        timeout_val = int(args[i + 1])
                    except (ValueError, IndexError):
                        pass
                    i += 2
                else:
                    prompt_tokens.append(args[i])
                    i += 1
            break
        else:
            prompt_tokens.append(arg)
            i += 1

    prompt_str = " ".join(prompt_tokens).strip()
    return prompt_str, output_val, timeout_val


def main() -> int:
    console.clear()
    banner = (
        "[brand]IMAGE GENERATOR — GOOGLE FLOW BOT[/brand] [muted]//[/muted] [gold]V2.0 ENTERPRISE[/gold]\n"
        "[muted]Automated Prompt Injection, Hotbar Detection, and Image Downloader[/muted]"
    )
    console.print(Panel(banner, box=box.ROUNDED, style="color(240)"))

    prompt, output_dest, timeout = parse_cli_args()

    if not prompt:
        console.print("[info]ℹ[/info] [dim]Tips: Jalankan `python image_generator.py --prompt gambar produk hidup -o hasil/` tanpa tanda petik.[/dim]\n")
        prompt = Prompt.ask("[cyan]Masukkan Prompt Generasi Gambar[/cyan]")

    if not prompt.strip():
        console.print("[error]✗[/error] Prompt tidak boleh kosong.")
        return 1

    target_display = str(Path(output_dest).resolve()) if output_dest else str(Path("outputs").resolve())

    table = Table(box=box.ROUNDED, show_header=False, expand=True)
    table.add_column("Parameter", style="cyan", width=22)
    table.add_column("Nilai", style="bold white")
    table.add_row("Prompt Teks", f"[gold]{prompt}[/gold]")
    table.add_row("Target Pemindahan", f"[accent]{target_display}[/accent]")
    table.add_row("Batas Waktu (Timeout)", f"{timeout} detik")
    console.print(table)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Menjalankan otomasi generasi gambar...", total=None)

        try:
            progress.update(task, description="[cyan]Memverifikasi peramban & tab Google Flow...")
            generator = ImageGenerator()
            generator.ensure_browser()
            generator.connect()

            existing = {str(f.resolve()) for f in list(generator.download_dir.glob("*.jpg")) + list(generator.download_dir.glob("*.jpeg"))}
            generator.find_flow_tab()

            progress.update(task, description="[cyan]Mengirim prompt & memicu eksekusi...")
            generator.submit_prompt(prompt)

            progress.update(task, description="[gold]Menunggu render gambar selesai (memantau hotbar tile)...")
            generator.hover_and_wait_tile(timeout=timeout)

            progress.update(task, description="[cyan]Mengeklik hotbar opsi & memicu unduhan...")
            generator.click_hotbar_and_download()

            progress.update(task, description="[cyan]Menunggu file .jpg di folder unduhan...")
            downloaded = generator.wait_for_downloaded_file(existing_files=existing, timeout=60)

            progress.update(task, description="[cyan]Memindahkan file gambar ke lokasi tujuan...")
            if output_dest is None:
                dest_dir = generator.workspace_dir / "outputs"
                dest_dir.mkdir(parents=True, exist_ok=True)
                slug = re.sub(r"[^\w\s-]", "", prompt)[:30].strip().replace(" ", "_")
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                target_file = dest_dir / f"{slug}_{timestamp}.jpg"
            else:
                target_path = Path(output_dest).resolve()
                if target_path.is_dir() or (not target_path.suffix and not target_path.exists()):
                    target_path.mkdir(parents=True, exist_ok=True)
                    slug = re.sub(r"[^\w\s-]", "", prompt)[:30].strip().replace(" ", "_")
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    target_file = target_path / f"{slug}_{timestamp}.jpg"
                else:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    target_file = target_path

            shutil.move(str(downloaded), str(target_file))
            generator.close()

        except Exception as e:
            console.print(f"\n[error]✗ Kegagalan Otomasi:[/error] {e}")
            return 1

    summary_table = Table(box=box.ROUNDED, show_header=True)
    summary_table.add_column("Komponen", style="cyan")
    summary_table.add_column("Status / Lokasi", style="bold")
    summary_table.add_row("Status Generasi", "[bold green]✓ Selesai & Terverifikasi[/bold green]")
    summary_table.add_row("Hotbar & Download Menu", "[bold green]✓ Berhasil Diklik[/bold green]")
    summary_table.add_row("File Hasil Gambar", f"[bold green]{target_file}[/bold green]")
    console.print(summary_table)

    console.print(
        Panel(
            f"[bold green]BERHASIL MENGHASILKAN & MENGUNDUH GAMBAR![/bold green]\n\n"
            f"[muted]Prompt:[/muted] [gold]{prompt}[/gold]\n"
            f"[muted]Lokasi Berkas:[/muted] [white]{target_file}[/white]\n"
            f"[muted]Ukuran Berkas:[/muted] [cyan]{target_file.stat().st_size:,} bytes[/cyan]",
            box=box.ROUNDED,
            style="color(240)",
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
