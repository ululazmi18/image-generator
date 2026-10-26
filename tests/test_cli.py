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
            ) = parse_cli_args()

            self.assertEqual(prompt, "Robot AI di hutan")
            self.assertEqual(model, "Nano Banana Pro")
            self.assertEqual(ratio, "9:16")
            self.assertEqual(count, "x2")
            self.assertEqual(output, "hasil/")
            self.assertTrue(debug)
            self.assertIsNone(email)
            self.assertIsNone(pwd)

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
            prompt, output, model, ratio, count, timeout, debug, email, pwd = parse_cli_args()

            self.assertEqual(prompt, "Pemandangan alam pegunungan")
            self.assertEqual(model, "Nano Banana 2 Lite")
            self.assertEqual(ratio, "1:1")
            self.assertEqual(count, "x1")
            self.assertFalse(debug)


if __name__ == "__main__":
    unittest.main()
