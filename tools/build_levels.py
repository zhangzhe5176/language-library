#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT.parent / "references"
RUNTIME_ROOT = Path("/Users/wise/.cache/codex-runtimes/codex-primary-runtime/dependencies")
PDFTOPPM = RUNTIME_ROOT / "bin" / "override" / "pdftoppm"
if not PDFTOPPM.exists():
    PDFTOPPM = Path(shutil.which("pdftoppm") or "pdftoppm")


@dataclass(frozen=True)
class Topic:
    id: int
    title: str
    reading: str
    english: str
    page: int


@dataclass(frozen=True)
class Book:
    level: str
    pdf: Path
    audio_url: str
    track_count: int
    word_count: int
    numbered_word_count: int
    content_first_pdf_page: int
    content_last_pdf_page: int
    printed_page_offset: int
    topics: tuple[Topic, ...]
    marker_overrides: dict[int, tuple[int, int]]


def make_topics(rows: list[tuple[str, str, str, int]]) -> tuple[Topic, ...]:
    return tuple(Topic(index, *row) for index, row in enumerate(rows, start=1))


BOOKS = {
    "n2": Book(
        level="n2",
        pdf=SOURCE_ROOT / "2.pdf",
        audio_url="https://bookclub2.japantimes.co.jp/download/files/Best_Vocab_N2.zip",
        track_count=452,
        word_count=2400,
        numbered_word_count=2360,
        content_first_pdf_page=19,
        content_last_pdf_page=337,
        printed_page_offset=5,
        topics=make_topics([
            ("食事", "しょくじ", "Eating", 14),
            ("家事", "かじ", "Housework", 26),
            ("買い物", "かいもの", "Shopping", 41),
            ("ファッション", "", "Fashion", 50),
            ("テクノロジー", "", "Technology", 65),
            ("流行", "りゅうこう", "Trends", 82),
            ("趣味", "しゅみ", "Hobbies", 102),
            ("人付き合い", "ひとづきあい", "Social Life", 114),
            ("年中行事", "ねんちゅうぎょうじ", "Annual Events", 128),
            ("スポーツ", "", "Sports", 133),
            ("動物", "どうぶつ", "Animals", 148),
            ("住", "じゅう", "Housing", 159),
            ("町", "まち", "Cities", 170),
            ("天気", "てんき", "Weather", 181),
            ("旅行", "りょこう", "Travel", 194),
            ("学校", "がっこう", "School", 212),
            ("仕事", "しごと", "Work", 232),
            ("人生", "じんせい", "Life", 249),
            ("健康", "けんこう", "Health", 264),
            ("マナー", "", "Manners", 276),
            ("社会", "しゃかい", "Society", 290),
            ("政治", "せいじ", "Politics", 305),
            ("環境・科学", "かんきょう・かがく", "Environment & Science", 313),
        ]),
        marker_overrides={
            1: (19, 748),
            12: (27, 318),
            17: (30, 584),
            28: (39, 318),
            98: (91, 1295),
            413: (310, 744),
        },
    ),
    "n5": Book(
        level="n5",
        pdf=SOURCE_ROOT / "5.pdf",
        audio_url="https://bookclub2.japantimes.co.jp/download/files/Best_Vocab_N5.zip",
        track_count=373,
        word_count=1000,
        numbered_word_count=1010,
        content_first_pdf_page=18,
        content_last_pdf_page=229,
        printed_page_offset=2,
        topics=make_topics([
            ("あいさつ1", "あいさつ", "Greetings 1", 15),
            ("あいさつ2", "あいさつ", "Greetings 2", 19),
            ("カフェ", "", "At the Cafe", 23),
            ("時間", "じかん", "Time", 27),
            ("値段", "ねだん", "Prices", 33),
            ("レストラン1", "", "Restaurants 1", 39),
            ("位置・場所1", "いち・ばしょ", "Positions & Places 1", 44),
            ("曜日・年月日1", "ようび・ねんがっぴ", "Days & Dates 1", 55),
            ("朝昼晩", "あさひるばん", "Morning, Noon & Night", 64),
            ("毎日のこと・場所2", "まいにち・ばしょ", "Daily Activities & Places 2", 72),
            ("趣味・場所3", "しゅみ・ばしょ", "Hobbies & Places 3", 80),
            ("部屋の中", "へやのなか", "Indoors", 92),
            ("形容詞1", "けいようし", "Adjectives 1", 100),
            ("形容詞2", "けいようし", "Adjectives 2", 108),
            ("年月日2・季節", "ねんがっぴ・きせつ", "Dates 2 & Seasons", 119),
            ("家族1", "かぞく", "Family 1", 127),
            ("プレゼント", "", "Presents", 136),
            ("レストラン2", "", "Restaurants 2", 144),
            ("家族2", "かぞく", "Family 2", 156),
            ("服・体", "ふく・からだ", "Clothing & Body", 166),
            ("物への動作", "ものへのどうさ", "Actions & Items", 178),
            ("交通・道", "こうつう・みち", "Roads & Traffic", 187),
            ("郵便局・天気", "ゆうびんきょく・てんき", "Post Office & Weather", 201),
            ("クラス", "", "In Class", 211),
        ]),
        # Vision OCR misses a few tiny track labels, including two rotated vocabulary charts.
        # Values are (PDF page, top pixel at 180 dpi), verified against the source pages.
        marker_overrides={
            1: (18, 305),
            5: (19, 761),
            32: (37, 305),
            73: (63, 305),
            184: (130, 235),
            185: (131, 235),
        },
    ),
    "n4": Book(
        level="n4",
        pdf=SOURCE_ROOT / "4.pdf",
        audio_url="https://bookclub2.japantimes.co.jp/download/files/Best_Vocab_N4.zip",
        track_count=262,
        word_count=1200,
        numbered_word_count=1035,
        content_first_pdf_page=18,
        content_last_pdf_page=186,
        printed_page_offset=2,
        topics=make_topics([
            ("家・寮", "いえ・りょう", "At Home & the Dorm", 15),
            ("店", "みせ", "Shops & Restaurants", 29),
            ("学校", "がっこう", "School & University", 45),
            ("町", "まち", "Around Town", 63),
            ("病院", "びょういん", "At the Hospital", 75),
            ("駅", "えき", "At the Train Station", 85),
            ("観光地", "かんこうち", "Sightseeing", 95),
            ("山・海", "やま・うみ", "The Mountains & the Sea", 111),
            ("公園", "こうえん", "At the Park", 121),
            ("ジム・グラウンド", "", "At the Gym & on the Field", 129),
            ("訪問先", "ほうもんさき", "Visiting Destination", 143),
            ("インターネット", "", "The Internet", 153),
            ("職場", "しょくば", "At Work", 163),
        ]),
        marker_overrides={189: (141, 583)},
    ),
}


