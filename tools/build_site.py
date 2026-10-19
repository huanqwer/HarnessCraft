#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 posts/ 下的文章构建成 MkDocs 站点源（docs/）。

设计约束（与仓库现状对齐）：

1. posts/ 是文章唯一真源（SSOT），docs/ 每次构建重新生成、不入库（见 .gitignore）。
2. 不改写文章正文，只做两件事：取出正文首行 H1 作为标题、补一段 YAML front matter。
3. front matter 的每个字段都来自仓库内可核查的信息，不臆造：
   - 标题  ：文章首行 H1
   - 日期  ：git 中该文件（含重命名前身）的首次提交日期
   - 分类  ：README「系列文章」表的「主题」列
   - slug  ：标题的拼音转写（ASCII、稳定、可读）
   - 作者  ：文章头部 blockquote 中已有的作者简介
4. 正文实质内容过短的文章（例如只有模板头）自动标为 draft，不让站点出现空页面；
   草稿仍在 sync 报告里列出来，方便补完。

用法：
    python3 tools/build_site.py           # 生成 docs/
    python3 tools/build_site.py --check   # 只做内容体检，不写任何文件（CI 用）
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from pypinyin import lazy_pinyin
except ImportError:  # pragma: no cover
    sys.exit(
        "缺少依赖 pypinyin。请先准备环境：\n"
        "  python3 -m venv .venv && source .venv/bin/activate\n"
        "  pip install -r requirements.txt"
    )

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "posts"
DOCS_DIR = ROOT / "docs"
ASSETS_DIR = ROOT / "site-assets"
README = ROOT / "README.md"

AUTHOR_KEY = "laolata"
# 正文中文字符数低于该值时视为"只有模板头"的草稿
DRAFT_MIN_CJK = 50

# README 系列文章表：| 序号 | [标题](posts/xxx.md) | 主题 |
SERIES_ROW = re.compile(
    r"^\|\s*(\d+)\s*\|\s*\[([^\]]+)\]\((posts/[^)]+)\)\s*\|\s*([^|]+?)\s*\|\s*$"
)
H1 = re.compile(r"^#\s+(.+?)\s*$")
CJK = re.compile(r"[\u4e00-\u9fff]")

warnings: list = []
errors: list = []
notes: list = []


# --------------------------------------------------------------------------
# 基础工具
# --------------------------------------------------------------------------
def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def yaml_str(value: str) -> str:
    """用 JSON 引号输出，保证中文/引号/冒号都不会破坏 YAML。"""
    return json.dumps(value, ensure_ascii=False)


def git_first_commit_date(rel_path: str):
    """文件（含 --follow 重命名前身）在 git 中的首次提交日期 YYYY-MM-DD。"""
    try:
        out = subprocess.run(
            [
                "git", "log", "--follow", "--diff-filter=A",
                "--date=short", "--format=%ad", "--", rel_path,
            ],
            cwd=str(ROOT), capture_output=True, text=True, check=True,
        ).stdout.split()
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:  # pragma: no cover
        errors.append("读取 git 历史失败：%s" % exc)
        return None
    return out[-1] if out else None


def slugify(title: str) -> str:
    slug = "-".join(lazy_pinyin(title))
    slug = re.sub(r"[^0-9A-Za-z]+", "-", slug).strip("-").lower()
    slug = re.sub(r"-{2,}", "-", slug)
    return slug[:80].strip("-")


# --------------------------------------------------------------------------
# 解析
# --------------------------------------------------------------------------
def parse_readme_series():
    """解析 README 的「系列文章」表 -> [{order, title, path, category}]"""
    text = read(README)
    start = text.find("## 系列文章")
    end = text.find("## 贡献")
    if start < 0:
        errors.append("README.md 找不到「## 系列文章」章节")
        return []
    block = text[start:end if end > start else len(text)]
    rows = []
    for line in block.splitlines():
        m = SERIES_ROW.match(line.strip())
        if m:
            rows.append(
                {
                    "order": int(m.group(1)),
                    "title": m.group(2).strip(),
                    "path": m.group(3).strip(),
                    "category": m.group(4).strip(),
                }
            )
    if not rows:
        errors.append("README.md「系列文章」表未解析到任何行")
    return rows


