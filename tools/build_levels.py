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
    content_first_pdf_page: int
    content_last_pdf_page: int
    printed_page_offset: int
    topics: tuple[Topic, ...]
    marker_overrides: dict[int, tuple[int, int]]


def make_topics(rows: list[tuple[str, str, str, int]]) -> tuple[Topic, ...]:
    return tuple(Topic(index, *row) for index, row in enumerate(rows, start=1))


BOOKS = {
    "n5": Book(
        level="n5",
        pdf=SOURCE_ROOT / "5.pdf",
        audio_url="https://bookclub2.japantimes.co.jp/download/files/Best_Vocab_N5.zip",
        track_count=373,
        word_count=1000,
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
        "starts": starts,
        "images": images_by_track,
    }
    path = work_dir(book) / "manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{book.level}: prepared {len(starts)} tracks and {len(set(s['pdfPage'] for s in starts))} source pages")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build N4/N5 scanned-book assets and OCR caches")
    parser.add_argument("level", choices=[*BOOKS, "all"])
    args = parser.parse_args()
    selected = BOOKS.values() if args.level == "all" else [BOOKS[args.level]]
    for book in selected:
        prepare(book)


if __name__ == "__main__":
    main()
