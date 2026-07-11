# N5 内容修复前状态

- 检查时间：2026-07-11（Asia/Tokyo）
- 项目：`/Users/wise/Documents/图书电子化/language-library`
- 当前分支：`feature/n5-sample`
- 当前提交：`3ac159bf82fd0fd0fcd3dd3e358f428274a34d35`
- 工作区状态：干净，无未提交文件。
- 远程：`origin = https://github.com/zhangzhe5176/language-library.git`
- 与 `origin/main`：本地领先 4 个提交，落后 0 个提交。
- 上游关联：当前功能分支尚未关联远程分支。
- 分支判断：当前已是合适的 N5 功能分支，因此继续使用，不另建分支。

## 关键文件

- N5 数据：`data/n5-data.js`
- N5/N4 通用构建脚本：`tools/build_levels.py`
- OCR 脚本：`tools/ocr_vision.swift`
- N5 既有测试：`tests/test_n5_sample.py`、`tests/test_level_builder.py`
- N5 原书：`/Users/wise/Documents/图书电子化/references/5.pdf`
- N5 原页图片：`assets/n5/pages/`
- N5 音频：`assets/n5/audio/`

## N3 参考流程

- N3 数据位于 `data/n3-data.js`，故事字段为 `id/topicId/page/type/title/audio/images/japanese/focus/naturalChinese/originalChinese/vocab/vocabRaw/ocrText/reviewStatus`。
- 历史 `tools/patch_topic*.py` 使用按 story id 建立的 `PATCHES` 字典，完整覆盖标题、类型、日文、学习重点、两种中文和五列词汇，最后写回数据并将通过复核的条目标记为“已校对”。
- 后续词汇修复脚本按编号定位并替换单行词汇。部分旧脚本仍硬编码旧项目路径，本轮 N5 脚本改用仓库相对路径。
- 本轮明确不修改 N3，只把它作为字段形式和中文词性缩写的参考。

## 修复边界

- 本轮只处理 N5 Topic 1（story 1–8）。
- 不修改 N3、N4，不合并 `main`，不强推，不改写历史，不删除来源或 OCR 追溯数据。
