# HarnessCraft 内容与工程化缺口分析

> 分析对象：`huanqwer/HarnessCraft` main 分支（HEAD = `a77475e docs: 文章头部模板加入作者简介（老邋遢）`）
> 分析时间：2026-10-19 ｜ 分析方式：仓库全量文件 + git 历史 + 可执行脚本核验（每条结论都带证据命令）
> 结论口径：**只列可复现的事实**，涉及作者意图的部分标注"待作者决定"。

---

## 0. 一句话结论

仓库里**有 10 篇成稿 + 1 篇只有模板头的空文**，文章质量与读者价值没问题；
真正缺的是**"内容之外的那一圈"**：没有站点、没有元数据、没有 CI、没有模板与协作入口，
以及 README 承诺的 `.devin/`（Skills / Rules / Workflows / Memories）**根本没有随仓库发布**——
也就是说，README 说的"不只是文章，还包含可直接使用的工程组件"目前是**未兑现的承诺**。

| 维度 | 现状 | 缺口等级 |
| --- | --- | --- |
| 文章内容 | 10 篇成稿（合计约 3.1 万中文字）+ 1 篇空文 | P0：第 6 篇空文 |
| 内容元数据 | 无 front matter、无日期、无标签、无摘要 | P0 |
| 发布载体 | 只有 GitHub 上的 `.md` 源码，无站点 / 无 RSS / 无域名 | P0（本次已补） |
| README 承诺的 Harness 资产 | `.devin/` 被 .gitignore 排除，仓库里不存在 | P0 |
| 工程化 | 无 CI、无 issue/PR 模板、无文章模板、AGENTS.md 为占位 | P1（本次已补） |
| 版本化归档 | `git tag` 数量 = 0，与自家 ISIER「带版本号归档」的要求不符 | P1 |
| 资产依赖 | 34 张配图 100% 依赖第三方 Cloudinary CDN | P2 |

---

## 1. 内容层面的缺口

### P0-1 第 6 篇是空文，只有模板头

`posts/AI自验证并纠错通宵跑完任务，我只负责验收.md` 全文 17 行：H1 + 两段 blockquote + `[TOC]` + `---`，
正文实质内容 **0 个中文字**（其余 10 篇正文中文字数在 2624～5130 之间）。

证据：

```bash
wc -l "posts/AI自验证并纠错通宵跑完任务，我只负责验收.md"   # 17
python3 tools/build_site.py --check                          # INFO：正文实质内容仅 0 个中文字
```

影响：README 目录里它排在第 6 位（后端实践），读者点进去是空页；站点侧已自动标为草稿隐藏，
系列表里显示"待补完"（不生成链接），不会再出现打不开的页面。

### P0-2 章节编号与 README 序号不一致，读者会迷路

10 篇成稿里有 8 篇带章节尾注，编号与 README 序号**整体错位**：

| README 序号 | 文章 | 文章内章节尾注 |
| --- | --- | --- |
| 1 | 如何选择自己称手的VibeCoding「兵器」 | 第一章毕 |
| 2 | 我自研的Harness五层架构原理 | 无（更像总纲/引子） |
| 3 | 如何让AI设计出优秀的产品 | **第二章毕** |
| 4 | 前端总跑偏？针对前端工程师的Harness | **第三章毕** |
| 5 | 架构思维于Harness的重要性 | 第四章毕 |
| 6 | AI自验证并纠错通宵跑完任务（空文） | 无 |
| 7 | 测试工程师借助AI不完全摸鱼指南 | **第五章毕** |
| 8 | 通用上线skill，让AI帮你部署和运维 | **第六章毕** |
| 9 | 优秀的AI应用工程师需要学会白嫖Token的技巧 | **第七章毕** |
| 10 | 别人的AI为什么越来越好用 | **第八章毕** |
| 11 | 看看真实企业内部的Harness+FDE改造如何落地的 | 无（实践篇） |

证据：`grep -oE "第[一二三四五六七八九十]+章毕" posts/*.md`

事实：内容其实是「8 章正文 + 五层架构总纲 + FDE 实践篇」的结构，但 README 用 1～11 的线性序号表达，
两个编号体系互相打架。建议二选一（**待作者决定**）：
在 README 表格里加一列"章节号"，或把文章里的"第X章毕"改成与 README 序号一致。

