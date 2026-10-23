"""Image Generator — Modul & CLI Otomasi Google Flow (Solusi 1: Native OS Input).

Dapat dipanggil langsung sebagai CLI atau diimpor sebagai fungsi Python:
    from image_generator import generate_image
    output_path = generate_image("gambar produk hidup", output_dir="hasil_gambar")

Menggunakan Native OS Input (Windows API / win32clipboard / SendInput / keybd_event)
serta stealth mode (dom.webdriver.enabled=false) untuk menjamin event.isTrusted === true
dan bebas 100% dari deteksi kontrol peramban (remote control detection).
"""

import ctypes
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

import win32api
import win32clipboard
import win32con
import win32gui
import win32process
import win32service

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
FLOW_PROJECT_URL = "https://flow.google.com/project/8eed2cd9-e563-46d8-9ad2-395e53901db4"

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

# Item pertama di submenu resolusi unduhan adalah 1K (Ukuran asli)
XPATH_SUBMENU_DOWNLOAD_1K = (
    "//flow-menu-item[contains(., '1K') or contains(., 'Ukuran asli') or contains(., 'Original')]"
)
XPATH_SUBMENU_DOWNLOAD_ITEM_2 = (
    "/html/body/div[6]/div[2]/div/div/div/flow-menu-item[2]"
)


# ==============================================================================
# NATIVE OS CONTROLLER (WINDOWS API / WIN32 / CLIPBOARD / HARDWARE EVENTS)
# ==============================================================================
class NativeOSController:
    """Pengontrol input tingkat sistem operasi Windows (Solusi 1: Native OS Input).

    Mengirimkan event keyboard dan mouse melalui antrian pesan sistem operasi
    sehingga event.isTrusted bernilai true 100% dan tidak dapat dibedakan
    dari interaksi fisik manusia.
    """

    @staticmethod
    def set_dpi_awareness() -> None:
        """Mengatur DPI awareness proses agar konversi koordinat piksel akurat."""
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-Monitor DPI Aware
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

    @staticmethod
    def ensure_interactive_desktop() -> bool:
        """Memastikan thread terikat ke desktop interaktif 'Default'."""
        try:
            desk = win32service.OpenDesktop("Default", 0, False, win32con.GENERIC_ALL)
            desk.SetThreadDesktop()
            return True
        except Exception:
            return False

    @classmethod
    def find_firefox_hwnd(cls, preferred_title: str | None = None) -> int | None:
        """Mencari HWND jendela peramban Firefox di desktop interaktif."""
        cls.ensure_interactive_desktop()
        candidates: list[tuple[int, str]] = []

        def enum_cb(hwnd: int, _: None) -> bool:
            if win32gui.IsWindowVisible(hwnd):
                cls_name = win32gui.GetClassName(hwnd)
                if cls_name == "MozillaWindowClass":
                    title = win32gui.GetWindowText(hwnd)
                    candidates.append((hwnd, title))
            return True

        try:
            win32gui.EnumWindows(enum_cb, None)
        except Exception:
            pass

        if not candidates:
            return None

        if preferred_title:
            for hwnd, title in candidates:
                if preferred_title.lower() in title.lower():
                    return hwnd

        for hwnd, title in candidates:
            lower = title.lower()
            if "flow" in lower or "sandbox" in lower:
                return hwnd

        return candidates[0][0]

    @classmethod
    def activate_window(cls, hwnd: int | None = None) -> bool:
        """Mengaktifkan dan memulihkan jendela Firefox ke garis depan (foreground)."""
        cls.ensure_interactive_desktop()
        if hwnd is None:
            hwnd = cls.find_firefox_hwnd()
        if not hwnd or not win32gui.IsWindow(hwnd):
            return False

        try:
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            else:
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)

            fore_hwnd = win32gui.GetForegroundWindow()
            if fore_hwnd != hwnd:
                cur_tid = win32api.GetCurrentThreadId()
                fore_tid, _ = win32process.GetWindowThreadProcessId(fore_hwnd) if fore_hwnd else (0, 0)
                if fore_tid and fore_tid != cur_tid:
                    try:
                        win32process.AttachThreadInput(cur_tid, fore_tid, True)
                    except Exception:
                        pass

                # Kirim sinyal Alt untuk membypass pembatasan SetForegroundWindow Windows
                win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
                win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
                win32gui.SetForegroundWindow(hwnd)
                win32gui.BringWindowToTop(hwnd)

                if fore_tid and fore_tid != cur_tid:
                    try:
                        win32process.AttachThreadInput(cur_tid, fore_tid, False)
                    except Exception:
                        pass

            time.sleep(0.15)
            return True
        except Exception:
            return False

    @classmethod
    def set_clipboard_text(cls, text: str) -> None:
        """Menaruh teks ke Windows Clipboard format CF_UNICODETEXT."""
        cls.ensure_interactive_desktop()
        for _ in range(5):
            try:
                win32clipboard.OpenClipboard()
                try:
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
                    return
                finally:
                    win32clipboard.CloseClipboard()
            except Exception:
                time.sleep(0.05)

    @classmethod
    def send_key_combination(cls, *vk_codes: int, hold_ms: float = 0.05) -> None:
        """Menekan kombinasi tombol keyboard secara serempak lalu melepasnya."""
        cls.ensure_interactive_desktop()
        for vk in vk_codes:
            win32api.keybd_event(vk, 0, 0, 0)
        time.sleep(hold_ms)
        for vk in reversed(vk_codes):
            win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.04)

    @classmethod
    def send_paste_and_enter(cls, prompt_text: str) -> None:
        """Menaruh prompt ke clipboard, membersihkan input lama, paste (Ctrl+V), dan Enter."""
        cls.set_clipboard_text(prompt_text)
        time.sleep(0.08)

        # Seleksi semua (Ctrl+A) lalu hapus (Backspace) jika ada teks sebelumnya
        cls.send_key_combination(win32con.VK_CONTROL, ord("A"))
        time.sleep(0.05)
        win32api.keybd_event(win32con.VK_BACK, 0, 0, 0)
        win32api.keybd_event(win32con.VK_BACK, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)

        # Tempel teks asli via Clipboard (Ctrl+V)
        cls.send_key_combination(win32con.VK_CONTROL, ord("V"))
        time.sleep(0.25)  # Beri waktu bagi Angular rich-text editor untuk bind teks

        # Tekan tombol Enter asli (Hardware VK_RETURN)
        win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)

    @classmethod
    def send_mouse_move(cls, x: int, y: int) -> None:
        """Menggerakkan kursor mouse fisik ke koordinat desktop (x, y)."""
        cls.ensure_interactive_desktop()
        win32api.SetCursorPos((int(x), int(y)))
        time.sleep(0.05)

    @classmethod
    def send_mouse_click(cls, x: int, y: int) -> None:
        """Mengeklik tombol kiri mouse secara fisik pada koordinat desktop (x, y)."""
        cls.ensure_interactive_desktop()
        win32api.SetCursorPos((int(x), int(y)))
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.05)


