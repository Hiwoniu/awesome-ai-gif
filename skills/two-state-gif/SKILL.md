---
name: two-state-gif
description: 用一个原创角色做“两种状态来回切换”的动图：光栅变画卡（480×720，像实体光栅卡那样日常态和变身态竖条翻转切换，6 秒循环）和动态海报（720×960，同一张海报的“安静 / 登场”两态切换，字和画一起设计）。出双联图提示词、可调 Codex CLI 内置生图出图、切开对齐、合成体积可控的循环 GIF、可在底部加固定标题。当用户要做光栅卡、变画卡、翻转卡、变身前后对比动图、两态切换的动态海报或角色登场海报时使用。
---

# 两态切换动图（光栅变画卡 / 动态海报）

一张图里画出同一构图的 A、B 两态，脚本切开后做成“A 停留 → 竖条翻到 B → B 停留 → 翻回”的循环 GIF。

| 类型 | 规格 `--spec` | 尺寸 | 时长 | 适合 |
|---|---|---|---|---|
| 光栅变画卡 | `card` | 480×720 | 6 秒 | 角色日常 / 变身、白天 / 夜晚、换装前后 |
| 动态海报 | `poster` | 720×960 | 4 秒 | 角色登场海报，标题字和画面一起变 |

依赖只有 Python 3 和 Pillow。出图按这个顺序选：本机有已登录的 Codex CLI 就用 `scripts/codex_gen.py`；当前环境自带生图工具就直接用；都没有就把提示词交给用户去 ChatGPT 出图，再把图交回来。

## 开始前先确认

- 角色是**原创**的，或用户自家宠物。现有 IP、明星脸、真人肖像不做。
- A、B 两态各是什么。两态要**一眼能看出差别**（道具、表情、光色都变），但构图、机位、角色位置和大小必须一样，否则翻转时角色会跳。
- 海报要不要画字，字的准确内容是什么。字只让模型画短词（2–6 个字），长句后期加。

## 流程

1. **写提示词**：按 [references/prompts.md](references/prompts.md) 的公式，换掉角色、两态和文字。要有角色定稿图就带上当参考图。
2. **出图**：
   ```
   python3 scripts/codex_gen.py one --prompt prompt.md --image character.png --out diptych.png
   ```
3. **验货**（打开图看）：
   - 是不是左右两格、各自比例对（变画卡每格 2:3，海报每格 3:4）。模型常把格子画得更瘦长、底下留一大条空白。
   - 两格里角色的头、眼睛、身体轮廓是否对齐。差得多就重画，脚本没法帮你对齐。
   - 海报的字有没有错字、多字。
4. **合成**：
   ```
   python3 scripts/two_state.py --spec card --split diptych.png result.gif
   python3 scripts/two_state.py --spec poster --split diptych.png result.gif
   ```
   - 比例不对时脚本会报错。用 `--crop-y 0.19:0.69` 从每格里取一段高度（先看图估计角色从耳朵到脚的范围），或者重画。
   - 要标题：`--title 橘团 --subtitle "夜读 / 变身"`；底部要深色栏再加 `--footer 90`。
   - 两张分开出的图也行：`two_state.py --spec card a.png b.png result.gif`。
5. **看成品**：抽中间一帧看竖条翻转，再看体积。超过规格里的 `soft_max_bytes` 会提示，用 `--colors` 降一档（网点、细纹理的画面降到 48 色通常还看不出）。

## 参数

规格默认值在 `specs/card.json`、`specs/poster.json`，命令行的 `--width --height --seconds --fps --hold --slats --colors` 可以覆盖。`--hold` 是两端停留占整段的比例（默认 0.6），`--slats` 是竖条数。

## 来源

类型和规格参考 [gif-factory](https://github.com/WoYun520/gif-factory)（MIT）的光栅卡和动态海报说明，脚本自写。`codex_gen.py` 与微信表情包 Skill 里的是同一份，拷过来是为了本目录能单独用。加标题默认找同仓库微信 Skill 自带的得意黑，单独拷走时把字体放到本目录 `fonts/` 下或用 `--font` 指定。
