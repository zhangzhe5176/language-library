#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "n1-data.js"
REPORT_DIR = ROOT / "reports" / "n1-repair"
SEVERITIES = ("阻断发布", "内容错误", "字段异常", "格式问题", "可选优化")
REQUIRED_FIELDS = {
    "id", "topicId", "page", "type", "title", "audio", "images", "japanese",
    "naturalChinese", "originalChinese", "vocab", "vocabRaw", "ocrText", "reviewStatus",
}
ALLOWED_POS = {
    "名", "句", "語句", "感", "副", "接続", "連", "連体", "接頭", "接尾", "イ", "ナ",
    "動1自", "動1他", "動2自", "動2他", "動3自", "動3他",
    "名・副", "名・動3自", "名・動3他", "名・動3自他", "名・ナ",
}
BAD_TEXT_RE = re.compile(r"[�□■◆]")
VIETNAMESE_RE = re.compile(r"[ăâđêôơưĂÂĐÊÔƯƠ]|[ạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]", re.I)


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


def suspicious_chinese(text: str) -> bool:
    if VIETNAMESE_RE.search(text) or BAD_TEXT_RE.search(text):
        return True
    scrubbed = text
    for allowed in ("AI", "SNS", "IT", "WEB", "Web", "APP", "CPU", "N1", "JLPT", "OECD", "YouTube", "OTO Navi", "I’m POSSIBLE"):
        scrubbed = scrubbed.replace(allowed, "")
    scrubbed = re.sub(r"\b[A-Z]\b", "", scrubbed)
    return bool(re.search(r"[A-Za-z]{3,}", scrubbed))


