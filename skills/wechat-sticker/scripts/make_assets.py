#!/usr/bin/env python3
"""做表情专辑的配套素材：封面、聊天面板图标、详情页横幅。尺寸和体积按平台规格。

    make_assets.py cover  character.png --key-white --out assets/cover.png
    make_assets.py icon   character.png --key-white --out assets/icon.png
    make_assets.py banner banner-raw.png --out assets/banner.png

封面用角色全身或半身；图标默认裁主体上部当头部，裁得不对就用 --crop 指定；
横幅按比例居中裁切，输出不透明 RGB。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageOps

import gifkit


def subject(path: Path, key: bool, tolerance: int) -> Image.Image:
    im = Image.open(path).convert("RGBA")
    return gifkit.key_white(im, tolerance) if key else im


def save_png(im: Image.Image, out: Path, rule: dict) -> int:
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, optimize=True)
    size = out.stat().st_size
    if size > rule["max_bytes"]:
        # 透明素材先减色再存，体积一般能降一半以上
        im.quantize(colors=128, method=Image.Quantize.FASTOCTREE).save(out, optimize=True)
        size = out.stat().st_size
    return size


def head_box(im: Image.Image, ratio: float) -> tuple[int, int, int, int]:
    """主体外框的上部 ratio 高度，保留全宽，免得把脸两侧裁掉。缩放时等比、居中。"""
    left, top, right, bottom = im.split()[3].getbbox() or (0, 0, *im.size)
    return (left, top, right, top + max(1, round((bottom - top) * ratio)))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("kind", choices=["cover", "icon", "banner"], help="要做哪一种")
    parser.add_argument("source", type=Path, help="源图")
    parser.add_argument("--out", type=Path, required=True, help="输出路径")
    parser.add_argument("--spec", default="wechat", help="平台规格名或 json 路径（默认 wechat）")
    parser.add_argument("--key-white", action="store_true", help="从边缘向内去掉白底（封面、图标用）")
    parser.add_argument("--tolerance", type=int, default=12, help="去白底的容差 0–255（默认 12）")
    parser.add_argument("--crop", help="图标的裁切框 x0,y0,x1,y1（源图像素）；不给就自动取头部")
    parser.add_argument("--head-ratio", type=float, default=0.5,
                        help="自动取头部时，取主体高度的多少（默认 0.5）")
    args = parser.parse_args()

    spec = gifkit.load_spec(args.spec)
    rule = spec["assets"][args.kind]
    size = (rule["width"], rule["height"])

    if args.kind == "banner":
        im = ImageOps.fit(Image.open(args.source).convert("RGB"), size, method=Image.Resampling.LANCZOS)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        if args.out.suffix.lower() in (".jpg", ".jpeg"):
            im.save(args.out, quality=90, optimize=True)
        else:
            im.save(args.out, optimize=True)
        corners = [im.getpixel(p) for p in ((0, 0), (size[0] - 1, 0), (0, size[1] - 1), (size[0] - 1, size[1] - 1))]
        if rule.get("no_pure_white") and all(min(c) >= 250 for c in corners):
            print("WARN 横幅四角都接近纯白，平台不接受纯白底，换一张有底色的源图", file=sys.stderr)
    else:
        im = subject(args.source, args.key_white, args.tolerance)
        if args.kind == "icon":
            if args.crop:
                box = tuple(int(v) for v in args.crop.split(","))
                if len(box) != 4:
                    parser.error("--crop 要写成 x0,y0,x1,y1")
            else:
                box = head_box(im, args.head_ratio)
            im = im.crop(box)
        # 小图标再内收会把细线吃掉，只有封面内收 1 像素
        erode = 1 if args.kind == "cover" else 0
        im = gifkit.hard_alpha(gifkit.fit_frames([im], size)[0], erode=erode)
        if im.split()[3].getextrema()[0] == 255:
            print("WARN 输出没有透明区域；源图是白底的话加 --key-white", file=sys.stderr)

    out_bytes = save_png(im, args.out, rule) if args.kind != "banner" else args.out.stat().st_size
    ok = out_bytes <= rule["max_bytes"]
    print(f"{'OK' if ok else 'FAIL'} {rule['label']} {size[0]}×{size[1]}，{out_bytes / 1000:.0f}KB"
          f"（上限 {rule['max_bytes'] / 1000:.0f}KB），在 {args.out}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
