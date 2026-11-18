# 白兔换角复刻实测

试验日期为 2026-11-17。输入为用户声明拥有复刻权的原创橘猫套，共九张 GIF。输出目录为 `trials/2026-11-17-remix-rabbit/`。

已完成角色定稿、原套拆解、两张参考图换角、一次姿势修订、九张 GIF 合成、文案与配套素材、提交前机检及黑底静态对照。实际出图 **4 次**，用满预算。目录自动扫描成功，无需逐个传入 GIF，也没有强制改分类。

**机检为 1 FAIL、1 WARN、12 OK。九张 GIF 的规格检查均为 OK。** FAIL 是按任务要求保留的白底横幅。视觉自查仍有画风和挥爪嘴型偏差。实时播放检查因环境权限受阻，未完成，不能据逐帧检查宣称已验证实际播放流畅度。全部案例的 `approved` 保持 false。

## 固定角色与风格

角色描述全文如下，定稿和首次两张换角图提示词逐字一致。

> 一只圆滚滚的白色小兔子，长耳朵内侧是粉色，左耳尖有一个深灰色小斑点，短尾巴像一团棉花

风格描述全文如下。

> 简笔画卡通，线条粗细一致，颜色扁平，不超过 5 种主色

检查特征为粉色长耳、角色自身左耳尖深灰斑点（正面图的画面右侧）和棉花团短尾。三者在定稿、八个姿势和六个挥爪关键帧中均可辨认。

## 执行命令与结果

所有 Python 调用均使用下列解释器，并设置 `PYTHONDONTWRITEBYTECODE=1`。没有安装依赖。

```bash
PY=/private/tmp/claude-501/-Users-xiangming--claude-spares-spare-Jq5Iet/4f11ea30-083f-4294-895a-1b47bf73dfaf/scratchpad/venv/bin/python
OUT=trials/2026-11-17-remix-rabbit
SRC=trials/2026-11-16-codex-orange-cat
SCRIPTS=skills/wechat-sticker/scripts
```

下列命令用这四个变量简写实际执行的完整路径。运行日志位于 `logs/`。

### 1. 阅读与角色定稿

阅读了 `skills/wechat-sticker/SKILL.md` 全文，重点执行“复刻：一套 GIF 换个角色”。阅读了 `references/prompts.md` 的角色定稿公式，以及拆解、合成、配套素材、机检和共用去白底脚本。另阅读 `imagegen` 技能，使用内置出图工具。

第 1 次调用 `image_gen.imagegen`，提示词原文已存 `character-prompt.md`，`transparent_background=false`。图像生成工具返回后将图片复制为 `character.png`。

```bash
cp /Users/xiangming/.codex/generated_images/01a1e813-894a-7c82-bd6e-35eef0134cca/call_0RTtPT2OTdT92A72Y1DlMTbB.png "$OUT/character.png"
```

定稿全身入画、闭合深色外轮廓、无文字。粉色耳内和腮红有轻微明暗变化，未完全满足纯扁平色要求。

### 2. 自动拆原套

```bash
PYTHONDONTWRITEBYTECODE=1 "$PY" "$SCRIPTS/remix_extract.py" "$SRC" \
  --out "$OUT/_work" \
  --character '一只圆滚滚的白色小兔子，长耳朵内侧是粉色，左耳尖有一个深灰色小斑点，短尾巴像一团棉花' \
  --style '简笔画卡通，线条粗细一致，颜色扁平，不超过 5 种主色'
```

退出码 0，完整标准输出为 `logs/extract.txt`。生成 `plan.json`、`poses/ref.png`、`wx-009-wave/ref.png` 及对应的 `prompt.md`。脚本打印需出图 2 次，该数仅包含换角素材，不包含角色定稿和修订。

