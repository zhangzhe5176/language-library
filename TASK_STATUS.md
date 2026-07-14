# TASK_STATUS

## V1.2 单词筛查正式接入候选版（2026-07-14）

- 当前工作分支：`feature/vocabulary-prototype`。
- 本轮开始前 HEAD：`42e1cf44f75c690231b82d7d10d7b2adcf2d9604`。
- 正式页面：根路径 `vocabulary.html`；正式入口不再使用 prototype 页面路径。
- 导航：共用导航加入“单词筛查”；语言门户和日语首页增加入口。
- 数据：N5～N1 共 105 个 Topic、9,116 条目标生词；逐 Topic 词卡对账差异全部为 0；20 条人工读音修正继续生效。
- 兼容：正式页面沿用 `languageLibrary:vocabularyPrototype:all:v2` 和旧 N5 v1 迁移逻辑，原型已有记录可继续读取。
- 导出：正式页面保留当前 Topic/当前等级累计范围、三种薄弱词类型和六列 XLSX。
- 构建：正式 `dist/` 已按白名单更新为 2,090 个文件、531,869,830 bytes（507.23 MiB）；音频 1,952 个全部命中缓存；`--check-only` 通过。
- 验证：正式页面和临时 dist 页面、入口导航、前进后退、音频引用、五等级数据、响应式、导出、37 项自动测试、`site-state`、JavaScript 语法和 `git diff --check` 均通过。
- 发布边界：未修改 `gh-pages`，未发布，未合并 `main`；等待用户进行线上验收后再决定发布。
- 发布前报告：`reports/deployment/vocabulary-feature-release-report.md`。

## V1.2 N5～N1 完整功能候选版（2026-07-14）

- 当前工作分支：`feature/vocabulary-prototype`。
- 开始前 HEAD：`dfae000a2919159aeb9af701c536266e289fbae4`；`main` / `origin/main`：`d28ebe8d7c2e491f28679ab60a3eacd3d76f7856`；`gh-pages` / `origin/gh-pages`：`53fc20061b1e283a5004d05e65d6534cc88f05d9`。
- 范围：独立原型扩展至 N5、N4、N3、N2、N1 全部 105 个 Topic；页面只渲染当前等级的当前 Topic。
- 数据：从现有 `data/n5-data.js`、`data/n4-data.js`、`data/n3-data.js`、`data/n2-data.js`、`data/n1-data.js` 动态加载；原始目标词条 9,116 条，Topic 内去重后进入词表 9,001 条。
- 已完成：等级切换、Topic 总览折叠、Topic 前后切换、当前等级/Topic 统计、三列/两列/单列词卡、当前 Topic 重置、当前等级重置、当前 Topic 范围 Excel 导出、N5 v1 localStorage 迁移。
- 数据审计：`reports/vocabulary/vocabulary-full-data-audit.md`。
- 验证：五等级加载、105 Topic 遍历、五等级搜索与六种筛选、状态和答案显示、红黄绿 Topic 状态、重置确认、五等级导出、响应式、旧 N5 迁移、损坏记录容错、正式首页/导航/音频资源回归、37 项 Python 自动测试、`site-state`、JavaScript 语法和 `git diff --check` 已完成；浏览器 headless 的主动音频播放调用曾超时，正式音频资源 HTTP 加载和音频元素引用正常，未修改正式音频。
- 体积：原型源码从 39,466 bytes 增至 48,300 bytes，增加 8,834 bytes；正式 `dist/` 未重建，当前 2,086 文件、531,811,209 bytes。
- 当前下一步：提交本分支，保持本地预览服务运行，等待用户进行 N5～N1 完整验收；不合并、不发布、不修改 `gh-pages`。

## V1.2 单词筛查原型（2026-07-14）