def parse_author_bio():
    """从任意一篇文章头部取出作者简介 blockquote 的正文行。"""
    for post in sorted(POSTS_DIR.glob("*.md")):
        bio, in_bio = [], False
        for line in read(post).splitlines():
            if line.startswith(">"):
                if "**作者" in line:
                    in_bio = True
                    continue
                if in_bio:
                    bio.append(line.lstrip("> ").strip())
            elif in_bio:
                break
        if bio:
            return bio
    warnings.append("未在文章头部找到作者简介 blockquote，关于页面将退化")
    return []


def real_content_cjk(body: str) -> int:
    """正文里去掉模板头/TOC/分隔线后的中文字符数。"""
    keep = []
    for line in body.splitlines():
        s = line.strip()
        if not s or s.startswith(">") or s in ("[TOC]", "---", "***", "___"):
            continue
        keep.append(s)
    return len(CJK.findall("".join(keep)))


def load_post(path: Path, series_by_path: dict):
    text = read(path)
    lines = text.splitlines()
    title, body = None, text
    for i, line in enumerate(lines):
        m = H1.match(line)
        if m:
            title = m.group(1).strip()
            body = "\n".join(lines[i + 1:]).lstrip("\n")
            break
    if not title:
        title = path.stem
        warnings.append("%s：缺少一级标题（H1），已用文件名兜底" % path.name)

    rel = path.relative_to(ROOT).as_posix()
    meta = series_by_path.get(rel) or series_by_path.get(path.name)
    if not meta:
        warnings.append("%s：未出现在 README「系列文章」表中，分类记为「未分类」" % rel)
    category = meta["category"] if meta else "未分类"
    order = meta["order"] if meta else 999

    date = git_first_commit_date(rel)
    if not date:
        warnings.append("%s：取不到 git 首次提交日期，回退为 1970-01-01" % rel)
        date = "1970-01-01"

    cjk = real_content_cjk(body)
    draft = cjk < DRAFT_MIN_CJK
    if draft:
        notes.append(
            "%s：正文实质内容仅 %d 个中文字（疑似只有模板头），站点上标为草稿隐藏" % (rel, cjk)
        )
    if "**作者" not in text:
        warnings.append("%s：缺少文章头部模板中的作者简介 blockquote（见 templates/文章模板.md）" % rel)

    return {
        "file": path,
        "rel": rel,
        "title": title,
        "body": body,
        "date": date,
        "category": category,
        "order": order,
        "slug": slugify(title),
        "draft": draft,
        "cjk": cjk,
    }


# --------------------------------------------------------------------------
# 生成
# --------------------------------------------------------------------------
def front_matter(post: dict) -> str:
    out = ["---"]
    out.append("title: %s" % yaml_str(post["title"]))
    out.append("date: %s" % post["date"])
    out.append("categories:")
    out.append("  - %s" % yaml_str(post["category"]))
    out.append("authors:")
    out.append("  - %s" % AUTHOR_KEY)
    out.append("slug: %s" % yaml_str(post["slug"]))
    out.append("description: %s" % yaml_str(
        "Harness 工程化落地实践系列 · %s · %s" % (post["category"], post["title"])
    ))
    if post["draft"]:
        out.append("draft: true")
    out.append("---")
    return "\n".join(out)


def page_series_table(posts: list, link_prefix: str) -> str:
    has_draft = any(p["draft"] for p in posts)
    head = "| 序号 | 文章 | 主题 | 日期 |"
    sep = "| --- | --- | --- | --- |"
    if has_draft:
        head = "| 序号 | 文章 | 主题 | 日期 | 状态 |"
        sep = "| --- | --- | --- | --- | --- |"
    rows = [head, sep]
    for p in sorted(posts, key=lambda x: x["order"]):
        if p["draft"]:
            cells = [p["title"], p["category"], p["date"], "待补完"]
        else:
            cells = [
                "[%s](%s%s.md)" % (p["title"], link_prefix, p["slug"]),
                p["category"],
                p["date"],
            ]
        rows.append("| %d | %s |" % (p["order"], " | ".join(cells)))
    return "\n".join(rows)


