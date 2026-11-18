"""把 gen/<编号>/new.png 做成 240×240 静态 GIF，写 case.json（含自写文案）。
真实照片风格、带背景（照原套），所以不抠图、不透明；保持原图取景直接缩到 240。字压在照片上（和原套一样），不缩角色。"""
import json, sys
from pathlib import Path
from PIL import Image, ImageFilter
sys.path.insert(0, "/Users/xiangming/me-code/awesome-ai-gif/skills/wechat-sticker/scripts")
import gifkit

TRIAL = Path(__file__).resolve().parent.parent
CAPTIONS = {
    "03": {"text": "哈？", "position": "bottom"},
    "04": {"text": "为啥呀", "position": "bottom"},
    "07": {"text": "笑够没", "position": "bottom"},
    "10": {"text": "啥？", "position": "bottom"},
    "11": {"text": "……", "position": "top"},
    "12": {"text": "嗯哼？", "position": "bottom"},
    "13": {"text": "给我拿来", "position": "bottom"},
    "14": {"text": "？？？", "position": "top"},
    "15": {"text": "我笑了", "position": "top"},
    "17": {"text": "气死我了", "position": "bottom"},
    "18": {"text": "冷静点", "position": "top"},
    "19": {"text": "哦～", "position": "bottom"},
}
MEANING = {"01": "嘿嘿", "02": "举起手来", "03": "哈", "04": "委屈", "05": "就是你", "06": "耶", "07": "笑够没",
           "08": "尴尬", "09": "惊讶", "10": "啥", "11": "无语", "12": "嗯哼", "13": "拿来", "14": "疑惑",
           "15": "我笑了", "16": "呲牙", "17": "气死", "18": "冷静", "19": "哦"}

# 照片铺满画面，不能像 light_motion.py 那样在透明画布上挪，改成在原图里移动取景框
MOTION = {**{k: "zoom" for k in ["02", "03", "05", "09", "10", "18"]},
          **{k: "shake" for k in ["08", "16", "17"]},
          **{k: "bounce" for k in ["01", "06", "12", "13", "15"]},
          **{k: "breathe" for k in ["04", "07", "11", "14", "19"]}}

def photo_frames(im: Image.Image, motion: str) -> tuple[list[Image.Image], int]:
    import math
    side = min(im.size)
    cx, cy = im.width / 2, im.height / 2
    n, dur = (8, 160) if motion == "breathe" else (8, 90)
    frames = []
    for i in range(n):
        t = 2 * math.pi * i / n
        scale, dx, dy = 0.92, 0.0, 0.0
        if motion == "zoom":      # 冲镜头：快速推近再弹回
            scale = 0.92 - 0.10 * max(0.0, math.sin(t))
        elif motion == "shake":   # 左右抖
            dx = 0.025 * math.sin(2 * t)
        elif motion == "bounce":  # 上下颠
            dy = -0.03 * abs(math.sin(t))
        elif motion == "breathe": # 慢慢呼吸般轻推
            scale = 0.92 - 0.035 * (1 - math.cos(t)) / 2
        w = side * scale
        x = min(max(cx - w / 2 + dx * side, 0), im.width - w)
        y = min(max(cy - w / 2 + dy * side, 0), im.height - w)
        frames.append(im.crop((round(x), round(y), round(x + w), round(y + w))).resize((240, 240), Image.Resampling.LANCZOS))
    return frames, dur

def outline(im: Image.Image, px: int = 2) -> Image.Image:
    a = im.split()[3].point(lambda v: 255 if v >= 128 else 0)
    grown = a.filter(ImageFilter.MaxFilter(px * 2 + 1))
    base = Image.new("RGBA", im.size, (255, 255, 255, 0))
    base.putalpha(grown)
    base.alpha_composite(im)
    return base

spec = gifkit.load_spec("wechat")
for k in sys.argv[1:] or sorted(p.parent.name for p in (TRIAL / "_work/gen").glob("*/new.png")):
    src = TRIAL / "_work/gen" / k / "new.png"
    im = Image.open(src).convert("RGBA")
    frames, dur = photo_frames(im, MOTION[k])
    out = TRIAL / k
    out.mkdir(exist_ok=True)
    for stale in ("base.gif",):
        (out / stale).unlink(missing_ok=True)
    r = gifkit.encode_within_limit(frames, out / "result.gif", spec, duration=dur, transparent=False)
    case = {"id": "", "title": MEANING[k], "meaning": MEANING[k], "tags": [], "route": "still", "motion": MOTION[k],
            "remix_of": f"~/Downloads/蜗牛-猫-表情包 第 {k} 张（{src.parent.joinpath('ref.png').name}）",
            "engine": {"provider": "openai", "model": "codex image_gen (tool-managed)", "channel": "codex exec"},
            "checks": {"technical": True, "visual": False, "approved": False, "notes": ""},
            "status": "draft", "created": "2026-11-18"}
    if k in CAPTIONS:
        case["caption"] = {**CAPTIONS[k], "reveal": "char", "size": 40, "color": "#FFFFFF", "stroke-color": "#000000", "edge-color": "#000000"}
    (out / "case.json").write_text(json.dumps(case, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(k, r["bytes"], r["colors"])
