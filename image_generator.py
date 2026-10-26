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
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

# Standar encoding UTF-8 untuk terminal Windows
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

__all__ = [
    "ImageGenerator",
    "generate_image",
    "generate",
    "GenerationConfig",
    "GenerationResult",
    "GenerationFailedError",
    "AVAILABLE_MODELS",
    "AVAILABLE_ASPECT_RATIOS",
    "AVAILABLE_COUNTS",
    "DEFAULT_MODEL",
    "DEFAULT_ASPECT_RATIO",
    "DEFAULT_COUNT",
    "normalize_model",
    "normalize_aspect_ratio",
    "normalize_count",
]


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
FLOW_HOME_URL = "https://flow.google.com/"


# ==============================================================================
# KONFIGURASI & STANDARISASI SETELAN PEMBUATAN GAMBAR (GENERATION SETTINGS)
# ==============================================================================
AspectRatioType = Literal["16:9", "4:3", "1:1", "3:4", "9:16"]
ModelType = Literal["Nano Banana Pro", "Nano Banana 2 Lite", "Nano Banana 2.1"]
CountType = Literal[1, 2, 3, 4, "x1", "x2", "x3", "x4"]

DEFAULT_MODEL: str = "Nano Banana Pro"
DEFAULT_ASPECT_RATIO: str = "16:9"
DEFAULT_COUNT: int = 1

AVAILABLE_MODELS: list[str] = [
    "Nano Banana Pro",
    "Nano Banana 2 Lite",
    "Nano Banana 2.1",
]

AVAILABLE_ASPECT_RATIOS: list[str] = [
    "16:9",
    "4:3",
    "1:1",
    "3:4",
    "9:16",
]

AVAILABLE_COUNTS: list[int] = [1, 2, 3, 4]

# Pemetaan alias percakapan/fleksibel ke nama model resmi Google Flow
MODEL_ALIASES: dict[str, str] = {
    "pro": "Nano Banana Pro",
    "banana pro": "Nano Banana Pro",
    "nano banana pro": "Nano Banana Pro",
    "lite": "Nano Banana 2 Lite",
    "2 lite": "Nano Banana 2 Lite",
    "banana lite": "Nano Banana 2 Lite",
    "banana 2 lite": "Nano Banana 2 Lite",
    "nano banana 2 lite": "Nano Banana 2 Lite",
    "2.1": "Nano Banana 2.1",
    "banana 2.1": "Nano Banana 2.1",
    "nano banana 2.1": "Nano Banana 2.1",
}

# Pemetaan alias rasio ke format standar kanonikal
RATIO_ALIASES: dict[str, str] = {
    "16:9": "16:9",
    "16/9": "16:9",
    "16-9": "16:9",
    "landscape": "16:9",
    "wide": "16:9",
    "horizontal": "16:9",
    "4:3": "4:3",
    "4/3": "4:3",
    "4-3": "4:3",
    "standard": "4:3",
    "1:1": "1:1",
    "1/1": "1:1",
    "1-1": "1:1",
    "square": "1:1",
    "kotak": "1:1",
    "persegi": "1:1",
    "3:4": "3:4",
    "3/4": "3:4",
    "3-4": "3:4",
    "portrait": "3:4",
    "9:16": "9:16",
    "9/16": "9:16",
    "9-16": "9:16",
    "vertical": "9:16",
    "story": "9:16",
    "reel": "9:16",
    "shorts": "9:16",
    "tiktok": "9:16",
}

# Pemetaan nama icon Angular Material pada chip ringkasan setelan
RATIO_ICON_MAP: dict[str, str] = {
    "16:9": "crop_16_9",
    "4:3": "crop_landscape",
    "1:1": "crop_square",
    "3:4": "crop_portrait",
    "9:16": "crop_9_16",
}


def normalize_model(val: str | None) -> str:
    """Menormalkan input nama model AI ke format kanonikal resmi Google Flow.

    Mendukung variasi penulisan seperti 'pro', 'lite', '2.1', 'Nano Banana Pro', dll.

    Args:
        val (str | None): Input nama model.

    Returns:
        str: Nama model kanonikal resmi Google Flow.
    """
    if not val:
        return DEFAULT_MODEL
    clean = str(val).strip().lower()
    if clean in MODEL_ALIASES:
        return MODEL_ALIASES[clean]
    for m in AVAILABLE_MODELS:
        if clean in m.lower():
            return m
    return DEFAULT_MODEL


def normalize_aspect_ratio(val: str | None) -> str:
    """Menormalkan input aspek rasio gambar ke format standar kanonikal Google Flow.

    Mendukung variasi seperti '16:9', '1:1', 'square', 'vertical', 'shorts', 'landscape', dll.

    Args:
        val (str | None): Input nilai rasio.

    Returns:
        str: Nilai rasio standar ('16:9', '4:3', '1:1', '3:4', '9:16').
    """
    if not val:
        return DEFAULT_ASPECT_RATIO
    clean = str(val).strip().lower()
    if clean in RATIO_ALIASES:
        return RATIO_ALIASES[clean]
    for r in AVAILABLE_ASPECT_RATIOS:
        if clean == r:
            return r
    return DEFAULT_ASPECT_RATIO


def normalize_count(val: int | str | None) -> str:
    """Menormalkan input jumlah variasi gambar per generasi ke format string ('x1', 'x2', 'x3', 'x4').

    Args:
        val (int | str | None): Jumlah gambar (1, 2, 3, 4 atau 'x1', 'x2', dst).

    Returns:
        str: Format string kuantitas resmi ('x1', 'x2', 'x3', 'x4').
    """
    if not val:
        return f"x{DEFAULT_COUNT}"
    s = str(val).strip().lower()
    if s in ("1", "x1"):
        return "x1"
    elif s in ("2", "x2"):
        return "x2"
    elif s in ("3", "x3"):
        return "x3"
    elif s in ("4", "x4"):
        return "x4"
    return f"x{DEFAULT_COUNT}"


@dataclass
class GenerationConfig:
    """Objek konfigurasi parameter pembuatan gambar untuk layanan modul Python."""

    model: str = DEFAULT_MODEL
    aspect_ratio: str = DEFAULT_ASPECT_RATIO
    count: int = DEFAULT_COUNT

    def normalized(self) -> tuple[str, str, str]:
        """Mengembalikan tuple ternormalisasi (model_resmi, aspek_rasio, string_kuantitas)."""
        return (
            normalize_model(self.model),
            normalize_aspect_ratio(self.aspect_ratio),
            normalize_count(self.count),
        )


@dataclass
class GenerationResult:
    """Hasil keluaran proses pembuatan gambar lengkap dengan metadata teknis."""

    file_path: Path
    prompt: str
    model: str
    aspect_ratio: str
    count: str
    attempt: int
    duration_seconds: float
    file_paths: list[Path] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.file_paths and self.file_path:
            self.file_paths = [self.file_path]
        elif self.file_paths and not self.file_path:
            self.file_path = self.file_paths[0]

    def __str__(self) -> str:
        return str(self.file_path)

    def __fspath__(self) -> str:
        return str(self.file_path)


def resolve_target_file_path(
    output_path: str | Path | None,
    prompt: str,
    index: int,
    total_count: int,
    workspace_dir: Path,
    timestamp: str | None = None,
) -> Path:
    """Menentukan path tujuan berkas gambar hasil generasi sesuai konvensi penamaan standar.

    Aturan Penamaan:
    1. Jika total_count == 1:
       - Nama file spesifik (misal: 'testd.jpg'): disimpan sebagai 'testd.jpg'.
       - Direktori / None: disimpan sebagai '{slug}_{timestamp}.jpg'.
    2. Jika total_count >= 2:
       - Nama file spesifik (misal: 'testd.jpg'): langsung diberi penomoran '-1', '-2', dst
         (contoh: 'testd-1.jpg', 'testd-2.jpg', dst; tidak menggunakan 'testd.jpg' murni).
       - Direktori / None: disimpan sebagai '{slug}_{timestamp}-1.jpg', '{slug}_{timestamp}-2.jpg', dst.

    Args:
        output_path (str | Path | None): Lokasi atau nama file tujuan.
        prompt (str): Prompt teks untuk pembentukan slug jika disimpan di folder.
        index (int): Indeks gambar saat ini (0-indexed: 0, 1, 2, ...).
        total_count (int): Jumlah total gambar yang dihasilkan dan diunduh.
        workspace_dir (Path): Direktori workspace root.
        timestamp (str | None): Timestamp seragam format '%Y%m%d_%H%M%S'.

    Returns:
        Path: Path absolut target penyimpanan berkas.
    """
    if timestamp is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    if output_path is None:
        dest_dir = workspace_dir / "outputs"
        dest_dir.mkdir(parents=True, exist_ok=True)
        slug = re.sub(r"[^\w\s-]", "", prompt)[:30].strip().replace(" ", "_") or "image"
        if total_count >= 2:
            return dest_dir / f"{slug}_{timestamp}-{index + 1}.jpg"
        return dest_dir / f"{slug}_{timestamp}.jpg"

    target_path = Path(output_path).resolve()
    if target_path.is_dir() or (not target_path.suffix and not target_path.exists()):
        target_path.mkdir(parents=True, exist_ok=True)
        slug = re.sub(r"[^\w\s-]", "", prompt)[:30].strip().replace(" ", "_") or "image"
        if total_count >= 2:
            return target_path / f"{slug}_{timestamp}-{index + 1}.jpg"
        return target_path / f"{slug}_{timestamp}.jpg"

    target_path.parent.mkdir(parents=True, exist_ok=True)
    suffix = target_path.suffix or ".jpg"
    stem = target_path.stem

    if total_count >= 2:
        return target_path.parent / f"{stem}-{index + 1}{suffix}"
    return target_path.parent / f"{stem}{suffix}"


# ==============================================================================
# PENGECUALIAN KHUSUS OTOMASI (CUSTOM EXCEPTIONS)
# ==============================================================================
class GenerationFailedError(RuntimeError):
    """Pengecualian yang dilemparkan saat Google Flow menampilkan tile galat/gagal di kanvas."""

    pass


