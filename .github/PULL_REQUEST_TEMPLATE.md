<!-- 感谢贡献！PR 请聚焦单一改动，方便 review 和回滚 -->

## 改动内容

<!-- 一句话说清改了什么、为什么改 -->

## 类型

- [ ] 文章内容（新增 / 修订 posts/*.md）
- [ ] 站点与工程（tools/、mkdocs.yml、.github/、site-assets/）
- [ ] 文档（README、CONTRIBUTING、AGENTS）

## 自检清单

- [ ] 若新增文章：已放进 `posts/`，并已在 README「系列文章」表登记一行
- [ ] 若新增文章：保留了头部 blockquote（作者简介）与 `[TOC]`
- [ ] 本地跑过 `python3 tools/build_site.py --check --strict`（无警告/错误）
- [ ] 本地跑过 `python3 tools/build_site.py && mkdocs build --strict`
- [ ] 没有提交 `docs/`、`site/`、`.venv/`、任何凭据或 `.env`

## 回滚方案

<!-- Harness 硬约束：任何改动都要写清怎么回退（revert 提交 / 恢复哪个文件即可） -->
