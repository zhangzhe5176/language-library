#!/usr/bin/env python3
"""Generate the shared production HTML shells without changing level content data."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEVELS = ("n1", "n2", "n3", "n4", "n5")
ASSET_VERSION = "20260714-3"


def load_level_data(level: str) -> dict:
    path = ROOT / "data" / f"{level}-data.js"
    text = path.read_text(encoding="utf-8")
    wrapper = "N3_DATA" if level == "n3" else "LEVEL_DATA"
    match = re.fullmatch(rf"window\.{wrapper}\s*=\s*(\{{.*\}});\s*", text, re.DOTALL)
    if not match:
        raise ValueError(f"Unexpected data wrapper: {path}")
    return json.loads(match.group(1))


def level_page_html(level: str, page: str, title: str, topic_id: int | None = None) -> str:
    topic_attr = f' data-topic="{topic_id}"' if topic_id is not None else ""
    return f'''<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
    <link rel="icon" href="data:," />
    <link rel="stylesheet" href="../../styles.css?v={ASSET_VERSION}" />
  </head>
  <body data-page="{page}" data-level="{level}" data-base="../.."{topic_attr}>
    <main id="app"></main>
    <script src="../../data/{level}-data.js"></script>
    <script src="../../state.js?v={ASSET_VERSION}"></script>
    <script src="../../app.js?v={ASSET_VERSION}"></script>
  </body>
</html>
'''


def write_level_pages(level: str, data: dict | None = None) -> list[Path]:
    data = data or load_level_data(level)
    label = level.upper()
    level_dir = ROOT / "levels" / level
    level_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        level_dir / "index.html": level_page_html(level, "level-home", f"{label} 学习首页 · Language Library"),
        level_dir / "topics.html": level_page_html(level, "topics", f"{label} Topic 目录 · Language Library"),
        level_dir / "topic.html": level_page_html(level, "topic", f"{label} 学习内容 · Language Library"),
    }
    for topic in data["topics"]:
        outputs[level_dir / f"topic-{topic['id']:02d}.html"] = level_page_html(
            level,
            "topic",
            f"Topic {topic['id']} {topic['title']} · {label}",
            topic["id"],
        )
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8")
    return list(outputs)


def main() -> None:
    for level in LEVELS:
        outputs = write_level_pages(level)
        print(f"{level}: wrote {len(outputs)} production page shells")


if __name__ == "__main__":
    main()
