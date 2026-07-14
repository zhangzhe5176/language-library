# TASK_STATUS

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
