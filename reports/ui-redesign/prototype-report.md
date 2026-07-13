# language-library 网站改版第一阶段原型报告

## 1. 新版信息架构

新版信息架构分为四层：

1. 根首页 `/index.html`
   - 只展示语言入口：日语、英语、韩语、法语、西班牙语。
   - 不直接展示 JLPT 等级和学习内容，降低首页信息密度。
2. 日语独立首页 `/levels/japanese/index.html`
   - 展示 N1、N2、N3、N4、N5 五个等级。
   - 每个等级显示真实 Topic 数、故事数、词汇数、学习进度、收藏数和最近学习入口。
3. 等级首页
   - N1–N5 使用统一结构：等级介绍、学习进度、继续学习、Topic 入口、搜索、收藏入口。
4. Topic 学习页
   - 展示日文内容、中文理解、词汇、音频、原书图片、收藏、已学状态、上一篇/下一篇和返回目录。

## 2. 设计目标

- 让网站从“资料列表”转为“长期学习产品”。
- 首页只做语言分流，日语学习路径进入独立首页承载。
- 强调进度、连续学习、收藏和最近学习，减少管理后台感。
- 保持纯 HTML、CSS、JavaScript，兼容 GitHub Pages。
- 不引入 React、Vue、Tailwind、npm 依赖、外部 CDN 或服务器功能。

## 3. 视觉规范

- 整体风格：现代、克制、清晰，适合长期阅读和复习。
- 日语氛围：通过日文字体、纸张色、墨色、低饱和暖色和细微层次表达，不堆砌樱花、富士山等符号。
- 主要界面语言：中文辅助说明 + 日文内容优先。
- 背景：浅暖纸色渐变，深色模式下转为低亮度暖黑。
- 组件：大圆角卡片、轻阴影、细边框、柔和进场动画。

## 4. 字体层级

- 页面主标题：`clamp(2.1rem, 4.3vw, 3.8rem)`，在桌面端保留视觉重点，并降低长标题破坏布局的风险。
- 手机端主标题：`clamp(1.9rem, 8.7vw, 2.6rem)`；320px 下固定为 `1.78rem`。
- 学习页标题：`clamp(1.65rem, 2.8vw, 2.65rem)`，明显小于门户和等级页标题。
- 区块标题：`clamp(1.55rem, 3vw, 2.4rem)`。
- 卡片标题：约 `1.08rem`，配合等级、Topic 或语言标签。
- 日文正文：使用 serif 类日文字体，`clamp(1.28rem, 2vw, 1.8rem)`，行高约 `1.82`。
- 辅助文字：低对比灰色，行高约 `1.78`。

## 5. 间距与布局规则

- 页面最大宽度：`1180px`。
- 桌面端页面外边距：`26px–48px`。
- 手机端页面左右外边距：统一 `16px`。
- 卡片间距：`18px`。
- 主要布局：
  - 门户和等级首页：完整 Hero + 卡片网格；门户页使日语可用卡片占两列，其他语言明确标注“规划中”。
  - 学习页：桌面端主阅读区最大 `780px` + 右侧状态栏，移动端单列。
  - Topic 目录：桌面端三列，1024px 两列，手机端一列。

## 6. 卡片与按钮规范

- 卡片：
  - 圆角：`22px–30px`。
  - 边框：低透明度细线。
  - 阴影：轻层次，悬停时轻微上浮。
- 按钮：
  - 主按钮使用品牌渐变。
  - 次按钮使用半透明卡片底。
  - 状态按钮使用 chip 形态，支持 active 状态。
- 学习页底部操作栏：
  - 仅手机端显示。
  - 包含目录、播放、收藏、已学。

## 7. 颜色和状态规则

- 主品牌色：暖红棕，用于主按钮、标签和重点状态。
- 辅助色：
  - 深蓝：等级和音频状态。
  - 绿色：完成、学习进度。
  - 粉色：收藏。
  - 琥珀色：强调或提醒。
- 状态规则：
  - 已完成：绿色浅底。
  - 收藏：粉色浅底。
  - 学习中：进度条显示实际百分比。
  - 未完成：中性色 chip。

## 8. 动画规则

- 页面卡片进入：轻微上移淡入。
- 卡片悬停：上移 `2px–4px`，阴影增强。
- 按钮反馈：轻微上移。
- 音频播放状态：原型中使用轻微 pulse 动画表示播放中。
- 展开/收起：只做短淡入，不做复杂折叠动画。

## 9. 桌面端设计说明

- 1440px：Hero 左右分栏，语言/等级卡片多列展示，学习页主内容与侧栏并排。
- 1024px：语言卡片降为两列，等级卡片降为三列，Topic 降为两列，Hero 和学习页转为单列。
- 768px：核心内容进入单列，导航仍完整显示且不产生页面级横向滚动。

## 10. 手机端设计说明

