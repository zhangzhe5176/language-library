import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


class DistReleaseTests(unittest.TestCase):
    def test_dist_passes_the_release_builder_validation(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "build_dist.py"), "--check-only"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("dist 构建与引用检查通过", result.stdout)
        self.assertIn("距离 800 MiB 目标余量", result.stdout)

    def test_dist_runtime_has_no_source_image_feature(self):
        app = (DIST / "app.js").read_text(encoding="utf-8")
        css = (DIST / "styles.css").read_text(encoding="utf-8")
        for marker in (
            "story.images", "sourceMarkup", "imageModalMarkup", "bindImageModal",
            "data-source-image", "data-image-modal", "data-image-close",
            "原书图片", "查看原图",
        ):
            self.assertNotIn(marker, app)
        for selector in (
            ".sourceGrid", ".sourcePreview", ".imageModal", ".modalBackdrop",
            ".modalPanel", ".modalClose", ".modalOpen",
        ):
            self.assertNotIn(selector, css)


if __name__ == "__main__":
    unittest.main()