| 案例 | 分类 | 原帧数 | 拟合动作 | 幅度 | 拟合分数 | 参考位置 |
|---|---|---|---|---|---|---|
| 001 greeting | still | 8 | nod | 1.0 | 0.962600 | poses 第 1 格 |
| 002 laugh | still | 8 | bounce | 1.0 | 0.968901 | poses 第 2 格 |
| 003 cry | still | 8 | sway | 1.0 | 0.979962 | poses 第 3 格 |
| 004 stomp | still | 8 | bounce | 1.0 | 0.986968 | poses 第 4 格 |
| 005 heart | still | 8 | nod | 1.0 | 0.979959 | poses 第 5 格 |
| 006 shy | still | 8 | sway | 1.0 | 0.985722 | poses 第 6 格 |
| 007 shrug | still | 8 | sway | 1.0 | 0.967347 | poses 第 7 格 |
| 008 eat | still | 8 | bounce | 1.0 | 0.971552 | poses 第 8 格 |
| 009 wave | frames | 6 | 原 0–5 帧全选 | — | — | 3 列×2 行 |

001–008 的分类与原套 case.json 中的轻动效类型完全相符。009 保留六帧，分类正确。目录扫描、命名和合成均未发现此次输入可复现的脚本错误。

### 3. 按 prompt.md 换角

第 2 次出图使用 `_work/poses/prompt.md` 原文。参考图 1 为 `character.png`，参考图 2 为 `_work/poses/ref.png`。第 3 次出图使用 `_work/wx-009-wave/prompt.md` 原文。参考图 1 同上，参考图 2 为 `_work/wx-009-wave/ref.png`。两次均为白底输出。

```bash
cp /Users/xiangming/.codex/generated_images/01a1e813-894a-7c82-bd6e-35eef0134cca/call_1MO8cUygTzwvFcwZM3PqvuLj.png "$OUT/_work/poses/new.png"
cp /Users/xiangming/.codex/generated_images/01a1e813-894a-7c82-bd6e-35eef0134cca/call_Oqy3m9a4azx7YEvUzQ1Jn4M0.png "$OUT/_work/wx-009-wave/new.png"
```

实际打开原参考图，并查看生成结果。首版姿势图为 3×3 网格，前八格有角色，末格留空，顺序正确。第 4 格未抬脚，第 7 格气团有开口，因此使用唯一剩余调用修订这两格。第 4 次调用的两个参考图依次为首版兔子姿势图和原橘猫姿势参考，完整提示词保存在 `_work/poses/repair-prompt.md`。

```bash
cp "$OUT/_work/poses/new.png" "$OUT/_work/poses/new-before-repair.png"
cp /Users/xiangming/.codex/generated_images/01a1e813-894a-7c82-bd6e-35eef0134cca/call_tNNlXcFdBbz20E2H5a9Pl9e6.png "$OUT/_work/poses/new.png"
```

修订后第 4 格抬脚可辨，气团闭合，第 7 格白气团闭合。返回的是整张新图，其他格也有轻微线形和位置变化，因此重新检查了全部八格。

图像工具自动在其管理的 `~/.codex/generated_images/` 缓存图片，这是工具固定行为。所有项目内复制、脚本输出、辅助检查与报告均只写入本试验目录。没有改动用户禁止修改的原套、技能、提示词、文档或案例目录。

### 4. 合成

```bash
PYTHONDONTWRITEBYTECODE=1 "$PY" "$SCRIPTS/remix_build.py" "$OUT/_work" \
  --out "$OUT" --key-white
```

退出码 0，合成 9 张、跳过 0 张、失败 0 张。原始输出为 `logs/build.txt`。九张均为 240×240、透明、无限循环 GIF。

### 5. meaning、专辑与配套素材

使用指定 Python 读取原套各自的 case.json 并复制 meaning，写入本套对应 case.json。新增 pack.json，名称为“棉团兔日常”（5 字），介绍为“圆滚滚的小白兔，用招手、大笑、比心和小脾气，陪你表达日常心情。”，版权为“原创试作”，审核状态为未提交。

沿用的含义词依次为“你好、哈哈、委屈、生气、爱你、害羞、无奈、开吃、挥爪”。生成成本按全套记录，共享姿势图未逐张重复计费，具体金额和模型版本工具未披露。

