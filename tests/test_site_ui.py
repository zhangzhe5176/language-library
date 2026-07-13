import json
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEVELS = ("n1", "n2", "n3", "n4", "n5")
EXPECTED = {
    "n1": (27, 494, 2571),
    "n2": (23, 452, 2360),
    "n3": (18, 371, 2014),
    "n4": (13, 262, 1035),
    "n5": (24, 373, 1136),
}


def load_level(level: str) -> dict:
    text = (ROOT / "data" / f"{level}-data.js").read_text(encoding="utf-8")
    wrapper = "N3_DATA" if level == "n3" else "LEVEL_DATA"
    match = re.fullmatch(rf"window\.{wrapper}\s*=\s*(\{{.*\}});\s*", text, re.DOTALL)
    if not match:
        raise AssertionError(f"unexpected wrapper for {level}")
    return json.loads(match.group(1))


class ProductionSiteTests(unittest.TestCase):
    def test_real_statistics_match_contract(self):
        totals = [0, 0, 0]
        for level, expected in EXPECTED.items():
            data = load_level(level)
            actual = (
                len(data["topics"]),
                len(data["stories"]),
                sum(len(story.get("vocab", [])) for story in data["stories"]),
            )
            self.assertEqual(actual, expected)
            totals = [left + right for left, right in zip(totals, actual)]
        self.assertEqual(tuple(totals), (105, 1952, 9116))

    def test_production_information_architecture_exists(self):
        self.assertTrue((ROOT / "index.html").is_file())
        self.assertTrue((ROOT / "levels" / "japanese" / "index.html").is_file())
        for level in LEVELS:
            level_dir = ROOT / "levels" / level
            for name in ("index.html", "topics.html", "topic.html"):
                self.assertTrue((level_dir / name).is_file(), f"missing {level}/{name}")
            self.assertIn('data-page="level-home"', (level_dir / "index.html").read_text(encoding="utf-8"))
            self.assertIn('data-page="topics"', (level_dir / "topics.html").read_text(encoding="utf-8"))
            self.assertIn('data-page="topic"', (level_dir / "topic.html").read_text(encoding="utf-8"))

    def test_all_level_shells_use_shared_runtime_and_level_attribute(self):
        for level in LEVELS:
            data = load_level(level)
            names = ["index.html", "topics.html", "topic.html"]
            names.extend(f"topic-{topic['id']:02d}.html" for topic in data["topics"])
            for name in names:
                text = (ROOT / "levels" / level / name).read_text(encoding="utf-8")
                self.assertIn(f'data-level="{level}"', text)
                self.assertIn("../../state.js", text)
                self.assertIn("../../app.js", text)
                self.assertIn(f"../../data/{level}-data.js", text)
                self.assertNotIn('href="/', text)
                self.assertNotIn('src="/', text)

    def test_n3_is_migrated_and_keeps_historical_assets(self):
        index = (ROOT / "levels" / "n3" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-page="level-home"', index)
        self.assertIn('data-level="n3"', index)
        app = (ROOT / "app.js").read_text(encoding="utf-8")
        self.assertIn('level === "n3" ? "assets/audio"', app)
        data = load_level("n3")
        self.assertTrue(all(image.startswith("assets/entries/") for story in data["stories"] for image in story["images"]))

    def test_n3_blank_transition_pages_are_not_published(self):
        stories = {story["id"]: story for story in load_level("n3")["stories"]}
        self.assertEqual(stories[168]["images"], ["assets/entries/T168_1.png"])
        self.assertEqual(stories[199]["images"], ["assets/entries/T199_1.png"])
        self.assertTrue((ROOT / "assets" / "entries" / "T168_2.png").is_file())
        self.assertTrue((ROOT / "assets" / "entries" / "T199_2.png").is_file())

    def test_english_legacy_urls_are_consistent_planned_pages(self):
        for name in ("index.html", "sample.html"):
            text = (ROOT / "levels" / "english" / name).read_text(encoding="utf-8")
            self.assertIn("English / 英语", text)
            self.assertIn("规划中", text)
            self.assertIn('href="../../index.html"', text)
            self.assertIn('href="../../favicon.svg"', text)
            self.assertIn('href="../../favicon.ico"', text)
            for stale in ("本地版", "旧样张", "测试版", "开发说明", "english-outline.js"):
                self.assertNotIn(stale, text)

    def test_all_formal_pages_reference_the_local_favicon(self):
        favicon = ROOT / "favicon.svg"
        fallback = ROOT / "favicon.ico"
        self.assertTrue(favicon.is_file())
        self.assertTrue(fallback.is_file())
        ET.parse(favicon)
        self.assertTrue(fallback.read_bytes().startswith(b"\x00\x00\x01\x00"))
        pages = [
            (ROOT / "index.html", "./favicon.svg"),
            (ROOT / "levels" / "japanese" / "index.html", "../../favicon.svg"),
            (ROOT / "levels" / "english" / "index.html", "../../favicon.svg"),
            (ROOT / "levels" / "english" / "sample.html", "../../favicon.svg"),
        ]
        for level in LEVELS:
            data = load_level(level)
            level_dir = ROOT / "levels" / level
            names = ["index.html", "topics.html", "topic.html"]
            names.extend(f"topic-{topic['id']:02d}.html" for topic in data["topics"])
            pages.extend((level_dir / name, "../../favicon.svg") for name in names)
        for page, href in pages:
            text = page.read_text(encoding="utf-8")
            self.assertIn(f'<link rel="icon" href="{href}" type="image/svg+xml" />', text, str(page))
            fallback_href = href.removesuffix("favicon.svg") + "favicon.ico"
            self.assertIn(f'<link rel="alternate icon" href="{fallback_href}" type="image/x-icon" />', text, str(page))

    def test_removed_topic_url_helper_has_no_calls(self):
        app = (ROOT / "app.js").read_text(encoding="utf-8")
        self.assertNotIn("topicUrl(", app)

    def test_all_audio_and_image_resources_exist(self):
        for level in LEVELS:
            data = load_level(level)
            audio_base = data.get("audioBase") or ("assets/audio" if level == "n3" else f"assets/{level}/audio")
            for story in data["stories"]:
                self.assertTrue((ROOT / audio_base / story["audio"]).is_file())
                self.assertTrue(story["images"])
                for image in story["images"]:
                    self.assertTrue((ROOT / image).is_file())

    def test_portal_and_japanese_gateway_do_not_hardcode_statistics(self):
        portal = (ROOT / "index.html").read_text(encoding="utf-8")
        japanese = (ROOT / "levels" / "japanese" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-page="portal"', portal)
        self.assertIn('data-page="japanese"', japanese)
        for number in ("494", "452", "371", "262", "373", "9116"):
            self.assertNotIn(number, japanese)
        self.assertNotIn("levels/n3/index.html", portal)

    def test_formal_runtime_has_no_prototype_or_development_copy(self):
        text = "\n".join([
            (ROOT / "index.html").read_text(encoding="utf-8"),
            (ROOT / "levels" / "japanese" / "index.html").read_text(encoding="utf-8"),
            (ROOT / "app.js").read_text(encoding="utf-8"),
        ])
        for phrase in ("新版入口原型", "正式改版时", "原型以 N1 展示", "本原型只模拟状态", "GitHub Pages 静态可用"):
            self.assertNotIn(phrase, text)

    def test_state_keys_include_level_and_keep_legacy_keys(self):
        state = (ROOT / "state.js").read_text(encoding="utf-8")
        self.assertIn('`${PREFIX}:${String(level).toLowerCase()}:${name}`', state)
        self.assertIn('`${normalizedLevel}Learned`', state)
        self.assertIn('`${normalizedLevel}Starred`', state)
        self.assertNotIn("removeItem", state)

    def test_lesson_requirements_are_present_without_source_image_ui(self):
        app = (ROOT / "app.js").read_text(encoding="utf-8")
        for marker in (
            "data-audio-element", "data-audio-toggle", "data-section=\"chinese\"",
            "data-section=\"vocab\"", "data-learn-toggle", "data-favorite-toggle",
            "data-story-nav", "beforeunload",
        ):
            self.assertIn(marker, app)
        for marker in (
            "sourceMarkup", "story.images", "imageModalMarkup", "bindImageModal", "modalImage", "data-source-image",
            "data-image-modal", "data-image-close", "data-modal-image", "modalOpen",
            "原书图片", "查看原图",
        ):
            self.assertNotIn(marker, app)

        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        for selector in (
            ".sourceGrid", ".sourcePreview", ".imageModal", ".modalBackdrop",
            ".modalPanel", ".modalClose", ".modalOpen",
        ):
            self.assertNotIn(selector, css)

    def test_mobile_layout_uses_safe_area_without_horizontal_masking(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        self.assertIn("env(safe-area-inset-bottom)", css)
        self.assertIn(".page.hasBottomBar", css)
        self.assertIn("grid-template-columns: repeat(5, minmax(0, 1fr))", css)
        self.assertNotIn("overflow-x: hidden", css)

    def test_builders_preserve_unified_pages(self):
        levels_builder = (ROOT / "tools" / "build_levels.py").read_text(encoding="utf-8")
        n3_builder = (ROOT / "tools" / "build_n3.py").read_text(encoding="utf-8")
        self.assertIn('level_page_html(book, "topic"', levels_builder)
        self.assertIn('page_html("level-home"', n3_builder)
        self.assertIn('LEVEL_DIR / "topic.html"', n3_builder)
        self.assertNotIn('write_file(ROOT / "index.html"', n3_builder)


if __name__ == "__main__":
    unittest.main()
