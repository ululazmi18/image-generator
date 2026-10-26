"""TEST SUITE: MODELS & SCHEMAS — IMAGE GENERATOR."""

import json
from pathlib import Path
import tempfile
import unittest

from image_generator.models import (
    AspectRatio,
    Count,
    GenerationConfig,
    GenerationResult,
    Model,
    resolve_target_file_path,
)


class TestModelsAndSchemas(unittest.TestCase):
    """Pengujian unit Enum, Dataclass, dan resolve_target_file_path."""

    def test_enums(self) -> None:
        self.assertEqual(Model.PRO, "pro")
        self.assertEqual(AspectRatio.LANDSCAPE_16_9, "16:9")
        self.assertEqual(AspectRatio.WIDE, "16:9")
        self.assertEqual(Count.ONE, 1)
        self.assertEqual(Count.FOUR, 4)

    def test_generation_config(self) -> None:
        cfg = GenerationConfig(count=2, debug=True)
        self.assertEqual(cfg.count, 2)
        self.assertTrue(cfg.debug)
        self.assertEqual(cfg.model, "Nano Banana Pro")
        self.assertEqual(cfg.aspect_ratio, "16:9")
        norm_m, norm_a, norm_c = cfg.normalized()
        self.assertEqual(norm_m, "Nano Banana Pro")
        self.assertEqual(norm_a, "16:9")
        self.assertEqual(norm_c, "x2")

    def test_generation_result_to_dict_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "img1.jpg"
            file1.write_bytes(b"dummy_data")

            res = GenerationResult(
                success=True,
                file_path=file1,
                file_paths=[file1],
                prompt="Test prompt",
                model="Nano Banana Pro",
                aspect_ratio="16:9",
                count=1,
                attempt=1,
                duration_seconds=12.5,
            )

            self.assertTrue(res)
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0], file1)

            res_dict = res.to_dict()
            self.assertEqual(res_dict["success"], True)
            self.assertEqual(res_dict["prompt"], "Test prompt")

            json_str = res.to_json()
            parsed = json.loads(json_str)
            self.assertEqual(parsed["model"], "Nano Banana Pro")

    def test_resolve_target_file_path_single(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ws = Path(tmpdir)
            # 1. Output None -> outputs/{slug}_{timestamp}.jpg
            path1 = resolve_target_file_path(
                output_path=None,
                prompt="Neon Dragon",
                index=0,
                total_count=1,
                workspace_dir=ws,
                timestamp="20261026_120000",
            )
            self.assertEqual(path1.name, "Neon_Dragon_20261026_120000.jpg")

            # 2. Output specific filename
            path2 = resolve_target_file_path(
                output_path=ws / "my_custom_image.png",
                prompt="Neon Dragon",
                index=0,
                total_count=1,
                workspace_dir=ws,
            )
            self.assertEqual(path2.name, "my_custom_image.png")

    def test_resolve_target_file_path_multiple(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ws = Path(tmpdir)
            # 1. Output None, count = 2 -> outputs/{slug}_{timestamp}-1.jpg, -2.jpg
            path1 = resolve_target_file_path(
                output_path=None,
                prompt="Neon Dragon",
                index=0,
                total_count=2,
                workspace_dir=ws,
                timestamp="20261026_120000",
            )
            path2 = resolve_target_file_path(
                output_path=None,
                prompt="Neon Dragon",
                index=1,
                total_count=2,
                workspace_dir=ws,
                timestamp="20261026_120000",
            )
            self.assertEqual(path1.name, "Neon_Dragon_20261026_120000-1.jpg")
            self.assertEqual(path2.name, "Neon_Dragon_20261026_120000-2.jpg")

            # 2. Output specific file path, count = 2 -> file-1.jpg, file-2.jpg
            custom_path = ws / "pack.jpg"
            p1 = resolve_target_file_path(custom_path, "prompt", 0, 2, ws)
            p2 = resolve_target_file_path(custom_path, "prompt", 1, 2, ws)
            self.assertEqual(p1.name, "pack-1.jpg")
            self.assertEqual(p2.name, "pack-2.jpg")


if __name__ == "__main__":
    unittest.main()
