from pathlib import Path
import json
import shlex
import sys

PACK = Path(__file__).resolve().parents[1]
commands = json.loads((PACK / "_work/commands.json").read_text())
metrics = json.loads((PACK / "_work/gif-metrics.json").read_text())
image_metrics = json.loads((PACK / "_work/image-metrics.json").read_text())
verification = json.loads((PACK / "_work/verification.json").read_text())
generation_dir = "/Users/xiangming/.codex/generated_images/01a1e57f-2cd2-7631-b462-e16700a33c98"
generations = [
    ("character", "call_69efdf1816b14f7fae065f0bcbeca7d8.png", "character.png", None),
    ("atlas", "call_4b44dcc646d4400eae0809024a27a37b.png", "_work/atlas.png", "character.png"),
    ("frames", "call_0bed354d342b40f1954a20a562c59f19.png", "_work/frames-sheet.png", "_work/cells/cell_01.png"),
    ("banner", "call_a891a90f45c44f1a8d8d8eb44e39dcce.png", "_work/banner-original.png", "character.png"),
]
generation_records = []
for name, source, dest, reference in generations:
    generation_records.append({
        "tool": "image_gen.imagegen", "prompt": (PACK / f"_work/prompts/{name}.md").read_text().strip(),
        "referenced_image_paths": [str(PACK / reference)] if reference else None,
        "num_last_images_to_include": None, "transparent_background": False,
        "source": f"{generation_dir}/{source}", "copied_to": str(PACK / dest),
        "success": True,
    })
(PACK / "_work/generations.json").write_text(json.dumps(generation_records, ensure_ascii=False, indent=2) + "\n")

text = """# 橘团日常流程试跑报告

试跑日期为 2026-11-16。工作目录为 `/Users/xiangming/me-code/awesome-ai-gif`。目标套目录为 `trials/2026-11-16-codex-orange-cat/`。

已完整跑到普通机检和 `--final`。成品共 9 张，其中 atlas 8 张、frames 1 张。两次机检都是 **0 FAIL · 3 WARN · 13 OK**，退出码均为 0。全部案例保留 `status=draft`，`checks.technical=true`、`checks.visual=false`、`checks.approved=false`。视觉复核已执行，严格扁平色偏差、漏抠气团和六帧机位问题仍保留供本次流程评估。

所有手动创建和脚本输出均位于本套目录。内置出图工具按其默认行为先写入 `.codex/generated_images/`，随后逐张复制进本套目录，这是工具管理的初始输出位置。没有修改 `skills/`、`prompts/`、`docs/`、`cases/`，没有 pip install，没有使用 rembg。Python 调用全部使用指定解释器，并设置 `PYTHONDONTWRITEBYTECODE=1`，避免导入仓库脚本时在 skills 下生成缓存。

## 1. 读取、约定和实际执行记录

完整读取三份要求文件的命令如下，成功，退出码 0。

```sh
cat skills/wechat-sticker/SKILL.md skills/wechat-sticker/references/prompts.md skills/wechat-sticker/references/wechat-specs.md
```

另外读取 imagegen 技能、五个脚本、规格 JSON 和仓库 case/pack 模板。初次 `rg --files` 同时查找不存在的 `.agents`、`.codex` 路径，退出码 2，已成功列出技能文件；后续直接读取成功。未发现适用于本仓库的 AGENTS.md。初始 `git status --short` 已有 README、.gitignore、仓库规划以及若干未跟踪目录，本次未处理这些已有工作。

```sh
cat /Users/xiangming/.codex/skills/.system/imagegen/SKILL.md
cat skills/wechat-sticker/scripts/{slice_sheet.py,light_motion.py,make_gif.py,gifkit.py,check_assets.py} skills/wechat-sticker/specs/wechat.json
cat cases/_template/case/case.json cases/_template/pack.json .gitignore
git status --short
```

环境检查通过，Python 3.12.16，Pillow 13.0.0。所有成品使用默认 240×240、白底容差 12、透明阈值 128、主体内收 1 像素。轻动效默认 8 帧、100ms，六帧 GIF 默认 6 帧、120ms，未触发减色或减帧。

角色与风格冻结记录如下，三条生产路线以及横幅均复用原句。模板示例的“左耳”按用户角色改为“右耳”，以角色自身右侧为准，正面图对应画面左侧。特征件固定为白色肚皮、白色尾尖、右耳小缺口。

```text
角色：一只圆滚滚的橘猫，短腿，白色肚皮，尾巴尖是白色，右耳有一个小缺口
风格：简笔画卡通，线条粗细一致，颜色扁平，不超过 5 种主色
```

六帧模板中固定风格句与“逐字相同”要求冲突，本次采用冻结的风格句。六帧动作自主选择挥爪。封面用角色定稿全身，图标裁定稿头部，横幅采用浅青绿色背景。专辑名称自主填写“橘团日常”，版权填“原创试作”作为试跑字段，版权主体需用户提交前自行确定。

### 内置出图和复制

共调用内置 `image_gen.imagegen` **4 次**，全部成功，重画 0 次，剩余额度 1 次。未使用 API 或 CLI 出图。工具未提供模型版本和账单金额，case.json 的模型标为 `tool-managed-undisclosed`，金额为 null，未套用模板中的具体模型名。

每次完整提示词在 `_work/prompts/`，完整调用参数和原始输出路径在 `_work/generations.json`。每个 atlas 案例的 prompt.md 都是实际同一次图集提示词原文，sheet.png 是完整图集副本。第 9 张记录六帧提示词及原图。共享图集次数只按一次计，不能逐案例相加。

"""
for number, (name, source, dest, reference) in enumerate(generations, 1):
    text += f"{number}. `{name}`，参数 `transparent_background=false`、`num_last_images_to_include=null`，参考图为 `{reference or '无'}`，提示词为 `_work/prompts/{name}.md`。成功后执行复制。\n\n```sh\ncp {generation_dir}/{source} trials/2026-11-16-codex-orange-cat/{dest}\n```\n\n"

