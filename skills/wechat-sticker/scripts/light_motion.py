#!/usr/bin/env python3
"""给一张静态角色图加轻动效（点头、弹跳、摇摆），导出循环 GIF。

轻动效只是让整张图动起来，不改变角色的姿势。需要真实动作时走六帧序列图。
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image

import gifkit

MOTIONS = ("nod", "bounce", "sway")


def build_frames(im: Image.Image, motion: str, count: int, strength: float) -> list[Image.Image]:
    """在比原图大一圈的画布上做位移和旋转，留出动作空间，避免被画布边缘裁掉。"""
    im = im.convert("RGBA")
    box = im.split()[3].getbbox()
    if box:
        im = im.crop(box)
    w, h = im.size
    pad = round(max(w, h) * 0.18)
    canvas_size = (w + pad * 2, h + pad * 2)
    pivot = (pad + w / 2, pad + h)  # 脚底中点

    frames = []
    for i in range(count):
        t = 2 * math.pi * i / count
        dx = dy = 0.0
        angle = 0.0
        if motion == "nod":
            angle = 3.0 * strength * math.sin(t)
            dy = h * 0.025 * strength * (1 - math.cos(t)) / 2
        elif motion == "bounce":
            dy = -h * 0.08 * strength * abs(math.sin(t / 2))
        elif motion == "sway":
            angle = 6.0 * strength * math.sin(t)

        layer = Image.new("RGBA", canvas_size, (255, 255, 255, 0))
        layer.paste(im, (pad, pad))
        if angle:
            layer = layer.rotate(angle, resample=Image.Resampling.BICUBIC, center=pivot)
        frame = Image.new("RGBA", canvas_size, (255, 255, 255, 0))
        frame.paste(layer, (round(dx), round(dy)), layer)
        frames.append(frame)
    return frames


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, help="静态角色图（图集切出来的一格）")
    parser.add_argument("--motion", choices=MOTIONS, default="nod", help="动效类型（默认 nod）")
    parser.add_argument("--out", type=Path, required=True, help="输出 GIF 路径")
    parser.add_argument("--spec", default="wechat", help="平台规格名或 json 路径（默认 wechat）")
    parser.add_argument("--frames", type=int, default=8, help="帧数（默认 8）")
    parser.add_argument("--duration", type=int, default=100, help="每帧毫秒数（默认 100）")
    parser.add_argument("--strength", type=float, default=1.0, help="动作幅度倍数（默认 1.0）")
    parser.add_argument("--key-white", action="store_true", help="从边缘向内去掉白底")
    parser.add_argument("--tolerance", type=int, default=12, help="去白底的容差 0–255（默认 12）")
    args = parser.parse_args()

    im = Image.open(args.image).convert("RGBA")
    if args.key_white:
        im = gifkit.key_white(im, args.tolerance)

    frames = build_frames(im, args.motion, args.frames, args.strength)
    result = gifkit.export_gif(frames, args.out, gifkit.load_spec(args.spec),
                               duration=args.duration, transparent=True)
    result["motion"] = args.motion
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["within_limit"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