def audit_story(story: dict, root: Path = ROOT) -> list[dict]:
    found: list[dict] = []
    missing = REQUIRED_FIELDS - story.keys()
    if missing:
        found.append(issue("字段异常", "MISSING_FIELDS", f"缺少字段：{', '.join(sorted(missing))}", story))

    if story.get("reviewStatus") != "已校对":
        found.append(issue("阻断发布", "NOT_REVIEWED", "条目尚未完成逐图校对", story, "reviewStatus"))

    japanese = story.get("japanese") or []
    if not japanese:
        found.append(issue("阻断发布", "JAPANESE_EMPTY", "日文为空", story, "japanese"))
    for line in japanese:
        text = str(line.get("text", "")).strip()
        if not text:
            found.append(issue("内容错误", "JAPANESE_LINE_EMPTY", "存在空日文行", story, "japanese"))
        if BAD_TEXT_RE.search(text):
            found.append(issue("内容错误", "JAPANESE_OCR_GLYPH", f"日文含 OCR 异常字符：{text}", story, "japanese"))

    for field in ("naturalChinese", "originalChinese"):
        values = story.get(field) or []
        if not values or not any(str(value).strip() for value in values):
            found.append(issue("阻断发布", f"{field.upper()}_EMPTY", f"{field} 为空", story, field))
        for value in values:
            text = str(value).strip()
            if suspicious_chinese(text):
                found.append(issue("内容错误", "CHINESE_GARBLED", f"中文含乱码、越南语字符或异常英文：{text}", story, field))

    title = str(story.get("title", "")).strip()
    if not title:
        found.append(issue("内容错误", "TITLE_EMPTY", "标题为空", story, "title"))

    vocab = story.get("vocab") or []
    if not vocab:
        found.append(issue("阻断发布", "VOCAB_EMPTY", "结构化词汇为空", story, "vocab"))
    numbers: list[int] = []
    for row_index, row in enumerate(vocab, start=1):
        if not isinstance(row, list) or len(row) != 5:
            found.append(issue("字段异常", "VOCAB_SHAPE", f"第 {row_index} 行不是固定五列", story, "vocab"))
            continue
        number, word, kana, pos, meaning = map(lambda value: str(value).strip(), row)
        if not number.isdigit() or int(number) < 1 or int(number) > 2571:
            found.append(issue("字段异常", "VOCAB_NUMBER_INVALID", f"词汇编号无效：{number}", story, "vocab"))
        else:
            numbers.append(int(number))
        if not word or not meaning:
            found.append(issue("内容错误", "VOCAB_VALUE_EMPTY", f"词汇 {number or row_index} 的单词或释义为空", story, "vocab"))
        if meaning == "待确认" or word.startswith("語彙"):
            found.append(issue("阻断发布", "VOCAB_UNCONFIRMED", f"词汇 {number} 尚未从原图确认", story, "vocab"))
        if kana and not re.fullmatch(r"[ぁ-ゖァ-ヺー・／～（）\s]+", kana):
            found.append(issue("字段异常", "VOCAB_KANA_INVALID", f"假名疑似错误：{kana}", story, "vocab"))
        if story.get("reviewStatus") == "已校对" and pos not in ALLOWED_POS:
            found.append(issue("字段异常", "VOCAB_POS_INVALID", f"词性不符合统一格式：{pos}", story, "vocab"))
        if suspicious_chinese(meaning):
            found.append(issue("内容错误", "VOCAB_MEANING_GARBLED", f"词义异常：{meaning}", story, "vocab"))
        if re.search(r"[；;/／]", meaning):
            found.append(issue("可选优化", "VOCAB_MEANING_MULTIPLE", f"词义含多个释义：{meaning}", story, "vocab"))
    if len(numbers) != len(set(numbers)):
        found.append(issue("字段异常", "VOCAB_NUMBER_DUPLICATE", "条目内词汇编号重复", story, "vocab"))

    audio = root / "assets" / "n1" / "audio" / str(story.get("audio", ""))
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
    if len(stories) != 494:
        issues.append(issue("阻断发布", "STORY_COUNT", f"N1 应为 494 条，实际 {len(stories)} 条"))
    if ids != list(range(1, 495)) or len(ids) != len(set(ids)):
        issues.append(issue("阻断发布", "STORY_IDS", "story id 不连续、乱序或重复"))
    if len(data.get("topics", [])) != 27:
        issues.append(issue("阻断发布", "TOPIC_COUNT", f"N1 应为 27 个 Topic，实际 {len(data.get('topics', []))} 个"))

    all_vocab: list[int] = []
    for story in stories:
        issues.extend(audit_story(story, root))
        for row in story.get("vocab") or []:
            if isinstance(row, list) and row and str(row[0]).isdigit():
                all_vocab.append(int(row[0]))
    if all_vocab != list(range(1, 2572)):
        issues.append(issue("阻断发布", "VOCAB_SEQUENCE", "N1 词汇编号不是 1–2571 连续序列"))

    severity_counts = {name: 0 for name in SEVERITIES}
    severity_counts.update(Counter(item["severity"] for item in issues))
    code_counts = dict(sorted(Counter(item["code"] for item in issues).items()))
    return {
        "level": "n1",
        "story_count": len(stories),
        "topic_count": len(data.get("topics", [])),
        "reviewed_count": sum(story.get("reviewStatus") == "已校对" for story in stories),
        "ocr_organized_count": sum(story.get("reviewStatus") == "OCR已整理" for story in stories),
        "vocab_count": len(all_vocab),
        "issue_count": len(issues),
        "severity_counts": severity_counts,
        "code_counts": code_counts,
        "issues": issues,
    }


