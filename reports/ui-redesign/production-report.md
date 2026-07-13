# Language Library 正式全站改造报告

## 1. 完成范围

本次将 `prototype/ui-v2/` 已验收的视觉方向应用到正式网站，同时保留原型目录作为设计对照。正式站继续使用纯 HTML、CSS、JavaScript，不依赖构建工具、npm、外部 CDN 或服务器功能。

主要修改如下：

- `index.html`：改为只负责语言分流的正式门户。
- `levels/japanese/index.html`：新增日语独立首页。
- `levels/n1/` 至 `levels/n5/`：统一等级首页、Topic 目录页和学习页。
- `app.js`：统一门户、日语首页、等级、目录和学习页渲染逻辑。
- `state.js`：统一学习状态存储、等级隔离和旧状态迁移。
- `styles.css`：正式应用 UI v2 响应式视觉、深色模式和克制动画。
- `tools/site_templates.py`、`tools/build_levels.py`、`tools/build_n3.py`：生成器同步到正式统一结构。
- `tests/site-state.test.js`、`tests/test_site_ui.py`、`tests/test_n5_sample.py`：扩展状态迁移、页面结构、资源和兼容测试。
- `reports/ui-redesign/production-screenshots/`：正式页面验收截图。

未修改 `data/`、`assets/`、N1–N5 内容数据、音频和原图；未修改或合并 `main`。

## 2. 最终信息架构

```text
/index.html
/levels/japanese/index.html
/levels/n1..n5/index.html
/levels/n1..n5/topics.html
/levels/n1..n5/topic.html?topic={topicId}&story={storyId}
```

原有 `topic-XX.html` 继续保留为兼容入口，但已改用同一套正式渲染逻辑；站内新链接统一指向 `topic.html`。全部链接和资源路径均为相对路径，可用于 GitHub Pages 子目录部署。

导航层级统一为：

- 门户：语言。
- 日语首页：语言、日语。
- 等级与学习页面：语言、日语、当前等级、Topics、学习。

## 3. N3 迁移实现

N3 已从 `data-page="n3-home"` 迁移为 `data-page="level-home" data-level="n3"`，与 N1、N2、N4、N5 共用 `app.js`、`state.js` 和 `styles.css`。

迁移保留了：

- `data/n3-data.js` 原始内容，不改写数据。
- `assets/audio/` 音频路径。
- `assets/entries/` 原书图片路径。
- 原有 `topic-01.html` 至 `topic-18.html` 兼容入口。
- 收藏、已学和最近学习记录。

真实浏览器已打开旧入口 `levels/n3/topic-01.html`，确认其渲染为统一学习页，音频为 `../../assets/audio/T1.mp3`，原图为 `../../assets/entries/T001_1.png`，无横向溢出或原型文案。

## 4. localStorage 兼容方案

新结构按等级隔离：

```text
languageLibrary:v2:{level}:learned
languageLibrary:v2:{level}:favorites
languageLibrary:v2:{level}:recent
languageLibrary:v2:{level}:legacy-migrated
```

首次读取某等级时会检查旧 key：

```text
{level}Learned
{level}Starred
{level}Recent
```

迁移规则：

- 已学和收藏采用并集合并、字符串化编号并去重。
- 已存在的新 `recent` 优先，不被旧记录覆盖。
- 旧 key 始终保留，不调用 `removeItem`。
- 新状态 JSON 无效、旧状态无效或写入失败时，不覆盖原记录，也不写完成标记。
- N1–N5 相同故事编号使用不同等级 key，不会互相串联。

自动测试已覆盖 N3 合并去重、旧记录保留、失败回退、新状态优先和跨等级隔离。

## 5. 统计核对

统计由正式运行时从五个数据文件计算，日语首页 HTML 不重复硬编码统计数字。

| 等级 | Topics | 故事 | 词汇 |
|---|---:|---:|---:|
| N1 | 27 | 494 | 2571 |
| N2 | 23 | 452 | 2360 |
| N3 | 18 | 371 | 2014 |
| N4 | 13 | 262 | 1035 |
| N5 | 24 | 373 | 1136 |
| 合计 | 105 | 1952 | 9116 |