- 390px 与 320px：
  - 页面单列。
  - 主内容宽度分别为 `358px` 和 `288px`，等于 viewport 减去左右各 `16px`。
  - 顶部导航使用五列网格完整显示，不再依赖内部横向滚动。
  - 卡片压缩内边距和标题字号，取消 `overflow-wrap: anywhere` 引起的过度断行。
  - 学习页底部操作栏固定在底部。
  - 日文正文保持较大字号和舒适行高。
  - 词汇条目在 320px 下改为更窄网格，避免横向溢出。

## 响应式修复记录

### 根因

1. 旧截图使用整页长图，手机图高度达 `2011–2334px`，在预览中被整体缩放；另外，切换 viewport 后立即截图可复现“390px 布局被填入 1440px 画布”的宽高不同步问题。
2. `html`、`body`、`#app`、`.page`、`.shell` 等关键容器缺少一致的 `width` / `max-width` / `min-width` 防御约束，对截图工具或异常固有宽度的容错不足。
3. 标题和日文使用 `overflow-wrap: anywhere` 与较大的移动端字号，容器一旦变窄会出现过度、逐字式断行。
4. 移动端顶部导航原本依赖 `max-width: 54vw` 和内部横向滚动，与“不允许任何横向滚动”的验收目标不一致。
5. 学习页阅读列没有独立的阅读宽度上限，标题、正文、音频按钮和词汇网格也缺少完整的收缩约束。

### 修改内容

- 为页面根容器和主要布局子项补齐 `width: 100%`、`max-width: 100%` 和 `min-width: 0`；`.shell` 使用 `width: min(100%, 1180px)`。
- 未使用 `overflow-x: hidden` 遮盖问题；所有横向宽度通过实际布局约束解决。
- 手机页左右固定留白 `16px`，顶部导航改为五列网格，语言、等级和 Topic 卡片改为单列。
- 降低 Hero 和学习页标题字号，改用 `overflow-wrap: break-word`，并为日文设定正常断行规则。
- 学习页主阅读区限制为 `780px`，日文正文最大 `44rem`，词汇网格使用可收缩列。
- 门户页增加完整的语言区标题与状态层级：日语为可用状态，英语、韩语、法语、西班牙语统一标注“规划中”。
- 截图改为指定 viewport 的非整页截取，在 viewport 生效、页面加载和进场动画结束后再写入文件。

### 真实浏览器宽度验收

以下每一行都已在 `index.html`、`japanese.html`、`level.html`、`topics.html`、`lesson.html` 五个页面分别测量；五页结果一致。

| Viewport | `innerWidth` | `html.scrollWidth` | `body.scrollWidth` | 主内容实际宽度 | 越界主容器 | 裁切标题/正文 | 控制台错误 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1440 × 900 | 1440 | 1440 | 1440 | 1180 | 0 | 0 | 0 |
| 1024 × 768 | 1024 | 1024 | 1024 | 942.09 | 0 | 0 | 0 |
| 768 × 1024 | 768 | 768 | 768 | 706.56 | 0 | 0 | 0 |
| 390 × 844 | 390 | 390 | 390 | 358 | 0 | 0 | 0 |
| 320 × 568 | 320 | 320 | 320 | 288 | 0 | 0 | 0 |

测量范围包括 `#app`、`.page`、`.shell`、`.topbar`、`.hero`、`.panel`、`.grid`、`.card`、`.toolbar`、`.lessonLayout`、`.lessonCard`、`.sideStack`、`.toggleBlock`、`.vocabItem` 和手机底部操作栏。所有可见容器的 `left >= 0`且 `right <= innerWidth`。

## 11. N3 迁移方案

### 当前 N3 与 N1、N2、N4、N5 的结构差异

- N1、N2、N4、N5 的页面 `<body>` 使用 `data-page="level-home"` 或 `data-page="topic"`，并带有 `data-level="n1/n2/n4/n5"`。
- N3 首页当前为 `data-page="n3-home"`，Topic 页缺少 `data-level="n3"`。
- N3 数据文件 `data/n3-data.js` 只有 `topics` 和 `stories`，缺少 `level`、`label`、`audioBase`、`wordCount`、`numberedWordCount`、`reviewSummary` 等统一元信息。
- N3 原图路径使用 `assets/entries/T001_1.png` 这类历史路径；N1、N2、N4、N5 使用各自等级目录，例如 `assets/n1/pages/`。
- N3 使用较早的 `app.js?v=20260614-2` 版本参数；N1 使用较新的 `app.js?v=20260711-2`。

### 如何迁移到统一 `level-home` 和 `data-level="n3"` 结构

1. 将 `levels/n3/index.html` 的 body 从 `data-page="n3-home"` 改为：
   - `data-page="level-home"`
   - `data-level="n3"`
2. 将 `levels/n3/topic-*.html` 的 body 增加：
   - `data-level="n3"`
3. 统一脚本版本参数到正式改版使用的同一版本。
4. 在 `app.js` 中保留对旧 `n3-home` 的兼容判断，迁移完成后再删除旧分支。

### 如何保留 N3 现有数据、音频、原图、收藏和学习状态

