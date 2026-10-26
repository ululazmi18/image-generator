"""HIGH-LEVEL CLIENTS & CONVENIENCE APIS — GOOGLE FLOW IMAGE GENERATOR.

Modul ini menyediakan klien berstatus (ImageClient, FlowClient, AsyncImageClient)
serta fungsi-fungsi kemudahan tingkat tinggi (generate, generate_image, generate_batch, async_generate).
"""

import asyncio
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from image_generator.constants import (
    DEFAULT_ASPECT_RATIO,
    DEFAULT_COUNT,
    DEFAULT_MODEL,
    normalize_aspect_ratio,
    normalize_count,
    normalize_model,
)
from image_generator.core import ImageGenerator
from image_generator.models import (
    AspectRatio,
    Count,
    GenerationConfig,
    GenerationResult,
    Model,
)


class ImageClient:
    """Klien berstatus (*stateful client*) tingkat enterprise untuk generasi gambar Google Flow.

    Mempertahankan koneksi peramban aktif (*session reuse*) di antara pemanggilan berulang,
    menghemat 15-30 detik per pembuatan gambar dibanding membuka-tutup peramban setiap saat.
    Dapat digunakan langsung atau sebagai context manager (`with ImageClient() as client:`).

    Contoh Penggunaan:
        >>> with ImageClient(model="pro", aspect_ratio="16:9") as client:
        ...     res1 = client.generate("mobil balap futuristik di tokyo fajar")
        ...     res2 = client.generate("mobil balap klasik di pedesaan inggris")
        ...     print(f"Hasil 1: {res1.image_path}")
        ...     print(f"Hasil 2: {res2.image_path}")
    """

    def __init__(
        self,
        workspace_dir: Path | None = None,
        model: str | Model = DEFAULT_MODEL,
        aspect_ratio: str | AspectRatio = DEFAULT_ASPECT_RATIO,
        count: int | Count | str = DEFAULT_COUNT,
        email: str | None = None,
        password: str | None = None,
        auto_launch: bool = True,
        debug: bool = False,
    ):
        self.workspace_dir = workspace_dir
        self.default_model = model.value if isinstance(model, Model) else model
        self.default_aspect_ratio = aspect_ratio.value if isinstance(aspect_ratio, AspectRatio) else aspect_ratio
        self.default_count = count.value if isinstance(count, Count) else count
        self.email = email
        self.password = password
        self.auto_launch = auto_launch
        self.debug = debug
        self._generator: ImageGenerator | None = None

    def __enter__(self) -> "ImageClient":
        self._ensure_generator()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def _ensure_generator(
        self,
        model: str | Model | None = None,
        aspect_ratio: str | AspectRatio | None = None,
        count: int | Count | str | None = None,
    ) -> ImageGenerator:
        req_model = model.value if isinstance(model, Model) else model
        req_ratio = aspect_ratio.value if isinstance(aspect_ratio, AspectRatio) else aspect_ratio
        req_count = count.value if isinstance(count, Count) else count

        target_model = normalize_model(req_model or self.default_model)
        target_ratio = normalize_aspect_ratio(req_ratio or self.default_aspect_ratio)
        target_count = normalize_count(req_count if req_count is not None else self.default_count)

        if self._generator is None:
            self._generator = ImageGenerator(
                workspace_dir=self.workspace_dir,
                model=target_model,
                aspect_ratio=target_ratio,
                count=target_count,
                email=self.email,
                password=self.password,
                debug=self.debug,
            )
            self._generator.ensure_browser(auto_launch=self.auto_launch)
            self._generator.connect()
            self._generator.find_flow_tab()
            self._generator.capture_debug_screenshot("01_canvas_ready", "Kondisi awal kanvas siap")
        else:
            self._generator.model = target_model
            self._generator.aspect_ratio = target_ratio
            self._generator.count_str = target_count

        return self._generator

    def generate(
        self,
        prompt: str,
        output_path: str | Path | None = None,
        model: str | Model | None = None,
        aspect_ratio: str | AspectRatio | None = None,
        count: int | Count | str | None = None,
        timeout: int = 180,
        max_retries: int | None = None,
        retry_delay: float = 12.0,
        config: GenerationConfig | None = None,
        **kwargs: Any,
    ) -> GenerationResult:
        """Menghasilkan gambar dalam sesi peramban aktif dan mengembalikan objek `GenerationResult`."""
        if config is not None:
            model = model or config.model
            aspect_ratio = aspect_ratio or config.aspect_ratio
            count = count if count is not None else config.count
            output_path = output_path or config.output_path
            timeout = timeout if timeout != 180 else config.timeout
            max_retries = max_retries if max_retries is not None else config.max_retries
            retry_delay = retry_delay if retry_delay != 12.0 else config.retry_delay

        gen = self._ensure_generator(model=model, aspect_ratio=aspect_ratio, count=count)
        return gen.generate_flow(
            prompt=prompt,
            output_path=output_path,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
        )

    def generate_image(
        self,
        prompt: str,
        output_path: str | Path | None = None,
        **kwargs: Any,
    ) -> Path | list[Path]:
        """Shorthand yang mengembalikan Path berkas lokal (atau list[Path] jika -c >= 2)."""
        res = self.generate(prompt=prompt, output_path=output_path, **kwargs)
        if len(res.file_paths) > 1:
            return res.file_paths
        return res.file_path

    def batch(
        self,
        prompts: Sequence[str],
        output_dir: str | Path | None = None,
        on_progress: Callable[[int, int, GenerationResult], None] | None = None,
        **kwargs: Any,
    ) -> list[GenerationResult]:
        """Menghasilkan sekumpulan gambar secara sekuensial dalam satu sesi peramban aktif."""
        results: list[GenerationResult] = []
        total = len(prompts)
        for idx, p in enumerate(prompts):
            res = self.generate(prompt=p, output_path=output_dir, **kwargs)
            results.append(res)
            if on_progress:
                on_progress(idx + 1, total, res)
        return results

    def close(self) -> None:
        """Menutup koneksi soket dan mematikan peramban latar belakang jika diluncurkan oleh klien."""
        if self._generator is not None:
            try:
                self._generator.close()
            finally:
                self._generator = None


