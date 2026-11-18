#!/usr/bin/env python3
"""给铺满画面的照片风格静态图加轻动效，导出不透明的循环 GIF。

light_motion.py 是在透明画布上挪动角色，照片带背景、铺满画面，挪了会露边。
这里改成在原图里移动取景框（先裁掉一圈留出余量），动的是镜头不是角色：

  zoom     冲镜头：快速推近再弹回（震惊、吼、冲过来）
  shake    左右抖（尴尬、生气、发抖）
  bounce   上下颠（笑、得意、比耶）
  breathe  慢慢轻推（委屈、无语、发呆）

单张：
  photo_motion.py new.png --motion zoom --out result.gif
整个工作目录（每个子目录里的 new.png → <套目录>/<子目录名>/result.gif）：
  photo_motion.py <工作目录> --out <套目录> --motion bounce --set 03=zoom --set 08=shake
整套模式没有 case.json 时写一份最小的（route=photo、motion），已有的只更新 motion。
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import date
from pathlib import Path

from PIL import Image

import gifkit

MOTIONS = ("zoom", "shake", "bounce", "breathe")


def build_frames(im: Image.Image, motion: str, size: tuple[int, int], count: int = 8,
                 strength: float = 1.0) -> list[Image.Image]:
    im = im.convert("RGB")
    side = min(im.size)
    cx, cy = im.width / 2, im.height / 2
    frames = []
    for i in range(count):
        t = 2 * math.pi * i / count
        scale, dx, dy = 0.92, 0.0, 0.0  # 先裁掉 8%，留出移动余量
        if motion == "zoom":
            scale = 0.92 - 0.10 * strength * max(0.0, math.sin(t))
        elif motion == "shake":
            dx = 0.025 * strength * math.sin(2 * t)
        elif motion == "bounce":
            dy = -0.03 * strength * abs(math.sin(t))
        elif motion == "breathe":
            scale = 0.92 - 0.035 * strength * (1 - math.cos(t)) / 2
        w = side * scale
        x = min(max(cx - w / 2 + dx * side, 0), im.width - w)
        y = min(max(cy - w / 2 + dy * side, 0), im.height - w)
        frames.append(im.crop((round(x), round(y), round(x + w), round(y + w)))
                      .resize(size, Image.Resampling.LANCZOS))
    return frames


def default_duration(motion: str) -> int:
    return 160 if motion == "breathe" else 90


def export(src: Path, out: Path, motion: str, spec: dict, args) -> dict:
    rule = spec["sticker"]
    with Image.open(src) as im:
        frames = build_frames(im, motion, (rule["width"], rule["height"]), args.frames, args.strength)
    duration = args.duration or default_duration(motion)
    return gifkit.encode_within_limit(frames, out, spec, duration, transparent=False)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", type=Path, help="一张图，或一个工作目录（子目录里放 new.png）")
    parser.add_argument("--out", type=Path, required=True, help="单张时是输出 GIF，整套时是套目录")
    parser.add_argument("--motion", choices=MOTIONS, default="bounce", help="动效（默认 bounce）")
    parser.add_argument("--set", action="append", default=[], metavar="名字=动效",
                        help="整套模式下给某张单独指定动效，可多次给")
    parser.add_argument("--image-name", default="new.png", help="整套模式下每个子目录里的图名（默认 new.png）")
    parser.add_argument("--frames", type=int, default=8, help="帧数（默认 8）")
    parser.add_argument("--duration", type=int, help="每帧毫秒数（默认 breathe 160，其余 90）")
    parser.add_argument("--strength", type=float, default=1.0, help="幅度倍数（默认 1.0）")
    parser.add_argument("--spec", default="wechat", help="平台规格名或 json 路径（默认 wechat）")
    args = parser.parse_args()
    spec = gifkit.load_spec(args.spec)

    if args.source.is_file():
        r = export(args.source, args.out, args.motion, spec, args)
        print(f"OK   {args.out}: {args.motion}，{r['frames']} 帧，{r['bytes'] // 1024}KB")
        return 0 if r["within_limit"] else 1

    overrides = {}
    for item in args.set:
        name, _, motion = item.partition("=")
        if motion not in MOTIONS:
            parser.error(f"--set {item}：动效只能是 {', '.join(MOTIONS)}")
        overrides[name] = motion
    sources = sorted(p for p in args.source.iterdir() if (p / args.image_name).exists())
    if not sources:
        parser.error(f"{args.source} 的子目录里没有 {args.image_name}")
    bad = 0
    for d in sources:
        motion = overrides.get(d.name, args.motion)
        case_dir = args.out / d.name
        r = export(d / args.image_name, case_dir / "result.gif", motion, spec, args)
        (case_dir / "base.gif").unlink(missing_ok=True)  # 换了底图，旧的无字底图作废，caption.py 会重新存
        case_path = case_dir / "case.json"
        case = json.loads(case_path.read_text(encoding="utf-8")) if case_path.exists() else {
            "id": "", "title": "", "meaning": "", "tags": [], "route": "photo",
            "source_image": str((d / args.image_name).resolve()),
            "checks": {"technical": False, "visual": False, "approved": False, "notes": ""},
            "status": "draft", "created": date.today().isoformat()}
        case["motion"] = motion
        case_path.write_text(json.dumps(case, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        ok = r["within_limit"]
        bad += not ok
        print(f"{'OK  ' if ok else 'FAIL'} {d.name}: {motion}，{r['frames']} 帧，{r['bytes'] // 1024}KB")
    print("\n原图有字的，再用 caption.py <套目录> 加字（字压在照片上，“压在角色身上”的 WARN 是预期的）。")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
