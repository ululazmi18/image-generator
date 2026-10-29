"""DATA MODELS & SCHEMAS — GOOGLE FLOW IMAGE GENERATOR.

Modul ini mendefinisikan Enum representasi model AI, rasio gambar, jumlah variasi,
serta dataclass konfigurasi dan hasil generasi (`GenerationConfig` dan `GenerationResult`).
"""

import base64
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path
import shutil
from typing import Any, Iterator

from image_generator.constants import (
    DEFAULT_ASPECT_RATIO,
    DEFAULT_COUNT,
    DEFAULT_MODEL,
    DEFAULT_RESOLUTION,
    normalize_aspect_ratio,
    normalize_count,
    normalize_model,
    normalize_resolution,
)


class Model(str, Enum):
    """Model AI Google Flow resmi."""

    PRO = "pro"
    LITE = "lite"
    V2_1 = "2.1"
    NANO_BANANA_PRO = "Nano Banana Pro"
    NANO_BANANA_LITE = "Nano Banana 2 Lite"
    NANO_BANANA_2_1 = "Nano Banana 2.1"


class AspectRatio(str, Enum):
    """Aspek rasio gambar resmi Google Flow."""

    LANDSCAPE_16_9 = "16:9"
    STANDARD_4_3 = "4:3"
    SQUARE_1_1 = "1:1"
    PORTRAIT_3_4 = "3:4"
    PORTRAIT_9_16 = "9:16"
    # Alias umum
    WIDE = "16:9"
    SQUARE = "1:1"
    VERTICAL = "9:16"


class Count(int, Enum):
    """Kuantitas variasi gambar yang dihasilkan."""

    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4


class Resolution(str, Enum):
    """Pilihan resolusi unduhan gambar Google Flow."""

    TWO_K = "2k"
    ONE_K = "1k"
    # Alias umum
    UPSCALED = "2k"
    HIGH = "2k"
    ORIGINAL = "1k"
    ASLI = "1k"


@dataclass
class GenerationConfig:
    """Objek konfigurasi pembuatan gambar untuk integrasi modul Python tingkat enterprise."""

    model: str | Model = DEFAULT_MODEL
    aspect_ratio: str | AspectRatio = DEFAULT_ASPECT_RATIO
    count: int | Count | str = DEFAULT_COUNT
    resolution: str | Resolution = DEFAULT_RESOLUTION
    output_path: str | Path | None = None
    timeout: int = 180
    max_retries: int | None = None
    retry_delay: float = 12.0
    email: str | None = None
    password: str | None = None
    auto_launch: bool = True
    debug: bool = False

    def normalized(self) -> tuple[str, str, str, str]:
        """Mengembalikan tuple ternormalisasi (model_resmi, aspek_rasio, string_kuantitas, resolusi)."""
        m = self.model.value if isinstance(self.model, Model) else self.model
        a = self.aspect_ratio.value if isinstance(self.aspect_ratio, AspectRatio) else self.aspect_ratio
        c = self.count.value if isinstance(self.count, Count) else self.count
        r = self.resolution.value if isinstance(self.resolution, Resolution) else self.resolution
        return (
            normalize_model(m),
            normalize_aspect_ratio(a),
            normalize_count(c),
            normalize_resolution(r),
        )


@dataclass
class GenerationResult:
    """Hasil keluaran proses pembuatan gambar lengkap dengan metadata teknis dan utilitas modern."""

    file_path: Path
    prompt: str
    model: str
    aspect_ratio: str
    count: str
    resolution: str = DEFAULT_RESOLUTION
    attempt: int = 1
    duration_seconds: float = 0.0
    file_paths: list[Path] = field(default_factory=list)
    success: bool = True
    error_message: str | None = None

    def __post_init__(self) -> None:
        if isinstance(self.file_path, str):
            self.file_path = Path(self.file_path)
        if not self.file_paths and self.file_path:
            self.file_paths = [self.file_path]
        elif self.file_paths and not self.file_path:
            self.file_path = self.file_paths[0]
        self.file_paths = [Path(p) if isinstance(p, str) else p for p in self.file_paths]

    @property
    def image_path(self) -> Path:
        """Alias untuk file_path (lokasi berkas gambar utama)."""
        return self.file_path

    @property
    def image_paths(self) -> list[Path]:
        """Alias untuk file_paths (daftar seluruh berkas gambar hasil generasi)."""
        return self.file_paths

    @property
    def model_name(self) -> str:
        """Alias untuk nama model AI."""
        return self.model

    @property
    def bytes(self) -> bytes:
        """Bytes biner mentah dari gambar utama."""
        return self.read_bytes(0)

    def read_bytes(self, index: int = 0) -> bytes:
        """Membaca bytes biner dari gambar ke-index."""
        target = self.file_paths[index] if 0 <= index < len(self.file_paths) else self.file_path
        return target.read_bytes()

    def to_base64(self, index: int = 0, data_uri: bool = True) -> str:
        """Mengonversi berkas gambar ke string Base64 (data URI atau base64 mentah)."""
        b = self.read_bytes(index)
        encoded = base64.b64encode(b).decode("ascii")
        if data_uri:
            return f"data:image/jpeg;base64,{encoded}"
        return encoded

    def to_pillow(self, index: int = 0) -> Any:
        """Membuka gambar sebagai objek PIL.Image (Pillow) jika terpasang di sistem."""
        try:
            from PIL import Image

            target = self.file_paths[index] if 0 <= index < len(self.file_paths) else self.file_path
            return Image.open(target)
        except ImportError:
            raise ImportError(
                "Pustaka Pillow belum terpasang. Pasang dengan 'pip install Pillow' untuk menggunakan .to_pillow()."
            )

    @property
    def image(self) -> Any:
        """Objek PIL Image dari gambar utama."""
        return self.to_pillow(0)

    def to_dict(self) -> dict[str, Any]:
        """Mengonversi seluruh metadata hasil generasi menjadi dictionary Python."""
        return {
            "success": self.success,
            "file_path": str(self.file_path),
            "file_paths": [str(p) for p in self.file_paths],
            "prompt": self.prompt,
            "model": self.model,
            "aspect_ratio": self.aspect_ratio,
            "count": self.count,
            "resolution": self.resolution,
            "attempt": self.attempt,
            "duration_seconds": self.duration_seconds,
            "error_message": self.error_message,
        }

    def to_json(self, indent: int = 2) -> str:
        """Mengonversi metadata hasil generasi ke format JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def save_to(self, destination: str | Path, index: int = 0) -> Path:
        """Menyimpan atau menyalin berkas gambar hasil generasi ke path tujuan lain."""
        src = self.file_paths[index] if 0 <= index < len(self.file_paths) else self.file_path
        dest = Path(destination).resolve()
        if dest.is_dir():
            dest = dest / src.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src), str(dest))
        return dest

    def __str__(self) -> str:
        return str(self.file_path)

    def __fspath__(self) -> str:
        return str(self.file_path)

    def __len__(self) -> int:
        return len(self.file_paths)

    def __getitem__(self, index: int) -> Path:
        return self.file_paths[index]

    def __iter__(self) -> Iterator[Path]:
        return iter(self.file_paths)

    def __bool__(self) -> bool:
        return self.success and bool(self.file_path and self.file_path.exists())


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
    import datetime
    import re

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

