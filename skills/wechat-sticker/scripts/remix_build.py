#!/usr/bin/env python3
"""复刻第二步：把换了角色的新图合成回 GIF，节奏和动效沿用原 GIF。

先运行 remix_extract.py，按各目录的 prompt.md 出图，把新图存为：
  <工作目录>/poses/new.png     still 类的新姿势图集（和 poses/ref.png 同样网格）
  <工作目录>/<名字>/new.png    frames 类的新关键帧图（和 <名字>/ref.png 同样网格）
然后：
  remix_build.py <工作目录> --out <新套目录> --key-white

每张输出到 <新套目录>/<名字>/result.gif，并写一份 case.json（含义词留空，route 和来源已填）。
还没出新图的条目会跳过并提示。
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from PIL import Image

import gifkit
from light_motion import build_frames


def cells(sheet_path: Path, cols: int, rows: int, inset: int, key: bool, tolerance: int) -> list[Image.Image]:
    sheet = Image.open(sheet_path).convert("RGBA")
    out = []
    for box in gifkit.grid_boxes(sheet.size, cols, rows, inset):
        im = sheet.crop(box)
        out.append(gifkit.key_white(im, tolerance) if key else im)
    return out


def write_case(case_dir: Path, item: dict, route: str, overwrite: bool) -> None:
    path = case_dir / "case.json"
    if path.exists() and not overwrite:
        return
    case = {
        "id": "", "title": "", "meaning": "", "tags": [],
        "route": route,
        "remix_of": item["source"],
        "engine": {"provider": None, "model": None, "quality": None, "channel": None},
        "cost": {"generations": 0, "usd": None, "shared": "poses" if route == "atlas" else None},
        "checks": {"technical": False, "visual": False, "approved": False, "notes": ""},
        "status": "draft",
        "created": date.today().isoformat(),
    }
    path.write_text(json.dumps(case, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("work", type=Path, help="remix_extract.py 的工作目录")
    parser.add_argument("--out", type=Path, required=True, help="新套目录")
    parser.add_argument("--spec", default="wechat", help="平台规格名或 json 路径（默认 wechat）")
    parser.add_argument("--key-white", action="store_true", help="从边缘向内去掉白底")
    parser.add_argument("--tolerance", type=int, default=12, help="去白底的容差 0–255（默认 12）")
    parser.add_argument("--inset", type=int, default=0, help="切格时每格向内收的像素（新图有格线时用）")
    parser.add_argument("--strength", type=float, help="覆盖 still 类的动作幅度（默认沿用原 GIF 的拟合值）")
    parser.add_argument("--only", nargs="*", help="只合成这些名字")
    parser.add_argument("--overwrite-case", action="store_true", help="已有 case.json 也重写")
    args = parser.parse_args()

    plan = json.loads((args.work / "plan.json").read_text(encoding="utf-8"))
    spec = gifkit.load_spec(args.spec)
    items = [i for i in plan["items"] if not args.only or i["name"] in args.only]
    if plan.get("transparent") and args.key_white:
        print("WARN plan.json 是透明底出图，不需要 --key-white；加了会把贴边的白色部位抠掉")

    sheets: dict[str, list[Image.Image] | None] = {}
    for s in plan["pose_sheets"]:
        new = args.work / s["dir"] / "new.png"
        sheets[s["dir"]] = cells(new, *s["grid"], args.inset, args.key_white, args.tolerance) \
            if new.exists() else None

    made = skipped = failed = 0
    for item in items:
        case_dir = args.out / item["name"]
        if item["route"] == "still":
            group = sheets.get(item["sheet"])
            if group is None:
                print(f"SKIP {item['name']}: 还没有 {item['sheet']}/new.png")
                skipped += 1
                continue
            pose = group[item["cell"]]
            if pose.split()[3].getbbox() is None:
                print(f"FAIL {item['name']}: {item['sheet']}/new.png 第 {item['cell'] + 1} 格是空的")
                failed += 1
                continue
            m = item["motion"]
            count = item["frames"] if m["motion"] else 2
            # duration 是原 GIF 逐帧时长列表（旧版 plan.json 是一个平均值）
            durations = item["duration"] if isinstance(item["duration"], list) else [item["duration"]] * item["frames"]
            if m["motion"]:
                frames = build_frames(pose, m["motion"], count, args.strength or m["strength"])
                frames = frames[m["phase"]:] + frames[:m["phase"]]
            else:
                frames = [pose, pose]
                total = sum(durations)
                durations = [total // 2, total - total // 2]
            result = gifkit.export_gif(frames, case_dir / "result.gif", spec,
                                       duration=durations, transparent=True)
            note = f"{m['motion']} ×{args.strength or m['strength']}" if m["motion"] else "静止"
            route = "atlas"
        else:
            new = args.work / item["name"] / "new.png"
            if not new.exists():
                print(f"SKIP {item['name']}: 还没有 {item['name']}/new.png")
                skipped += 1
                continue
            frames = cells(new, *item["grid"], args.inset, args.key_white, args.tolerance)
            keys = item["keyframes"]
            frames = frames[:len(keys)]
            result = gifkit.export_gif(frames, case_dir / "result.gif", spec,
                                       duration=[k["duration"] for k in keys], transparent=True)
            note = f"{len(keys)} 个关键帧"
            route = "frames"

        write_case(case_dir, item, route, args.overwrite_case)
        status = "OK  " if result["within_limit"] else "FAIL"
        if not result["within_limit"]:
            failed += 1
        else:
            made += 1
        print(f"{status} {item['name']}: {note}，{result['frames']} 帧，{result['bytes'] / 1000:.0f}KB")

    print(f"\n合成 {made} 张，跳过 {skipped} 张，失败 {failed} 张，在 {args.out}")
    print("接下来：逐张打开看动作对不对、黑底查白边，填 case.json 的 meaning，再跑 check_assets.py。")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
