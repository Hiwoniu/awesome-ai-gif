#!/usr/bin/env python3
"""复刻第一步：拆开一套 GIF，给每张做动作参考图和提示词，供换角色重画。

每张 GIF 先判断属于哪一类：
  still   整段只有一个姿势在动（点头、弹跳、摇摆这类整体位移和旋转）。
          只需要重画一个静态姿势，再套回最接近的轻动效。整套所有 still 的姿势
          拼进一张 poses/ref.png，一次出图画完，跨张一致性最好。
  frames  姿势本身在变（挥手、转身）。抽最多 6 个关键帧拼成 <名字>/ref.png，
          让模型按格换角色，合成时每个关键帧沿用它在原 GIF 里覆盖的总时长。

输出目录：
  plan.json           整套计划，remix_build.py 读它
  poses/ref.png       still 类的姿势参考图集；poses/prompt.md 是提示词
  <名字>/ref.png      frames 类的关键帧参考图；<名字>/prompt.md 是提示词
出图后把新图存为 poses/new.png、<名字>/new.png，再运行 remix_build.py。
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image

import gifkit
from light_motion import MOTIONS, build_frames

ANALYSIS_SIZE = (96, 96)
STRENGTHS = (0.5, 0.75, 1.0, 1.5, 2.0, 3.0)

POSES_PROMPT = """参考图 1 是新角色的定稿图，参考图 2 是一张 {cols} 列×{rows} 行的姿势参考图，共 {count} 格。
生成一张同样 {cols} 列×{rows} 行、{count} 格的姿势图集：每一格画参考图 1 的角色，摆出参考图 2 同一格里的姿势、手势、表情和朝向，道具照搬但画成新角色的画风。逐格对照细节：抬的是哪只手哪只脚、脚是否着地、眼睛睁开还是闭上、嘴巴张开还是闭上，都和参考图 2 那一格一致。
只借参考图 2 的动作，不要沿用它的角色外形、配色、服装、花纹和画风，全部换成参考图 1 的。
每格尺寸完全一致，从左到右、从上到下与参考图 2 一一对应，角色全身入画并居中，不越格。{blank}
角色：{character}
风格：{style}
{background}画面里不出现任何文字、字母、数字、标点和拟声字，参考图 2 里的字幕和文字一律不画。无边框、无格线、无阴影。
"""

FRAMES_PROMPT = """参考图 1 是新角色的定稿图，参考图 2 是一段动画的 {count} 个关键帧，按 {cols} 列×{rows} 行排列，从左到右、从上到下播放。
生成一张同样 {cols} 列×{rows} 行、{count} 格的动画序列图：每一格画参考图 1 的角色，做出参考图 2 同一格里的姿势和动作，在格子里的位置、大小、朝向也和参考图 2 那一格一致，这样连起来播放动作才对得上。表情也逐格照搬：眼睛睁闭、嘴巴开合、嘴型和参考图 2 那一格一样，不要统一改成同一个表情。
只借参考图 2 的动作，不要沿用它的角色外形、配色、服装、花纹和画风，全部换成参考图 1 的。
每个面板尺寸完全一致，所有格子机位固定，同一个角色、同一套配色。
角色：{character}
风格：{style}
{background}画面里不出现任何文字、字母、数字、标点和拟声字，参考图 2 里的字幕和文字一律不画。不画格线，每格四周给角色留少量边距。无边框、无阴影。
"""

# 白底：合成时用 --key-white 去底，所以白色部位必须有闭合描边。
# 透明底：3D、毛绒、无描边的画风用这个，白色部位贴着白底会被一起抠掉。
BACKGROUND_WHITE = "背景：纯白，不要渐变和纹理。白色的部位和道具都要有完整闭合的深色描边。"
BACKGROUND_TRANSPARENT = ("背景：透明背景（transparent background），格子之间和角色四周都不要任何底色、地面和阴影。")


def subject_masks(frames: list[Image.Image]) -> list[Image.Image]:
    """每帧的主体蒙版。原 GIF 有透明就用透明通道，没有就从边缘去白底。"""
    has_alpha = any(f.split()[3].getextrema()[0] < 255 for f in frames)
    out = []
    for f in frames:
        im = f if has_alpha else gifkit.key_white(gifkit.flatten(f).convert("RGBA"))
        out.append(im.split()[3].point(lambda v: 255 if v >= 128 else 0))
    return out


def with_mask(frame: Image.Image, mask: Image.Image) -> Image.Image:
    im = gifkit.flatten(frame).convert("RGBA")
    im.putalpha(mask)
    return im


def iou(a: Image.Image, b: Image.Image) -> float:
    ha = a.histogram()[255]
    hb = b.histogram()[255]
    inter = Image.composite(a, Image.new("L", a.size, 0), b).histogram()[255]
    union = ha + hb - inter
    return inter / union if union else 1.0


def analysis_masks(frames: list[Image.Image]) -> list[Image.Image]:
    """整组共用一个裁切框缩到小尺寸，只留蒙版，用来比较轮廓。"""
    fitted = gifkit.fit_frames(frames, ANALYSIS_SIZE, scale=1.0)
    return [f.split()[3].point(lambda v: 255 if v >= 128 else 0) for f in fitted]


def merge_repeats(frames, masks, durations):
    """相邻几乎一样的帧合并成一帧，时长相加。"""
    keep_f, keep_m, keep_d = [frames[0]], [masks[0]], [durations[0]]
    small = analysis_masks([with_mask(f, m) for f, m in zip(frames, masks)])
    last = small[0]
    for f, m, d, s in zip(frames[1:], masks[1:], durations[1:], small[1:]):
        if iou(last, s) > 0.995 and gifkit.hamming(gifkit.dhash(keep_f[-1]), gifkit.dhash(f)) <= 1:
            keep_d[-1] += d
            continue
        keep_f.append(f)
        keep_m.append(m)
        keep_d.append(d)
        last = s
    return keep_f, keep_m, keep_d


def medoid(small: list[Image.Image]) -> int:
    """和其他帧轮廓最接近的那一帧，当作中立姿势。"""
    scores = [sum(iou(a, b) for b in small) for a in small]
    return max(range(len(small)), key=scores.__getitem__)


def fit_motion(subjects: list[Image.Image], base: int) -> dict:
    """拿中立姿势套每种轻动效、每种幅度、每个起始相位，找轮廓最接近原 GIF 的一组。"""
    target = analysis_masks(subjects)
    n = len(subjects)
    static = sum(iou(target[base], t) for t in target) / n
    best = {"motion": None, "strength": 0.0, "phase": 0, "score": static}
    for motion in MOTIONS:
        for strength in STRENGTHS:
            generated = analysis_masks(build_frames(subjects[base], motion, n, strength))
            for phase in range(n):
                score = sum(iou(generated[(i + phase) % n], target[i]) for i in range(n)) / n
                if score > best["score"]:
                    best = {"motion": motion, "strength": strength, "phase": phase, "score": score}
    best["static_score"] = static
    return best


def pick_keyframes(small: list[Image.Image], durations: list[int], limit: int) -> list[dict]:
    """把序列切成 limit 段，每段取第一帧，时长取整段之和。

    切分按“动作量”和“时间”各占一半：只看动作量，动作慢的那段会被并成一个很长的关键帧，
    播放时一顿一顿；只看时间，快动作的关键姿势会被跳过。
    """
    n = len(small)
    if n <= limit:
        return [{"index": i, "duration": durations[i]} for i in range(n)]
    motion = [1 - iou(a, b) for a, b in zip(small, small[1:])]
    motion_total = sum(motion) or 1.0
    time_total = sum(durations[:-1]) or 1
    cum = [0.0]
    for m, d in zip(motion, durations):
        cum.append(cum[-1] + 0.5 * m / motion_total + 0.5 * d / time_total)
    total = cum[-1] or 1.0
    chosen: list[int] = []
    for j in range(limit):
        target = j * total / limit
        idx = next(i for i, c in enumerate(cum) if c >= target - 1e-9)
        if chosen and idx <= chosen[-1]:
            idx = chosen[-1] + 1
        chosen.append(min(idx, n - limit + j))
    bounds = chosen + [n]
    return [{"index": chosen[k], "duration": sum(durations[bounds[k]:bounds[k + 1]])}
            for k in range(limit)]


def grid_for(count: int) -> tuple[int, int]:
    if count <= 3:
        return count, 1
    if count == 4:
        return 2, 2
    if count <= 6:
        return 3, 2
    if count <= 9:
        return 3, 3
    return 4, 4


def compose_sheet(images: list[Image.Image], cols: int, rows: int, cell: int, scale: float) -> Image.Image:
    """把图片按网格排在纯白底上，每张等比缩放后居中。images 已经是同一裁切框时位置关系会保留。"""
    sheet = Image.new("RGB", (cols * cell, rows * cell), (255, 255, 255))
    for (left, top, right, bottom), im in zip(gifkit.grid_boxes(sheet.size, cols, rows), images):
        w, h = im.size
        ratio = min((right - left) * scale / w, (bottom - top) * scale / h)
        small = im.resize((max(1, round(w * ratio)), max(1, round(h * ratio))), Image.Resampling.LANCZOS)
        x = left + (right - left - small.width) // 2
        y = top + (bottom - top - small.height) // 2
        sheet.paste(small, (x, y), small if small.mode == "RGBA" else None)
    return sheet


def union_box(masks: list[Image.Image]) -> tuple[int, int, int, int]:
    boxes = [m.getbbox() for m in masks if m.getbbox()]
    if not boxes:
        return (0, 0, *masks[0].size)
    return (min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes))


def analyse(path: Path, args) -> dict:
    frames, durations, _ = gifkit.read_gif(path)
    durations = [d if d and d >= 20 else 100 for d in durations]
    masks = subject_masks(frames)
    frames, masks, durations = merge_repeats(frames, masks, durations)
    subjects = [with_mask(f, m) for f, m in zip(frames, masks)]
    small = analysis_masks(subjects)
    base = medoid(small)

    item = {"name": path.stem, "source": str(path), "frames": len(frames), "total_ms": sum(durations)}
    motion = fit_motion(subjects, base) if len(frames) > 1 else \
        {"motion": None, "strength": 0.0, "phase": 0, "score": 1.0, "static_score": 1.0}
    # 判据：套上某种轻动效后轮廓几乎完全吻合，且明显好过“完全不动”，说明姿势没变、只是整体在动；
    # 或者本来就几乎不动。姿势真在变的（挥手），套什么轻动效都不会比不动好多少。
    explained = motion["motion"] is not None and motion["score"] >= args.fit_threshold \
        and motion["score"] - motion["static_score"] >= 0.03
    still = explained or motion["static_score"] >= 0.99
    if args.force:
        still = args.force == "still"
    if still:
        if not explained and not args.force:
            motion.update(motion=None, strength=0.0, phase=0, score=motion["static_score"])
        item.update(route="still", base=base, motion=motion,
                    duration=durations)
        box = masks[base].getbbox() or (0, 0, *frames[base].size)
        item["_pose"] = gifkit.flatten(subjects[base]).crop(box)
    else:
        keys = pick_keyframes(small, durations, args.max_keyframes)
        cols, rows = grid_for(len(keys))
        box = union_box(masks)
        crops = [gifkit.flatten(subjects[k["index"]]).crop(box) for k in keys]
        item.update(route="frames", keyframes=keys, grid=[cols, rows])
        item["_sheet"] = compose_sheet(crops, cols, rows, args.cell, 0.86)
    return item


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputs", nargs="+", type=Path, help="GIF 文件，或放着一套 GIF 的目录")
    parser.add_argument("--out", type=Path, required=True, help="工作目录")
    parser.add_argument("--character", default="[与新角色定稿图完全相同的角色描述]", help="新角色的“角色”描述")
    parser.add_argument("--style", default="[与新角色定稿图一致的风格描述]", help="新角色的“风格”描述")
    parser.add_argument("--max-keyframes", type=int, default=6, help="frames 类最多抽几个关键帧（默认 6，最多 9）")
    parser.add_argument("--fit-threshold", type=float, default=0.95,
                        help="套轻动效后轮廓吻合度达到多少算 still（0–1，默认 0.95）")
    parser.add_argument("--force", choices=["still", "frames"], help="不自动判断，全部按这一类处理")
    parser.add_argument("--cell", type=int, default=512, help="参考图每格边长（默认 512）")
    parser.add_argument("--transparent", action="store_true",
                        help="提示词要求透明底（3D、毛绒、无描边画风用），合成时不加 --key-white")
    parser.add_argument("--character-image", type=Path, help="新角色定稿图路径，写进 plan.json 供 codex_gen.py 使用")
    args = parser.parse_args()
    args.max_keyframes = max(2, min(args.max_keyframes, 9))

    paths: list[Path] = []
    for p in args.inputs:
        # 目录：散放的 *.gif，或按套目录结构放在 <案例>/result.gif
        paths += sorted(set(p.glob("*.gif")) | set(p.glob("*/result.gif"))) if p.is_dir() else [p]
    # 每张表情放在自己的目录里时（wx-001-xxx/result.gif），用目录名当名字
    named = []
    for p in paths:
        name = p.parent.name if p.stem == "result" else p.stem
        named.append((name, p))
    if not named:
        parser.error("没找到 GIF")

    args.out.mkdir(parents=True, exist_ok=True)
    background = BACKGROUND_TRANSPARENT if args.transparent else BACKGROUND_WHITE
    items = []
    for name, path in named:
        item = analyse(path, args)
        item["name"] = name
        items.append(item)

    stills = [i for i in items if i["route"] == "still"]
    pose_sheets = []
    for start in range(0, len(stills), 16):
        group = stills[start:start + 16]
        cols, rows = grid_for(len(group))
        sheet_dir = args.out / ("poses" if start == 0 else f"poses-{start // 16 + 1}")
        sheet_dir.mkdir(parents=True, exist_ok=True)
        compose_sheet([i.pop("_pose") for i in group], cols, rows, 384, 0.82).save(sheet_dir / "ref.png")
        blank = "" if cols * rows == len(group) else f"网格里最后 {cols * rows - len(group)} 格留空。"
        (sheet_dir / "prompt.md").write_text(POSES_PROMPT.format(
            cols=cols, rows=rows, count=len(group), blank=blank,
            character=args.character, style=args.style, background=background), encoding="utf-8")
        for k, i in enumerate(group):
            i["sheet"] = sheet_dir.name
            i["cell"] = k
        pose_sheets.append({"dir": sheet_dir.name, "grid": [cols, rows], "count": len(group)})

    for i in items:
        if i["route"] == "frames":
            d = args.out / i["name"]
            d.mkdir(parents=True, exist_ok=True)
            i.pop("_sheet").save(d / "ref.png")
            cols, rows = i["grid"]
            (d / "prompt.md").write_text(FRAMES_PROMPT.format(
                cols=cols, rows=rows, count=len(i["keyframes"]),
                character=args.character, style=args.style, background=background), encoding="utf-8")

    plan = {"version": 1, "transparent": args.transparent,
            "character_image": str(args.character_image.resolve()) if args.character_image else None,
            "pose_sheets": pose_sheets, "items": items}
    (args.out / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    generations = len(pose_sheets) + sum(1 for i in items if i["route"] == "frames")
    for i in items:
        if i["route"] == "still":
            m = i["motion"]
            fit = f"{m['motion']} ×{m['strength']}，吻合度 {m['score']:.2f}" if m["motion"] else "静止"
            print(f"still   {i['name']}: {i['frames']} 帧，{fit} → {i['sheet']}/ref.png 第 {i['cell'] + 1} 格")
        else:
            print(f"frames  {i['name']}: {i['frames']} 帧 → {len(i['keyframes'])} 个关键帧，{i['name']}/ref.png")
    print(f"\nOK {len(items)} 张，需要出图 {generations} 次。计划在 {args.out / 'plan.json'}")
    if args.transparent:
        print("透明底：出图时要求透明背景，合成时 remix_build.py 不要加 --key-white。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