```bash
PYTHONDONTWRITEBYTECODE=1 "$PY" "$SCRIPTS/make_assets.py" cover "$OUT/character.png" --key-white --out "$OUT/assets/cover.png"
PYTHONDONTWRITEBYTECODE=1 "$PY" "$SCRIPTS/make_assets.py" icon "$OUT/character.png" --key-white --out "$OUT/assets/icon.png"
PYTHONDONTWRITEBYTECODE=1 "$PY" "$SCRIPTS/make_assets.py" banner "$OUT/character.png" --out "$OUT/assets/banner.png"
```

三条退出码均为 0，封面 240×240 约 35KB，图标 50×50 约 4KB，横幅 750×400 约 212KB。实际打开 `review/assets-black.png`，封面主体完整，自动图标裁到兔脸和长耳，放大后有小尺寸像素化。横幅使用定稿图居中裁切，长耳上端被裁掉，并保留白底。根据任务要求保留这个预期 FAIL，没有再出横幅。

### 6. 提交前机检

```bash
PYTHONDONTWRITEBYTECODE=1 "$PY" "$SCRIPTS/check_assets.py" "$OUT" --final \
  --report "$OUT/logs/check-final.json"
```

退出码 1。完整输出位于 `logs/check-final.txt`，结构化结果为 `logs/check-final.json`。FAIL / WARN 原样如下。

```text
[WARN] wx-005-heart: 和 wx-006-shy 首帧轮廓相近，并排看一下：只是表情不同算正常，姿势和动作也一样才会被判整套差异不足
[FAIL] banner: 详情页横幅不能是纯白底
```

汇总原文如下。

```text
1 FAIL · 1 WARN · 12 OK（规格：微信表情开放平台，提交前模式）
```

配套素材生成阶段另有一条原始警告。

```text
WARN 横幅四角都接近纯白，平台不接受纯白底，换一张有底色的源图
```

比心与害羞已经在黑底对照图中并排复核。比心为胸前持心形、单眼眨眼并点头，害羞为双手遮脸并摇摆，姿势、表情和动效可区分，保留该 WARN。

### 7. 黑底与动作对照

在 `review/build_review.py` 写了本试验的检查脚本，只读取原套和本套，将所有输出写在本套目录。执行命令如下。

```bash
PYTHONDONTWRITEBYTECODE=1 "$PY" "$OUT/review/build_review.py"
```

`review/compare.png` 为 480×2160，九行，每行左侧是原 GIF 首帧，右侧是兔子 GIF 首帧，均以原始 240×240 像素贴到纯黑底。`review/wave-frames.png` 为 1440×480，上行原六帧，下行新六帧，同样是黑底。

另外生成每张完整逐帧黑底对照、八张轻动效总览 `all-motion-frames.png`、跺脚 4 倍放大图 `stomp-black-4x.png`、素材黑底图和机器测量 `metrics.json`。辅助 Python 生成上述总览与放大图。已用 `view_image` 实际打开首帧对照、挥爪六帧对照、八张动作总览、跺脚放大图、素材图，也查看了图像工具返回的三次新图及修订图。

辅助检查脚本触发了一条 Pillow 的 `getdata()` 弃用警告，位于 `logs/review.txt`，不影响此次结果。其为本试验辅助代码的兼容性问题，未修改仓库脚本。

## 新图逐格验货

| 格 / 案例 | 姿势对应结论 | 细节 |
|---|---|---|
| 1 / 你好 | 对应 | 画面左手举起、张嘴笑，动势线保留 |
| 2 / 哈哈 | 对应 | 闭眼张嘴大笑，双手放低 |
| 3 / 委屈 | 对应 | 闭眼哭泣、双手胸前、蓝色泪滴 |
| 4 / 生气 | 修订后对应 | 皱眉张嘴、握拳、画面左脚抬起，白气团完整 |
| 5 / 爱你 | 对应 | 胸前持心形、单眼眨眼 |
| 6 / 害羞 | 对应 | 双手遮脸，粉色害羞线 |
| 7 / 无奈 | 对应 | 双手摊开、闭眼叹气，气团修订后闭合 |
| 8 / 开吃 | 对应 | 双手持咬过的饼干、闭眼笑 |
| 9 / 挥爪六格 | 动作次序对应，嘴型有偏差 | 放下→半抬→抬高→抬高→半落→放下，原张嘴笑改成闭嘴笑 |

