from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def dialogue(*lines: tuple[str, str]) -> list[dict]:
    return [{"speaker": speaker, "text": text} for speaker, text in lines]


def compact(value) -> str:
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


def apply_topic_patch(*, level: str, topic_id: int, patches: dict[int, dict], source: str, reviewed_at: str) -> int:
    data_path = ROOT / "data" / f"{level}-data.js"
    log_path = ROOT / "reports" / f"{level}-repair" / "fix-log.csv"
    text = data_path.read_text(encoding="utf-8")
    prefix, raw = text.split("=", 1)
    data = json.loads(raw.strip().rstrip(";"))
    by_id = {story["id"]: story for story in data["stories"]}
    rows = []
    for story_id, patch in patches.items():
        story = by_id[story_id]
        if story["topicId"] != topic_id:
            raise SystemExit(f"{level.upper()} T{story_id} 不属于 Topic {topic_id}")
        if not story.get("vocabRaw") or not story.get("ocrText"):
            raise SystemExit(f"{level.upper()} T{story_id} 缺少 OCR 追溯字段")
        completed = dict(patch)
        completed["reviewStatus"] = "已校对"
        for field, after in completed.items():
            before = story.get(field)
            if before == after:
                continue
            rows.append([
                level, story_id, story["topicId"], story["page"], field,
                compact(before), compact(after), "对照原书修正并统一为已确认字段风格",
                source, reviewed_at,
            ])
            story[field] = after
    data_path.write_text(prefix + "= " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    if rows:
        with log_path.open("a", encoding="utf-8", newline="") as handle:
            csv.writer(handle, lineterminator="\n").writerows(rows)
    return len(rows)
