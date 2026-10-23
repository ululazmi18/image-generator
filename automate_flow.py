"""Skrip Automasi Google Flow — Image Generator.

Mengotomasi input prompt dan eksekusi generasi gambar pada tab Google Flow
melalui protokol Marionette Firefox Portable secara native tanpa dependensi eksternal.
"""

import json
import os
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
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
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
# XPATH & SELECTOR TARGETS (GOOGLE FLOW)
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

FALLBACK_PROMPT_XPATHS = [
    XPATH_PROMPT_INPUT,
    "//flow-rich-text-editor//p",
    "//flow-rich-text-editor//div[@contenteditable='true']",
    "//flow-base-prompt-box//flow-rich-text-editor//p",
]

FALLBACK_BUTTON_XPATHS = [
    XPATH_GENERATE_BUTTON,
    "//flow-generate-icon-button//button",
    "//flow-base-prompt-box//flow-generate-icon-button//button",
    "//button[contains(@class, 'generate') or contains(@aria-label, 'Generate')]",
]


# ==============================================================================
# MARIONETTE NATIVE CLIENT (ZERO-DEPENDENCY)
# ==============================================================================
class MarionetteDriver:
    """Klien protokol Marionette untuk Firefox Portable."""

    def __init__(self, host: str = "127.0.0.1", port: int = 2828):
        self.host = host
        self.port = port
        self.sock: socket.socket | None = None
        self.msg_id = 0
        self.session_id: str | None = None

    def is_port_open(self, timeout: float = 1.0) -> bool:
        """Memeriksa apakah port Marionette sedang terbuka."""
        try:
            with socket.create_connection((self.host, self.port), timeout=timeout):
                return True
        except (OSError, socket.timeout):
            return False

    def connect(self, timeout: float = 5.0) -> str:
        """Menghubungkan ke soket Marionette dan membuka sesi baru."""
        self.sock = socket.create_connection((self.host, self.port), timeout=timeout)
        # Baca handshake awalan (format: <len>:{...})
        hs_len = b""
        while True:
            ch = self.sock.recv(1)
            if ch == b":":
                break
            hs_len += ch
        self.sock.recv(int(hs_len.decode("ascii")))

        # Inisialisasi NewSession
        resp = self.send("WebDriver:NewSession", {})
        self.session_id = resp.get("sessionId")
        self.send("Marionette:SetContext", {"value": "content"})
        return self.session_id or ""

    def send(self, method: str, params: dict | None = None) -> dict:
        """Mengirim pesan terenkapsulasi JSON wire protocol ke Marionette."""
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
                raise ConnectionError("Soket terputus saat membaca data respons.")
            data += chunk

        parsed = json.loads(data.decode("utf-8"))
        if parsed[2] is not None:
            raise RuntimeError(f"Galat Marionette pada {method}: {parsed[2]}")
        return parsed[3]

    def execute_script(self, script: str, args: list | None = None) -> any:
        """Mengeksekusi skrip JavaScript di konteks halaman aktif."""
        res = self.send(
            "WebDriver:ExecuteScript",
            {"script": script, "args": args or []},
        )
        if isinstance(res, dict) and "value" in res:
            return res["value"]
        return res

    def get_window_handles(self) -> list[str]:
        """Mengambil daftar seluruh tab/jendela peramban yang terbuka."""
        handles = self.send("WebDriver:GetWindowHandles")
        return handles if isinstance(handles, list) else []

    def switch_to_window(self, handle: str) -> None:
        """Beralih ke tab/jendela tertentu."""
        self.send("WebDriver:SwitchToWindow", {"handle": handle})

    def close(self) -> None:
        """Menutup koneksi soket dengan aman."""
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None


# ==============================================================================
# LOGIKA UTAMA OTOMASI
# ==============================================================================
def parse_prompt_argument() -> str:
    """Mengekstrak prompt dari argumen CLI tanpa mewajibkan tanda petik ganda.

    Contoh: python automate_flow.py --prompt gambar produk hidup
    -> 'gambar produk hidup'
    """
    args = sys.argv[1:]
    prompt_flags = ["--prompt", "-p"]

    for flag in prompt_flags:
        if flag in args:
            idx = args.index(flag)
            # Ambil semua argumen setelah flag dan satukan dengan spasi
            remaining = args[idx + 1 :]
            if remaining:
                return " ".join(remaining).strip()

    return ""