### P0-3 文章没有元数据，导致"不能聚合、不能排序、不能筛选"

11 篇全部是纯 Markdown：首行 H1 + 头部 blockquote，**没有 front matter**（日期 / 标签 / 摘要 / slug 一律没有）。

证据：`for f in posts/*.md; do head -1 "$f"; done` → 全部为 `# 标题`，没有一篇以 `---` 开头。

影响：任何博客系统（Jekyll / Hugo / VitePress / MkDocs）都无法把它们排成列表；
GitHub 自己也不渲染 `[TOC]`（11 篇里 11 个 `[TOC]` 标记在 GitHub 上都是纯文本）。

本次处理：**不改文章**，由 `tools/build_site.py` 在构建时补 front matter——
日期取每篇文章的 git 首次提交日期（含重命名前身），分类取 README「主题」列，slug 取标题拼音。
即"元数据有唯一真源、可核查"，而不是人工维护 11 份重复信息。

### P1-4 配图的 alt 与资产依赖

- 34 张配图 100% 指向 `res.cloudinary.com/isieghiq/...`，仓库内**零本地图片**：
  Cloudinary 账号一旦限额/欠费/改结构，文章全部变成红叉。这是外部单点依赖。
- 1 处 Typora 残留 alt：`![image-20260518151953156]`（在"我自研的Harness五层架构原理"里），
  其余 33 张 alt 都写得不错。

证据：`grep -ohE '!\[image-[0-9]+\]' posts/*.md | wc -l` → 1

### P2-5 没有摘要 / 关键词 / 版权声明

每篇文章没有 1～2 句"这篇文章解决什么问题"的摘要，分享到微信、知乎、X 时没有摘要可抓；
文章内也没有单独的转载声明（只有仓库级 MIT LICENSE）。

---

## 2. README 承诺与仓库实际的偏差（最需要作者拍板的一项）

README 第 23-37 行的"项目结构"写着：

```
HarnessCraft/
├── posts/
├── .devin/             # 工程化落地实践
│   ├── skills/         # 可复用 Skills（配图、任务执行、反思等）
│   ├── rules/          # 全局规则（Rollback、记忆、反思等）
```

并且第 160 行明确说：**"如果你对文章中提到的 Skills、Rules、Workflows 感兴趣，可以直接查看 `.devin/` 目录下的工程化实现。"**

但事实是：

```bash
git ls-files | grep devin        # 空
grep -n "devin" .gitignore       # .devin/   ← 被显式排除
```

`.devin/` 被作者当作"本机私有配置"排除了，**没有随仓库发布**。
于是仓库最核心的差异化价值（"不只是文章，还包含经过实际验证的 Skills / Rules / Workflows"）
在读者侧**完全拿不到**，README 的这句话目前是**失效指引**。

建议（**待作者决定**，两种都合理）：

1. 真的开放：另建 `harness/`（或 `examples/`）目录，把可公开的 Skills / Rules / Workflows 脱敏后放进去，
   并在 README 里改成指向新路径；
2. 暂时不开放：把 README 里"项目结构"的 `.devin/` 段落和"可以直接查看 `.devin/` 目录"的句子改掉，
   改成"这部分为作者本机私有 Harness，暂不公开；文章里已给出关键实现思路"，避免读者白找。

本次我只做了 **事实性修补**：README 结构树改为与仓库实际一致，并注明 `.devin/` 为本地私有、不入库。

---

## 3. 工程化缺口

| 缺口 | 证据 | 影响 |
| --- | --- | --- |
| 没有任何 CI | 分析前仓库无 `.github/` 目录 | CONTRIBUTING 里写着"确保所有 CI 检查通过"，但一条流水线都没有 |
| 没有 issue / PR 模板 | 同上 | 读者反馈格式各异，"文章勘误"和"站点 bug"混在一起 |
| 没有文章模板 | 头部 11 份 blockquote 靠手抄 | 作者自己已经踩过：提交 `1baab58`/`a77475e` 就是"改头部模板"式的批量同步 |
| `AGENTS.md` 是占位文件 | 全文 2 行，内容是"OpenMemory 暂时关闭" | 对 Agent 读者没有信息量；本仓库的 AI 协作规则无处可寻 |
| 没有版本化归档 | `git tag \| wc -l` = 0 | 与自家方法论 ISIER 的 Refl 层要求（"生成带版本号的归档文档"）不一致 |
| 没有站点 | 仓库只有 `.md` | 读者只能在 GitHub 上翻源码，无法直接阅读/订阅 |
| 无 CHANGELOG / CODE_OF_CONDUCT | 根目录只有 README / CONTRIBUTING / LICENSE | CONTRIBUTING 提到"行为准则"却没有独立文件（可接受，属轻微） |

