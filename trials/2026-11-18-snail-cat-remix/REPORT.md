# 蜗牛猫复刻试做（19 张）

日期：2026-11-18。主角：用户自家的黑白奶牛猫（照片 `_work/photo.jpg`，不入库）。动作来源：`~/Downloads/蜗牛-猫-表情包` 里 19 张网络梗图（橘猫照片 P 上人类眼睛和嘴唇），**仅练手，不可提交微信**；原图和由原图做的参考图不入库。

## 画风：用真猫照片，不用卡通定稿

原套是“真猫照片 + P 上去的真人五官”，笑点靠照片感。先按卡通定稿试了 3 张（留在 `_work/cartoon/`），味道不对，改成直接拿用户的猫照片当参考图 1，提示词要求真实照片风格、保留 P 图感。

## 出图（Codex image_gen，20 次）

- 每张单独出：`codex_gen.py one --prompt gen/<编号>/prompt.md --image photo.jpg --image gen/<编号>/ref.png --out gen/<编号>/new.png`，3 个并行，每张 90–290 秒。
- 照片风格第 1 张（01）先单独试，通过后跑其余 18 张；19 张全部一次通过，没有画出字幕。
- 背景照原图：抠图白底的出白底，室内照的出虚化室内，02 保留火焰背景。所以 GIF 不透明。
- 提示词生成脚本见 `_work/mkprompts.py` 的结果 `gen/*/prompt.md`。

## 合成（`_work/build.py`）

- 原图是静态的，机检要求动图。照片铺满画面，`light_motion.py`（透明画布上挪动）不适用，改为在原图里移动取景框：zoom（冲镜头）、shake（左右抖）、bounce（上下颠）、breathe（慢推），每张用哪种写在 case.json 的 `motion`。
- 加字：12 张原图有字的位置加了**自己写**的文案（不照抄原句），白字黑描边、40px、逐字出现，压在照片上（和原套一样，所以 caption.py 的“压在角色身上”WARN 是预期的）。

## 结果

19 张 GIF，164–335KB；`check_assets.py`：0 FAIL，WARN 只剩专辑文案、封面、图标、横幅（练手不做）。总览 `preview.png`。

## 待人工确认

- 10「啥？」、19「哦～」的字压到了嘴边一点。
- 照片风格下嘴边的小白块有几张没画出来（05、10、18）。

## 写进 Skill

这次的做法已收进 Skill（SKILL.md“复刻：一套静态照片梗图换主角”）：`codex_gen.py each` 逐张出图，`photo_motion.py` 做取景框轻动效（和 `_work/build.py` 出的 GIF 逐字节一致），`references/prompts.md` 新增“照片梗图换主角”提示词。