- 不改动 `stories[].id`、`topicId`、`audio`、`images`、`vocab` 等字段。
- 不移动 `assets/entries/`，正式改造只读取现有路径。
- localStorage key 如果已包含等级信息，应继续以 `n3` 为等级标识；如果旧逻辑缺少等级标识，需要在正式迁移时做兼容读取。
- 学习状态和收藏状态应采用“先读旧 key，再写新 key”的过渡策略，避免用户已有状态丢失。

### 迁移时需要修改的文件

- `levels/n3/index.html`
- `levels/n3/topics.html`
- `levels/n3/topic-01.html` 至 `levels/n3/topic-18.html`
- `data/n3-data.js`（仅补充元信息时需要）
- `app.js`
- `styles.css`
- 相关测试文件

### 迁移风险

- 旧 `n3-home` 渲染逻辑与新版 `level-home` 逻辑可能存在分支差异。
- 如果 localStorage key 规则不同，收藏和已学状态可能短暂显示不一致。
- N3 原图路径在 `assets/entries/`，不能简单套用 N1/N2/N4/N5 的 `assets/n*/pages/` 规则。
- N3 数据缺少统一元信息，正式改造时需要在兼容层补齐默认值，避免页面统计为空。

## 12. 正式改造涉及的文件

预计正式改造会涉及：

- `/index.html`
- `/levels/japanese/index.html`（新增）
- `/levels/n1/index.html`
- `/levels/n2/index.html`
- `/levels/n3/index.html`
- `/levels/n4/index.html`
- `/levels/n5/index.html`
- `/levels/n1/topics.html` 至 `/levels/n5/topics.html`
- `/levels/n1/topic-*.html` 至 `/levels/n5/topic-*.html`
- `/app.js`
- `/styles.css`
- `/data/n3-data.js`（如补充统一元信息）
- 自动测试文件

本阶段没有修改这些正式页面和数据文件。

## 13. 对现有功能的兼容策略

- 原型不写入现有 localStorage，只模拟按钮状态。
- 正式改造时保留现有学习状态、收藏、搜索、音频、图片路径读取逻辑。
- 新 UI 应通过 `data-level` 识别等级，避免为 N1–N5 分别复制渲染逻辑。
- 图片和音频仍使用相对路径，兼容 GitHub Pages 子路径部署。
- 旧页面可分阶段替换，先增加新入口，再迁移等级页，最后迁移 Topic 学习页。

## 14. GitHub Pages 路径处理方式

- 原型使用相对路径，例如：
  - `./japanese.html`
  - `../../assets/n1/pages/page-017.jpeg`
  - `../../assets/n1/audio/T1.mp3`
- 正式改版应继续避免绝对根路径，保证仓库部署到 GitHub Pages 子目录时资源仍可加载。
- `data-base` 或统一路径辅助函数应继续保留，用于不同层级页面加载数据、图片和音频。

## 原型文件

- 门户首页：`prototype/ui-v2/index.html`
- 日语首页：`prototype/ui-v2/japanese.html`
- 等级首页：`prototype/ui-v2/level.html`
- Topic 目录页：`prototype/ui-v2/topics.html`
- 学习内容页：`prototype/ui-v2/lesson.html`

## 浏览器验收记录

- 检查视口：`1440 × 900`、`1024 × 768`、`768 × 1024`、`390 × 844`、`320 × 568`。
- 检查页面：门户首页、日语首页、等级首页、Topic 目录页、学习内容页。
- 页面级横向溢出：0。
- 主要容器越界：0。
- 标题与正文裁切：0。
- 控制台错误：0。
- 外部互联网资源依赖：0。
- 坏图：0。
- 主要跳转：可互相跳转。
- 搜索：输入“科学”后可筛出 Topic 27。
- 收藏筛选：可切换并更新卡片列表。
- 中文内容展开/收起：有效。
- 词汇区域展开/收起：有效。
- 音频播放按钮视觉状态：有效。
- 手机端底部操作栏：390px 显示正常。
- 截图方式：完整浏览器 viewport，`fullPage: false`；桌面截图实际尺寸为 `1440 × 900`，手机截图实际尺寸为 `390 × 844`。

## 截图文件

- `reports/ui-redesign/screenshots/portal-desktop.png`
- `reports/ui-redesign/screenshots/portal-mobile.png`
- `reports/ui-redesign/screenshots/japanese-desktop.png`
- `reports/ui-redesign/screenshots/japanese-mobile.png`
- `reports/ui-redesign/screenshots/level-desktop.png`
- `reports/ui-redesign/screenshots/level-mobile.png`
- `reports/ui-redesign/screenshots/lesson-desktop.png`
- `reports/ui-redesign/screenshots/lesson-mobile.png`

## 使用的真实统计

- N1：27 Topics、494 条、2571 词
- N2：23 Topics、452 条、2360 词
- N3：18 Topics、371 条、2014 词
- N4：13 Topics、262 条、1035 词
- N5：24 Topics、373 条、1136 词
