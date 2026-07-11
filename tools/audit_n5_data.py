#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "n5-data.js"
REPORT_DIR = ROOT / "reports" / "n5-repair"
SEVERITIES = ("阻断发布", "内容错误", "字段异常", "格式问题", "可选优化")
REQUIRED_FIELDS = {
    "id", "topicId", "page", "type", "title", "audio", "images", "japanese",
    "naturalChinese", "originalChinese", "vocab", "reviewStatus",
}
ALLOWED_POS = {
    "名", "句", "語句", "感", "副", "接続", "連体", "接頭", "接尾", "イ", "ナ",
    "動1自", "動1他", "動2自", "動2他", "動3自", "動3他",
    "名・副", "名・動3自", "名・動3他", "名・動3自他", "名・ナ",
}
VIETNAMESE_RE = re.compile(r"[ăâđêôơưĂÂĐÊÔƠƯ]|[ạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]", re.I)
BAD_TEXT_RE = re.compile(r"[�□■◆]")
SPEAKERS = {"A", "B", "C", "D"}


def load_data(path: Path = DATA) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(r"window\.LEVEL_DATA\s*=\s*(\{.*\});\s*", text, re.DOTALL)
    if not match:
        raise ValueError(f"无法识别数据包装格式：{path}")
    return json.loads(match.group(1))


def issue(severity: str, code: str, message: str, story: dict | None = None, field: str = "") -> dict:
    return {
        "severity": severity,
        "code": code,
        "story_id": story.get("id") if story else None,
        "topic_id": story.get("topicId") if story else None,
        "page": story.get("page") if story else None,
        "field": field,
        "message": message,
    }


def has_chinese_sentence_in_japanese(text: str) -> bool:
    simplified_markers = "这还请没为说见吗们个后时会里让从对与过着"
    return not re.search(r"[ぁ-ゖァ-ヺ]", text) and sum(char in simplified_markers for char in text) >= 2


def suspicious_chinese(text: str) -> bool:
    if VIETNAMESE_RE.search(text) or "�" in text:
        return True
    scrubbed = text.replace("Anne", "").replace("Kento", "")
    return bool(re.search(r"[A-Za-z]{3,}", scrubbed))