class QuotaExceededError(GenerationFailedError):
    """Pengecualian yang dilemparkan saat akun Google Flow mencapai batas penggunaan (rate limit / quota)."""

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

        # Menginjeksi ekstensi stealth native Gecko untuk mengeliminasi flag navigator.webdriver
        self._install_stealth_addon()

        return self.session_id

    def _install_stealth_addon(self) -> None:
        """Mengompilasi dan menginstal WebExtension stealth secara otomatis ke sesi Marionette."""
        addon_dir = Path(__file__).resolve().parent / "stealth_addon"
        manifest_file = addon_dir / "manifest.json"
        if not manifest_file.exists():
            return

        xpi_path = addon_dir / "stealth_addon.xpi"
        try:
            with zipfile.ZipFile(xpi_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                for item in addon_dir.iterdir():
                    if item.name.endswith(".xpi"):
                        continue
                    if item.is_file():
                        zf.write(item, item.name)

            self.send("Addon:Install", {"path": str(xpi_path.resolve()), "temporary": True})
        except Exception:
            # Tetap lanjutkan jika instalasi addon gagal agar tidak menghambat operasional
            pass

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

    def send_keys(self, element_id: str, text: str) -> None:
        """Mengirimkan pengetikan teks native (Gecko C++ keystrokes) ke elemen input.

        Aksi ini memicu event input, keydown, dan keyup asli peramban sehingga model
        state editor kompleks (seperti ProseMirror di Google Flow) terbarui secara instan.

        Args:
            element_id (str): Identifier elemen W3C hasil find_element().
            text (str): Teks yang akan diketikkan ke dalam elemen.
        """
        self.send("WebDriver:ElementSendKeys", {"id": element_id, "text": text})

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

    def close_window(self) -> list[str]:
        """Menutup tab atau jendela yang sedang aktif dan mengembalikan sisa handles."""
        return self.send("WebDriver:CloseWindow", {})

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

    def __init__(
        self,
        workspace_dir: Path | None = None,
        model: str = DEFAULT_MODEL,
        aspect_ratio: str = DEFAULT_ASPECT_RATIO,
        count: int | str = DEFAULT_COUNT,
        email: str | None = None,
        password: str | None = None,
        debug: bool = False,
    ):
        """Menginisialisasi konfigurasi pengontrol ImageGenerator.

        Args:
            workspace_dir (Path | None): Direktori workspace root. Jika None, otomatis
                                         menggunakan direktori tempat skrip ini berada.
            model (str): Nama rangkaian model AI (default: 'Nano Banana Pro').
            aspect_ratio (str): Aspek rasio gambar ('16:9', '4:3', '1:1', '3:4', '9:16').
            count (int | str): Kuantitas variasi gambar per generasi (1, 2, 3, 4 atau 'x1', 'x2', dst).
            email (str | None): Alamat email Google opsional untuk login otomatis.
            password (str | None): Kata sandi Google opsional untuk login otomatis.
            debug (bool): Mengaktifkan mode debug dengan dokumentasi tangkapan layar visual (default: False).
        """
        if workspace_dir is None:
            self.workspace_dir = Path(__file__).resolve().parent
        else:
            self.workspace_dir = Path(workspace_dir).resolve()

        self.model = normalize_model(model)
        self.aspect_ratio = normalize_aspect_ratio(aspect_ratio)
        self.count_str = normalize_count(count)
        self.email = email
        self.password = password

        # Deteksi profil peramban (lokal, environment variable, atau dari repo browser tetangga)
        custom_profile = os.environ.get("BROWSER_PROFILE")
        if custom_profile:
            self.profile_dir = Path(custom_profile).resolve()
        else:
            local_profile = self.workspace_dir / "browser_profile"
            neighbor_profiles = [
                local_profile,
                self.workspace_dir / "firefox-stealth-automation" / "browser_profile",
                self.workspace_dir.parent / "firefox-stealth-automation" / "browser_profile",
                self.workspace_dir.parent / "browser" / "browser_profile",
                self.workspace_dir.parent / "browser_profile",
                Path(r"D:\FirefoxPortable\Data\profile"),
            ]
            self.profile_dir = next((p for p in neighbor_profiles if p.exists()), local_profile)

        # Deteksi binary Firefox Portable (lokal, environment variable, atau repo browser)
        custom_bin = os.environ.get("FIREFOX_BIN")
        if custom_bin:
            self.ff_bin = Path(custom_bin).resolve()
        else:
            default_ff = Path(r"D:\FirefoxPortable\App\Firefox64\firefox.exe")
            neighbor_bins = [
                self.workspace_dir / "firefox_portable" / "App" / "Firefox64" / "firefox.exe",
                self.workspace_dir / "firefox-stealth-automation" / "firefox_portable" / "App" / "Firefox64" / "firefox.exe",
                self.workspace_dir.parent / "firefox-stealth-automation" / "firefox_portable" / "App" / "Firefox64" / "firefox.exe",
                self.workspace_dir.parent / "browser" / "firefox_portable" / "App" / "Firefox64" / "firefox.exe",
                self.workspace_dir.parent / "firefox_portable" / "App" / "Firefox64" / "firefox.exe",
                default_ff,
            ]
            self.ff_bin = next((b for b in neighbor_bins if b.exists()), default_ff)

        self.download_dirs = self._detect_download_dirs()
        self.driver = MarionetteDriver()
        self.proc: subprocess.Popen | None = None
        self.debug = debug
        self.debug_dir = self.workspace_dir / "debug"
        if self.debug:
            self.debug_dir.mkdir(parents=True, exist_ok=True)

        # Brankas Sesi Multi-Akun Ringan (Zero-Bloat Single Profile Vault)
        self.vault_dir = self.profile_dir / "accounts"
        self.vault_dir.mkdir(parents=True, exist_ok=True)

    def capture_debug_screenshot(self, step_name: str, description: str = "") -> Path | None:
        """Mengambil tangkapan layar viewport peramban untuk dokumentasi visual saat mode debug aktif.

        Args:
            step_name (str): Label pengenal langkah proses (misal: '01_canvas_ready').
            description (str): Keterangan penjelasan langkah untuk ditampilkan pada log terminal.

        Returns:
            Path | None: Lokasi berkas gambar .png yang disimpan jika debug aktif, atau None.
        """
        if not self.debug:
            return None
        try:
            self.debug_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_step = re.sub(r"[^\w\-_]", "_", step_name).strip("_")
            filename = f"{timestamp}_{safe_step}.png"
            filepath = self.debug_dir / filename
            png_bytes = self.driver.take_screenshot(full=False)
            filepath.write_bytes(png_bytes)
            if description:
                console.print(
                    f"[dim magenta]📸 [DEBUG VISUAL][/dim magenta] [dim]{description}[/dim] -> [link=file:///{filepath.as_posix()}]{filepath.name}[/link]"
                )
            return filepath
        except Exception as err:
            if self.debug:
                console.print(f"[dim warning]⚠ [DEBUG GAGAL TANGKAP LAYAR]: {err}[/dim warning]")
            return None

    @property
    def download_dir(self) -> Path:
        """Direktori unduhan utama untuk kompatibilitas mundur."""
        return self.download_dirs[0]

    def _detect_download_dirs(self) -> list[Path]:
        """Mendeteksi semua direktori unduhan potensial peramban di Windows.

        Memeriksa folder Downloads pengguna Windows, D:\\Downloads, dan direktori lokal workspace.

        Returns:
            list[Path]: Daftar direktori unduhan yang ada di sistem dan siap dipindai.
        """
        candidates = [
            Path.home() / "Downloads",
            Path(r"D:\Downloads"),
            self.workspace_dir / "downloads",
        ]
        dirs = [c for c in candidates if c.exists()]
        if not dirs:
            default_dir = Path.home() / "Downloads"
            default_dir.mkdir(parents=True, exist_ok=True)
            dirs.append(default_dir)
        return dirs

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
        if not self.profile_dir.exists():
            return

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
            'user_pref("browser.startup.homepage", "https://flow.google.com/");',
        ]
        existing = ""
        if user_js.exists():
            existing = user_js.read_text(encoding="utf-8", errors="ignore")

        missing = [p for p in required_prefs if p not in existing]
        if missing:
            try:
                with open(user_js, "a", encoding="utf-8") as f:
                    f.write("\n" + "\n".join(missing) + "\n")
            except Exception:
                pass

    def ensure_browser(self, auto_launch: bool = True) -> None:
        """Memastikan peramban Firefox berjalan dan mendengarkan port otomasi Marionette (2828).

        Jika peramban sudah berjalan dari Repo Browser (port 2828 terbuka), metode ini
        akan langsung menggunakan sesi peramban tersebut tanpa gangguan.
        Jika belum berjalan, metode ini akan mencoba meluncurkannya secara otomatis di latar belakang.

        Args:
            auto_launch (bool): Luncurkan peramban secara otomatis jika belum berjalan (default: True).

        Raises:
            RuntimeError: Jika port otomasi tidak terbuka setelah batas waktu tunggu peluncuran habis.
        """
        self._ensure_stealth_preferences()

        # 1. Cek apakah port otomasi Marionette (2828) sudah aktif dari Repo Browser
        if self.driver.is_port_open(timeout=0.8):
            return

        # 2. Jika belum aktif, periksa apakah executable Firefox tersedia untuk diluncurkan otomatis
        if not self.ff_bin.exists():
            console.print(
                Panel(
                    "[bold yellow]Port otomasi Marionette (127.0.0.1:2828) belum aktif.[/bold yellow]\n\n"
                    "Repositori [brand]Image Generator[/brand] ini beroperasi sebagai klien generasi gambar yang terkoneksi ke [cyan]Repo Browser[/cyan].\n\n"
                    "[bold white]Petunjuk Menyiapkan Peramban:[/bold white]\n"
                    "1. Buka dan jalankan peramban dari repositori [cyan]firefox-stealth-automation[/cyan] (port 2828 aktif).\n"
                    "2. Atau salin folder [cyan]browser_profile[/cyan] dan [cyan]firefox_portable[/cyan] ke dalam folder proyek ini.\n"
                    "3. Atau atur variabel lingkungan [cyan]FIREFOX_BIN[/cyan] dan [cyan]BROWSER_PROFILE[/cyan].",
                    title="[gold]Menunggu Koneksi Peramban (Port 2828)[/gold]",
                    box=box.ROUNDED,
                )
            )
            raise RuntimeError(
                "Port otomasi peramban (2828) belum aktif dan biner Firefox belum ditemukan. "
                "Silakan jalankan peramban atau salin folder browser_profile & firefox_portable terlebih dahulu."
            )

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
                raise RuntimeError(
                    "Gagal terhubung ke port otomasi peramban (2828). "
                    "Pastikan peramban dari repo browser berjalan dan mendengarkan port 2828."
                )

    def connect(self) -> None:
        """Menghubungkan klien soket Marionette ke peramban Firefox."""
        self.driver.connect(timeout=30.0)

    def cleanup_extra_tabs(self, keep_handle: str | None = None) -> str:
        """Menutup seluruh tab tambahan yang tidak digunakan sehingga hanya tersisa satu tab bersih.

        Args:
            keep_handle (str | None): ID handle tab yang ingin dipertahankan (opsional).

        Returns:
            str: ID handle tab yang tersisa dan aktif.
        """
        handles = self.driver.get_window_handles()
        if len(handles) <= 1:
            if handles:
                self.driver.switch_to_window(handles[0])
                return handles[0]
            raise RuntimeError("Tidak ada tab peramban yang terbuka.")

        target_handle = keep_handle if (keep_handle and keep_handle in handles) else handles[0]
        for h in handles:
            if h != target_handle:
                try:
                    self.driver.switch_to_window(h)
                    self.driver.close_window()
                except Exception:
                    pass

        self.driver.switch_to_window(target_handle)
        return target_handle

    def prompt_and_login_if_needed(
        self,
        email: str | None = None,
        password: str | None = None,
        force: bool = False,
    ) -> bool:
        """Memeriksa status login Google Flow dan membantu proses login secara langsung & otomatis.

        Jika sesi akun Google belum terhubung atau telah kedaluwarsa (atau jika force=True):
        1. Menampilkan panel informasi yang jelas dan ramah kepada pengguna.
        2. Menawarkan bantuan langsung di terminal untuk menghubungkan akun Google Flow (100% Full CLI).
        3. Menjalankan modul otomasi login headless mandiri (via Chromium Playwright lokal).
        4. Menyimpan token autentikasi (cookies.sqlite) langsung ke profil peramban.
        5. Meluncurkan ulang peramban dan melanjutkan alur generasi gambar secara mulus.

        Args:
            email (str | None): Alamat email Google Flow opsional.
            password (str | None): Kata sandi Google Flow opsional.
            force (bool): Paksa alur login akun baru meskipun peramban sedang memiliki sesi aktif.

        Returns:
            bool: True jika akun berhasil terhubung dan siap digunakan.

        Raises:
            RuntimeError: Jika pengguna menolak bantuan login atau autentikasi gagal.
        """
        curr_url = ""
        try:
            curr_url = (self.driver.execute_script("return window.location.href;") or "").lower()
        except Exception:
            pass

        # Deteksi kondisi belum login
        is_unauth = False
        if force:
            is_unauth = True
        elif "/about" in curr_url or "accounts.google.com" in curr_url or "flow.google.com/about" in curr_url:
            is_unauth = True
        elif "flow.google.com" in curr_url and not ("/project/" in curr_url):
            try:
                has_signin_or_about = self.driver.execute_script("""
                const text = (document.body ? document.body.innerText : '') || '';
                const hasBtn = !!Array.from(document.querySelectorAll('button, a')).find(el => {
                    const t = (el.textContent || '').trim().toLowerCase();
                    return t.includes('create with google flow') || t.includes('sign in') || t.includes('masuk');
                });
                return hasBtn || text.includes('Create with Google Flow') || text.includes('Unlock your best creative work');
                """)
                if has_signin_or_about:
                    is_unauth = True
            except Exception:
                pass

        if not is_unauth:
            return True

        # Tampilkan panel informasi bantuan autentikasi
        console.print(
            Panel(
                "[bold yellow]Akun Google belum terhubung atau sesi login Google Flow telah berakhir.[/bold yellow]\n\n"
                "Peramban mendeteksi halaman publik ([cyan]flow.google.com/about[/cyan]).\n"
                "Otomasi siap membantu menghubungkan akun Google Anda sekarang secara langsung & otomatis (100% Full CLI).\n"
                "[dim]• Biner peramban otomasi berjalan senyap di latar belakang (tanpa jendela GUI).\n"
                "• Token sesi disimpan aman dan terisolasi di [cyan]browser_profile/cookies.sqlite[/cyan] lokal proyek.[/dim]",
                title="[gold]Bantuan Autentikasi Google Flow[/gold]",
                box=box.ROUNDED,
            )
        )

        email_to_use = email or getattr(self, "email", None) or os.environ.get("GOOGLE_EMAIL")
        pwd_to_use = password or getattr(self, "password", None) or os.environ.get("GOOGLE_PASSWORD")

        if not email_to_use or not pwd_to_use:
            try:
                connect_ask = Prompt.ask(
                    "[cyan]Apakah Anda ingin menghubungkan akun Google Flow sekarang? [Y/n][/cyan]",
                    default="y",
                )
            except (EOFError, KeyboardInterrupt):
                connect_ask = "n"

            if connect_ask.strip().lower() in ("n", "no", "tidak"):
                raise RuntimeError(
                    "Akun Google belum terhubung. Diperlukan autentikasi akun Google Flow aktif "
                    "untuk dapat mengakses kanvas dan menghasilkan gambar."
                )

            console.print("\n[bold cyan]Silakan masukkan kredensial akun Google Anda untuk login otomatis (100% Full CLI):[/bold cyan]")
            if not email_to_use:
                while not email_to_use:
                    try:
                        email_to_use = Prompt.ask("[cyan]• Masukkan Email Google[/cyan]").strip()
                    except (EOFError, KeyboardInterrupt):
                        raise RuntimeError("Proses login dibatalkan oleh pengguna.")
                    if not email_to_use:
                        console.print("[warning]Alamat email tidak boleh kosong. Silakan masukkan email yang valid.[/warning]")

            if not pwd_to_use:
                while not pwd_to_use:
                    try:
                        pwd_to_use = Prompt.ask("[cyan]• Masukkan Kata Sandi Google[/cyan]", password=True).strip()
                    except (EOFError, KeyboardInterrupt):
                        raise RuntimeError("Proses login dibatalkan oleh pengguna.")
                    if not pwd_to_use:
                        console.print("[warning]Kata sandi tidak boleh kosong. Silakan masukkan kata sandi.[/warning]")

            self.email = email_to_use
            self.password = pwd_to_use

        # Temukan berkas login.py dari folder firefox-stealth-automation
        login_script_candidates = [
            self.workspace_dir / "firefox-stealth-automation" / "login.py",
            self.workspace_dir.parent / "firefox-stealth-automation" / "login.py",
            Path(r"D:\New folder\image-generator\firefox-stealth-automation\login.py"),
            Path(r"D:\New folder\firefox-stealth-automation\login.py"),
        ]
        login_script = next((p for p in login_script_candidates if p.exists()), None)

        if not login_script:
            raise RuntimeError(
                "Modul login 'firefox-stealth-automation/login.py' tidak ditemukan. "
                "Silakan pastikan repositori/folder firefox-stealth-automation tersedia di direktori proyek."
            )

        # Tutup Firefox sementara agar cookies.sqlite tidak terkunci oleh proses Gecko
        console.print("[info]ℹ Menyiapkan peramban otomasi untuk autentikasi langsung...[/info]")
        self.close()

        login_dir = login_script.parent
        if str(login_dir) not in sys.path:
            sys.path.insert(0, str(login_dir))

        try:
            from login import automated_google_login
            success = automated_google_login(
                email=email_to_use,
                password=pwd_to_use,
                profile_dir=self.profile_dir,
            )
        except Exception as login_err:
            console.print(f"[error]✗ Terjadi kegagalan pada modul login otomatis:[/error] {login_err}")
            success = False

        if not success:
            raise RuntimeError(
                "Autentikasi akun Google Flow belum berhasil diselesaikan. "
                "Silakan periksa kredensial Anda dan ulangi perintah untuk mencoba kembali."
            )

        # Sinkronkan file cookies ke profil firefox-stealth-automation jika berbeda
        neighbor_profile = login_dir / "browser_profile"
        if neighbor_profile.resolve() != self.profile_dir.resolve() and neighbor_profile.exists():
            try:
                src_db = self.profile_dir / "cookies.sqlite"
                if src_db.exists():
                    shutil.copy2(src_db, neighbor_profile / "cookies.sqlite")
            except Exception:
                pass

        console.print("[success]✓ Autentikasi berhasil! Meluncurkan peramban kembali dan melanjutkan generasi gambar...[/success]")
        time.sleep(1.5)

        # Luncurkan kembali Firefox dengan sesi yang kini sudah aktif
        self.ensure_browser()
        self.connect()
        self.driver.navigate(FLOW_HOME_URL)
        time.sleep(3.5)
        return True

    def detect_browser_active_email(self) -> str | None:
        """Mendeteksi alamat email akun Google yang benar-benar sedang aktif di dalam peramban (murni dari DOM).

        Returns:
            str | None: Alamat email yang aktif di DOM peramban, atau None jika belum login / tidak terdeteksi.
        """
        detect_script = """
        // 1. Cek tombol atau avatar profil akun Google (memuat aria-label: 'Akun Google: Nama (email@gmail.com)')
        const profileElements = Array.from(document.querySelectorAll('button, a, img, div, span'));
        for (const el of profileElements) {
            const aria = (el.getAttribute('aria-label') || el.getAttribute('title') || '').trim();
            if (aria.includes('@')) {
                const match = aria.match(/([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,})/);
                if (match) return match[1];
            }
        }

        // 2. Pemindaian regex fallback pada struktur dokumen
        try {
            const html = document.documentElement ? document.documentElement.innerHTML : '';
            const matches = html.match(/[a-zA-Z0-9._%+-]+@(?:gmail\\.com|[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,})/g);
            if (matches) {
                const filtered = Array.from(new Set(matches)).filter(e => {
                    const low = e.toLowerCase();
                    return !low.includes('google.com') && !low.includes('example.com') &&
                           !low.includes('sentry') && !low.includes('schema.org') &&
                           !low.includes('w3.org') && !low.includes('github.com');
                });
                if (filtered.length > 0) return filtered[0];
            }
        } catch (e) {}

        return null;
        """
        try:
            detected = self.driver.execute_script(detect_script)
            if detected and isinstance(detected, str) and "@" in detected:
                return detected.strip()
        except Exception:
            pass
        return None

    def get_current_user_email(self) -> str | None:
        """Mengembalikan alamat email akun Google yang aktif.

        Mendahulukan deteksi langsung dari DOM peramban untuk mencegah false positive
        dari argumen CLI. Jika DOM tidak dapat dipindai, menggunakan fallback self.email.

        Returns:
            str | None: Alamat email pengguna aktif atau None.
        """
        dom_email = self.detect_browser_active_email()
        if dom_email:
            return dom_email

        return getattr(self, "email", None) or os.environ.get("GOOGLE_EMAIL")

    def _sanitize_email(self, email: str) -> str:
        """Membersihkan format alamat email agar aman digunakan sebagai nama direktori."""
        return re.sub(r"[^\w\-_]", "_", email.strip().lower())

    def save_account_to_vault(self, email: str | None = None) -> bool:
        """Mencadangkan sesi akun (cookies.sqlite) saat ini ke dalam brankas akun lokal (Account Vault).

        Args:
            email (str | None): Alamat email akun. Jika None, akan dideteksi dari kanvas aktif.

        Returns:
            bool: True jika berhasil dicadangkan ke brankas akun lokal.
        """
        target_email = email or self.get_current_user_email()
        if not target_email or "@" not in target_email:
            return False

        src_cookie = self.profile_dir / "cookies.sqlite"
        if not src_cookie.exists():
            return False

        account_dir = self.vault_dir / self._sanitize_email(target_email)
        account_dir.mkdir(parents=True, exist_ok=True)
        dest_cookie = account_dir / "cookies.sqlite"

        try:
            shutil.copy2(src_cookie, dest_cookie)
            meta_file = account_dir / "meta.json"
            meta_data = {
                "email": target_email,
                "saved_at": time.time(),
                "saved_at_human": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            meta_file.write_text(json.dumps(meta_data, indent=2), encoding="utf-8")
            return True
        except Exception:
            return False

    def load_account_from_vault(self, email: str) -> bool:
        """Memuat sesi akun (cookies.sqlite) dari brankas akun lokal ke profil peramban aktif.

        Args:
            email (str): Alamat email akun yang ingin dimuat dari brankas.

        Returns:
            bool: True jika sesi akun berhasil dimuat dari brankas.
        """
        if not email or "@" not in email:
            return False

        account_dir = self.vault_dir / self._sanitize_email(email)
        src_cookie = account_dir / "cookies.sqlite"
        if not src_cookie.exists():
            return False

        dest_cookie = self.profile_dir / "cookies.sqlite"
        try:
            # Tutup peramban sementara agar file cookies.sqlite tidak terkunci oleh proses Gecko
            was_running = self.proc is not None or self.driver.is_port_open(0.2)
            if was_running:
                self.close()

            shutil.copy2(src_cookie, dest_cookie)
            self.email = email
            return True
        except Exception:
            return False

    def list_vault_accounts(self) -> list[dict]:
        """Mendaftar seluruh sesi akun Google yang tersimpan di dalam brankas akun lokal.

        Returns:
            list[dict]: Daftar akun tersimpan beserta metadata waktu penyimpanan.
        """
        accounts = []
        if not self.vault_dir.exists():
            return accounts

        for ad in self.vault_dir.iterdir():
            if ad.is_dir() and (ad / "cookies.sqlite").exists():
                meta_file = ad / "meta.json"
                email_name = ad.name.replace("_", ".")
                saved_time = ""
                if meta_file.exists():
                    try:
                        data = json.loads(meta_file.read_text(encoding="utf-8"))
                        email_name = data.get("email", email_name)
                        saved_time = data.get("saved_at_human", "")
                    except Exception:
                        pass
                accounts.append({
                    "email": email_name,
                    "dir": ad,
                    "saved_at": saved_time,
                })
        return accounts

    def switch_account_if_needed(self, requested_email: str | None = None) -> bool:
        """Memeriksa dan mengeksekusi pergantian akun Google Flow secara cerdas (Account Vault).

        Jika requested_email ditentukan dan berbeda dari akun aktif saat ini:
        1. Mencadangkan sesi aktif saat ini ke brankas akun (~512 KB, zero disk bloat).
        2. Jika requested_email sudah ada di brankas -> hot-swap cookies.sqlite secara instan (0.1s).
        3. Jika requested_email belum ada di brankas -> luncurkan login otomatis dan simpan sesi baru.

        Args:
            requested_email (str | None): Alamat email target (misal dari flag --email).

        Returns:
            bool: True jika akun siap digunakan.
        """
        target = requested_email or getattr(self, "email", None)
        curr_active = (self.detect_browser_active_email() or "").strip().lower()

        # Selalu cadangkan sesi akun aktif saat ini ke brankas jika terdeteksi
        if curr_active:
            self.save_account_to_vault(curr_active)

        if not target or "@" not in str(target):
            return True

        target_clean = str(target).strip().lower()

        # Jika akun yang diminta sama persis dengan akun aktif di peramban, tidak perlu tindakan
        if curr_active and curr_active == target_clean:
            return True

        console.print(
            Panel(
                f"[bold cyan]PERMINTAAN PERGANTIAN AKUN GOOGLE FLOW[/bold cyan]\n\n"
                f"• Akun Aktif di Peramban : [yellow]{curr_active or 'Belum terdeteksi'}[/yellow]\n"
                f"• Akun Target Diminta    : [bold green]{target}[/bold green]",
                box=box.ROUNDED,
                title="[cyan]Account Vault Switcher[/cyan]",
            )
        )

        # 1. Periksa apakah akun target sudah ada di brankas lokal
        if self.load_account_from_vault(target):
            console.print(
                f"[success]✓ Sesi akun [cyan]{target}[/cyan] ditemukan di brankas lokal! Mengaktifkan sesi secara instan...[/success]"
            )
            time.sleep(1.0)
            self.ensure_browser()
            self.connect()
            self.driver.navigate(FLOW_HOME_URL)
            time.sleep(3.5)
            return True

        # 2. Jika belum ada di brankas, jalankan autentikasi otomatis untuk akun target baru
        console.print(
            f"[info]ℹ Akun [cyan]{target}[/cyan] belum ada di brankas. Menyiapkan autentikasi langsung...[/info]"
        )
        self.prompt_and_login_if_needed(
            email=target,
            password=getattr(self, "password", None),
            force=True,
        )
        self.save_account_to_vault(target)
        return True

    def open_or_create_project(self, target_project_name: str = "images generator") -> bool:
        """Mencari proyek dengan nama target di dasbor, atau membuka proyek yang ada / membuat baru.

        Jika kanvas proyek aktif sudah terbuka, metode ini akan langsung menggunakannya.
        Jika di beranda atau halaman 404, peramban akan membuka proyek yang ada di dasbor
        atau membuat proyek baru jika belum ada.

        Args:
            target_project_name (str): Nama proyek yang dicari atau dibuat (default: 'images generator').

        Returns:
            bool: True jika berhasil masuk ke dalam kanvas proyek target.
        """
        # 1. Cek apakah saat ini sudah berada di dalam kanvas proyek yang valid
        check_inside_script = """
        const url = (window.location.href || '').toLowerCase();
        const bodyText = (document.body ? document.body.innerText : '').toLowerCase();
        const is404 = url.includes('/404') || url.includes('reason=project') || bodyText.includes('project tidak ditemukan') || bodyText.includes('halaman tidak ditemukan');
        const hasEditor = !!document.querySelector('.ProseMirror[contenteditable="true"]');
        const hasPromptBox = !!document.querySelector('flow-prompt-box');
        const isCanvasReady = url.includes('/project/') && !is404 && (hasEditor || hasPromptBox);
        return {
            inside: isCanvasReady,
            url: window.location.href
        };
        """
        try:
            curr = self.driver.execute_script(check_inside_script)
            if isinstance(curr, dict) and curr.get("inside"):
                self.current_project_url = curr.get("url")
                return True
        except Exception:
            pass

        # 2. Navigasikan ke beranda Google Flow jika belum di kanvas valid atau sedang di 404
        console.print(f"[info]ℹ[/info] Memeriksa proyek [cyan]{target_project_name}[/cyan] di Google Flow...")
        self.driver.navigate(FLOW_HOME_URL)
        time.sleep(3.5)

        # 3. Tutup dialog modal onboarding jika muncul di beranda
        self.dismiss_onboarding_dialog()

        # 4. Cari proyek di dasbor atau buat proyek baru
        select_project_script = """
        const target = (arguments[0] || '').toLowerCase().replace(/[\\s_-]+/g, ' ');

        // 4a. Cari proyek yang namanya cocok dengan target ('images generator' / 'image generator')
        const links = Array.from(document.querySelectorAll('a[href*="/project/"]')).filter(a => {
            const h = (a.href || '').toLowerCase();
            return !h.includes('/404') && !h.includes('reason=project');
        });
        if (target) {
            const matchedLink = links.find(a => {
                const txt = (a.textContent || '').toLowerCase().replace(/[\\s_-]+/g, ' ');
                const aria = (a.getAttribute('aria-label') || '').toLowerCase();
                return txt.includes(target) || aria.includes(target) || txt.includes('image generator') || aria.includes('image generator');
            });
            if (matchedLink) {
                matchedLink.click();
                return { action: 'opened_named', href: matchedLink.href };
            }
        }

        // 4b. Jika ada proyek yang sudah ada di dasbor pengguna, buka proyek pertama/terbaru
        if (links.length > 0) {
            links[0].click();
            return { action: 'opened_existing', href: links[0].href };
        }

        // 4c. Jika belum ada proyek sama sekali, klik tombol 'Project baru'
        const newProjBtn = document.querySelector('button.new-project-button') ||
                           Array.from(document.querySelectorAll('button, a')).find(el => {
                               const t = (el.textContent || '').trim().toLowerCase();
                               const aria = (el.getAttribute('aria-label') || '').toLowerCase();
                               return t.includes('project baru') || t.includes('new project') || aria.includes('project baru') || aria.includes('new project');
                           });
        if (newProjBtn) {
            newProjBtn.click();
            return { action: 'created_new' };
        }

        return { action: 'none' };
        """

        opened = False
        for _ in range(15):
            try:
                res = self.driver.execute_script(select_project_script, [target_project_name])
                if isinstance(res, dict) and res.get("action") in ("opened_named", "opened_existing", "created_new"):
                    opened = True
                    break
            except Exception:
                pass
            time.sleep(1.0)

        # 5. Tunggu kanvas proyek termuat penuh dengan editor ProseMirror aktif
        wait_canvas_script = """
        const url = (window.location.href || '').toLowerCase();
        const bodyText = (document.body ? document.body.innerText : '').toLowerCase();
        const is404 = url.includes('/404') || url.includes('reason=project') || bodyText.includes('project tidak ditemukan') || bodyText.includes('halaman tidak ditemukan');
        const hasEditor = !!document.querySelector('.ProseMirror[contenteditable="true"]');
        const hasPromptBox = !!document.querySelector('flow-prompt-box');
        return url.includes('/project/') && !is404 && (hasEditor || hasPromptBox);
        """
        for _ in range(30):
            try:
                ready = self.driver.execute_script(wait_canvas_script)
                if ready:
                    time.sleep(1.5)
                    try:
                        self.current_project_url = self.driver.execute_script("return window.location.href;")
                    except Exception:
                        pass
                    return True
            except Exception:
                pass
            time.sleep(1.0)

        return False

    def dismiss_onboarding_dialog(self) -> bool:
        """Menutup dialog modal onboarding atau persetujuan kebijakan privasi Google Flow secara mandiri.

        Mendeteksi modal 'Gunakan dan kembangkan alat AI untuk kreativitas' atau 'Tinjau kebijakan privasi kami',
        menggulirkan konten ke paling dasar, mencentang checkbox jika ada, dan mengeklik tombol aksi
        seperti 'Berikutnya', 'Lanjutkan', 'Saya setuju', 'Mulai', atau 'Selesai' hingga modal tertutup.

        Returns:
            bool: True jika ada dialog yang berhasil ditutup atau jika tidak ada dialog yang menghalangi.
        """
        dismiss_script = """
        const dialog = document.querySelector('mat-dialog-container, [role="dialog"], flow-onboarding, div[class*="dialog"]');
        if (!dialog) return { hasDialog: false };

        // Scroll semua elemen konten di dalam dialog agar tombol enabled
        const scrollables = dialog.querySelectorAll('mat-dialog-content, div');
        for (const s of scrollables) {
            if (s.scrollHeight > s.clientHeight) {
                s.scrollTop = s.scrollHeight;
                s.dispatchEvent(new Event('scroll', { bubbles: true }));
            }
        }

        // Cek checkbox jika ada yang belum tercentang
        const checkboxes = Array.from(dialog.querySelectorAll('input[type="checkbox"], mat-checkbox'));
        for (const cb of checkboxes) {
            if (!cb.checked && !cb.classList.contains('mat-mdc-checkbox-checked')) {
                cb.click();
            }
        }

        // Cari tombol aksi utama di dalam dialog (abaikan Logout atau Batal)
        const btns = Array.from(dialog.querySelectorAll('button'));
        const primaryBtn = btns.find(b => {
            const t = (b.textContent || '').trim().toLowerCase();
            const aria = (b.getAttribute('aria-label') || '').toLowerCase();
            const isDismissAction = t === 'berikutnya' || t === 'next' || t === 'lanjutkan' ||
                                    t === 'continue' || t === 'saya setuju' || t === 'setuju' ||
                                    t === 'mulai' || t === 'selesai' || t === 'i agree' ||
                                    t.includes('berikutnya') || t.includes('lanjutkan') || t.includes('setuju');
            const isNegative = t === 'logout' || t === 'batal' || t === 'cancel' || t === 'sebelumnya';
            return isDismissAction && !isNegative && !b.disabled && b.getAttribute('aria-disabled') !== 'true';
        });

        if (primaryBtn) {
            const btnText = primaryBtn.textContent.trim();
            primaryBtn.click();
            return { hasDialog: true, action: 'clicked', button: btnText };
        }

        return { hasDialog: true, action: 'waiting_scroll_or_enabled' };
        """

        closed_any = False
        for cycle in range(1, 6):
            try:
                res = self.driver.execute_script(dismiss_script)
                if isinstance(res, dict):
                    if not res.get("hasDialog"):
                        break
                    closed_any = True
                    btn_clicked = res.get("button", "Aksi")
                    console.print(f"[info]ℹ[/info] Menutup modal onboarding Google Flow (Tahap {cycle}: mengeklik '{btn_clicked}')...")
                    self.capture_debug_screenshot(f"dismiss_onboarding_step_{cycle}", f"Dismiss onboarding dialog tahap {cycle}")
                    time.sleep(2.0)
            except Exception:
                pass
            time.sleep(0.5)

        return closed_any

    def close_agent_panel_if_open(self) -> bool:
        """Menutup sidebar panel 'Sesi' agen di sebelah kanan jika sedang terbuka.

        Saat panel sesi agen terbuka, kanvas tengah tidak menampilkan kotak prompt utama.
        Mengeklik tombol tutup ('Tutup' / icon close) akan memunculkan flow-prompt-box
        di bagian tengah bawah kanvas utama.

        Returns:
            bool: True jika panel berhasil ditutup atau sudah dalam kondisi tertutup.
        """
        close_script = """
        const closeBtn = document.querySelector('button[aria-label="Tutup"], button[aria-label*="Tutup sesi"], .page-layout header button.mdc-icon-button:last-child');
        if (closeBtn && closeBtn.offsetParent !== null) {
            closeBtn.click();
            return { closed: true };
        }
        return { closed: false };
        """
        try:
            res = self.driver.execute_script(close_script)
            if isinstance(res, dict) and res.get("closed"):
                console.print("[info]ℹ[/info] Panel sesi samping ditutup (beralih ke kanvas utama).")
                time.sleep(1.5)
                return True
        except Exception:
            pass
        return False

    def disable_agent_mode(self) -> bool:
        """Menonaktifkan Mode Agen pada kotak prompt Google Flow jika sedang aktif.

        Memeriksa atribut `aria-pressed` atau styling tombol chip 'Agen' (class `agent-mode-chip-checked`).
        Jika aktif, tombol tersebut diklik untuk beralih kembali ke mode pembuatan gambar standar.

        Returns:
            bool: True jika mode agen non-aktif atau berhasil dimatikan.
        """
        toggle_script = """
        const agentBtn = document.querySelector('button.agent-mode-chip, .agent-mode-chip') ||
                         Array.from(document.querySelectorAll('button')).find(el => (el.textContent || '').trim() === 'Agen');
        if (!agentBtn) return { status: 'not_found' };

        const isPressed = agentBtn.getAttribute('aria-pressed') === 'true' ||
                          agentBtn.classList.contains('agent-mode-chip-checked') ||
                          agentBtn.classList.contains('active') ||
                          agentBtn.classList.contains('mat-mdc-button-checked');

        if (isPressed) {
            agentBtn.click();
            return { status: 'deactivated' };
        }
        return { status: 'already_off' };
        """
        try:
            res = self.driver.execute_script(toggle_script)
            if isinstance(res, dict) and res.get("status") == "deactivated":
                console.print("[info]ℹ[/info] Mode Agen dinonaktifkan (beralih ke mode gambar standar).")
                time.sleep(1.0)
                return True
        except Exception:
            pass
        return True

    def configure_generation_settings(
        self,
        model_name: str | None = None,
        aspect_ratio: str | None = None,
        count_str: str | None = None,
    ) -> bool:
        """Mengonfigurasi setelan model AI, aspek rasio, dan jumlah variasi di kanvas Google Flow.

        Navigasi dilakukan secara senyap melalui Angular Material toggle dan overlay menu:
        1. Memeriksa apakah chip ringkasan setelan di luar sudah sesuai dengan target.
        2. Jika belum, membuka panel setelan prompt box (`flow-prompt-box-settings`).
        3. Memastikan tab mode 'Gambar' aktif.
        4. Memilih tombol aspek rasio target ('16:9', '4:3', '1:1', '3:4', '9:16').
        5. Memilih tombol kuantitas variasi target ('x1', 'x2', 'x3', 'x4').
        6. Jika model target berbeda, membuka dropdown model dan memilih model yang diminta.
        7. Menutup panel setelan dan mencetak status ringkasan akhir.

        Args:
            model_name (str | None): Nama model AI yang dipilih (default: self.model).
            aspect_ratio (str | None): Nilai aspek rasio kanvas (default: self.aspect_ratio).
            count_str (str | None): Kuantitas variasi gambar per generasi (default: self.count_str).

        Returns:
            bool: True jika setelan berhasil diterapkan atau sudah sesuai.
        """
        target_model = normalize_model(model_name or self.model)
        target_ratio = normalize_aspect_ratio(aspect_ratio or self.aspect_ratio)
        target_count = normalize_count(count_str or self.count_str)
        target_icon = RATIO_ICON_MAP.get(target_ratio, "crop_16_9")

        # Sinkronkan kembali nilai atribut instance
        self.model = target_model
        self.aspect_ratio = target_ratio
        self.count_str = target_count

        open_panel_script = """
        const targetModel = arguments[0];
        const targetRatio = arguments[1];
        const targetIcon = arguments[2];
        const targetCount = arguments[3];

        // 1. Cek apakah ringkasan chip setelan sudah sesuai persis
        const summaryEl = document.querySelector('button.settings-trigger-button .settings-summary') ||
                          document.querySelector('button.settings-trigger-button');
        const summaryText = summaryEl ? (summaryEl.textContent || '') : '';

        const hasModel = summaryText.includes(targetModel);
        const hasCount = summaryText.includes(targetCount);
        const hasRatio = summaryText.includes(targetIcon) || summaryText.includes(targetRatio);

        if (hasModel && hasCount && hasRatio) {
            return { status: 'already_configured', summary: summaryText.trim() };
        }

        // 2. Buka panel setelan jika belum terbuka
        let settingsPanel = document.querySelector('flow-prompt-box-settings');
        if (!settingsPanel) {
            const settingsBtn = document.querySelector('button.settings-trigger-button') ||
                                document.querySelector('button[aria-label="Pemicu setelan"]');
            if (settingsBtn) {
                settingsBtn.click();
            }
        }

        return { status: 'opened' };
        """

        # Tahap A: Periksa dan ubah model jika berbeda
        check_model_script = """
        const targetModel = arguments[0];
        const panel = document.querySelector('flow-prompt-box-settings');
        if (!panel) return { error: 'Panel tidak ditemukan' };

        const modelBtn = panel.querySelector('button[aria-label="Pilih rangkaian model"]') ||
                         Array.from(panel.querySelectorAll('button')).find(b => (b.textContent || '').includes('Banana'));
        if (modelBtn && !(modelBtn.textContent || '').includes(targetModel)) {
            modelBtn.click();
            return { needChange: true };
        }
        return { needChange: false };
        """

        select_model_script = """
        const targetModel = arguments[0];
        const items = Array.from(document.querySelectorAll('.cdk-overlay-container [role="menuitem"], .mat-mdc-menu-item'));
        const targetItem = items.find(it => (it.textContent || '').includes(targetModel));
        if (targetItem) {
            targetItem.click();
            return { clicked: true, itemText: targetItem.textContent.trim() };
        }
        return { clicked: false };
        """

        # Tahap B: Atur tab Gambar, Aspek Rasio, dan Kuantitas
        apply_toggles_script = """
        const targetRatio = arguments[0];
        const targetCount = arguments[1];

        const panel = document.querySelector('flow-prompt-box-settings');
        if (!panel) return { error: 'Panel tidak ditemukan' };

        function clickToggle(toggle) {
            if (!toggle) return false;
            const target = toggle.querySelector('.toggle-label') ||
                           toggle.querySelector('.mat-button-toggle-label-content') ||
                           toggle;
            target.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true }));
            target.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true }));
            target.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
            return toggle.classList.contains('mat-button-toggle-checked');
        }

        const toggles = Array.from(panel.querySelectorAll('mat-button-toggle'));

        // 1. Pastikan tab "Gambar" aktif
        const imgToggle = toggles.find(t => (t.textContent || '').includes('Gambar'));
        if (imgToggle && !imgToggle.classList.contains('mat-button-toggle-checked')) {
            clickToggle(imgToggle);
        }

        // 2. Atur Aspek Rasio (16:9, 4:3, 1:1, 3:4, 9:16)
        const ratioToggle = toggles.find(t => (t.textContent || '').includes(targetRatio));
        if (ratioToggle && !ratioToggle.classList.contains('mat-button-toggle-checked')) {
            clickToggle(ratioToggle);
        }

        // 3. Atur Kuantitas Gambar (x1, x2, x3, x4)
        const countToggle = toggles.find(t => (t.textContent || '').trim() === targetCount);
        if (countToggle && !countToggle.classList.contains('mat-button-toggle-checked')) {
            clickToggle(countToggle);
        }

        return {
            imgChecked: imgToggle ? imgToggle.classList.contains('mat-button-toggle-checked') : false,
            ratioChecked: ratioToggle ? ratioToggle.classList.contains('mat-button-toggle-checked') : false,
            countChecked: countToggle ? countToggle.classList.contains('mat-button-toggle-checked') : false
        };
        """

        close_panel_script = """
        const panel = document.querySelector('flow-prompt-box-settings');
        if (panel) {
            const trigger = document.querySelector('button.settings-trigger-button');
            if (trigger) trigger.click();
            else document.body.click();
        }
        const summary = (document.querySelector('button.settings-trigger-button') || {}).textContent || '';
        return { summary: summary.trim() };
        """

        try:
            # 1. Tunggu hingga tombol trigger setelan tersedia di DOM
            for _ in range(16):
                has_trigger = self.driver.execute_script(
                    "return !!(document.querySelector('button.settings-trigger-button') || "
                    "document.querySelector('button[aria-label=\"Pemicu setelan\"]'));"
                )
                if has_trigger:
                    break
                time.sleep(0.4)

            res_open = self.driver.execute_script(
                open_panel_script,
                [target_model, target_ratio, target_icon, target_count],
            )
            if isinstance(res_open, dict) and res_open.get("status") == "already_configured":
                console.print(
                    f"[success]✓ Setelan aktif:[/success] [cyan]{target_model}[/cyan] | "
                    f"Rasio: [cyan]{target_ratio}[/cyan] | Kuantitas: [cyan]{target_count}[/cyan]"
                )
                return True

            # 2. Tunggu hingga panel flow-prompt-box-settings benar-benar terbuka
            for _ in range(10):
                has_panel = self.driver.execute_script("return !!document.querySelector('flow-prompt-box-settings');")
                if has_panel:
                    break
                self.driver.execute_script(
                    "const b = document.querySelector('button.settings-trigger-button') || "
                    "document.querySelector('button[aria-label=\"Pemicu setelan\"]'); if (b) b.click();"
                )
                time.sleep(0.4)

            # Langkah 1: Ubah model terlebih dahulu jika diperlukan
            res_m = self.driver.execute_script(check_model_script, [target_model])
            if isinstance(res_m, dict) and res_m.get("needChange"):
                time.sleep(0.5)
                self.driver.execute_script(select_model_script, [target_model])
                time.sleep(0.6)

            # Langkah 2: Terapkan toggle tab gambar, aspek rasio, dan jumlah variasi
            self.driver.execute_script(apply_toggles_script, [target_ratio, target_count])
            time.sleep(0.4)

            # Langkah 3: Tutup panel setelan
            final_res = self.driver.execute_script(close_panel_script)
            final_summary = final_res.get("summary") if isinstance(final_res, dict) else ""
            console.print(
                f"[success]✓ Setelan dikonfigurasi:[/success] [cyan]{target_model}[/cyan] | "
                f"Rasio: [cyan]{target_ratio}[/cyan] | Kuantitas: [cyan]{target_count}[/cyan] "
                f"[dim]({final_summary})[/dim]"
            )
            return True
        except Exception as e:
            console.print(f"[warning]⚠ Gagal mengonfigurasi setelan: {e}[/warning]")
            return False

    def find_flow_tab(self) -> str:
        """Mencari dan beralih ke tab Google Flow aktif, atau menginisialisasi lingkungan proyek.

        Alur:
        1. Memindai seluruh tab peramban untuk menemukan tab Google Flow aktif.
        2. Jika belum ada tab Google Flow:
           - Membersihkan semua tab ekstra sehingga peramban bersih.
           - Mengarahkan tab ke beranda Google Flow (https://flow.google.com/).
        3. Menangani alur login otomatis jika akun belum terhubung.
        4. Masuk ke proyek 'images generator' (atau membuat baru jika belum ada).
        5. Menonaktifkan Mode Agen pada prompt box.
        6. Mengonfigurasi setelan model AI, aspek rasio, dan jumlah variasi.
        7. Membersihkan seluruh tile lama di kanvas sehingga kanvas kosong sempurna.

        Returns:
            str: Identifier handle tab Google Flow yang siap digunakan.
        """
        handles = self.driver.get_window_handles()
        if not handles:
            raise RuntimeError("Tidak ada tab peramban yang terbuka.")

        detection_script = """
        return {
            url: window.location.href,
            title: document.title,
            hasFlow: !!document.querySelector('aisandbox-root, flow-project-shell, flow-prompt-box, flow-rich-text-editor'),
            isHome: window.location.href.includes('flow.google.com') && !window.location.href.includes('/project/')
        };
        """

        flow_handle = None
        for handle in handles:
            try:
                self.driver.switch_to_window(handle)
                info = self.driver.execute_script(detection_script)
                if isinstance(info, dict):
                    url = (info.get("url") or "").lower()
                    if info.get("hasFlow") or "flow.google.com" in url:
                        flow_handle = handle
                        break
            except Exception:
                continue

        if not flow_handle:
            console.print("[info]ℹ[/info] Tab Google Flow belum ada. Membersihkan tab ekstra dan membuka Google Flow...")
            active_handle = self.cleanup_extra_tabs()
            self.driver.switch_to_window(active_handle)
            self.driver.navigate(FLOW_HOME_URL)
            time.sleep(3.5)
            flow_handle = active_handle
        else:
            self.driver.switch_to_window(flow_handle)

        # 1. Periksa apakah pengguna meminta pergantian akun (Account Vault Switcher)
        self.switch_account_if_needed(self.email)

        # 2. Periksa apakah sesi akun Google belum terhubung dan bantu login secara langsung & otomatis jika diperlukan
        self.prompt_and_login_if_needed(self.email, self.password)

        # 2. Tutup dialog modal onboarding jika muncul di beranda
        self.dismiss_onboarding_dialog()

        # 3. Masuk ke proyek 'images generator' atau buka kanvas proyek
        if not self.open_or_create_project(target_project_name="images generator"):
            console.print("[warning]⚠ Mencoba ulang membuka kanvas proyek Google Flow...[/warning]")
            if not self.open_or_create_project(target_project_name=""):
                # Cek kembali apakah setelah dicoba ulang ternyata dialihkan ke /about
                retry_url = ""
                try:
                    retry_url = (self.driver.execute_script("return window.location.href;") or "").lower()
                except Exception:
                    pass
                if "/about" in retry_url or "accounts.google.com" in retry_url:
                    self.prompt_and_login_if_needed()
                    if not self.open_or_create_project(target_project_name="images generator"):
                        if not self.open_or_create_project(target_project_name=""):
                            raise RuntimeError("Gagal membuka atau membuat kanvas proyek Google Flow setelah login.")
                else:
                    raise RuntimeError("Gagal membuka atau membuat kanvas proyek Google Flow. Pastikan jaringan internet aktif.")

        # 4. Tutup dialog modal onboarding jika muncul di kanvas proyek
        self.dismiss_onboarding_dialog()

        # 5. Tutup sidebar panel sesi agen jika terbuka agar prompt box kanvas aktif
        self.close_agent_panel_if_open()

        # 6. Nonaktifkan mode agen jika sedang aktif pada prompt box kanvas
        self.disable_agent_mode()

        # 7. Konfigurasi setelan model, aspek rasio, dan kuantitas variasi
        self.configure_generation_settings(
            model_name=self.model,
            aspect_ratio=self.aspect_ratio,
            count_str=self.count_str,
        )

        # 8. Bersihkan seluruh tile lama dari kanvas agar kanvas selalu kosong sebelum memulai
        self.delete_all_canvas_tiles()

        return flow_handle

    def clean_failed_tiles(self) -> int:
        """Mendeteksi dan menghapus tile error/gagal yang masih ada pada kanvas Google Flow.

        Memindai seluruh elemen tile pada kanvas untuk menemukan pesan galat seperti
        'Gagal', 'Failed', 'batas penggunaan', 'coba lagi', atau 'error', lalu mengeklik
        tombol hapus ('delete_forever' / 'delete' / 'hapus') pada tile tersebut secara senyap.

        Returns:
            int: Jumlah tile gagal yang berhasil dibersihkan dari kanvas.
        """
        clean_script = """
        const tiles = Array.from(document.querySelectorAll('flow-image-tile'));
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

    def delete_all_canvas_tiles(self, max_tiles: int = 100) -> int:
        """Menghapus SEMUA tile gambar (berhasil maupun gagal) secara massal & total dari kanvas Google Flow.

        Operasi pembersihan ini independen dari kuantitas gambar (-c). Sistem memindai
        seluruh tile yang ada di kanvas proyek dan menghapusnya secara menyeluruh hingga
        kanvas 100% kosong (zero remaining tiles).

        Tahapan:
        1. Menutup backdrop/overlay popup liar jika ada di layar kanvas.
        2. Menghapus seluruh tile gagal/error secara instan melalui tombol hapus cepat.
        3. Menghapus setiap tile yang tersisa satu per satu via hotbar menu 'Pindahkan ke sampah'.
        4. Menggunakan polling interaksi responsif (0.15s) agar proses penghapusan berjalan kilat.
        5. Melakukan verifikasi akhir untuk memastikan kanvas benar-benar bersih total.

        Args:
            max_tiles (int): Batas maksimal pembersihan pengaman per siklus (default: 100).

        Returns:
            int: Jumlah total tile yang berhasil dibersihkan dari kanvas.
        """
        deleted_count = 0

        # Tutup backdrop/overlay popup liar di awal
        try:
            self.driver.execute_script("document.querySelectorAll('.cdk-overlay-backdrop').forEach(el => el.click());")
        except Exception:
            pass

        # 1. Bersihkan semua tile gagal terlebih dahulu secara massal
        failed_cleaned = self.clean_failed_tiles()
        deleted_count += failed_cleaned

        # 2. Hapus tile yang ada secara berulang sampai kanvas benar-benar kosong
        delete_step_script = """
        // Tutup overlay sebelumnya jika ada
        const backdrops = document.querySelectorAll('.cdk-overlay-backdrop');
        if (backdrops.length > 0) {
            backdrops.forEach(el => el.click());
        }

        const tile = document.querySelector('flow-image-tile');
        if (!tile) return { status: 'empty' };

        // Pindahkan kursor virtual ke tile
        tile.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true, cancelable: true }));
        tile.dispatchEvent(new MouseEvent('mouseover', { bubbles: true, cancelable: true }));

        const btn = tile.querySelector('button[aria-label="Opsi lainnya"], flow-image-hotbar button:nth-child(3), flow-image-hotbar button:last-child');
        if (!btn) return { status: 'no_hotbar' };

        btn.click();
        return { status: 'opened' };
        """

        click_trash_script = """
        const items = Array.from(document.querySelectorAll('.cdk-overlay-container button.mat-mdc-menu-item, button.mat-mdc-menu-item'));
        const trash = items.find(b => {
            const txt = (b.textContent || '').toLowerCase();
            return txt.includes('sampah') || txt.includes('delete') || txt.includes('hapus') || txt.includes('trash');
        });
        if (trash) {
            trash.click();
            return { success: true };
        }
        return { success: false };
        """

        consecutive_empty = 0
        for _ in range(max_tiles):
            # Cek jumlah tile tersisa di kanvas
            try:
                remaining_tiles = self.driver.execute_script("return document.querySelectorAll('flow-image-tile').length;")
            except Exception:
                remaining_tiles = 0

            if not remaining_tiles or remaining_tiles == 0:
                consecutive_empty += 1
                if consecutive_empty >= 2:
                    break
                time.sleep(0.2)
                continue

            consecutive_empty = 0

            # Buka hotbar menu tile
            res_open = None
            try:
                res_open = self.driver.execute_script(delete_step_script)
            except Exception:
                pass

            if not isinstance(res_open, dict) or res_open.get("status") != "opened":
                time.sleep(0.25)
                continue

            # Tunggu overlay menu muncul dan klik opsi 'Pindahkan ke sampah'
            trash_clicked = False
            for _ in range(10):
                time.sleep(0.15)
                try:
                    res_trash = self.driver.execute_script(click_trash_script)
                    if isinstance(res_trash, dict) and res_trash.get("success"):
                        trash_clicked = True
                        deleted_count += 1
                        break
                except Exception:
                    pass

            if not trash_clicked:
                try:
                    self.driver.execute_script("document.querySelectorAll('.cdk-overlay-backdrop').forEach(el => el.click());")
                except Exception:
                    pass
                time.sleep(0.25)
            else:
                time.sleep(0.2)

        # 3. Verifikasi akhir: pastikan kanvas benar-benar kosong total
        try:
            final_count = self.driver.execute_script("return document.querySelectorAll('flow-image-tile').length;")
        except Exception:
            final_count = 0

        if final_count > 0:
            console.print(f"[warning]⚠ Perhatian: Masih tersisa {final_count} tile di kanvas. Membersihkan sisa...[/warning]")
            self.clean_failed_tiles()

        if deleted_count > 0:
            console.print(f"[dim info]ℹ Pembersihan kanvas total: {deleted_count} tile gambar dipindahkan ke sampah (kanvas 100% bersih).[/dim info]")

        return deleted_count

    def submit_prompt(self, prompt_text: str) -> dict:
        """Memasukkan teks prompt ke editor ProseMirror via native keystrokes dan memicu pembuatan gambar.

        Alur:
        1. Menutup overlay popup menu liar jika ada yang aktif.
        2. Menghapus SEMUA tile lama dari kanvas agar bersih total sebelum render baru.
        3. Mencatat snapshot awal kondisi kanvas (jumlah gambar & URL gambar teratas).
        4. Mengosongkan teks lama di editor ProseMirror.
        5. Mengirimkan pengetikan teks asli via Gecko C++ 'ElementSendKeys' sehingga Angular
           seketika mendeteksi teks dan mengaktifkan tombol submit ('disabled: false').
        6. Mengeklik tombol 'Mulai pembuatan' via Gecko C++ native click ('ElementClick').

        Args:
            prompt_text (str): Teks deskripsi gambar yang akan digenerate.

        Returns:
            dict: Snapshot awal kanvas berisi `imgCount` (int) dan `firstImgSrc` (str | None).

        Raises:
            RuntimeError: Jika elemen editor prompt atau tombol submit tidak ditemukan.
        """
        # Tutup menu overlay liar jika ada
        try:
            self.driver.execute_script("document.querySelectorAll('.cdk-overlay-backdrop').forEach(el => el.click());")
        except Exception:
            pass

        # Wajib bersihkan seluruh tile dari kanvas sebelum membuat gambar baru
        self.delete_all_canvas_tiles()

        # Catat snapshot kondisi kanvas sebelum generasi baru dimulai
        snapshot_script = """
        const firstImg = document.querySelector('flow-image-tile img');
        return {
            imgCount: document.querySelectorAll('flow-image-tile img').length,
            firstImgSrc: firstImg ? firstImg.src : null
        };
        """
        initial_state = self.driver.execute_script(snapshot_script) or {"imgCount": 0, "firstImgSrc": None}

        # 1. Bersihkan editor ProseMirror
        clear_script = """
        const editor = document.querySelector('.ProseMirror[contenteditable="true"]') ||
                       document.querySelector('flow-rich-text-editor div[contenteditable="true"]');
        if (!editor) return false;
        editor.focus();
        document.execCommand('selectAll', false, null);
        document.execCommand('delete', false, null);
        return true;
        """
        cleared = False
        for _ in range(12):
            try:
                cleared = self.driver.execute_script(clear_script)
                if cleared:
                    break
            except Exception:
                pass
            time.sleep(0.5)

        if not cleared:
            # Fallback pemulihan otomatis: coba buka kembali proyek yang valid
            console.print("[warning]⚠ Editor ProseMirror belum aktif pada kanvas. Melakukan pemulihan proyek kanvas...[/warning]")
            if self.open_or_create_project():
                time.sleep(1.5)
                for _ in range(15):
                    try:
                        cleared = self.driver.execute_script(clear_script)
                        if cleared:
                            break
                    except Exception:
                        pass
                    time.sleep(0.5)

        if not cleared:
            raise RuntimeError("Elemen editor ProseMirror tidak ditemukan pada kanvas.")

        time.sleep(0.3)

        # 2. Temukan element ID editor dan ketikkan prompt via native ElementSendKeys
        editor_id = self.driver.find_element("css selector", ".ProseMirror[contenteditable='true']")
        self.driver.click_element(editor_id)
        time.sleep(0.2)

        console.print(f"[info]ℹ[/info] Mengirim prompt: [cyan]{prompt_text}[/cyan]")
        self.driver.send_keys(editor_id, prompt_text)
        time.sleep(0.8)

        # 3. Klik tombol submit (yang kini diaktifkan disabled: false oleh Angular)
        btn_id = None
        for sel in (
            "flow-prompt-box button.generate-icon-button",
            "button[aria-label='Mulai pembuatan']",
            "flow-prompt-box button[type='submit']",
        ):
            try:
                btn_id = self.driver.find_element("css selector", sel)
                if btn_id:
                    break
            except Exception:
                pass

        if btn_id:
            try:
                self.driver.click_element(btn_id)
            except Exception:
                self.driver.execute_script("const b = document.querySelector('button[aria-label=\"Mulai pembuatan\"], button.generate-icon-button'); if (b) b.click();")
        else:
            # Fallback DOM click
            self.driver.execute_script("const b = document.querySelector('button[aria-label=\"Mulai pembuatan\"], button.generate-icon-button'); if (b) b.click();")

        return initial_state

    def hover_and_wait_tile(
        self,
        initial_state: dict | None = None,
        timeout: int = 180,
        progress_callback: any = None,
    ) -> bool:
        """Memantau progres generasi gambar (0% -> 100%) dan menunggu render tile baru selesai.

        Mendukung pemantauan pembuatan satu atau banyak gambar (x1 s/d x4).
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

        expected_count = 1
        try:
            expected_count = int(str(self.count_str).replace("x", "").strip())
        except Exception:
            expected_count = 1

        check_script = """
        const expectedCount = arguments[0];
        const tiles = Array.from(document.querySelectorAll('flow-image-tile, flow-grid-tile-container'));
        const imageTiles = Array.from(document.querySelectorAll('flow-image-tile'));
        const firstTile = document.querySelector('flow-image-tile') || tiles[0];
        const tileText = firstTile ? firstTile.innerText : '';
        const progressMatch = tileText.match(/(\\d+)%/);
        const allImgs = Array.from(document.querySelectorAll('flow-image-tile img'));
        const firstImg = firstTile ? firstTile.querySelector('img') : null;
        const btn = document.querySelector('flow-generate-icon-button button');
        const isImgLoaded = firstImg ? (firstImg.complete && firstImg.naturalWidth > 0) : false;
        const allLoaded = allImgs.length >= expectedCount && allImgs.every(img => img.complete && img.naturalWidth > 0);
        const hasProgress = tiles.some(t => /\\d+%/.test(t.innerText || ''));

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
            const hbBtn = firstTile.querySelector('button[aria-label="Opsi lainnya"], flow-image-hotbar button:nth-child(3), flow-image-hotbar button:last-child');
            hotbarReady = !!hbBtn;
        }

        return {
            imgCount: allImgs.length,
            firstImgSrc: firstImg ? firstImg.src : null,
            isImgLoaded: isImgLoaded,
            allLoaded: allLoaded,
            hasProgress: hasProgress,
            progress: progressMatch ? progressMatch[1] : null,
            btnDisabled: btn ? btn.disabled : false,
            hotbarReady: hotbarReady,
            failedMsg: failedMsg
        };
        """

        seen_progress = False
        last_progress = None

        while time.time() - start_time < timeout:
            st = self.driver.execute_script(check_script, [expected_count])
            if isinstance(st, dict):
                # Deteksi kegagalan render secara instan tanpa menunggu timeout
                failed_msg = st.get("failedMsg")
                if failed_msg:
                    self.capture_debug_screenshot("tile_render_failed", f"Tile gagal terdeteksi: {failed_msg}")
                    time.sleep(1.0)
                    failed_lower = failed_msg.lower()
                    if any(k in failed_lower for k in ["batas penggunaan", "quota", "rate limit", "coba lagi nanti", "usage limit"]):
                        raise QuotaExceededError(failed_msg)
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
                has_progress = st.get("hasProgress")
                all_loaded = st.get("allLoaded")

                is_new_image = (img_count > init_count) or (first_src and first_src != init_src)

                # 1. Seluruh gambar target terdeteksi dan sudah selesai dimuat tanpa progress bar aktif
                if is_new_image and all_loaded and not has_progress:
                    time.sleep(1.0)
                    return True

                # 2. Progres pernah berjalan dan sekarang sudah 100% (progress == None)
                if seen_progress and not current_prog and not has_progress and is_new_image:
                    time.sleep(1.0)
                    return True

                # 3. Hotbar opsi siap diakses setelah beberapa detik
                if is_new_image and not current_prog and not has_progress and st.get("hotbarReady") and (time.time() - start_time > 8):
                    time.sleep(1.0)
                    return True

                # 4. Gambar selesai dibuat (persentase hilang, tile baru ada, dan bukan tile galat)
                if is_new_image and not current_prog and not has_progress and (time.time() - start_time > 6):
                    time.sleep(1.0)
                    return True

            time.sleep(1.5)

        raise TimeoutError(f"Waktu tunggu generasi gambar habis ({timeout} detik). Gambar belum selesai dirender.")

    def click_hotbar_and_download(self, tile_index: int = 0, timeout: int = 20) -> bool:
        """Membuka menu opsi hotbar (tombol 3), mengeklik 'Download', dan memilih resolusi '1K (Ukuran asli)'.

        Navigasi dilakukan secara senyap melalui Angular CDK overlay event tanpa memerlukan kursor mouse fisik:
        1. Mengirimkan event hover (`mouseenter`/`mouseover`) ke tile dengan index yang ditentukan dan mengeklik tombol hotbar 3.
        2. Mengeklik item menu 'Download' pada popup menu overlay.
        3. Mengeklik submenu resolusi '1K (Ukuran asli)' untuk memulai pengunduhan berkas ke disk.

        Args:
            tile_index (int): Indeks tile yang akan diunduh (default: 0 untuk tile pertama).
            timeout (int): Batas waktu maksimal interaksi menu dalam detik (default: 20).

        Returns:
            bool: True jika opsi unduhan resolusi 1K berhasil diklik.

        Raises:
            RuntimeError: Jika elemen hotbar, menu Download, atau opsi 1K tidak ditemukan.
        """
        # 1. Buka menu hotbar button 3 secara senyap pada tile index tertentu
        open_hotbar_script = """
        const tileIndex = arguments[0];
        const tiles = Array.from(document.querySelectorAll('flow-image-tile'));
        const tile = tiles[tileIndex] || tiles[0];
        if (!tile) return { success: false, error: 'Tile gambar tidak ditemukan.' };

        tile.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true, cancelable: true }));
        tile.dispatchEvent(new MouseEvent('mouseover', { bubbles: true, cancelable: true }));

        const btn = tile.querySelector('button[aria-label="Opsi lainnya"], flow-image-hotbar button:nth-child(3), flow-image-hotbar button:last-child');
        if (!btn) return { success: false, error: 'Tombol hotbar 3 tidak ditemukan.' };

        btn.click();
        return { success: true };
        """
        res_h = self.driver.execute_script(open_hotbar_script, [tile_index])
        if not isinstance(res_h, dict) or not res_h.get("success"):
            raise RuntimeError(f"Gagal membuka menu hotbar opsi pada tile ke-{tile_index}: {res_h}")

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
            raise RuntimeError(f"Gagal mengeklik menu Download pada tile ke-{tile_index}: {res_dl}")

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
            raise RuntimeError(f"Gagal mengeklik opsi resolusi 1K pada tile ke-{tile_index}: {res_1k}")

        return True

    def download_all_tiles(
        self,
        expected_count: int = 1,
        existing_files: set[str] | None = None,
        progress_callback: any = None,
        timeout: int = 60,
    ) -> list[Path]:
        """Memicu unduhan resolusi 1K untuk seluruh tile gambar hasil generasi di kanvas secara berurutan.

        Mendukung pengunduhan 1 hingga 4 gambar sekaligus sesuai jumlah variasi (-c 1 s/d -c 4).
        Memastikan setiap berkas unduhan benar-benar stabil dan selesai sebelum memicu unduhan berikutnya.

        Args:
            expected_count (int): Jumlah target gambar yang diharapkan (1-4).
            existing_files (set[str] | None): Berkas gambar yang sudah ada sebelum pengunduhan.
            progress_callback (callable | None): Callback laporan status unduhan per-gambar.
            timeout (int): Batas waktu maksimal unduhan per gambar dalam detik (default: 60).

        Returns:
            list[Path]: Daftar path berkas unduhan gambar baru (.jpg) yang berhasil diunduh.
        """
        if existing_files is None:
            existing_files = set()
            for d in self.download_dirs:
                if d.exists():
                    for f in list(d.glob("*.jpg")) + list(d.glob("*.jpeg")):
                        existing_files.add(str(f.resolve()))

        # Hitung jumlah tile aktual yang ada di kanvas
        tile_count = 0
        try:
            tile_count = int(self.driver.execute_script("return document.querySelectorAll('flow-image-tile').length;") or 0)
        except Exception:
            tile_count = 0

        target_downloads = min(tile_count, expected_count) if tile_count > 0 else expected_count
        if target_downloads <= 0:
            target_downloads = 1

        downloaded_files: list[Path] = []
        current_existing = set(existing_files)

        for idx in range(target_downloads):
            if progress_callback:
                progress_callback(idx + 1, target_downloads)

            # 1. Pemicu unduhan 1K pada tile ke-idx
            self.click_hotbar_and_download(tile_index=idx)

            # 2. Tunggu berkas unduhan selesai
            dl_file = self.wait_for_downloaded_file(existing_files=current_existing, timeout=timeout)
            downloaded_files.append(dl_file)
            current_existing.add(str(dl_file.resolve()))
            time.sleep(1.0)

        return downloaded_files

    def wait_for_downloaded_file(self, existing_files: set[str], timeout: int = 60) -> Path:
        """Memantau folder unduhan sampai berkas gambar .jpg baru selesai diunduh secara utuh.

        Memindai seluruh direktori unduhan yang valid di sistem (Downloads pengguna Windows,
        D:\\Downloads, dan direktori lokal workspace) untuk mendeteksi berkas baru,
        memastikan berkas bukan bagian dari berkas lama (`existing_files`), tidak berekstensi `.part`,
        dan ukuran berkasnya stabil (> 0 bytes).

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
            all_current_files = []
            for d in self.download_dirs:
                if d.exists():
                    all_current_files.extend(list(d.glob("*.jpg")) + list(d.glob("*.jpeg")))

            new_files = [f for f in all_current_files if str(f.resolve()) not in existing_files]

            if new_files:
                latest_file = max(new_files, key=lambda f: f.stat().st_mtime)

                part_files = list(latest_file.parent.glob(f"{latest_file.name}.part"))
                if not part_files:
                    size1 = latest_file.stat().st_size
                    time.sleep(0.5)
                    size2 = latest_file.stat().st_size
                    if size1 == size2 and size1 > 0:
                        return latest_file

            time.sleep(1.0)

        dirs_str = ", ".join(str(d) for d in self.download_dirs)
        raise TimeoutError(f"File .jpg hasil unduhan tidak terdeteksi di [{dirs_str}] dalam {timeout} detik.")

    def delete_current_tile(self, timeout: int = 15) -> bool:
        """Menghapus seluruh tile dari kanvas Google Flow ('Pindahkan ke sampah').

        Menjamin kanvas proyek selalu bersih total tanpa ada gambar lama yang menumpuk.

        Args:
            timeout (int): Batas waktu operasi penghapusan dalam detik (default: 15).

        Returns:
            bool: True jika proses pembersihan selesai.
        """
        self.delete_all_canvas_tiles()
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
# HIGH-LEVEL CALLABLE API FUNCTIONS (UNTUK LAYANAN MODUL PYTHON PROFESIONAL)
# ==============================================================================
def generate_image(
    prompt: str,
    output_path: str | Path | None = None,
    model: str = DEFAULT_MODEL,
    aspect_ratio: str = DEFAULT_ASPECT_RATIO,
    count: int | str = DEFAULT_COUNT,
    email: str | None = None,
    password: str | None = None,
    timeout: int = 180,
    max_retries: int | None = None,
    retry_delay: float = 12.0,
    auto_launch: bool = True,
    debug: bool = False,
    **kwargs: object,
) -> Path:
    """Fungsi utama tingkat tinggi untuk membuat, mengunduh, dan menyimpan gambar secara senyap.

    Fungsi ini menjalankan seluruh siklus kerja otomasi Google Flow secara 100% natif
    dalam mode headless di latar belakang tanpa jendela GUI dan tanpa mengganggu kursor (*zero cursor hijacking*):
    1. Memverifikasi/menjalankan Firefox Portable secara otomatis dalam mode -headless murni.
    2. Mendeteksi tab Google Flow aktif atau mengarahkannya ke proyek.
    3. Mengonfigurasi model AI (Banana Pro/Lite/2.1), aspek rasio (16:9, 1:1, 9:16, dll), dan kuantitas (x1-x4).
    4. Membersihkan kanvas dari seluruh tile lama agar steril.
    5. Mengisi prompt ke editor ProseMirror via native keystrokes dan memicu pembuatan gambar.
    6. Memantau progres hingga generasi selesai (0% -> 100%).
    7. Mengunduh gambar dalam resolusi asli 1K.
    8. Memindahkan berkas gambar dari folder unduhan ke direktori tujuan yang diminta.
    9. Menghapus tile gambar dari kanvas Google Flow ('Pindahkan ke sampah').

    Fitur Pemulihan Mandiri Tanpa Batas (Unlimited Self-Healing Auto-Retry):
    Jika proses render gagal di sisi Google Flow (misal terkena batas penggunaan atau kendala server),
    fungsi secara otomatis mendeteksi tile gagal, membersihkannya dari kanvas, menunggu jeda cooldown,
    menyegarkan halaman jika diperlukan, dan terus mencoba ulang tanpa batasan sampai berkas gambar berhasil diperoleh.

    Args:
        prompt (str): Deskripsi teks gambar yang ingin dibuat.
        output_path (str | Path | None): Jalur folder atau berkas tujuan penyimpanan gambar.
            - Jika berupa folder: berkas disimpan dengan format slug prompt dan timestamp.
            - Jika berupa path berkas .jpg: berkas disimpan persis dengan nama tersebut.
            - Jika None: otomatis disimpan di folder 'outputs/' pada root workspace.
        model (str): Rangkaian model AI (misal: 'Nano Banana Pro', 'Nano Banana 2 Lite', 'Nano Banana 2.1').
                     Dapat juga menggunakan singkatan: 'pro', 'lite', '2.1'. Default: 'Nano Banana Pro'.
        aspect_ratio (str): Aspek rasio gambar ('16:9', '4:3', '1:1', '3:4', '9:16' atau alias 'square', 'vertical').
                            Default: '16:9'.
        count (int | str): Kuantitas variasi gambar per generasi (1, 2, 3, 4 atau 'x1', 'x2', dst). Default: 1.
        email (str | None): Alamat email Google opsional untuk login otomatis mandiri.
        password (str | None): Kata sandi Google opsional untuk login otomatis mandiri.
        timeout (int): Batas waktu maksimal proses pembuatan gambar per percobaan dalam detik (default: 180).
        max_retries (int | None): Batas maksimal percobaan ulang (default: None, mengulang tanpa batas).
        retry_delay (float): Jeda waktu dalam detik sebelum mengulang percobaan berikutnya (default: 12.0).
        auto_launch (bool): Luncurkan Firefox Portable secara otomatis jika belum berjalan (default: True).
        debug (bool): Aktifkan mode debug untuk mendokumentasikan setiap langkah via tangkapan layar (default: False).
        **kwargs: Parameter opsional kompatibilitas mundur.

    Returns:
        Path: Lokasi absolut berkas gambar .jpg yang berhasil dibuat dan dipindahkan.

    Raises:
        RuntimeError: Jika seluruh percobaan gagal atau terjadi kegagalan fatal koneksi peramban.
        TimeoutError: Jika waktu tunggu pembuatan gambar atau pengunduhan habis.

    Example:
        >>> from image_generator import generate_image
        >>> # Generasi vertikal 9:16 untuk Reel / Shorts
        >>> file_path = generate_image(
        ...     prompt="astronot melayang di ruang angkasa fajar",
        ...     aspect_ratio="9:16",
        ...     model="pro",
        ...     output_path="hasil/"
        ... )
        >>> print("Gambar disimpan di:", file_path)
    """
    res = generate(
        prompt=prompt,
        output_path=output_path,
        model=model,
        aspect_ratio=aspect_ratio,
        count=count,
        email=email,
        password=password,
        timeout=timeout,
        max_retries=max_retries,
        retry_delay=retry_delay,
        auto_launch=auto_launch,
        debug=debug,
        **kwargs,
    )
    if len(res.file_paths) > 1:
        return res.file_paths
    return res.file_path


def generate(
    prompt: str,
    output_path: str | Path | None = None,
    model: str = DEFAULT_MODEL,
    aspect_ratio: str = DEFAULT_ASPECT_RATIO,
    count: int | str = DEFAULT_COUNT,
    email: str | None = None,
    password: str | None = None,
    timeout: int = 180,
    max_retries: int | None = None,
    retry_delay: float = 12.0,
    auto_launch: bool = True,
    debug: bool = False,
    **kwargs: object,
) -> GenerationResult:
    """Layanan modul Python tingkat profesional yang mengembalikan objek `GenerationResult` lengkap.

    Args:
        prompt (str): Deskripsi teks gambar yang ingin dibuat.
        output_path (str | Path | None): Jalur folder atau nama file tujuan.
        model (str): Model AI Google Flow yang dipilih (default: 'Nano Banana Pro').
        aspect_ratio (str): Aspek rasio kanvas gambar (default: '16:9').
        count (int | str): Kuantitas variasi gambar per generasi (default: 1).
        email (str | None): Alamat email Google opsional untuk login otomatis mandiri.
        password (str | None): Kata sandi Google opsional untuk login otomatis mandiri.
        timeout (int): Batas waktu maksimal per percobaan dalam detik (default: 180).
        max_retries (int | None): Batas percobaan maksimal (default: None, tanpa batas).
        retry_delay (float): Waktu tunggu antar-percobaan dalam detik (default: 12.0).
        auto_launch (bool): Luncurkan Firefox Portable headless otomatis jika belum aktif (default: True).
        debug (bool): Simpan tangkapan layar debug visual (default: False).

    Returns:
        GenerationResult: Objek terstruktur berisi file_path, file_paths, prompt, model, aspect_ratio,
                          count, attempt, dan duration_seconds.
    """
    start_ts = time.time()
    generator = ImageGenerator(
        model=model,
        aspect_ratio=aspect_ratio,
        count=count,
        email=email,
        password=password,
        debug=debug,
    )

    try:
        generator.ensure_browser(auto_launch=auto_launch)
        generator.connect()
        generator.find_flow_tab()
        generator.capture_debug_screenshot("01_canvas_ready", "Kondisi awal kanvas siap")

        last_error = None
        attempt = 1
        while True:
            if max_retries is not None and attempt > max_retries:
                raise RuntimeError(
                    f"Gagal membuat gambar setelah {max_retries} kali percobaan berturut-turut. Kesalahan terakhir: {last_error}"
                )

            try:
                # Bersihkan SELURUH tile di kanvas agar kanvas selalu kosong sebelum generasi baru
                generator.delete_all_canvas_tiles()

                # Segarkan halaman jika beberapa kali percobaan berturut-turut gagal
                if attempt > 1 and attempt % 4 == 0:
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

                initial_state = generator.submit_prompt(prompt)
                generator.capture_debug_screenshot(
                    f"prompt_submitted_att_{attempt}",
                    f"Prompt dikirim (Percobaan ke-{attempt})",
                )

                generator.hover_and_wait_tile(initial_state=initial_state, timeout=timeout)
                generator.capture_debug_screenshot(
                    f"render_success_att_{attempt}",
                    f"Render selesai (Percobaan ke-{attempt})",
                )

                expected_num = 1
                try:
                    expected_num = int(str(generator.count_str).replace("x", "").strip())
                except Exception:
                    expected_num = 1

                downloaded_files = generator.download_all_tiles(
                    expected_count=expected_num,
                    existing_files=existing,
                    timeout=60,
                )
                generator.capture_debug_screenshot(
                    f"download_completed_att_{attempt}",
                    f"Unduhan {len(downloaded_files)} gambar selesai (Percobaan ke-{attempt})",
                )

                # Pemindahan seluruh berkas unduhan ke lokasi tujuan dengan penamaan resolusi standar
                target_files: list[Path] = []
                total_dl = len(downloaded_files)
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

                for idx, dl_file in enumerate(downloaded_files):
                    dest_file = resolve_target_file_path(
                        output_path=output_path,
                        prompt=prompt,
                        index=idx,
                        total_count=total_dl,
                        workspace_dir=generator.workspace_dir,
                        timestamp=timestamp,
                    )
                    shutil.move(str(dl_file), str(dest_file))
                    target_files.append(dest_file)

                # Hapus SELURUH gambar dari kanvas peramban setelah berkas aman tersimpan
                try:
                    generator.delete_all_canvas_tiles()
                    generator.capture_debug_screenshot("canvas_after_cleanup", "Pembersihan kanvas selesai")
                except Exception as del_err:
                    console.print(f"[warning]⚠ Catatan pembersihan: {del_err}[/warning]")

                duration = time.time() - start_ts
                primary_file = target_files[0] if target_files else (generator.workspace_dir / "outputs" / "unknown.jpg")
                return GenerationResult(
                    file_path=primary_file,
                    file_paths=target_files,
                    prompt=prompt,
                    model=generator.model,
                    aspect_ratio=generator.aspect_ratio,
                    count=generator.count_str,
                    attempt=attempt,
                    duration_seconds=duration,
                )

            except (GenerationFailedError, TimeoutError) as attempt_err:
                last_error = attempt_err
                generator.capture_debug_screenshot(
                    f"failure_state_att_{attempt}",
                    f"Visual kegagalan (Percobaan ke-{attempt}): {attempt_err}",
                )
                generator.delete_all_canvas_tiles()
                retry_tag = f"Percobaan ke-{attempt}" if max_retries is None else f"Percobaan {attempt}/{max_retries}"
                console.print(
                    f"[warning]⚠ {retry_tag} terdeteksi gagal ({attempt_err}). "
                    f"Mengulang dari input prompt dalam {retry_delay:.0f} detik...[/warning]"
                )
                time.sleep(retry_delay)
                attempt += 1

    finally:
        generator.close()


# ==============================================================================
# BANTUAN TERMINAL (HELP INTERFACE)
# ==============================================================================
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


if __name__ == "__main__":
    sys.exit(main())

