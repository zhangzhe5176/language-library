# Language Library

Language Library 是一个面向日语学习的静态网站，按 JLPT N1–N5 等级组织 Topic、学习文章、中文理解、词汇和官方音频，供本地开发检查和 GitHub Pages 正式访问使用。

正式网址：<https://zhangzhe5176.github.io/language-library/>

当前正式版本：`v1.1.0`

## 分支和发布资源

- `main`：正式稳定源码分支，包含源代码、原始资源、数据、测试、工具和项目记录。
- `feature/*` 或其他独立任务分支：从最新 `main` 创建，用于功能、文档或修复开发；未经验收不得直接作为正式版本。
- `gh-pages`：只保存正式网站发布产物，内容为经过验证的 `dist/` 根目录文件。

源码资源与发布资源有明确区别：

- `assets/` 中保留原始音频和原始图片，作为源码母版，不得修改或删除。
- `dist/` 是构建生成的发布目录，使用发布专用的压缩 MP3 音频，不包含原书图片。
- `gh-pages` 发布的是 `dist/` 的正式产物，不是完整源码目录。

## 基本构建

`tools/build_dist.py` 用于生成和检查正式发布目录。它会按照发布白名单复制页面、运行文件、数据和实际引用的音频，生成发布数据副本，校验路径和引用，并对发布音频执行 MP3、64 kbps、mono 转码及 `.build/audio-cache/` 缓存复用。

在任务分支中执行：

```bash
python3 tools/build_dist.py
python3 tools/build_dist.py --check-only
```

`dist/` 是可删除后重新生成的构建产物，不应手工编辑。仅检查已有产物时使用 `--check-only`，它不会重新构建。

基础检查可使用：

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
node tests/site-state.test.js
git diff --check
```

## 基本发布流程

1. 从最新 `main` 创建独立分支。
2. 完成本地修改和测试，确认原始音频、原始图片及无关发布产物没有变化。
3. 构建并检查 `dist/`。
4. 将经过验证的 `dist/` 内容更新到 `gh-pages` 根目录并正常推送。
5. 等待 GitHub Pages 部署完成。
6. 使用正式网址进行页面、资源、音频、控制台和 `404` 线上验收。
7. 线上验收通过后，使用 fast-forward 合并 `main` 并推送正式记录。

未通过线上验收前，不得合并 `main`，不得把未验收版本当作正式版本发布。

## 项目目录

```text
index.html                 根门户页面
app.js / state.js          页面运行逻辑和本地学习状态
styles.css                 全站样式
favicon.*                  项目图标
assets/                    原始音频、原始图片等源码资源
data/                      N1–N5 源数据
levels/                    等级首页、Topic 目录和学习页
dist/                      生成的正式发布产物
tools/                     构建、审计、数据处理和修复工具
tests/                     Python 与 JavaScript 测试
reports/                   审计、验收和发布报告
TASK_STATUS.md             当前项目状态和后续工作记录
TASK_STATUS_HISTORY.md     历史状态记录
prototype/                 原型和开发阶段资料
```

修改内容时，必须保护 `assets/` 中的原始音频和原始图片。压缩音频只能用于 `dist/` 和 `gh-pages` 发布，不得覆盖源码母版；正式发布也不得把原书图片带入网站。