def audit_story(story: dict, root: Path = ROOT, audio_base: str = "assets/n5/audio") -> list[dict]:
    found: list[dict] = []
    missing = REQUIRED_FIELDS - story.keys()
    if missing:
        found.append(issue("字段异常", "MISSING_FIELDS", f"缺少字段：{', '.join(sorted(missing))}", story))

    japanese = story.get("japanese") or []
    if not japanese:
        found.append(issue("阻断发布", "JAPANESE_EMPTY", "日文为空", story, "japanese"))
    speakers = []
    for line in japanese:
        text = str(line.get("text", "")).strip()
        speaker = line.get("speaker", "")
        if not text:
            found.append(issue("内容错误", "JAPANESE_LINE_EMPTY", "存在空日文行", story, "japanese"))
        if speaker not in SPEAKERS | {""}:
            found.append(issue("字段异常", "SPEAKER_INVALID", f"人物标记无效：{speaker}", story, "japanese"))
        if speaker:
            speakers.append(speaker)
        if BAD_TEXT_RE.search(text):
            found.append(issue("内容错误", "JAPANESE_OCR_GLYPH", f"日文含 OCR 异常字符：{text}", story, "japanese"))
        if VIETNAMESE_RE.search(text):
            found.append(issue("内容错误", "JAPANESE_VIETNAMESE", "日文混入越南语字符", story, "japanese"))
        if has_chinese_sentence_in_japanese(text):
            found.append(issue("内容错误", "JAPANESE_HAS_CHINESE", f"日文区域疑似混入中文：{text}", story, "japanese"))
        if "\n" in text or re.search(r"\s{2,}", text):
            found.append(issue("格式问题", "JAPANESE_SPLIT", "日文存在异常拆行或连续空格", story, "japanese"))
    if story.get("type") == "dialogue" and (len(speakers) < 2 or any(not line.get("speaker") for line in japanese)):
        found.append(issue("字段异常", "DIALOGUE_SPEAKERS_INCOMPLETE", "对话人物标记不完整", story, "japanese"))

    for field in ("naturalChinese", "originalChinese"):
        values = story.get(field) or []
        if not values or not any(str(value).strip() for value in values):
            found.append(issue("阻断发布", f"{field.upper()}_EMPTY", f"{field} 为空", story, field))
        for value in values:
            text = str(value).strip()
            if suspicious_chinese(text):
                found.append(issue("内容错误", "CHINESE_GARBLED", f"中文含乱码、越南语字符或异常英文：{text}", story, field))
            if "/" in text:
                found.append(issue("内容错误", "CHINESE_LANGUAGES_GLUED", "中文疑似与其他语言粘连", story, field))

    title = str(story.get("title", "")).strip()
    if not title or re.search(r"[ぁ-ゖァ-ヺ]", title) or not re.search(r"[\u3400-\u9fff]", title):
        found.append(issue("内容错误", "TITLE_INVALID", f"标题不是完整中文场景标题：{title}", story, "title"))

    vocab = story.get("vocab") or []
    if not vocab:
        found.append(issue("阻断发布", "VOCAB_EMPTY", "结构化词汇为空", story, "vocab"))
    numbers: list[int] = []
    for row_index, row in enumerate(vocab, start=1):
        if not isinstance(row, list) or len(row) != 5:
            found.append(issue("字段异常", "VOCAB_SHAPE", f"第 {row_index} 行不是固定五列", story, "vocab"))
            continue
        number, word, kana, pos, meaning = map(lambda value: str(value).strip(), row)
        if not number.isdigit() or int(number) < 1 or int(number) > 1010:
            found.append(issue("字段异常", "VOCAB_NUMBER_INVALID", f"词汇编号无效：{number}", story, "vocab"))
        else:
            numbers.append(int(number))
        if not word or not meaning:
            found.append(issue("内容错误", "VOCAB_VALUE_EMPTY", f"词汇 {number or row_index} 的单词或释义为空", story, "vocab"))
        if kana and not re.fullmatch(r"[ぁ-ゖー・／～\s]+", kana):
            found.append(issue("字段异常", "VOCAB_KANA_INVALID", f"假名疑似错误：{kana}", story, "vocab"))
        if pos not in ALLOWED_POS or re.search(r"[A-Za-z]", pos):
            found.append(issue("字段异常", "VOCAB_POS_INVALID", f"词性不符合 N3 中文缩写风格：{pos}", story, "vocab"))
        if suspicious_chinese(meaning):
            found.append(issue("内容错误", "VOCAB_MEANING_GARBLED", f"词义异常：{meaning}", story, "vocab"))
        if re.search(r"[；;/／]", meaning):
            found.append(issue("可选优化", "VOCAB_MEANING_MULTIPLE", f"词义含多个释义：{meaning}", story, "vocab"))
    if len(numbers) != len(set(numbers)):
        found.append(issue("字段异常", "VOCAB_NUMBER_DUPLICATE", "条目内词汇编号重复", story, "vocab"))

    audio = root / audio_base / str(story.get("audio", ""))
    if not audio.is_file():
        found.append(issue("阻断发布", "AUDIO_MISSING", f"音频不存在：{audio.relative_to(root)}", story, "audio"))
    images = story.get("images") or []
    if not images:
        found.append(issue("阻断发布", "IMAGE_MISSING", "未关联原图", story, "images"))
    for image_path in images:
        if not (root / image_path).is_file():
            found.append(issue("阻断发布", "IMAGE_MISSING", f"原图不存在：{image_path}", story, "images"))
    return found


