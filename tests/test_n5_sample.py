import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_level_data(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(r"window\.LEVEL_DATA\s*=\s*(\{.*\});\s*", text, re.DOTALL)
    if not match:
        raise AssertionError(f"unexpected data wrapper: {path}")
    return json.loads(match.group(1))


class N5SampleTests(unittest.TestCase):
    REQUIRED_STORY_FIELDS = {
        "id", "topicId", "page", "type", "audio", "images", "japanese",
        "naturalChinese", "originalChinese", "vocab", "reviewStatus",
    }

    def assert_level_is_complete(self, level, topic_count, track_count):
        data = load_level_data(ROOT / "data" / f"{level}-data.js")
        self.assertEqual(len(data["topics"]), topic_count)
        self.assertEqual(len(data["stories"]), track_count)
        self.assertEqual([story["id"] for story in data["stories"]], list(range(1, track_count + 1)))
        self.assertEqual(
            {story["topicId"] for story in data["stories"]},
            set(range(1, topic_count + 1)),
        )
        for story in data["stories"]:
            self.assertTrue(self.REQUIRED_STORY_FIELDS <= story.keys())
            self.assertTrue((ROOT / data["audioBase"] / story["audio"]).is_file())
            self.assertTrue(story["images"])
            for image in story["images"]:
                self.assertTrue((ROOT / image).is_file())
        return data

    def test_n5_contains_all_tracks_and_topics(self):
        data = self.assert_level_is_complete("n5", 24, 373)
        self.assertEqual(data["level"], "n5")
        self.assertEqual(data["topics"][0]["title"], "あいさつ1")
        self.assertTrue(all(story["reviewStatus"] == "已校对" for story in data["stories"][:8]))

    def test_reviewed_sample_covers_vocab_one_through_thirteen(self):
        data = load_level_data(ROOT / "data" / "n5-data.js")
        vocab_numbers = [int(row[0]) for story in data["stories"][:8] for row in story["vocab"]]
        self.assertEqual(vocab_numbers, list(range(1, 14)))

    def test_topic_one_assets_exist(self):
        data = load_level_data(ROOT / "data" / "n5-data.js")
        for story in data["stories"]:
            self.assertTrue((ROOT / data["audioBase"] / story["audio"]).is_file())
            for image in story["images"]:
                self.assertTrue((ROOT / image).is_file())

    def test_n5_pages_load_generic_data_and_app(self):
        for relative_path in [
            "levels/n5/index.html",
            "levels/n5/topics.html",
            "levels/n5/topic.html",
            "levels/n5/topic-01.html",
        ]:
            text = (ROOT / relative_path).read_text(encoding="utf-8")
            self.assertIn('data-level="n5"', text)
            self.assertIn("../../data/n5-data.js", text)
            self.assertIn("../../state.js", text)
            self.assertIn("../../app.js", text)
            self.assertIn('rel="icon" href="data:,"', text)

    def test_n4_contains_all_tracks_and_topics(self):
        data = self.assert_level_is_complete("n4", 13, 262)
        self.assertEqual(data["level"], "n4")
        for relative_path in ["levels/n4/index.html", "levels/n4/topics.html", "levels/n4/topic-13.html"]:
            self.assertTrue((ROOT / relative_path).is_file())

    def test_n2_contains_all_tracks_and_topics(self):
        data = self.assert_level_is_complete("n2", 23, 452)
        self.assertEqual(data["level"], "n2")
        self.assertEqual(data["topics"][0]["title"], "食事")
        self.assertEqual(data["topics"][-1]["title"], "環境・科学")
        self.assertEqual(data["numberedWordCount"], 2360)
        for relative_path in ["levels/n2/index.html", "levels/n2/topics.html", "levels/n2/topic-23.html"]:
            self.assertTrue((ROOT / relative_path).is_file())

    def test_n1_contains_all_tracks_and_topics(self):
        data = self.assert_level_is_complete("n1", 27, 494)
        self.assertEqual(data["level"], "n1")
        self.assertEqual(data["topics"][0]["title"], "食事")
        self.assertEqual(data["topics"][-1]["title"], "科学")
        self.assertEqual(data["numberedWordCount"], 2571)
        vocab_numbers = [int(row[0]) for story in data["stories"] for row in story["vocab"]]
        self.assertEqual(vocab_numbers, list(range(1, 2572)))
        for relative_path in ["levels/n1/index.html", "levels/n1/topics.html", "levels/n1/topic-27.html"]:
            self.assertTrue((ROOT / relative_path).is_file())

    def test_portal_only_links_to_japanese_gateway(self):
        text = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-page="portal"', text)
        self.assertNotIn("./levels/n3/index.html", text)
        self.assertNotIn("./levels/n5/index.html", text)
        self.assertIn("./app.js", text)

    def test_app_uses_level_specific_paths_and_storage(self):
        text = (ROOT / "app.js").read_text(encoding="utf-8")
        state_text = (ROOT / "state.js").read_text(encoding="utf-8")
        self.assertIn("document.body.dataset.level", text)
        self.assertIn('levelUrl(level, "topic.html")', text)
        self.assertIn('`${PREFIX}:${String(level).toLowerCase()}:${name}`', state_text)
        self.assertIn('`${normalizedLevel}Learned`', state_text)
        self.assertIn('`${normalizedLevel}Starred`', state_text)

    def test_final_tablet_media_rule_collapses_study_layout(self):
        text = (ROOT / "styles.css").read_text(encoding="utf-8")
        tablet_rule = text.rsplit("@media (max-width: 1040px)", 1)[1]
        self.assertRegex(tablet_rule, r"\.lessonLayout\s*\{\s*grid-template-columns:\s*1fr;")

    def test_theme_has_one_editable_token_block(self):
        text = (ROOT / "styles.css").read_text(encoding="utf-8")
        self.assertEqual(text.count(":root {"), 2)
        self.assertIn("@media (prefers-color-scheme: dark)", text)
        self.assertIn("--font-sans:", text)


if __name__ == "__main__":
    unittest.main()
