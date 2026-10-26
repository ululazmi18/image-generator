"""CUSTOM EXCEPTIONS — GOOGLE FLOW IMAGE GENERATOR.

Hierarki eksepsi terstruktur untuk menangani galat kanvas Google Flow,
kegagalan generasi tile, kuota/rate-limit terlampaui, dan ketiadaan biner peramban.
"""

from typing import Any, Optional


class ImageGeneratorError(RuntimeError):
    """Kelas dasar untuk seluruh pengecualian pada modul image-generator."""

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} (Rincian: {self.details})"
        return self.message


class GenerationFailedError(ImageGeneratorError):
    """Pengecualian yang dilemparkan saat Google Flow menampilkan tile galat/gagal di kanvas."""
    pass


class QuotaExceededError(GenerationFailedError):
    """Pengecualian yang dilemparkan saat akun Google Flow mencapai batas penggunaan (rate limit / quota)."""
    pass


class CanvasNavigationError(ImageGeneratorError):
    """Pengecualian yang dilemparkan saat tab Google Flow atau proyek tidak dapat diakses (404/expired)."""
    pass


class BrowserNotFoundError(ImageGeneratorError):
    """Pengecualian saat biner Firefox Portable tidak ditemukan dan port Marionette tidak aktif."""
    pass
