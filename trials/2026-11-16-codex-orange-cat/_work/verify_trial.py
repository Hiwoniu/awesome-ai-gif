"""Record artifact checks and the visual review decisions for this trial."""
from pathlib import Path
import json
import sys

from PIL import Image, ImageChops, ImageStat

PACK = Path(__file__).resolve().parents[1]
ROOT = PACK.parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "skills/wechat-sticker/scripts"))
import gifkit
import check_assets


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


cases = sorted(PACK.glob("wx-*/case.json"))
assert len(cases) == 9
meanings = []
records = []
for path in cases:
    case = json.loads(path.read_text())
    assert case["status"] == "draft"
    assert all(key in case for key in ("meaning", "route", "engine", "cost", "checks"))
    meanings.append(case["meaning"])
    directory = path.parent
    assert all((directory / name).is_file() for name in ("prompt.md", "sheet.png", "result.gif"))
    frames, durations, info = gifkit.read_gif(directory / "result.gif")
    assert info["size"] == (240, 240) and info["loop"] == 0 and len(frames) >= 2
    assert (directory / "result.gif").stat().st_size <= 500000
    assert all(set(frame.getchannel("A").getdata()).issubset({0, 255}) for frame in frames)
    assert all(frame.getchannel("A").getextrema() == (0, 255) for frame in frames)
    # Opening the sequence/contact PNGs was performed through view_image.
    notes = ["已打开切格、黑底拼图及动作序列复核，主体完整，动作可见，未见连续白边。",
             "橘色填充有轻微渐变，与严格扁平色要求存在偏差，visual 保守记为 false。"]
    if case["id"] == "wx-002":
        notes.append("与委屈 dHash 距离为5而触发相似 WARN，人工可辨大笑与哭泣，保留试跑样本。")
    if case["id"] == "wx-007":
        notes.append("白色气团轮廓开口导致内部被 key-white 去掉，黑底只剩深色线条，视觉缺陷保留。")
    if case["id"] == "wx-009":
        notes.append("六帧顺序正确，主体有微小漂移，机位为正面，首尾 dHash=0但像素不完全一致，未验证实时播放流畅度。")
    case["checks"] = {
        "technical": True, "visual": False, "approved": False,
        "black_background": True, "continuous_white_halo_seen": False,
        "notes": " ".join(notes),
    }
    save(path, case)
    records.append({"case": directory.name, "frames": len(frames),
                    "duration_ms": durations, "bytes": (directory / "result.gif").stat().st_size,
                    "max_white_edge_ratio": max(check_assets.white_edge_ratio(f) or 0 for f in frames)})
assert len(set(meanings)) == 9 and all(len(word) <= 4 for word in meanings)

for name, size in [("cover", (240, 240)), ("icon", (50, 50)), ("banner", (750, 400))]:
    im = Image.open(PACK / f"assets/{name}.png").convert("RGBA")
    assert im.size == size
    if name == "banner":
        assert im.getchannel("A").getextrema() == (255, 255)
    else:
        assert check_assets.corners_alpha(im) == [0, 0, 0, 0]

wave = gifkit.read_gif(PACK / "wx-009-wave/result.gif")[0]
first = Image.new("RGB", (240, 240), "black")
last = first.copy()
first.paste(wave[0], mask=wave[0].getchannel("A"))
last.paste(wave[-1], mask=wave[-1].getchannel("A"))
diff = ImageChops.difference(first, last)
seam = {"first_last_dhash": gifkit.hamming(gifkit.dhash(wave[0]), gifkit.dhash(wave[-1])),
        "first_last_rgb_mean_absolute_difference": sum(ImageStat.Stat(diff).mean) / 3,
        "pixel_identical": diff.getbbox() is None}
save(PACK / "_work/verification.json", {"cases": records, "wave_seam": seam,
                                       "all_assertions_passed": True})
print(json.dumps({"all_assertions_passed": True, "cases": len(cases), "wave_seam": seam,
                  "max_all_frames_white_edge_ratio": max(r["max_white_edge_ratio"] for r in records)},
                 ensure_ascii=False, indent=2))
