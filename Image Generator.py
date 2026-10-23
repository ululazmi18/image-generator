"""Image Generator — Entrypoint.

Delegates execution to image_generator.py.
"""
import sys
from image_generator import main, generate_image, ImageGenerator

if __name__ == "__main__":
    sys.exit(main())
