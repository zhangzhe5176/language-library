# TASK_STATUS

## 当前目标

在不影响线上 `main` 的前提下，一次性完成 N5 全部 24 个 Topic 与 N4 全部 13 个 Topic，完成全站验证和用户最终确认后再发布。

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

- 将 OCR 页面内容转换为结构化学习数据并生成全部章节页面。
- 完成 N5 词条 14–1000、全部 24 个 Topic。
- 完成 N4 词条 1–1200、全部 13 个 Topic。
- 执行 N3 回归、全站数据和浏览器验证。
- 用户最终确认后再决定合并与发布。

## 关键文件

- 来源：`/Users/wise/Documents/图书电子化/references/5.pdf`
- N4 来源：`/Users/wise/Documents/图书电子化/references/4.pdf`
- N3 参考构建器：`tools/build_n3.py`
- N3 数据结构：`data/n3-data.js`
- 当前分支：`feature/n5-sample`

## 发布边界

- 未经用户确认，不合并到 `main`，不推送未校对内容。
- 制作期间保留本地阶段提交，不发布中间版本。

## 验证结果

- `python3 -m unittest discover -s tests -p 'test_*.py'`：7 项通过。
- JavaScript 语法检查：`app.js`、`data/n5-data.js` 通过。
- 桌面浏览器：HTTP 200，8 张卡片、8 个音频控件、无控制台错误。
- 交互：搜索、收藏筛选正常；`T1.mp3` 实际播放成功。
- 320px 手机：页面宽度 320/320，无横向溢出、无控制台错误。
- 公共主题变量已合并为唯一配置块，8 项原有测试与新增构建测试通过。
- N5：373/373 条音频编号、185 张来源页匹配完成。
- N4：262/262 条音频编号、157 张来源页匹配完成。
- 特殊页面：N5 6 个、N4 1 个 OCR 漏标位置均已对照原页固定并纳入测试。
