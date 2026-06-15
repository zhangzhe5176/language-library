import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "n3-data.js"

VOCAB_BY_NO = {
    "1668": ["1668", "苦しむ", "くるしむ", "動1自", "痛苦，受苦"],
    "1735": ["1735", "休業[する]", "きゅうぎょう", "名・動3自", "停业，歇业"],
    "1750": ["1750", "出血[する]", "しゅっけつ", "名・動3自", "出血，流血"],
}


def main():
    text = DATA.read_text(encoding="utf-8")
    prefix, raw = text.split("=", 1)
    data = json.loads(raw.strip().rstrip(";"))
    seen = set()
    for story in data["stories"]:
        for i, row in enumerate(story.get("vocab", [])):
            no = str(row[0])
            if no in VOCAB_BY_NO:
                story["vocab"][i] = VOCAB_BY_NO[no]
                seen.add(no)
    missing = sorted(set(VOCAB_BY_NO) - seen, key=int)
    if missing:
        raise SystemExit(f"Missing vocab numbers: {missing}")
    DATA.write_text(
        prefix + "= " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
