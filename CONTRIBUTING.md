# 贡献指南

感谢您对 HarnessCraft 项目的关注！我们欢迎各种形式的贡献。

## 如何贡献

### 报告问题

如果您发现了 bug 或有功能建议，请在 [GitHub Issues](https://github.com/huanqwer/HarnessCraft/issues) 中提交。

提交 issue 时，请尽可能提供：
- 清晰的描述
- 复现步骤
- 预期行为
- 实际行为
- 环境信息（操作系统、版本等）

### 提交代码

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

### 代码规范

- 请确保代码风格与项目保持一致
- 添加必要的注释和文档
- 确保代码通过所有测试（如有）
- 更新相关文档

### Pull Request 指南

- 保持 PR 聚焦于单一问题或功能
- 在 PR 描述中清晰说明更改内容
- 引用相关的 issue（如有）
- 确保所有 CI 检查通过

## 贡献文章

文章的唯一真源是 `posts/`，站点（GitHub Pages）由它自动生成——**不要另建正文副本**。

1. 从模板开始：`cp templates/文章模板.md "posts/你的文章标题.md"`（文件名即文章标题，保持平铺，不按章节建目录）
2. 保留头部 blockquote（作者简介）与 `[TOC]` 标记，正文写在 `---` 之后
3. 在 `README.md` 的「系列文章」表格登记一行：`| 序号 | [标题](posts/文件名.md) | 主题 |`
4. 章节收尾沿用 `> 第X章毕`（中文数字）；配图用技术图表风格，不用表情包
5. 本地自检 + 预览（见下一节），再提 PR

## 本地预览与站点构建

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python3 tools/build_site.py --check --strict   # 内容体检：README 表 ↔ posts/ 双向核对、slug 冲突、缺头部模板
python3 tools/build_site.py                    # 生成站点源 docs/（构建产物，不入库）
mkdocs serve                                   # 本地预览 http://127.0.0.1:8000
mkdocs build --strict                          # 生成 site/，断链/锚点问题会直接失败
```

- 站点的 front matter（日期 / 分类 / slug）由脚本自动补：日期取该文件的 git 首次提交日期，
  分类取 README 的「主题」列，slug 取标题拼音。**不要在文章里手写这些元数据**。
- `docs/`、`site/`、`.venv/` 均已在 `.gitignore` 中，请不要提交。

## Agent 协作约定

本仓库经常由 AI Agent 参与维护，请遵守以下约定（同样的规则适用于人类贡献者）：

| 路径 | 性质 | 能否手改 |
| --- | --- | --- |
| `posts/*.md` | 文章唯一真源 | ✅ 只改这里 |
| `README.md` | 系列顺序 + 主题分类，站点导航的数据来源 | ✅ 新增文章必须登记 |
| `templates/`、`tools/`、`site-assets/` | 模板、生成器、站点资源 | ✅ |
| `docs/`、`site/` | 构建产物 | ❌ 会被覆盖，且不入库 |
| `.devin/` | 作者本机私有配置 | ❌ 不入库 |

硬约束：

1. **不臆造事实**：日期、分类、标签都从仓库既有信息推导，不要编造日期、估时或数据。
2. **不改文章语义**：批量格式化前先确认；被告知"只是排版"时也不要顺手改措辞。
3. **提交前必跑**：`python3 tools/build_site.py --check --strict` 与 `mkdocs build --strict`（CI 同样会跑）。
4. **不提交凭据**：Cloudinary、token、`.env*` 一律不入库。
5. **有副作用的动作先给清单**：推送、改 Pages 设置、改仓库可见性之前，先列出将要发生什么并等确认。

## 行为准则

请保持友善和尊重。我们致力于为所有人提供开放、友好的环境。

## 许可证

通过贡献代码，您同意您的贡献将根据项目的 MIT 许可证进行授权。
