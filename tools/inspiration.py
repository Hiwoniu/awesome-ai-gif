#!/usr/bin/env python3
"""灵感池：收集全网看到的好 case，审批通过后才能拿来用。只用标准库。

  inspiration.py add --title "xx 的光栅卡" --url https://… --type cards --why "竖条翻转很顺"
  inspiration.py review insp-003 approve --by 向明 --note "借翻转手法，角色换橘团"
  inspiration.py review insp-004 reject  --by 向明 --note "真人肖像"
  inspiration.py land insp-003 cd-001          # 记下它落成了哪个案例（或试做目录）
  inspiration.py board                         # 校验并重新生成 inspiration/README.md 看板（不带子命令也是它）

状态：pending 待审 → approved 已通过 / rejected 驳回 / parked 搁置；approved 落成案例后 → landed 已落地。
收进来默认 pending，pending、parked、rejected 的都不能用。approve 只能由仓库主人本人做，
Agent 不能自己批，只有用户在对话里明确说“通过 insp-xxx”时才代为执行，并写上用户的名字。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POOL = ROOT / "inspiration"
README = POOL / "README.md"
START, END = "<!-- board:start -->", "<!-- board:end -->"

STATUS = {"pending": "待审", "approved": "已通过", "landed": "已落地", "parked": "搁置", "rejected": "驳回"}
USABLE = {"approved", "landed"}
DECISIONS = {"approve": "approved", "reject": "rejected", "park": "parked", "reopen": "pending"}
ROOT_README = ROOT / "README.md"
TOPIC_DIR = POOL / "topics"
R_START, R_END = "<!-- inspiration:start -->", "<!-- inspiration:end -->"

# 主题：给人浏览用的分类，比 type 细。按顺序匹配，先中先得；item.json 里写了 "topic" 就以它为准。
# 每项：代号、名称、能借到什么、我们自己做出来的图（[] 是这类还没做，None 是这类不产出图；别人的图不放）、匹配规则。
_T = lambda it: " ".join([it.get("title", ""), it.get("what", ""), " ".join(it.get("tags") or []), " ".join(it.get("borrow") or [])])
_P = lambda it: (it.get("source") or {}).get("platform") or ""
TOPICS = [
    ("signatures", "动态签名", "签名卡的规格、首帧能独立成图、逐字出现的时序", [],
     lambda it, t: it.get("type") == "signatures" or re.search(r"签名", it.get("title", ""))),
    ("storybooks", "动态绘本", "每页只做一个动作的拆页法、跨页角色一致、微动而不是大动作", [],
     lambda it, t: it.get("type") == "storybooks" or re.search(r"绘本", it.get("title", ""))),
    ("cards", "光栅卡、全息卡与贺卡", "两态对齐、翻转节奏、共享调色板、节日题材",
     ["trials/2026-11-18-gif-factory-styles/card/result.gif"],
     lambda it, t: it.get("type") == "cards" or re.search(r"光栅|全息|闪卡|贺卡", it.get("title", ""))),
    ("skills", "开源 Skill 与工具", "别人的 Skill 怎么拆步骤、怎么做机检、怎么组织脚本和规格配置", None,
     lambda it, t: "Skill" in (it.get("tags") or []) or re.search(r"Skill|MCP|CLI|开源", it.get("title", ""))
     or re.search(r"GitHub|PyPI|Skills Directory|SkillHub|Hugging Face", _P(it))),
    ("sketch", "手绘、涂鸦变动图", "保留原笔触的提示思路、先净化成角色再加动作、孩子的画怎么动起来", [],
     lambda it, t: re.search(r"涂鸦|草图|素描|手绘|线稿|儿童画|孩子", it.get("title", ""))),
    ("video", "视频模型与无缝循环", "首尾同帧、藏接缝、补帧这些循环技法；我们只借思路，成品仍是 GIF", None,
     lambda it, t: re.search(r"AnimateDiff|ComfyUI|Wan[ -]?2|Seedance|Kling|可灵|Hailuo|海螺|SVD|LTX|CogVideo|图生视频|Veo|Sora|Runway|Higgsfield|Pika|FLF2V|Hotshot|视频模型|Grok 视频", t)),
    ("game", "游戏精灵与像素动画", "多方向精灵表、行走循环、锚点和帧计划；像素画风的出图顺序",
     ["trials/2026-11-18-gif-factory-styles/pixel/03-laugh/result.gif", "trials/2026-11-18-gif-factory-styles/pixel/08-shock/result.gif"],
     lambda it, t: re.search(r"游戏|八方向|8 方向|行走循环|Godot|Unity|Aseprite|RPG|tileset|像素", t, re.I)),
    ("code", "代码动效：Lottie、SVG、逐帧渲染", "不靠模型出图、用代码逐帧画的路线，适合文字和几何动效", None,
     lambda it, t: re.search(r"Lottie|SVG|CSS|HTML|Remotion|Rive|代码画|程序化|ASCII", t)),
    ("platforms", "其他平台贴纸：LINE、WhatsApp、Telegram、Discord", "各平台的尺寸、格式和上架流程，留给多平台规格用", None,
     lambda it, t: re.search(r"WhatsApp|LINE|Telegram|Discord|Kakao|Zalo|Twitch", t)),
    ("posters", "动态海报、产品图与局部动效", "只动一个元素其余锁死、字不动背景动、按节拍排场、首帧能当封面",
     ["trials/2026-11-18-gif-factory-styles/poster/result.gif"],
     lambda it, t: it.get("type") == "posters" or re.search(r"海报|Cinemagraph|影格|产品|Logo|品牌|二维码", it.get("title", ""))),
    ("wechat", "微信表情包：整套、上架与变现", "从定角色到投稿的全流程、素材规格、被拒原因、赞赏和定制的变现路径",
     ["trials/2026-11-16-codex-orange-cat/wx-001-greeting/result.gif", "trials/2026-11-17-remix-rabbit/wx-002-laugh/result.gif"],
     lambda it, t: re.search(r"微信|上架|投稿|变现|赞赏", t)),
    ("photo", "照片变表情：宠物、头像", "多张参考图锁角色、保长相只加微动、照片转 Q 版；真人部分不用，换自家宠物",
     ["trials/2026-11-18-duoduo/06-sneak/result.gif", "trials/2026-11-18-snail-cat-remix/13/result.gif"],
     lambda it, t: re.search(r"照片|自拍|宠物|头像|猫|狗", it.get("title", ""))),
    ("sheets", "图集与序列帧：九宫格、六帧、精灵表", "一张图画完整套或整段动作、切图避开网格线、末帧接回首帧",
     ["trials/2026-11-18-gif-factory-styles/clay/01-wave/result.gif", "trials/2026-11-16-codex-orange-cat/wx-002-laugh/result.gif"],
     lambda it, t: re.search(r"精灵表|精灵图|sprite|九宫格|宫格|六帧|6 帧|序列帧|图集|4×4|3×3|3×2|网格", t, re.I)),
    ("tests", "实测、参数与避坑", "帧数和尺寸怎么配、成本多少、哪些动作会做坏、原生 GIF 的边界", None,
     lambda it, t: re.search(r"实测|参数|帧数|成本|失败|翻车|对比|横评|规格|边界|限制", it.get("title", ""))),
    ("prompts", "提示词模板与公式", "提示词分几段写、哪句管循环、哪句管一致性", None,
     lambda it, t: re.search(r"提示词", t)),
    ("misc", "其他教程与资讯", "入门教程、功能发布、工具页", None, lambda it, t: True),
]
TOPIC_NAMES = {k: n for k, n, *_ in TOPICS}
# 展示顺序：先放已经做出东西的类型，再放规划中的，最后是方法和资料
SHOW = ["wechat", "photo", "sheets", "posters", "cards", "game", "signatures", "storybooks", "sketch",
        "prompts", "tests", "skills", "video", "code", "platforms", "misc"]


def topic_of(it: dict) -> str:
    if it.get("topic") in TOPIC_NAMES:
        return it["topic"]
    t = _T(it)
    return next(k for k, _n, _d, _g, fn in TOPICS if fn(it, t))


TYPES = {"wechat-stickers": "微信表情包", "cards": "光栅变画卡", "posters": "动态海报",
         "signatures": "动态签名", "storybooks": "动态绘本", "multi": "多类型", "unknown": "未定"}


def item_dirs() -> list[Path]:
    return sorted(d for d in POOL.iterdir() if d.is_dir() and d != TOPIC_DIR and not d.name.startswith(("_", ".")))


def load_all() -> tuple[list[dict], list[str]]:
    items, errors, seen = [], [], {}
    for d in item_dirs():
        path = d / "item.json"
        if not path.exists():
            errors.append(f"{d.name}/ 没有 item.json")
            continue
        try:
            it = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{d.name}/item.json 不是合法 JSON：{exc}")
            continue
        it["_dir"] = d
        iid = it.get("id", "")
        if not d.name.startswith(iid + "-") and d.name != iid:
            errors.append(f"{d.name}/ 目录名要以编号 {iid} 开头")
        if iid in seen:
            errors.append(f"编号 {iid} 重复")
        seen[iid] = d.name
        st = it.get("status")
        if st not in STATUS:
            errors.append(f"{iid}: 状态 {st!r} 不认识，只能是 {', '.join(STATUS)}")
        if st in USABLE | {"rejected", "parked"} and not (it.get("review") or {}).get("by"):
            errors.append(f"{iid}: 状态是 {st} 但没有审批记录（review.by）")
        if st == "landed" and not it.get("landed"):
            errors.append(f"{iid}: 状态是 landed 但 landed 列表为空")
        if not it.get("source", {}).get("url"):
            errors.append(f"{iid}: 没有出处 source.url")
        items.append(it)
    return items, errors


def find(iid: str) -> dict:
    items, _ = load_all()
    for it in items:
        if it["id"] == iid:
            return it
    raise SystemExit(f"灵感池里没有 {iid}")


def save(it: dict) -> None:
    d = it.pop("_dir")
    (d / "item.json").write_text(json.dumps(it, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    it["_dir"] = d


def slugify(text: str) -> str:
    s = re.sub(r"[^0-9a-zA-Z]+", "-", text).strip("-").lower()
    return s[:40] or "item"


def cmd_add(args) -> int:
    items, _ = load_all()
    for it in items:
        if args.url and it.get("source", {}).get("url") == args.url:
            raise SystemExit(f"已经收过：{it['id']} {it['title']}")
    nums = [int(m.group(1)) for it in items if (m := re.fullmatch(r"insp-(\d+)", it.get("id", "")))]
    iid = f"insp-{(max(nums) + 1) if nums else 1:03d}"
    d = POOL / f"{iid}-{args.slug or slugify(args.url or args.title)}"
    d.mkdir(parents=True)
    tpl = json.loads((POOL / "_template/item.json").read_text(encoding="utf-8"))
    today = date.today().isoformat()
    tpl.update(id=iid, title=args.title, type=args.type, what=args.what, why=args.why,
               borrow=args.borrow, tags=args.tag, status="pending",
               history=[{"date": today, "status": "pending", "by": args.by, "note": "收进灵感池"}])
    tpl["source"].update(url=args.url, platform=args.platform, author=args.author, found_at=today, found_by=args.by)
    (d / "item.json").write_text(json.dumps(tpl, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (d / "notes.md").write_text((POOL / "_template/notes.md").read_text(encoding="utf-8"), encoding="utf-8")
    print(f"OK   {d.relative_to(ROOT)}：待审。补完 item.json 的 what/why/borrow/risks 和 notes.md，等审批")
    return board(quiet=True)


def cmd_review(args) -> int:
    it = find(args.id)
    new = DECISIONS[args.decision]
    if it["status"] == "landed" and new != "landed":
        raise SystemExit(f"{args.id} 已落地，不能再改审批结论")
    today = date.today().isoformat()
    it["status"] = new
    it["review"] = None if new == "pending" else {"decision": new, "by": args.by, "date": today, "note": args.note}
    it.setdefault("history", []).append({"date": today, "status": new, "by": args.by, "note": args.note})
    save(it)
    print(f"OK   {args.id}：{STATUS[new]}（{args.by}）")
    return board(quiet=True)


def cmd_land(args) -> int:
    it = find(args.id)
    if it["status"] not in USABLE:
        raise SystemExit(f"{args.id} 现在是“{STATUS[it['status']]}”，审批通过前不能落地")
    today = date.today().isoformat()
    it.setdefault("landed", []).append({"ref": args.ref, "date": today})
    it["status"] = "landed"
    it.setdefault("history", []).append({"date": today, "status": "landed", "by": args.by, "note": f"落成 {args.ref}"})
    save(it)
    print(f"OK   {args.id}：已落地 → {args.ref}。案例的 case.json 里记得写 \"inspired_by\": \"{args.id}\"")
    return board(quiet=True)


def render(items: list[dict]) -> str:
    count = Counter(it["status"] for it in items)
    lines = [START, "", "总数：**%d**（" % len(items) + "，".join(f"{STATUS[s]} {count.get(s, 0)}" for s in STATUS) + "）", ""]
    for st, label in STATUS.items():
        group = [it for it in items if it["status"] == st]
        if not group:
            continue
        lines += [f"### {label}（{len(group)}）", "", "| 编号 | 标题 | 类型 | 出处 | 借什么 | 审批 / 落地 |", "|---|---|---|---|---|---|"]
        for it in group:
            link = source_link(it)
            rv = it.get("review") or {}
            tail = f"{rv.get('by', '')} {rv.get('date', '')}".strip()
            if it.get("landed"):
                tail += "；→ " + "、".join(x["ref"] for x in it["landed"])
            rel = it["_dir"].relative_to(POOL).as_posix()
            lines.append(f"| [{it['id']}]({rel}/) | {it.get('title', '')} | {TYPES.get(it.get('type'), it.get('type'))} | "
                         f"{link} | {'、'.join(it.get('borrow') or []) or '—'} | {tail or '—'} |")
        lines.append("")
    lines.append(END)
    return "\n".join(lines)


def source_link(it: dict) -> str:
    src = it.get("source", {})
    if src.get("url", "").startswith("http"):
        return f"[{src.get('platform') or '链接'}]({src['url']})"
    return src.get("platform") or src.get("url", "")


def write_topics(items: list[dict], errors: list[str]) -> None:
    """按主题生成 inspiration/topics/*.md，并更新根 README 里的分类表。"""
    groups: dict[str, list[dict]] = {k: [] for k in TOPIC_NAMES}
    for it in items:
        if it.get("topic") and it["topic"] not in TOPIC_NAMES:
            errors.append(f"{it['id']}: topic {it['topic']!r} 不认识，只能是 {', '.join(TOPIC_NAMES)}")
        groups[topic_of(it)].append(it)
    TOPIC_DIR.mkdir(exist_ok=True)
    for old in TOPIC_DIR.glob("*.md"):
        old.unlink()
    index = ["# 灵感池：按主题看", "", "由 `tools/inspiration.py board` 生成，不要手改。分错了的条目，在它的 `item.json` 里加 `\"topic\": \"代号\"` 改过来。",
             "", "| 主题 | 代号 | 条数 | 能借到什么 |", "|---|---|---|---|"]
    rows = []
    for key, name, desc, gifs, _fn in sorted(TOPICS, key=lambda x: SHOW.index(x[0])):
        group = groups[key]
        if not group:
            continue
        index.append(f"| [{name}]({key}.md) | `{key}` | {len(group)} | {desc} |")
        page = [f"# {name}（{len(group)} 条）", "", f"能借到什么：{desc}。", "",
                "用法只有一种：借手法，换成原创角色重做。[规则](../README.md) · [全部主题](README.md)", "",
                "| 编号 | 标题 | 出处 | 借什么 |", "|---|---|---|---|"]
        for it in group:
            page.append(f"| [{it['id']}](../{it['_dir'].name}/) | {it.get('title', '')} | {source_link(it)} | {'、'.join(it.get('borrow') or []) or '—'} |")
        (TOPIC_DIR / f"{key}.md").write_text("\n".join(page) + "\n", encoding="utf-8")
        for g in gifs or []:
            if not (ROOT / g).exists():
                errors.append(f"主题 {key} 的配图不存在：{g}")
        imgs = "—" if gifs is None else (" ".join(f'<img src="{g}" width="72">' for g in gifs) or "还没做")
        rows.append(f"| [{name}](inspiration/topics/{key}.md) | {len(group)} | {desc} | {imgs} |")
    (TOPIC_DIR / "README.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    block = "\n".join([R_START, f"收了 **{len(items)}** 条，每条都有出处链接和我们自己写的分析（它怎么做的、我们能借什么）。别人的图不入库，下面的配图都是我们自己做的。", "",
                       "| 主题 | 条数 | 能借到什么 | 我们做出来的 |", "|---|---|---|---|", *rows, R_END])
    text = ROOT_README.read_text(encoding="utf-8")
    if R_START in text and R_END in text:
        head, rest = text.split(R_START, 1)
        ROOT_README.write_text(head + block + rest.split(R_END, 1)[1], encoding="utf-8")
    else:
        errors.append(f"README.md 里没有 {R_START} … {R_END} 标记，灵感池分类表没有更新")


def board(quiet: bool = False) -> int:
    items, errors = load_all()
    write_topics(items, errors)
    text = README.read_text(encoding="utf-8")
    if START in text and END in text:
        head, rest = text.split(START, 1)
        tail = rest.split(END, 1)[1]
        README.write_text(head + render(items) + tail, encoding="utf-8")
    for e in errors:
        print(f"ERROR {e}", file=sys.stderr)
    if not quiet or errors:
        c = Counter(it["status"] for it in items)
        print(f"{len(items)} 条灵感：" + "，".join(f"{STATUS[s]} {c.get(s, 0)}" for s in STATUS))
    return 1 if errors else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    a = sub.add_parser("add", help="收一条进灵感池（状态：待审）")
    a.add_argument("--title", required=True)
    a.add_argument("--url", default="", help="出处链接；本地素材写路径说明")
    a.add_argument("--type", default="unknown", choices=list(TYPES))
    a.add_argument("--platform", default="", help="小红书、抖音、GitHub、微信表情商店……")
    a.add_argument("--author", default="")
    a.add_argument("--what", default="", help="一句话：它是什么")
    a.add_argument("--why", default="", help="一句话：为什么值得收")
    a.add_argument("--borrow", action="append", default=[], help="想借的点，可多次给：类型、动效、构图、提示词结构……")
    a.add_argument("--tag", action="append", default=[])
    a.add_argument("--by", default="", help="谁收的")
    a.add_argument("--slug", help="目录名里编号后面那段，默认从链接生成")
    r = sub.add_parser("review", help="审批：approve 通过 / reject 驳回 / park 搁置 / reopen 退回待审")
    r.add_argument("id")
    r.add_argument("decision", choices=list(DECISIONS))
    r.add_argument("--by", required=True, help="审批人（仓库主人）")
    r.add_argument("--note", default="", help="结论说明：借什么、不借什么、为什么驳回")
    la = sub.add_parser("land", help="记下已落成的案例或试做（必须已通过）")
    la.add_argument("id")
    la.add_argument("ref", help="案例编号（如 cd-001）或试做目录")
    la.add_argument("--by", default="")
    sub.add_parser("board", help="校验并重新生成看板")
    args = ap.parse_args()
    return {"add": cmd_add, "review": cmd_review, "land": cmd_land}.get(args.cmd, lambda _: board())(args)


if __name__ == "__main__":
    raise SystemExit(main())
