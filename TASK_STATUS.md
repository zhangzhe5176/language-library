# TASK_STATUS

## 当前目标

在不影响线上 `main` 的前提下，使用 `references/5.pdf` 制作 N5 Topic 1 样章；经人工确认后，再决定是否批量处理并推送 GitHub Pages。

## 已完成

- 已确认 GitHub 账户 `zhangzhe5176` 在本机可用。
- 已将 `zhangzhe5176/language-library` 检出到本目录。
- 已建立工作分支 `feature/n5-sample`。
- 已确认 N5 来源为 `/Users/wise/Documents/图书电子化/references/5.pdf`，共 259 页，无可提取文本层。

## 已完成样章

- 已定位 Topic 1「あいさつ1」：PDF 第 17–20 页，学习内容为词条 1–13。
- 已加入 8 段已校对对话、中文理解、原书中文、词汇和 3 张原页对照图。
- 已从出版社官方免费下载包中提取 Topic 1 的 `T1.mp3`–`T8.mp3`。
- 已将公共页面脚本改为按 `data-level` 读取 N3/N5 数据、路径和本地学习状态。
- 已新增 N5 首页、目录和 Topic 1 页面，并在门户加入 N5 入口。
- 已修复 320px 手机宽度下的双栏溢出和 favicon 404。

## 未完成

- 用户审阅 Topic 1 样章内容与显示效果。
- 用户确认后推送工作分支；是否合并到 `main` 并发布，仍需单独确认。
- 样章通过后，按 Topic 2–24 分批制作整本 N5。

## 关键文件

- 来源：`/Users/wise/Documents/图书电子化/references/5.pdf`
- N3 参考构建器：`tools/build_n3.py`
- N3 数据结构：`data/n3-data.js`
- 当前分支：`feature/n5-sample`

## 发布边界

- 未经用户确认，不合并到 `main`，不推送未校对内容。

## 验证结果

- `python3 -m unittest discover -s tests -p 'test_*.py'`：7 项通过。
- JavaScript 语法检查：`app.js`、`data/n5-data.js` 通过。
- 桌面浏览器：HTTP 200，8 张卡片、8 个音频控件、无控制台错误。
- 交互：搜索、收藏筛选正常；`T1.mp3` 实际播放成功。
- 320px 手机：页面宽度 320/320，无横向溢出、无控制台错误。