def build_index(posts: list, readme_text: str) -> str:
    intro = "一套完整的 Harness 工程化落地实践——不只是文章，更包含可直接使用并经过实际验证的 Skills、Rules、Workflows、Memories 和工程结构。"
    m = re.search(r"^一套完整的.*?工程结构。\s*$", readme_text, re.M)
    if m:
        intro = m.group(0).strip()
    audience = re.search(r"适合人群\s*\n+(?P<body>(?:[ \t]*\*.*\n?)+)", readme_text)
    published = [p for p in posts if not p["draft"]]
    drafts = len(posts) - len(published)
    latest = max((p["date"] for p in published), default="")
    meta = ["**Harness 工程化落地实践**", "已发布 %d 篇" % len(published)]
    if drafts:
        meta.append("%d 篇待补完" % drafts)
    meta += ["最近更新 %s" % latest, "MIT License"]
    lines = [
        "---",
        "hide:",
        "  - navigation",
        "---",
        "",
        "# HarnessCraft",
        "",
        " · ".join(meta),
        "",
        intro,
        "",
        "!!! quote \"这套方法论在做什么\"",
        "    用完善的 Harness（Rules / Skills / Workflows / Memories / 工程结构）约束 AI Agent，",
        "    让它在低成本模型上也能稳定交付商业级应用——博主所在的 5 人团队已实现 0 手写代码交付。",
        "",
        "## 系列文章",
        "",
        page_series_table(posts, "blog/posts/"),
        "",
        "## 读前先看",
        "",
        "- [ISIER 五层落地架构](blog/posts/%s.md)：Intent 意图 → Spec 契约 → Impl 执行 → Eval 验收 → Refl 反思，Rollback 横切全层。"
        % next((p["slug"] for p in posts if "五层架构" in p["title"]), ""),
        "- [实践案例](blog/posts/%s.md)：真实企业内部的 Harness + FDE 改造如何落地。"
        % next((p["slug"] for p in posts if "FDE" in p["title"]), ""),
        "- 仓库里的 `posts/` 是文章真源，站点由 `tools/build_site.py` + MkDocs 自动生成。",
        "",
    ]
    if audience:
        lines += ["## 适合人群", "", audience.group("body").rstrip(), ""]
    lines += [
        "## 参与",
        "",
        "- 项目主页：<https://github.com/huanqwer/HarnessCraft>",
        "- 发现文章错误或有想补充的实践，欢迎开 [Issue](https://github.com/huanqwer/HarnessCraft/issues) 或 PR。",
        "- 订阅更新：[RSS](https://huanqwer.github.io/feed_rss_created.xml)",
        "",
    ]
    return "\n".join(lines)


def build_series(posts: list) -> str:
    return "\n".join(
        [
            "---",
            "hide:",
            "  - navigation",
            "---",
            "",
            "# 系列文章",
            "",
            "按推荐阅读顺序排列（顺序取自仓库 README，日期取自每篇文章的 git 首次提交）。",
            "点击标题即可进入正文；也可以在 [文章列表](blog/index.md) 按时间浏览、按分类筛选。",
            "",
            page_series_table(posts, "blog/posts/"),
            "",
            "> 新文章只需要把 `.md` 放进 `posts/` 并在 README 表格里登记一行，站点会自动收录。",
            "",
        ]
    )


def build_about(bio: list) -> str:
    lines = [
        "# 关于作者",
        "",
        "## 老邋遢（笔名）",
        "",
    ]
    lines += [line + "  " if line else line for line in bio]
    lines += [
        "",
        "## 联系方式",
        "",
        "- 项目主页：<https://github.com/huanqwer/HarnessCraft>",
        "- GitHub：<https://github.com/huanqwer>",
        "- 邮箱：huanqwer0314@gmail.com",
        "",
        "## 许可证",
        "",
        "本站文章与仓库内容采用 MIT 许可证，转载请注明出处。",
        "",
    ]
    return "\n".join(lines)