def ensure_browser_running(workspace_dir: Path) -> None:
    """Memastikan Firefox dengan profil browser_profile berjalan dengan Marionette aktif."""
    driver = MarionetteDriver()
    if driver.is_port_open(timeout=0.8):
        return

    profile_dir = workspace_dir / "browser_profile"
    starter_bat = profile_dir / "starter.bat"
    ff_bin = Path(r"D:\FirefoxPortable\App\Firefox64\firefox.exe")

    # Cek apakah Firefox sedang berjalan tanpa Marionette
    lock_file = profile_dir / "parent.lock"
    if lock_file.exists():
        console.print(
            Panel(
                "[warning]⚠ Firefox terdeteksi sedang berjalan tetapi port otomasi (2828) belum aktif.[/warning]\n"
                "[muted]Kemungkinan Firefox diluncurkan sebelum penambahan flag otomasi.[/muted]\n\n"
                "Silakan tutup jendela Firefox tersebut, lalu skrip ini akan meluncurkannya kembali secara otomatis.",
                title="[gold]Port Otomasi Belum Terhubung[/gold]",
                box=box.ROUNDED,
            )
        )
        Prompt.ask("[cyan]Tekan Enter setelah Anda menutup jendela Firefox...[/cyan]")

    console.print("[info]ℹ[/info] Meluncurkan peramban Firefox Portable dengan profil terisolasi...")
    env = os.environ.copy()
    env["MOZ_CRASHREPORTER_DISABLE"] = "1"
    env["MOZ_CRASHREPORTER_NO_REPORT"] = "1"

    cmd = [str(ff_bin), "-no-remote", "-marionette", "-profile", str(profile_dir)]
    subprocess.Popen(cmd, env=env)

    # Tunggu soket Marionette terbuka
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Menunggu kesiapan engine browser...", total=None)
        opened = False
        for _ in range(30):
            time.sleep(0.5)
            if driver.is_port_open(timeout=0.5):
                opened = True
                break

    if not opened:
        console.print("[error]✗[/error] Gagal terhubung ke peramban pada port 2828.")
        sys.exit(1)

    console.print("[success]✓[/success] Peramban siap dan port otomasi aktif.")


def find_google_flow_tab(driver: MarionetteDriver) -> str | None:
    """Mencari tab yang memuat aplikasi Google Flow (AI Sandbox)."""
    handles = driver.get_window_handles()
    if not handles:
        return None

    # Skrip deteksi elemen inti Google Flow
    detection_script = """
    return {
        url: window.location.href,
        title: document.title,
        hasFlowShell: !!document.querySelector('aisandbox-root, flow-project-shell, flow-prompt-box'),
        hasRichEditor: !!document.querySelector('flow-rich-text-editor')
    };
    """

    for handle in handles:
        try:
            driver.switch_to_window(handle)
            info = driver.execute_script(detection_script)
            if not isinstance(info, dict):
                continue

            url = (info.get("url") or "").lower()
            title = (info.get("title") or "").lower()
            has_flow = info.get("hasFlowShell") or info.get("hasRichEditor")

            if has_flow or "flow" in url or "flow" in title or "aisandbox" in url:
                return handle
        except Exception:
            continue

    return None


