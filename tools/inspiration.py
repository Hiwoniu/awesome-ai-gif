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
TYPES = {"wechat-stickers": "微信表情包", "cards": "光栅变画卡", "posters": "动态海报",
         "signatures": "动态签名", "storybooks": "动态绘本", "multi": "多类型", "unknown": "未定"}


def item_dirs() -> list[Path]:
    return sorted(d for d in POOL.iterdir() if d.is_dir() and not d.name.startswith(("_", ".")))


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
            src = it.get("source", {})
            link = f"[{src.get('platform') or '链接'}]({src['url']})" if src.get("url", "").startswith("http") else (src.get("platform") or src.get("url", ""))
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


def board(quiet: bool = False) -> int:
    items, errors = load_all()
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
