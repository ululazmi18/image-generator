"""TEST SUITE: CLI PARSER — IMAGE GENERATOR."""

import sys
import unittest
from unittest.mock import patch

from image_generator.cli import parse_cli_args


class TestCliParser(unittest.TestCase):
    """Pengujian unit parser parameter baris perintah (CLI)."""

    def test_parse_prompt_and_flags(self) -> None:
        test_args = [
            "image_generator.py",
            "-p",
            "Robot AI di hutan",
            "-m",
            "pro",
            "-a",
            "9:16",
            "-c",
            "2",
            "-o",
            "hasil/",
            "--debug",
        ]
        with patch.object(sys, "argv", test_args):
            (
                prompt,
                output,
                model,
                ratio,
                count,
                timeout,
                debug,
                email,
                pwd,
                resolution,
            ) = parse_cli_args()

            self.assertEqual(prompt, "Robot AI di hutan")
            self.assertEqual(model, "Nano Banana Pro")
            self.assertEqual(ratio, "9:16")
            self.assertEqual(count, "x2")
            self.assertEqual(output, "hasil/")
            self.assertTrue(debug)
            self.assertIsNone(email)
            self.assertIsNone(pwd)
            self.assertEqual(resolution, "2k")  # Default is 2k

    def test_parse_positional_prompt(self) -> None:
        test_args = [
            "image_generator.py",
            "--model",
            "lite",
            "--ar",
            "1:1",
            "Pemandangan alam pegunungan",
        ]
        with patch.object(sys, "argv", test_args):
            (
                prompt,
                output,
                model,
                ratio,
                count,
                timeout,
                debug,
                email,
                pwd,
                resolution,
            ) = parse_cli_args()

            self.assertEqual(prompt, "Pemandangan alam pegunungan")
            self.assertEqual(model, "Nano Banana 2 Lite")
            self.assertEqual(ratio, "1:1")
            self.assertEqual(count, "x1")
            self.assertFalse(debug)
            self.assertEqual(resolution, "2k")

    def test_parse_resolution_flags(self) -> None:
        # Flag --resolution 1k
        test_args_1k = ["image_generator.py", "-p", "Test", "--resolution", "1k"]
        with patch.object(sys, "argv", test_args_1k):
            *_, resolution = parse_cli_args()
            self.assertEqual(resolution, "1k")

        # Flag --res 2k
        test_args_2k = ["image_generator.py", "-p", "Test", "--res", "2k"]
        with patch.object(sys, "argv", test_args_2k):
            *_, resolution = parse_cli_args()
            self.assertEqual(resolution, "2k")

        # Flag -r 1k
        test_args_r = ["image_generator.py", "-p", "Test", "-r", "original"]
        with patch.object(sys, "argv", test_args_r):
            *_, resolution = parse_cli_args()
            self.assertEqual(resolution, "1k")


if __name__ == "__main__":
    unittest.main()
