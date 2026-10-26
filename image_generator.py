"""IMAGE GENERATOR — GOOGLE FLOW BACKGROUND AUTOMATION COMPATIBILITY SHIM.

Berkas ini adalah shim kompatibilitas mundur (backward-compatibility shim) yang
mengarahkan pemanggilan berkas legacy langsung ke paket modular `image_generator`.
"""

import sys
from pathlib import Path

# Pastikan workspace root terdaftar di sys.path
_workspace_root = Path(__file__).resolve().parent
if str(_workspace_root) not in sys.path:
    sys.path.insert(0, str(_workspace_root))

from image_generator.cli import main, parse_cli_args, show_help
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
    COUNT_ALIASES,
    DEFAULT_ASPECT_RATIO,
    DEFAULT_COUNT,
    DEFAULT_MODEL,
    FLOW_HOME_URL,
    MODEL_ALIASES,
    normalize_aspect_ratio,
    normalize_count,
    normalize_model,
)
from image_generator.core import ImageGenerator
from image_generator.exceptions import (
    BrowserNotFoundError,
    CanvasNavigationError,
    GenerationFailedError,
    ImageGeneratorError,
    QuotaExceededError,
)
from image_generator.models import (
    AspectRatio,
    Count,
    GenerationConfig,
    GenerationResult,
    Model,
    resolve_target_file_path,
)

__version__ = "1.0.0"

if __name__ == "__main__":
    sys.exit(main())
