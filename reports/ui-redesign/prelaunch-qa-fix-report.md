# Language Library 上线前 QA 修复报告

日期：2026-07-14

分支：`feature/n5-sample`

修复基线：`b91ee4eff0557d55040bbfb8ce126a31968593ea`

## 结论

本轮指定的 QA-01、QA-02、QA-03、QA-06、QA-08 均已处理，自动测试、静态资源检查和针对性浏览器回归均通过。未发现新的 Critical 或 High 问题。

最终建议：**Go**。

该建议仅针对当前 `feature/n5-sample` 的上线前质量状态；本轮未合并 `main`，也未发布 GitHub Pages。

## QA-01：N3 空白第二张原图

### 最终判断

`T168_2.png` 和 `T199_2.png` 对应原书中真实存在的纯空白过渡页，但它们不属于 Story 168 或 Story 199 的有效内容。问题本质是提取流程从当前 Story 起始页遍历到下一 Story 起始页时，将 Topic 之间的空白页误关联为当前 Story 的第二张原图。

判断依据：

- N3 原始来源：`/Users/wise/Documents/图书电子化/references/3.pdf`。
- Story 168 正文位于书内第 123 页（PDF 第 125 页）；书内第 124 页（PDF 第 126 页）为纯空白页，之后是 Topic 9 分隔页和 Story 169。
- Story 199 正文位于书内第 145 页（PDF 第 147 页）；书内第 146 页（PDF 第 148 页）为纯空白页，之后是 Topic 11 分隔页和 Story 200。
- 两张第二页图片尺寸均为 1043 × 1470，内容完全一致；亮度检测为单一值，没有文字、图表或其他有效原书内容。
- `tools/build_n3.py` 的历史裁切逻辑按 Story 起止页跨页提取，未判断中间页是否为 Topic 间空白页；`tools/patch_topics8_10.py` 中的旧覆盖配置随后保留了这两张空白图引用。

处理方式：

- `data/n3-data.js` 中 Story 168 只保留 `assets/entries/T168_1.png`。
- `data/n3-data.js` 中 Story 199 只保留 `assets/entries/T199_1.png`。
- 同步修正 `tools/patch_topics8_10.py` 的图片覆盖配置，避免再次执行该修复脚本时恢复错误引用。
- `assets/entries/T168_2.png` 和 `assets/entries/T199_2.png` 保留为追溯材料，未删除。

回归结果：

- Story 168、Story 199 均只显示 1 张有效原图，图片加载正常，弹窗可打开和关闭。
- Story 167、169、198、200 的原图加载正常。
- Story 168 ↔ 169、Story 198 ↔ 199 ↔ 200 的上一篇和下一篇实际跳转正常。
- 其他 N3 图片引用未受影响，全部数据资源存在性测试通过。

## QA-02：旧英语页面

`levels/english/index.html` 和 `levels/english/sample.html` 已替换为统一正式样式的英语规划中页面：

- 显示 `English / 英语`、`规划中` 和返回语言门户按钮。
- 两个旧 URL 均可直接打开，不依赖服务器重写或跳转规则。
- 不再加载旧课程数据或旧样张脚本。
- 不显示“本地版”“旧样张”“测试版”或开发说明。
- 不提供不存在的学习入口。
- 门户中的英语卡片仍为不可点击的 `ARTICLE`，状态为“规划中”。

## QA-03：favicon

- 新增项目自有的 `favicon.svg`，不依赖外部资源。
- 根首页、日语首页、英语两个旧 URL，以及 N1–N5 的 120 个正式页面均显式引用本地图标，共检查 124 个正式页面。
- 同步更新 `tools/site_templates.py`、`tools/build_levels.py` 和 `tools/build_n3.py`，后续重新生成页面时会保留 favicon。
- 浏览器访问记录显示 `GET /favicon.svg` 返回 200，未再请求 `/favicon.ico`，因此未额外添加兼容 ICO 文件。

## QA-06：未使用代码

确认 `app.js` 中 `topicUrl()` 没有调用点后已删除。新增自动断言，防止该未使用函数再次出现。

## QA-08：状态文档

`TASK_STATUS.md` 已按当前实际进度修正：

- 当前分支为 `feature/n5-sample`。
- 正式站统一改造已完成。
- 本轮上线前 QA 修复和针对性回归已完成。
- 下一步为等待最终上线决定。
- 已删除“等待提交推送”等过期状态描述，历史内容未整体重写。

## 针对性回归结果

### 自动测试

- Python：35 项全部通过。
- 状态迁移与等级隔离测试：全部通过。
- JavaScript 语法检查：10 个文件全部通过。
- 正式页面本地引用：124 个页面、620 个显式本地引用，缺失 0。
- N1–N5 全部音频和原图存在性测试：通过。
- `git diff --check`：通过。

### 浏览器回归

共检查 31 个页面/viewport 组合：

| viewport | 页面组合数 | 最大 `documentElement.scrollWidth` | 最大 `body.scrollWidth` | 结果 |
| --- | ---: | ---: | ---: | --- |
| 320 × 568 | 6 | 320 | 320 | 通过 |
| 390 × 844 | 6 | 390 | 390 | 通过 |
| 768 × 1024 | 5 | 768 | 768 | 通过 |
| 1440 × 900 | 14 | 1440 | 1440 | 通过 |

实际检查包括：

- 门户、英语 `index.html`、英语 `sample.html`。
- N3 Story 168、199 及相邻 Story 167、169、198、200。
- N1–N5 各等级至少一条学习页。
- Story 168 和 199 原图弹窗打开、关闭及有效图片路径。
- 搜索“会費”只显示 Topic 8。
- 收藏筛选和已学筛选均正确显示 Topic 8；测试后收藏和已学状态已恢复。
- 最近学习和继续学习正确指向 N3 Story 168。
- 页面无横向溢出、无内容越界、无已加载图片失败。
- 浏览器控制台错误和警告均为 0。
- favicon、抽查音频和抽查原图的 HTTP 请求均返回 200 或缓存命中 304，没有 404。

## 修改范围

- N3 图片引用：`data/n3-data.js`、`tools/patch_topics8_10.py`。
- 英语规划中页面：`levels/english/index.html`、`levels/english/sample.html`。
- favicon：`favicon.svg`、根首页、日语首页、N1–N5 正式页面及三个页面生成工具。
- 正式运行时代码：`app.js`、`styles.css`。
- 自动测试：`tests/test_site_ui.py`、`tests/test_n5_sample.py`。
- 项目状态：`TASK_STATUS.md`。

除 N3 Story 168 和 Story 199 的图片引用外，本轮未修改 N1–N5 内容数据；未删除任何图片、音频或追溯材料。

## 保留的非阻断维护项

以下问题按任务要求未处理，不阻断本轮 Go 建议：

- QA-04：86 个未引用图片，后续确认用途后再整理。
- QA-05：重复图片，后续建立明确的资源去重策略后再处理。
- QA-07：测试文件中的成功提示 `console.log`，仅出现在测试脚本中。
- QA-09：`.build/` 缓存，本轮未清理、未修改。

## Git 边界

- 当前工作分支：`feature/n5-sample`。
- `main` 与 `origin/main` 均保持在 `22ed78927d4b29d5bf5fbf4e9d349a566d1e05aa`，未修改、未合并。
- 未发布 GitHub Pages，未强制推送，未改写历史。
