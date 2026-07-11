#!/usr/bin/env python3
from repair_utils import apply_topic_patch, dialogue


PATCHES = {
    9: {
        "title": "让座时请对方先坐",
        "type": "dialogue",
        "japanese": dialogue(("A", "どうぞ。"), ("B", "あ、すみません。")),
        "focus": ["どうぞ", "すみません"],
        "naturalChinese": ["A：您请。", "B：啊，谢谢。"],
        "originalChinese": ["A：请。", "B：啊，不好意思。"],
        "vocab": [["14", "どうぞ①", "", "副", "请"], ["15", "すみません①", "", "句", "不好意思"]],
    },
    10: {
        "title": "碰到别人时道歉",
        "type": "dialogue",
        "japanese": dialogue(("A", "あっ、すみません！"), ("B", "いいえ。")),
        "focus": ["すみません", "いいえ"],
        "naturalChinese": ["A：啊，对不起！", "B：没事。"],
        "originalChinese": ["A：啊，不好意思。", "B：没事。"],
        "vocab": [["16", "いいえ", "", "感", "没事"]],
    },
    11: {
        "title": "感谢与回应",
        "type": "dialogue",
        "japanese": dialogue(("A", "ありがとうございます。"), ("B", "いいえ。どういたしまして。")),
        "focus": ["ありがとうございます", "どういたしまして"],
        "naturalChinese": ["A：谢谢。", "B：不用谢，不客气。"],
        "originalChinese": ["A：谢谢。", "B：不客气。"],
        "vocab": [["17", "ありがとうございます", "", "句", "谢谢"], ["18", "どういたしまして", "", "句", "不客气"]],
    },
    12: {
        "title": "递东西时致谢",
        "type": "dialogue",
        "japanese": dialogue(("A", "どうぞ。"), ("B", "どうも。")),
        "focus": ["どうぞ", "どうも"],
        "naturalChinese": ["A：给你。", "B：谢谢。"],
        "originalChinese": ["A：请。", "B：谢谢。"],
        "vocab": [["19", "どうも", "", "副", "谢谢"]],
    },
    13: {
        "title": "打翻东西时道歉",
        "type": "dialogue",
        "japanese": dialogue(("A", "ごめんなさい。"), ("B", "あ、いえ。")),
        "focus": ["ごめんなさい", "いえ"],
        "naturalChinese": ["A：对不起。", "B：啊，没事。"],
        "originalChinese": ["A：对不起。", "B：啊，不会。"],
        "vocab": [["20", "ごめんなさい", "", "句", "对不起"], ["21", "いえ①", "", "感", "没事"]],
    },
    14: {
        "title": "进门时打招呼",
        "type": "dialogue",
        "japanese": dialogue(("A", "しつれいします。"), ("B", "どうぞ。")),
        "focus": ["しつれいします", "どうぞ"],
        "naturalChinese": ["A：打扰了。", "B：请进。"],
        "originalChinese": ["A：打扰了。", "B：请进。"],
        "vocab": [["22", "しつれいします②", "", "句", "打扰了"], ["23", "どうぞ②", "", "副", "请进"]],
    },
    15: {
        "title": "接电话时问候",
        "type": "dialogue",
        "japanese": dialogue(("A", "もしもし。"), ("B", "あ、アンさん。")),
        "focus": ["もしもし"],
        "naturalChinese": ["A：喂？", "B：啊，是安小姐。"],
        "originalChinese": ["A：喂～。", "B：啊，Anne小姐。"],
        "vocab": [["24", "もしもし", "", "感", "喂"]],
    },
    16: {
        "title": "久别后的电话问候",
        "type": "dialogue",
        "japanese": dialogue(("A", "おひさしぶりです。"), ("B", "あ、アンさん。おげんきですか。")),
        "focus": ["おひさしぶりです", "おげんきですか"],
        "naturalChinese": ["A：好久不见。", "B：啊，安小姐。你最近好吗？"],
        "originalChinese": ["A：好久不见。", "B：啊，Anne小姐，你过得好吗？"],
        "vocab": [["25", "おひさしぶりです", "", "句", "好久不见"], ["26", "（お）げんきですか", "", "句", "你过得好吗"]],
    },
}


if __name__ == "__main__":
    changed = apply_topic_patch(
        level="n5", topic_id=2, patches=PATCHES,
        source="N5 PDF pages 22-24 (printed pages 20-22)",
        reviewed_at="2026-07-12T00:00:00+09:00",
    )
    print(f"patched {len(PATCHES)} N5 Topic 2 stories; logged {changed} field changes")
