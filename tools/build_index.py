#!/usr/bin/env python3
"""扫描 cases/，生成全量索引、各系列的 README，并更新根 README 里的统计。

只用标准库。目录约定：cases/<系列>/<分组>/<案例>/case.json
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "cases"
README = ROOT / "README.md"
START, END = "<!-- cases:start -->", "<!-- cases:end -->"

SERIES_TITLES = {
    "wechat-stickers": "微信表情包",
    "cards": "光栅变画卡",
    "posters": "动态海报",
    "signatures": "动态签名",
    "storybooks": "动态绘本",
    "reactions": "反应类 GIF",
    "memes": "梗图 GIF",
    "product": "产品演示 GIF",
    "kid-drawings": "孩子画动图",
}
ROUTE_LABELS = {"atlas": "图集轻动效", "frames": "六帧序列图", "native": "原生 GIF"}
STATUS_LABELS = {"draft": "草稿", "ready": "成品", "submitted": "已提交", "published": "已上架", "rejected": "被拒"}


def visible_dirs(folder: Path) -> list[Path]:
    return sorted(d for d in folder.iterdir() if d.is_dir() and not d.name.startswith(("_", ".")))


def inspiration_status() -> dict[str, str]:
    """灵感池里每条的状态，给 inspired_by 校验用。"""
    pool = ROOT / "inspiration"
    out = {}
    if pool.exists():
        for d in visible_dirs(pool):
            path = d / "item.json"
            if path.exists():
                it = json.loads(path.read_text(encoding="utf-8"))
                out[it.get("id", "")] = it.get("status", "")
    return out


def collect() -> tuple[list[dict], list[str]]:
    cases, errors = [], []
    pool = inspiration_status()
    seen: dict[str, str] = {}
    for series in visible_dirs(CASES):
        for group in visible_dirs(series):
            pack = {}
            if (group / "pack.json").exists():
                pack = json.loads((group / "pack.json").read_text(encoding="utf-8"))
            for case_dir in visible_dirs(group):
                meta_path = case_dir / "case.json"
                if not meta_path.exists():
                    continue
                rel = case_dir.relative_to(ROOT).as_posix()
                try:
                    meta = json.loads(meta_path.read_text(encoding="utf-8"))
                except json.JSONDecodeError as exc:
                    errors.append(f"{rel}/case.json 不是合法 JSON：{exc}")
                    continue
                case_id = meta.get("id", "")
                if not case_id:
                    errors.append(f"{rel} 没有 id")
                    continue
                if case_id in seen:
                    errors.append(f"编号 {case_id} 重复：{seen[case_id]} 和 {rel}")
                    continue
                if not case_dir.name.startswith(case_id):
                    errors.append(f"{rel} 的目录名应以编号 {case_id} 开头")
                seen[case_id] = rel
                src = meta.get("inspired_by")
                if src and pool.get(src) not in ("approved", "landed"):
                    errors.append(f"{rel} 的灵感来源 {src} " + ("不在灵感池里" if src not in pool else
                                  f"还没审批通过（{pool[src]}），不能落成案例，已从索引里剔除"))
                    continue
                engine = meta.get("engine", {})
                cases.append({
                    "id": case_id,
                    "title": meta.get("title", ""),
                    "series": series.name,
                    "group": group.name,
                    "character": pack.get("character", ""),
                    "meaning": meta.get("meaning", ""),
                    "tags": meta.get("tags", []),
                    "route": meta.get("route", ""),
                    "model": engine.get("model", ""),
                    "quality": engine.get("quality", ""),
                    "channel": engine.get("channel", ""),
                    "cost": meta.get("cost", {}),
                    "checks": meta.get("checks", {}),
                    "status": meta.get("status", "draft"),
                    "review_status": pack.get("review_status", ""),
                    "created": meta.get("created", ""),
                    "inspired_by": meta.get("inspired_by"),
                    "path": rel,
                    "gif": f"{rel}/result.gif" if (case_dir / "result.gif").exists() else None,
                    "prompt": f"{rel}/prompt.md" if (case_dir / "prompt.md").exists() else None,
                })
    cases.sort(key=lambda c: (c["series"], c["id"]))
    return cases, errors


def series_readme(series: str, cases: list[dict]) -> str:
    title = SERIES_TITLES.get(series, series)
    lines = [f"# {title}", "",
             f"共 {len(cases)} 个案例。本页由 `tools/build_index.py` 生成，不要手改。", ""]
    if not cases:
        lines += ["还没有案例。", ""]
        return "\n".join(lines)

    groups: dict[str, list[dict]] = {}
    for case in cases:
        groups.setdefault(case["group"], []).append(case)
    for group, items in groups.items():
        name = items[0]["character"] or group
        review = items[0]["review_status"]
        lines += [f"## {name}（{len(items)} 个{'，审核：' + review if review else ''}）", "",
                  "| 编号 | 预览 | 案例 | 含义词 | 路线 | 型号 | 状态 |", "|---|---|---|---|---|---|---|"]
        for case in items:
            here = case["path"].split("/", 2)[2]  # 相对于系列目录
            preview = f'<img src="{here}/result.gif" width="80">' if case["gif"] else "—"
            model = " ".join(x for x in (case["model"], case["quality"]) if x)
            lines.append(f"| {case['id']} | {preview} | [{case['title']}]({here}/) | {case['meaning']} | "
                         f"{ROUTE_LABELS.get(case['route'], case['route'])} | {model} | "
                         f"{STATUS_LABELS.get(case['status'], case['status'])} |")
        lines.append("")
    return "\n".join(lines)


def root_block(cases: list[dict], series_names: list[str]) -> str:
    by_series = Counter(c["series"] for c in cases)
    published = sum(1 for c in cases if c["status"] == "published")
    lines = [START, f"案例总数：**{len(cases)}**（已上架 {published}）", "",
             "| 系列 | 案例数 | 索引 |", "|---|---|---|"]
    for name in series_names:
        lines.append(f"| {SERIES_TITLES.get(name, name)} | {by_series.get(name, 0)} | [查看](cases/{name}/README.md) |")
    lines.append(END)
    return "\n".join(lines)


def main() -> int:
    cases, errors = collect()
    series_names = [d.name for d in visible_dirs(CASES)]

    (CASES / "index.json").write_text(
        json.dumps({"total": len(cases), "cases": cases}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name in series_names:
        (CASES / name / "README.md").write_text(
            series_readme(name, [c for c in cases if c["series"] == name]), encoding="utf-8")

    text = README.read_text(encoding="utf-8")
    if START in text and END in text:
        head, rest = text.split(START, 1)
        tail = rest.split(END, 1)[1]
        README.write_text(head + root_block(cases, series_names) + tail, encoding="utf-8")
    else:
        errors.append(f"README.md 里没有 {START} … {END} 标记，统计没有更新")

    print(f"{len(cases)} 个案例，{len(series_names)} 个系列")
    for error in errors:
        print(f"ERROR {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
