#!/usr/bin/env python3
"""Build and validate the source-image-free GitHub Pages artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

LEVELS = ("n1", "n2", "n3", "n4", "n5")
ROOT_FILES = (
    PurePosixPath("index.html"),
    PurePosixPath("favicon.svg"),
    PurePosixPath("favicon.ico"),
    PurePosixPath("styles.css"),
    PurePosixPath("state.js"),
    PurePosixPath("app.js"),
)
PLANNING_FILES = (
    PurePosixPath("levels/english/index.html"),
    PurePosixPath("levels/english/sample.html"),
    PurePosixPath("levels/japanese/index.html"),
)
DATA_FILES = {
    level: PurePosixPath(f"data/{level}-data.js") for level in LEVELS
}
DATA_VARIABLES = {
    "n1": "LEVEL_DATA",
    "n2": "LEVEL_DATA",
    "n3": "N3_DATA",
    "n4": "LEVEL_DATA",
    "n5": "LEVEL_DATA",
}
AUDIO_BASES = {
    "n1": PurePosixPath("assets/n1/audio"),
    "n2": PurePosixPath("assets/n2/audio"),
    "n3": PurePosixPath("assets/audio"),
    "n4": PurePosixPath("assets/n4/audio"),
    "n5": PurePosixPath("assets/n5/audio"),
}
AUDIO_SUFFIXES = {".mp3", ".m4a", ".aac", ".ogg", ".wav"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tif", ".tiff", ".svg", ".ico"}
TEXT_SUFFIXES = {".html", ".css", ".js", ".svg"}
TARGET_BYTES = 800 * 1024 * 1024
PAGES_LIMIT_BYTES = 1_000_000_000
GIB_BYTES = 1024 * 1024 * 1024

JS_ASSIGNMENT_RE = re.compile(
    r"\A\s*window\.([A-Za-z_$][\w$]*)\s*=\s*(.*)\s*;?\s*\Z",
    re.DOTALL,
)
CSS_URL_RE = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE | re.DOTALL)
CSS_IMPORT_RE = re.compile(
    r"@import\s+(?!url\()(['\"])(.*?)\1", re.IGNORECASE | re.DOTALL
)
LOCAL_MACHINE_PATH_RE = re.compile(
    r"(?i)(?:file://|/(?:Users|Volumes|home|private|tmp|var)/|(?<![A-Z0-9])[A-Z]:[\\/])"
)
IMAGE_REFERENCE_RE = re.compile(
    r"(?i)(?:[A-Z]:[\\/]|file://|(?:\.\.?/|/)?)[^\s\"'`()<>]+?"
    r"\.(?:png|jpe?g|gif|webp|bmp|tiff?|svg)(?:[?#][^\s\"'`()<>]*)?"
)
ORIGINAL_IMAGE_DIR_RE = re.compile(
    r"(?i)(?:assets/)?(?:entries|cards)/|assets/n[1-5]/(?:pages|entries)/|/pages/"
)
ROOT_URL_RE = re.compile(r"rootUrl\(\s*(['\"])([^'\"${}]+)\1\s*\)")
RUNTIME_PATH_RE = re.compile(
    r"(?P<path>(?:levels|data|assets)/[A-Za-z0-9_./${}-]+)"
)


class BuildError(RuntimeError):
    """A production artifact invariant was violated."""


class HtmlReferenceParser(HTMLParser):
    """Collect resource and navigation references without third-party parsers."""

    URL_ATTRIBUTES = {"href", "src", "poster", "data"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: list[str] = []
        self.inline_styles: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        del tag
        for name, value in attrs:
            if not value:
                continue
            lowered = name.lower()
            if lowered in self.URL_ATTRIBUTES:
                self.references.append(value)
            elif lowered == "srcset":
                for candidate in value.split(","):
                    url = candidate.strip().split(maxsplit=1)[0]
                    if url:
                        self.references.append(url)
            elif lowered == "style":
                self.inline_styles.append(value)

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.handle_starttag(tag, attrs)


def display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def require_project_file(relative: PurePosixPath) -> Path:
    source = ROOT.joinpath(*relative.parts)
    if source.is_symlink():
        raise BuildError(f"白名单源文件不得为符号链接：{relative.as_posix()}")
    if not source.is_file():
        raise BuildError(f"缺少正式运行文件：{relative.as_posix()}")
    try:
        source.resolve().relative_to(ROOT.resolve())
    except ValueError as error:
        raise BuildError(f"源文件越出项目目录：{relative.as_posix()}") from error
    return source


def destination_path(relative: PurePosixPath) -> Path:
    target = DIST.joinpath(*relative.parts)
    try:
        target.resolve(strict=False).relative_to(DIST.resolve())
    except ValueError as error:
        raise BuildError(f"发布路径越出 dist：{relative.as_posix()}") from error
    return target


def copy_required(relative: PurePosixPath) -> None:
    source = require_project_file(relative)
    target = destination_path(relative)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def reset_dist() -> None:
    expected = ROOT.resolve() / "dist"
    if DIST.is_symlink():
        raise BuildError("拒绝清空符号链接 dist/")
    if DIST.exists():
        if not DIST.is_dir():
            raise BuildError("dist 存在但不是目录，拒绝覆盖")
        if DIST.resolve() != expected:
            raise BuildError("dist 实际路径异常，拒绝清空")
        shutil.rmtree(DIST)
    DIST.mkdir(parents=False)


def parse_js_assignment(path: Path) -> tuple[str, dict[str, Any]]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise BuildError(f"数据文件不是 UTF-8：{display_path(path)}") from error
    match = JS_ASSIGNMENT_RE.match(text)
    if not match:
        raise BuildError(f"无法识别数据文件赋值格式：{display_path(path)}")
    variable, payload = match.groups()
    payload = payload.rstrip()
    if payload.endswith(";"):
        payload = payload[:-1].rstrip()
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as error:
        raise BuildError(f"数据 JSON 无效：{display_path(path)}：{error}") from error
    if not isinstance(data, dict):
        raise BuildError(f"数据顶层必须是对象：{display_path(path)}")
    return variable, data


def scrub_local_machine_paths(value: Any) -> int:
    """Blank audit-only machine paths in the dist copy, preserving source files."""

    removed = 0
    if isinstance(value, dict):
        for key, child in list(value.items()):
            if isinstance(child, str) and LOCAL_MACHINE_PATH_RE.search(child):
                value[key] = ""
                removed += 1
            else:
                removed += scrub_local_machine_paths(child)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            if isinstance(child, str) and LOCAL_MACHINE_PATH_RE.search(child):
                value[index] = ""
                removed += 1
            else:
                removed += scrub_local_machine_paths(child)
    return removed


def production_data(level: str) -> tuple[str, dict[str, Any], int, int]:
    relative = DATA_FILES[level]
    variable, data = parse_js_assignment(require_project_file(relative))
    expected_variable = DATA_VARIABLES[level]
    if variable != expected_variable:
        raise BuildError(
            f"{relative.as_posix()} 应赋值给 window.{expected_variable}，实际为 window.{variable}"
        )
    stories = data.get("stories")
    if not isinstance(stories, list):
        raise BuildError(f"{relative.as_posix()} 缺少 stories 数组")
    removed_images = 0
    for index, story in enumerate(stories):
        if not isinstance(story, dict):
            raise BuildError(f"{relative.as_posix()} stories[{index}] 不是对象")
        images = story.get("images")
        if isinstance(images, list):
            removed_images += len(images)
        elif images not in (None, []):
            removed_images += 1
        story["images"] = []
    removed_local_paths = scrub_local_machine_paths(data)
    return variable, data, removed_images, removed_local_paths


def write_production_data(
    level: str, variable: str, data: dict[str, Any]
) -> None:
    relative = DATA_FILES[level]
    target = destination_path(relative)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        data,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    )
    target.write_text(f"window.{variable} = {payload};\n", encoding="utf-8")


def topic_page_paths(level: str, data: dict[str, Any]) -> set[PurePosixPath]:
    topics = data.get("topics")
    if not isinstance(topics, list) or not topics:
        raise BuildError(f"{level.upper()} 数据缺少 topics")
    topic_ids: set[int] = set()
    for index, topic in enumerate(topics):
        if not isinstance(topic, dict):
            raise BuildError(f"{level.upper()} topics[{index}] 不是对象")
        topic_id = topic.get("id")
        if not isinstance(topic_id, int) or topic_id <= 0:
            raise BuildError(f"{level.upper()} topics[{index}] id 无效：{topic_id!r}")
        if topic_id in topic_ids:
            raise BuildError(f"{level.upper()} Topic id 重复：{topic_id}")
        topic_ids.add(topic_id)
    base = PurePosixPath("levels") / level
    pages = {
        base / "index.html",
        base / "topics.html",
        base / "topic.html",
    }
    pages.update(base / f"topic-{topic_id:02d}.html" for topic_id in topic_ids)
    return pages


def audio_paths(level: str, data: dict[str, Any]) -> set[PurePosixPath]:
    expected_base = AUDIO_BASES[level]
    raw_base = data.get("audioBase")
    if raw_base is None and level == "n3":
        raw_base = expected_base.as_posix()
    if raw_base != expected_base.as_posix():
        raise BuildError(
            f"{level.upper()} audioBase 应为 {expected_base.as_posix()}，实际为 {raw_base!r}"
        )
    stories = data.get("stories")
    if not isinstance(stories, list):
        raise BuildError(f"{level.upper()} 数据缺少 stories")
    result: set[PurePosixPath] = set()
    seen_story_ids: set[str] = set()
    for index, story in enumerate(stories):
        if not isinstance(story, dict):
            raise BuildError(f"{level.upper()} stories[{index}] 不是对象")
        story_id = str(story.get("id", ""))
        if not story_id:
            raise BuildError(f"{level.upper()} stories[{index}] 缺少 id")
        if story_id in seen_story_ids:
            raise BuildError(f"{level.upper()} Story id 重复：{story_id}")
        seen_story_ids.add(story_id)
        audio = story.get("audio")
        if not isinstance(audio, str) or not audio:
            raise BuildError(f"{level.upper()} Story {story_id} 缺少音频引用")
        audio_path = PurePosixPath(audio)
        if audio_path.is_absolute() or audio_path.name != audio or ".." in audio_path.parts:
            raise BuildError(f"{level.upper()} Story {story_id} 音频路径不安全：{audio!r}")
        if audio_path.suffix.lower() not in AUDIO_SUFFIXES:
            raise BuildError(f"{level.upper()} Story {story_id} 音频扩展名无效：{audio!r}")
        result.add(expected_base / audio_path)
    return result


def expected_manifest(
    data_by_level: dict[str, dict[str, Any]]
) -> tuple[set[PurePosixPath], dict[str, set[PurePosixPath]]]:
    manifest = set(ROOT_FILES) | set(PLANNING_FILES) | set(DATA_FILES.values())
    audio_by_level: dict[str, set[PurePosixPath]] = {}
    for level in LEVELS:
        data = data_by_level[level]
        manifest.update(topic_page_paths(level, data))
        paths = audio_paths(level, data)
        audio_by_level[level] = paths
        manifest.update(paths)
    return manifest, audio_by_level


def local_reference_target(reference: str, owner: Path) -> Path | None:
    reference = reference.strip()
    if not reference or reference.startswith("#"):
        return None
    split = urlsplit(reference)
    if split.scheme:
        if split.scheme.lower() == "file":
            raise BuildError(f"禁止 file:// 引用：{display_path(owner)} -> {reference}")
        return None
    if reference.startswith("//"):
        return None
    raw_path = unquote(split.path)
    if not raw_path:
        return owner
    if "\\" in raw_path:
        raise BuildError(f"禁止反斜杠 URL：{display_path(owner)} -> {reference}")
    if raw_path.startswith("/"):
        raise BuildError(f"绝对站点路径不兼容仓库子目录：{display_path(owner)} -> {reference}")
    target = (owner.parent / raw_path).resolve(strict=False)
    try:
        target.relative_to(DIST.resolve())
    except ValueError as error:
        raise BuildError(f"引用越出 dist：{display_path(owner)} -> {reference}") from error
    if raw_path.endswith("/") or target.is_dir():
        target /= "index.html"
    return target


def validate_reference(reference: str, owner: Path) -> None:
    target = local_reference_target(reference, owner)
    if target is not None and not target.is_file():
        raise BuildError(f"缺失本地引用：{display_path(owner)} -> {reference}")


def css_references(text: str) -> Iterable[str]:
    for match in CSS_URL_RE.finditer(text):
        yield match.group(2).strip()
    for match in CSS_IMPORT_RE.finditer(text):
        yield match.group(2).strip()


def validate_html_and_css_references() -> None:
    for html_path in sorted(DIST.rglob("*.html")):
        parser = HtmlReferenceParser()
        try:
            parser.feed(html_path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, ValueError) as error:
            raise BuildError(f"HTML 无法解析：{display_path(html_path)}") from error
        for reference in parser.references:
            validate_reference(reference, html_path)
        for inline_style in parser.inline_styles:
            for reference in css_references(inline_style):
                validate_reference(reference, html_path)
    for css_path in sorted(DIST.rglob("*.css")):
        try:
            text = css_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            raise BuildError(f"CSS 不是 UTF-8：{display_path(css_path)}") from error
        for reference in css_references(text):
            validate_reference(reference, css_path)


def validate_root_runtime_reference(reference: str, owner: Path) -> None:
    if not reference or reference.startswith(("http://", "https://", "//")):
        return
    if reference.startswith("/"):
        raise BuildError(f"运行代码含绝对站点路径：{display_path(owner)} -> {reference}")
    target = DIST.joinpath(*PurePosixPath(reference).parts)
    if not target.exists():
        raise BuildError(f"运行代码引用缺失：{display_path(owner)} -> {reference}")


def validate_javascript_references() -> None:
    for js_path in sorted(DIST.rglob("*.js")):
        text = js_path.read_text(encoding="utf-8")
        for match in ROOT_URL_RE.finditer(text):
            validate_root_runtime_reference(match.group(2), js_path)
        for match in RUNTIME_PATH_RE.finditer(text):
            reference = match.group("path")
            if "${name}" in reference:
                for level in LEVELS:
                    directory = reference.replace("${level}", level).split("${name}", 1)[0]
                    validate_root_runtime_reference(directory, js_path)
                continue
            if "${level}" in reference:
                expansion_levels = LEVELS
                if reference.startswith("assets/${level}/audio"):
                    expansion_levels = ("n1", "n2", "n4", "n5")
                for level in expansion_levels:
                    validate_root_runtime_reference(reference.replace("${level}", level), js_path)
                continue
            validate_root_runtime_reference(reference, js_path)


def validate_forbidden_content() -> None:
    for path in sorted(DIST.rglob("*")):
        if path.is_symlink():
            raise BuildError(f"dist 不得包含符号链接：{display_path(path)}")
        if not path.is_file():
            continue
        relative = PurePosixPath(path.relative_to(DIST).as_posix())
        suffix = path.suffix.lower()
        if suffix in IMAGE_SUFFIXES and relative not in {
            PurePosixPath("favicon.svg"),
            PurePosixPath("favicon.ico"),
        }:
            raise BuildError(f"dist 包含原图或其他图片文件：{relative.as_posix()}")
        if suffix not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            raise BuildError(f"文本文件不是 UTF-8：{relative.as_posix()}") from error
        if LOCAL_MACHINE_PATH_RE.search(text):
            raise BuildError(f"dist 含本机绝对路径或 file://：{relative.as_posix()}")
        if ORIGINAL_IMAGE_DIR_RE.search(text):
            raise BuildError(f"dist 含原书图片目录引用：{relative.as_posix()}")
        for match in IMAGE_REFERENCE_RE.finditer(text):
            reference = match.group(0).split("?", 1)[0].split("#", 1)[0]
            normalized = reference.replace("\\", "/")
            if normalized == "favicon.svg" or normalized.endswith("/favicon.svg"):
                continue
            raise BuildError(
                f"dist 含图片扩展名引用：{relative.as_posix()} -> {match.group(0)}"
            )


def load_dist_data() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for level in LEVELS:
        relative = DATA_FILES[level]
        path = destination_path(relative)
        if not path.is_file():
            raise BuildError(f"dist 缺少数据文件：{relative.as_posix()}")
        variable, data = parse_js_assignment(path)
        if variable != DATA_VARIABLES[level]:
            raise BuildError(f"dist 数据变量错误：{relative.as_posix()}")
        stories = data.get("stories")
        if not isinstance(stories, list):
            raise BuildError(f"dist 数据缺少 stories：{relative.as_posix()}")
        for story in stories:
            if not isinstance(story, dict) or story.get("images") != []:
                story_id = story.get("id") if isinstance(story, dict) else "?"
                raise BuildError(f"{level.upper()} Story {story_id} 的 images 必须为 []")
        result[level] = data
    return result


def validate_exact_manifest(expected: set[PurePosixPath]) -> None:
    actual = {
        PurePosixPath(path.relative_to(DIST).as_posix())
        for path in DIST.rglob("*")
        if path.is_file()
    }
    missing = sorted(expected - actual, key=str)
    extra = sorted(actual - expected, key=str)
    if missing or extra:
        details: list[str] = []
        if missing:
            details.append("缺少：" + ", ".join(path.as_posix() for path in missing[:20]))
        if extra:
            details.append("多余：" + ", ".join(path.as_posix() for path in extra[:20]))
        raise BuildError("dist 白名单不一致；" + "；".join(details))


def validate_dist() -> tuple[dict[str, dict[str, Any]], dict[str, set[PurePosixPath]]]:
    if not DIST.is_dir() or DIST.is_symlink():
        raise BuildError("dist 不存在或不是安全目录")
    data_by_level = load_dist_data()
    manifest, audio_by_level = expected_manifest(data_by_level)
    validate_exact_manifest(manifest)
    validate_forbidden_content()
    validate_html_and_css_references()
    validate_javascript_references()
    return data_by_level, audio_by_level


def category_for(relative: PurePosixPath) -> str:
    if relative.parts[:2] == ("assets", "audio"):
        return "audio_n3"
    if len(relative.parts) >= 3 and relative.parts[0] == "assets" and relative.parts[2] == "audio":
        level = relative.parts[1]
        if level in LEVELS:
            return f"audio_{level}"
    if relative.parts and relative.parts[0] == "data":
        return "data"
    suffix = relative.suffix.lower()
    if suffix == ".html":
        return "html"
    if suffix == ".css":
        return "css"
    if suffix == ".js":
        return "javascript"
    return "other"


def byte_digest_and_sizes() -> tuple[str, dict[str, tuple[int, int]]]:
    digest = hashlib.sha256()
    counts: dict[str, int] = defaultdict(int)
    sizes: dict[str, int] = defaultdict(int)
    for path in sorted((item for item in DIST.rglob("*") if item.is_file()), key=str):
        relative = PurePosixPath(path.relative_to(DIST).as_posix())
        category = category_for(relative)
        counts[category] += 1
        size = path.stat().st_size
        sizes[category] += size
        encoded_name = relative.as_posix().encode("utf-8")
        digest.update(len(encoded_name).to_bytes(4, "big"))
        digest.update(encoded_name)
        digest.update(size.to_bytes(8, "big"))
        with path.open("rb") as handle:
            while chunk := handle.read(1024 * 1024):
                digest.update(chunk)
    return digest.hexdigest(), {
        category: (counts[category], sizes[category])
        for category in sorted(set(counts) | set(sizes))
    }


def mib(size: int) -> str:
    return f"{size / 1024 / 1024:.2f} MiB"


def print_summary() -> int:
    digest, categories = byte_digest_and_sizes()
    total_files = sum(count for count, _ in categories.values())
    total_bytes = sum(size for _, size in categories.values())
    code_categories = ("html", "css", "javascript", "data")
    code_files = sum(categories.get(name, (0, 0))[0] for name in code_categories)
    code_bytes = sum(categories.get(name, (0, 0))[1] for name in code_categories)

    print("dist 构建与引用检查通过")
    print(f"文件总数：{total_files}")
    print(f"总字节数：{total_bytes}")
    print(f"总体积：{mib(total_bytes)}")
    print(f"代码与数据：{code_files} 个文件，{mib(code_bytes)}")
    labels = {
        "html": "  HTML",
        "css": "  CSS",
        "javascript": "  JavaScript",
        "data": "  Data",
    }
    for category in code_categories:
        count, size = categories.get(category, (0, 0))
        print(f"{labels[category]}：{count} 个文件，{mib(size)}")
    for level in LEVELS:
        count, size = categories.get(f"audio_{level}", (0, 0))
        print(f"{level.upper()} 音频：{count} 个文件，{mib(size)}")
    other_count, other_size = categories.get("other", (0, 0))
    print(f"其他资源：{other_count} 个文件，{mib(other_size)}")
    print(f"距离 800 MiB 目标余量：{mib(TARGET_BYTES - total_bytes)}")
    print(f"距离 1 GB 保守上限余量：{mib(PAGES_LIMIT_BYTES - total_bytes)}")
    print(f"距离 1 GiB 参考值余量：{mib(GIB_BYTES - total_bytes)}")
    print(f"可重复构建摘要 SHA-256：{digest}")
    return total_bytes


def build() -> None:
    reset_dist()
    for relative in ROOT_FILES:
        copy_required(relative)

    data_by_level: dict[str, dict[str, Any]] = {}
    removed_images = 0
    removed_local_paths = 0
    for level in LEVELS:
        variable, data, image_count, local_path_count = production_data(level)
        write_production_data(level, variable, data)
        data_by_level[level] = data
        removed_images += image_count
        removed_local_paths += local_path_count

    manifest, audio_by_level = expected_manifest(data_by_level)
    page_files = manifest - set(ROOT_FILES) - set(DATA_FILES.values())
    for relative in sorted(page_files - set().union(*audio_by_level.values()), key=str):
        copy_required(relative)
    for level in LEVELS:
        for relative in sorted(audio_by_level[level], key=str):
            copy_required(relative)

    print(f"生产数据已清除原图路径：{removed_images} 条")
    print(f"生产数据已清除本机审计路径：{removed_local_paths} 条")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="构建不含原书图片的 GitHub Pages dist/ 发布产物"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="不重新构建，只检查现有 dist/ 并输出体积",
    )
    args = parser.parse_args()
    try:
        if not args.check_only:
            build()
        validate_dist()
        total_bytes = print_summary()
        if total_bytes >= PAGES_LIMIT_BYTES:
            raise BuildError("dist 达到或超过 1 GB GitHub Pages 保守上限")
        if total_bytes >= TARGET_BYTES:
            raise BuildError("dist 达到或超过 800 MiB 阶段目标，请停止后续操作")
    except (BuildError, OSError) as error:
        print(f"构建失败：{error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