text += """### 切图、合成与机检

先独立执行了两次切图并打开图像验货，随后 `_work/run_trial.py` 再执行相同切图以生成可追溯日志。重复切图的内容一致。以下为实际调用命令及 stdout/stderr，全部退出码 0。该封装脚本仅存在于本套目录，复用原脚本，不修改生产脚本。

```sh
PYTHONDONTWRITEBYTECODE=1 /private/tmp/claude-501/-Users-xiangming--claude-spares-spare-Jq5Iet/4f11ea30-083f-4294-895a-1b47bf73dfaf/scratchpad/venv/bin/python trials/2026-11-16-codex-orange-cat/_work/run_trial.py
```

以下每条 Python 命令执行时都继承 `PYTHONDONTWRITEBYTECODE=1`。

"""
for c in commands:
    text += f"#### {c['label']}\n\n```sh\n{shlex.join(c['command'])}\n```\n\n退出码 {c['exit_code']}，成功。原始输出如下。\n\n```text\n{c['output'].rstrip()}\n```\n\n"

text += """### 配套素材和复核命令

配套素材加工实际由 `_work/run_trial.py` 执行。封面使用 `gifkit.key_white(character)` → `fit_frames((240,240))` → `hard_alpha()`。图标从定稿坐标 `(200,70,1040,665)` 裁头部，缩到 50×50，采用 `hard_alpha(erode=0)`，避免 50px 细线被再次蚀掉。图标仍为二值透明。横幅将 1717×916 的原图转 RGB，用 `ImageOps.fit(...,(750,400),LANCZOS)` 微量居中裁切，没有主体裁断。成品均保存为 PNG。

`review/black-bg-contact.png` 由 Pillow 将各 result.gif 的第 1 帧解码为 RGBA，再用 alpha 贴到 RGB 纯黑画布，排列成 3×3。每格 240×240，顶部加 24px 文件名，成图 720×792。文件名只出现在复核图中。另导出每张所有帧的灰底序列和分组动作拼图，便于检查后续帧轮廓。

还执行了套内辅助 Python 检查命令，成功，退出码 0。

```sh
PYTHONDONTWRITEBYTECODE=1 /private/tmp/claude-501/-Users-xiangming--claude-spares-spare-Jq5Iet/4f11ea30-083f-4294-895a-1b47bf73dfaf/scratchpad/venv/bin/python trials/2026-11-16-codex-orange-cat/_work/verify_trial.py
```

结果为 9 个案例字段/文件齐全、含义词唯一且各为 2 字、全部 GIF 尺寸/透明/循环/字节上限断言通过。辅助脚本首次运行收到 Pillow 13 的 `getdata` 弃用提示，检查仍成功，这条提示来自本次套内辅助脚本。详细数值见 `_work/verification.json`。

实际 `view_image` 打开记录包含以下文件，均成功。

- `review/atlas-row-1.png` 至 `review/atlas-row-4.png`，由实际切出的 cell PNG 拼接，完整覆盖 16 格。
- `_work/frames/frame_01.png` 和 `review/frames-sliced.png`，覆盖切出的全部六帧。
- `review/black-bg-contact.png`，覆盖九张 GIF 的首帧。
- `review/wx-009-wave-sequence.png` 和 `review/motions-1.png`、`review/motions-2.png`，复核六帧和全部轻动效的代表帧。
- `review/assets-preview.png`，复核封面、实际 50px 图标和成品横幅。
- `review/shrug-cloud-source.png`，局部放大确认白气团轮廓存在开口。

原始四张生成图也已在图像工具输出中实际观察。所有检查和日志均留存在套内。

## 2. 每张出图验货

### 定稿图

1254×1254，单图，无格子。全身完整，无文字、边框、道具和落地阴影。白肚皮、白尾尖、右耳缺口均保留。正面四肢可辨，但手臂仍贴近躯干。橘色、粉色及背景存在轻微渐变和颗粒，未完全达到严格扁平色。肉眼接近白底，边缘采样最暗通道 253，最亮 255，严格纯白像素只占边缘约 5.11%，因此不能记为严格纯白。默认 key-white 能去底。

### 4×4 图集

1254×1254，共 16 格、顺序正确，无显式格线，四列四行逻辑等大。切图得到 16 张 313×313，脚本舍去最右和最下各 2px 空白边，未裁到主体。未使用 inset。各格主体大小和脚底位置有轻微变化，第 14 格趴姿显著更矮。整体配色延续定稿，但保留了渐变，第 4 格泪水新增蓝色。第 7 格有 Zz，第 14 格有省略号。二者均未入选。图集背景边缘范围 252–255，严格白色比例约 11.23%，非严格纯白。

| 格子 | 动作与特征件验货 | 文字或符号 | 使用决定 |
|---|---|---|---|
| 01 | 挥手，三特征保留，全身完整 | 黄色动势线，无文字 | wx-001，nod |
| 02 | 低头闭眼，三特征保留，侧倾可见 | 弧形动势线 | 未选 |
| 03 | 仰头大笑，三特征保留，姿势与哭格的躯干相近 | 黄色动势线 | wx-002，bounce |
| 04 | 举爪哭泣，三特征保留，蓝泪明确 | 无文字 | wx-003，sway |
| 05 | 抬腿跺脚，三特征保留 | 怒气图形与动势线 | wx-004，bounce |
| 06 | 双爪捧心，三特征保留 | 心形道具 | wx-005，nod |
| 07 | 捂嘴打哈欠，三特征保留 | Zz 字母，违反无文字 | 排除 |
| 08 | 惊讶双爪抬起，三特征保留 | 闪电图形 | 未选 |
| 09 | 合爪鼓掌，三特征保留 | 黄色动势线 | 未选 |
| 10 | 捂脸，白肚皮及尾尖保留，右耳缺口仍可见 | 腮红线 | wx-006，sway |
| 11 | 摊手叹气，三特征保留 | 白色气团开口，去白后内部透明 | wx-007，sway，视觉缺陷留档 |
| 12 | 握拳抬爪，三特征保留 | 黄色动势线 | 未选 |
| 13 | 双爪拿饼干，三特征保留 | 饼干道具，无文字 | wx-008，bounce |
| 14 | 趴姿，耳缺口和白尾尖保留，肚皮被姿势遮挡 | 三点省略号 | 未选 |
| 15 | 张开双臂抱抱，三特征保留 | 粉色动势线 | 未选 |
| 16 | 背对挥手，白尾尖可见，肚皮不可见，右耳缺口无法按正面标准确认 | 弧形动势线 | 未选 |

16 格并非相同站姿只换文字，但大多数沿用直立躯干，动作差异主要在脸、双爪和道具。选中 8 格均无字母和字幕，右耳缺口、白肚皮和白尾尖可辨。

### 六帧序列图

1536×1024，严格 3×2，切出六张 512×512，无丢边，无缺帧、越格或主体裁断。三特征在六帧都保留，无文字，无格线。画面有黄色动势线。动作顺序是垂爪 → 抬爪 → 举爪 → 横挥 → 降爪 → 垂爪，第三、四帧轮廓位置变化清楚。背景边缘 253–255，严格白色比例约 10.95%，非严格纯白。

实际机位为正面，偏离“固定前侧四分之三”。各帧猫耳、脸和脚底有数像素级漂移。第 6 帧能回到相近的垂爪起点，首尾 dHash 为 0，但 RGB 平均绝对差为 2.6482/255，像素不完全相同。可确认姿势闭环，实时循环的流畅程度仍需播放复核。

### 横幅原图

1717×916，与要求的 750∶400 比例很接近。只有一只全身猫，三特征保留，没有文字或水印，背景为浅青绿色且不透明。背景和角色有轻微渐变，纯色指令执行不严格。原图尺寸由工具决定，按规范缩放裁切为 750×400 成品，约 248KB。成品已打开验货，猫未被裁断。

## 3. 成品数值与机检

| 案例 | 含义词 | 路线及动效 | 帧数 | 每帧毫秒 | 字节数 |
|---|---|---|---|---|---|
"""
for m in metrics:
    case = json.loads((PACK / m['case'] / "case.json").read_text())
    text += f"| {m['case']} | {case['meaning']} | {case['route']} {case.get('motion','挥爪')} | {m['frames']} | {m['durations'][0]} | {m['bytes']} |\n"