def work_dir(book: Book) -> Path:
    return ROOT / ".build" / "levels" / book.level


def page_dir(book: Book) -> Path:
    return work_dir(book) / "pages"


def ocr_dir(book: Book) -> Path:
    return work_dir(book) / "ocr"


def entry_dir(book: Book) -> Path:
    return ROOT / "assets" / book.level / "entries"


def audio_dir(book: Book) -> Path:
    return ROOT / "assets" / book.level / "audio"


def render_pages(book: Book) -> None:
    target = page_dir(book)
    target.mkdir(parents=True, exist_ok=True)
    expected = book.content_last_pdf_page - book.content_first_pdf_page + 1
    existing = list(target.glob("page-*.png"))
    if len(existing) == expected:
        return
    for path in existing:
        path.unlink()
    subprocess.run([
        str(PDFTOPPM), "-png", "-r", "180",
        "-f", str(book.content_first_pdf_page),
        "-l", str(book.content_last_pdf_page),
        str(book.pdf), str(target / "page"),
    ], check=True)


def page_ocr_cache(book: Book) -> Path:
    return ocr_dir(book) / "pages.jsonl"


def run_page_ocr(book: Book) -> dict[int, dict]:
    cache = page_ocr_cache(book)
    cache.parent.mkdir(parents=True, exist_ok=True)
    pages = sorted(page_dir(book).glob("page-*.png"))
    cached: dict[int, dict] = {}
    if cache.exists():
        for line in cache.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            obj = json.loads(line)
            match = re.search(r"page-(\d+)\.png$", obj["path"])
            if match:
                cached[int(match.group(1))] = obj
    missing = [path for path in pages if int(re.search(r"(\d+)", path.stem).group(1)) not in cached]
    if missing:
        executable = compile_ocr()
        with cache.open("a", encoding="utf-8") as output:
            for offset in range(0, len(missing), 12):
                chunk = missing[offset : offset + 12]
                result = subprocess.run(
                    [str(executable), *map(str, chunk)], check=True, text=True, capture_output=True
                )
                for line in result.stdout.splitlines():
                    if not line.strip():
                        continue
                    obj = json.loads(line)
                    match = re.search(r"page-(\d+)\.png$", obj["path"])
                    if match:
                        cached[int(match.group(1))] = obj
                    output.write(json.dumps(obj, ensure_ascii=False) + "\n")
                print(f"{book.level}: page OCR {min(offset + 12, len(missing))}/{len(missing)} new pages")
    if len(cached) != len(pages):
        raise RuntimeError(f"{book.level}: page OCR cache {len(cached)} does not match {len(pages)} pages")
    return cached


