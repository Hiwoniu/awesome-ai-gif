"""Local trial orchestration. All writes stay inside this pack directory."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[3]
PACK = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/wechat-sticker/scripts"
sys.dont_write_bytecode = True
sys.path.insert(0, str(SCRIPTS))
import gifkit

COMMANDS = []


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def run(label, arguments):
    command = [sys.executable, *map(str, arguments)]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True)
    output = result.stdout + result.stderr
    (PACK / f"_work/logs/{label}.txt").write_text(output)
    COMMANDS.append({"label": label, "command": command, "exit_code": result.returncode,
                     "output": output})
    save_json(PACK / "_work/commands.json", COMMANDS)
    print(label, "exit", result.returncode, output, flush=True)
    return result


spec = json.loads((PACK / "_work/character-spec.json").read_text())
frames_prompt = f"""生成一张用于无缝循环 GIF 的单张动画序列图，用来做微信表情包。严格包含 6 个连续帧，按 3 列×2 行网格排列，从左到右、从上到下阅读，每个面板尺寸完全一致。
角色：{spec['role']}
动作：右前爪自然下垂作为起点 → 抬起右前爪 → 举爪向外挥 → 举爪向内挥 → 慢慢放下右前爪 → 回到右前爪自然下垂的起点。
固定前侧四分之三机位，六个格子里是同一个角色、同一套配色、同一个姿势起点。第 6 帧要平滑过渡回第 1 帧。
风格：{spec['style']}
背景：纯白。无字幕、无文字、无边框、无留白、无阴影。
"""
(PACK / "_work/prompts/frames.md").write_text(frames_prompt)
banner_prompt = f"""为一套原创卡通橘猫表情包画详情页横幅，横向构图，画幅比例 750:400。
角色：{spec['role']}
风格：{spec['style']}
参考图用于角色外观，保留白色肚皮、白色尾巴尖、右耳小缺口。画一只橘猫全身在画面中开心地伸展双爪，四周留足空间。
背景：浅青绿色纯色背景，整张图不透明，背景非纯白。无文字、无字幕、无标点、无水印、无边框、无阴影。
"""
(PACK / "_work/prompts/banner.md").write_text(banner_prompt)

run("slice-atlas", [SCRIPTS / "slice_sheet.py", PACK / "_work/atlas.png",
                    "--cols", 4, "--rows", 4, "--out", PACK / "_work/cells"])
run("slice-frames", [SCRIPTS / "slice_sheet.py", PACK / "_work/frames-sheet.png",
                     "--cols", 3, "--rows", 2, "--out", PACK / "_work/frames"])

selections = [
    (1, "greeting", "你好", "nod"),
    (3, "laugh", "哈哈", "bounce"),
    (4, "cry", "委屈", "sway"),
    (5, "stomp", "生气", "bounce"),
    (6, "heart", "爱你", "nod"),
    (10, "shy", "害羞", "sway"),
    (11, "shrug", "无奈", "sway"),
    (13, "eat", "开吃", "bounce"),
]
cases = []
for index, (cell, action, meaning, motion) in enumerate(selections, 1):
    directory = PACK / f"wx-{index:03}-{action}"
    directory.mkdir(exist_ok=True)
    shutil.copy2(PACK / "_work/atlas.png", directory / "sheet.png")
    shutil.copy2(PACK / "_work/prompts/atlas.md", directory / "prompt.md")
    result = run(f"gif-{index:03}", [SCRIPTS / "light_motion.py",
                 PACK / f"_work/cells/cell_{cell:02}.png", "--motion", motion,
                 "--key-white", "--out", directory / "result.gif"])
    case = {
        "id": f"wx-{index:03}", "title": action, "meaning": meaning,
        "route": "atlas", "motion": motion, "source_cell": cell,
        "engine": {"provider": "OpenAI", "tool": "image_gen.imagegen",
                   "model": "tool-managed-undisclosed", "channel": "Codex built-in"},
        "cost": {"generations": 0, "shared_generations": 1,
                 "shared_source": "_work/atlas.png", "usd": None,
                 "note": "八张共用一次图集生成，禁止逐张累加 shared_generations；另有一次共用角色定稿"},
        "checks": {"technical": result.returncode == 0, "visual": False,
                   "approved": False, "notes": "已打开切图验货，待黑底及序列拼图复核"},
        "status": "draft", "created": "2026-11-16",
    }
    save_json(directory / "case.json", case)
    cases.append(directory)

directory = PACK / "wx-009-wave"
directory.mkdir(exist_ok=True)
shutil.copy2(PACK / "_work/frames-sheet.png", directory / "sheet.png")
shutil.copy2(PACK / "_work/prompts/frames.md", directory / "prompt.md")
result = run("gif-009", [SCRIPTS / "make_gif.py", PACK / "_work/frames",
             "--key-white", "--out", directory / "result.gif"])
save_json(directory / "case.json", {
    "id": "wx-009", "title": "挥爪循环", "meaning": "挥爪", "route": "frames",
    "engine": {"provider": "OpenAI", "tool": "image_gen.imagegen",
               "model": "tool-managed-undisclosed", "channel": "Codex built-in"},
    "cost": {"generations": 1, "usd": None, "note": "参考图集第1格，另与全套共用一次角色定稿"},
    "checks": {"technical": result.returncode == 0, "visual": False,
               "approved": False, "notes": "六帧可见挥爪，机位偏正面，待序列拼图复核"},
    "status": "draft", "created": "2026-11-16",
})
cases.append(directory)

# Reuse the production white-key and binary-alpha routines for supporting assets.
character = gifkit.key_white(Image.open(PACK / "character.png").convert("RGBA"))
cover = gifkit.hard_alpha(gifkit.fit_frames([character], (240, 240))[0])
cover.save(PACK / "assets/cover.png", optimize=True)
# The face occupies this source rectangle. Keep the ear notch inside the crop.
head = character.crop((200, 70, 1040, 665))
icon = gifkit.hard_alpha(gifkit.fit_frames([head], (50, 50))[0], erode=0)
icon.save(PACK / "assets/icon.png", optimize=True)
banner = ImageOps.fit(Image.open(PACK / "_work/banner-original.png").convert("RGB"),
                      (750, 400), method=Image.Resampling.LANCZOS)
banner.save(PACK / "assets/banner.png", optimize=True)
save_json(PACK / "pack.json", {
    "character": "圆滚滚橘猫", "title": "橘团日常",
    "intro": "圆滚滚的橘猫，用挥爪、大笑、比心和小脾气，陪你聊聊每天的心情。",
    "copyright": "原创试作", "animated": True, "review_status": "未提交",
    "submitted": None, "generation_count": 4,
    "generation_breakdown": {"character": 1, "atlas": 1, "frames": 1, "banner": 1},
})

contact = Image.new("RGB", (720, 792), "black")
draw = ImageDraw.Draw(contact)
metrics = []
for index, directory in enumerate(cases):
    frames, durations, info = gifkit.read_gif(directory / "result.gif")
    x, y = index % 3 * 240, index // 3 * 264
    contact.paste(frames[0], (x, y + 24), frames[0].getchannel("A"))
    draw.text((x + 8, y + 5), directory.name, fill="white")
    sequence = Image.new("RGB", (240 * len(frames), 264), "#303030")
    sequence_draw = ImageDraw.Draw(sequence)
    for n, frame in enumerate(frames):
        sequence.paste(frame, (240 * n, 24), frame.getchannel("A"))
        sequence_draw.text((240 * n + 8, 6), f"{n+1} / {durations[n]} ms", fill="white")
    sequence.save(PACK / f"review/{directory.name}-sequence.png")
    hashes = [gifkit.dhash(frame) for frame in frames]
    metrics.append({"case": directory.name, "frames": len(frames),
                    "bytes": (directory / "result.gif").stat().st_size,
                    "durations": durations, "loop": info.get("loop"),
                    "white_edge_ratio": __import__('check_assets').white_edge_ratio(frames[0]),
                    "first_last_dhash": gifkit.hamming(hashes[0], hashes[-1]),
                    "movement_dhash": max(gifkit.hamming(hashes[0], h) for h in hashes)})
contact.save(PACK / "review/black-bg-contact.png")
save_json(PACK / "_work/gif-metrics.json", metrics)

frame_contact = Image.new("RGB", (1536, 1072), "#dddddd")
frame_draw = ImageDraw.Draw(frame_contact)
for n, path in enumerate(sorted((PACK / "_work/frames").glob("*.png"))):
    x, y = n % 3 * 512, n // 3 * 536
    frame_contact.paste(Image.open(path).convert("RGB"), (x, y + 24))
    frame_draw.text((x + 8, y + 6), path.stem, fill="black")
frame_contact.save(PACK / "review/frames-sliced.png")

run("check-standard", [SCRIPTS / "check_assets.py", PACK,
                       "--report", PACK / "_work/check-standard.json"])
run("check-final", [SCRIPTS / "check_assets.py", PACK, "--final",
                    "--report", PACK / "_work/check-final.json"])
