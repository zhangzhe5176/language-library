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
    def test_topic_one_contains_eight_checked_dialogues(self):
        data = load_level_data(ROOT / "data" / "n5-data.js")
        self.assertEqual(data["level"], "n5")
        self.assertEqual(len(data["topics"]), 1)
        self.assertEqual(data["topics"][0]["title"], "あいさつ1")
        self.assertEqual(len(data["stories"]), 8)
        self.assertTrue(all(story["reviewStatus"] == "已校对" for story in data["stories"]))

    def test_topic_one_covers_vocab_one_through_thirteen(self):
        data = load_level_data(ROOT / "data" / "n5-data.js")
        vocab_numbers = [int(row[0]) for story in data["stories"] for row in story["vocab"]]
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
            "levels/n5/topic-01.html",
        ]:
            text = (ROOT / relative_path).read_text(encoding="utf-8")
            self.assertIn('data-level="n5"', text)
            self.assertIn("../../data/n5-data.js", text)
            self.assertIn("../../app.js", text)
            self.assertIn('rel="icon" href="data:,"', text)

    def test_portal_links_to_n5(self):
        text = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn("./levels/n5/index.html", text)

    def test_app_uses_level_specific_paths_and_storage(self):
        text = (ROOT / "app.js").read_text(encoding="utf-8")
        self.assertIn('document.body.dataset.level || "n3"', text)
        self.assertIn('`${level}Learned`', text)
        self.assertIn('`${basePath}/levels/${level}/topic-', text)

    def test_final_tablet_media_rule_collapses_study_layout(self):
        text = (ROOT / "styles.css").read_text(encoding="utf-8")
        final_tablet_rule = text.rsplit("@media (max-width: 980px)", 1)[1]
        self.assertIn(".studyShell { grid-template-columns: 1fr; }", final_tablet_rule)


if __name__ == "__main__":
    unittest.main()
