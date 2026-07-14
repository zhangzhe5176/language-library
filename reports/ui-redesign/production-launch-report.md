# Language Library 正式上线报告

## 1. 上线结论

- 正式上线时间：2026-07-14 03:28 JST
- 最终结论：**Go**
- 正式网址：<https://zhangzhe5176.github.io/language-library/>
- GitHub Pages 发布源：`gh-pages` 分支根目录 `/`
- 源码上线基线：`227a37b0e75c92e242c2847776c523f535793ffb`
- 发布提交：`5dc1d9eb14f8a62b8378891c45a4898201ef3677`
- 上线记录提交：本报告所在的 `docs(project): record production launch` 提交

新版已从独立发布分支上线，线上内容只来自 `dist/`。`main` 中保留完整源码、音频、原书图片、报告和构建工具，但这些源码资源不会由 GitHub Pages 直接发布。

## 2. 合并前保护检查

发布和合并前确认：

- `feature/n5-sample` 与 `origin/feature/n5-sample` 均为 `227a37b0e75c92e242c2847776c523f535793ffb`。
- 旧 `main` 与 `origin/main` 均为 `22ed78927d4b29d5bf5fbf4e9d349a566d1e05aa`。
- 功能分支相对旧 `main` 为 ahead 76、behind 0，满足 fast-forward 条件。
- 工作区在发布前保持干净。
- 本地构建缓存 `.build/` 依照既定要求保留，并通过本地 Git 排除规则避免进入提交。

## 3. 备份标签

- 标签：`pre-japanese-library-launch-20260714`
- 指向：`22ed78927d4b29d5bf5fbf4e9d349a566d1e05aa`
- 本地与远程标签一致。
- 标签未删除、未移动、未强制覆盖。

## 4. 发布产物与体积

重新运行 `tools/build_dist.py` 后的正式产物：

- 文件数：2086
- 总字节数：838486609 bytes
- 总体积：799.64 MiB
- 可重复构建摘要：`3908f9f1e5eae83cccf631f144404f8779859499513d6549985f8f35c5ad5a1e`
- 代码与数据：5.98 MiB
- N1 音频：494 个，163.73 MiB
- N2 音频：452 个，349.88 MiB
- N3 音频：371 个，137.97 MiB
- N4 音频：262 个，64.68 MiB
- N5 音频：373 个，77.38 MiB
- 音频合计：1952 个，793.64 MiB

产物低于本次 850 MiB 上限，不含原书图片、报告、测试、工具、原型、OCR 中间文件、截图或构建缓存。未发现本地绝对路径、`file://` 路径或缺失引用。

## 5. `gh-pages` 发布结果

- 远程原先不存在 `gh-pages`。
- 使用独立 orphan 分支创建发布历史。
- 分支根目录直接包含 `index.html`、`app.js`、`state.js`、`styles.css`、favicon、`data/`、`levels/` 和正式音频。
- 分支根目录与本地 `dist/` 逐文件一致。
- 提交信息：`deploy: publish language library`
- 提交：`5dc1d9eb14f8a62b8378891c45a4898201ef3677`
- 父提交数：0，确认是独立发布历史。
- 本地与 `origin/gh-pages` 一致，使用正常推送，未强制推送。

## 6. GitHub Pages 部署

- 发布方式：GitHub Pages legacy branch deployment。
- 发布源已从 `main /` 切换为 `gh-pages /`。
- 自定义域名保持为空，HTTPS 保持启用，未修改其他仓库设置。
- Pages 构建运行：<https://github.com/zhangzhe5176/language-library/actions/runs/29273430463>
- 部署提交：`5dc1d9eb14f8a62b8378891c45a4898201ef3677`
- 部署完成时间：2026-07-14 03:12:47 JST
- 部署状态：`completed / success`
- Pages API 状态：`built`

## 7. 发布前自动验证

以下检查全部通过：

- 37 项 Python 自动测试。
- `tests/site-state.test.js` 状态迁移与等级隔离测试。
- 17 个 JavaScript 文件的 `node --check`。
- `tools/build_dist.py --check-only` 引用和发布白名单检查。
- `git diff --check`。
- `dist/` 原书图片、绝对路径和缺失资源检查。

## 8. 线上入口与路由验收

真实线上地址验收结果：

- 根首页显示新版 Language Library 语言门户。
- 日语入口进入独立日语首页。
- 英语、韩语、法语和西班牙语显示“规划中”，没有不存在的学习入口。
- 门户不再直接进入 N3。
- 日语首页可进入 N1–N5。
- 五个等级首页、Topic 目录、首条学习页均正常。
- 英语旧地址 `levels/english/index.html` 和 `levels/english/sample.html` 均正常显示规划中页面。
- 124 个正式 HTML 页面全部返回 HTTP `200`，0 重定向、0 失败，并与本地 `dist/` 对应文件逐字节一致。

## 9. N1–N5 统计验收

线上日语首页显示并核对：

| 等级 | Topics | 故事 | 词汇 |
| --- | ---: | ---: | ---: |
| N1 | 27 | 494 | 2571 |
| N2 | 23 | 452 | 2360 |
| N3 | 18 | 371 | 2014 |
| N4 | 13 | 262 | 1035 |
| N5 | 24 | 373 | 1136 |
| 合计 | 105 | 1952 | 9116 |

## 10. 学习功能验收

N1–N5 分别完成线上学习页检查：

