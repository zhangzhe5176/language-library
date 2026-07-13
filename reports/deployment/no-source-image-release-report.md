# 不含原书图片的正式发布产物报告

- 日期：2026-07-14
- 分支：`feature/n5-sample`
- 起点提交：`41d477df9e06905048fb4570a9273c0f18a60626`
- 任务范围：移除正式站原图功能，建立不含原书图片的 `dist/`；不合并 `main`，不部署。

## 1. 移除的原图功能

N1–N5 共享学习页已一致移除：

- 原书图片侧栏卡片、图片数量和查看入口。
- 缩略图、点击放大、大图弹窗、遮罩、关闭按钮和 `Escape` 关闭逻辑。
- 原图 DOM 查询、事件监听、图片 `src` 设置和相关可访问性文案。
- `.sourceGrid`、`.sourcePreview`、`.imageModal`、`.modalBackdrop`、`.modalPanel`、`.modalClose`、`.modalOpen` 等专用样式。
- 已无使用点的通用 `img` 样式。

删除原图卡片后，1024px 附近的学习页侧栏由三列收紧为两列，手机端仍为单列，没有留下空白占位。正式资源查询版本由 `20260714-3` 提升为 `20260714-4`，避免发布后短时间继续命中旧版 `app.js`。

## 2. 源码原图保留情况

- `data/n1-data.js` 至 `data/n5-data.js` 未修改，源数据的 `images` 追溯字段完整保留。
- `assets/` 未修改、未删除、未压缩；Git 差异中 `data/` 和 `assets/` 的源文件变更数均为 0。
- `assets/` 内保留 1514 个栅格图片文件，共 653296636 bytes（623.03 MiB）。
- 源数据共保留 2095 条原图路径引用，对应 1426 个唯一原图文件。
- 只有 `dist/data/*.js` 发布副本将每条 Story 的 `images` 设为 `[]`；同时置空 1 条不应进入发布产物的本机审计绝对路径。

## 3. 修改文件概览

- 正式运行逻辑：`app.js`、`styles.css`。
- 正式页面：根 `index.html` 及 `levels/` 下 123 个页面 shell，只增加新资源版本和 favicon 兼容引用。
- 页面生成器：`tools/site_templates.py`、`tools/build_levels.py`、`tools/build_n3.py`。
- 发布构建：新增 `tools/build_dist.py` 和 `dist/`。
- favicon：保留 `favicon.svg`，并从同一项目图标生成兼容文件 `favicon.ico`。
- 测试：调整 `tests/test_site_ui.py`，新增 `tests/test_dist_release.py`。
- 文档：`TASK_STATUS.md` 和本报告。

## 4. `dist/` 构建方式

```bash
python3 tools/build_dist.py
python3 tools/build_dist.py --check-only
```

构建脚本每次只会安全重建项目根目录下的 `dist/`，并且：

1. 仅复制严格白名单中的正式页面、共享运行文件、数据副本、favicon 和 Story 实际引用的音频。
2. 从源数据重新生成发布数据，仅清空原图引用和本机绝对路径。
3. 校验精确文件清单、HTML/CSS/JavaScript/data 引用、动态路由、Story 音频、相对路径和文件存在性。
4. 遇到原图文件、原图目录引用、本机路径、`file://`、符号链接、越界路径或缺失资源时直接失败。
5. 输出文件数、字节数、MiB、分类体积和内容摘要。

连续两次完整构建的结果完全一致：

`3908f9f1e5eae83cccf631f144404f8779859499513d6549985f8f35c5ad5a1e`

## 5. `dist/` 文件清单概览

| 类别 | 文件数 |
|---|---:|
| HTML | 124 |
| CSS | 1 |
| 正式运行 JavaScript | 2 |
| 等级数据 | 5 |
| N1–N5 音频 | 1952 |
| favicon | 2 |
| 合计 | 2086 |

124 个 HTML 包括语言门户、日语首页、英语两个“规划中”旧 URL，以及 N1–N5 的等级首页、Topic 目录、统一学习页和各 Topic 兼容页。

## 6. 体积验收

- 文件总数：2086。
- 总字节数：838486609 bytes。
- 总体积：799.64 MiB。
- HTML/CSS/JavaScript/Data：5.98 MiB。
- 其他资源：2 个 favicon，共约 0.02 MiB。
- 低于 800 MiB 阶段目标，余量 0.36 MiB。
- 低于 1,000,000,000 bytes 保守上限，余量 161513391 bytes（154.03 MiB）。
- 相对 1 GiB 参考值余量 224.36 MiB。

说明：由于任务明确禁止压缩音频或迁移外部存储，当前在保留全部 1952 条正式音频的前提下已接近 800 MiB 目标；二进制 1 GiB 参考余量超过 200 MiB，按更保守的十进制 1 GB 计算时余量为 154.03 MiB。

## 7. 音频体积分布