def write_reports(result: dict) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "n1-audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# N1 全量内容审计",
        "",
        f"- Topic 数：{result['topic_count']}",
        f"- 故事数：{result['story_count']}",
        f"- 已校对：{result['reviewed_count']}",
        f"- OCR 已整理：{result['ocr_organized_count']}",
        f"- 词汇数：{result['vocab_count']}",
        f"- 问题总数：{result['issue_count']}",
        "",
    ]
    for severity in SEVERITIES:
        selected = [item for item in result["issues"] if item["severity"] == severity]
        lines.extend([f"## {severity}（{result['severity_counts'][severity]}）", ""])
        if not selected:
            lines.append("- 无")
        else:
            for item in selected[:500]:
                where = "全局" if item["story_id"] is None else f"T{item['story_id']} / Topic {item['topic_id']} / p.{item['page']}"
                lines.append(f"- `{item['code']}` {where} `{item['field']}`：{item['message']}")
            if len(selected) > 500:
                lines.append(f"- 其余 {len(selected) - 500} 项见 JSON 报告。")
        lines.append("")
    (REPORT_DIR / "n1-audit.md").write_text("\n".join(lines), encoding="utf-8")
    summary = [
        "# N1 审计摘要",
        "",
        f"- N1 Topic：{result['topic_count']}（要求 27）",
        f"- N1 总条数：{result['story_count']}（要求 494）",
        f"- 已校对条数：{result['reviewed_count']}",
        f"- OCR 已整理条数：{result['ocr_organized_count']}",
        f"- 词汇条数：{result['vocab_count']}（要求 2571）",
        f"- 检出问题：{result['issue_count']}",
        "",
    ]
    summary.extend(f"- {severity}：{result['severity_counts'][severity]}" for severity in SEVERITIES)
    summary.extend(["", "## 结论", "", "- 当前 N1 已完成 EPUB 图片抽取、音频整理和 OCR 结构化初稿。", "- 仍需逐条对照原始图片校对后，才能将条目标记为“已校对”。", ""])
    (REPORT_DIR / "summary.md").write_text("\n".join(summary), encoding="utf-8")

    with (REPORT_DIR / "fix-log.csv").open("w", newline="", encoding="utf-8") as output:
        writer = csv.writer(output)
        writer.writerow(["level", "scope", "field", "before", "after", "source", "note"])
        writer.writerow(["N1", "source", "epub", "", "图片型 EPUB，按 spine 提取原始图片", "EPUB content.opf / spine", "自动来源检查"])
        writer.writerow(["N1", "source", "audio", "", "T1.mp3–T494.mp3", "官方音频包 Best_Vocab_N1.zip", "自动音频整理"])
        writer.writerow(["N1", "data", "stories", "", str(result["story_count"]), "data/n1-data.js", "OCR 结构化初稿"])
        writer.writerow(["N1", "data", "vocab", "", str(result["vocab_count"]), "data/n1-data.js", "主编号词汇序列"])
        writer.writerow(["N1", "review", "reviewStatus", "OCR已整理", "已校对", "原始图片逐条校对", f"未完成：{result['ocr_organized_count']} 条仍需人工级校对"])

    final_lines = [
        "# N1 最终验收报告",
        "",
        "## 当前结论",
        "",
    ]
    if result["severity_counts"]["阻断发布"] == 0:
        final_lines.append("- N1 已通过当前审计工具的全部阻断检查。")
    else:
        final_lines.append("- N1 尚未达到最终发布条件；存在阻断发布问题。")
    final_lines.extend([
        "",
        "## 统计",
        "",
        f"- Topic 总数：{result['topic_count']}",
        f"- 故事总数：{result['story_count']}",
        f"- 词汇总数：{result['vocab_count']}",
        f"- 已校对数量：{result['reviewed_count']}",
        f"- 未校对数量：{result['ocr_organized_count']}",
        f"- 问题总数：{result['issue_count']}",
        "",
        "## 严重级别",
        "",
    ])
    final_lines.extend(f"- {severity}：{result['severity_counts'][severity]}" for severity in SEVERITIES)
    final_lines.extend([
        "",
        "## 资源状态",
        "",
        "- EPUB 原始图片已按 spine 顺序提取到 `assets/n1/pages/`。",
        "- 官方音频已整理到 `assets/n1/audio/`。",
        "",
        "## 未完成事项",
        "",
        "- 494 条内容仍为 `OCR已整理`，不能等同于逐图校对完成。",
        "- 需要逐条对照 EPUB 原始图片修正日文、中文、词汇、假名、词性和释义后，再将 `reviewStatus` 标记为 `已校对`。",
        "",
    ])
    (REPORT_DIR / "final-report.md").write_text("\n".join(final_lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="审计 N1 全部内容数据")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    result = audit_data(load_data())
    if not args.no_write:
        write_reports(result)
    print(json.dumps({key: result[key] for key in ("story_count", "topic_count", "reviewed_count", "ocr_organized_count", "vocab_count", "issue_count", "severity_counts")}, ensure_ascii=False))
    return 1 if result["severity_counts"]["阻断发布"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
