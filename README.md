# 第一推动丛书·综合系列（2022 年版）· 点化学习系统

把 11 册书做成一套能直接开学的知识库：统一入口 `index.html`、每册一个可独立发送的单书伴侣、全 Markdown 知识库，以及跨书总览。纯静态，可直接挂 GitHub Pages。

## 快速开始

双击 `index.html`。顶部切换书籍与跨书总览，左侧按「学习路径 / 章节 / 概念 / 测验 / 抽认卡 / 术语 / 模式 / 速查」浏览，搜索覆盖全部 11 册，进度存在浏览器本地。

离线可用；Mermaid 图走 CDN，断网时降级显示源码并给出提示，不会白屏。

## 内容规模

| 项 | 数量 |
|---|---|
| 书籍 | 11 册 |
| 章节精讲 | 145 章 |
| 跨章概念页 | 37 篇 |
| 测验题（含解析） | 257 题 |
| 抽认卡 | 526 张 |
| 术语 | 165 条 |
| 跨书总览 | 3 篇（推荐顺序 / 概念映射 / 综合检验） |

## 目录结构

```
点化学习系统/
├── index.html                  总学习手册（单文件，统一入口）
├── index.md                    Markdown 导航页
├── README.md                   本文件（使用与部署）
├── 交付说明.md                 交付清单、验证结论、取舍说明
├── .nojekyll                   GitHub Pages 关闭 Jekyll
├── 00-跨书总览/                推荐顺序、跨书概念映射、综合检验
├── 01-复杂/ … 11-四维旅行/     每册一套：
│   ├── SKILL.md                学习总纲（路径 + 章节索引 + 前置缺口）
│   ├── chapters/               逐章精讲
│   ├── concepts/               跨章概念页
│   ├── glossary.md patterns.md cheatsheet.md quiz.md flashcards.md
│   ├── manifest.json           结构化清单（HTML 由它组装）
│   ├── <slug>学习伴侣.html     单书伴侣（单文件，可单独发送）
│   └── _work/raw/              分章原文（full 包保留）
└── _build/                     抽取与编译脚本、结构地图（full 包保留）
```

## 推荐阅读顺序

不按书号读。推荐顺序与理由写在 `00-跨书总览/README.md`，简版：

1. 《逻辑的引擎》→ 2.《复杂》→ 3.《复杂的引擎》→ 4.《物理之外的世界》
5. 《伽利略的手指》→ 6.《四维旅行》→ 7.《皇帝新脑》→ 8.《数学的意义》
9. 《真理与美》→ 10.《未来50年》→ 11.《下一步是什么》

## 部署到 GitHub Pages

站点根目录必须是本目录的全部文件（不要把 `点化学习系统/` 这一层再套进去）。

```bash
cd <本目录>
git init
git add -A
git commit -m "点化学习系统：总学习手册 + 11 册学习伴侣"
git branch -M main
git remote add origin https://github.com/<用户名>/<仓库名>.git
git push -u origin main
```

然后：仓库 **Settings → Pages → Source: Deploy from a branch → Branch: main，目录 `/ (root)` → Save**。约 1–2 分钟后访问 `https://<用户名>.github.io/<仓库名>/`。

已有仓库只需 `git add -A && git commit && git push`，Pages 设置不变。

### 排错

- **404**：确认 `index.html` 在仓库根目录；Pages 选的是 `main` + `/ (root)`；刚开启要等 1–2 分钟。
- **中文文件名 404**：`index.html` 内部全用 hash 路由，不受影响；单书伴侣链接已做 URL 编码。
- **Mermaid 不显示**：图走 CDN，离线或 CDN 被拦时降级为源码，属预期。
- **仓库太大**：Pages 上限 1 GB、单文件 100 MB。本包 `full` 版约 11 MB，无需精简；若要更小，删各册 `_work/` 与 `_build/` 不影响站点。

## 版权

源书为《第一推动丛书·综合系列（2022 年版·11 册套装）》。本知识库是学习笔记性质的精讲与重组，**仅供个人学习使用，请支持正版**。`_work/raw/` 中的分章原文请在分享前删除。