text += """
封面为透明 240×240 PNG，机检约 51KB。图标为透明 50×50 PNG，约 4KB。横幅为不透明 RGB 750×400 PNG，约 248KB。精确字节数可直接读取文件。九张 GIF 均有实际透明区域，解码后 alpha 值只有 0 和 255，`loop=0`。

### 最终 FAIL / WARN 原样列表

FAIL 列表为空。以下三条是最终 `--final` 输出中的全部 WARN，逐字保留。

```text
"""
final_log = (PACK / "_work/logs/check-final.txt").read_text()
text += "\n".join(line for line in final_log.splitlines() if line.startswith(("[WARN]", "[FAIL]")))
text += "\n```\n\n最终完整输出如下，普通模式完整输出已在执行记录和 `_work/logs/check-standard.txt` 保留。\n\n```text\n" + final_log.rstrip() + "\n```\n\n"

text += """### WARN 人工判定

- `review` 缺 result.gif 和 meaning 两条是目录发现逻辑造成的误报。用户要求的 review 目录存放验货图，原脚本遍历除 assets、下划线和点目录以外的一切目录。保留 review 以满足交付路径，不伪造案例字段，不调整脚本。
- 大笑和委屈的首帧 dHash 距离为 5，低于或等于阈值 6。已并排查看，笑脸、哭嘴、双爪位置和蓝色眼泪明确不同，但两者都是直立躯干，轮廓相似仍是事实。本次保留差异警告，供流程评估和用户后续取舍。

没有 FAIL，因此未执行 FAIL 修复和重合成。全部 WARN 已实际核图判断。

## 4. 黑底白边自查

已打开 `review/black-bg-contact.png`。九张首帧主体周围均未见连续白色光圈，肚皮、爪尖和尾尖的内部白色得到保留。轮廓有锯齿、细微深棕杂色和少量孤立亮点，属于当前缩放、二值透明和内收处理下的可见边缘质量问题。没有把“未触发白边 WARN”直接当作视觉通过。

白边算法的首帧近白轮廓占比为 0–0.4264%。另遍历所有解码帧得到的最大值仍为 0.4264%，远低于脚本 50% 的告警线。局部白边和一两像素亮点仍可能被该阈值忽略。

无奈的白色气团源图有明确开口，背景白色与气团内部连通，key-white 去底后整个内部透明，黑底只剩深棕轮廓。已打开 `review/shrug-cloud-source.png` 放大确认。该现象符合连通去白算法，但会破坏这类道具的原有表现，需要源图闭合轮廓或换格。此次作为真实试跑缺陷保留，未重画。

## 5. 流程发现的问题和建议

| 编号 | 现象及证据 | 建议 |
|---|---|---|
| 1 | 实际复现，check_assets.py 第 197–198 行把 review 识别为案例，产生两条误报 | 用案例清单、wx-* 命名或 case.json/result.gif 存在条件筛选，明确支持 review/cells/frames 等辅助目录 |
| 2 | 实际复现，atlas 1254 无法整除 4，slice_sheet 提示“丢 2×2 像素”容易误读为仅丢四个像素 | 明确提示右侧丢 2 列、底部丢 2 行；要求生成边长可整除或定义分界坐标及补边策略；本次只丢空白边 |
| 3 | 实际复现，要求“无文字”仍生成 Zz；省略号、怒气符号和动作线也自动出现 | 补充禁止字母、数字、标点、拟声字，并写出打哈欠只用捂嘴和眼睛表达；对符号是否接受给出明确口径 |
| 4 | 实际复现，所有生成图颜色有渐变，白底也有 252–255 的轻微纹理 | 对严格纯色、无纹理、无渐变作正向约束，验货时增加背景和色块采样，保持默认近白容差能处理这一类轻微背景偏差 |
| 5 | 实际复现，序列图机位为正面，提示要求四分之三；参考图是正面挥手 | 增加独立机位参考或先定稿四分之三视图，提示注明参考外观但按固定相机角度重画 |
| 6 | 文档冲突，prompts.md 要三段风格描述逐字一致，但六帧模板固定句不同；无留白与等格全身安全边距也缺少解释 | 六帧风格统一用冻结字段，区分面板之间的空白与角色四周的安全边距 |
| 7 | 实际复现，无奈气团有开口而漏抠；白肚皮本次封闭所以保留 | 提示要求白色部件轮廓完全闭合，验货覆盖白色小道具；文档明确连通去白保护成立的条件，必要时在套内换格 |
| 8 | 实际复现，similar_distance=6 对大笑/哭泣触发 WARN，距离为5 | 保留 WARN 的人工复核定位，增加脸部局部特征、颜色或多代表帧比较，先收集误报样本再调阈值，单套不足以确定新阈值 |
| 9 | 实际复现，六帧首尾 dHash=0而像素差不为零；机检目前没有接缝检测 | 增加全帧对齐、主体锚点偏移和首尾差异的提示，要求实际循环播放自查，避免只靠低分辨率哈希判断无缝 |
| 10 | 实际观察，白边 50% 阈值只在首帧检查，本次局部亮点和锯齿均未告警 | 遍历全帧，补充连通白边长度或局部区域比例。50% 对严重整圈白边较明确，对局部缺陷偏宽，不能从本次样本直接推导替代数值 |
| 11 | 静态代码观察，check_sticker 第 71–73 行缺 GIF 始终 WARN，copy 缺字段始终 WARN；final 仅提升数量和配套缺失等级 | 如果目标是完整交付，final 可要求已声明案例有 GIF、meaning 和专辑字段；本次材料齐全，未构造缺失样本来复现 |
| 12 | 静态代码观察，机检没有检测文字、单色填充、角色特征件、版权归属、视觉认可，透明素材主要检查四角 | 文档列清自动检查覆盖范围，配人工复核清单，避免把 exit 0 解释为可直接提交；本次技术通过同时保留 visual=false |
| 13 | 模板 engine 示例使用具体模型名，内置工具实际未返回模型版本或费用；共享图集成本没有统一口径 | 模型未知时明确填 null/unknown 或工具管理，共享源图成本按 pack 汇总，给 case 字段定义 schema |
| 14 | 实际观察，16 格多数直立，姿势“同样大小”与趴姿自然冲突，背面也无法核对腹部 | 将特征可见性按机位与遮挡记录，要求至少若干明显轮廓变化，明确同尺寸取景不等于相同主体高度 |
| 15 | 实际执行，封面、图标、横幅制作没有专用 CLI，需要临时写 Pillow 编排 | 文档补充复用 key_white/fit_frames 的示例以及图标裁切和小尺寸内收参数，并给出统一产物/日志目录 |

以上建议均只记录在本报告，未应用到生产脚本或技能文档。默认 still_distance=1 下九张动作最大距离为 4–21，均未触发静止 WARN，拼图可见位移。该阈值能识别本次动作，仍无法保证动作自然。500000 字节上限按规格原值执行，本次所有 GIF 在第一轮 255 色即合格，压缩降级逻辑未被触发。

## 6. 本次未做或未验证

- 没有提交平台、注册、查询当前官方页面、验证真实审核结果或专辑名称是否重名。规格沿用技能附带的 2026-08-26 第三方归档，提交前需以 sticker.weixin.qq.com 当页复核。被拒后的重提流程也没有验证。
- 没有微信客户端、真机或浏览器 GIF 播放验证。已检查解码顺序、时长、首尾帧和静态序列，实时视觉流畅度仍待播放评估。
- 没有用户认可，所有案例保持 draft，视觉字段因上述偏差设 false。版权字段“原创试作”未代表已确认的法律主体；没有做 IP 近似检索。
- 没有使用第 5 次生成机会，没有坏格局部重绘，也没有去修非 FAIL 的图像偏差。第 7 格字母等坏格已避开，保留原图作为试跑证据。
- 没有触发超 500KB 后的减色/减帧路径，没有测试复杂背景、rembg、并发、损坏图像和错误参数；未安装任何依赖。
- 没有制作可选 120×120 缩略图、艺术家主页横幅、头像或赞赏素材，这些不在本次四类交付中，也不在现有机检覆盖范围内。
- 没有对阈值做多套样本统计，没有把代码阅读发现当成本次已实测的错误。

## 7. 证据位置

- `character.png` 为定稿，`pack.json` 为专辑字段，`assets/` 为三项配套。
- 九个 `wx-00N-*/` 均包含 case.json、prompt.md、sheet.png、result.gif。
- `_work/commands.json` 保存实际 Python 子命令、退出码和输出，`_work/logs/` 为逐步原始日志。
- `_work/generations.json` 和 `_work/prompts/` 保存四次出图调用与提示词。
- `_work/cells/`、`_work/frames/` 为原脚本实际切图，`review/` 为已打开的视觉复核产物。
- `_work/run_trial.py`、`_work/verify_trial.py`、`_work/write_report.py` 为本套专用编排、断言和报告生成源码。

报告生成命令如下，退出码 0。

```sh
PYTHONDONTWRITEBYTECODE=1 /private/tmp/claude-501/-Users-xiangming--claude-spares-spare-Jq5Iet/4f11ea30-083f-4294-895a-1b47bf73dfaf/scratchpad/venv/bin/python trials/2026-11-16-codex-orange-cat/_work/write_report.py
```

更新 case.json 的复核字段后，又实际运行以下 final 复检命令，退出码 0，输出与上面最终完整输出一致。

```sh
PYTHONDONTWRITEBYTECODE=1 /private/tmp/claude-501/-Users-xiangming--claude-spares-spare-Jq5Iet/4f11ea30-083f-4294-895a-1b47bf73dfaf/scratchpad/venv/bin/python skills/wechat-sticker/scripts/check_assets.py trials/2026-11-16-codex-orange-cat --final --report trials/2026-11-16-codex-orange-cat/_work/check-final.json
```

最后逐案例读取字段并核对四项文件，9 个案例全部齐全；套内资产精确字节数为 cover.png 51417、icon.png 3667、banner.png 248113。
"""
(PACK / "REPORT.md").write_text(text)
print("Wrote", PACK / "REPORT.md")