def detect_starts(book: Book, pages_ocr: dict[int, dict]) -> list[dict]:
    candidates: list[tuple[int, int, str, str]] = []
    for pdf_page, obj in sorted(pages_ocr.items()):
        for line in sorted(obj.get("lines", []), key=lambda item: -item["y"]):
            text = line["text"].strip()
            digits = "".join(re.findall(r"\d", text))
            if not digits or "p." in text.lower():
                continue
            if not (0.68 < line["x"] < 0.82 and 0.15 < line["y"] < 0.9 and len(text) < 18):
                continue
            y = int((1 - line["y"] - line["height"]) * 1980)
            candidates.append((pdf_page, max(0, y), text, digits))

    detected: dict[int, dict] = {}
    previous = 0
    for pdf_page, y, text, digits in candidates:
        possible = [
            track
            for track in range(previous + 1, min(book.track_count + 1, previous + 16))
            if digits.endswith(str(track))
        ]
        if not possible:
            continue
        track = min(possible)
        detected[track] = {"pdfPage": pdf_page, "y": y, "markerText": text}
        previous = track

    for track, (pdf_page, y) in book.marker_overrides.items():
        detected[track] = {"pdfPage": pdf_page, "y": y, "markerText": "manual-verified"}

    missing = [track for track in range(1, book.track_count + 1) if track not in detected]
    if missing:
        raise RuntimeError(f"{book.level}: missing track markers {missing}")
    starts = []
    for track in range(1, book.track_count + 1):
        start = detected[track]
        start.update({
            "id": track,
            "printedPage": start["pdfPage"] - book.printed_page_offset,
            "pageImage": f"page-{start['pdfPage']:03d}.jpg",
        })
        start["topicId"] = topic_for_page(book, start["printedPage"])
        starts.append(start)
    if any(starts[index]["pdfPage"] > starts[index + 1]["pdfPage"] for index in range(len(starts) - 1)):
        raise RuntimeError(f"{book.level}: detected track pages are not monotonic")
    return starts


def topic_for_page(book: Book, printed_page: int) -> int:
    topic_id = 1
    for topic in book.topics:
        if topic.page <= printed_page:
            topic_id = topic.id
        else:
            break
    return topic_id


def export_source_pages(book: Book, starts: list[dict]) -> dict[int, list[str]]:
    from PIL import Image

    target = ROOT / "assets" / book.level / "pages"
    target.mkdir(parents=True, exist_ok=True)
    for path in target.glob("page-*.jpg"):
        path.unlink()
    used_pages = sorted({start["pdfPage"] for start in starts})
    for page_number in used_pages:
        source = page_dir(book) / f"page-{page_number:03d}.png"
        Image.open(source).convert("RGB").save(
            target / f"page-{page_number:03d}.jpg", "JPEG", quality=84, optimize=True
        )
    return {
        start["id"]: [f"assets/{book.level}/pages/page-{start['pdfPage']:03d}.jpg"]
        for start in starts
    }


def audio_member_map(names: list[str]) -> dict[int, str]:
    members: dict[int, str] = {}
    for name in names:
        match = re.fullmatch(r"T0*(\d+)\.mp3", Path(name).name, re.IGNORECASE)
        if match:
            members[int(match.group(1))] = name
    return members


def download_audio(book: Book) -> None:
    target = audio_dir(book)
    target.mkdir(parents=True, exist_ok=True)
    archive = work_dir(book) / "audio.zip"
    archive.parent.mkdir(parents=True, exist_ok=True)
    if not archive.exists():
        urllib.request.urlretrieve(book.audio_url, archive)
    with zipfile.ZipFile(archive) as bundle:
        members = audio_member_map(bundle.namelist())
        if len(members) != book.track_count:
            raise RuntimeError(f"{book.level}: expected {book.track_count} audio files, found {len(members)}")
        for track in range(1, book.track_count + 1):
            name = f"T{track}.mp3"
            member = members.get(track)
            if not member:
                raise RuntimeError(f"{book.level}: missing {name}")
            destination = target / name
            data = bundle.read(member)
            if not destination.exists() or destination.stat().st_size != len(data):
                destination.write_bytes(data)