def audit_data(data: dict, root: Path = ROOT) -> dict:
    stories = data.get("stories", [])
    issues: list[dict] = []
    ids = [story.get("id") for story in stories]
    if len(stories) != 373:
        issues.append(issue("阻断发布", "STORY_COUNT", f"N5 应为 373 条，实际 {len(stories)} 条"))
    if ids != list(range(1, 374)) or len(ids) != len(set(ids)):
        issues.append(issue("阻断发布", "STORY_IDS", "story id 不连续、乱序或重复"))
    topic_ids = [story.get("topicId") for story in stories]
    if any(not isinstance(value, int) or not 1 <= value <= 24 for value in topic_ids):
        issues.append(issue("阻断发布", "TOPIC_ID_INVALID", "存在超出 1–24 的 topicId"))
    if topic_ids != sorted(topic_ids):
        issues.append(issue("字段异常", "TOPIC_ORDER", "topicId 顺序异常"))

    topics = sorted(data.get("topics", []), key=lambda item: item["id"])
    for story in stories:
        eligible = [topic["id"] for topic in topics if topic["page"] <= story.get("page", -1)]
        expected_topic = eligible[-1] if eligible else None
        if expected_topic is not None and story.get("topicId") != expected_topic:
            issues.append(issue("字段异常", "TOPIC_ID_MISMATCH", f"按原书页码应属于 Topic {expected_topic}", story, "topicId"))

    for story in stories:
        story_issues = audit_story(story, root, data.get("audioBase", "assets/n5/audio"))
        issues.extend(story_issues)
        if story.get("reviewStatus") == "已校对":
            mandatory = [item for item in story_issues if item["severity"] != "可选优化"]
            if mandatory:
                issues.append(issue("阻断发布", "REVIEWED_FORCE_ERROR", f"已校对条目仍有 {len(mandatory)} 个强制错误", story, "reviewStatus"))

    severity_counts = {name: 0 for name in SEVERITIES}
    severity_counts.update(Counter(item["severity"] for item in issues))
    code_counts = dict(sorted(Counter(item["code"] for item in issues).items()))
    return {
        "level": "n5",
        "story_count": len(stories),
        "reviewed_count": sum(story.get("reviewStatus") == "已校对" for story in stories),
        "issue_count": len(issues),
        "severity_counts": severity_counts,
        "code_counts": code_counts,
        "issues": issues,
    }


def write_reports(result: dict) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "n5-audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# N5 全量内容审计", "", f"- 故事数：{result['story_count']}", f"- 已校对：{result['reviewed_count']}", f"- 问题总数：{result['issue_count']}", ""]
    for severity in SEVERITIES:
        lines.extend([f"## {severity}（{result['severity_counts'][severity]}）", ""])
        selected = [item for item in result["issues"] if item["severity"] == severity]
        if not selected:
            lines.append("- 无")
        else:
            for item in selected:
                where = "全局" if item["story_id"] is None else f"T{item['story_id']} / Topic {item['topic_id']} / p.{item['page']}"
                lines.append(f"- `{item['code']}` {where} `{item['field']}`：{item['message']}")
        lines.append("")
    (REPORT_DIR / "n5-audit.md").write_text("\n".join(lines), encoding="utf-8")

    summary = ["# N5 审计摘要", "", f"- N5 总条数：{result['story_count']}（要求 373）", f"- 已校对条数：{result['reviewed_count']}", f"- 检出问题：{result['issue_count']}", ""]
    summary.extend(f"- {severity}：{result['severity_counts'][severity]}" for severity in SEVERITIES)
    summary.extend(["", "## 结论", "", "- 只有不存在 `REVIEWED_FORCE_ERROR` 的条目才允许保留“已校对”状态。", "- 尚未校对条目的 OCR 问题继续保留在报告中，后续按 Topic 修复。", ""])
    (REPORT_DIR / "summary.md").write_text("\n".join(summary), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="审计 N5 全部 373 条内容数据")
    parser.add_argument("--no-write", action="store_true", help="只检查，不写报告")
    args = parser.parse_args()
    result = audit_data(load_data())
    if not args.no_write:
        write_reports(result)
    print(json.dumps({key: result[key] for key in ("story_count", "reviewed_count", "issue_count", "severity_counts")}, ensure_ascii=False))
    return 1 if result["code_counts"].get("REVIEWED_FORCE_ERROR", 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