姿势图为 3 列×3 行，八个有效格、末格空白。挥爪图为 3 列×2 行，六格齐全。每格全身入画，没有越格或裁断。角色替换干净，未见橘色皮毛、额头条纹、胡须、猫耳缺口或猫长尾残留。黄色动势线与棕色饼干属于原动作道具。未见文字、字母、数字、标点和拟声字。哭泣泪滴、生气符号和动作线为图形情绪标记。

严格画风要求尚未完全满足。粉色有轻微明暗变化，描边随头身、细节处有宽度差异。兔子基础配色为白、粉、深棕、深灰，加入道具后全套超过五种主色，开吃一格还同时引入饼干棕黄和黄色动势线。按严格标准将各 case 的 visual 保守记为 false，不能以机检通过替代画风验收。

## 白色角色去白底

九张主体的白色头部、耳朵、躯干、脚和短尾均保留。第 4 张抬脚曾在缩略图中被误判为抠空，随后实际打开 4 倍黑底图确认白色脚完整，最终结论以放大图为准。第 7 张修订后的白气团完整，原橘猫同处气团在黑底上只剩暗色线条。

没有看到环绕角色的连续白边。机器测量全部帧中最高近白轮廓占比分别约为 001 的 0.192%、004 的 0.164%、008 的 0.101%，其余为 0。该指标只能支持整体轮廓判断，放大图中仍可见零星亮点和 1-bit 透明边缘的小锯齿。各帧保留的不透明近白像素至少约 1.0–1.5 万，结合实际黑底图可确认没有整块身体被抠掉。

## 动作类型、幅度与节奏

001–008 沿用自动拟合动作，全部 strength=1.0、phase=0。nod 最大角度参数为 ±3°，sway 为 ±6°，bounce 位移参数为主体高度的 8%。兔子身形和耳朵比例变化会改变具体轮廓，不能将同一 strength 解释成每个像素轨迹完全一致。

| 案例 | 类型 | 原 / 新帧数 | 原 / 新总时长 | 原 / 新顶部 bbox 垂直跨度 | GIF 大小 |
|---|---|---|---|---|---|
| 001 | nod | 8 / 8 | 800 / 800 ms | 6 / 6 px | 92.6KB |
| 002 | bounce | 8 / 8 | 800 / 800 ms | 17 / 17 px | 89.8KB |
| 003 | sway | 8 / 8 | 800 / 800 ms | 3 / 2 px | 102.9KB |
| 004 | bounce | 8 / 8 | 800 / 800 ms | 17 / 16 px | 95.0KB |
| 005 | nod | 8 / 8 | 800 / 800 ms | 6 / 6 px | 102.8KB |
| 006 | sway | 8 / 8 | 800 / 800 ms | 2 / 3 px | 94.8KB |
| 007 | sway | 8 / 8 | 800 / 800 ms | 3 / 3 px | 99.8KB |
| 008 | bounce | 8 / 8 | 800 / 800 ms | 17 / 17 px | 94.0KB |
| 009 | 六帧挥爪 | 6 / 6 | 720 / 720 ms | 0 / 0 px | 58.6KB |

顶部 bbox 跨度为不透明包围框顶边在全段的极差，用于辅助比较，不能代替旋转角度或手部运动量。轻动效每帧原、新均为 100ms，挥爪每帧原、新均为 120ms，全部 loop=0。帧数、帧序、每帧时长和周期完全一致，整体运动类型与幅度接近。

挥爪六帧中手臂升降相位一致，第 3、4 帧均举高，第 6 帧放下并衔接第 1 帧。原与新的循环接缝比值分别为 0.4321 与 0.4362，均低于机检 0.6 警告阈值。兔子左右手尺寸和局部线形仍有逐帧漂移，嘴型也有上述偏差。

**实际播放验证未完成。** 已生成 `review/playback.html`，以原、新 GIF 成对供实时播放。尝试启动以下本地服务时，环境禁止监听端口，返回 `PermissionError: [Errno 1] Operation not permitted`，完整错误在 `logs/playback-server.txt`。

```bash
PYTHONDONTWRITEBYTECODE=1 "$PY" -m http.server 8765 --bind 127.0.0.1
```