def compile_ocr() -> Path:
    executable = work_dir(BOOKS["n5"]).parent / "ocr_vision"
    source = ROOT / "tools" / "ocr_vision.swift"
    if not executable.exists() or executable.stat().st_mtime < source.stat().st_mtime:
        executable.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["swiftc", str(source), "-o", str(executable)], check=True)
    return executable


def run_ocr(book: Book, images: list[Path]) -> dict[str, dict]:
    target = ocr_dir(book)
    target.mkdir(parents=True, exist_ok=True)
    cache = target / "entries.jsonl"
    cached: dict[str, dict] = {}
    if cache.exists():
        for line in cache.read_text(encoding="utf-8").splitlines():
            if line.strip():
                obj = json.loads(line)
                cached[Path(obj["path"]).name] = obj
    missing = [path for path in images if path.name not in cached]
    if missing:
        executable = compile_ocr()
        with cache.open("a", encoding="utf-8") as output:
            for offset in range(0, len(missing), 16):
                chunk = missing[offset : offset + 16]
                result = subprocess.run(
                    [str(executable), *map(str, chunk)], check=True, text=True, capture_output=True
                )
                for line in result.stdout.splitlines():
                    if not line.strip():
                        continue
                    obj = json.loads(line)
                    cached[Path(obj["path"]).name] = obj
                    output.write(json.dumps(obj, ensure_ascii=False) + "\n")
                print(f"{book.level}: OCR {min(offset + 16, len(missing))}/{len(missing)} new images")
    if len(cached) != len(images):
        raise RuntimeError(f"{book.level}: OCR cache {len(cached)} does not match {len(images)} images")
    return cached


def prepare(book: Book) -> None:
    if not book.pdf.exists():
        raise FileNotFoundError(book.pdf)
    render_pages(book)
    pages_ocr = run_page_ocr(book)
    starts = detect_starts(book, pages_ocr)
    images_by_track = export_source_pages(book, starts)
    download_audio(book)
    manifest = {
        "level": book.level,
        "trackCount": book.track_count,
        "wordCount": book.word_count,
        "numberedWordCount": book.numbered_word_count,
        "starts": starts,
        "images": images_by_track,
    }
    path = work_dir(book) / "manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{book.level}: prepared {len(starts)} tracks and {len(set(s['pdfPage'] for s in starts))} source pages")


def line_top(line: dict) -> int:
    return int((1 - line["y"] - line["height"]) * 1980)


def segment_lines(pages_ocr: dict[int, dict], starts: list[dict], index: int) -> list[dict]:
    start = starts[index]
    next_start = starts[index + 1] if index + 1 < len(starts) else None
    end_y = next_start["y"] if next_start and next_start["pdfPage"] == start["pdfPage"] else 1740
    lines = []
    for line in pages_ocr[start["pdfPage"]].get("lines", []):
        top = line_top(line)
        if start["y"] <= top < end_y:
            item = dict(line)
            item["top"] = top
            item["text"] = re.sub(r"\s+", " ", item["text"]).strip()
            if item["text"]:
                lines.append(item)
    return sorted(lines, key=lambda item: (item["top"], item["x"]))


def has_japanese(text: str) -> bool:
    return bool(re.search(r"[ぁ-ゖァ-ヺ一-龯]", text))


def has_kana(text: str) -> bool:
    return bool(re.search(r"[ぁ-ゖァ-ヺ]", text))


def has_han(text: str) -> bool:
    return bool(re.search(r"[一-龯]", text))


def extract_japanese(lines: list[dict]) -> list[dict]:
    output: list[dict] = []
    for line in lines:
        text = line["text"]
        if "/" in text or re.match(r"^\d{1,4}(?:\s|$)", text):
            continue
        speaker = re.match(r"^([ABＡＢ])\s*[:：]\s*(.+)$", text)
        if speaker and has_japanese(speaker.group(2)):
            output.append({"speaker": speaker.group(1).translate(str.maketrans("ＡＢ", "AB")), "text": speaker.group(2)})
        elif output and has_japanese(text) and len(text) >= 4 and line["top"] - lines[0]["top"] < 260:
            output.append({"text": text})
        if len(output) >= 8:
            break
    if output:
        return output
    for line in lines:
        text = line["text"]
        if "/" not in text and has_kana(text) and len(text) >= 8:
            return [{"text": text}]
    return []


