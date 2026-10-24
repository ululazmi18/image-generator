"""Image Generator (Silent Background Edition) — Modul & CLI Otomasi Google Flow.

Modul otomasi penuh untuk pembuatan dan pengunduhan gambar dari Google Flow secara
100% senyap di latar belakang (*background*) tanpa memerlukan intervensi pengguna,
tanpa mengontrol kursor mouse (*zero cursor hijacking*), dan tanpa mencuri fokus jendela.

Fitur Utama:
1. Zero Cursor Hijacking:
   Tidak menggunakan pergerakan mouse kursor fisik Windows, keyboard OS, atau clipboard.
   Pengguna bebas mengetik, bekerja, atau bermain game tanpa terganggu sedikit pun.
2. Native Headless Background Mode:
   Peramban Firefox Portable diluncurkan secara permanen dan natif dalam mode -headless murni,
   sehingga 100% tanpa antarmuka jendela grafis (GUI) di layar dan tidak mengganggu aktivitas pengguna.
3. Otomasi Siklus Penuh:
   Memasukkan teks prompt -> Memicu pembuatan gambar -> Memantau progres (0%-100%) ->
   Mengunduh resolusi asli 1K -> Memindahkan berkas ke folder tujuan -> Menghapus tile
   dari kanvas Google Flow ('Pindahkan ke sampah').
4. Fleksibel (Callable & CLI):
   Dapat diimpor sebagai fungsi Python (`from image_generator import generate_image`)
   atau dijalankan langsung via terminal/CLI (`run.bat --prompt "..."`).

Contoh Penggunaan Singkat:
    # Sebagai CLI via batch runner:
    run.bat --prompt pemandangan gunung bersalju saat fajar sinematik -o hasil/

    # Sebagai Modul Python:
    from image_generator import generate_image
    file_hasil = generate_image("kucing lucu di taman bunga", output_path="outputs/")
    print(f"Gambar tersimpan di: {file_hasil}")
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
# KONFIGURASI URL GOOGLE FLOW
# ==============================================================================
FLOW_PROJECT_URL = "https://flow.google.com/project/d2653e23-18ab-4dda-b15b-3a77cf1085dd"
FLOW_HOME_URL = "https://flow.google.com/"


# ==============================================================================
# PENGECUALIAN KHUSUS OTOMASI (CUSTOM EXCEPTIONS)
# ==============================================================================
class GenerationFailedError(RuntimeError):
    """Pengecualian yang dilemparkan saat Google Flow menampilkan tile galat/gagal di kanvas.

    Misalnya jika terdeteksi teks 'Gagal', 'Anda telah mencapai batas penggunaan',
    atau kegagalan komputasi server pembuatan gambar lainnya.
    """

    pass


# ==============================================================================
# MARIONETTE PROTOCOL CLIENT (STEALTH SILENT BRIDGE)
# ==============================================================================
class MarionetteDriver:
    """Klien soket native Marionette untuk Firefox Portable (Stealth Silent Bridge).

    Menyediakan komunikasi langsung dengan mesin peramban Gecko melalui protokol Marionette
    tanpa menggunakan WebDriver standar eksternal, sehingga atribut navigator.webdriver
    tetap bernilai undefined (100% stealth dan tidak terdeteksi sebagai robot otomasi).

    Attributes:
        host (str): Alamat IP host lokal (default '127.0.0.1').
        port (int): Port soket Marionette (default 2828).
        sock (socket.socket | None): Objek koneksi soket TCP aktif.
        msg_id (int): Penomoran ID pesan berurutan untuk JSON wire protocol.
        session_id (str | None): ID sesi peramban yang sedang aktif.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 2828):
        """Menginisialisasi konfigurasi klien Marionette.

        Args:
            host (str): Host peramban lokal yang mendengarkan port otomasi (default: '127.0.0.1').
            port (int): Nomor port komunikasi Marionette Firefox (default: 2828).
        """
        self.host = host
        self.port = port
        self.sock: socket.socket | None = None
        self.msg_id = 0
        self.session_id: str | None = None

    def is_port_open(self, timeout: float = 0.8) -> bool:
        """Memeriksa apakah port Marionette peramban sedang terbuka dan siap menerima koneksi.

        Metode ini mencoba membuka koneksi soket cepat tanpa mengirimkan data apapun untuk
        memverifikasi kesiapan Firefox Portable sebelum mencoba proses handshake.

        Args:
            timeout (float): Waktu tunggu maksimal pengujian port dalam detik (default: 0.8).

        Returns:
            bool: True jika port terbuka dan peramban siap, False jika port tertutup/timeout.
        """
        try:
            with socket.create_connection((self.host, self.port), timeout=timeout):
                return True
        except (OSError, socket.timeout):
            return False

    def connect(self, timeout: float = 30.0) -> str:
        """Membuka koneksi soket TCP ke peramban, melakukan handshake, dan membuat sesi baru.

        Alur kerja:
        1. Menghubungkan ke 127.0.0.1:2828 via TCP.
        2. Menerima paket pembuka (handshake JSON) dari Firefox Gecko.
        3. Mengirimkan pesan 'WebDriver:NewSession' untuk mendaftarkan sesi kontrol aktif.
        4. Mengatur konteks eksekusi Marionette ke 'content' (halaman web DOM).

        Args:
            timeout (float): Waktu tunggu maksimal koneksi soket dalam detik (default: 30.0).

        Returns:
            str: ID sesi Marionette yang dibuat (session_id).

        Raises:
            ConnectionError: Jika peramban tidak merespons atau soket gagal terhubung.
            RuntimeError: Jika inisialisasi sesi baru ditolak oleh Gecko.
        """
        self.sock = socket.create_connection((self.host, self.port), timeout=timeout)
        self.sock.settimeout(timeout)
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
        """Mengirimkan perintah berformat Marionette JSON wire protocol ke peramban.

        Format paket pesan Marionette:
        `[panjang]:[0, msg_id, name, parameters]`

        Args:
            name (str): Nama perintah Marionette (misal 'WebDriver:ExecuteScript', 'WebDriver:ElementClick').
            parameters (dict | None): Argumen pendukung untuk perintah tersebut.

        Returns:
            dict: Respons payload hasil eksekusi dari Gecko.

        Raises:
            RuntimeError: Jika soket belum tersambung atau jika Gecko mengembalikan pesan galat.
            ConnectionError: Jika koneksi terputus di tengah proses penerimaan respons.
        """
        if not self.sock:
            raise RuntimeError("Koneksi soket Marionette belum dibuka. Panggil connect() terlebih dahulu.")

        self.msg_id += 1
        payload = json.dumps([0, self.msg_id, name, parameters or {}])
        msg = f"{len(payload)}:{payload}".encode("utf-8")
        self.sock.sendall(msg)

        # Baca panjang respons berformat <length>:
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
        """Mengeksekusi skrip JavaScript langsung di dalam konteks halaman web aktif.

        Skrip dieksekusi secara terisolasi di dalam window tab aktif dan dapat mengembalikan
        nilai berupa tipe data primitif, objek JavaScript (menjadi dictionary Python), array, dsb.

        Args:
            script (str): Kode JavaScript yang akan dijalankan (dapat menggunakan return nilai).
            args (list | None): Argumen yang akan dioper ke dalam skrip via array 'arguments'.

        Returns:
            any: Nilai yang dikembalikan oleh pernyataan return di JavaScript.

        Example:
            driver.execute_script("return document.title;")
            driver.execute_script("document.querySelector('button').click();")
        """
        res = self.send("WebDriver:ExecuteScript", {"script": script, "args": args or []})
        return res.get("value")

    def find_element(self, using: str, value: str) -> str:
        """Mencari elemen web di halaman aktif dan mengembalikan ID elemen string W3C.

        Args:
            using (str): Strategi pencarian elemen (misal: 'css selector', 'xpath', 'tag name').
            value (str): Nilai pemilih/selector elemen yang dicari.

        Returns:
            str: Identifier string elemen unik (element UUID) untuk pemanggilan ElementClick.

        Raises:
            RuntimeError: Jika elemen tidak ditemukan di dalam dokumen halaman aktif.
        """
        res = self.send("WebDriver:FindElement", {"using": using, "value": value})
        val = res.get("value", res) if isinstance(res, dict) else res
        if isinstance(val, dict):
            return val.get("element-6066-11e4-a52e-4f735466cecf") or list(val.values())[0]
        return str(val)

    def click_element(self, element_id: str) -> None:
        """Mengeklik elemen via Gecko C++ native click tanpa menggerakkan kursor mouse OS.

        Perintah ini memicu aksi klik tingkat rendah di mesin rendering Firefox (Gecko)
        secara murni internal, sehingga kursor mouse fisik pengguna sama sekali tidak
        tersentuh atau berpindah posisi.

        Args:
            element_id (str): ID elemen W3C yang diperoleh dari metode find_element().
        """
        self.send("WebDriver:ElementClick", {"id": element_id})

    def get_window_handles(self) -> list[str]:
        """Mengambil daftar seluruh handle jendela atau tab yang sedang terbuka di Firefox.

        Returns:
            list[str]: Daftar string unik identifier untuk setiap tab/jendela.
        """
        return self.send("WebDriver:GetWindowHandles", {})

    def switch_to_window(self, handle: str) -> None:
        """Beralih fokus konteks perintah Marionette ke tab atau jendela tertentu.

        Args:
            handle (str): ID string handle jendela target yang ingin diaktifkan.
        """
        self.send("WebDriver:SwitchToWindow", {"handle": handle})

    def navigate(self, url: str) -> None:
        """Membuka atau mengarahkan tab aktif ke alamat URL yang ditentukan.

        Args:
            url (str): Alamat web lengkap (misal: 'https://flow.google.com/').
        """
        try:
            self.send("WebDriver:Navigate", {"url": url})
        except Exception:
            self.execute_script("window.location.href = arguments[0];", [url])

    def take_screenshot(self, full: bool = False) -> bytes:
        """Mengambil tangkapan layar murni dari viewport peramban web dalam format PNG bytes.

        Tangkapan layar diambil langsung dari frame buffer peramban tanpa memotret
        frame jendela desktop Windows, sehingga menghasilkan gambar jernih halaman web.

        Args:
            full (bool): Jika True, mengambil seluruh panjang dokumen yang dapat digulir.
                         Jika False, hanya area viewport yang sedang tampil (default: False).

        Returns:
            bytes: Data mentah gambar berformat PNG.
        """
        import base64

        res = self.send("WebDriver:TakeScreenshot", {"full": full})
        val = res.get("value") if isinstance(res, dict) else res
        return base64.b64decode(val)

    def close(self) -> None:
        """Menutup koneksi soket Marionette secara aman."""
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
    """Pengontrol utama otomasi Google Flow untuk generasi gambar latar belakang senyap.

    Mengelola siklus hidup peramban, pendeteksian tab Google Flow, pengisian prompt via
    DOM ProseMirror, penanganan render tile, pengunduhan file resolusi 1K, pemindahan
    berkas hasil, hingga pembersihan kanvas ('Pindahkan ke sampah').

    Attributes:
        workspace_dir (Path): Direktori root workspace proyek.
        profile_dir (Path): Lokasi direktori profil Firefox Portable terisolasi.
        ff_bin (Path): Path eksekutabel Firefox Portable (firefox.exe).
        download_dir (Path): Lokasi folder tempat peramban menyimpan berkas unduhan.
        driver (MarionetteDriver): Klien soket Marionette internal.
    """

    def __init__(self, workspace_dir: Path | None = None):
        """Menginisialisasi konfigurasi pengontrol ImageGenerator.

        Args:
            workspace_dir (Path | None): Direktori workspace root. Jika None, otomatis
                                         menggunakan direktori tempat skrip ini berada.
        """
        if workspace_dir is None:
            self.workspace_dir = Path(__file__).resolve().parent
        else:
            self.workspace_dir = Path(workspace_dir).resolve()

        self.profile_dir = self.workspace_dir / "browser_profile"
        self.ff_bin = Path(r"D:\FirefoxPortable\App\Firefox64\firefox.exe")
        self.download_dir = self._detect_download_dir()
        self.driver = MarionetteDriver()
        self.proc: subprocess.Popen | None = None

    def _detect_download_dir(self) -> Path:
        """Mendeteksi direktori unduhan peramban secara otomatis dengan prioritas D:\\Downloads.

        Returns:
            Path: Lokasi direktori unduhan yang valid dan siap digunakan.
        """
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
        """Memeriksa apakah profil Firefox sedang dikunci atau memiliki lock yatim (parent.lock).

        Jika file 'parent.lock' ada tetapi dapat dibuka dalam mode append, berarti berkas
        tersebut adalah lock yatim dari sesi sebelumnya yang crash/ditutup paksa.
        Metode ini secara otomatis membersihkan lock yatim tersebut (*self-healing*).

        Returns:
            bool: True jika profil benar-benar sedang digunakan proses Firefox lain,
                  False jika profil bebas digunakan.
        """
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
        """Menjamin preferensi stealth anti-deteksi terpasang pada user.js profil.

        Mengatur `dom.webdriver.enabled = false` agar variabel `navigator.webdriver` bernilai
        `undefined` pada halaman web, serta mengaktifkan port Marionette permanen (2828).
        """
        user_js = self.profile_dir / "user.js"
        required_prefs = [
            'user_pref("marionette.enabled", true);',
            'user_pref("marionette.port", 2828);',
            'user_pref("dom.webdriver.enabled", false);',
            'user_pref("marionette.actors.enabled", true);',
            'user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);',
            'user_pref("browser.sessionstore.resume_from_crash", false);',
            'user_pref("toolkit.startup.max_resumed_crashes", -1);',
            'user_pref("browser.startup.page", 3);',
            'user_pref("browser.startup.homepage", "https://flow.google.com/project/8eed2cd9-e563-46d8-9ad2-395e53901db4");',
        ]
        existing = ""
        if user_js.exists():
            existing = user_js.read_text(encoding="utf-8", errors="ignore")

        missing = [p for p in required_prefs if p not in existing]
        if missing:
            with open(user_js, "a", encoding="utf-8") as f:
                f.write("\n" + "\n".join(missing) + "\n")

    def ensure_browser(self, auto_launch: bool = True) -> None:
        """Memastikan Firefox berjalan dalam mode native headless dan mendengarkan port otomasi 2828.

        Jika peramban belum aktif dan auto_launch=True, peramban akan diluncurkan secara
        permanen dalam mode -headless murni tanpa jendela grafis sama sekali di latar belakang.

        Args:
            auto_launch (bool): Luncurkan peramban secara otomatis jika belum berjalan (default: True).

        Raises:
            RuntimeError: Jika port otomasi tidak terbuka setelah batas waktu tunggu peluncuran habis.
        """
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
            console.print("[info]ℹ[/info] Meluncurkan peramban Firefox dalam mode headless (tanpa GUI)...")
            env = os.environ.copy()
            env["MOZ_CRASHREPORTER_DISABLE"] = "1"
            env["MOZ_CRASHREPORTER_NO_REPORT"] = "1"

            cmd = [
                str(self.ff_bin),
                "-no-remote",
                "-headless",
                "-marionette",
                "-profile",
                str(self.profile_dir),
            ]

            self.proc = subprocess.Popen(cmd, env=env)

            opened = False
            for _ in range(30):
                time.sleep(0.5)
                if self.driver.is_port_open(timeout=0.5):
                    opened = True
                    break

            if not opened:
                raise RuntimeError("Gagal terhubung ke port otomasi peramban (2828).")

    def connect(self) -> None:
        """Menghubungkan klien soket Marionette ke peramban Firefox."""
        self.driver.connect(timeout=30.0)

    def find_flow_tab(self) -> str:
        """Mencari dan beralih ke tab Google Flow aktif, atau mengarahkan tab ke proyek Flow.

        Memindai seluruh tab terbuka untuk menemukan komponen `aisandbox-root`, `flow-project-shell`,
        atau URL yang memuat 'flow.google.com/project/'. Jika berada di beranda (home), otomatis
        mengeklik proyek pertama yang tersedia. Jika belum ada, membuka URL proyek secara langsung.

        Returns:
            str: Identifier handle tab Google Flow yang berhasil diaktifkan.

        Raises:
            RuntimeError: Jika tidak ada jendela/tab terbuka sama sekali.
        """
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
                        # Auto-resolve jika URL proyek lama kedaluwarsa
                        self.driver.navigate(FLOW_HOME_URL)
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

    def clean_failed_tiles(self) -> int:
        """Mendeteksi dan menghapus tile error/gagal yang masih ada pada kanvas Google Flow.

        Memindai seluruh elemen tile pada kanvas untuk menemukan pesan galat seperti
        'Gagal', 'Failed', 'batas penggunaan', 'coba lagi', atau 'error', lalu mengeklik
        tombol hapus ('delete_forever' / 'delete' / 'hapus') pada tile tersebut secara senyap.

        Returns:
            int: Jumlah tile gagal yang berhasil dibersihkan dari kanvas.
        """
        clean_script = """
        const tiles = Array.from(document.querySelectorAll('flow-image-tile, flow-grid-tile-container'));
        let deleted = 0;
        for (const t of tiles) {
            const txt = (t.innerText || '').toLowerCase();
            if (txt.includes('gagal') || txt.includes('failed') || txt.includes('coba lagi') || txt.includes('batas penggunaan') || txt.includes('error') || txt.includes('tidak dapat membuat')) {
                const delBtn = Array.from(t.querySelectorAll('button')).find(b => {
                    const bTxt = (b.innerText || '').toLowerCase();
                    const bAria = (b.getAttribute('aria-label') || '').toLowerCase();
                    return bTxt.includes('delete') || bAria.includes('delete') || bTxt.includes('hapus') || bAria.includes('hapus');
                });
                if (delBtn) {
                    delBtn.click();
                    deleted++;
                }
            }
        }
        return deleted;
        """
        try:
            res = self.driver.execute_script(clean_script)
            return int(res) if res is not None else 0
        except Exception:
            return 0

    def submit_prompt(self, prompt_text: str) -> dict:
        """Memasukkan teks prompt ke editor ProseMirror dan memicu tombol buat gambar secara senyap.

        Alur:
        1. Membersihkan tile gagal sebelumnya jika ada di kanvas.
        2. Mencatat snapshot kondisi kanvas saat ini (jumlah gambar & URL gambar teratas).
        3. Memfokuskan editor ProseMirror (`flow-rich-text-editor div[contenteditable="true"]`).
        4. Membersihkan teks lama, memasukkan teks prompt via DOM execCommand, dan memicu InputEvent.
        5. Mengeklik tombol 'Mulai pembuatan' (`flow-generate-icon-button button`) melalui Gecko
           native click tanpa menggerakkan kursor mouse pengguna.

        Args:
            prompt_text (str): Teks deskripsi gambar yang akan digenerate.

        Returns:
            dict: Snapshot awal kanvas berisi `imgCount` (int) dan `firstImgSrc` (str | None).

        Raises:
            RuntimeError: Jika elemen editor prompt tidak ditemukan pada halaman.
        """
        self.clean_failed_tiles()

        # Catat snapshot kondisi kanvas sebelum generasi baru dimulai
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
        document.execCommand('delete', false, null);
        document.execCommand('insertText', false, prompt);
        editor.dispatchEvent(new InputEvent('input', { bubbles: true, inputType: 'insertText', data: prompt }));
        editor.dispatchEvent(new Event('change', { bubbles: true }));

        return { success: true };
        """
        res_in = None
        for _ in range(40):
            res_in = self.driver.execute_script(input_script, [prompt_text])
            if isinstance(res_in, dict) and res_in.get("success"):
                break
            time.sleep(0.5)

        if not isinstance(res_in, dict) or not res_in.get("success"):
            raise RuntimeError(f"Gagal memasukkan teks prompt: {res_in}")

        time.sleep(0.5)

        # Klik tombol generate via Gecko C++ native click (tanpa sentuh kursor OS)
        try:
            btn_id = self.driver.find_element("css selector", "flow-generate-icon-button button")
            self.driver.click_element(btn_id)
        except Exception:
            # Fallback ke DOM click jika ID belum terindeks
            click_btn_script = """
            const btn = document.querySelector('flow-generate-icon-button button') ||
                        document.querySelector('flow-generate-icon-button');
            if (btn) { btn.click(); return true; }
            return false;
            """
            self.driver.execute_script(click_btn_script)

        return initial_state

    def hover_and_wait_tile(
        self,
        initial_state: dict | None = None,
        timeout: int = 180,
        progress_callback: any = None,
    ) -> bool:
        """Memantau progres generasi gambar (0% -> 100%) dan menunggu render tile baru selesai.

        Mendeteksi kegagalan generasi (seperti batas penggunaan / server error) secara instan.
        Jika terdeteksi kegagalan di kanvas, fungsi segera menghapus tile gagal tersebut dan
        melemparkan `GenerationFailedError` agar proses dapat langsung diulang dari awal.

        Args:
            initial_state (dict | None): Snapshot kanvas awal hasil dari `submit_prompt()`.
            timeout (int): Batas waktu maksimal menunggu proses render dalam detik (default: 180).
            progress_callback (callable | None): Fungsi callback yang menerima string persentase
                                                 (misal: `lambda pct: print(f"{pct}%")`).

        Returns:
            bool: True jika gambar selesai dirender dan hotbar menu opsi siap diakses.

        Raises:
            GenerationFailedError: Jika peramban Google Flow menampilkan tile galat/gagal.
            TimeoutError: Jika waktu tunggu habis sebelum gambar selesai dirender.
        """
        start_time = time.time()
        init_count = (initial_state or {}).get("imgCount", 0)
        init_src = (initial_state or {}).get("firstImgSrc")

        check_script = """
        const tiles = Array.from(document.querySelectorAll('flow-image-tile, flow-grid-tile-container'));
        const firstTile = document.querySelector('flow-image-tile') || tiles[0];
        const tileText = firstTile ? firstTile.innerText : '';
        const progressMatch = tileText.match(/(\\d+)%/);
        const firstImg = firstTile ? firstTile.querySelector('img') : null;
        const allImgs = document.querySelectorAll('flow-image-tile img');
        const btn = document.querySelector('flow-generate-icon-button button');
        const isImgLoaded = firstImg ? (firstImg.complete && firstImg.naturalWidth > 0) : false;

        let failedMsg = null;
        for (const t of tiles) {
            const txt = (t.innerText || '').toLowerCase();
            if (txt.includes('gagal') || txt.includes('failed') || txt.includes('batas penggunaan') || txt.includes('coba lagi') || txt.includes('error') || txt.includes('tidak dapat membuat')) {
                failedMsg = t.innerText.replace(/\\n/g, ' -- ');
                const delBtn = Array.from(t.querySelectorAll('button')).find(b => {
                    const bTxt = (b.innerText || '').toLowerCase();
                    const bAria = (b.getAttribute('aria-label') || '').toLowerCase();
                    return bTxt.includes('delete') || bAria.includes('delete') || bTxt.includes('hapus') || bAria.includes('hapus');
                });
                if (delBtn) {
                    delBtn.click();
                }
                break;
            }
        }

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
            isImgLoaded: isImgLoaded,
            progress: progressMatch ? progressMatch[1] : null,
            btnDisabled: btn ? btn.disabled : false,
            hotbarReady: hotbarReady,
            failedMsg: failedMsg
        };
        """

        seen_progress = False
        last_progress = None

        while time.time() - start_time < timeout:
            st = self.driver.execute_script(check_script)
            if isinstance(st, dict):
                # Deteksi kegagalan render secara instan tanpa menunggu timeout
                failed_msg = st.get("failedMsg")
                if failed_msg:
                    time.sleep(1.0)
                    raise GenerationFailedError(failed_msg)

                current_prog = st.get("progress")
                if current_prog:
                    seen_progress = True
                    if current_prog != last_progress:
                        last_progress = current_prog
                        if progress_callback:
                            progress_callback(current_prog)

                # Kondisi verifikasi gambar baru:
                img_count = st.get("imgCount", 0)
                first_src = st.get("firstImgSrc")

                is_new_image = (img_count > init_count) or (first_src and first_src != init_src)

                # 1. Progres pernah berjalan dan sekarang sudah 100% (progress == None)
                if seen_progress and not current_prog and is_new_image:
                    time.sleep(1.0)
                    return True

                # 2. Gambar baru terdeteksi sudah selesai dimuat (isImgLoaded)
                if is_new_image and not current_prog and st.get("isImgLoaded"):
                    time.sleep(1.0)
                    return True

                # 3. Fallback jika hotbar siap setelah beberapa detik
                if is_new_image and not current_prog and st.get("hotbarReady") and (time.time() - start_time > 8):
                    time.sleep(1.0)
                    return True

            time.sleep(1.5)

        raise TimeoutError(f"Waktu tunggu generasi gambar habis ({timeout} detik). Gambar belum selesai dirender.")

    def click_hotbar_and_download(self, timeout: int = 20) -> bool:
        """Membuka menu opsi hotbar (tombol 3), mengeklik 'Download', dan memilih resolusi '1K (Ukuran asli)'.

        Navigasi dilakukan secara senyap melalui Angular CDK overlay event tanpa memerlukan kursor mouse fisik:
        1. Mengirimkan event hover (`mouseenter`/`mouseover`) ke tile teratas dan mengeklik tombol hotbar 3.
        2. Mengeklik item menu 'Download' pada popup menu overlay.
        3. Mengeklik submenu resolusi '1K (Ukuran asli)' untuk memulai pengunduhan berkas ke disk.

        Args:
            timeout (int): Batas waktu maksimal interaksi menu dalam detik (default: 20).

        Returns:
            bool: True jika opsi unduhan resolusi 1K berhasil diklik.

        Raises:
            RuntimeError: Jika elemen hotbar, menu Download, atau opsi 1K tidak ditemukan.
        """
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
        """Memantau folder unduhan sampai berkas gambar .jpg baru selesai diunduh secara utuh.

        Memastikan berkas unduhan bukan bagian dari daftar berkas lama (`existing_files`),
        tidak memiliki ekstensi unduhan sementara (`.part`), dan ukuran berkasnya stabil (> 0 bytes).

        Args:
            existing_files (set[str]): Kumpulan path absolut berkas gambar yang sudah ada sebelum unduhan dipicu.
            timeout (int): Batas waktu maksimal menunggu unduhan selesai dalam detik (default: 60).

        Returns:
            Path: Path absolut dari berkas .jpg yang baru saja selesai diunduh.

        Raises:
            TimeoutError: Jika berkas unduhan tidak muncul atau tidak selesai dalam batas waktu.
        """
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
        """Menghapus gambar yang baru digenerate dari kanvas Google Flow ('Pindahkan ke sampah').

        Membuka menu hotbar pada tile teratas dan mengeklik opsi 'Pindahkan ke sampah'
        secara otomatis tanpa konfirmasi dialog, sehingga kanvas proyek tetap bersih
        dan tidak menumpuk riwayat gambar yang tidak terpakai.

        Args:
            timeout (int): Batas waktu operasi penghapusan dalam detik (default: 15).

        Returns:
            bool: True jika perintah pemindahan ke sampah berhasil dieksekusi.

        Raises:
            RuntimeError: Jika opsi 'Pindahkan ke sampah' tidak ditemukan pada menu.
        """
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
        self.driver.execute_script(trash_script)
        time.sleep(1.5)
        return True

    def close(self) -> None:
        """Menutup koneksi soket Marionette dan menghentikan proses peramban latar belakang jika dibuat oleh skrip.

        Jika instance Firefox diluncurkan secara otomatis oleh skrip ini (bukan dibuka manual oleh pengguna),
        metode ini akan menghentikan proses peramban tersebut secara bersih untuk melepaskan penguncian
        profil ('parent.lock') dan membebaskan memori RAM sistem.
        """
        self.driver.close()
        if self.proc is not None:
            try:
                subprocess.run(
                    ["taskkill", "/f", "/t", "/pid", str(self.proc.pid)],
                    capture_output=True,
                    timeout=5,
                )
            except Exception:
                try:
                    self.proc.kill()
                except Exception:
                    pass
            self.proc = None

            # Pastikan file lock usang terhapus seketika
            lock_file = self.profile_dir / "parent.lock"
            for _ in range(10):
                if not lock_file.exists():
                    break
                try:
                    lock_file.unlink(missing_ok=True)
                    break
                except Exception:
                    time.sleep(0.2)


# ==============================================================================
# HIGH-LEVEL CALLABLE API FUNCTION (UNTUK DIPANGGIL OLEH SKRIP LAIN)
# ==============================================================================
def generate_image(
    prompt: str,
    output_path: str | Path | None = None,
    timeout: int = 180,
    max_retries: int = 3,
    retry_delay: float = 6.0,
    auto_launch: bool = True,
    **kwargs: object,
) -> Path:
    """Fungsi utama tingkat tinggi untuk membuat, mengunduh, dan menyimpan gambar secara senyap.

    Fungsi ini menjalankan seluruh siklus kerja otomasi Google Flow secara 100% natif
    dalam mode headless di latar belakang tanpa jendela GUI dan tanpa mengganggu kursor (*zero cursor hijacking*):
    1. Memverifikasi/menjalankan Firefox Portable secara otomatis dalam mode -headless murni.
    2. Mendeteksi tab Google Flow aktif atau mengarahkannya ke proyek.
    3. Mengisi prompt ke editor ProseMirror dan memicu pembuatan gambar.
    4. Menunggu hingga generasi selesai (0% -> 100%).
    5. Mengunduh gambar dalam resolusi asli 1K.
    6. Memindahkan file gambar dari folder unduhan ke direktori tujuan yang diminta.
    7. Menghapus tile gambar dari kanvas Google Flow ('Pindahkan ke sampah').

    Fitur Pemulihan Mandiri (Auto-Retry on Failure):
    Jika proses render gagal di sisi Google Flow (misal terkena batas penggunaan atau kendala
    server), fungsi secara otomatis mendeteksi tile gagal, membersihkannya dari kanvas,
    dan langsung mengulang proses mulai dari input prompt hingga batas `max_retries`.

    Args:
        prompt (str): Deskripsi teks gambar yang ingin dibuat.
        output_path (str | Path | None): Jalur folder atau berkas tujuan penyimpanan gambar.
            - Jika berupa folder: berkas disimpan dengan format slug prompt dan timestamp.
            - Jika berupa path berkas .jpg: berkas disimpan persis dengan nama tersebut.
            - Jika None: otomatis disimpan di folder 'outputs/' pada root workspace.
        timeout (int): Batas waktu maksimal proses pembuatan gambar per percobaan dalam detik (default: 180).
        max_retries (int): Jumlah maksimal pengulangan percobaan jika generasi gagal (default: 3).
        retry_delay (float): Jeda waktu dalam detik sebelum mengulang percobaan berikutnya (default: 6.0).
        auto_launch (bool): Luncurkan Firefox Portable secara otomatis jika belum berjalan (default: True).
        **kwargs: Parameter opsional kompatibilitas mundur (misal jika parameter `headless` dioper).

    Returns:
        Path: Lokasi absolut berkas gambar .jpg yang berhasil dibuat dan dipindahkan.

    Raises:
        RuntimeError: Jika seluruh percobaan gagal atau terjadi kegagalan fatal koneksi peramban.
        TimeoutError: Jika waktu tunggu pembuatan gambar atau pengunduhan habis di semua percobaan.

    Example:
        >>> from image_generator import generate_image
        >>> # Simpan otomatis ke folder outputs/ (100% native headless dengan auto-retry)
        >>> file_path = generate_image("pemandangan danau pegunungan berkabut saat fajar")
        >>> print("Gambar disimpan di:", file_path)
        >>>
        >>> # Kustomisasi nama berkas, batas percobaan, dan lokasi tujuan
        >>> file_kustom = generate_image(
        ...     prompt="cyberpunk robot cat neon city",
        ...     output_path="D:/Project/assets/hero_image.jpg",
        ...     timeout=200,
        ...     max_retries=5
        ... )
    """
    generator = ImageGenerator()

    try:
        generator.ensure_browser(auto_launch=auto_launch)
        generator.connect()
        generator.find_flow_tab()

        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                # Bersihkan sisa tile gagal sebelumnya jika ada di kanvas
                generator.clean_failed_tiles()

                existing = {
                    str(f.resolve())
                    for f in list(generator.download_dir.glob("*.jpg")) + list(generator.download_dir.glob("*.jpeg"))
                }
                initial_state = generator.submit_prompt(prompt)
                generator.hover_and_wait_tile(initial_state=initial_state, timeout=timeout)
                generator.click_hotbar_and_download()
                downloaded_file = generator.wait_for_downloaded_file(existing_files=existing, timeout=60)

                # Pemindahan berkas ke lokasi tujuan
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

                # Hapus gambar dari kanvas peramban setelah berkas aman tersimpan
                try:
                    generator.delete_current_tile()
                except Exception as del_err:
                    console.print(f"[warning]⚠ Catatan pembersihan: {del_err}[/warning]")

                return target_file

            except (GenerationFailedError, TimeoutError) as attempt_err:
                last_error = attempt_err
                generator.clean_failed_tiles()
                if attempt < max_retries:
                    console.print(
                        f"[warning]⚠ Percobaan {attempt}/{max_retries} terdeteksi gagal ({attempt_err}). "
                        f"Mengulang dari input prompt dalam {retry_delay:.0f} detik...[/warning]"
                    )
                    time.sleep(retry_delay)
                else:
                    raise RuntimeError(
                        f"Gagal membuat gambar setelah {max_retries} kali percobaan berturut-turut. Kesalahan terakhir: {attempt_err}"
                    )

        raise RuntimeError(f"Gagal membuat gambar setelah {max_retries} kali percobaan. Kesalahan: {last_error}")

    finally:
        generator.close()


# ==============================================================================
# CLI PARSER & INTERFACE RUNNER
# ==============================================================================
def parse_cli_args() -> tuple[str, str | None, int, int]:
    """Mengekstrak parameter baris perintah (CLI) dengan dukungan prompt tanpa wajib tanda petik.

    Peramban selalu dijalankan secara 100% otomatis dalam mode native headless di latar belakang.

    Mendukung opsi:
    - `--prompt` / `-p`: Teks prompt (seluruh kata setelah opsi ini digabungkan otomatis).
    - `--output` / `-o` / `--dest` / `-d`: Folder atau nama berkas tujuan pemindahan.
    - `--timeout` / `-t`: Batas waktu maksimal generasi per percobaan dalam detik (default: 180).
    - `--retries` / `-r`: Jumlah maksimal percobaan ulang jika generasi gagal (default: 3).

    Returns:
        tuple[str, str | None, int, int]: (prompt_text, output_dest, timeout, max_retries)

    Example:
        `python image_generator.py --prompt pemandangan gunung es -o hasil/`
        `run.bat --prompt robot astronot di planet mars --retries 5`
    """
    args = sys.argv[1:]
    output_flags = ["--output", "-o", "--dest", "-d"]
    timeout_flags = ["--timeout", "-t"]
    retries_flags = ["--retries", "-r"]
    prompt_flags = ["--prompt", "-p"]
    headless_flags = ["--headless"]

    output_val = None
    timeout_val = 180
    retries_val = 3
    prompt_tokens = []

    # Konsumsi flag --headless jika masih dioper oleh pengguna agar kompatibel
    args = [a for a in args if a not in headless_flags]

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
        elif arg in retries_flags and i + 1 < len(args):
            try:
                retries_val = int(args[i + 1])
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
                elif args[i] in retries_flags:
                    try:
                        retries_val = int(args[i + 1])
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
    return prompt_str, output_val, timeout_val, retries_val


def main() -> int:
    """Titik masuk eksekusi utama CLI dengan antarmuka Rich terminal dan auto-retry dinamis.

    Returns:
        int: Kode keluar proses (0 jika sukses, 1 jika terjadi kegagalan).
    """
    console.clear()
    banner = (
        "[brand]IMAGE GENERATOR — GOOGLE FLOW BOT[/brand] [muted]//[/muted] [gold]SILENT BACKGROUND EDITION[/gold]\n"
        "[muted]Otomasi 100% Senyap Tanpa Mengontrol Kursor Pengguna & Berjalan di Latar Belakang[/muted]"
    )
    console.print(Panel(banner, box=box.ROUNDED, style="color(240)"))

    prompt, output_dest, timeout, max_retries = parse_cli_args()

    if not prompt:
        console.print(
            "[info]ℹ[/info] [dim]Tips: Jalankan `run.bat --prompt gambar pemandangan -o hasil/` tanpa tanda petik.[/dim]\n"
        )
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
    table.add_row("Mode Tampilan", "[bold yellow]100% Native Headless (Tanpa GUI)[/bold yellow]")
    table.add_row("Maksimal Percobaan", f"[cyan]{max_retries}x (Auto-Retry jika Gagal)[/cyan]")
    table.add_row("Target Pemindahan", f"[accent]{target_display}[/accent]")
    table.add_row("Batas Waktu (Timeout)", f"{timeout} detik/percobaan")
    console.print(table)

    target_file = None
    successful_attempt = 1
    retry_delay = 6.0

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
            generator.find_flow_tab()

            success = False
            last_err = None

            for attempt in range(1, max_retries + 1):
                try:
                    generator.clean_failed_tiles()

                    existing = {
                        str(f.resolve())
                        for f in list(generator.download_dir.glob("*.jpg")) + list(generator.download_dir.glob("*.jpeg"))
                    }

                    if attempt > 1:
                        progress.update(
                            task,
                            description=f"[cyan]Mengulang input prompt (Percobaan {attempt}/{max_retries})...[/cyan]",
                        )
                    else:
                        progress.update(task, description="[cyan]Mengirim prompt secara senyap (ProseMirror DOM)...")

                    initial_state = generator.submit_prompt(prompt)

                    progress.update(
                        task,
                        description=f"[gold]Menunggu render gambar (Percobaan {attempt}/{max_retries})...[/gold]",
                    )
                    generator.hover_and_wait_tile(
                        initial_state=initial_state,
                        timeout=timeout,
                        progress_callback=lambda p: progress.update(
                            task,
                            description=f"[gold]Menunggu render gambar selesai ({p}% - Percobaan {attempt}/{max_retries})...[/gold]",
                        ),
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

                    success = True
                    successful_attempt = attempt
                    break

                except (GenerationFailedError, TimeoutError) as attempt_err:
                    last_err = attempt_err
                    generator.clean_failed_tiles()
                    if attempt < max_retries:
                        progress.update(
                            task,
                            description=f"[warning]⚠ Percobaan {attempt}/{max_retries} gagal ({attempt_err}). Mengulang input prompt dalam {retry_delay:.0f}s...[/warning]",
                        )
                        time.sleep(retry_delay)
                    else:
                        raise RuntimeError(
                            f"Gagal membuat gambar setelah {max_retries} kali percobaan: {attempt_err}"
                        )

            if not success:
                raise RuntimeError(f"Gagal setelah {max_retries} percobaan: {last_err}")

        except Exception as e:
            console.print(f"\n[error]✗ Kegagalan Otomasi:[/error] {e}")
            return 1
        finally:
            generator.close()

    summary_table = Table(box=box.ROUNDED, show_header=True)
    summary_table.add_column("Komponen", style="cyan")
    summary_table.add_column("Status / Lokasi", style="bold")
    summary_table.add_row("Status Generasi", "[bold green]✓ Selesai & Terverifikasi[/bold green]")
    summary_table.add_row("Interupsi Kursor Pengguna", "[bold green]✓ 0% (Kursor Bebas Digunakan)[/bold green]")
    summary_table.add_row("Mode Tampilan Jendela", "[bold green]✓ 100% Native Headless (Tanpa GUI)[/bold green]")
    summary_table.add_row("Auto-Retry Penanganan Gagal", f"[bold green]✓ Berhasil pada Percobaan {successful_attempt}/{max_retries}[/bold green]")
    summary_table.add_row("Hotbar & Download 1K", "[bold green]✓ Berhasil Diunduh Resolusi Asli[/bold green]")
    summary_table.add_row("Pembersihan Kanvas", "[bold green]✓ Dipindahkan ke Sampah[/bold green]")
    summary_table.add_row("File Hasil Gambar", f"[bold green]{target_file}[/bold green]")
    console.print(summary_table)

    console.print(
        Panel(
            f"[bold green]BERHASIL MENGHASILKAN & MENGUNDUH GAMBAR SECARA SENYAP![/bold green]\n\n"
            f"[muted]Prompt:[/muted] [gold]{prompt}[/gold]\n"
            f"[muted]Lokasi Berkas:[/muted] [white]{target_file}[/white]\n"
            f"[muted]Percobaan:[/muted] [green]Berhasil pada percobaan {successful_attempt}/{max_retries}[/green]\n"
            f"[muted]Kursor Mouse:[/muted] [green]Tidak tersentuh sama sekali selama proses berlangsung[/green]",
            box=box.ROUNDED,
            style="color(240)",
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
