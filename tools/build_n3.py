#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

from PIL import Image
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PDF = Path("/Users/wise/Documents/codex学习/N3-x.pdf")
AUDIO_ROOT = Path("/Users/wise/日本語資料/単語/N3_vocab")
RUNTIME_BIN = Path("/Users/wise/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin")
PDFTOPPM = RUNTIME_BIN / "pdftoppm"
OCR_BIN = ROOT / "tools" / "ocr_vision"

PAGE_DIR = ROOT / ".build" / "pages"
OCR_DIR = ROOT / ".build" / "ocr"
ENTRY_DIR = ROOT / "assets" / "entries"
AUDIO_DIR = ROOT / "assets" / "audio"
DATA_DIR = ROOT / "data"
LEVEL_DIR = ROOT / "levels" / "n3"

TOPICS = [
    {"id": 1, "title": "食事", "reading": "しょくじ", "english": "Eating", "page": 13},
    {"id": 2, "title": "家事", "reading": "かじ", "english": "Housework", "page": 33},
    {"id": 3, "title": "買い物", "reading": "かいもの", "english": "Shopping", "page": 49},
    {"id": 4, "title": "ファッション", "reading": "", "english": "Fashion", "page": 59},
    {"id": 5, "title": "テクノロジー", "reading": "", "english": "Technology", "page": 71},
    {"id": 6, "title": "流行", "reading": "りゅうこう", "english": "Trends", "page": 89},
    {"id": 7, "title": "人づきあい", "reading": "ひとづきあい", "english": "Social Life", "page": 103},
    {"id": 8, "title": "スポーツ", "reading": "", "english": "Sports", "page": 111},
    {"id": 9, "title": "動物", "reading": "どうぶつ", "english": "Animals", "page": 125},
    {"id": 10, "title": "町", "reading": "まち", "english": "Cities", "page": 137},
    {"id": 11, "title": "天気", "reading": "てんき", "english": "Weather", "page": 147},
    {"id": 12, "title": "旅行", "reading": "りょこう", "english": "Travel", "page": 157},
    {"id": 13, "title": "学校", "reading": "がっこう", "english": "School", "page": 177},
    {"id": 14, "title": "仕事", "reading": "しごと", "english": "Work", "page": 201},
    {"id": 15, "title": "人生", "reading": "じんせい", "english": "Life", "page": 215},
    {"id": 16, "title": "健康", "reading": "けんこう", "english": "Health", "page": 227},
    {"id": 17, "title": "マナー", "reading": "", "english": "Manners", "page": 237},
    {"id": 18, "title": "社会", "reading": "しゃかい", "english": "Society", "page": 249},
]

TOPIC_RANGES = [
    (1, 1, 160),
    (2, 161, 280),
    (3, 281, 360),
    (4, 361, 460),
    (5, 461, 600),
    (6, 601, 720),
    (7, 721, 835),
    (8, 836, 960),
    (9, 961, 1040),
    (10, 1041, 1120),
    (11, 1121, 1200),
    (12, 1201, 1360),
    (13, 1361, 1520),
    (14, 1521, 1660),
    (15, 1661, 1760),
    (16, 1761, 1840),
    (17, 1841, 1956),
    (18, 1957, 2100),
]

