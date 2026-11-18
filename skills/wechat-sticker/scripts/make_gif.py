#!/usr/bin/env python3
"""把一组帧合成符合平台规格的循环 GIF：先缩尺寸，再压体积。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image

import gifkit


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("frames", type=Path, help="帧所在目录，按文件名顺序播放")
    parser.add_argument("--out", type=Path, required=True, help="输出 GIF 路径")
    parser.add_argument("--spec", default="wechat", help="平台规格名或 json 路径（默认 wechat）")
    parser.add_argument("--duration", type=int, default=120, help="每帧毫秒数（默认 120）")
    parser.add_argument("--key-white", action="store_true", help="从边缘向内去掉白底")
    parser.add_argument("--tolerance", type=int, default=12, help="去白底的容差 0–255（默认 12）")
    parser.add_argument("--opaque", action="store_true", help="不要透明，垫白底输出")
    args = parser.parse_args()

    paths = gifkit.list_images(args.frames)
    if len(paths) < 2:
        parser.error(f"{args.frames} 里至少要有 2 张图")

    frames = [Image.open(p).convert("RGBA") for p in paths]
    if args.key_white:
        frames = [gifkit.key_white(f, args.tolerance) for f in frames]

    result = gifkit.export_gif(frames, args.out, gifkit.load_spec(args.spec),
                               duration=args.duration, transparent=not args.opaque)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["within_limit"]:
        print("FAIL 压到最低仍超过体积上限，需要减少帧数或简化画面")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
