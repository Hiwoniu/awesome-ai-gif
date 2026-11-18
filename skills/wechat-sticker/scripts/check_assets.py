#!/usr/bin/env python3
"""对一套表情做上架前机检，逐项给出 FAIL / WARN / OK。

检查的目录结构：
    <套目录>/pack.json
    <套目录>/assets/cover.png、icon.png、banner.png
    <套目录>/<案例目录>/case.json、result.gif

含 case.json 或 result.gif 的子目录才算一张表情，其他子目录（review/ 等）不检查。

有任何 FAIL 时退出码为 1。机检通过只代表规格合格，不代表审核会通过。
机检分级和差异哈希的思路参考 charmoji-sticker-skill（MIT）。
"""
from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter

import gifkit


class Report:
    def __init__(self) -> None:
        self.items: list[dict] = []

    def add(self, level: str, target: str, message: str) -> None:
        self.items.append({"level": level, "target": target, "message": message})

    def count(self, level: str) -> int:
        return sum(1 for i in self.items if i["level"] == level)


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def count_on(mask: Image.Image) -> int:
    return mask.histogram()[255]


def white_edge_ratio(frame: Image.Image) -> float | None:
    """主体轮廓上近白像素的占比。没有透明区域时返回 None。"""
    r, g, b, a = frame.convert("RGBA").split()
    solid = a.point(lambda v: 255 if v >= 128 else 0)
    if count_on(solid) == frame.width * frame.height:
        return None
    edge = ImageChops.subtract(solid, solid.filter(ImageFilter.MinFilter(3)))
    total = count_on(edge)
    if total == 0:
        return None
    darkest = ImageChops.darker(ImageChops.darker(r, g), b)
    near_white = darkest.point(lambda v: 255 if v >= 240 else 0)
    return count_on(ImageChops.multiply(edge, near_white)) / total


def corners_alpha(im: Image.Image) -> list[int]:
    a = im.convert("RGBA").split()[3]
    w, h = im.size
    return [a.getpixel(p) for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))]


def frame_diff(a: Image.Image, b: Image.Image) -> float:
    """两帧垫灰底后的平均像素差（0–255）。灰底让透明区域的变化也算进去。"""
    def flat(im: Image.Image) -> Image.Image:
        base = Image.new("RGB", im.size, (128, 128, 128))
        base.paste(im, mask=im.split()[3])
        return base.convert("L")
    hist = ImageChops.difference(flat(a), flat(b)).histogram()
    return sum(i * n for i, n in enumerate(hist)) / max(1, sum(hist))


def loop_seam(frames: list[Image.Image]) -> float:
    """末帧离首帧的距离 ÷ 整个动作里离首帧最远的距离。

    回到起点的循环接近 0（实测完好的六帧挥爪约 0.43）；停在动作中途的会接近 1。
    """
    dists = [frame_diff(frames[0], f) for f in frames[1:]]
    peak = max(dists)
    return dists[-1] / peak if peak else 0.0


