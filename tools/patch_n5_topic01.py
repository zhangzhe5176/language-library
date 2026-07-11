#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "n5-data.js"
LOG = ROOT / "reports" / "n5-repair" / "fix-log.csv"
REVIEWED_AT = "2026-07-11T00:00:00+09:00"
SOURCE = "N5 PDF pages 18-20 (printed pages 16-18)"


def d(speaker: str, text: str) -> dict:
    return {"speaker": speaker, "text": text}


OCR_ARCHIVE = {
    1: ["A：はじめまして。アンです。", "B：あ、けんとです。はじめまして。", "はじめまして", "Phr, nice to meet you （meeting for the first time）/初次面 / xin chao （danh cho lan", "dau gap mat）", "A： Nice to meet you. Im Anne. B： Oh， Im Kento. Nice to meet you， too. / A：初次面、我", "是Anne。B：啊，我是Kento。初次面。/A:Xin chao. Minh la An. B： A， to la Kento. Xin"],
    2: ["192", "A：よろしくおねがいします。", "B：こちらこそ、どうぞよろしくおねがいします。", "よろしくおねがいします", "glad to meet you / 清多照/Rat vui duioc gap ban", "Phr.", "こちらこそ", "Phr.", "same here / 哪里哪里（我オ～）/Toi， Minh cing vay", "A： Glad to meet youl. B： Oh， same here. Glad to meet you. / A： 清多照。B：哪里哪里、清", "多照。/A： Rat vui dugc gap ban. B： To ciing vay. Rat vui duigc gap ban."],
    3: ["4） 3", "A： おはようございます。", "B：アンさん。おはようございます。", "おはようございます", "4", "Intio", "good morning / 早上好 / Xin chao, Chao （budi sang）", "～さん", "5", "Suf.", "~san （honorific title）/〜小姐、先生/anh， chi， ban,co， chi， bac， Ong,ba~", "16"],
    4: ["4）4", "A：こんにちは。", "B：こんにちは。", "こんにちは", "6", "hello / 午安（在白天河候吋也可以用好）/Xin chao， chao （buoitruia）", "A： Hello. B： Hello. / A： 好。B：你好。/A:Chao ban. B： Chao ban."],
    5: ["A：こんばんは。", "B：こんばんは。", "こんばんは", "good evening / 晚上好/ Xin chao, chao （buoitoi）", "A： Good evening. B： Good evening/A： 晩上好。B：晩上好。/A： Em chao co. B： Chao em."],
    6: ["ッ", "6", "A： じや、また。", "B：また明日。", "あした", "じゃ、また", "8", "Phr. see you/那，再ア / Vay hen gap lai", "またあしたまた明日", "Phr, see you tomorrow / 明天児/ Gap lai vao ngay mai nhe", "A： See you. B： See you tomorrow. / A： 那再了。B：明天。/A： Vay hen gip lai B： Gap", "lai vao ngay mai nhe.", "17"],
    7: ["497", "A：じゃ、また。", "B：はい。おやすみなさい。", "はい", "10", "Intj", "yeah, yes/ 好的/vang, da, ii", "おやすみなさい", "good night /晩安 / Chiic ngi ngon", "Phr.", "A： See you. B： Yeah. Good night. / A： 那，再了。B：好的。晩安。/A： Hen gip lai. B： U，", "ngi ngon nhe."],
    8: ["④））8", "A：しつれいします。", "B：さようなら。", "しつれいします↓", "12", "Phr.", "T'm heading home/ 告辞了/Toixin phep （lam viec gido truidc ai）", "さようなら", "13", "Intij. goodbye/再/ Tam biet", "A:I'm heading home. B： Goodbye. / A： 告了。B：再。/A： Minh ve truidc nhe. B： Tam", "biet.", "18"],
}


