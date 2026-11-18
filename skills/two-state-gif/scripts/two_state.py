#!/usr/bin/env python3
"""两态切换 GIF：A 停留 → 竖条从左到右错开翻到 B → B 停留 → 翻回 A，无限循环。
光栅变画卡（--spec card，480×720）和动态海报（--spec poster，720×960）共用。
思路参考 gif-factory 的光栅卡说明（MIT），代码自写。

  two_state.py --spec card --split diptych.png out.gif
  two_state.py --spec poster a.png b.png out.gif
  two_state.py --spec card --split diptych.png out.gif --crop-y 0.19:0.69 --title 橘团 --subtitle "夜读 / 变身"

--split    输入是一张左右双联图，从正中切成 A、B
--crop-y   切开后每格只取这段高度（占整格高度的比例），用来去掉模型多留的空白条、
           或者在比例不符时手动选一个窗口。比例差太多又没给 --crop-y 会直接报错，不悄悄裁掉一大块。
规格（尺寸、时长、帧率、条数、颜色数）来自 specs/<名字>.json，命令行给的值优先。
标题画在底部固定位置，每帧完全相同，不随切换闪动；字直接画在图里的海报不用加。
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SPEC_DIR = HERE.parent / "specs"
# 字体只在加标题时才用：先找本 Skill 的 fonts/，再找同仓库微信 Skill 自带的得意黑
FONT_CANDIDATES = [HERE.parent / "fonts/SmileySans-Oblique.ttf",
                   HERE.parent.parent / "wechat-sticker/fonts/SmileySans-Oblique.ttf"]


def load_spec(name_or_path: str) -> dict:
    path = Path(name_or_path)
    if path.suffix != ".json":
        path = SPEC_DIR / f"{name_or_path}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def find_font(path: str | None) -> Path:
    for p in ([Path(path)] if path else FONT_CANDIDATES):
        if p.exists():
            return p
    raise SystemExit("加标题要中文字体：用 --font 指定一个 .ttf，或把得意黑放到本 Skill 的 fonts/ 下")


def cover(im: Image.Image, size: tuple[int, int]) -> Image.Image:
    """等比缩放后居中裁到 size。宽高比差超过 8% 就报错。"""
    w, h = size
    if abs(im.width / im.height - w / h) > 0.08:
        raise SystemExit(f"宽高比不符：图 {im.width}×{im.height}，目标 {w}×{h}。"
                         f"用 --crop-y 选一段高度（比如 0.2:0.7），或重新出图")
    ratio = max(w / im.width, h / im.height)
    im = im.convert("RGB").resize((round(im.width * ratio), round(im.height * ratio)), Image.Resampling.LANCZOS)
    left, top = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((left, top, left + w, top + h))


def slat_frame(a: Image.Image, b: Image.Image, p: float, slats: int) -> Image.Image:
    """p=0 全是 A，p=1 全是 B。条从左到右依次翻，单双条错开，正在翻的条带一道亮边。"""
    w, h = a.size
    out = a.copy()
    sw = w / slats
    draw = ImageDraw.Draw(out)
    for i in range(slats):
        start = i / slats * 0.55 + (i % 2) * 0.25   # 0 … 0.8
        local = min(max((p - start) / 0.2, 0), 1)
        x0, x1 = round(i * sw), round((i + 1) * sw)
        if local >= 1:
            out.paste(b.crop((x0, 0, x1, h)), (x0, 0))
        elif local > 0:
            cut = x0 + round((x1 - x0) * local)      # 这一条正在翻：左边已是 B
            out.paste(b.crop((x0, 0, cut, h)), (x0, 0))
            draw.line([(cut, 0), (cut, h)], fill=(255, 255, 255), width=1)
    return out


def add_title(im: Image.Image, title: str, subtitle: str, footer: int, font: Path | None) -> Image.Image:
    if not title and not subtitle:
        return im
    im = im.copy()
    w, h = im.size
    draw = ImageDraw.Draw(im)
    if footer:
        draw.rectangle([0, h - footer, w, h], fill=(18, 18, 22))
    area_top = h - (footer or round(h * 0.11))
    area_h = h - area_top
    stroke = 0 if footer else max(2, round(area_h * 0.04))   # 没有深色栏时字压在画面上，加黑描边
    if title:
        f = ImageFont.truetype(str(font), round(area_h * (0.5 if subtitle else 0.62)))
        draw.text((w / 2, area_top + area_h * (0.4 if subtitle else 0.5)), title, font=f, anchor="mm",
                  fill=(255, 255, 255), stroke_width=stroke, stroke_fill=(0, 0, 0))
    if subtitle:
        f = ImageFont.truetype(str(font), round(area_h * 0.22))
        draw.text((w / 2, area_top + area_h * 0.8), subtitle, font=f, anchor="mm", fill=(220, 220, 228),
                  stroke_width=stroke // 2, stroke_fill=(0, 0, 0))
    return im


def build(a, b, cfg, title="", subtitle="", footer=0, font=None):
    size = (cfg["width"], cfg["height"])
    a, b = cover(a, size), cover(b, size)
    n = round(cfg["seconds"] * cfg["fps"])
    hold = round(n * cfg["hold"] / 2)          # 每个端点停留的帧数
    move = n // 2 - hold                       # 每次切换的帧数
    seq = [0.0] * hold + [i / move for i in range(1, move + 1)] + [1.0] * hold + \
          [1 - i / move for i in range(1, move + 1)]
    seq = seq[:n] + [0.0] * (n - len(seq))
    frames, durations = [], []
    step = round(1000 / cfg["fps"])
    for p in seq:
        f = add_title(slat_frame(a, b, p, cfg["slats"]), title, subtitle, footer, font)
        if frames and f.tobytes() == frames[-1].tobytes():
            durations[-1] += step               # 相同的停留帧合并，累计时长不变
        else:
            frames.append(f)
            durations.append(step)
    return frames, durations


def encode(frames, out: Path, durations, colors: int) -> int:
    """不透明 GIF：整段共用一张调色板，disposal=1 让 Pillow 每帧只写变化的矩形区域。
    逐帧整张写 6 秒的卡约 5MB，这样写不到 1MB。"""
    w, h = frames[0].size
    strip = Image.new("RGB", (w, h * len(frames)))
    for i, f in enumerate(frames):
        strip.paste(f, (0, i * h))
    pal = strip.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pages = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    out.parent.mkdir(parents=True, exist_ok=True)
    pages[0].save(out, save_all=True, append_images=pages[1:], duration=durations, loop=0, disposal=1)
    return out.stat().st_size


def crop_y(im: Image.Image, spec: str) -> Image.Image:
    top, _, bottom = spec.partition(":")
    return im.crop((0, round(im.height * float(top)), im.width, round(im.height * float(bottom))))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", type=Path, help="a.png b.png out.gif，或 --split 时 diptych.png out.gif")
    ap.add_argument("--spec", default="card", help="规格名（card / poster）或 json 路径，默认 card")
    ap.add_argument("--split", action="store_true", help="输入是左右双联图，从正中切开")
    ap.add_argument("--crop-y", metavar="上:下", help="每格只取这段高度，比例，如 0.19:0.69")
    for k, t in [("width", int), ("height", int), ("seconds", float), ("fps", int), ("hold", float),
                 ("slats", int), ("colors", int)]:
        ap.add_argument(f"--{k}", type=t, help="覆盖规格里的值")
    ap.add_argument("--title", default="")
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--footer", type=int, default=0, help="底部另画一条深色标题栏的高度（像素）")
    ap.add_argument("--font", help="标题字体 .ttf（默认找得意黑）")
    args = ap.parse_args()

    cfg = load_spec(args.spec)
    for k in ("width", "height", "seconds", "fps", "hold", "slats", "colors"):
        if getattr(args, k) is not None:
            cfg[k] = getattr(args, k)

    if args.split:
        if len(args.inputs) != 2:
            ap.error("--split 要两个参数：双联图 输出.gif")
        src, out = args.inputs
        im = Image.open(src).convert("RGB")
        a, b = im.crop((0, 0, im.width // 2, im.height)), im.crop((im.width - im.width // 2, 0, im.width, im.height))
    else:
        if len(args.inputs) != 3:
            ap.error("要三个参数：a.png b.png 输出.gif")
        pa, pb, out = args.inputs
        a, b = Image.open(pa).convert("RGB"), Image.open(pb).convert("RGB")
    if args.crop_y:
        a, b = crop_y(a, args.crop_y), crop_y(b, args.crop_y)

    font = find_font(args.font) if (args.title or args.subtitle) else None
    frames, durations = build(a, b, cfg, args.title, args.subtitle, args.footer, font)
    size = encode(frames, out, durations, cfg["colors"])
    over = size > cfg.get("soft_max_bytes", 10 ** 9)
    print(f"{'WARN' if over else 'OK  '} {out}: {cfg['width']}×{cfg['height']}，{len(frames)} 帧，"
          f"累计 {sum(durations)}ms，{size // 1024}KB" + ("（偏大，试试 --colors 降一档）" if over else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