def check_sticker(case_dir: Path, spec: dict, final: bool, report: Report, route: str = "") -> int | None:
    """检查单张表情，返回它的代表帧哈希。"""
    name = case_dir.name
    rule = spec["sticker"]
    gif = case_dir / "result.gif"
    if not gif.exists():
        report.add("FAIL" if final else "WARN", name, "还没有 result.gif")
        return None

    frames, durations, info = gifkit.read_gif(gif)
    problems = 0

    if info["format"] not in rule["formats"]:
        report.add("FAIL", name, f"格式是 {info['format']}，要求 {'/'.join(rule['formats'])}")
        problems += 1
    if info["size"] != (rule["width"], rule["height"]):
        report.add("FAIL", name, f"尺寸 {info['size'][0]}×{info['size'][1]}，要求 {rule['width']}×{rule['height']}")
        problems += 1
    size_bytes = gif.stat().st_size
    if size_bytes > rule["max_bytes"]:
        report.add("FAIL", name, f"体积 {size_bytes / 1000:.0f}KB，上限 {rule['max_bytes'] / 1000:.0f}KB")
        problems += 1
    if len(frames) < rule["min_frames"]:
        report.add("FAIL", name, f"只有 {len(frames)} 帧，不是动图")
        problems += 1
    elif rule["must_loop"] and info.get("loop") != 0:
        report.add("FAIL", name, "没有设置无限循环")
        problems += 1

    hashes = [gifkit.dhash(f) for f in frames]
    if len(frames) >= 2:
        movement = max(gifkit.hamming(hashes[0], h) for h in hashes[1:])
        if movement <= spec["pack"]["still_distance"]:
            report.add("WARN", name, "各帧几乎一样，动作可能看不出来")
            problems += 1

    # 轻动效是脚本按周期生成的，天然闭环；只查模型画的序列帧
    if route == "frames" and len(frames) >= 3:
        seam = loop_seam(frames)
        if seam > 0.6:
            report.add("WARN", name, f"末帧和首帧差得较远（达到动作幅度的 {seam:.0%}），"
                                     "可能没回到起点，循环到头会跳一下，实际播放看一遍")
            problems += 1

    ratios = [(white_edge_ratio(f), i) for i, f in enumerate(frames)]
    ratios = [(r, i) for r, i in ratios if r is not None]
    if ratios:
        ratio, worst = max(ratios)
        if ratio > 0.5:
            report.add("WARN", name, f"第 {worst + 1} 帧轮廓上 {ratio:.0%} 是近白像素，放到黑底上查一下白边")
            problems += 1

    if problems == 0:
        report.add("OK", name, f"{len(frames)} 帧，{size_bytes / 1000:.0f}KB")
    return hashes[0]


def check_copy(pack: dict, cases: dict[str, dict], spec: dict, final: bool, report: Report) -> None:
    rule = spec["copy"]
    missing = "FAIL" if final else "WARN"
    seen: dict[str, str] = {}
    for name, case in cases.items():
        word = (case.get("meaning") or "").strip()
        if not word:
            report.add(missing, name, "case.json 里还没填含义词（meaning）")
            continue
        if len(word) > rule["meaning_max_chars"]:
            report.add("FAIL", name, f"含义词“{word}”超过 {rule['meaning_max_chars']} 个字")
        if word in seen:
            report.add("FAIL", name, f"含义词“{word}”和 {seen[word]} 重复")
        seen.setdefault(word, name)
        for banned in rule["banned_words"]:
            if banned in word:
                report.add("FAIL", name, f"含义词里有“{banned}”")

    for field, limit, label in (("title", rule["title_max_chars"], "专辑名称"),
                                ("intro", rule["intro_max_chars"], "专辑介绍"),
                                ("copyright", rule["copyright_max_chars"], "版权信息")):
        text = (pack.get(field) or "").strip()
        if not text:
            report.add(missing, "pack.json", f"还没填{label}（{field}）")
            continue
        if len(text) > limit:
            report.add("FAIL", "pack.json", f"{label} {len(text)} 个字，上限 {limit}")
        for banned in rule["banned_words"]:
            if banned in text:
                report.add("FAIL", "pack.json", f"{label}里有“{banned}”")