- 当前工作分支：`feature/vocabulary-prototype`
- 原型路径：`prototype/vocabulary-prototype/vocabulary-prototype.html`
- 范围：仅 N5，3 个真实 Topic、24 个目标生词；不接入正式首页、导航或共用运行文件。
- 已完成：单词状态筛查、localStorage、搜索、状态筛选、统计、目标生词单元提示、重置确认和标准 `.xlsx` 导出。
- 已完成验证：本地 Chrome 交互回归、5 种视口无横向溢出、正式首页/音频本地回归、Excel 结构检查、项目自动测试和发布边界检查。
- 原型功能提交：`eb5d44b`；未推送、未合并、未发布。
- 当前下一步：保持本地预览服务运行，等待用户体验反馈。

## V1.2 词卡界面第二版（2026-07-14）

- 范围：仅调整独立原型的单词筛查列表视觉结构和交互显示，不扩展功能范围。
- 词卡：桌面端两列紧凑网格，`720px` 以下单列；未筛查只显示假名和三个状态方块。
- 答案：选择任意状态后在假名下显示日语汉字和唯一中文释义；取消状态或刷新规则保持正确；无汉字词不显示占位文字。
- 页面隐藏：词性、Topic 编号、单元名称和其他辅助字段不再显示在词卡中；导出仍从原始词汇数据读取四列字段。
- 修改文件：`prototype/vocabulary-prototype/vocabulary-prototype.css`、`prototype/vocabulary-prototype/vocabulary-prototype.js`。
- 验证：本地浏览器交互、5 种视口、搜索、6 种筛选、统计、单元提示、重置、`.xlsx` 下载、37 项自动测试、`site-state`、构建检查和 `git diff --check` 均通过。
- 预览：`http://127.0.0.1:4173/prototype/vocabulary-prototype/vocabulary-prototype.html`；未发布、未合并、未修改正式首页、导航、共用文件、`main` 或 `gh-pages`。

## V1.2 Topic 交互第三版（2026-07-14）

- 起点提交：`b6d520b2c1a46e5e7bd20e586419f5134c88a328`。
- 范围：继续使用 3 个真实 N5 Topic、24 个真实目标词；每次只显示当前 Topic 的 8 个目标词。
- 交互：新增 Topic 总览、当前 Topic 前后切换、当前 Topic 统计、当前 Topic/当前 N5 重置和当前 Topic 范围导出；切换会清空搜索、恢复“全部”筛选并滚动到词卡区域。
- 词卡：桌面三列、平板两列、手机单列；假名在上，答案按状态显示，三个状态按钮固定在卡片底部并等宽排列。
- 完成反馈：当前 Topic 全部筛查后显示会/模糊/不会总结、复习短文后续实现提示和可用的下一个 Topic 操作。
- 导出：文件名增加 `Topic01` 等当前 Topic 标识，仍为假名、日语汉字、词性、唯一中文释义四列；搜索和筛选不影响导出范围。
- 验证：Topic 切换、状态范围、红黄绿规则、重置确认、localStorage、三种导出、空结果提示、5 种视口、等宽按钮、37 项自动测试、`site-state`、构建检查和 `git diff --check` 均通过。
- 修改范围：仅独立原型 CSS/JS 和本状态文件；未修改正式页面、导航、共用 CSS/JS、原始数据、音频、图片、`dist` 或 `gh-pages`。
- 当前下一步：提交本分支并保持本地预览服务运行，等待用户体验反馈。

## 项目状态

- 当前分支：`feature/vocabulary-prototype`
- 正式站：已上线并通过线上验收
- QA 结论：`Go`
- 正式地址：<https://zhangzhe5176.github.io/language-library/>
- Pages 发布源：`gh-pages` 分支根目录 `/`
- `main` V1.1 音频压缩源码已 fast-forward 合并；最终正式记录提交见本次发布记录
- `gh-pages` 发布提交：`53fc20061b1e283a5004d05e65d6534cc88f05d9`
- 上线记录：由提交 `docs(project): record production launch` 保存
- 上线时间：2026-07-14 03:28 JST
- `feature/n5-sample`：保留，未删除
- 上线前备份标签：`pre-japanese-library-launch-20260714`，指向旧 `main` `22ed78927d4b29d5bf5fbf4e9d349a566d1e05aa`

