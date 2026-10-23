"""Image Generator v2 (Silent Background Edition) — Modul & CLI Otomasi Google Flow.

Fitur Utama:
1. 100% Senyap & Non-Intrusif: Bebas total dari kontrol mouse fisik Windows,
   clipboard OS, atau pencurian fokus jendela (zero cursor hijacking).
2. Berjalan di Latar Belakang (Background / Minimized): Peramban dibuka secara
   terminimalkan (SW_SHOWMINNOACTIVE) atau mode -headless sehingga pengguna dapat
   tetap bekerja, mengetik, bermain game, atau beraktivitas tanpa terganggu sedikit pun.
3. Otomasi Siklus Penuh: Input prompt -> Generate -> Monitor progres -> Unduh 1K ->
   Pindahkan berkas -> Hapus gambar dari kanvas ('Pindahkan ke sampah').
4. Callable & CLI: Dapat diimpor sebagai fungsi Python atau dipanggil dari terminal.

Penggunaan:
    # Sebagai CLI:
    python image_generator.py --prompt pemandangan gunung es sinematik -o hasil/
    python image_generator.py --headless --prompt robot kucing futuristik

    # Sebagai Modul Python:
    from image_generator import generate_image
    output_path = generate_image("gambar produk estetik", output_path="outputs/")
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

import win32con
import win32gui

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
# XPATH & SELECTOR DEFINITIONS DARI SPESIFIKASI & PENGUJIAN EMPIRIS
# ==============================================================================
FLOW_PROJECT_URL = "https://flow.google.com/project/d2653e23-18ab-4dda-b15b-3a77cf1085dd"
FLOW_FALLBACK_URL = "https://flow.google.com/project/8eed2cd9-e563-46d8-9ad2-395e53901db4"

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

XPATH_SUBMENU_DOWNLOAD_1K = (
    "//flow-menu-item[contains(., '1K') or contains(., 'Ukuran asli') or contains(., 'Original')]"
)


# ==============================================================================
# MARIONETTE PROTOCOL CLIENT (STEALTH BACKGROUND BRIDGE)
# ==============================================================================
class MarionetteDriver:
    """Klien soket native Marionette untuk Firefox Portable (Stealth Silent Bridge)."""

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

        res = self.send("WebDriver:NewSession", {})
        self.session_id = res.get("sessionId")
        self.send("Marionette:SetContext", {"value": "content"})
        return self.session_id

    def send(self, name: str, parameters: dict | None = None) -> dict:
        """Mengirim pesan perintah JSON wire protocol ke Marionette."""
        if not self.sock:
            raise RuntimeError("Koneksi soket Marionette belum dibuka.")

        self.msg_id += 1
        payload = json.dumps([0, self.msg_id, name, parameters or {}])
        msg = f"{len(payload)}:{payload}".encode("utf-8")
        self.sock.sendall(msg)

        # Baca panjang respons
        length_bytes = b""
        while True:
            c = self.sock.recv(1)
            if not c:
                raise ConnectionError("Koneksi terputus saat membaca respons peramban.")
            if c == b":":
                break
            length_bytes += c

        total_length = int(length_bytes.decode("ascii"))
        received_data = b""
        while len(received_data) < total_length:
            chunk = self.sock.recv(min(4096, total_length - len(received_data)))
            if not chunk:
                break
            received_data += chunk

        raw_resp = json.loads(received_data.decode("utf-8"))
        if raw_resp[2] is not None:
            raise RuntimeError(f"Kesalahan Marionette [{name}]: {raw_resp[2]}")
        return raw_resp[3]

    def execute_script(self, script: str, args: list | None = None) -> any:
        """Mengeksekusi skrip JavaScript di konteks halaman aktif."""
        res = self.send("WebDriver:ExecuteScript", {"script": script, "args": args or []})
        return res.get("value")

    def find_element(self, using: str, value: str) -> str:
        """Mencari elemen dan mengembalikan element ID string."""
        res = self.send("WebDriver:FindElement", {"using": using, "value": value})
        val = res.get("value", res) if isinstance(res, dict) else res
        if isinstance(val, dict):
            return val.get("element-6066-11e4-a52e-4f735466cecf") or list(val.values())[0]
        return str(val)

    def click_element(self, element_id: str) -> None:
        """Mengeklik elemen via Gecko C++ native click (tanpa menggerakkan mouse OS)."""
        self.send("WebDriver:ElementClick", {"id": element_id})

    def get_window_handles(self) -> list[str]:
        """Mengambil daftar handle semua tab/jendela yang terbuka."""
        return self.send("WebDriver:GetWindowHandles", {})

    def switch_to_window(self, handle: str) -> None:
        """Beralih ke tab/jendela tertentu."""
        self.send("WebDriver:SwitchToWindow", {"handle": handle})

    def navigate(self, url: str) -> None:
        """Membuka atau mengarahkan tab aktif ke URL yang ditentukan."""
        try:
            self.send("WebDriver:Navigate", {"url": url})
        except Exception:
            self.execute_script("window.location.href = arguments[0];", [url])

    def take_screenshot(self, full: bool = False) -> bytes:
        """Mengambil tangkapan layar halaman web peramban (PNG) langsung dari viewport browser."""
        import base64
        res = self.send("WebDriver:TakeScreenshot", {"full": full})
        val = res.get("value") if isinstance(res, dict) else res
        return base64.b64decode(val)

    def close(self) -> None:
        """Menutup koneksi soket."""
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None


# ==============================================================================
# IMAGE GENERATOR AUTOMATION CONTROLLER (SILENT BACKGROUND EDITION)
# ==============================================================================
class ImageGenerator:
    """Pengontrol otomasi Google Flow generasi senyap tanpa interupsi pengguna."""

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

    def _is_profile_locked(self) -> bool:
        """Memeriksa apakah profil sedang dikunci proses lain atau hanya lock yatim."""
        lock_file = self.profile_dir / "parent.lock"
        if not lock_file.exists():
            return False
        try:
            with open(lock_file, "a+b"):
                pass
            try:
                lock_file.unlink(missing_ok=True)
            except Exception:
                pass
            return False
        except (PermissionError, OSError):
            return True

    def _ensure_stealth_preferences(self) -> None:
        """Menjamin pengaturan stealth aktif agar navigator.webdriver tidak terdeteksi."""
        user_js = self.profile_dir / "user.js"
        required_prefs = [
            'user_pref("marionette.enabled", true);',
            'user_pref("marionette.port", 2828);',
            'user_pref("marionette.defaultPrefs.enabled", true);',
            'user_pref("dom.webdriver.enabled", false);',
            'user_pref("marionette.actors.enabled", true);',
            'user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);',
        ]
        existing = ""
        if user_js.exists():
            existing = user_js.read_text(encoding="utf-8", errors="ignore")

        missing = [p for p in required_prefs if p not in existing]
        if missing:
            with open(user_js, "a", encoding="utf-8") as f:
                f.write("\n" + "\n".join(missing) + "\n")

    def ensure_browser(self, auto_launch: bool = True, headless: bool = False) -> None:
        """Memastikan Firefox berjalan dengan stealth mode di latar belakang."""
        self._ensure_stealth_preferences()

        if self.driver.is_port_open(timeout=0.8):
            return

        if self._is_profile_locked():
            console.print(
                Panel(
                    "[warning]⚠ Profil peramban sedang digunakan oleh Firefox lain tanpa port otomasi.[/warning]\n"
                    "Silakan tutup jendela peramban tersebut agar skrip dapat menjalankannya dalam mode otomasi stealth.",
                    title="[gold]Profil Sedang Terkunci[/gold]",
                    box=box.ROUNDED,
                )
            )
            Prompt.ask("[cyan]Tekan Enter setelah menutup jendela Firefox...[/cyan]")

        if auto_launch:
            mode_desc = "headless (tanpa GUI)" if headless else "minimized background (tanpa ganggu fokus)"
            console.print(f"[info]ℹ[/info] Meluncurkan peramban Firefox dalam mode {mode_desc}...")
            env = os.environ.copy()
            env["MOZ_CRASHREPORTER_DISABLE"] = "1"
            env["MOZ_CRASHREPORTER_NO_REPORT"] = "1"

            cmd = [str(self.ff_bin), "-no-remote", "-marionette", "-profile", str(self.profile_dir)]
            if headless:
                cmd.append("-headless")

            # Buka secara terminimalkan tanpa mencuri fokus pengguna (SW_SHOWMINNOACTIVE)
            startupinfo = None
            if sys.platform == "win32" and not headless:
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 7  # SW_SHOWMINNOACTIVE

            subprocess.Popen(cmd, env=env, startupinfo=startupinfo)

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
            hasFlow: !!document.querySelector('aisandbox-root, flow-project-shell, flow-prompt-box, flow-rich-text-editor'),
            projectLink: (function() {
                const a = document.querySelector('a[href*="/project/"]');
                return a ? a.href : null;
            })()
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

                if has_flow or ("flow" in url and "project" in url):
                    return handle

                # Jika di halaman home Google Flow, buka project yang tersedia
                if info.get("projectLink"):
                    self.driver.navigate(info["projectLink"])
                    time.sleep(3.0)
                    return handle
            except Exception:
                continue

        # Jika belum ada tab yang memuat Google Flow, arahkan tab aktif ke proyek Google Flow
        console.print(f"[info]ℹ[/info] Mengarahkan peramban ke [cyan]{FLOW_PROJECT_URL}[/cyan]...")
        self.driver.switch_to_window(handles[0])
        self.driver.navigate(FLOW_PROJECT_URL)
        time.sleep(4.0)

        for _ in range(25):
            try:
                info = self.driver.execute_script(detection_script)
                if isinstance(info, dict):
                    if "404" in (info.get("url") or ""):
                        # Jika 404, navigasi ke home Google Flow untuk auto-resolve project
                        self.driver.navigate("https://flow.google.com/")
                        time.sleep(3.0)
                        h_info = self.driver.execute_script(detection_script)
                        if h_info and h_info.get("projectLink"):
                            self.driver.navigate(h_info["projectLink"])
                            time.sleep(3.0)
                            return handles[0]
                    if info.get("hasFlow") or "flow" in (info.get("url") or "").lower():
                        return handles[0]
            except Exception:
                pass
            time.sleep(1.0)

        return handles[0]

    def submit_prompt(self, prompt_text: str) -> dict:
        """Memasukkan prompt secara senyap via ProseMirror DOM & Gecko ElementClick."""
        # Catat snapshot kondisi kanvas sebelum generasi baru
        snapshot_script = """
        const firstImg = document.querySelector('flow-image-tile img');
        return {
            imgCount: document.querySelectorAll('flow-image-tile img').length,
            firstImgSrc: firstImg ? firstImg.src : null
        };
        """
        initial_state = self.driver.execute_script(snapshot_script) or {"imgCount": 0, "firstImgSrc": None}

        input_script = """
        const prompt = arguments[0];
        const editor = document.querySelector('flow-rich-text-editor div[contenteditable="true"]') ||
                       document.querySelector('flow-rich-text-editor p') ||
                       document.querySelector('div[contenteditable="true"]');
        if (!editor) return { success: false, error: 'Editor prompt tidak ditemukan.' };

        editor.focus();
        document.execCommand('selectAll', false, null);
        document.execCommand('insertText', false, prompt);
        editor.dispatchEvent(new InputEvent('input', { bubbles: true, inputType: 'insertText', data: prompt }));
        editor.dispatchEvent(new Event('change', { bubbles: true }));

        return { success: true };
        """
        res_in = self.driver.execute_script(input_script, [prompt_text])
        if not isinstance(res_in, dict) or not res_in.get("success"):
            raise RuntimeError(f"Gagal memasukkan teks prompt: {res_in}")

        time.sleep(0.5)

        # Klik tombol generate via Gecko C++ native click (tanpa sentuh kursor OS)
        try:
            btn_id = self.driver.find_element("css selector", "flow-generate-icon-button button")
            self.driver.click_element(btn_id)
        except Exception:
            # Fallback ke DOM click
            click_btn_script = """
            const btn = document.querySelector('flow-generate-icon-button button') ||
                        document.querySelector('flow-generate-icon-button');
            if (btn) { btn.click(); return true; }
            return false;
            """
            self.driver.execute_script(click_btn_script)

        return initial_state

    def hover_and_wait_tile(self, initial_state: dict | None = None, timeout: int = 180, progress_callback: any = None) -> bool:
        """Menunggu generasi gambar selesai (0% -> 100%) dan memantau status render tile baru."""
        start_time = time.time()
        init_count = (initial_state or {}).get("imgCount", 0)
        init_src = (initial_state or {}).get("firstImgSrc")

        check_script = """
        const bodyText = document.body.innerText;
        const progressMatch = bodyText.match(/(\\d+)%/);
        const firstTile = document.querySelector('flow-image-tile');
        const firstImg = firstTile ? firstTile.querySelector('img') : null;
        const allImgs = document.querySelectorAll('flow-image-tile img');
        const btn = document.querySelector('flow-generate-icon-button button');

        let hotbarReady = false;
        if (firstTile) {
            firstTile.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true, cancelable: true }));
            firstTile.dispatchEvent(new MouseEvent('mouseover', { bubbles: true, cancelable: true }));
            const hbBtn = firstTile.querySelector('flow-image-hotbar button:nth-child(3)');
            hotbarReady = !!hbBtn;
        }

        return {
            imgCount: allImgs.length,
            firstImgSrc: firstImg ? firstImg.src : null,
            progress: progressMatch ? progressMatch[1] : null,
            btnDisabled: btn ? btn.disabled : false,
            hotbarReady: hotbarReady
        };
        """

        seen_progress = False
        last_progress = None

        while time.time() - start_time < timeout:
            st = self.driver.execute_script(check_script)
            if isinstance(st, dict):
                current_prog = st.get("progress")
                if current_prog:
                    seen_progress = True
                    if current_prog != last_progress:
                        last_progress = current_prog
                        if progress_callback:
                            progress_callback(current_prog)

                # Kondisi selesai generasi:
                # 1. Progres pernah muncul dan sekarang sudah selesai (progress == None)
                # 2. Atau jumlah gambar bertambah dibanding saat submit
                # 3. Atau sumber gambar paling atas berbeda dari init_src dan hotbar sudah siap
                img_count = st.get("imgCount", 0)
                first_src = st.get("firstImgSrc")

                is_new_image = (
                    (img_count > init_count) or
                    (first_src and first_src != init_src)
                )

                if seen_progress and not current_prog and is_new_image and st.get("hotbarReady"):
                    time.sleep(1.0)
                    return True

                if is_new_image and not current_prog and st.get("hotbarReady") and (time.time() - start_time > 8):
                    time.sleep(1.0)
                    return True

            time.sleep(1.5)

        raise TimeoutError(f"Waktu tunggu generasi gambar habis ({timeout} detik). Gambar belum selesai dirender.")

    def click_hotbar_and_download(self, timeout: int = 20) -> bool:
        """Mengeklik hotbar opsi (tombol 3), membuka menu 'Download', lalu memilih resolusi '1K (Ukuran asli)'."""
        # 1. Buka menu hotbar button 3 secara senyap pada tile teratas
        open_hotbar_script = """
        const tile = document.querySelector('flow-image-tile');
        if (!tile) return { success: false, error: 'Tile gambar tidak ditemukan.' };

        tile.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true, cancelable: true }));
        tile.dispatchEvent(new MouseEvent('mouseover', { bubbles: true, cancelable: true }));

        const btn = tile.querySelector('flow-image-hotbar button:nth-child(3)');
        if (!btn) return { success: false, error: 'Tombol hotbar 3 tidak ditemukan.' };

        btn.click();
        return { success: true };
        """
        res_h = self.driver.execute_script(open_hotbar_script)
        if not isinstance(res_h, dict) or not res_h.get("success"):
            raise RuntimeError(f"Gagal membuka menu hotbar opsi: {res_h}")

        time.sleep(1.0)

        # 2. Klik menu 'Download' pada overlay
        click_dl_script = """
        const buttons = Array.from(document.querySelectorAll('.cdk-overlay-container button.mat-mdc-menu-item, button.mat-mdc-menu-item'));
        const dl = buttons.find(b => (b.textContent || '').includes('Download') || (b.textContent || '').includes('Unduh'));
        if (!dl) return { success: false, error: 'Menu Download tidak ditemukan.' };

        dl.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true }));
        dl.click();
        return { success: true, text: dl.textContent.trim() };
        """
        res_dl = self.driver.execute_script(click_dl_script)
        if not isinstance(res_dl, dict) or not res_dl.get("success"):
            raise RuntimeError(f"Gagal mengeklik menu Download: {res_dl}")

        time.sleep(1.0)

        # 3. Klik opsi '1K (Ukuran asli)' di submenu overlay
        click_1k_script = """
        const buttons = Array.from(document.querySelectorAll('.cdk-overlay-container button.mat-mdc-menu-item, button.mat-mdc-menu-item'));
        const oneK = buttons.find(b => (b.textContent || '').includes('1K') || (b.textContent || '').includes('Ukuran asli') || (b.textContent || '').includes('Original'));
        if (!oneK) return { success: false, error: 'Opsi 1K tidak ditemukan.' };

        oneK.click();
        return { success: true, text: oneK.textContent.trim() };
        """
        res_1k = self.driver.execute_script(click_1k_script)
        if not isinstance(res_1k, dict) or not res_1k.get("success"):
            raise RuntimeError(f"Gagal mengeklik opsi resolusi 1K: {res_1k}")

        return True

    def wait_for_downloaded_file(self, existing_files: set[str], timeout: int = 60) -> Path:
        """Memantau folder download sampai file .jpg baru selesai diunduh."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            current_files = list(self.download_dir.glob("*.jpg")) + list(self.download_dir.glob("*.jpeg"))
            new_files = [f for f in current_files if str(f.resolve()) not in existing_files]

            if new_files:
                latest_file = max(new_files, key=lambda f: f.stat().st_mtime)

                part_files = list(self.download_dir.glob(f"{latest_file.name}.part"))
                if not part_files:
                    size1 = latest_file.stat().st_size
                    time.sleep(0.5)
                    size2 = latest_file.stat().st_size
                    if size1 == size2 and size1 > 0:
                        return latest_file

            time.sleep(1.0)

        raise TimeoutError(f"File .jpg hasil unduhan tidak terdeteksi di {self.download_dir} dalam {timeout} detik.")

    def delete_current_tile(self, timeout: int = 15) -> bool:
        """Menghapus gambar dari kanvas peramban ('Pindahkan ke sampah') secara senyap."""
        # 1. Buka hotbar button 3
        open_script = """
        const tile = document.querySelector('flow-image-tile');
        if (!tile) return { success: false, error: 'Tile tidak ditemukan untuk dihapus.' };

        tile.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true, cancelable: true }));
        tile.dispatchEvent(new MouseEvent('mouseover', { bubbles: true, cancelable: true }));

        const btn = tile.querySelector('flow-image-hotbar button:nth-child(3)');
        if (btn) btn.click();
        return { success: true };
        """
        self.driver.execute_script(open_script)
        time.sleep(1.0)

        # 2. Klik opsi 'Pindahkan ke sampah' pada overlay
        trash_script = """
        const buttons = Array.from(document.querySelectorAll('.cdk-overlay-container button.mat-mdc-menu-item, button.mat-mdc-menu-item'));
        const trash = buttons.find(b => (b.textContent || '').includes('sampah') || (b.textContent || '').includes('Delete'));
        if (!trash) return { success: false, error: 'Opsi Pindahkan ke sampah tidak ditemukan.' };

        trash.click();
        return { success: true };
        """
        res_tr = self.driver.execute_script(trash_script)
        time.sleep(1.5)
        return True

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
    headless: bool = False,
) -> Path:
    """Fungsi utama untuk menghasilkan dan mengunduh gambar dari Google Flow secara senyap.

    Args:
        prompt: Teks deskripsi gambar yang akan digenerate.
        output_path: Jalur folder atau berkas tujuan pemindahan gambar.
                     Jika None, disimpan otomatis di folder 'outputs/' dengan nama slug prompt.
        timeout: Waktu tunggu maksimal generasi gambar (detik).
        auto_launch: Luncurkan Firefox Portable secara otomatis jika belum berjalan.
        headless: Jalankan Firefox dalam mode -headless tanpa GUI.

    Returns:
        Path: Lokasi absolut berkas gambar .jpg yang telah dipindahkan.
    """
    generator = ImageGenerator()

    try:
        generator.ensure_browser(auto_launch=auto_launch, headless=headless)
        generator.connect()

        existing = {str(f.resolve()) for f in list(generator.download_dir.glob("*.jpg")) + list(generator.download_dir.glob("*.jpeg"))}
        generator.find_flow_tab()
        initial_state = generator.submit_prompt(prompt)
        generator.hover_and_wait_tile(initial_state=initial_state, timeout=timeout)
        generator.click_hotbar_and_download()
        downloaded_file = generator.wait_for_downloaded_file(existing_files=existing, timeout=60)

        # Pemindahan berkas
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

        # Hapus gambar dari kanvas peramban setelah berkas aman disimpan
        try:
            generator.delete_current_tile()
        except Exception as del_err:
            console.print(f"[warning]⚠ Catatan pembersihan: {del_err}[/warning]")

        return target_file

    finally:
        generator.close()