- 日文和中文内容正常显示。
- 中文理解可展开和收起。
- 词汇可展开和收起。
- 收藏和已学可切换并恢复。
- 最近学习和继续学习入口正确。
- 相同 Story 编号在不同等级间互不串状态。
- Topic 搜索可从 Story 标题检索到正确 Topic；清空后恢复全部 Topic。
- 收藏、已学和全部筛选结果正确。
- 首篇边界只显示下一篇；N3 Story 168、199 的上一篇和下一篇均指向正确条目。
- N3 Story 168、199 页面正常，均不显示或请求原书图片。

旧 N3 状态迁移由自动测试覆盖：合并时去重、保留旧 key、保留已有新结构数据、迁移标记和失败保护均通过。线上 `state.js` 与已测试的 `dist/state.js` 字节一致；浏览器中的等级隔离、收藏、已学、最近学习和继续学习也完成实测。

## 11. 音频验收

- N1–N5 首条官方音频均在真实 Chrome 中完成在线播放。
- 五条音频均达到 `readyState=4`，播放状态为未暂停，播放时间实际前进。
- 音频地址分别指向各等级预期目录。
- N1–N5 首末代表音频共 10 个文件，HTTP HEAD 返回 `200`，Range GET 返回 `206`，大小与本地一致，MP3 文件头有效。
- 切换页面会停止上一条音频。

## 12. 原书图片取消结果

- N1–N5 学习页均无“查看原图”按钮。
- 无原图数量、弹窗、轮播、放大或手机端原图入口。
- DOM 中不存在原图弹窗和相关控件。
- 浏览器资源请求中没有原书图片。
- 正式发布分支不含原书图片文件。
- `main` 的 `assets/` 原书图片和 `data/` 追溯字段完整保留，未删除、未压缩。

## 13. 响应式、网络和控制台验收

检查尺寸：1440×900、1024×768、768×1024、390×844、320×568。

- `document.documentElement.scrollWidth === window.innerWidth`。
- `document.body.scrollWidth === window.innerWidth`。
- 主要页面无越界元素、横向滚动或文字裁切。
- 390 和 320 像素学习页底部栏正常显示；页面底部预留 118px，超过底栏及安全间距所需 70px，不遮挡内容。
- 桌面端底部栏正确隐藏。
- 控制台错误和警告为 0。
- 核心页面与资源无站内 `404`。
- favicon 的 SVG 和 ICO 兼容文件均返回 `200`。

## 14. `main` fast-forward 结果

- 在 Pages 线上验收通过后才开始合并源码。
- 拉取并确认 `origin/main` 仍为旧提交。
- 使用 `git merge --ff-only feature/n5-sample`。
- 合并后源码基线为 `227a37b0e75c92e242c2847776c523f535793ffb`。
- 正常推送到 `origin/main`。
- 未创建 merge commit，未 rebase、squash、强制推送或改写历史。
- Pages 已从 `gh-pages` 发布，因此本次 `main` 推送不会把源码原书图片发布到正式站。

## 15. 保留的非阻断维护项

- QA-04：源码中 86 个未引用图片，后续确认用途后再整理。
- QA-05：重复图片，后续建立明确去重策略后再处理。
- QA-07：测试文件中的成功提示 `console.log`，仅存在于测试脚本。
- QA-09：`.build/` 缓存按要求保留。
- GitHub 管理的 Pages 工作流提示 Node.js 20 将弃用，并自动使用 Node.js 24 运行相关 action；本次部署成功，该提示不影响网站功能，也不是项目运行代码错误。
- `dist/` 距 800 MiB 目标仅约 0.36 MiB，后续增加音频前必须重新核对发布体积；距本次 850 MiB 上限仍有约 50.36 MiB。

## 16. 后续发布方式

后续更新建议保持同一流程：

1. 在功能分支完成修改和测试。
2. 使用 `tools/build_dist.py` 重建发布产物并检查体积与引用。
3. 只把 `dist/` 内容更新到 `gh-pages` 根目录。
4. 等待 Pages 部署并进行线上验收。
5. 验收通过后再 fast-forward 合并源码分支。

不要把 Pages 发布源切回包含完整源码和原书图片的 `main`。

## 17. V1.1 发布音频压缩记录

2026-07-14 完成 V1.1 音频压缩发布，Pages 发布源保持 `gh-pages` 根目录 `/`。

- feature 分支：`feature/audio-compression`
- feature 提交：`ddc07314d1aed4c2be52a964287c15499785281f`
- `gh-pages` 发布提交：`53fc20061b1e283a5004d05e65d6534cc88f05d9`
- 发布参数：MP3、64 kbps、mono，`-vn -ac 1 -b:a 64k -map_metadata -1`。
- 原始音频继续完整保存在 `main`；1952 个原始音频的路径、大小和 SHA-256 聚合清单未变化。
- `dist/` 从 838486609 bytes（799.64 MiB）降至 531811209 bytes（507.17 MiB）。
- 音频从 832195876 bytes（793.64 MiB）降至 525520476 bytes（501.18 MiB），节省 306675400 bytes（36.85% 的音频体积；占原 dist 体积 36.57%）。
- 全量 1952 条音频均通过 `ffprobe`、时长一致性、mono、64000 bps 和 MP3 文件头检查。
- 本地五种视口回归、100 条抽样播放、自动测试和 `build_dist.py --check-only` 全部通过。
- Pages API 状态为 `built`。线上 N1–N5 各 5 条、共 25 条音频真实播放通过，覆盖前/中/后段；播放时间前进，无 404、控制台错误或警告。
- 最终结论：`Go`。未改变 Pages 发布源，未发布原书图片，未强制推送或改写历史。
