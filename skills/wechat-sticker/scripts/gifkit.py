"""切图、去底、合成 GIF 的共用函数。只依赖 Pillow。"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageSequence

SPEC_DIR = Path(__file__).resolve().parent.parent / "specs"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def load_spec(name_or_path: str) -> dict:
    """读平台规格。传名字（wechat）或 json 文件路径都行。"""
    path = Path(name_or_path)
    if path.suffix != ".json":
        path = SPEC_DIR / f"{name_or_path}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def grid_boxes(size: tuple[int, int], cols: int, rows: int, inset: int = 0) -> list[tuple[int, int, int, int]]:
    """按行优先给出网格每格的裁切框。边界按比例取整，除不尽的像素分摊到各格，不丢边。"""
    width, height = size
    xs = [round(i * width / cols) for i in range(cols + 1)]
    ys = [round(i * height / rows) for i in range(rows + 1)]
    return [(xs[c] + inset, ys[r] + inset, xs[c + 1] - inset, ys[r + 1] - inset)
            for r in range(rows) for c in range(cols)]


def flatten(im: Image.Image, background=(255, 255, 255)) -> Image.Image:
    """透明区域垫成纯色，返回 RGB。"""
    im = im.convert("RGBA")
    base = Image.new("RGB", im.size, background)
    base.paste(im, mask=im.split()[3])
    return base


def list_images(folder: Path) -> list[Path]:
    return sorted(p for p in Path(folder).iterdir() if p.suffix.lower() in IMAGE_SUFFIXES)


def key_white(im: Image.Image, tolerance: int = 12) -> Image.Image:
    """从四边向内把连通的近白色变透明。角色内部的白色（眼白、肚皮）不会被去掉。"""
    im = im.convert("RGBA")
    r, g, b, a = im.split()
    low = 255 - tolerance
    darkest = ImageChops.darker(ImageChops.darker(r, g), b)
    near_white = darkest.point(lambda v: 255 if v >= low else 0)
    already_clear = a.point(lambda v: 255 if v < 128 else 0)
    candidate = ImageChops.lighter(near_white, already_clear)

    w, h = im.size
    padded = Image.new("L", (w + 2, h + 2), 255)
    padded.paste(candidate, (1, 1))
    ImageDraw.floodfill(padded, (0, 0), 128)
    background = padded.crop((1, 1, w + 1, h + 1)).point(lambda v: 255 if v == 128 else 0)

    im.putalpha(ImageChops.subtract(a, background))
    return im


def hard_alpha(im: Image.Image, erode: int = 1) -> Image.Image:
    """GIF 只有 1-bit 透明：阈值 128 二值化，再把主体向内收 erode 像素，去掉边缘杂色。"""
    im = im.convert("RGBA")
    alpha = im.split()[3].point(lambda v: 255 if v >= 128 else 0)
    for _ in range(erode):
        alpha = alpha.filter(ImageFilter.MinFilter(3))
    im.putalpha(alpha)
    return im


def fit_frames(frames: list[Image.Image], size: tuple[int, int], scale: float = 0.92) -> list[Image.Image]:
    """把一组帧等比缩放后居中放到 size 画布上。

    所有帧共用同一个裁剪框和缩放比，否则每帧各自裁剪会把动作位移吃掉。
    """
    frames = [f.convert("RGBA") for f in frames]
    box = None
    for f in frames:
        b = f.split()[3].getbbox()
        if b is None:
            continue
        box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
    if box is None:
        box = (0, 0, *frames[0].size)

    bw, bh = box[2] - box[0], box[3] - box[1]
    ratio = min(size[0] * scale / bw, size[1] * scale / bh)
    new_size = (max(1, round(bw * ratio)), max(1, round(bh * ratio)))
    offset = ((size[0] - new_size[0]) // 2, (size[1] - new_size[1]) // 2)

    out = []
    for f in frames:
        canvas = Image.new("RGBA", size, (255, 255, 255, 0))
        canvas.paste(f.crop(box).resize(new_size, Image.Resampling.LANCZOS), offset)
        out.append(canvas)
    return out


def encode_gif(frames, out: Path, duration: int | list[int], transparent: bool, colors: int = 255,
               background=(255, 255, 255)) -> int:
    """写一个无限循环的 GIF，返回文件字节数。所有帧共用一张调色板。"""
    rgbs, masks = [], []
    for f in frames:
        f = f.convert("RGBA")
        alpha = f.split()[3]
        base = Image.new("RGB", f.size, background)
        base.paste(f, mask=alpha)
        rgbs.append(base)
        masks.append(alpha)

    w, h = rgbs[0].size
    strip = Image.new("RGB", (w * len(rgbs), h))
    for i, im in enumerate(rgbs):
        strip.paste(im, (i * w, 0))
    palette_image = strip.quantize(colors=min(colors, 255), method=Image.Quantize.MEDIANCUT,
                                   dither=Image.Dither.NONE)

    pages = []
    for im, mask in zip(rgbs, masks):
        page = im.quantize(palette=palette_image, dither=Image.Dither.NONE)
        palette = page.getpalette() or []
        page.putpalette(palette + [0] * (768 - len(palette)))
        if transparent:
            page.paste(255, mask=ImageChops.invert(mask))
        pages.append(page)

    options = dict(save_all=True, append_images=pages[1:], duration=duration, loop=0,
                   disposal=2, optimize=False)
    if transparent:
        options["transparency"] = 255
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    pages[0].save(out, **options)
    return out.stat().st_size


def export_gif(frames, out: Path, spec: dict, duration: int | list[int] = 120,
               transparent: bool = True) -> dict:
    """按规格导出：缩到规定尺寸，超体积就先减色、再减帧。duration 可以是每帧各自的毫秒数列表。"""
    rule = spec["sticker"]
    size = (rule["width"], rule["height"])
    frames = fit_frames(frames, size)
    if transparent:
        frames = [hard_alpha(f) for f in frames]
    return encode_within_limit(frames, out, spec, duration, transparent)


def encode_within_limit(frames, out: Path, spec: dict, duration: int | list[int] = 120,
                        transparent: bool = True) -> dict:
    """帧已经是规定尺寸时直接编码，超体积就先减色、再减帧。"""
    rule = spec["sticker"]
    attempts = [(frames, duration, c) for c in (255, 128, 64, 32)]
    if len(frames) > 4:
        if isinstance(duration, list):
            # 隔一帧丢一帧，被丢那帧的时长并进前一帧，总时长不变
            halved = [sum(duration[i:i + 2]) for i in range(0, len(duration), 2)]
        else:
            halved = duration * 2
        attempts.append((frames[::2], halved, 64))

    for use_frames, use_duration, colors in attempts:
        size_bytes = encode_gif(use_frames, out, use_duration, transparent, colors)
        if size_bytes <= rule["max_bytes"]:
            break
    return {
        "path": str(out), "bytes": size_bytes, "frames": len(use_frames),
        "duration_ms": use_duration, "colors": colors,
        "within_limit": size_bytes <= rule["max_bytes"],
    }


def read_gif(path: Path) -> tuple[list[Image.Image], list[int], dict]:
    """读出 GIF 的每一帧（RGBA）、每帧时长和文件信息。"""
    with Image.open(path) as im:
        info = dict(im.info)
        info["format"] = im.format
        info["size"] = im.size
        frames, durations = [], []
        for frame in ImageSequence.Iterator(im):
            durations.append(frame.info.get("duration", 0))
            frames.append(frame.convert("RGBA"))
    return frames, durations, info


def dhash(im: Image.Image) -> int:
    """差异哈希，64 位。先垫白底，避免透明区域干扰。"""
    im = im.convert("RGBA")
    base = Image.new("RGB", im.size, (255, 255, 255))
    base.paste(im, mask=im.split()[3])
    small = base.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
    px = small.tobytes()
    bits = 0
    for row in range(8):
        for col in range(8):
            bits = (bits << 1) | (px[row * 9 + col] > px[row * 9 + col + 1])
    return bits


def hamming(a: int, b: int) -> int:
    return bin(a ^ b).count("1")