# Alias resmi untuk ImageClient
FlowClient = ImageClient
ImageGeneratorClient = ImageClient


class AsyncImageClient:
    """Klien asynchronous non-blocking berbasis `ImageClient` untuk framework modern (FastAPI, asyncio, bot)."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._sync_client = ImageClient(*args, **kwargs)

    async def __aenter__(self) -> "AsyncImageClient":
        await asyncio.to_thread(self._sync_client.__enter__)
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await asyncio.to_thread(self._sync_client.__exit__, exc_type, exc_val, exc_tb)

    async def generate(self, prompt: str, **kwargs: Any) -> GenerationResult:
        """Versi asynchronous dari generate()."""
        return await asyncio.to_thread(self._sync_client.generate, prompt, **kwargs)

    async def generate_image(self, prompt: str, **kwargs: Any) -> Path | list[Path]:
        """Versi asynchronous dari generate_image()."""
        return await asyncio.to_thread(self._sync_client.generate_image, prompt, **kwargs)

    async def batch(
        self,
        prompts: Sequence[str],
        output_dir: str | Path | None = None,
        on_progress: Callable[[int, int, GenerationResult], None] | None = None,
        **kwargs: Any,
    ) -> list[GenerationResult]:
        """Versi asynchronous dari batch()."""
        return await asyncio.to_thread(
            self._sync_client.batch, prompts, output_dir=output_dir, on_progress=on_progress, **kwargs
        )

    async def close(self) -> None:
        """Versi asynchronous dari close()."""
        await asyncio.to_thread(self._sync_client.close)


AsyncFlowClient = AsyncImageClient


# ==============================================================================
# HIGH-LEVEL CALLABLE API FUNCTIONS (COMPATIBLE & VERSATILE)
# ==============================================================================

def generate(
    prompt: str,
    output_path: str | Path | None = None,
    model: str | Model = DEFAULT_MODEL,
    aspect_ratio: str | AspectRatio = DEFAULT_ASPECT_RATIO,
    count: int | Count | str = DEFAULT_COUNT,
    email: str | None = None,
    password: str | None = None,
    timeout: int = 180,
    max_retries: int | None = None,
    retry_delay: float = 12.0,
    auto_launch: bool = True,
    debug: bool = False,
    client: ImageClient | None = None,
    config: GenerationConfig | None = None,
    **kwargs: Any,
) -> GenerationResult:
    """Layanan modul Python tingkat profesional yang mengembalikan objek `GenerationResult` lengkap.

    Mendukung berbagai gaya pemanggilan:
    1. Standar: `generate("prompt")`
    2. Enums: `generate("prompt", model=Model.PRO, aspect_ratio=AspectRatio.SQUARE_1_1)`
    3. Konfigurasi: `generate("prompt", config=cfg)`
    4. Sesi Reusable: `generate("prompt", client=client)`

    Args:
        prompt (str): Deskripsi teks gambar yang ingin dibuat.
        output_path (str | Path | None): Jalur folder atau nama file tujuan.
        model (str | Model): Model AI Google Flow (default: 'pro' / 'Nano Banana Pro').
        aspect_ratio (str | AspectRatio): Aspek rasio kanvas gambar (default: '16:9').
        count (int | Count | str): Kuantitas variasi gambar per generasi (default: 1).
        email (str | None): Alamat email Google opsional untuk login otomatis mandiri.
        password (str | None): Kata sandi Google opsional untuk login otomatis mandiri.
        timeout (int): Batas waktu maksimal per percobaan dalam detik (default: 180).
        max_retries (int | None): Batas percobaan maksimal (default: None, tanpa batas).
        retry_delay (float): Waktu tunggu antar-percobaan dalam detik (default: 12.0).
        auto_launch (bool): Luncurkan peramban headless otomatis jika belum aktif (default: True).
        debug (bool): Simpan tangkapan layar debug visual (default: False).
        client (ImageClient | None): Instance klien aktif untuk sesi berkelanjutan (opsional).
        config (GenerationConfig | None): Objek konfigurasi alternatif (opsional).

    Returns:
        GenerationResult: Objek terstruktur kaya metadata, bytes, to_base64(), to_pillow(), metadata, dll.
    """
    if config is not None:
        model = config.model
        aspect_ratio = config.aspect_ratio
        count = count if count != DEFAULT_COUNT else config.count
        output_path = output_path or config.output_path
        timeout = timeout if timeout != 180 else config.timeout
        max_retries = max_retries if max_retries is not None else config.max_retries
        retry_delay = retry_delay if retry_delay != 12.0 else config.retry_delay
        email = email or config.email
        password = password or config.password
        auto_launch = config.auto_launch
        debug = config.debug

    if client is not None:
        return client.generate(
            prompt=prompt,
            output_path=output_path,
            model=model,
            aspect_ratio=aspect_ratio,
            count=count,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
            **kwargs,
        )

    with ImageClient(
        model=model,
        aspect_ratio=aspect_ratio,
        count=count,
        email=email,
        password=password,
        auto_launch=auto_launch,
        debug=debug,
    ) as temp_client:
        return temp_client.generate(
            prompt=prompt,
            output_path=output_path,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
            **kwargs,
        )


def generate_image(
    prompt: str,
    output_path: str | Path | None = None,
    model: str | Model = DEFAULT_MODEL,
    aspect_ratio: str | AspectRatio = DEFAULT_ASPECT_RATIO,
    count: int | Count | str = DEFAULT_COUNT,
    email: str | None = None,
    password: str | None = None,
    timeout: int = 180,
    max_retries: int | None = None,
    retry_delay: float = 12.0,
    auto_launch: bool = True,
    debug: bool = False,
    client: ImageClient | None = None,
    config: GenerationConfig | None = None,
    **kwargs: Any,
) -> Path | list[Path]:
    """Fungsi praktis klasik yang mengembalikan Path berkas gambar (atau list[Path] jika variasi >= 2)."""
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
        client=client,
        config=config,
        **kwargs,
    )
    if len(res.file_paths) > 1:
        return res.file_paths
    return res.file_path


def generate_batch(
    prompts: Sequence[str],
    output_dir: str | Path | None = None,
    model: str | Model = DEFAULT_MODEL,
    aspect_ratio: str | AspectRatio = DEFAULT_ASPECT_RATIO,
    count: int | Count | str = DEFAULT_COUNT,
    email: str | None = None,
    password: str | None = None,
    client: ImageClient | None = None,
    progress_callback: Callable[[int, int, GenerationResult], None] | None = None,
    **kwargs: Any,
) -> list[GenerationResult]:
    """Menghasilkan banyak gambar dari sekumpulan prompt secara efisien dalam satu sesi peramban aktif."""
    if client is not None:
        return client.batch(prompts, output_dir=output_dir, on_progress=progress_callback, **kwargs)

    with ImageClient(
        model=model,
        aspect_ratio=aspect_ratio,
        count=count,
        email=email,
        password=password,
    ) as temp_client:
        return temp_client.batch(prompts, output_dir=output_dir, on_progress=progress_callback, **kwargs)


async def async_generate(
    prompt: str,
    *args: Any,
    **kwargs: Any,
) -> GenerationResult:
    """Versi asynchronous non-blocking dari `generate()` untuk integrasi framework asyncio modern."""
    return await asyncio.to_thread(generate, prompt, *args, **kwargs)


async def async_generate_image(
    prompt: str,
    *args: Any,
    **kwargs: Any,
) -> Path | list[Path]:
    """Versi asynchronous non-blocking dari `generate_image()` untuk integrasi framework asyncio modern."""
    return await asyncio.to_thread(generate_image, prompt, *args, **kwargs)


# ==============================================================================
