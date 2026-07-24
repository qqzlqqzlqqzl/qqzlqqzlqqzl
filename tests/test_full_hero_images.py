import sys
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from full_hero_images.common import positive_hint_score, reject_text
from full_hero_images.github_source import markdown_image_refs
from full_hero_images.image_quality import image_photo_metrics


class HeroPipelineTests(unittest.TestCase):
    def test_rejects_known_bad_assets(self):
        for value in [
            "https://opengraph.githubassets.com/1/org/repo",
            "https://example.com/favicon.png",
            "docs/3D-Front.png",
            "assets/schematic.png",
            "ui/settings-screenshot.jpg",
        ]:
            self.assertTrue(reject_text(value), value)

    def test_accepts_photo_filename_hints(self):
        self.assertGreater(positive_hint_score("docs/images/PXL_20240101_123456.jpg"), 5)
        self.assertGreater(positive_hint_score("assets/product_overview.jpg"), 5)

    def test_line_art_metrics(self):
        image = Image.new("RGB", (800, 500), "white")
        draw = ImageDraw.Draw(image)
        for x in range(50, 750, 50):
            draw.line((x, 50, x, 450), fill="black", width=2)
        metrics = image_photo_metrics(image)
        self.assertGreater(metrics["near_white"], 0.8)
        self.assertLess(metrics["colorfulness"], 5)

    def test_markdown_image_parser(self):
        text = "![Hardware photo](docs/product.jpg)\n<img src='assets/front.JPG' alt='front device'>"
        refs = markdown_image_refs(text)
        self.assertIn(("docs/product.jpg", "Hardware photo"), refs)
        self.assertIn(("assets/front.JPG", "front device"), refs)


if __name__ == "__main__":
    unittest.main()