| 等级 | 文件数 | 字节数 | 体积 |
|---|---:|---:|---:|
| N1 | 494 | 171681829 | 163.73 MiB |
| N2 | 452 | 366878972 | 349.88 MiB |
| N3 | 371 | 144672972 | 137.97 MiB |
| N4 | 262 | 67822020 | 64.68 MiB |
| N5 | 373 | 81140083 | 77.38 MiB |
| 合计 | 1952 | 832195876 | 793.64 MiB |

音频按各等级 `stories[].audio` 的实际引用精确复制，没有压缩、转码或外部托管。

## 8. 已排除资源

`dist/` 不包含：

- `assets/entries/`、`assets/n1/pages/` 至 `assets/n5/pages/` 和任何原书扫描图。
- 任何 PNG、JPEG、WebP、GIF、TIFF 或 PDF 原图文件。
- `prototype/`、`reports/`、`tests/`、`tools/`、`.build/`、`TASK_STATUS_HISTORY.md`。
- OCR 中间文件、截图、QA 报告、开发文档、构建缓存和未引用图片。

白名单检查结果：多余文件 0，禁止目录 0，原图文件 0，原图路径引用 0，符号链接 0。

## 9. 路径和引用检查

- HTML `href`/`src`/`srcset`、CSS `url()`/`@import`、JavaScript 静态与动态路径均已校验。
- 所有本地引用均能在 `dist/` 内解析，缺失资源 0。
- 绝对站点路径、`file://`、`/Users/wise/`、越界路径和反斜杠 URL 均为 0。
- N1–N5 的 1952 条音频引用均存在。
- 各页面使用相对路径，可兼容 `https://zhangzhe5176.github.io/language-library/` 子目录。
- 每个正式页面均显式引用 `favicon.svg` 和兼容 `favicon.ico`。

## 10. 自动化验证

- Python：37 项全部通过，包含源数据完整性、正式 UI 无原图运行链和 `dist --check-only` 验证。
- localStorage 状态迁移与等级隔离测试：通过。
- JavaScript `node --check`：17 个文件全部通过。
- `dist` 精确白名单、引用和体积检查：通过。
- `git diff --check`：通过。

## 11. 从 `dist/` 启动的浏览器回归

使用本地静态服务器直接托管 `dist/`，完成：

- 19 类页面 × 5 种 viewport，加 N3 Story 168/199 × 5，共 105 次页面检查，失败 0。
- viewport：1440×900、1024×768、768×1024、390×844、320×568。
- 各尺寸 `document.documentElement.scrollWidth === document.body.scrollWidth === window.innerWidth`，溢出元素 0，内容裁切 0。
- N1–N5 各一条音频均实际点击播放与暂停，`readyState=4`、`error=0`；N3 Story 168/199 音频也正常就绪。
- 中文、词汇展开收起，搜索，收藏，已学，筛选，最近学习，继续学习，上一篇和下一篇均正常。
- 学习页中原图按钮 0、原图弹窗 0、原图文案 0，静态服务器请求日志中原图请求 0。
- 手机底栏未遮挡内容，320px 长标题正常换行。
- 英语 `index.html` 和 `sample.html` 均为统一“规划中”页，其他规划中语言没有失效入口。
- 控制台 error/warning 为 0，网络 404 为 0。
- 测试中的收藏/已学状态已恢复；所有测试只作用于 localhost origin，不会修改真实用户数据。

回归期间曾捕获 Chrome 对默认 `/favicon.ico` 的兼容请求；已增加项目自有 `favicon.ico`、纳入构建白名单，并在最终产物重测为 HTTP 200，不再产生 404。

## 12. GitHub Pages 限制判定

`dist/` 低于 800 MiB 阶段目标，也低于保守按 1,000,000,000 bytes 计算的 1 GB 限制。从产物体积、白名单和运行引用看，满足下一阶段 GitHub Pages 发布条件。

但当前 Pages 仍从 `main` 根目录的 legacy 源发布；仅将本分支 fast-forward 到 `main` 不会自动改为发布 `dist/`，反而仍会尝试处理含原图的整个仓库根目录。

## 13. 下一步合并和部署建议

1. 在单独授权的上线任务中，先将 GitHub Pages 发布流程调整为仅上传 `dist/` 产物（优先使用 GitHub Actions Pages artifact），或使用只包含 `dist/` 内容的专用发布分支。
2. 不应在保持当前 `main` 根目录 legacy 发布方式时直接上线。
3. 发布方式确认后，再执行 fast-forward 合并、推送 `main`、等待 Pages 部署并完成真实线上验收。

## 最终结论

- **`dist/` 发布产物：Go。**
- **继续使用当前 `main` 根目录 legacy Pages 方式直接部署：No-Go。**
- 本阶段满足“提交并推送 `feature/n5-sample`，不合并、不部署”的交付条件。