def inject_prompt_and_generate(driver: MarionetteDriver, prompt_text: str) -> dict:
    """Memasukkan teks prompt ke dalam editor dan memicu tombol eksekusi."""
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
        // Fallback pencarian fleksibel
        editorEl = document.querySelector('flow-rich-text-editor div[contenteditable="true"]') ||
                   document.querySelector('flow-rich-text-editor div div p') ||
                   document.querySelector('flow-rich-text-editor p') ||
                   document.querySelector('flow-prompt-box [contenteditable="true"]');
    }

    if (!editorEl) {
        return { success: false, step: 'find_input', error: 'Elemen input prompt tidak ditemukan pada DOM.' };
    }

    // 2. Fokus dan isi konten teks
    editorEl.focus();
    
    // Pilih seluruh konten jika ada teks lama
    const sel = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents(editorEl);
    sel.removeAllRanges();
    sel.addRange(range);

    // Gunakan execCommand agar terikat sempurna ke Angular / Material binding
    let inserted = document.execCommand('insertText', false, promptText);
    if (!inserted || !editorEl.innerText.includes(promptText.trim())) {
        editorEl.innerText = promptText;
        editorEl.dispatchEvent(new Event('input', { bubbles: true }));
        editorEl.dispatchEvent(new Event('change', { bubbles: true }));
    }

    // 3. Cari tombol eksekusi
    let btnEl = getByXPath(buttonXpath);
    if (!btnEl) {
        btnEl = document.querySelector('flow-generate-icon-button button') ||
                document.querySelector('flow-generate-icon-button') ||
                document.querySelector('flow-base-prompt-box button.generate-button') ||
                document.querySelector('flow-base-prompt-box button[aria-label*="Generate"]');
    }

    // 4. Klik tombol dan tekan Enter
    let buttonClicked = false;
    if (btnEl) {
        // Jika elemen adalah span, klik button pembungkusnya bila tersedia
        const clickable = btnEl.closest ? (btnEl.closest('button') || btnEl) : btnEl;
        clickable.click();
        buttonClicked = true;
    }

    // Kirim event Keyboard Enter sebagai fallback/pelengkap eksekusi
    editorEl.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
    editorEl.dispatchEvent(new KeyboardEvent('keypress', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
    editorEl.dispatchEvent(new KeyboardEvent('keyup', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));

    return {
        success: true,
        inputFound: true,
        buttonClicked: buttonClicked,
        finalText: editorEl.innerText
    };
    """

    res = driver.execute_script(script, [XPATH_PROMPT_INPUT, XPATH_GENERATE_BUTTON, prompt_text])
    return res if isinstance(res, dict) else {"success": False, "error": str(res)}


# ==============================================================================
# ENTRYPOINT CLI
# ==============================================================================
def main() -> int:
    console.clear()
    banner = (
        "[brand]GOOGLE FLOW AUTOMATION BOT[/brand] [muted]//[/muted] [gold]IMAGE GENERATOR[/gold]\n"
        "[muted]Pengirim Prompt Otomatis ke Antarmuka AI Sandbox Flow[/muted]"
    )
    console.print(Panel(banner, box=box.ROUNDED, style="color(240)"))

    workspace_dir = Path(__file__).resolve().parent

    # 1. Ekstraksi argumen prompt
    prompt = parse_prompt_argument()
    if not prompt:
        console.print("[info]ℹ[/info] [dim]Tips: Anda dapat langsung menjalankan `python automate_flow.py --prompt teks prompt` tanpa tanda petik.[/dim]\n")
        prompt = Prompt.ask("[cyan]Masukkan Prompt Generasi Gambar[/cyan]")

    if not prompt.strip():
        console.print("[error]✗[/error] Prompt tidak boleh kosong.")
        return 1

    table = Table(box=box.ROUNDED, show_header=False, expand=True)
    table.add_column("Parameter", style="cyan", width=20)
    table.add_column("Nilai", style="bold white")
    table.add_row("Prompt Teks", f"[gold]{prompt}[/gold]")
    table.add_row("Folder Profil", str(workspace_dir / "browser_profile"))
    table.add_row("Port Marionette", "127.0.0.1:2828")
    console.print(table)

    # 2. Pastikan peramban berjalan
    ensure_browser_running(workspace_dir)

    # 3. Hubungkan ke Marionette
    driver = MarionetteDriver()
    try:
        driver.connect(timeout=5.0)
    except Exception as e:
        console.print(f"[error]✗[/error] Gagal terhubung ke Marionette: {e}")
        return 1

    try:
        # 4. Cari Tab Google Flow
        console.print("[info]ℹ[/info] Memindai tab peramban untuk mendeteksi Google Flow...")
        target_handle = find_google_flow_tab(driver)

        if not target_handle:
            console.print(
                Panel(
                    "[warning]⚠ Tab Google Flow tidak terdeteksi di jendela peramban aktif.[/warning]\n\n"
                    "Langkah yang dapat dilakukan:\n"
                    "1. Buka tab Google Flow ([https://labs.google/flow](https://labs.google/flow)) di peramban Firefox Anda.\n"
                    "2. Masuk ke halaman proyek yang dituju.\n"
                    "3. Jalankan kembali perintah ini.",
                    title="[gold]Tab Tidak Ditemukan[/gold]",
                    box=box.ROUNDED,
                )
            )
            return 1

        driver.switch_to_window(target_handle)
        console.print("[success]✓[/success] Berhasil beralih ke tab Google Flow.")

        # 5. Masukkan Prompt & Eksekusi
        console.print("[info]ℹ[/info] Memasukkan prompt ke editor teks dan mengeksekusi generasi...")
        result = inject_prompt_and_generate(driver, prompt)

        if not result.get("success"):
            console.print(f"[error]✗[/error] Gagal mengirim prompt: {result.get('error')}")
            return 1

        # 6. Ringkasan & Status Bersambung
        status_table = Table(box=box.ROUNDED, show_header=True)
        status_table.add_column("Komponen", style="cyan")
        status_table.add_column("Status", style="bold")
        status_table.add_row("Area Input Prompt", "[bold green]✓ Terisi Sempurna[/bold green]")
        status_table.add_row("Tombol Eksekusi / Enter", "[bold green]✓ Ditekan[/bold green]" if result.get("buttonClicked") else "[bold yellow]⚠ Enter Terkirim[/bold yellow]")
        console.print(status_table)

        summary_text = (
            "[bold green]PROMPT BERHASIL DIKIRIM KE GOOGLE FLOW![/bold green]\n\n"
            f"[muted]Prompt:[/muted] [gold]{prompt}[/gold]\n\n"
            "[accent]BERSAMBUNG (Tahap Berikutnya):[/accent]\n"
            "[muted]Sesi diserahkan kembali. Tahap berikutnya adalah menyiapkan deteksi status generasi:\n"
            "• Memantau proses rendering (InProgress)\n"
            "• Mendeteksi hasil generasi selesai (Completed)\n"
            "• Menangani jika terjadi kegagalan/kuota habis (Failed)[/muted]"
        )
        console.print(Panel(summary_text, box=box.ROUNDED, style="color(240)"))

    finally:
        driver.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
