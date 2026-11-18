#!/usr/bin/env python3
"""给做好的表情 GIF 加字：模型只画角色，字由这个脚本后期画上去，字迹清楚、每帧一致。

三种用法：
  单个 GIF：  caption.py result.gif --text "开饭了" --out captioned.gif
  单张表情：  caption.py <套目录>/wx-001-吃饭 --text "开饭了"
  整套：      caption.py <套目录>          （读每张 case.json 里的 caption 字段）

单张和整套模式会把原图保存为同目录的 base.gif，以后重跑都从 base.gif 加字，不会叠字。
case.json 里的 caption 可以是一句话，也可以是对象，键和命令行参数同名：
  "caption": "谢谢！"
  "caption": {"text": "我要|减肥", "position": "right", "reveal": "char", "shrink": 0.8}

文字里用 | 换行（竖排时是换列）。position 选 left/right 时默认竖排。
默认样式和常见表情一致：蓝字、白色描边、外圈一道细蓝边，放到白色和黑色聊天背景上都看得清。
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageColor, ImageDraw, ImageFont

import gifkit

# 可免费商用的中文字体，按优先顺序找。文件名里含这些片段就算命中。
FREE_FONTS = ["SmileySans", "得意黑", "ZCOOLKuaiLe", "站酷快乐体", "ZCOOLQingKeHuangYou", "站酷庆科黄油体",
              "SourceHanSans", "思源黑体", "NotoSansCJK", "NotoSansSC", "AlimamaShuHeiTi", "阿里妈妈数黑体",
              "LXGWWenKai", "霞鹜文楷"]
# 找不到上面的字体时退回系统字体，只适合练手：商用授权要自己确认。
SYSTEM_FONTS = ["PingFang.ttc", "STHeiti Medium.ttc", "Hiragino Sans GB.ttc", "Arial Unicode.ttf",
                "msyhbd.ttc", "msyh.ttc", "simhei.ttf", "wqy-microhei.ttc", "wqy-zenhei.ttc"]
FONT_DIRS = [Path(__file__).resolve().parent.parent / "fonts", Path.home() / "Library/Fonts",
             Path("/Library/Fonts"), Path("/System/Library/Fonts"), Path("/usr/share/fonts"),
             Path("/usr/local/share/fonts"), Path.home() / ".local/share/fonts", Path.home() / ".fonts",
             Path("C:/Windows/Fonts")]
FONT_SUFFIXES = {".ttf", ".otf", ".ttc"}

DEFAULTS = {"text": None, "position": "top", "vertical": None, "size": None, "color": "#1E8CFF",
            "stroke_color": "#FFFFFF", "edge_color": None, "stroke": None, "reveal": "none",
            "reveal_ratio": 0.5, "shrink": None, "margin": 6, "font": None}


def font_files() -> list[Path]:
    found = []
    for d in FONT_DIRS:
        if d.is_dir():
            found += [p for p in d.rglob("*") if p.suffix.lower() in FONT_SUFFIXES]
    return found


def find_font(explicit: str | None) -> tuple[Path, bool]:
    """返回 (字体路径, 是否确认可商用)。"""
    if explicit or os.environ.get("STICKER_FONT"):
        path = Path(explicit or os.environ["STICKER_FONT"]).expanduser()
        if not path.exists():
            raise SystemExit(f"找不到字体文件 {path}")
        return path, True
    files = font_files()
    for key in FREE_FONTS:
        for p in files:
            if key.lower() in p.name.lower().replace(" ", ""):
                return p, True
    for name in SYSTEM_FONTS:
        for p in files:
            if p.name.lower() == name.lower():
                return p, False
    raise SystemExit("没有找到中文字体。下载一个可免费商用的字体（如得意黑 SmileySans、思源黑体）"
                     "放进 skill 的 fonts/ 目录，或用 --font 指定。")


def missing_glyphs(font_path: Path, text: str) -> list[str]:
    """字体里没有的字。缺字会画成和“未定义字符”一样的方块或空白，拿它比对。"""
    font = ImageFont.truetype(str(font_path), 32)

    def shape(ch: str) -> bytes:
        im = Image.new("L", (48, 48), 0)
        ImageDraw.Draw(im).text((4, 4), ch, font=font, fill=255)
        return im.tobytes()

    notdef = shape("\U000F0000")
    return sorted({ch for ch in text if ch.strip() and ch != "|" and shape(ch) == notdef})


def resolve_color(value: str) -> tuple[int, int, int]:
    return ImageColor.getrgb(value)[:3]


def darker(rgb: tuple[int, int, int], k: float = 0.75) -> tuple[int, int, int]:
    return tuple(round(c * k) for c in rgb)


def layout(text: str, font_path: Path, box: tuple[int, int, int, int], vertical: bool,
           size: int | None, stroke: int | None) -> tuple[ImageFont.FreeTypeFont, int, list[tuple[str, int, int]]]:
    """把文字排进 box，返回 (字体, 描边粗细, [(字, x, y), ...])，坐标是每个字的左上角。

    没指定字号时取放得下的最大字号。每个字单独定位，竖排和逐字出现都用同一套坐标。
    """
    lines = [l for l in text.split("|") if l]
    bw, bh = box[2] - box[0], box[3] - box[1]
    top = size or 72
    for px in range(top, 11, -1):
        font = ImageFont.truetype(str(font_path), px)
        sw = stroke if stroke is not None else max(2, round(px / 10))
        pad = sw + max(1, sw // 2)  # 描边加外圈
        cell = px + pad
        gap = round(px * 0.12)
        if vertical:
            col_w = cell + gap
            w = col_w * len(lines) - gap
            h = max(len(l) for l in lines) * (px + gap) - gap + 2 * pad
        else:
            widths = [sum(font.getlength(ch) for ch in l) for l in lines]
            w = max(widths) + 2 * pad
            h = (cell + gap) * len(lines) - gap
        if (w <= bw and h <= bh) or px == 12:
            break
    if w > bw or h > bh:
        print(f"WARN 文字太长，最小字号也放不下：{text}", file=sys.stderr)

    x0 = box[0] + (bw - w) / 2
    y0 = box[1] + (bh - h) / 2
    glyphs = []
    if vertical:
        # 竖排从右往左排列
        for ci, line in enumerate(lines):
            cx = x0 + w - (ci + 1) * (cell + gap) + gap + pad / 2
            col_h = len(line) * (px + gap) - gap
            cy = y0 + pad + (h - 2 * pad - col_h) / 2
            for i, ch in enumerate(line):
                adv = font.getlength(ch)
                glyphs.append((ch, round(cx + (px - adv) / 2), round(cy + i * (px + gap))))
    else:
        for li, line in enumerate(lines):
            lw = sum(font.getlength(ch) for ch in line)
            x = x0 + (w - lw) / 2
            y = y0 + pad / 2 + li * (cell + gap)
            for ch in line:
                glyphs.append((ch, round(x), round(y)))
                x += font.getlength(ch)
    return font, sw, glyphs


def render_text(size: tuple[int, int], font, sw: int, glyphs, count: int, color, stroke_color,
                edge_color) -> Image.Image:
    """画出前 count 个字。三遍：外圈细边、白色描边、字身。返回 1-bit 透明的 RGBA 图层。"""
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    shown = glyphs[:count]
    edge = max(1, sw // 2)
    for ch, x, y in shown:
        draw.text((x, y), ch, font=font, fill=edge_color, stroke_width=sw + edge, stroke_fill=edge_color)
    for ch, x, y in shown:
        draw.text((x, y), ch, font=font, fill=stroke_color, stroke_width=sw, stroke_fill=stroke_color)
    for ch, x, y in shown:
        draw.text((x, y), ch, font=font, fill=color)
    return gifkit.hard_alpha(layer, erode=0)


def shrink_frames(frames: list[Image.Image], scale: float, position: str) -> list[Image.Image]:
    """角色整体缩小，贴到字的对面一侧，给字让位置。所有帧同一个缩放和偏移，动作不变形。"""
    w, h = frames[0].size
    nw, nh = round(w * scale), round(h * scale)
    x = (w - nw) // 2
    y = (h - nh) // 2
    if position == "top":
        y = h - nh
    elif position == "bottom":
        y = 0
    elif position == "left":
        x = w - nw
    elif position == "right":
        x = 0
    out = []
    for f in frames:
        canvas = Image.new("RGBA", (w, h), (255, 255, 255, 0))
        canvas.alpha_composite(f.resize((nw, nh), Image.Resampling.LANCZOS), (x, y))
        out.append(gifkit.hard_alpha(canvas, erode=0))
    return out


def text_box(size: tuple[int, int], position: str, scale: float | None, margin: int) -> tuple[int, int, int, int]:
    w, h = size
    # 缩小了就用让出来的那块，没缩小就默认占 30%
    band = 1 - scale if scale else 0.3
    if position == "top":
        return (margin, margin, w - margin, round(h * band))
    if position == "bottom":
        return (margin, h - round(h * band), w - margin, h - margin)
    if position == "left":
        return (margin, margin, round(w * band), h - margin)
    return (w - round(w * band), margin, w - margin, h - margin)


def split_for_reveal(frames, durations, times):
    """在每个字出现的时刻把帧切开，逐字出现不受原 GIF 帧数限制。返回 (帧, 时长, 起始时刻)。"""
    out_f, out_d, out_t = [], [], []
    t = 0
    for f, d in zip(frames, durations):
        cuts = sorted({c for c in times if t < c < t + d})
        start = t
        for c in cuts + [t + d]:
            if c - start >= 20:  # GIF 最短可靠时长约 20ms，太短就并入前一段
                out_f.append(f)
                out_d.append(c - start)
                out_t.append(start)
                start = c
        if start < t + d and out_d:
            out_d[-1] += t + d - start
        t += d
    return out_f, out_d, out_t


def overlap_ratio(frames: list[Image.Image], layer: Image.Image) -> float:
    """字压在角色身上的比例（取最糟的一帧）。"""
    text = layer.split()[3]
    total = text.histogram()[255]
    if not total:
        return 0.0
    worst = 0
    for f in frames:
        both = ImageChops.multiply(text, f.split()[3].point(lambda v: 255 if v >= 128 else 0))
        worst = max(worst, both.histogram()[255])
    return worst / total


def caption_gif(src: Path, out: Path, opts: dict, spec: dict) -> dict:
    frames, durations, _ = gifkit.read_gif(src)
    durations = [d or 100 for d in durations]
    position = opts["position"]
    vertical = opts["vertical"] if opts["vertical"] is not None else position in ("left", "right")
    if opts["shrink"]:
        frames = shrink_frames(frames, opts["shrink"], position)

    font_path, licensed = find_font(opts["font"])
    missing = missing_glyphs(font_path, opts["text"])
    if missing:
        print(f"WARN 字体 {font_path.name} 里没有这些字，会显示成方块或空白：{''.join(missing)}。"
              "换个说法，或用 --font 换字体", file=sys.stderr)
    size = frames[0].size
    box = text_box(size, position, opts["shrink"], opts["margin"])
    font, sw, glyphs = layout(opts["text"], font_path, box, vertical, opts["size"], opts["stroke"])
    color = resolve_color(opts["color"])
    stroke_color = resolve_color(opts["stroke_color"])
    edge_color = resolve_color(opts["edge_color"]) if opts["edge_color"] else darker(color)
    n = len(glyphs)

    full = render_text(size, font, sw, glyphs, n, color, stroke_color, edge_color)
    overlap = overlap_ratio(frames, full)

    if opts["reveal"] == "char" and n > 1:
        total = sum(durations)
        step = total * opts["reveal_ratio"] / n
        times = [round(i * step) for i in range(1, n)]
        frames, durations, starts = split_for_reveal(frames, durations, times)
        layers = {}
        out_frames = []
        for f, t in zip(frames, starts):
            k = 1 + sum(1 for c in times if c <= t)
            if k not in layers:
                layers[k] = render_text(size, font, sw, glyphs, k, color, stroke_color, edge_color)
            out_frames.append(Image.alpha_composite(f, layers[k]))
    else:
        out_frames = [Image.alpha_composite(f, full) for f in frames]

    out_frames = [gifkit.hard_alpha(f, erode=0) for f in out_frames]
    result = gifkit.encode_within_limit(out_frames, out, spec, durations, transparent=True)
    result.update(font=str(font_path), licensed=licensed, overlap=overlap, font_size=font.size)
    return result


def merge_opts(base: dict, override) -> dict:
    opts = dict(base)
    if isinstance(override, str):
        opts["text"] = override
    elif isinstance(override, dict):
        opts.update({k.replace("-", "_"): v for k, v in override.items()})
    return opts


def case_source(case_dir: Path) -> Path | None:
    """单张表情目录的无字原图：有 base.gif 用它，没有就把 result.gif 存一份成 base.gif。"""
    base, result = case_dir / "base.gif", case_dir / "result.gif"
    if base.exists():
        return base
    if result.exists():
        shutil.copy2(result, base)
        return base
    return None


def report(name: str, r: dict) -> bool:
    ok = r["within_limit"]
    print(f"{'OK  ' if ok else 'FAIL'} {name}: {r['font_size']}px，{r['frames']} 帧，{r['bytes'] / 1000:.0f}KB")
    if r["overlap"] > 0.15:
        print(f"WARN {name}: 字有 {r['overlap']:.0%} 压在角色身上，试试 --shrink 0.8 或换 --position")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("target", type=Path, help="GIF 文件、单张表情目录或套目录")
    parser.add_argument("--text", help="文字，| 换行（竖排时换列）")
    parser.add_argument("--out", type=Path, help="输出 GIF（只在输入是 GIF 文件时用，默认 <原名>_caption.gif）")
    parser.add_argument("--position", choices=["top", "bottom", "left", "right"], help="字放哪边（默认 top）")
    parser.add_argument("--vertical", action=argparse.BooleanOptionalAction, default=None,
                        help="竖排（left/right 默认竖排）")
    parser.add_argument("--size", type=int, help="字号上限（默认自动取放得下的最大字号）")
    parser.add_argument("--color", help="字身颜色（默认 #1E8CFF 蓝）")
    parser.add_argument("--stroke-color", help="描边颜色（默认白）")
    parser.add_argument("--edge-color", help="最外圈细边颜色（默认字身颜色加深）")
    parser.add_argument("--stroke", type=int, help="描边粗细像素（默认字号的 1/10）")
    parser.add_argument("--reveal", choices=["none", "char"], help="char：逐字出现（默认 none 一直显示）")
    parser.add_argument("--reveal-ratio", type=float, help="逐字出现用掉整段循环的多少比例（默认 0.5）")
    parser.add_argument("--shrink", type=float, help="把角色缩到这个比例、贴到字的对面，给字让位（如 0.8）")
    parser.add_argument("--margin", type=int, help="字离画面边缘的像素（默认 6）")
    parser.add_argument("--font", help="字体文件路径（默认先找可免费商用的中文字体，也读环境变量 STICKER_FONT）")
    parser.add_argument("--spec", default="wechat", help="平台规格名或 json 路径（默认 wechat）")
    args = parser.parse_args()

    spec = gifkit.load_spec(args.spec)
    cli = {k: v for k, v in vars(args).items() if k in DEFAULTS and v is not None}
    base = merge_opts(DEFAULTS, cli)
    target = args.target

    jobs: list[tuple[str, Path, Path, dict]] = []
    if target.is_file():
        if not base["text"]:
            parser.error("输入是 GIF 文件时要给 --text")
        jobs.append((target.name, target, args.out or target.with_name(f"{target.stem}_caption.gif"), base))
    elif (target / "case.json").exists() or (target / "result.gif").exists():
        case = json.loads((target / "case.json").read_text(encoding="utf-8")) if (target / "case.json").exists() else {}
        opts = merge_opts(merge_opts(DEFAULTS, case.get("caption")), cli)
        if not opts["text"]:
            parser.error("这张表情的 case.json 里没有 caption，用 --text 给文字")
        src = case_source(target)
        if src is None:
            parser.error(f"{target} 里没有 result.gif")
        jobs.append((target.name, src, target / "result.gif", opts))
    elif target.is_dir():
        for case_dir in sorted(p for p in target.iterdir() if (p / "case.json").exists()):
            case = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
            if not case.get("caption"):
                continue
            src = case_source(case_dir)
            if src is None:
                print(f"SKIP {case_dir.name}: 没有 result.gif")
                continue
            jobs.append((case_dir.name, src, case_dir / "result.gif", merge_opts(merge_opts(DEFAULTS, case["caption"]), cli)))
        if not jobs:
            print("没有要加字的表情：在各张 case.json 里写 caption 字段。")
            return 1
    else:
        parser.error(f"找不到 {target}")

    failed = 0
    licensed = True
    font = None
    for name, src, out, opts in jobs:
        r = caption_gif(src, out, opts, spec)
        failed += not report(name, r)
        licensed &= r["licensed"]
        font = r["font"]
    print(f"\n字体：{font}")
    if not licensed:
        print("WARN 用的是系统字体，只适合练手。要上架就换可免费商用的字体（得意黑、思源黑体、站酷快乐体），"
              "放进 skill 的 fonts/ 目录或用 --font 指定。")
    print("加完字逐张播放看一遍：字有没有挡脸、在白底和黑底上是否都看得清。")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
