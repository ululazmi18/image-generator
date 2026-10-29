"""CONSTANTS & NORMALIZATION UTILITIES — GOOGLE FLOW IMAGE GENERATOR.

Modul ini menyimpan seluruh konstanta model AI Google Flow, aspek rasio, kuantitas,
pemetaan alias percakapan, tema visual Rich terminal, dan fungsi penentu path file.
"""

import datetime
from pathlib import Path
import re
from typing import Literal

from rich.console import Console
from rich.theme import Theme

# ==============================================================================
# TEMA TERMINAL & ENCODING
# ==============================================================================
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
# TIPE DAN NILAI DEFAULT
# ==============================================================================
AspectRatioType = Literal["16:9", "4:3", "1:1", "3:4", "9:16"]
ModelType = Literal["Nano Banana Pro", "Nano Banana 2 Lite", "Nano Banana 2.1"]
CountType = Literal[1, 2, 3, 4, "x1", "x2", "x3", "x4"]
ResolutionType = Literal["2k", "1k"]

DEFAULT_MODEL: str = "Nano Banana Pro"
DEFAULT_ASPECT_RATIO: str = "16:9"
DEFAULT_COUNT: int = 1
DEFAULT_RESOLUTION: str = "2k"

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

AVAILABLE_RESOLUTIONS: list[str] = [
    "2k",
    "1k",
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

# Alias eksternal untuk kompatibilitas
ASPECT_RATIO_ALIASES: dict[str, str] = RATIO_ALIASES
COUNT_ALIASES: dict[str, str] = {
    "1": "x1",
    "x1": "x1",
    "2": "x2",
    "x2": "x2",
    "3": "x3",
    "x3": "x3",
    "4": "x4",
    "x4": "x4",
}

# Pemetaan alias resolusi ke format standar kanonikal ('2k' atau '1k')
RESOLUTION_ALIASES: dict[str, str] = {
    "2k": "2k",
    "2": "2k",
    "upscaled": "2k",
    "ditingkatkan": "2k",
    "resolusi ditingkatkan": "2k",
    "high": "2k",
    "hd": "2k",
    "1k": "1k",
    "1": "1k",
    "original": "1k",
    "asli": "1k",
    "ukuran asli": "1k",
    "standard": "1k",
}


def normalize_model(val: str | None) -> str:
    """Menormalkan input nama model AI ke format kanonikal resmi Google Flow.

    Args:
        val (str | None): Input nama model (misal: 'pro', 'lite', '2.1').

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

    Args:
        val (str | None): Input nilai rasio (misal: '16:9', 'square', 'vertical').

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
        val (int | str | None): Jumlah gambar (1..4 atau 'x1'..'x4').

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


def normalize_resolution(val: str | None) -> str:
    """Menormalkan input resolusi unduhan ke format kanonikal ('2k' atau '1k').

    Google Flow menyediakan opsi resolusi:
    - '2k': Opsi baris kedua ('2K - Resolusi ditingkatkan'), default standar.
    - '1k': Opsi baris pertama ('1K - Ukuran asli').

    Args:
        val (str | None): Input resolusi (misal: '2k', '1k', 'original', 'upscaled').

    Returns:
        str: Resolusi kanonikal ('2k' atau '1k', default: '2k').
    """
    if not val:
        return DEFAULT_RESOLUTION
    clean = str(val).strip().lower()
    if clean in RESOLUTION_ALIASES:
        return RESOLUTION_ALIASES[clean]
    for r in AVAILABLE_RESOLUTIONS:
        if clean == r:
            return r
    return DEFAULT_RESOLUTION


def resolve_target_file_path(
    output_path: str | Path | None,
    prompt: str,
    index: int,
    total_count: int,
    workspace_dir: Path,
    timestamp: str | None = None,
) -> Path:
    """Menentukan path tujuan berkas gambar hasil generasi sesuai konvensi penamaan standar.

    Args:
        output_path: Lokasi atau nama file tujuan.
        prompt: Prompt teks untuk pembentukan slug jika disimpan di folder.
        index: Indeks gambar saat ini (0-indexed).
        total_count: Jumlah total gambar yang dihasilkan dan diunduh.
        workspace_dir: Direktori workspace root.
        timestamp: Timestamp format '%Y%m%d_%H%M%S'.

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
