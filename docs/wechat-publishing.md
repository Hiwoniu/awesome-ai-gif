# 微信表情包上架指南

从一个角色到提交审核的完整步骤。规格表见 [wechat-specs.md](../skills/wechat-sticker/references/wechat-specs.md)。

> 状态：初稿，按调研资料整理，我们自己还没有走完一次提交。走完第一套后按实际情况修订。

## 准备

- 微信表情开放平台账号：[sticker.weixin.qq.com](https://sticker.weixin.qq.com)，电脑端操作。个人注册需要大陆居民身份证和已绑银行卡的微信。
- Python 3 和 Pillow：

```bash
pip install pillow
```

## 步骤

### 1. 定角色

按 [角色定稿公式](../prompts/character-sheet.md) 出一张定稿图。只用原创角色。在 `cases/wechat-stickers/` 下建角色目录，拷入 [模板](../cases/_template/)，把角色和风格描述写进 `pack.md`。

### 2. 出整套姿势

按 [4×4 图集公式](../prompts/atlas-4x4.md) 一次出 16 个姿势。逐格验货，不合格的格子局部重绘。

### 3. 切图并加轻动效

```bash
python3 skills/wechat-sticker/scripts/slice_sheet.py atlas.png --cols 4 --rows 4 --out cells/
```

```bash
python3 skills/wechat-sticker/scripts/light_motion.py cells/cell_01.png --motion nod --key-white --out cases/wechat-stickers/<角色>/wx-001-<动作>/result.gif
```

### 4. 挑几张升级成真动作（可选）

拿图集里那一格当参考图，按 [六帧公式](../prompts/sprite-sheet-6-frame.md) 出图，然后：

```bash
python3 skills/wechat-sticker/scripts/slice_sheet.py sheet.png --cols 3 --rows 2 --out frames/
```

```bash
python3 skills/wechat-sticker/scripts/make_gif.py frames/ --key-white --out result.gif
```

### 5. 填元数据

每个案例的 `case.json` 填含义词（≤4 个字，同套不重复）、路线、型号、出图次数；`prompt.md` 贴提示词原文和验货记录。`pack.json` 填专辑名称（≤8 字）、介绍（≤80 字）、版权信息（≤10 字）。

### 6. 做配套素材

放进角色目录的 `assets/`：

- `cover.png`：240×240，透明底，正面半身或全身。
- `icon.png`：50×50，透明底，头部正面。
- `banner.png`：750×400，不透明、非纯白、无文字。

```bash
python3 skills/wechat-sticker/scripts/make_assets.py cover character.png --key-white --out assets/cover.png
python3 skills/wechat-sticker/scripts/make_assets.py icon character.png --key-white --out assets/icon.png
python3 skills/wechat-sticker/scripts/make_assets.py banner banner-raw.png --out assets/banner.png
```

横幅的源图要单独出一张有底色、无文字的横图；图标默认取主体上半部，没裁对用 `--head-ratio` 或 `--crop` 调。

### 7. 机检

```bash
python3 skills/wechat-sticker/scripts/check_assets.py cases/wechat-stickers/<角色> --final
```

FAIL 必须清零。WARN 逐条打开图看。再把每张表情放到纯黑底上看一遍白边。

### 8. 先自用

在家人群或朋友群当贴纸发 1–2 天，确认别人看得懂每张的情绪。

### 9. 提交

按平台表单上传。超规格的素材平台不会报错，会直接静默压缩裁剪，所以第 7 步不能省。提交后把日期和状态记进 `pack.json` 和 `pack.md`。

### 10. 被拒了

在**原专辑**上编辑重提，不要新建一套。把拒因和改法记进 `pack.md`，并补到 [被拒原因](rejections.md)。

## 更新索引

```bash
python3 tools/build_index.py
```