## 正式内容

- N1：27 Topics、494 条、2571 词
- N2：23 Topics、452 条、2360 词
- N3：18 Topics、371 条、2014 词
- N4：13 Topics、262 条、1035 词
- N5：24 Topics、373 条、1136 词
- 合计：105 Topics、1952 条、9116 词

## 发布结构

- 源码、审计资料和原书图片保留在 `main`。
- 正式站只发布 `dist/` 白名单产物。
- `dist/` 共 2086 个文件、531811209 bytes（507.17 MiB）。
- 发布音频共 1952 个、525520476 bytes（501.18 MiB），统一为 64 kbps mono MP3。
- 正式站不包含原书图片，也不提供“查看原图”功能。
- 源码中的原书图片及数据追溯字段保持完整，未删除、未压缩。

## 验收结果

- 发布前 37 项 Python 测试、状态迁移测试、全部 JavaScript 语法检查、引用检查和 `git diff --check` 通过。
- Pages 部署成功，发布提交与 `gh-pages` 一致。
- 线上 124 个 HTML 页面和 10 个核心资源全部返回 `200`，并与本地 `dist/` 一致。
- N1–N5 首页、Topic 目录、学习页、搜索、收藏、已学、最近学习、继续学习和前后篇通过。
- N1–N5 官方音频均完成真实在线加载与播放验证。
- 1440、1024、768、390、320 像素宽度均无横向溢出或内容裁切。
- 控制台无错误，站内引用无 `404`，正式页面无原书图片请求。
- `main` 已通过 fast-forward 合并并推送；未使用普通 merge、rebase、squash 或强制推送。

## 保留的非阻断维护项

- QA-04：源码中 86 个未引用图片，待用途确认后再整理。
- QA-05：源码中的重复图片，待建立明确去重策略后再处理。
- QA-07：测试脚本中的成功提示 `console.log`，不进入正式运行页面。
- QA-09：`.build/` 本地缓存保持不变，未清理。
- GitHub Pages 托管工作流显示 GitHub 管理的 Node.js 20 弃用提示；本次构建成功，不影响正式站。

## V1.1 发布音频压缩（2026-07-14）

- feature 分支：`feature/audio-compression`
- feature 提交：`ddc07314d1aed4c2be52a964287c15499785281f`
- `gh-pages` 发布提交：`53fc20061b1e283a5004d05e65d6534cc88f05d9`
- 发布参数：MP3、64 kbps、mono；参数为 `-vn -ac 1 -b:a 64k -map_metadata -1`。
- 原始音频：1952 个文件的路径、大小和 SHA-256 聚合清单均与基线一致，未修改、未删除、未覆盖。
- 体积：`dist/` 从 838486609 bytes（799.64 MiB）降至 531811209 bytes（507.17 MiB）；音频从 832195876 bytes（793.64 MiB）降至 525520476 bytes（501.18 MiB），总节省 306675400 bytes（36.57%）。
- 全量验证：1952/1952 可由 `ffprobe` 解析，均为 mono、64000 bps，源/发布时长最大差异 0.000122 秒。
- 缓存：首次 0 命中、1952 新转码；复建 1952 命中、0 新转码；`.build/audio-cache/` 不入 Git。
- 本地浏览器回归、100 条抽样播放和自动测试全部通过。
- Pages API 为 `built`；线上 N1–N5 各 5 条、共 25 条音频真实播放通过，覆盖前/中/后段；无 404、控制台错误或警告。
- 正式结论：`Go`。Pages 发布源保持 `gh-pages` 根目录，未发布原书图片。

## 下一步

正式站当前可正常使用。后续功能或内容更新应先在功能分支完成验证，重新构建 `dist/`，再独立更新 `gh-pages`；不要直接把源码目录作为 Pages 发布源。