def check_asset(pack_dir: Path, key: str, rule: dict, final: bool, report: Report) -> None:
    label = rule["label"]
    path = next((pack_dir / "assets" / f for f in rule["files"] if (pack_dir / "assets" / f).exists()), None)
    if path is None:
        report.add("FAIL" if final else "WARN", key, f"缺{label}（assets/{rule['files'][0]}）")
        return

    im = Image.open(path)
    problems = 0
    if im.size != (rule["width"], rule["height"]):
        report.add("FAIL", key, f"{label}尺寸 {im.width}×{im.height}，要求 {rule['width']}×{rule['height']}")
        problems += 1
    size_bytes = path.stat().st_size
    if size_bytes > rule["max_bytes"]:
        report.add("FAIL", key, f"{label}体积 {size_bytes / 1000:.0f}KB，上限 {rule['max_bytes'] / 1000:.0f}KB")
        problems += 1

    corners = corners_alpha(im)
    if rule["transparent"]:
        if any(c > 0 for c in corners):
            report.add("FAIL", key, f"{label}必须是透明底，四角里有不透明的")
            problems += 1
        else:
            ratio = white_edge_ratio(im)
            if ratio is not None and ratio > 0.5:
                report.add("WARN", key, f"{label}轮廓上 {ratio:.0%} 是近白像素，查一下白边")
                problems += 1
    else:
        alpha_min = im.convert("RGBA").split()[3].getextrema()[0]
        if alpha_min < 255:
            report.add("FAIL", key, f"{label}不能有透明区域")
            problems += 1
        if rule.get("no_pure_white"):
            rgb = im.convert("RGB")
            w, h = rgb.size
            if all(min(rgb.getpixel(p)) >= 250 for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))):
                report.add("FAIL", key, f"{label}不能是纯白底")
                problems += 1

    if problems == 0:
        report.add("OK", key, f"{label} {im.width}×{im.height}，{size_bytes / 1000:.0f}KB")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pack", type=Path, help="套目录")
    parser.add_argument("--spec", default="wechat", help="平台规格名或 json 路径（默认 wechat）")
    parser.add_argument("--final", action="store_true",
                        help="提交前模式：数量不足、缺 GIF、缺含义词、缺专辑文案、缺配套素材都算 FAIL")
    parser.add_argument("--report", type=Path, help="把结果另存为 JSON")
    args = parser.parse_args()

    spec = gifkit.load_spec(args.spec)
    report = Report()
    pack = read_json(args.pack / "pack.json")
    # 只有放了 case.json 或 result.gif 的目录才算一张表情；review/、cells/ 这类辅助目录直接跳过
    case_dirs = sorted(d for d in args.pack.iterdir()
                       if d.is_dir() and d.name != "assets" and not d.name.startswith(("_", "."))
                       and ((d / "case.json").exists() or (d / "result.gif").exists()))

    hashes: dict[str, int] = {}
    cases: dict[str, dict] = {}
    for case_dir in case_dirs:
        cases[case_dir.name] = read_json(case_dir / "case.json")
        h = check_sticker(case_dir, spec, args.final, report, route=cases[case_dir.name].get("route", ""))
        if h is not None:
            hashes[case_dir.name] = h

    rule = spec["pack"]
    for a, b in combinations(sorted(hashes), 2):
        if gifkit.hamming(hashes[a], hashes[b]) <= rule["similar_distance"]:
            report.add("WARN", a, f"和 {b} 首帧轮廓相近，并排看一下：只是表情不同算正常，"
                                  "姿势和动作也一样才会被判整套差异不足")

    ready = len(hashes)
    if ready < rule["min_count"]:
        report.add("FAIL" if args.final else "WARN", "整套", f"成品 {ready} 张，成套至少 {rule['min_count']} 张")
    elif ready > rule["max_count"]:
        report.add("FAIL", "整套", f"成品 {ready} 张，一套最多 {rule['max_count']} 张")
    else:
        report.add("OK", "整套", f"成品 {ready} 张")

    check_copy(pack, cases, spec, args.final, report)
    for key, asset_rule in spec["assets"].items():
        check_asset(args.pack, key, asset_rule, args.final, report)

    for item in report.items:
        print(f"[{item['level']:4}] {item['target']}: {item['message']}")
    summary = {level: report.count(level) for level in ("FAIL", "WARN", "OK")}
    print(f"\n{summary['FAIL']} FAIL · {summary['WARN']} WARN · {summary['OK']} OK"
          f"（规格：{spec['title']}{'，提交前模式' if args.final else ''}）")

    if args.report:
        args.report.write_text(json.dumps({"spec": spec["name"], "final": args.final,
                                           "summary": summary, "items": report.items},
                                          ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 1 if summary["FAIL"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
