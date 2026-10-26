"""TEST SUITE: CONSTANTS & NORMALIZERS — IMAGE GENERATOR."""

import unittest

from image_generator.constants import (
    AVAILABLE_ASPECT_RATIOS,
    AVAILABLE_COUNTS,
    AVAILABLE_MODELS,
    DEFAULT_ASPECT_RATIO,
    DEFAULT_COUNT,
    DEFAULT_MODEL,
    normalize_aspect_ratio,
    normalize_count,
    normalize_model,
)


class TestConstantsAndNormalizers(unittest.TestCase):
    """Pengujian unit normalisasi model, rasio, dan jumlah variasi."""

    def test_normalize_model(self) -> None:
        self.assertEqual(normalize_model("pro"), "Nano Banana Pro")
        self.assertEqual(normalize_model("banana pro"), "Nano Banana Pro")
        self.assertEqual(normalize_model("lite"), "Nano Banana 2 Lite")
        self.assertEqual(normalize_model("2 lite"), "Nano Banana 2 Lite")
        self.assertEqual(normalize_model("2.1"), "Nano Banana 2.1")
        self.assertEqual(normalize_model("Nano Banana Pro"), "Nano Banana Pro")
        # None / invalid fallback
        self.assertEqual(normalize_model(None), DEFAULT_MODEL)
        self.assertEqual(normalize_model("unknown_model"), DEFAULT_MODEL)

    def test_normalize_aspect_ratio(self) -> None:
        self.assertEqual(normalize_aspect_ratio("16:9"), "16:9")
        self.assertEqual(normalize_aspect_ratio("wide"), "16:9")
        self.assertEqual(normalize_aspect_ratio("landscape"), "16:9")
        self.assertEqual(normalize_aspect_ratio("1:1"), "1:1")
        self.assertEqual(normalize_aspect_ratio("square"), "1:1")
        self.assertEqual(normalize_aspect_ratio("kotak"), "1:1")
        self.assertEqual(normalize_aspect_ratio("9:16"), "9:16")
        self.assertEqual(normalize_aspect_ratio("vertical"), "9:16")
        self.assertEqual(normalize_aspect_ratio("shorts"), "9:16")
        # None / invalid fallback
        self.assertEqual(normalize_aspect_ratio(None), DEFAULT_ASPECT_RATIO)
        self.assertEqual(normalize_aspect_ratio("invalid"), DEFAULT_ASPECT_RATIO)

    def test_normalize_count(self) -> None:
        self.assertEqual(normalize_count(1), "x1")
        self.assertEqual(normalize_count("1"), "x1")
        self.assertEqual(normalize_count("x1"), "x1")
        self.assertEqual(normalize_count(2), "x2")
        self.assertEqual(normalize_count("2"), "x2")
        self.assertEqual(normalize_count("x2"), "x2")
        self.assertEqual(normalize_count(4), "x4")
        self.assertEqual(normalize_count(None), f"x{DEFAULT_COUNT}")
        self.assertEqual(normalize_count(99), f"x{DEFAULT_COUNT}")

    def test_ratio_icon_map(self) -> None:
        from image_generator.constants import RATIO_ICON_MAP
        self.assertEqual(RATIO_ICON_MAP["16:9"], "crop_16_9")
        self.assertEqual(RATIO_ICON_MAP["1:1"], "crop_square")
        self.assertEqual(RATIO_ICON_MAP["9:16"], "crop_9_16")
        self.assertEqual(RATIO_ICON_MAP["4:3"], "crop_landscape")
        self.assertEqual(RATIO_ICON_MAP["3:4"], "crop_portrait")


if __name__ == "__main__":
    unittest.main()
