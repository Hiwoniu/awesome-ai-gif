#!/usr/bin/env python3
"""把一张网格图切成等大的小图。六帧序列图用 3×2，姿势图集用 4×4。"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

import gifkit


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sheet", type=Path, help="网格图")
    parser.add_argument("--cols", type=int, default=3, help="列数（默认 3）")
    parser.add_argument("--rows", type=int, default=2, help="行数（默认 2）")
    parser.add_argument("--out", type=Path, required=True, help="输出目录")
    parser.add_argument("--inset", type=int, default=0, help="每格四边各向内收多少像素，用来去掉格线")
    parser.add_argument("--prefix", default=None, help="文件名前缀（默认 3×2 用 frame，其他用 cell）")
    args = parser.parse_args()

    sheet = Image.open(args.sheet).convert("RGBA")
    width, height = sheet.size
    # 边界按比例取整，除不尽的像素分摊到各格（相邻格最多差 1 像素），不丢边
    boxes = gifkit.grid_boxes((width, height), args.cols, args.rows, args.inset)
    if min(min(b[2] - b[0], b[3] - b[1]) for b in boxes) <= 0:
        parser.error("--inset 太大，格子会被收没")

    prefix = args.prefix or ("frame" if (args.cols, args.rows) == (3, 2) else "cell")
    args.out.mkdir(parents=True, exist_ok=True)
    index = 0
    sizes = set()
    for box in boxes:
        index += 1
        sizes.add((box[2] - box[0], box[3] - box[1]))
        sheet.crop(box).save(args.out / f"{prefix}_{index:02d}.png")

    size_text = "、".join(f"{w}×{h}" for w, h in sorted(sizes))
    note = "（原图不能整除，各格差 1 像素，合成时会统一缩放）" if len(sizes) > 1 else ""
    print(f"OK 切出 {index} 张，每张 {size_text}{note}，在 {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