def chinese_segment(text: str) -> str:
    candidates = []
    for part in re.split(r"/+", text):
        part = part.strip(" ，。,:：")
        if has_han(part) and not has_kana(part):
            candidates.append(part)
    return max(candidates, key=len) if candidates else ""


def extract_original_chinese(lines: list[dict]) -> list[str]:
    candidates = []
    for line in lines:
        text = line["text"]
        if "/" not in text:
            continue
        chinese = chinese_segment(text)
        if len(chinese) >= 6:
            candidates.append((len(text), chinese))
    if not candidates:
        return []
    candidates.sort(reverse=True)
    return [candidates[0][1]]


def extract_vocab_with_top(lines: list[dict], word_count: int) -> list[tuple[int, list[str]]]:
    vocab: list[tuple[int, list[str]]] = []
    for index, line in enumerate(lines):
        if line["x"] > 0.42:
            continue
        match = re.match(r"^(\d{1,4})\s*(.*)$", line["text"])
        if not match:
            continue
        number = int(match.group(1))
        if not 1 <= number <= word_count:
            continue
        word = match.group(2).strip()
        nearby = [item for item in lines[index + 1 :] if item["top"] - line["top"] <= 115]
        if not word or not has_japanese(word):
            for item in nearby:
                if "/" not in item["text"] and has_japanese(item["text"]) and not re.match(r"^[ABＡＢ][:：]", item["text"]):
                    word = item["text"]
                    break
        gloss = next((item["text"] for item in nearby if "/" in item["text"]), "")
        meaning = chinese_segment(gloss)
        kind_match = re.search(r"\b(Phr|Adv|Adj|Intj|Conj|Adnom|Suf|N|V[123](?:-[IT])?)\b", gloss, re.IGNORECASE)
        kind = kind_match.group(1) if kind_match else ""
        if word:
            vocab.append((line["top"], [str(number), word, "", kind, meaning]))
    unique: dict[int, tuple[int, list[str]]] = {}
    for top, row in vocab:
        unique.setdefault(int(row[0]), (top, row))
    return [unique[number] for number in sorted(unique)]


def extract_vocab(lines: list[dict], word_count: int) -> list[list[str]]:
    return [row for _, row in extract_vocab_with_top(lines, word_count)]


def story_title(track: int, japanese: list[dict]) -> str:
    if not japanese:
        return f"词汇记忆 {track}"
    text = japanese[0]["text"].strip()
    return text[:18] + ("…" if len(text) > 18 else "")


def load_existing_reviewed_sample() -> dict[int, dict]:
    path = ROOT / "data" / "n5-data.js"
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(r"window\.LEVEL_DATA\s*=\s*(\{.*\});\s*", text, re.DOTALL)
    if not match:
        return {}
    data = json.loads(match.group(1))
    return {story["id"]: story for story in data.get("stories", []) if story.get("reviewStatus") == "已校对"}