随后尝试 CUA 浏览器读取本地 playback.html，返回 `The browser access host is unavailable`。CUA 原生 Chrome 入口返回 `Computer Use was not approved to use Google Chrome`。该限制来自工具访问层，未能通过当前可用权限恢复。因此仅完成实际开图、完整逐帧和时长检查，实时观看九组循环及主观流畅度仍待验证。

## 流程问题与建议

| 类别 | 现象 | 建议 |
|---|---|---|
| 提示词精度 | 首版第 4 格保留生气表情，却没有保留抬脚姿势 | 自动参考提示词增加逐格可见动作清单，将抬哪只脚、是否着地等写成明确约束 |
| 去白底前验货 | 首版无奈气团仍有开口，单写完整闭合描边没有保证生成闭合 | 生成后先对每格执行 key-white 黑底预览，重点复核白色道具和关节连线 |
| 六帧表情一致性 | 挥爪顺序保留，但张嘴笑改成闭嘴笑 | 提示词明确逐帧保持原参考的嘴部开合、眼部形状与表情 |
| 风格约束 | 粉色轻微渐变，线宽有变化，道具让总主色超过五种 | 定义全套统一的五色色板，并明确泪滴、饼干、动势线的复用色，增加禁止纹理与色阶的验收项 |
| 局部重绘 | 修订两格时返回整张新图，其他六格有轻微漂移 | 工作流说明重绘后重新验收整图，或提供受控区域替换步骤 |
| 分类文档 | 打印的“需要出图 2 次”没有包含定稿和可能的重画 | 文档显式列出换角素材次数、角色定稿次数与预留重绘预算，便于设定总调用上限 |
| 节奏保真边界 | 本套等时长完整保留。源码中 still 路线将时长取平均，非等时长原片会丢失逐帧节奏，属于源码发现的适用边界，本次未触发 | 文档说明等时长前提，后续为 still 保存并传递原 durations 列表 |
| 素材脚本状态 | make_assets banner 检出纯白四角，只给 WARN，仍以退出码 0 打印 OK，最终机检再 FAIL | 区分体积尺寸成功与整项合规状态，或提供严格模式返回非零退出码 |
| 横幅构图 | 从竖向定稿居中裁到横幅，长耳上端被裁断且白底不合规 | 文档继续要求单独设计横图，本次按用户要求保留复用定稿的负例 |
| 输出可追溯性 | remix_build 的 case 初始 id、title、meaning 留空，cost.generations=0，且不复制提示词和图集到各案例 | 文档明确补元数据步骤，后续可写入共享来源路径、生成次数及角色提示词引用 |
| 自动机检能力 | 文字、角色特征、嘴型偏差、严格色板与局部轮廓缺口未自动判定 | 将“逐格参考核对、去白底黑底检查、全套颜色验收”列为独立人工必检项 |
| 执行环境 | 本地端口和浏览器控制均不可用，实时播放无法验收 | 流程应记录可用播放工具及权限，失败时交付播放页并明确留下待验证项 |

没有修改上述脚本或文档。原套分类和扫描在此次输入上工作正常，未为证明问题而改写流程实现。

## 产物索引与验收状态

- `character.png` 和 `character-prompt.md` 为定稿与完整提示词。
- `_work/plan.json` 为分类、动作拟合、相位、时长和来源记录。
- `_work/poses/` 和 `_work/wx-009-wave/` 为原参考、提示词与换角图，姿势目录另保留修订前图和重绘提示词。
- 九个 `wx-*/result.gif` 与 `case.json` 为成品和元数据。
- `pack.json`、`assets/` 为专辑资料和三项配套素材。
- `review/compare.png`、`review/wave-frames.png` 为要求的两张对照图。
- `review/playback.html` 为待完成实时播放验证的入口。
- `logs/` 和 `review/metrics.json` 保留命令输出、机检和动作测量。

技术状态为九张 GIF 规格合格，整套因白底横幅 FAIL。视觉状态为角色已换净、白色主体保留、姿势与时序总体对应，仍有轻微画风偏差和挥爪嘴型差异。实际播放流畅度尚未验证，用户认可及提交审核均未进行。
