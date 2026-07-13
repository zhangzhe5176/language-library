import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_levels", ROOT / "tools" / "build_levels.py")
build_levels = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = build_levels
SPEC.loader.exec_module(build_levels)


class LevelBuilderConfigTests(unittest.TestCase):
    def test_n2_book_contract(self):
        config = build_levels.BOOKS["n2"]
        self.assertEqual(config.track_count, 452)
        self.assertEqual(config.word_count, 2400)
        self.assertEqual(config.numbered_word_count, 2360)
        self.assertEqual(len(config.topics), 23)
        self.assertEqual(config.topics[0].title, "食事")
        self.assertEqual(config.topics[-1].title, "環境・科学")
        self.assertEqual(set(config.marker_overrides), {1, 12, 17, 28, 98, 413})

    def test_n5_book_contract(self):
        config = build_levels.BOOKS["n5"]
        self.assertEqual(config.track_count, 373)
        self.assertEqual(config.word_count, 1000)
        self.assertEqual(len(config.topics), 24)
        self.assertEqual(config.topics[0].title, "あいさつ1")
        self.assertEqual(config.topics[-1].title, "クラス")
        self.assertEqual(set(config.marker_overrides), {1, 5, 32, 73, 184, 185})

    def test_n4_book_contract(self):
        config = build_levels.BOOKS["n4"]
        self.assertEqual(config.track_count, 262)
        self.assertEqual(config.word_count, 1200)
        self.assertEqual(len(config.topics), 13)
        self.assertEqual(config.topics[0].title, "家・寮")
        self.assertEqual(config.topics[-1].title, "職場")
        self.assertEqual(config.marker_overrides, {189: (141, 583)})

    def test_topic_pages_are_strictly_increasing(self):
        for config in build_levels.BOOKS.values():
            pages = [topic.page for topic in config.topics]
            self.assertEqual(pages, sorted(set(pages)))

    def test_audio_members_accept_zero_padded_track_names(self):
        members = build_levels.audio_member_map(["folder/T01.mp3", "folder/T10.mp3"])
        self.assertEqual(members, {1: "folder/T01.mp3", 10: "folder/T10.mp3"})


if __name__ == "__main__":
    unittest.main()