def build_data(book: Book) -> dict:
    manifest = json.loads((work_dir(book) / "manifest.json").read_text(encoding="utf-8"))
    starts = manifest["starts"]
    pages_ocr = run_page_ocr(book)
    reviewed = load_existing_reviewed_sample() if book.level == "n5" else {}
    stories = []
    for index, start in enumerate(starts):
        track = start["id"]
        if track in reviewed:
            story = dict(reviewed[track])
            story["topicId"] = start["topicId"]
            story["page"] = start["printedPage"]
            story["images"] = manifest["images"][str(track)] if str(track) in manifest["images"] else manifest["images"][track]
            stories.append(story)
            continue
        lines = segment_lines(pages_ocr, starts, index)
        japanese = extract_japanese(lines)
        original_chinese = extract_original_chinese(lines)
        vocab = extract_vocab(lines, book.word_count)
        raw = [line["text"] for line in lines]
        story_type = "dialogue" if any(line.get("speaker") for line in japanese) else "short"
        stories.append({
            "id": track,
            "topicId": start["topicId"],
            "page": start["printedPage"],
            "type": story_type,
            "title": story_title(track, japanese),
            "audio": f"T{track}.mp3",
            "images": manifest["images"].get(str(track), manifest["images"].get(track, [])),
            "japanese": japanese,
            "focus": [],
            "naturalChinese": original_chinese,
            "originalChinese": original_chinese,
            "vocab": vocab,
            "vocabRaw": raw[:80],
            "ocrText": "\n".join(raw),
            "reviewStatus": "OCR已整理",
        })

    # Supplement segment OCR with page-wide anchors. This recovers vocabulary numbers
    # that sit just above a detected audio marker or on rotated memorization charts.
    seen_numbers = {int(row[0]) for story in stories for row in story["vocab"]}
    starts_by_page: dict[int, list[dict]] = {}
    for start in starts:
        starts_by_page.setdefault(start["pdfPage"], []).append(start)
    story_by_id = {story["id"]: story for story in stories}
    for pdf_page, obj in pages_ocr.items():
        page_lines = []
        for line in obj.get("lines", []):
            item = dict(line)
            item["top"] = line_top(line)
            item["text"] = re.sub(r"\s+", " ", item["text"]).strip()
            if item["text"]:
                page_lines.append(item)
        page_lines.sort(key=lambda item: (item["top"], item["x"]))
        page_starts = sorted(starts_by_page.get(pdf_page, []), key=lambda item: item["y"])
        if not page_starts:
            continue
        for top, row in extract_vocab_with_top(page_lines, book.word_count):
            number = int(row[0])
            if number in seen_numbers:
                continue
            owner = page_starts[0]
            for candidate in page_starts:
                if candidate["y"] <= top:
                    owner = candidate
                else:
                    break
            story_by_id[owner["id"]]["vocab"].append(row)
            story_by_id[owner["id"]]["vocab"].sort(key=lambda item: int(item[0]))
            seen_numbers.add(number)
    return {
        "level": book.level,
        "label": book.level.upper(),
        "audioBase": f"assets/{book.level}/audio",
        "wordCount": book.word_count,
        "numberedWordCount": book.numbered_word_count,
        "reviewSummary": {
            "reviewed": sum(story["reviewStatus"] == "已校对" for story in stories),
            "ocrOrganized": sum(story["reviewStatus"] == "OCR已整理" for story in stories),
        },
        "topics": [topic.__dict__ for topic in book.topics],
        "stories": stories,
    }


def level_page_html(book: Book, page: str, title: str, topic_id: int | None = None) -> str:
    topic_attr = f' data-topic="{topic_id}"' if topic_id is not None else ""
    return f'''<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
    <link rel="icon" href="../../favicon.svg" type="image/svg+xml" />
    <link rel="alternate icon" href="../../favicon.ico" type="image/x-icon" />
    <link rel="stylesheet" href="../../styles.css?v=20260714-4" />
  </head>
  <body data-page="{page}" data-level="{book.level}" data-base="../.."{topic_attr}>
    <main id="app"></main>
    <script src="../../data/{book.level}-data.js"></script>
    <script src="../../state.js?v=20260714-4"></script>
    <script src="../../app.js?v=20260714-4"></script>
  </body>
</html>
'''


def write_site(book: Book) -> None:
    data = build_data(book)
    data_path = ROOT / "data" / f"{book.level}-data.js"
    data_path.write_text(
        "window.LEVEL_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    level_dir = ROOT / "levels" / book.level
    level_dir.mkdir(parents=True, exist_ok=True)
    (level_dir / "index.html").write_text(
        level_page_html(book, "level-home", f"{book.level.upper()} 首页 - 日本语学习站"), encoding="utf-8"
    )
    (level_dir / "topics.html").write_text(
        level_page_html(book, "topics", f"{book.level.upper()} 目录 - 日本语学习站"), encoding="utf-8"
    )
    (level_dir / "topic.html").write_text(
        level_page_html(book, "topic", f"{book.level.upper()} 学习内容 - 日本语学习站"), encoding="utf-8"
    )
    for topic in book.topics:
        (level_dir / f"topic-{topic.id:02d}.html").write_text(
            level_page_html(book, "topic", f"Topic {topic.id} {topic.title} - {book.level.upper()}", topic.id),
            encoding="utf-8",
        )
    print(f"{book.level}: wrote {len(data['stories'])} stories and {len(book.topics)} topic pages")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build N4/N5 scanned-book assets and OCR caches")
    parser.add_argument("level", choices=[*BOOKS, "all"])
    parser.add_argument("--write-site", action="store_true")
    args = parser.parse_args()
    selected = BOOKS.values() if args.level == "all" else [BOOKS[args.level]]
    for book in selected:
        if args.write_site:
            write_site(book)
        else:
            prepare(book)


if __name__ == "__main__":
    main()