任务说明中的“合计 97 Topics”与五个分项之和不一致；实际数据与分项合计均为 **105 Topics**，正式页面和测试已按真实数据更正。

## 6. 功能验证

真实浏览器已验证：

- 门户进入日语首页，规划中语言没有无效链接。
- 日语首页进入 N1–N5，五个等级真实统计正确。
- 五个等级首页、Topic 目录和首末条学习页均可打开。
- 每个等级首条“上一篇”禁用、末条“下一篇”禁用，其他导航链接有效。
- 搜索、收藏筛选、已学筛选、进度、最近学习和继续学习有效。
- 中文与词汇可展开/收起。
- 原书图片可打开，关闭按钮、背景点击和 Escape 可关闭。
- 音频资源可加载到浏览器可播放状态，按钮包含加载、播放、暂停和失败提示逻辑；切换或离开文章会停止当前音频。
- 手机底部栏使用 `safe-area-inset-bottom`，390px 与 320px 滚动到页尾时分别保留约 31px 和 48px 内容间距，不遮挡正文或页尾操作。

## 7. 自动测试结果

- JavaScript 语法检查：10 个 `.js` 文件全部通过。
- 状态迁移测试：`site-state: all migration and isolation assertions passed`。
- Python 自动测试：31 项全部通过。
- 音频和原图路径：自动测试逐条确认存在。
- GitHub Pages 相对路径：自动测试确认正式页面没有根路径 `href="/"` 或 `src="/"`。
- 原型与开发说明文案：正式入口和运行时均未发现。

## 8. 浏览器响应式结果

对 17 个正式规范页面（门户、日语首页，以及 N1–N5 的首页、目录和学习页）在 5 种 viewport 下进行了 85 组真实浏览器检查。

| Viewport | `innerWidth` | HTML / Body `scrollWidth` | 主容器宽度 | 溢出元素 | 控制台错误 |
|---|---:|---:|---:|---:|---:|
| 1440 × 900 | 1440 | 1440 / 1440 | 1180 | 0 | 0 |
| 1024 × 768 | 1024 | 1024 / 1024 | 942.09 | 0 | 0 |
| 768 × 1024 | 768 | 768 / 768 | 706.56 | 0 | 0 |
| 390 × 844 | 390 | 390 / 390 | 358 | 0 | 0 |
| 320 × 568 | 320 | 320 / 320 | 288 | 0 | 0 |

全部组合满足 `document.documentElement.scrollWidth === window.innerWidth` 和 `document.body.scrollWidth === window.innerWidth`，无内容裁切、失效链接、控制台错误、缺失数据或开发说明文字。

## 9. 截图

截图目录：`reports/ui-redesign/production-screenshots/`

- `portal-desktop.png`：1440 × 900
- `portal-mobile.png`：390 × 844
- `japanese-desktop.png`：1440 × 900
- `japanese-mobile.png`：390 × 844
- `n1-home-desktop.png`：1440 × 900
- `n3-home-desktop.png`：1440 × 900
- `topics-desktop.png`：1440 × 900
- `lesson-desktop.png`：1440 × 900
- `lesson-mobile.png`：390 × 844

## 10. 已知限制

- 学习状态仍保存在当前浏览器 localStorage，不进行跨设备同步。
- 本阶段没有修改 GitHub Pages 设置、没有合并 `main`、没有发布网站。
- 浏览器自动化环境会阻止真正输出音频声音；已通过浏览器 `readyState`、自动资源路径检查以及播放成功/失败状态逻辑验证音频接入。

## 11. 下一步上线步骤

1. 用户检查本报告和正式截图。
2. 在目标部署环境进行一次人工音频试听与深色模式目视验收。
3. 验收通过后再决定是否将 `feature/n5-sample` 合并到 `main`。
4. 合并后再单独执行 GitHub Pages 发布；本阶段未进行发布操作。
