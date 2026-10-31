"""IMAGE GENERATOR — GOOGLE FLOW BACKGROUND AUTOMATION PACKAGE.

Modul otomasi generasi gambar Google Flow berbasis Firefox Portable Stealth,
100% senyap tanpa interupsi kursor pengguna (Zero Cursor Hijacking), dan
arsitektur modular PEP 517/518/621.
"""

from image_generator.client import (
    AsyncFlowClient,
    AsyncImageClient,
    FlowClient,
    ImageClient,
    ImageGeneratorClient,
    async_generate,
    async_generate_image,
    generate,
    generate_batch,
    generate_image,
)
from image_generator.constants import (
    ASPECT_RATIO_ALIASES,
    AVAILABLE_ASPECT_RATIOS,
    AVAILABLE_COUNTS,
    AVAILABLE_MODELS,
    AVAILABLE_RESOLUTIONS,
    COUNT_ALIASES,
    DEFAULT_ASPECT_RATIO,
    DEFAULT_COUNT,
    DEFAULT_MODEL,
    DEFAULT_RESOLUTION,
    FLOW_HOME_URL,
    MODEL_ALIASES,
    RATIO_ICON_MAP,
    RESOLUTION_ALIASES,
    normalize_aspect_ratio,
    normalize_count,
    normalize_model,
    normalize_resolution,
)

from image_generator.core import ImageGenerator
from image_generator.exceptions import (
    BrowserNotFoundError,
    CanvasNavigationError,
    GenerationFailedError,
    ImageGeneratorError,
    PolicyViolationError,
    QuotaExceededError,
)
from image_generator.models import (
    AspectRatio,
    Count,
    GenerationConfig,
    GenerationResult,
    Model,
    Resolution,
    resolve_target_file_path,
)

__version__ = "1.0.0"
__author__ = "Ulul Azmi"

__all__ = [
    # Versi
    "__version__",
    # Constants & Normalizers
    "DEFAULT_MODEL",
    "DEFAULT_ASPECT_RATIO",
    "DEFAULT_COUNT",
    "DEFAULT_RESOLUTION",
    "AVAILABLE_MODELS",
    "AVAILABLE_ASPECT_RATIOS",
    "AVAILABLE_COUNTS",
    "AVAILABLE_RESOLUTIONS",
    "MODEL_ALIASES",
    "ASPECT_RATIO_ALIASES",
    "COUNT_ALIASES",
    "RESOLUTION_ALIASES",
    "FLOW_HOME_URL",
    "RATIO_ICON_MAP",
    "normalize_model",
    "normalize_aspect_ratio",
    "normalize_count",
    "normalize_resolution",
    # Models & Enums
    "Model",
    "AspectRatio",
    "Count",
    "Resolution",
    "GenerationConfig",
    "GenerationResult",
    "resolve_target_file_path",
    # Exceptions
    "ImageGeneratorError",
    "GenerationFailedError",
    "QuotaExceededError",
    "PolicyViolationError",
    "CanvasNavigationError",
    "BrowserNotFoundError",
    # Core Controller
    "ImageGenerator",
    # Clients & Helpers
    "ImageClient",
    "FlowClient",
    "ImageGeneratorClient",
    "AsyncImageClient",
    "AsyncFlowClient",
    "generate",
    "generate_image",
    "generate_batch",
    "async_generate",
    "async_generate_image",
]
