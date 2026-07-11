import copy
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("audit_n5_data", ROOT / "tools" / "audit_n5_data.py")
audit = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = audit
SPEC.loader.exec_module(audit)


class N5AuditTests(unittest.TestCase):
    def test_real_data_has_373_continuous_stories(self):
        result = audit.audit_data(audit.load_data())
        self.assertEqual(result["story_count"], 373)
        self.assertNotIn("STORY_COUNT", result["code_counts"])
        self.assertNotIn("STORY_IDS", result["code_counts"])

    def test_auditor_detects_mandatory_reviewed_errors(self):
        data = audit.load_data()
        broken = copy.deepcopy(data)
        story = broken["stories"][0]
        story["japanese"] = []
        story["vocab"] = [["x", "word", "bad-reading", "Phr", "释义/第二义"]]
        result = audit.audit_data(broken)
        self.assertIn("JAPANESE_EMPTY", result["code_counts"])
        self.assertIn("VOCAB_NUMBER_INVALID", result["code_counts"])
        self.assertIn("VOCAB_POS_INVALID", result["code_counts"])
        self.assertIn("REVIEWED_FORCE_ERROR", result["code_counts"])

    def test_auditor_detects_topic_mismatch(self):
        data = audit.load_data()
        broken = copy.deepcopy(data)
        broken["stories"][0]["topicId"] = 2
        result = audit.audit_data(broken)
        self.assertIn("TOPIC_ID_MISMATCH", result["code_counts"])

    def test_reviewed_topic_one_passes_all_mandatory_checks(self):
        data = audit.load_data()
        result = audit.audit_data(data)
        topic_one_ids = {story["id"] for story in data["stories"] if story["topicId"] == 1}
        errors = [
            item for item in result["issues"]
            if item["story_id"] in topic_one_ids and item["severity"] != "可选优化"
        ]
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