def build_authors_yml(bio: list) -> str:
    """注意：mkdocs-material 9.7.7 的 .authors.yml 需要 `authors:` 顶层键，
    且每项必须提供 name / description / avatar 三个字段，否则构建直接报错。"""
    desc = " / ".join(bio[:3]) if bio else "Harness 工程化实践作者"
    return "\n".join(
        [
            "# 作者信息（站点构建时从文章头部的作者简介同步生成）",
            "authors:",
            "  %s:" % AUTHOR_KEY,
            "    name: %s" % yaml_str("老邋遢"),
            "    description: %s" % yaml_str(desc),
            "    avatar: %s" % yaml_str("https://github.com/huanqwer.png?size=120"),
        ]
    )


# --------------------------------------------------------------------------
# 主流程
# --------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description="从 posts/ 生成 MkDocs 站点源 docs/")
    ap.add_argument("--check", action="store_true", help="只做内容体检，不写文件")
    ap.add_argument("--strict", action="store_true", help="把警告也当作失败（CI 用）")
    args = ap.parse_args()

    if not POSTS_DIR.is_dir():
        errors.append("找不到 posts/ 目录")
        return report()

    readme_text = read(README) if README.exists() else ""
    series = parse_readme_series()
    by_path = {row["path"]: row for row in series}
    by_name = {Path(row["path"]).name: row for row in series}

    posts = [load_post(p, {**by_path, **by_name}) for p in sorted(POSTS_DIR.glob("*.md"))]
    posts.sort(key=lambda p: (p["order"], p["title"]))

    listed = {Path(row["path"]).name for row in series}
    on_disk = {p.name for p in POSTS_DIR.glob("*.md")}
    for missing in sorted(listed - on_disk):
        errors.append("README 系列文章表登记了 %s，但 posts/ 下不存在该文件" % missing)
    for extra in sorted(on_disk - listed):
        warnings.append("posts/%s 未登记进 README 系列文章表（不会出现在系列导航里）" % extra)

    dupes = {}
    for p in posts:
        dupes.setdefault(p["slug"], []).append(p["title"])
    for slug, titles in dupes.items():
        if len(titles) > 1:
            errors.append("slug 冲突 %s：%s" % (slug, " / ".join(titles)))

    if not args.check:
        if DOCS_DIR.exists():
            shutil.rmtree(DOCS_DIR)
        (DOCS_DIR / "blog" / "posts").mkdir(parents=True, exist_ok=True)
        if ASSETS_DIR.is_dir():
            shutil.copytree(ASSETS_DIR, DOCS_DIR / "assets")
        bio = parse_author_bio()
        for p in posts:
            (DOCS_DIR / "blog" / "posts" / ("%s.md" % p["slug"])).write_text(
                front_matter(p) + "\n\n" + p["body"].rstrip() + "\n", encoding="utf-8"
            )
        (DOCS_DIR / "index.md").write_text(build_index(posts, readme_text), encoding="utf-8")
        (DOCS_DIR / "series.md").write_text(build_series(posts), encoding="utf-8")
        (DOCS_DIR / "about.md").write_text(build_about(bio), encoding="utf-8")
        (DOCS_DIR / "blog" / ".authors.yml").write_text(build_authors_yml(bio), encoding="utf-8")

    print("== 站点内容体检 ==")
    print("文章总数：%d（其中草稿/待补完：%d）" % (len(posts), sum(1 for p in posts if p["draft"])))
    print("中文正文字数合计：%d" % sum(p["cjk"] for p in posts))
    for p in posts:
        print(
            "  %2d. %s  [%s] %s  %s"
            % (
                p["order"], p["date"], p["category"],
                "草稿" if p["draft"] else "正常", p["title"],
            )
        )
    if not args.check:
        print("已生成站点源：%s" % DOCS_DIR.relative_to(ROOT))
    return report(strict=args.strict)


def report(strict: bool = False) -> int:
    for n in notes:
        print("INFO  %s" % n)
    for w in warnings:
        print("WARN  %s" % w, file=sys.stderr)
    for e in errors:
        print("ERROR %s" % e, file=sys.stderr)
    if errors or (strict and warnings):
        return 1
    print("体检通过（%d 条警告，%d 条提示，0 条错误）" % (len(warnings), len(notes)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