MANUAL_OVERRIDES = {
    1: {
        "title": "朝食とフルーツ",
        "type": "dialogue",
        "japanese": [
            {"speaker": "A", "text": "朝食にフルーツを食べるといいって聞いたんだけど、皮をむくのが面倒くさいんだよね。"},
            {"speaker": "B", "text": "じゃあ缶詰でいいんじゃない。"},
            {"speaker": "A", "text": "でも、新鮮な方がよくない？"},
        ],
        "focus": ["朝食", "フルーツ", "皮", "むく", "缶詰", "新鮮"],
        "naturalChinese": [
            "A：我听说早餐吃水果比较好，可是剥皮太麻烦了。",
            "B：那吃水果罐头不就好了？",
            "A：可是，新鲜水果不是更好吗？",
        ],
        "originalChinese": [
            "A：我听说早饭吃水果很好，但我嫌剥皮好麻烦。",
            "B：那就吃罐头呀。",
            "A：可是，还是吃新鲜的比较好吧？",
        ],
        "vocab": [
            ["1", "朝食", "ちょうしょく", "名", "早饭"],
            ["2", "昼食", "ちゅうしょく", "名", "中饭"],
            ["3", "夕食", "ゆうしょく", "名", "晚饭"],
            ["4", "フルーツ", "", "名", "水果"],
            ["5", "皮", "かわ", "名", "皮"],
            ["6", "むく", "", "動1他", "剥"],
            ["7", "缶詰", "かんづめ", "名", "罐头"],
            ["8", "新鮮な", "しんせんな", "ナ", "新鲜的"],
        ],
    },
    39: {
        "title": "昼寝とアルバイト",
        "type": "dialogue",
        "japanese": [
            {"speaker": "A", "text": "少し体がだるいから、今からちょっと昼寝するよ。"},
            {"speaker": "B", "text": "アルバイトはどうするの？"},
            {"speaker": "A", "text": "それは行くから、3時に起こしてくれない？"},
            {"speaker": "B", "text": "分かった。"},
            {"speaker": "A", "text": "ちゃんと起こしてね。"},
        ],
        "focus": ["だるい", "昼寝", "ちゃんと"],
        "naturalChinese": [
            "A：身体有点没劲儿，我现在想稍微睡个午觉。",
            "B：那打工怎么办？",
            "A：我会去的，你能 3 点叫我起来吗？",
            "B：好。",
            "A：一定要好好叫醒我哦。",
        ],
        "originalChinese": [
            "A：感觉身体有点倦怠感，现在想睡一下午觉。",
            "B：打工怎么办呢？",
            "A：我会去的，可以 3 点叫我起来吗？",
            "B：好的。",
            "A：要准确地叫醒我哦。",
        ],
        "vocab": [
            ["215", "だるい", "", "イ", "倦怠感"],
            ["216", "昼寝する", "ひるね", "名・動3自", "午觉，睡午觉"],
            ["217", "ちゃんと", "", "副", "准确地，规矩地"],
        ],
    },
    158: {
        "title": "柔道選手と金メダル",
        "type": "short",
        "japanese": [{"text": "柔道の48キロ級の日本選手が試合中に肩を負傷したが、見事に金メダルを獲得した。"}],
        "focus": ["級", "肩", "負傷", "メダル", "獲得"],
        "naturalChinese": ["一名日本柔道 48 公斤级选手在比赛中肩膀受伤，但仍然出色地拿下了金牌。"],
        "originalChinese": ["柔道的 48 公斤级日本选手在比赛中肩膀受伤了。但还是很漂亮地获得了金牌。"],
        "vocab": [
            ["836", "～級", "きゅう", "接尾", "～级"],
            ["837", "肩", "かた", "名", "肩膀"],
            ["838", "負傷する", "ふしょう", "名・動3自", "受伤"],
            ["839", "メダル", "", "名", "奖牌"],
            ["840", "獲得する", "かくとく", "名・動3他", "获得"],
        ],
    },
    159: {
        "title": "ランニングの効果",
        "type": "short",
        "japanese": [{"text": "私はランニングが苦手だ。しかしコーチが、ランニングの効果は大きいと言ったので、走り続けている。"}],
        "focus": ["ランニング", "苦手", "コーチ", "効果"],
        "naturalChinese": ["我不擅长跑步。不过教练说跑步很有效果，所以我一直坚持跑下去。"],
        "originalChinese": ["我不擅长跑步，但教练说，跑步的效果很好，所以我一直有在跑。"],
        "vocab": [
            ["841", "ランニングする", "", "名・動3自", "跑步"],
            ["842", "苦手な", "にがて", "ナ", "不擅长"],
            ["843", "コーチ", "", "名", "教练"],
            ["844", "効果", "こうか", "名", "效果"],
        ],
    },
    367: {
        "title": "通訳ロボット",
        "type": "short",
        "japanese": [{"text": "最近、通訳ロボットの話題がニュースで取り上げられている。21世紀は科学が進歩し、ますます使用が拡大されるだろう。"}],
        "focus": ["通訳", "ロボット", "話題", "世紀", "進歩", "ますます", "拡大"],
        "naturalChinese": ["最近，翻译机器人这个话题经常被新闻报道。到了 21 世纪，随着科学进步，它的使用范围应该会越来越广。"],
        "originalChinese": ["最近新闻常常提起关于翻译机器人的话题。21 世纪科学进步后，使用范围会愈加扩大吧。"],
        "vocab": [
            ["1981", "通訳する", "つうやく", "名・動3自", "翻译"],
            ["1982", "ロボット", "", "名", "机器人"],
            ["1983", "話題", "わだい", "名", "话题"],
            ["1984", "～世紀", "せいき", "接尾", "～世纪"],
            ["1985", "進歩する", "しんぽ", "名・動3自", "进步"],
            ["1986", "ますます", "", "副", "愈加"],
            ["1987", "拡大する", "かくだい", "名・動3自", "扩大"],
        ],
    },
}


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def ensure_dirs() -> None:
    for path in [PAGE_DIR, OCR_DIR, ENTRY_DIR, AUDIO_DIR, DATA_DIR, LEVEL_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def render_pages() -> None:
    if len(list(PAGE_DIR.glob("page-*.png"))) == 248:
        return
    shutil.rmtree(PAGE_DIR, ignore_errors=True)
    PAGE_DIR.mkdir(parents=True, exist_ok=True)
    run([
        str(PDFTOPPM),
        "-png",
        "-r",
        "180",
        "-f",
        "16",
        "-l",
        "263",
        str(PDF),
        str(PAGE_DIR / "page"),
    ])


def detect_starts() -> list[dict]:
    starts = []
    for page_path in sorted(PAGE_DIR.glob("page-*.png")):
        match = re.search(r"page-(\d+)\.png$", page_path.name)
        if not match:
            continue
        pdf_page = int(match.group(1))
        arr = np.array(Image.open(page_path).convert("L"))
        region = arr[:, 250:1240]
        dark = (region < 80).sum(axis=1)
        rows = np.where(dark > 450)[0]
        groups = []
        if rows.size:
            start = prev = int(rows[0])
            for row in rows[1:]:
                row = int(row)
                if row - prev > 3:
                    if dark[start : prev + 1].max() > 800:
                        groups.append((start, prev))
                    start = row
                prev = row
            if dark[start : prev + 1].max() > 800:
                groups.append((start, prev))
        for y1, y2 in groups:
            starts.append({"pdfPage": pdf_page, "printedPage": pdf_page - 2, "y": (y1 + y2) // 2, "pageImage": page_path.name})
    if len(starts) != 371:
        raise RuntimeError(f"expected 371 story starts, found {len(starts)}")
    for index, start in enumerate(starts, start=1):
        start["id"] = index
    return starts


def topic_for_word_no(word_no: int) -> int:
    for topic_id, begin, end in TOPIC_RANGES:
        if begin <= word_no <= end:
            return topic_id
    return 18


def topic_for_story(story_id: int) -> int:
    # Approximate by story number when OCR cannot prove the first vocab number.
    if story_id <= 28:
        return 1
    if story_id <= 49:
        return 2
    if story_id <= 64:
        return 3
    if story_id <= 83:
        return 4
    if story_id <= 107:
        return 5
    if story_id <= 128:
        return 6
    if story_id <= 157:
        return 7
    if story_id <= 178:
        return 8
    if story_id <= 193:
        return 9
    if story_id <= 207:
        return 10
    if story_id <= 222:
        return 11
    if story_id <= 251:
        return 12
    if story_id <= 282:
        return 13
    if story_id <= 306:
        return 14
    if story_id <= 325:
        return 15
    if story_id <= 341:
        return 16
    if story_id <= 363:
        return 17
    return 18


def crop_entries(starts: list[dict]) -> dict[int, list[str]]:
    shutil.rmtree(ENTRY_DIR, ignore_errors=True)
    ENTRY_DIR.mkdir(parents=True, exist_ok=True)
    images_by_story: dict[int, list[str]] = {}
    page_cache: dict[int, Image.Image] = {}

    def page_image(pdf_page: int) -> Image.Image:
        if pdf_page not in page_cache:
            page_cache[pdf_page] = Image.open(PAGE_DIR / f"page-{pdf_page:03d}.png").convert("RGB")
        return page_cache[pdf_page]

    x1, x2 = 225, 1268
    top_margin = 24
    content_top = 235
    content_bottom = 1705
    for idx, start in enumerate(starts):
        story_id = start["id"]
        next_start = starts[idx + 1] if idx + 1 < len(starts) else None
        pdf_page = start["pdfPage"]
        end_page = next_start["pdfPage"] if next_start else pdf_page
        parts = []
        part_no = 1
        for page_no in range(pdf_page, end_page + 1):
            page = page_image(page_no)
            if page_no == pdf_page:
                y1 = max(0, start["y"] - top_margin)
            else:
                y1 = content_top
            if next_start and page_no == next_start["pdfPage"]:
                y2 = max(y1 + 120, next_start["y"] - top_margin)
            else:
                y2 = min(page.height, content_bottom)
            # Avoid generating a tiny continuation sliver.
            if y2 - y1 < 140:
                continue
            crop = page.crop((x1, y1, x2, y2))
            name = f"T{story_id:03d}_{part_no}.png"
            crop.save(ENTRY_DIR / name, optimize=True)
            parts.append(f"assets/entries/{name}")
            part_no += 1
        images_by_story[story_id] = parts
    return images_by_story


def run_ocr(image_paths: list[Path]) -> dict[str, dict]:
    ocr_cache = OCR_DIR / "entries.jsonl"
    if ocr_cache.exists():
        result = {}
        with ocr_cache.open("r", encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    obj = json.loads(line)
                    result[Path(obj["path"]).name] = obj
        if len(result) == len(image_paths):
            return result

    result = {}
    with ocr_cache.open("w", encoding="utf-8") as out:
        chunk_size = 18
        for i in range(0, len(image_paths), chunk_size):
            chunk = image_paths[i : i + chunk_size]
            proc = subprocess.run([str(OCR_BIN), *map(str, chunk)], check=True, text=True, capture_output=True)
            for line in proc.stdout.splitlines():
                if not line.strip():
                    continue
                obj = json.loads(line)
                result[Path(obj["path"]).name] = obj
                out.write(json.dumps(obj, ensure_ascii=False) + "\n")
            print(f"OCR {min(i + chunk_size, len(image_paths))}/{len(image_paths)}")
    return result


def sorted_ocr_lines(ocr_obj: dict) -> list[dict]:
    return sorted(ocr_obj.get("lines", []), key=lambda item: (-item["y"], item["x"]))


def has_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def has_kana(text: str) -> bool:
    return bool(re.search(r"[\u3040-\u30ff]", text))


def is_vocab_number(text: str) -> bool:
    return bool(re.fullmatch(r"\d{1,4}", text.strip()))


def extract_japanese(lines: list[dict]) -> list[dict]:
    collected = []
    for line in lines:
        text = clean_text(line["text"])
        if not text:
            continue
        if is_vocab_number(text):
            break
        if re.search(r"[A-Za-z]{4,}/", text):
            break
        if "/" in text and re.search(r"[A-Za-z]", text):
            break
        if has_kana(text) or re.search(r"[A：B：]", text):
            # Drop very short furigana-only lines where possible.
            if re.fullmatch(r"[\u3040-\u309fー]+", text) and len(text) <= 8:
                continue
            speaker_match = re.match(r"^([ABＡＢ])[:：]\s*(.+)$", text)
            if speaker_match:
                collected.append({"speaker": speaker_match.group(1).translate(str.maketrans("ＡＢ", "AB")), "text": speaker_match.group(2)})
            else:
                collected.append({"text": text})
    if not collected:
        for line in lines[:4]:
            text = clean_text(line["text"])
            if has_kana(text) or has_cjk(text):
                collected.append({"text": text})
    return collected[:8]


def extract_chinese(lines: list[dict]) -> list[str]:
    lower_lines = lines[int(len(lines) * 0.55) :]
    text = " ".join(clean_text(line["text"]) for line in lower_lines)
    pieces = []
    for segment in re.split(r"/+", text):
        segment = segment.strip(" 。,，")
        if has_cjk(segment) and not has_kana(segment):
            # Remove obvious English and Vietnamese residue around the Chinese segment.
            segment = re.sub(r"^[A-Za-z0-9 .,'’:-]+", "", segment).strip()
            if len(segment) >= 6:
                pieces.append(segment)
    if pieces:
        return [max(pieces, key=len)]
    cjk_lines = [clean_text(line["text"]) for line in lower_lines if has_cjk(line["text"]) and not has_kana(line["text"])]
    return [" ".join(cjk_lines[-3:]).strip()] if cjk_lines else []


def extract_vocab_raw(lines: list[dict]) -> list[str]:
    started = False
    output = []
    for line in lines:
        text = clean_text(line["text"])
        if not text:
            continue
        if is_vocab_number(text):
            started = True
        if started:
            if len(output) >= 42:
                break
            output.append(text)
    return output


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def title_from_japanese(story_id: int, japanese: list[dict]) -> str:
    if not japanese:
        return f"No. {story_id}"
    text = japanese[0].get("text", "")
    text = re.sub(r"^[ABＡＢ][:：]\s*", "", text)
    return text[:22] + ("…" if len(text) > 22 else "")


def copy_audio() -> None:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    for i in range(1, 372):
        src = AUDIO_ROOT / f"T{i}.mp3"
        if not src.exists():
            raise FileNotFoundError(src)
        dst = AUDIO_DIR / src.name
        if not dst.exists() or dst.stat().st_size != src.stat().st_size:
            shutil.copy2(src, dst)


def build_data(starts: list[dict], images_by_story: dict[int, list[str]], ocr_by_image: dict[str, dict]) -> dict:
    stories = []
    for start in starts:
        story_id = start["id"]
        image_names = [Path(path).name for path in images_by_story[story_id]]
        ocr_parts = [ocr_by_image[name] for name in image_names if name in ocr_by_image]
        lines = []
        for part in ocr_parts:
            lines.extend(sorted_ocr_lines(part))
        japanese = extract_japanese(lines)
        original_chinese = extract_chinese(lines)
        vocab_raw = extract_vocab_raw(lines)
        story_type = "dialogue" if any(line.get("speaker") for line in japanese) else "short"
        topic_id = topic_for_story(story_id)
        story = {
            "id": story_id,
            "topicId": topic_id,
            "page": start["printedPage"],
            "type": story_type,
            "title": title_from_japanese(story_id, japanese),
            "audio": f"T{story_id}.mp3",
            "images": images_by_story[story_id],
            "japanese": japanese,
            "focus": [],
            "naturalChinese": ["待根据日文重新翻译。"],
            "originalChinese": original_chinese or ["OCR 暂未提取到原书中文。"],
            "vocab": [],
            "vocabRaw": vocab_raw,
            "ocrText": "\n".join(clean_text(line["text"]) for line in lines),
            "reviewStatus": "OCR未校对",
        }
        if story_id in MANUAL_OVERRIDES:
            override = MANUAL_OVERRIDES[story_id]
            story.update(override)
            story["reviewStatus"] = "样张已校对"
        stories.append(story)
    return {"topics": TOPICS, "stories": stories}


def write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_site_files(data: dict) -> None:
    write_file(DATA_DIR / "n3-data.js", "window.N3_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n")

    write_file(ROOT / "index.html", """<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>日本语学习站</title>
    <link rel="icon" href="data:," />
    <link rel="stylesheet" href="./styles.css" />
  </head>
  <body data-page="levels" data-base=".">
    <header class="siteHeader">
      <a class="brand" href="./index.html"><span>日本语学习站</span><strong>JLPT Library</strong></a>
      <nav class="topNav" aria-label="主导航">
        <a aria-current="page" href="./index.html">等级</a>
        <a href="./levels/n3/index.html">N3</a>
        <a href="./levels/n3/topics.html">目录</a>
      </nav>
    </header>
    <main class="siteShell">
      <section class="heroPanel">
        <p class="eyebrow">Local Personal Edition</p>
        <h1>外语学习门户本地版</h1>
        <p class="lead">当前已接入日语 N3 个人学习内容。N5、N4、N2、N1 和其他语言课程作为后续入口预留。</p>
      </section>
      <section class="levelGrid" aria-label="等级入口">
        <a class="levelCard locked" href="#" aria-disabled="true"><span>N5</span><strong>预留</strong><em>后续添加</em></a>
        <a class="levelCard locked" href="#" aria-disabled="true"><span>N4</span><strong>预留</strong><em>后续添加</em></a>
        <a class="levelCard active" href="./levels/n3/index.html"><span>N3</span><strong>371 段</strong><em>个人本地学习版</em></a>
        <a class="levelCard locked" href="#" aria-disabled="true"><span>N2</span><strong>预留</strong><em>后续添加</em></a>
        <a class="levelCard locked" href="#" aria-disabled="true"><span>N1</span><strong>预留</strong><em>后续添加</em></a>
      </section>
    </main>
    <script src="./data/n3-data.js"></script>
    <script src="./app.js"></script>
  </body>
</html>
""")

    write_file(LEVEL_DIR / "index.html", page_html("n3-home", "../..", "N3 首页 - 日本语学习站"))
    write_file(LEVEL_DIR / "topics.html", page_html("topics", "../..", "N3 目录 - 日本语学习站"))
    for topic in TOPICS:
        write_file(LEVEL_DIR / f"topic-{topic['id']:02d}.html", page_html("topic", "../..", f"Topic {topic['id']} {topic['title']} - N3", topic["id"]))


def page_html(page: str, base: str, title: str, topic_id: int | None = None) -> str:
    topic_attr = f' data-topic="{topic_id}"' if topic_id is not None else ""
    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
    <link rel="icon" href="data:," />
    <link rel="stylesheet" href="{base}/styles.css" />
  </head>
  <body data-page="{page}"{topic_attr} data-base="{base}">
    <header class="siteHeader">
      <a class="brand" href="{base}/index.html"><span>日本语学习站</span><strong>JLPT Library</strong></a>
      <nav class="topNav" aria-label="主导航">
        <a href="{base}/index.html">等级</a>
        <a href="{base}/levels/n3/index.html">N3</a>
        <a href="{base}/levels/n3/topics.html">目录</a>
      </nav>
    </header>
    <main id="app"></main>
    <script src="{base}/data/n3-data.js"></script>
    <script src="{base}/app.js"></script>
  </body>
</html>
"""


def main() -> None:
    ensure_dirs()
    render_pages()
    starts = detect_starts()
    print(f"detected {len(starts)} story starts")
    images_by_story = crop_entries(starts)
    print(f"cropped {sum(len(v) for v in images_by_story.values())} entry images")
    entry_images = sorted(ENTRY_DIR.glob("T*.png"))
    ocr_by_image = run_ocr(entry_images)
    print(f"OCR cache has {len(ocr_by_image)} images")
    copy_audio()
    data = build_data(starts, images_by_story, ocr_by_image)
    write_site_files(data)
    print("done")


if __name__ == "__main__":
    main()