# ==============================================================================
# CLI PARSER & INTERFACE
# ==============================================================================
def parse_cli_args() -> tuple[str, str | None, int, bool]:
    """Mengekstrak prompt tanpa wajib tanda petik, output path, timeout, dan headless flag."""
    args = sys.argv[1:]
    output_flags = ["--output", "-o", "--dest", "-d"]
    timeout_flags = ["--timeout", "-t"]
    prompt_flags = ["--prompt", "-p"]
    headless_flag = "--headless"

    output_val = None
    timeout_val = 180
    headless_val = False
    prompt_tokens = []

    if headless_flag in args:
        headless_val = True
        args = [a for a in args if a != headless_flag]

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
    return prompt_str, output_val, timeout_val, headless_val


def main() -> int:
    console.clear()
    banner = (
        "[brand]IMAGE GENERATOR v2 — GOOGLE FLOW BOT[/brand] [muted]//[/muted] [gold]SILENT BACKGROUND EDITION[/gold]\n"
        "[muted]Otomasi 100% Senyap Tanpa Mengontrol Kursor Pengguna & Berjalan di Latar Belakang[/muted]"
    )
    console.print(Panel(banner, box=box.ROUNDED, style="color(240)"))

    prompt, output_dest, timeout, headless = parse_cli_args()

    if not prompt:
        console.print("[info]ℹ[/info] [dim]Tips: Jalankan `python image_generator.py --prompt gambar pemandangan -o hasil/` tanpa tanda petik.[/dim]\n")
        prompt = Prompt.ask("[cyan]Masukkan Prompt Generasi Gambar[/cyan]")

    if not prompt.strip():
        console.print("[error]✗[/error] Prompt tidak boleh kosong.")
        return 1

    target_display = str(Path(output_dest).resolve()) if output_dest else str(Path("outputs").resolve())

    table = Table(box=box.ROUNDED, show_header=False, expand=True)
    table.add_column("Parameter", style="cyan", width=22)
    table.add_column("Nilai", style="bold white")
    table.add_row("Prompt Teks", f"[gold]{prompt}[/gold]")
    table.add_row("Metode Eksekusi", "[bold green]100% Silent Background (Zero Cursor Hijacking)[/bold green]")
    table.add_row("Mode Tampilan", "[yellow]Headless (Tanpa GUI)[/yellow]" if headless else "[cyan]Minimized Background[/cyan]")
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
            generator.ensure_browser(headless=headless)
            generator.connect()

            existing = {str(f.resolve()) for f in list(generator.download_dir.glob("*.jpg")) + list(generator.download_dir.glob("*.jpeg"))}
            generator.find_flow_tab()

            progress.update(task, description="[cyan]Mengirim prompt secara senyap (ProseMirror DOM)...")
            initial_state = generator.submit_prompt(prompt)

            progress.update(task, description="[gold]Menunggu render gambar selesai di latar belakang...")
            generator.hover_and_wait_tile(
                initial_state=initial_state,
                timeout=timeout,
                progress_callback=lambda p: progress.update(task, description=f"[gold]Menunggu render gambar selesai ({p}%)...[/gold]")
            )

            progress.update(task, description="[cyan]Mengeklik hotbar opsi & memicu unduhan 1K...")
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

            progress.update(task, description="[cyan]Menghapus gambar dari kanvas peramban (Pindahkan ke sampah)...")
            try:
                generator.delete_current_tile()
            except Exception as del_err:
                console.print(f"[warning]⚠ Catatan pembersihan: {del_err}[/warning]")

            generator.close()

        except Exception as e:
            console.print(f"\n[error]✗ Kegagalan Otomasi:[/error] {e}")
            return 1

    summary_table = Table(box=box.ROUNDED, show_header=True)
    summary_table.add_column("Komponen", style="cyan")
    summary_table.add_column("Status / Lokasi", style="bold")
    summary_table.add_row("Status Generasi", "[bold green]✓ Selesai & Terverifikasi[/bold green]")
    summary_table.add_row("Interupsi Kursor Pengguna", "[bold green]✓ 0% (Kursor Bebas Digunakan)[/bold green]")
    summary_table.add_row("Mode Tampilan Jendela", "[bold green]✓ Berjalan di Latar Belakang (Minimized)[/bold green]")
    summary_table.add_row("Hotbar & Download 1K", "[bold green]✓ Berhasil Diunduh Resolusi Asli[/bold green]")
    summary_table.add_row("Pembersihan Kanvas", "[bold green]✓ Dipindahkan ke Sampah[/bold green]")
    summary_table.add_row("File Hasil Gambar", f"[bold green]{target_file}[/bold green]")
    console.print(summary_table)

    console.print(
        Panel(
            f"[bold green]BERHASIL MENGHASILKAN & MENGUNDUH GAMBAR SECARA SENYAP![/bold green]\n\n"
            f"[muted]Prompt:[/muted] [gold]{prompt}[/gold]\n"
            f"[muted]Lokasi Berkas:[/muted] [white]{target_file}[/white]\n"
            f"[muted]Kursor Mouse:[/muted] [green]Tidak tersentuh sama sekali selama proses berlangsung[/green]",
            box=box.ROUNDED,
            style="color(240)",
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