---

## 4. 本次已补齐的内容（可直接合并）

### 4.1 免费托管站点（GitHub Pages，零成本）

- `mkdocs.yml` + `requirements.txt`：MkDocs Material（中文 search、标签/归档、深/浅色、`[TOC]` 渲染、RSS）
- `tools/build_site.py`：**posts/ 仍是唯一真源**，构建时生成 `docs/`（不入库），
  自动补 front matter（日期来自 git、分类来自 README、slug 用拼音）、自动跳过空文（标 draft）、
  并在构建时就做内容体检（README 表 ↔ posts/ 双向核对、slug 冲突、缺头部模板、取不到日期）
- `site-assets/stylesheets/extra.css`：中文字体栈（不加载 Google Fonts，国内可访问）、行宽/字重/表格优化
- GitHub Pages 本地无依赖产物验证：11 篇 → 发布 10 篇，RSS 10 条，sitemap 25 条 URL，`mkdocs build --strict` 零警告

### 4.2 CI / CD

- `.github/workflows/deploy-pages.yml`：push main → 生成 → `mkdocs build --strict` → 发布 Pages
- `.github/workflows/content-check.yml`：PR 上跑内容体检 + 严格构建（断链、锚点、模板缺失直接失败）

### 4.3 协作入口

- `.github/ISSUE_TEMPLATE/content_fix.yml`（文章勘误，要求给依据）
- `.github/ISSUE_TEMPLATE/site_bug.yml`（站点/工程问题）
- `.github/ISSUE_TEMPLATE/config.yml`、`.github/PULL_REQUEST_TEMPLATE.md`（含"回滚方案"必填项，呼应 fallback-first）
- `templates/文章模板.md`：把 11 篇共用的头部模板固化成唯一出处 + 发布检查清单
  （".devin/ 私有"这条也已写进 CONTRIBUTING 与本文档）

### 4.4 文档

- `README.md`：新增"在线阅读 / 本地预览"章节，结构树与仓库实际对齐
- `CONTRIBUTING.md`：新增"文章贡献流程 / 本地预览 / 站点发布 / Agent 协作约定"
- 本文件：`analysis/gap-analysis.md`

### 4.5 未能完成 / 需作者确认

- `AGENTS.md` 的正文重写被本机安全策略拦下（该文件属受保护的 agent 指令文件，需作者本人确认后才可写）。
  本次改把同等内容写进 `CONTRIBUTING.md` 的"Agent 协作约定"一节。
- `.devin/` 是否开放：**待作者决定**（见第 2 节）。

---

## 5. 建议的后续动作（按性价比排序）

1. **补第 6 篇**（`AI自验证并纠错通宵跑完任务，我只负责验收`）：系列里唯一的空文，且主题（AI 自验证 + 通宵跑任务）是读者最想要的那种实操文。
2. **统一编号体系**：README 序号 ↔ 文章"第X章毕"二者取一（第 1 节 P0-2）。
3. **决定 `.devin/` 的公开边界**：开放则新建 `harness/` 并改 README；不开放则改掉 README 的失效指引。
4. **打版本 tag**：例如 `v1.0-系列首发`，配套 GitHub Release，和自家 ISIER 的归档要求闭环。
5. **配图去单点依赖**：把 Cloudinary 图片按 `assets/posts/<slug>/` 落进仓库，或至少导出包一份备份。
6. **给站点配自定义域名**（可选，仍是免费的）：`CNAME` 文件 + 域名解析，Pages 侧无需付费。
7. **补文章摘要**：每篇开头加 1～2 句"读完你能拿到什么"，分享与 RSS 摘要都受益。