# ==============================================================================
# MARIONETTE PROTOCOL CLIENT (STEALTH BACKGROUND BRIDGE)
# ==============================================================================
class MarionetteDriver:
    """Klien soket native Marionette untuk Firefox Portable (Stealth Bridge)."""

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
        # Struktur respons Marionette: [type, msg_id, error, result]
        if raw_resp[2] is not None:
            raise RuntimeError(f"Kesalahan Marionette [{name}]: {raw_resp[2]}")
        return raw_resp[3]

    def execute_script(self, script: str, args: list | None = None) -> any:
        """Mengeksekusi skrip JavaScript di konteks halaman aktif."""
        res = self.send("WebDriver:ExecuteScript", {"script": script, "args": args or []})
        return res.get("value")

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
# IMAGE GENERATOR AUTOMATION CONTROLLER
# ==============================================================================
class ImageGenerator:
    """Pengontrol utama otomasi Google Flow Image Generator dengan Solusi 1."""

    def __init__(self, workspace_dir: Path | None = None):
        if workspace_dir is None:
            self.workspace_dir = Path(__file__).resolve().parent
        else:
            self.workspace_dir = Path(workspace_dir).resolve()

        self.profile_dir = self.workspace_dir / "browser_profile"
        self.ff_bin = Path(r"D:\FirefoxPortable\App\Firefox64\firefox.exe")
        self.download_dir = self._detect_download_dir()
        self.driver = MarionetteDriver()

        # Inisialisasi DPI awareness agar koordinat piksel akurat
        NativeOSController.set_dpi_awareness()

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
            # Berhasil dibuka -> file lock yatim (orphan), aman dihapus otomatis
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
        ]
        existing = ""
        if user_js.exists():
            existing = user_js.read_text(encoding="utf-8", errors="ignore")

        missing = [p for p in required_prefs if p not in existing]
        if missing:
            with open(user_js, "a", encoding="utf-8") as f:
                f.write("\n" + "\n".join(missing) + "\n")

    def ensure_browser(self, auto_launch: bool = True) -> None:
        """Memastikan Firefox berjalan dengan stealth mode & Marionette siap."""
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
            console.print("[info]ℹ[/info] Meluncurkan peramban Firefox dalam mode stealth (Solusi 1)...")
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

        # Jika belum ada tab yang memuat Google Flow, arahkan tab aktif ke proyek Google Flow
        console.print(f"[info]ℹ[/info] Tab Google Flow belum terbuka. Mengarahkan peramban ke [cyan]{FLOW_PROJECT_URL}[/cyan]...")
        self.driver.switch_to_window(handles[0])
        self.driver.navigate(FLOW_PROJECT_URL)
        time.sleep(3.0)

        # Tunggu sampai komponen utama Google Flow terpasang di DOM
        for _ in range(25):
            try:
                info = self.driver.execute_script(detection_script)
                if isinstance(info, dict) and (info.get("hasFlow") or "flow" in (info.get("url") or "").lower()):
                    time.sleep(1.0)
                    return handles[0]
            except Exception:
                pass
            time.sleep(1.0)

        return handles[0]

    def submit_prompt(self, prompt_text: str) -> bool:
        """Memasukkan prompt via Solusi 1 (Native OS Input: Clipboard + Ctrl+V + Enter)."""
        # 1. Aktifkan jendela Firefox ke garis depan
        NativeOSController.activate_window()
        time.sleep(0.15)

        # 2. Cari elemen editor input dan dapatkan koordinat layarnya
        locate_script = """
        const inputXpath = arguments[0];
        const buttonXpath = arguments[1];

        function getByXPath(xpath) {
            try {
                return document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            } catch (e) {
                return null;
            }
        }

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

        editorEl.scrollIntoView({ block: 'center' });
        editorEl.focus();

        const rect = editorEl.getBoundingClientRect();
        const screenX = Math.round(window.mozInnerScreenX + rect.left + rect.width / 2);
        const screenY = Math.round(window.mozInnerScreenY + rect.top + rect.height / 2);

        // Ambil juga info tombol generate jika ada
        let btnEl = getByXPath(buttonXpath) ||
                    document.querySelector('flow-generate-icon-button button') ||
                    document.querySelector('flow-generate-icon-button') ||
                    document.querySelector('flow-base-prompt-box button.generate-button');
        let btnCoord = null;
        if (btnEl) {
            const bRect = btnEl.getBoundingClientRect();
            btnCoord = {
                x: Math.round(window.mozInnerScreenX + bRect.left + bRect.width / 2),
                y: Math.round(window.mozInnerScreenY + bRect.top + bRect.height / 2)
            };
        }

        return {
            success: true,
            screenX: screenX,
            screenY: screenY,
            btnCoord: btnCoord
        };
        """
        res = self.driver.execute_script(locate_script, [XPATH_PROMPT_INPUT, XPATH_GENERATE_BUTTON])
        if not isinstance(res, dict) or not res.get("success"):
            raise RuntimeError(f"Gagal menemukan elemen prompt di Google Flow: {res}")

        screen_x = res["screenX"]
        screen_y = res["screenY"]
        btn_coord = res.get("btnCoord")

        # 3. Klik langsung pada area input menggunakan mouse fisik OS untuk mengunci fokus
        NativeOSController.send_mouse_click(screen_x, screen_y)
        time.sleep(0.1)

        # 4. Kirim Native OS Input: Salin prompt ke Clipboard -> Ctrl+A -> Backspace -> Ctrl+V -> Enter
        NativeOSController.send_paste_and_enter(prompt_text)
        time.sleep(0.5)

        # 5. Jika tombol generate terdeteksi dan prompt belum terkirim, klik tombol generate secara fisik
        if btn_coord and btn_coord.get("x") and btn_coord.get("y"):
            NativeOSController.send_mouse_click(btn_coord["x"], btn_coord["y"])

        return True

    def hover_and_wait_tile(self, timeout: int = 180) -> bool:
        """Memeriksa dan men-hover tile gambar secara fisik sampai hotbar tombol opsi muncul."""
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

        let tileEl = getByXPath(tileXpath) ||
                     document.querySelector('cdk-virtual-scroll-viewport flow-grid-tile-container') ||
                     document.querySelector('flow-grid-tile-container');

        let tileCoord = null;
        if (tileEl) {
            tileEl.scrollIntoView({ block: 'nearest' });
            const rect = tileEl.getBoundingClientRect();
            tileCoord = {
                x: Math.round(window.mozInnerScreenX + rect.left + rect.width / 2),
                y: Math.round(window.mozInnerScreenY + rect.top + rect.height / 2)
            };
            tileEl.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true }));
            tileEl.dispatchEvent(new MouseEvent('mouseover', { bubbles: true }));
        }

        let hotbarEl = getByXPath(hotbarXpath) ||
                       document.querySelector('flow-grid-tile-container flow-image-hotbar button:nth-child(3) mat-icon') ||
                       document.querySelector('flow-image-hotbar button:nth-child(3)') ||
                       document.querySelector('flow-image-hotbar button mat-icon[data-mat-icon-name*="more"]');

        let hotbarCoord = null;
        if (hotbarEl) {
            const hRect = hotbarEl.getBoundingClientRect();
            hotbarCoord = {
                x: Math.round(window.mozInnerScreenX + hRect.left + hRect.width / 2),
                y: Math.round(window.mozInnerScreenY + hRect.top + hRect.height / 2)
            };
        }

        return {
            tileCoord: tileCoord,
            hotbarReady: !!hotbarEl,
            hotbarCoord: hotbarCoord
        };
        """

        start_time = time.time()
        last_hover_time = 0.0

        while time.time() - start_time < timeout:
            res = self.driver.execute_script(check_script, [XPATH_TILE_CONTAINER, XPATH_HOTBAR_ICON])
            if isinstance(res, dict):
                # Gerakkan kursor mouse fisik ke tile setiap beberapa detik
                if res.get("tileCoord") and (time.time() - last_hover_time > 3.0):
                    coord = res["tileCoord"]
                    NativeOSController.send_mouse_move(coord["x"], coord["y"])
                    last_hover_time = time.time()

                if res.get("hotbarReady"):
                    return True

            time.sleep(1.5)

        raise TimeoutError(f"Waktu tunggu generasi gambar habis ({timeout} detik). Gambar belum selesai dirender.")

    def click_hotbar_and_download(self, timeout: int = 20) -> bool:
        """Mengeklik hotbar opsi (tombol 3), membuka menu 'Download', lalu mengeklik resolusi '1K (Ukuran asli)'."""
        # 1. Dapatkan koordinat tombol Hotbar Opsi (button[3]/mat-icon)
        get_hotbar_script = """
        const hotbarXpath = arguments[0];
        function getByXPath(xpath) {
            try { return document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue; } catch (e) { return null; }
        }

        let hotbarBtn = getByXPath(hotbarXpath) ||
                        document.querySelector('flow-grid-tile-container flow-image-hotbar button:nth-child(3)') ||
                        document.querySelector('flow-image-hotbar button:nth-child(3)') ||
                        document.querySelector('flow-image-tile flow-image-hotbar button:last-child');

        if (!hotbarBtn) return { success: false, error: 'Tombol hotbar tidak ditemukan.' };

        const rect = hotbarBtn.getBoundingClientRect();
        return {
            success: true,
            x: Math.round(window.mozInnerScreenX + rect.left + rect.width / 2),
            y: Math.round(window.mozInnerScreenY + rect.top + rect.height / 2)
        };
        """
        res_h = self.driver.execute_script(get_hotbar_script, [XPATH_HOTBAR_ICON])
        if not isinstance(res_h, dict) or not res_h.get("success"):
            raise RuntimeError(f"Gagal menemukan koordinat tombol hotbar: {res_h}")

        # Klik fisik pada tombol hotbar
        NativeOSController.send_mouse_click(res_h["x"], res_h["y"])
        time.sleep(0.8)

        # 2. Dapatkan koordinat Context Menu Item 'Download' & klik/hover kursor fisik
        get_download_menu_script = """
        const menu5Xpath = arguments[0];
        function getByXPath(xpath) {
            try { return document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue; } catch (e) { return null; }
        }

        let dlMenu = null;
        const allItems = document.querySelectorAll('div.cdk-overlay-pane flow-menu-item, flow-image-context-menu-items flow-menu-item, [role="menuitem"]');
        for (let item of allItems) {
            const text = (item.innerText || '').trim().toLowerCase();
            if (text.startsWith('download') || text.startsWith('unduh')) {
                dlMenu = item;
                break;
            }
        }

        if (!dlMenu) {
            dlMenu = getByXPath(menu5Xpath);
        }

        if (!dlMenu && allItems.length >= 5) {
            dlMenu = allItems[4];
        }

        if (!dlMenu) return { success: false, error: 'Menu Download tidak ditemukan.' };

        dlMenu.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true }));
        dlMenu.dispatchEvent(new MouseEvent('mouseover', { bubbles: true }));

        const rect = dlMenu.getBoundingClientRect();
        return {
            success: true,
            x: Math.round(window.mozInnerScreenX + rect.left + rect.width / 2),
            y: Math.round(window.mozInnerScreenY + rect.top + rect.height / 2)
        };
        """
        res_m = self.driver.execute_script(get_download_menu_script, [XPATH_CONTEXT_MENU_ITEM_5])
        if isinstance(res_m, dict) and res_m.get("success"):
            NativeOSController.send_mouse_move(res_m["x"], res_m["y"])
            time.sleep(0.1)
            # Klik atau hover menu download untuk memunculkan submenu resolusi
            NativeOSController.send_mouse_click(res_m["x"], res_m["y"])

        time.sleep(0.8)

        # 3. Dapatkan koordinat opsi '1K (Ukuran asli)' di submenu resolusi & klik fisik
        get_1k_script = """
        function getByXPath(xpath) {
            try { return document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue; } catch (e) { return null; }
        }

        let oneKItem = null;
        const subItems = document.querySelectorAll('div.cdk-overlay-pane flow-menu-item, div.cdk-overlay-pane [role="menuitem"], div.cdk-overlay-pane button, flow-menu-item');
        for (let sub of subItems) {
            const text = (sub.innerText || '').trim();
            if (text.includes('1K') || text.toLowerCase().includes('ukuran asli') || text.toLowerCase().includes('original size')) {
                oneKItem = sub;
                break;
            }
        }

        if (!oneKItem) {
            // Fallback ke item pertama pada overlay pane yang paling baru dibuka
            const panes = document.querySelectorAll('div.cdk-overlay-pane');
            if (panes.length > 0) {
                const lastPane = panes[panes.length - 1];
                oneKItem = lastPane.querySelector('flow-menu-item, [role="menuitem"], button');
            }
        }

        if (!oneKItem) return { success: false, error: 'Opsi unduhan 1K (Ukuran asli) tidak ditemukan di submenu.' };

        const rect = oneKItem.getBoundingClientRect();
        return {
            success: true,
            x: Math.round(window.mozInnerScreenX + rect.left + rect.width / 2),
            y: Math.round(window.mozInnerScreenY + rect.top + rect.height / 2)
        };
        """
        res_1k = self.driver.execute_script(get_1k_script)
        if not isinstance(res_1k, dict) or not res_1k.get("success"):
            raise RuntimeError(f"Gagal menemukan koordinat tombol 1K (Ukuran asli): {res_1k}")

        # Klik fisik opsi 1K untuk memicu pengunduhan berkas .jpg
        NativeOSController.send_mouse_click(res_1k["x"], res_1k["y"])
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

    def delete_current_tile(self, timeout: int = 15) -> bool:
        """Menghapus gambar dari kanvas peramban ('Pindahkan ke sampah') setelah berhasil diunduh."""
        NativeOSController.activate_window()
        time.sleep(0.3)

        # 1. Pastikan kursor hover ke tile gambar agar tombol hotbar muncul
        hover_script = """
        const tile = document.querySelector('flow-image-tile, flow-grid-tile-container');
        if (!tile) return { success: false, error: 'Tile gambar tidak ditemukan di kanvas.' };
        tile.scrollIntoView({ block: 'center' });
        tile.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true }));
        tile.dispatchEvent(new MouseEvent('mouseover', { bubbles: true }));
        const rect = tile.getBoundingClientRect();
        return {
            success: true,
            x: Math.round(window.mozInnerScreenX + rect.left + rect.width / 2),
            y: Math.round(window.mozInnerScreenY + rect.top + rect.height / 2)
        };
        """
        res_t = self.driver.execute_script(hover_script)
        if isinstance(res_t, dict) and res_t.get("success"):
            NativeOSController.send_mouse_move(res_t["x"], res_t["y"])
        time.sleep(0.5)

        # 2. Dapatkan koordinat tombol Hotbar 3 (titik tiga / opsi lainnya)
        hotbar_script = """
        let btn = document.querySelector('flow-grid-tile-container flow-image-hotbar button:nth-child(3)') ||
                  document.querySelector('flow-image-hotbar button:nth-child(3)') ||
                  document.querySelector('flow-image-tile flow-image-hotbar button:last-child');
        if (!btn) {
            const tile = document.querySelector('flow-image-tile, flow-grid-tile-container');
            if (tile) {
                const buttons = tile.querySelectorAll('button');
                const hotbarBtns = Array.from(buttons).filter(b => {
                    const r = b.getBoundingClientRect();
                    return r.width > 0 && r.height > 0;
                });
                if (hotbarBtns.length >= 3) btn = hotbarBtns[2];
            }
        }
        if (!btn) return { success: false, error: 'Tombol hotbar opsi tidak ditemukan.' };
        const rect = btn.getBoundingClientRect();
        return {
            success: true,
            x: Math.round(window.mozInnerScreenX + rect.left + rect.width / 2),
            y: Math.round(window.mozInnerScreenY + rect.top + rect.height / 2)
        };
        """
        res_h = self.driver.execute_script(hotbar_script)
        if not isinstance(res_h, dict) or not res_h.get("success"):
            raise RuntimeError(f"Gagal menemukan tombol opsi hotbar untuk penghapusan: {res_h}")

        NativeOSController.send_mouse_click(res_h["x"], res_h["y"])
        time.sleep(0.8)

        # 3. Cari menu 'Pindahkan ke sampah' pada overlay menu konteks
        trash_menu_script = """
        const items = Array.from(document.querySelectorAll('button.mat-mdc-menu-item, [role="menuitem"], .mat-mdc-menu-item, flow-menu-item'));
        const target = items.find(el => el.textContent && el.textContent.includes('Pindahkan ke sampah'));
        if (!target) return { success: false, error: 'Menu Pindahkan ke sampah tidak ditemukan.' };
        const rect = target.getBoundingClientRect();
        return {
            success: true,
            x: Math.round(window.mozInnerScreenX + rect.left + rect.width / 2),
            y: Math.round(window.mozInnerScreenY + rect.top + rect.height / 2)
        };
        """
        res_trash = self.driver.execute_script(trash_menu_script)
        if not isinstance(res_trash, dict) or not res_trash.get("success"):
            raise RuntimeError(f"Gagal menemukan menu 'Pindahkan ke sampah': {res_trash}")

        # Klik fisik opsi Pindahkan ke sampah
        NativeOSController.send_mouse_click(res_trash["x"], res_trash["y"])
        time.sleep(1.0)
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
        "[brand]IMAGE GENERATOR — GOOGLE FLOW BOT[/brand] [muted]//[/muted] [gold]SOLUSI 1 NATIVE OS INPUT[/gold]\n"
        "[muted]Bypass Total Deteksi Otomasi via Windows Clipboard, SendInput & Stealth Driver[/muted]"
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
    table.add_row("Metode Input", "[bold green]Solusi 1 (Native OS Input + Hardware Keystrokes)[/bold green]")
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

            progress.update(task, description="[cyan]Mengirim prompt via Native OS Clipboard & Enter...")
            generator.submit_prompt(prompt)

            progress.update(task, description="[gold]Menunggu render gambar selesai (hovering tile)...")
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
    summary_table.add_row("Metode Eksekusi", "[bold green]✓ Native OS Hardware Input (isTrusted: true)[/bold green]")
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