PATCHES = {
    1: {
        "title": "初次见面问候",
        "type": "dialogue",
        "japanese": [d("A", "はじめまして。アンです。"), d("B", "あ、けんとです。はじめまして。")],
        "focus": ["はじめまして"],
        "naturalChinese": ["A：初次见面，我叫安。", "B：啊，我叫健人。初次见面。"],
        "originalChinese": ["A：初次见面，我是Anne。", "B：啊，我是Kento。初次见面。"],
        "vocab": [["1", "はじめまして", "", "句", "初次见面"]],
    },
    2: {
        "title": "互相请多关照",
        "type": "dialogue",
        "japanese": [d("A", "よろしくおねがいします。"), d("B", "こちらこそ、どうぞよろしくおねがいします。")],
        "focus": ["よろしくおねがいします", "こちらこそ"],
        "naturalChinese": ["A：请多关照。", "B：我才要请你多多关照。"],
        "originalChinese": ["A：请多关照。", "B：哪里哪里，请你多关照。"],
        "vocab": [["2", "よろしくおねがいします", "", "句", "请多关照"], ["3", "こちらこそ", "", "句", "我才要请你多关照"]],
    },
    3: {
        "title": "早晨见面问候",
        "type": "dialogue",
        "japanese": [d("A", "おはようございます。"), d("B", "アンさん。おはようございます。")],
        "focus": ["おはようございます", "～さん"],
        "naturalChinese": ["A：早上好。", "B：安小姐，早上好。"],
        "originalChinese": ["A：早上好。", "B：Anne小姐，早上好。"],
        "vocab": [["4", "おはようございます", "", "感", "早上好"], ["5", "～さん", "", "接尾", "礼貌称呼"]],
    },
    4: {
        "title": "白天见面问候",
        "type": "dialogue",
        "japanese": [d("A", "こんにちは。"), d("B", "こんにちは。")],
        "focus": ["こんにちは"],
        "naturalChinese": ["A：你好。", "B：你好。"],
        "originalChinese": ["A：你好。", "B：你好。"],
        "vocab": [["6", "こんにちは", "", "感", "你好"]],
    },
    5: {
        "title": "晚上见面问候",
        "type": "dialogue",
        "japanese": [d("A", "こんばんは。"), d("B", "こんばんは。")],
        "focus": ["こんばんは"],
        "naturalChinese": ["A：晚上好。", "B：晚上好。"],
        "originalChinese": ["A：晚上好。", "B：晚上好。"],
        "vocab": [["7", "こんばんは", "", "感", "晚上好"]],
    },
    6: {
        "title": "约好明天再见",
        "type": "dialogue",
        "japanese": [d("A", "じゃ、また。"), d("B", "また明日。")],
        "focus": ["じゃ、また", "また明日"],
        "naturalChinese": ["A：那，再见。", "B：明天见。"],
        "originalChinese": ["A：那再见了。", "B：明天见。"],
        "vocab": [["8", "じゃ、また", "", "句", "再见"], ["9", "また明日", "またあした", "句", "明天见"]],
    },
    7: {
        "title": "道别时说晚安",
        "type": "dialogue",
        "japanese": [d("A", "じゃ、また。"), d("B", "はい。おやすみなさい。")],
        "focus": ["はい", "おやすみなさい"],
        "naturalChinese": ["A：那，再见。", "B：好的，晚安。"],
        "originalChinese": ["A：那，再见了。", "B：好的。晚安。"],
        "vocab": [["10", "はい", "", "感", "好的"], ["11", "おやすみなさい", "", "句", "晚安"]],
    },
    8: {
        "title": "离开时告辞",
        "type": "dialogue",
        "japanese": [d("A", "しつれいします。"), d("B", "さようなら。")],
        "focus": ["しつれいします", "さようなら"],
        "naturalChinese": ["A：我先告辞了。", "B：再见。"],
        "originalChinese": ["A：告辞了。", "B：再见。"],
        "vocab": [["12", "しつれいします①", "", "句", "告辞"], ["13", "さようなら", "", "感", "再见"]],
    },
}


def compact(value) -> str:
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


def main() -> None:
    text = DATA.read_text(encoding="utf-8")
    prefix, raw = text.split("=", 1)
    data = json.loads(raw.strip().rstrip(";"))
    by_id = {story["id"]: story for story in data["stories"]}
    log_rows = []
    for story_id, patch in PATCHES.items():
        story = by_id[story_id]
        if story["topicId"] != 1:
            raise SystemExit(f"T{story_id} 不属于 Topic 1")
        patch = dict(patch)
        patch["vocabRaw"] = OCR_ARCHIVE[story_id]
        patch["ocrText"] = "\n".join(OCR_ARCHIVE[story_id])
        patch["reviewStatus"] = "已校对"
        for field, after in patch.items():
            before = story.get(field)
            if before == after:
                continue
            log_rows.append([
                "n5", story_id, story["topicId"], story["page"], field,
                compact(before), compact(after), "对照原书修正并统一为 N3 字段风格",
                SOURCE, REVIEWED_AT,
            ])
            story[field] = after

    expected_numbers = [str(number) for number in range(1, 14)]
    actual_numbers = [row[0] for story_id in PATCHES for row in by_id[story_id]["vocab"]]
    if actual_numbers != expected_numbers:
        raise SystemExit(f"Topic 1 词汇编号异常：{actual_numbers}")

    DATA.write_text(prefix + "= " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    if log_rows:
        with LOG.open("a", encoding="utf-8", newline="") as handle:
            csv.writer(handle).writerows(log_rows)
    print(f"patched {len(PATCHES)} N5 Topic 1 stories; logged {len(log_rows)} field changes")


if __name__ == "__main__":
    main()
