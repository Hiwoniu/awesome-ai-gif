#!/usr/bin/env python3
"""用 Codex CLI 内置的 image_gen 出图（不需要 OPENAI_API_KEY，走 Codex 登录的额度）。

单张：
  codex_gen.py one --prompt character-prompt.md --image photo.jpg --out character.png --transparent
复刻整套（读 remix_extract.py 的 plan.json，给每个还没有 new.png 的目录出图）：
  codex_gen.py remix <工作目录> [--character character.png] [--jobs 3]
逐张出图（工作目录下每个子目录放 prompt.md，要照着做的原图放成 ref.png，可以没有）：
  codex_gen.py each <工作目录> --image photo.jpg [--jobs 3]
  参考图顺序：--image 给的图在前，子目录里的 ref.png 最后。

做法：把提示词文件交给 `codex exec`，让它用内置 image_gen 按原文出一张图，
再把 $CODEX_HOME/generated_images/ 下的原图复制到指定位置。每次调用的日志写在输出图旁边的
codex-<名字>.log，调用记录追加到同目录的 codex.json（提示词、参考图、原始输出路径、耗时）。

已有输出时：remix 模式跳过，加 --force 重画；重画和 one 模式都会把旧图改名成 <名字>-v1.png、-v2.png…
保留下来，不会覆盖。
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

INSTRUCTION = """用内置 image_gen 工具生成一张图（transparent_background={transparent}）。{images}
提示词逐字使用文件 {prompt} 的全部内容（先读它），不要改写、不要增删。
生成后把输出的 PNG 从 $CODEX_HOME/generated_images/ 复制到 {out}。
只生成 1 张，不要做别的事。最后一行只输出原始输出路径。"""

RAW_PATH = re.compile(r"(/\S*generated_images/\S+?\.png)")


def keep_old(out: Path) -> Path | None:
    """已有的输出改名成 -v1、-v2… 保留。返回改成的路径。"""
    if not out.exists():
        return None
    n = 1
    while (old := out.with_name(f"{out.stem}-v{n}{out.suffix}")).exists():
        n += 1
    out.rename(old)
    return old


def generate(prompt: Path, images: list[Path], out: Path, transparent: bool, image_note: str = "",
             model: str | None = None) -> dict:
    prompt, out = prompt.resolve(), out.resolve()
    images = [p.resolve() for p in images]
    for p in [prompt, *images]:
        if not p.exists():
            raise FileNotFoundError(p)
    out.parent.mkdir(parents=True, exist_ok=True)
    kept = keep_old(out)

    note = image_note or (f"附带 {len(images)} 张参考图，按提示词里的说法使用。" if images else "没有参考图。")
    text = INSTRUCTION.format(transparent=str(transparent).lower(), images=note, prompt=prompt, out=out)
    cmd = ["codex", "exec", "--skip-git-repo-check", "-s", "workspace-write", "-C", str(out.parent)]
    if model:
        cmd += ["-m", model]
    for p in images:
        cmd += ["-i", str(p)]
    cmd.append("-")  # 提示词走 stdin：-i 可以带多个文件，会把后面的位置参数也当成图片

    log = out.with_name(f"codex-{out.stem}.log")
    start = time.time()
    proc = subprocess.run(cmd, input=text, capture_output=True, text=True)
    log.write_text(proc.stdout + proc.stderr, encoding="utf-8")
    raws = RAW_PATH.findall(proc.stdout)
    record = {
        "time": datetime.now().isoformat(timespec="seconds"), "prompt": str(prompt),
        "images": [str(p) for p in images], "out": str(out), "transparent": transparent,
        "raw": raws[-1] if raws else None, "seconds": round(time.time() - start),
        "exit": proc.returncode, "ok": out.exists() and out.stat().st_mtime >= start - 1,
        "replaced": str(kept) if kept else None, "log": str(log),
    }
    # Codex 没复制成功但给了原始路径时，自己补一次复制
    if not record["ok"] and record["raw"] and Path(record["raw"]).exists():
        shutil.copy2(record["raw"], out)
        record["ok"] = True
    if not record["ok"] and kept:
        kept.rename(out)  # 失败了把旧图放回去
        record["replaced"] = None

    history = out.with_name("codex.json")
    entries = json.loads(history.read_text(encoding="utf-8")) if history.exists() else []
    entries.append(record)
    history.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record


def report(name: str, r: dict) -> bool:
    if r["ok"]:
        extra = f"，旧图留在 {Path(r['replaced']).name}" if r["replaced"] else ""
        print(f"OK   {name}: {r['out']}（{r['seconds']}s{extra}）")
    else:
        print(f"FAIL {name}: 没拿到图，退出码 {r['exit']}，看日志 {r['log']}")
    return r["ok"]


def cmd_one(args) -> int:
    r = generate(args.prompt, args.image or [], args.out, args.transparent, model=args.model)
    return 0 if report(args.out.name, r) else 1


def cmd_remix(args) -> int:
    work = args.work.resolve()
    plan = json.loads((work / "plan.json").read_text(encoding="utf-8"))
    character = args.character or (Path(plan["character_image"]) if plan.get("character_image") else None)
    if character is None:
        print("缺新角色定稿图：用 --character 指定，或 remix_extract.py 时加 --character-image", file=sys.stderr)
        return 2
    transparent = plan.get("transparent", False) if args.transparent is None else args.transparent

    dirs = [s["dir"] for s in plan["pose_sheets"]] + [i["name"] for i in plan["items"] if i["route"] == "frames"]
    if args.only:
        dirs = [d for d in dirs if d in args.only]
    jobs = []
    for d in dirs:
        new = work / d / "new.png"
        if new.exists() and not args.force:
            print(f"SKIP {d}: 已有 new.png（重画加 --force）")
            continue
        prompt = work / d / args.prompt_name
        if not prompt.exists():
            prompt = work / d / "prompt.md"
        jobs.append((d, prompt, new))
    if not jobs:
        return 0

    note = "附带两张参考图：第 1 张是新角色定稿图，第 2 张是动作参考图。"
    print(f"出图 {len(jobs)} 张，同时跑 {args.jobs} 个，{'透明底' if transparent else '白底'}……")
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {d: pool.submit(generate, prompt, [character, work / d / "ref.png"], new, transparent, note,
                                  args.model) for d, prompt, new in jobs}
    ok = sum(report(d, f.result()) for d, f in futures.items())
    print(f"\n成功 {ok}/{len(jobs)}。逐张打开 new.png 和 ref.png 对照验货，坏的改提示词后用 --only <名字> --force 重画。")
    return 0 if ok == len(jobs) else 1


def cmd_each(args) -> int:
    work = args.work.resolve()
    extra = [p.resolve() for p in args.image or []]
    dirs = sorted(d for d in work.iterdir() if d.is_dir() and (d / args.prompt_name).exists())
    if args.only:
        dirs = [d for d in dirs if d.name in args.only]
    jobs = []
    for d in dirs:
        new = d / "new.png"
        if new.exists() and not args.force:
            print(f"SKIP {d.name}: 已有 new.png（重画加 --force）")
            continue
        has_ref = (d / "ref.png").exists()
        images = extra + ([d / "ref.png"] if has_ref else [])
        # 说明要按这一张实际带了哪些图来写，没有 ref.png 却说有，Codex 会停下来找图
        if has_ref and extra:
            note = f"附带 {len(images)} 张参考图：前 {len(extra)} 张是主角，最后 1 张是要照着做的原图，按提示词里的说法使用。"
        elif has_ref:
            note = "附带 1 张参考图（要照着做的原图），按提示词里的说法使用。"
        elif extra:
            note = f"附带 {len(extra)} 张参考图（主角），按提示词里的说法使用。没有别的参考图，不要去找。"
        else:
            note = "没有参考图。"
        jobs.append((d.name, d / args.prompt_name, images, new, note))
    if not jobs:
        print("没有要出的图：子目录里要有提示词文件（默认 prompt.md）。" if not dirs else "全部已有 new.png。")
        return 0 if dirs else 2
    print(f"出图 {len(jobs)} 张，同时跑 {args.jobs} 个，{'透明底' if args.transparent else '不要求透明'}……")
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {name: pool.submit(generate, prompt, images, new, args.transparent, note, args.model)
                   for name, prompt, images, new, note in jobs}
    ok = sum(report(name, f.result()) for name, f in futures.items())
    print(f"\n成功 {ok}/{len(jobs)}。拼一张 ref/new 对照图逐张验货，坏的改提示词后用 --only <名字> --force 重画。")
    return 0 if ok == len(jobs) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    one = sub.add_parser("one", help="按一个提示词文件出一张图")
    one.add_argument("--prompt", type=Path, required=True, help="提示词文件")
    one.add_argument("--image", type=Path, action="append", help="参考图，可多次给，按顺序就是参考图 1、2…")
    one.add_argument("--out", type=Path, required=True, help="输出 PNG")
    one.add_argument("--transparent", action="store_true", help="要求透明背景")
    one.add_argument("--model", help="指定 Codex 模型（默认用 Codex 配置）")
    one.set_defaults(func=cmd_one)

    rm = sub.add_parser("remix", help="给 remix_extract.py 的工作目录批量出图")
    rm.add_argument("work", type=Path, help="remix_extract.py 的工作目录")
    rm.add_argument("--character", type=Path, help="新角色定稿图（默认读 plan.json 的 character_image）")
    rm.add_argument("--only", nargs="*", help="只画这些目录")
    rm.add_argument("--force", action="store_true", help="已有 new.png 也重画（旧图改名保留）")
    rm.add_argument("--jobs", type=int, default=3, help="同时跑几个（默认 3）")
    rm.add_argument("--prompt-name", default="prompt.md",
                    help="每个目录里用哪个提示词文件（默认 prompt.md，找不到时也用它）")
    rm.add_argument("--transparent", action=argparse.BooleanOptionalAction, default=None,
                    help="覆盖 plan.json 里的透明底设置")
    rm.add_argument("--model", help="指定 Codex 模型（默认用 Codex 配置）")
    rm.set_defaults(func=cmd_remix)

    each = sub.add_parser("each", help="工作目录下每个子目录（prompt.md + ref.png）各出一张")
    each.add_argument("work", type=Path, help="工作目录")
    each.add_argument("--image", type=Path, action="append", help="每张都带的参考图（如主角照片），排在 ref.png 前面")
    each.add_argument("--only", nargs="*", help="只画这些子目录")
    each.add_argument("--force", action="store_true", help="已有 new.png 也重画（旧图改名保留）")
    each.add_argument("--jobs", type=int, default=3, help="同时跑几个（默认 3）")
    each.add_argument("--prompt-name", default="prompt.md", help="每个子目录里的提示词文件（默认 prompt.md）")
    each.add_argument("--transparent", action="store_true", help="要求透明背景")
    each.add_argument("--model", help="指定 Codex 模型（默认用 Codex 配置）")
    each.set_defaults(func=cmd_each)

    args = parser.parse_args()
    if shutil.which("codex") is None:
        print("找不到 codex 命令。装好 Codex CLI 并登录，或者把提示词交给用户在 ChatGPT 里出图。", file=sys.stderr)
        return 2
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
