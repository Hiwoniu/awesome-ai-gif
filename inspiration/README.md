# 灵感池

从全网收集来的好 case 先放这里。**收进来不等于能用**：每条都要仓库主人审批通过，才能拿去做试做或落成 `cases/` 里的案例。

## 规则

1. **收**：看到好的动图、表情包、Skill、教程，就收一条（`tools/inspiration.py add`），状态是**待审**。谁收的都行，Agent 也可以收。
2. **审**：只有仓库主人能审批。Agent 不能自己批，只有主人在对话里明确说“通过 / 驳回 / 搁置 insp-xxx”时，才代为执行 `review`，审批人写主人的名字。
3. **用**：只有**已通过**的条目能拿去用，用法也只有一种：借它的类型、手法、构图或提示词结构，换成**我们自己的原创角色**重做。不照搬对方的画面、角色、文案和提示词原文。
4. **落地**：重做出来的试做或案例，用 `land` 记回来，状态变成**已落地**。案例的 `case.json` 写 `"inspired_by": "insp-xxx"`，`tools/build_index.py` 会检查这条灵感是否已通过，没通过就报错。
5. **不入库**：别人的图片、视频、GIF 一律不进 git。截图放在条目的 `media/` 里只留本地，入库的只有链接和我们自己写的分析。

## 状态

```
待审 pending ──通过──▶ 已通过 approved ──落成案例──▶ 已落地 landed
    │
    ├──驳回──▶ 驳回 rejected（写清原因，比如 IP、真人、没新意）
    └──搁置──▶ 搁置 parked（现在做不了，比如要视频、要新脚本；以后 reopen 退回待审）
```

| 状态 | 能不能用 | 谁改 |
|---|---|---|
| 待审 | 不能 | 收的时候自动 |
| 已通过 | 能，按规则 3 重做 | 仓库主人 |
| 已落地 | 已经用过，还能继续用 | `land` 自动 |
| 搁置 | 不能 | 仓库主人 |
| 驳回 | 不能 | 仓库主人 |

## 一条灵感长什么样

```
inspiration/insp-003-xxx/
├── item.json   # 出处、类型、一句话是什么、为什么收、想借什么、风险、状态、审批记录、落地记录、历史
├── notes.md    # 自己的分析：它怎么做的、我们怎么用
└── media/      # 截图录屏，只留本地（.gitignore 已排除）
```

`item.json` 字段：

| 字段 | 说明 |
|---|---|
| `id` | `insp-` 加三位编号，`add` 自动排号 |
| `type` | 预计落到哪个类型：`wechat-stickers` `cards` `posters` `signatures` `storybooks` `multi` `unknown` |
| `source` | `url` 出处链接（必填）、`platform` 平台、`author` 作者、`found_at` 收的日期、`found_by` 谁收的 |
| `what` / `why` | 一句话它是什么；一句话为什么值得收 |
| `borrow` | 想借的点：类型、动效、构图、提示词结构、脚本思路…… |
| `risks` | `ip_or_real_person` 是否涉及 IP 或真人、`license` 对方的授权（`MIT`、`unknown`……）、`note` |
| `status` | 见上 |
| `review` | 审批记录：`decision` `by` `date` `note`。审批说明里写清“借什么、不借什么” |
| `landed` | 落成的案例编号或试做目录 |
| `history` | 每次状态变化：日期、状态、谁、说明 |

## 常用命令

```bash
python3 tools/inspiration.py add --title "某某的光栅卡" --url https://… --platform 小红书 --type cards --why "竖条翻转很顺" --borrow 翻转节奏 --by 向明
python3 tools/inspiration.py review insp-003 approve --by 向明 --note "借翻转节奏，角色换橘团"
python3 tools/inspiration.py land insp-003 cd-001
python3 tools/inspiration.py board
```

## 看板

由 `tools/inspiration.py board` 生成，不要手改。

<!-- board:start -->

总数：**168**（待审 166，已通过 0，已落地 2，搁置 0，驳回 0）

### 待审（166）

| 编号 | 标题 | 类型 | 出处 | 借什么 | 审批 / 落地 |
|---|---|---|---|---|---|
| [insp-003](insp-003-arcloop-image-2-6-expression-gif/) | Arcloop Image 2.6 六种角色表情 GIF 实测 | 微信表情包 | [Arcloop](https://arcloop.ai/handbook/zh-CN/image-2-6-character-expression-gif-guide) | 情绪提示词结构：情绪+面部变化+一个主要动作+结束姿势、六种高频情绪的动作化写法、拆帧验收方法 | — |
| [insp-004](insp-004-tencent-gpt-image-2-6-gif-guide/) | 腾讯云：从文字脚本到动态表情包的 GIF 动效指南 | 微信表情包 | [腾讯云开发者社区](https://cloud.tencent.com/developer/article/2779922) | 四句动作脚本结构、6-9帧起测、复杂动作再加到12-16帧的经验、首尾姿势一致的循环要求写法 | — |
| [insp-005](insp-005-varg-gpt-image-gif-skill/) | vargHQ 的 gpt-image-gif Skill：循环锁与像素预算 | 多类型 | [Skills Directory](https://www.skillsdirectory.com/skills/varghq-gpt-image-gif) | loop-lock 提示词措辞：首尾同姿势、锁定比例和地平线、2/4/6/9/12/16 帧的像素预算实测表思路、approve-a-still-first 工作流、转 WebP/MP4 的后处理脚本思路 | — |
| [insp-006](insp-006-animated-sticker-studio/) | animated-sticker-studio：一张角色图做多平台动图表情包 | 微信表情包 | [GitHub](https://github.com/fantuan-lab/animated-sticker-studio) | 多平台规格预设思路、plan到deliver的流水线分工、自动压缩到各平台体积上限并自检 | — |
| [insp-007](insp-007-hotshot-xl-text-to-gif/) | Hotshot-XL：SDXL 生态的开源 Text-to-GIF 模型 | 多类型 | [GitHub](https://github.com/hotshotco/hotshot-xl/blob/HEAD/README.md) | LoRA锁主体+运动模型分离的思路、ControlNet控制构图做GIF、短时长高帧率的参数取向 | — |
| [insp-008](insp-008-veevid-sprite-sheet-gif/) | Veevid：单张 sprite sheet 提示词直出 9 帧循环 GIF | 微信表情包 | [Veevid](https://veevid.ai/ai-gif-generator) | sprite sheet 提示词前缀结构、9帧x200ms的循环参数、反应表情/吉祥物/产品循环的分类示例组织 | — |
| [insp-009](insp-009-lemo-wake-image-to-loop/) | lemo-wake：一张静态图拆解重建做 5 秒无缝循环 | 多类型 | [SkillsLLM](https://skillsllm.com/skill/lemo-wake) | 拆图重建+代码编舞的路线、无缝循环的收尾处理、一张图多规格输出（GIF/WebP/实况照片等） | — |
| [insp-010](insp-010-gootaku-x-looping-anime-gif/) | Gootaku：为 X 帖子做的宽幅环境循环 GIF 与提示词公式 | 动态海报 | [Gootaku](https://gootaku.com/blog/anime-gif-for-twitter-x-header) | 宽幅环境循环提示词公式：宽景+慢速环境动效+氛围光影+风格+柔和无缝循环、X平台对GIF的展示限制、环境微动而非主体大动作的海报思路 | — |
| [insp-011](insp-011-gif-sticker-maker/) | Gif Sticker Maker：照片转 4 张 Funko 风动态贴纸 Skill | 微信表情包 | [GitHub](https://github.com/bighardperson/computer-science-skills-collection/tree/main/skills/GIF%20贴纸制作) | 照片转贴纸的三段式流程：生图、视频化、转 GIF、字幕对照表管多语言文案的思路、一次出 4 张成套表情的打包方式 | — |
| [insp-012](insp-012-pixel-gif-sticker-pack/) | pixel-gif-sticker-pack：透明循环 GIF 表情包 Skill | 微信表情包 | [GitHub](https://github.com/WoYun520/pixel-gif-sticker-pack) | 外观与动作分开选的搭配思路、透明底 512×512、约 2 秒循环的贴纸默认值、导出脚本加视觉复核的交付流程 | — |
| [insp-013](insp-013-varg-gpt-image-sticker-pack/) | vargHQ 的 gpt-image-sticker-pack Skill：一张定妆照出整套多平台表情包 | 微信表情包 | [Skills Directory](https://www.skillsdirectory.com/skills/varghq-gpt-image-sticker-pack) | 先审定妆照再批量出 GIF 的工作流、6-8 种情绪各一张 GIF 的成套规划、已核对官方文档的多平台规格表思路、导出脚本统一转码的流程 | — |
| [insp-014](insp-014-varg-gpt-image-sprite-sheet/) | vargHQ 的 gpt-image-sprite-sheet Skill：严格 4×4 游戏精灵图表 | 多类型 | [Skills Directory](https://www.skillsdirectory.com/skills/varghq-gpt-image-sprite-sheet) | 严格 4×4 格表规格：16 帧、等格、固定比例和地平线、切片加抠底加统一地平线的后处理脚本思路、TexturePacker 格式图集 JSON 的输出组织、PNG 表与原生 GIF 两条路线的对比取舍 | — |
| [insp-015](insp-015-pneuma-sprite/) | pneuma-sprite Skill：八方向精灵图与呼吸待机循环 | 多类型 | [Skills Directory](https://www.skillsdirectory.com/skills/pandazki-skill-20c6f714) | 八方向精灵表的规划思路、从视频借动作的转移动作做法、给静帧加呼吸感待机循环的思路、先看循环效果再交付的检查流程 | — |
| [insp-016](insp-016-sprite-gen/) | sprite-gen：一张底图出游戏精灵图集与透明循环 | 多类型 | [GitHub](https://github.com/aldegad/sprite-gen) | 按动作状态逐行生成再拼图的思路、抠纯色背景转真透明的抽帧做法、manifest.json 记录帧位置、帧率与循环标志的组织方式、挑帧浏览视图与循环质量检查流程 | — |
| [insp-017](insp-017-spritegen-ai/) | SpriteGen：文字描述直出像素风精灵表与 GIF | 多类型 | [SpriteGen](https://spritegen.ai/) | 6、8、12 帧三档的帧数选项、俯视与等距视角支持八方向的组织方式、生成后先播循环预览再下载的流程、像素画编辑器加洋葱皮的逐帧修法 | — |
| [insp-018](insp-018-lottie-ai/) | Lottie AI：文字提示词生成可编辑矢量动画并导出 GIF | 多类型 | [LottieFiles](https://lottie.ai/) | 提示词四要素：动什么、怎么动、风格、颜色、矢量动画生成后可改色改形的思路、Turbo 与 Quality 两档生成的取舍、GIF 只作兼容回退、主推矢量格式的导出策略 | — |
| [insp-019](insp-019-lotiqlab/) | LotiqLab：浏览器本地 AI 生成 Lottie 并转 GIF | 多类型 | [LotiqLab](https://lotiqlab.com/) | 浏览器本地解析渲染、不上传文件的思路、AI 直写 Lottie 再进编辑器改的流程、转 GIF、MP4、JSON、dotLottie 的导出组织 | — |
| [insp-020](insp-020-sticker-kitchen/) | Sticker Kitchen：一张照片转 AI 动态 GIF 与免费 GIF 工具箱 | 微信表情包 | [Product Hunt](https://www.producthunt.com/products/sticker-kitchen) | 一张照片转动态 GIF 的产品形态、生成收费、后处理工具免费的组织方式、浏览器内免上传的 GIF 压缩裁剪思路 | — |
| [insp-021](insp-021-docsaura-signature/) | DocsAura：从官网文案生成 480×160 动态邮件签名 GIF | 动态签名 | [DocsAura](https://www.docsaura.com/email-signature) | 480×160、12 秒循环、900KB 以内的签名卡规格、首帧独立成图、不播也能看的兜底思路、按邮件客户端列播放兼容表的验收方法、一次给三张候选再挑的生成组织 | — |
| [insp-022](insp-022-promptslove-gif-generator/) | Promptslove 的 GPT Image 2.6 提示词生成器：五段式简报与 GIF 参数 | 多类型 | [Promptslove](https://promptslove.com/free-tools/gpt-image-prompt-generator/) | 五段式简报结构：场景、主体、细节、用途、约束、循环 GIF 贴纸的固定模板套路、帧数与帧时长的参数取值范围 | — |
| [insp-023](insp-023-0xluffy-x-sticker-template/) | X 走红的 ChatGPT 贴纸 GIF 模板：自拟动作与顶部标语 | 微信表情包 | [Promptline](https://promptline.net/news/2026/11/chatgpt-animated-sticker-gif-prompt) | 留白式模板：动作与标语由模型自拟、顶部标语的格式要求：短句、粗圆体、白描边、一个核心笑点加首尾接回的动作要求 | — |
| [insp-024](insp-024-lumenfix-gif-generator/) | Lumenfix 的 GPT Image 2.6 GIF 生成器：12 帧实测与提示词示例 | 微信表情包 | [Lumenfix](https://www.lumenfix.app/gpt-image-2-6-gif) | 12 帧、150 毫秒、长边 640 像素的实测参数、失败退积分的容错做法、多种动作类型的提示词示例组织 | — |
| [insp-025](insp-025-bulkimagen-gif-guide/) | BulkImagen 实测：16 张贴纸总结的一主一体一动提示词结构 | 微信表情包 | [BulkImagen](https://bulkimagen.com/blog/gpt-image-2-6-gif) | 一个主体、一个动作、一种风格的极简提示词结构、9 帧、每帧 200 毫秒的默认参数、透明底不可靠、改尺寸压平 GIF 的避坑点 | — |
| [insp-026](insp-026-runware-animated-gifs/) | Runware 文档：GPT-Image-2.6 Flare 的 GIF API 参数与提示词 | 多类型 | [Runware](https://runware.ai/docs/models/openai-gpt-image-2-6-flare/guides/animated-gifs) | API 路线的 GIF 参数写法：输出格式、帧数、帧时长、默认 9 帧、0.2 秒、512×512 的参数组合、贴纸与产品旋转两类提示词模板结构 | — |
| [insp-027](insp-027-juejin-seedream-55/) | 掘金老金实测 Seedream 5.5：角色设定表加八格精灵图 | 微信表情包 | [掘金](https://juejin.cn/post/7707495140638556214) | 先做角色设定表再出动作格的流程、4 列×2 行八格、每帧 0.24 秒的参数、多轮改字保持其他区域不动的用法、透明底原生直出的取舍 | — |
| [insp-028](insp-028-huashu-selfie-sticker/) | 花叔的 huashu-selfie-sticker Skill：自拍做 8 表情透明底动态包 | 微信表情包 | [GitHub](https://github.com/alchaincyf/huashu-selfie-sticker) | 自拍转角色设定图再出八格表的 Skill 流程、字幕直接画在同一格里的字幕处理、8 个表情各 8 帧的成套规模组织 | — |
| [insp-029](insp-029-dong-six-frame-stickers/) | 懂AI：一句提示词出六帧的微信表情包全流程 | 微信表情包 | [懂AI](https://dong.xs91.com/archives/13014.html) | 3 列×2 行六格、每帧 100-150 毫秒的参数、六格提示词的要点清单：格数、一致性、首尾接回、无文字、国产工具 B 计划的横向对比、微信 240×240 与体积上限的规格提醒 | — |
| [insp-030](insp-030-aiboss88-gif-prompts/) | aiboss88 实测：参考 GIF 换主角与多场景 GIF 提示词 | 微信表情包 | [aiboss88](https://www.aiboss88.com/ja/news/tutorial-511613325-1794406095674-0) | 参考 GIF 换主角的做法：动作镜头取参考、外观取角色图、真人照片做自然小动作的表情做法、教育科普与商业图表两类非表情场景的提示词结构 | — |
| [insp-031](insp-031-ace-data-storybook/) | Ace Data：GPT Image 2.6 做四格动态绘本《小狐狸借月光》 | 动态绘本 | [Ace Data](https://20260104.platform.acedata.cloud/blog/gpt-image-2-6-little-fox-moonlight-storybook) | 四格分镜讲完整故事的结构：相遇、借光、同行、归家、微动而非大动作的绘本动效思路、每段独立生成 GIF 再拼视频的流程、关掉 GIF 内循环标记、用流式循环无限播的做法 | — |
| [insp-032](insp-032-ofox-seedream-gif-export/) | ofox 实测：Seedream 5.5 出帧后的本地导出与校验流程 | 多类型 | [ofox](https://ofox.ai/blog/seedream-5-5-frames-to-gif/) | 本地 PNG 帧拼 GIF 的导出工具链、导出后写检查报告的验收做法、验格表是否干净 3 列×2 行的检查要点、实测与未验证分开标注的写法 | — |
| [insp-033](insp-033-tjrobertson-sprite-sheet/) | TJ Robertson 实测：Sunburst 与 Flare 画精灵表的对比 | 多类型 | [TJ Robertson](https://tjrobertson.com/gpt-image-2-6-sprite-sheet-animation/) | Sunburst 与 Flare 画精灵表的选型结论、逐帧画优于整张表的实测结论、卡通角色可用、产品转盘不行的适用边界、透明底锯齿问题的提醒 | — |
| [insp-034](insp-034-banana-prompts-studio/) | Banana Prompts：网页端切 PNG/GIF 格式直出 1.8 秒循环 | 微信表情包 | [Banana Prompts](https://banana.prompts.xyz/studio/image) | PNG 与 GIF 格式切换出动画的产品形态、1.8 秒循环的默认动画预设、Sunburst 与 Flare 的模型选型入口 | — |
| [insp-035](insp-035-runway-gif-stickers/) | Runway Tool 模式：Flare 24 秒出 4 张循环 GIF 贴纸 | 多类型 | [Instagram（Runway 演示）](https://www.instagram.com/reel/DfqAutIj53N/) | Flare 与 Sunburst 的分工：贴纸图标走 Flare、产品图走 Sunburst、GIF 贴纸加 SVG 图标加产品图拼品牌套件的流程、24 秒出 4 张贴纸的速度参考 | — |
| [insp-036](insp-036-atlascloud-gif-sticker-guide/) | Atlas Cloud：GPT Image 2.6 动态贴纸指南，水獭提示词与导出规则 | 微信表情包 | [Atlas Cloud](https://www.atlascloud.ai/blog/tips/gpt-image-2.6-animated-sticker) | 三段式提示词结构：背景设定、角色与镜头固定、动作加收尾姿势、先定发布渠道再定导出格式 | — |
| [insp-037](insp-037-imagesv2-gif-guide/) | imagesv2：GPT Image 2.6 做 GIF 的设置、提示词与实例 | 微信表情包 | [imagesv2](https://imagesv2.ai/blog/gpt-image-2-6-gif) | 按场景选帧数的对照表、主体加起始姿势加一个动作加回起始姿势的提示词公式、背景分不透明与透明两档 | — |
| [insp-038](insp-038-video2dsprite-skill/) | video2dsprite Skill：Grok 视频转密帧精灵图 | 多类型 | [GitHub](https://github.com/0x0funky/agent-sprite-forge/tree/main/skills/video2dsprite) | 视频先行再抽帧的路线：静帧、原地运动视频、抽帧、抠色、采样、拼表、密帧与稀疏帧的分工 | — |
| [insp-039](insp-039-mori-sprite-studio/) | Mori Sprite Studio：一张参考图出 6+2 状态精灵包 | 多类型 | [Mori Sprite Studio](https://yazelin.github.io/mori-sprite-studio/) | 6 必需加 2 可选的状态规划、统一 4×4 规格、按用途分流导出 APNG、GIF、WebM | — |
| [insp-040](insp-040-thinkdiffusion-animatediff-gif/) | ThinkDiffusion：AnimateDiff 做 GIF 动画教程 | 多类型 | [Civitai](https://civitai.com/articles/2312/create-stunning-gif-animations-quickly-with-animatediff-by-thinkdiffusion) | 运动模块加基础模型的分层思路、16 帧起步、无限循环的参数取法 | — |
| [insp-041](insp-041-comfyui-animatediff-guide/) | ComfyUI AnimateDiff：静态图变动图的完整工作流 | 多类型 | [alexanderharte.com](https://www.alexanderharte.com/comfyui-animatediff-guide/) | 去噪 0.3-0.5 保一致性、提示词 75 token 上限、帧插值提顺滑度、闭环循环检查清单 | — |
| [insp-042](insp-042-aiplusgate-gif-guide/) | AIPlusGate：ChatGPT Images 2.6 一张图做循环动图 | 微信表情包 | [AIPlusGate](https://aiplusgate.com/guides/chatgpt-images-2-6-gif/) | 三步流程：基准图、写动作与保留项、两轮播放验收、头像重一致性、产品重文字区稳定 | — |
| [insp-043](insp-043-iljrose-image-26-gif-tips/) | iljrose：Image 2.6 动 GIF 与编辑一致性 5 个要点 | 动态海报 | [iljrose.com](https://iljrose.com/%ec%98%a4%ed%94%88ai-%ec%9d%b4%eb%af%b8%ec%a7%80-2-6-%ec%82%ac%ec%9a%a9%eb%b2%95-%ec%9b%80%ec%a7%81%ec%9d%b4%eb%8a%94-gif-%ec%83%9d%ec%84%b1%ea%b3%bc-%ed%8e%b8%ec%a7%91-%ec%9d%bc%ea%b4%80/) | 三步提示词结构：风格锚点、运动轨迹加缓动、帧插值与闭环、logo 只加小幅弹跳或旋转 | — |
| [insp-044](insp-044-openart-claude-motion-graphics/) | OpenArt：Claude 加 Remotion 代码做动态图形 | 动态海报 | [OpenArt](https://openart.ai/blog/how-to-make-ai-motion-graphics-with-claude/) | 图层拆分再编舞的路线、文字在代码里重建、六姿势精灵表加背景图的海报做法 | — |
| [insp-045](insp-045-flixly-gif-maker/) | Flixly：GPT Image 2.6 GIF Maker 实测与示例 | 多类型 | [Flixly](https://www.flixly.ai/blog/gpt-image-2-6-gif-maker) | 三档尺寸按用途分、产品固定只动蒸汽或反光、反应贴纸一个动作加粗白描边 | — |
| [insp-046](insp-046-xiaohu-seedream-55-guide/) | xiaohu：Seedream 5.5 官方指南 walkthrough，透明贴纸与多轮改图 | 微信表情包 | [xiaohu.ai](https://xiaohu.ai/en/article/seedream-5-5-user-guide/) | 先出一张再多轮精修、透明贴纸分开写半透明与抠除、一句话出一整版贴纸、风格词与审美词表 | — |
| [insp-047](insp-047-blogduwebdesign-gif-test/) | Blog du Webdesign：ChatGPT GIF 实测，三种用途的尺寸与翻车点 | 动态海报 | [Blog du Webdesign](https://www.blogduwebdesign.com/blog/tech/chatgpt-images-gif-anime.html) | 逐文件量尺寸、帧数、时长、体积的验收写法、三种用途的取舍、失败模式清单 | — |
| [insp-048](insp-048-xiaoheiwan-10-gif-prompts/) | 小黑丸：GPT-Image-2.6 实测，10 个 GIF 玩法提示词 | 多类型 | [小黑丸](https://upgrade.xiaoheiwan.com/aihot/kss7rjmanc8dv5mpj60jtdzgd) | 10 类玩法的提示词结构分类、跨对话角色记忆、局部圈改、动作序列网格对齐 | — |
| [insp-049](insp-049-kim-sticker-pack/) | kim-sticker-pack Skill：批量生成动态表情包的开源 Skill | 微信表情包 | [掘金](https://article.juejin.cn/post/7704580559872589858) | 先样片后批量的流程、8 条场景的规划方法、导出脚本只管帧序与时长 | — |
| [insp-050](insp-050-flowjam-video-signature/) | Flowjam：AI 视频邮件签名，可点击 GIF 预览做法 | 动态签名 | [Flowjam](https://www.flowjam.com/blog/how-to-make-a-video-email-signature-with-ai-2026) | 可点击 GIF 预览的思路、首帧放播放按钮、宽度 600 像素以内 | — |
| [insp-051](insp-051-morphlogo-email-signature/) | MorphLogo：动态邮件签名 GIF，首帧即 logo 的规则 | 动态签名 | [MorphLogo](https://morphlogo.com/blog/animated-email-signature) | 首帧即 logo 的规则、导出规格 240 像素、10fps、播一次停末帧、按客户端列兼容表 | — |
| [insp-052](insp-052-ohneis-chatgpt-gif-reel/) | Ohneis 的 Instagram 教程：一句提示词出精灵表循环 GIF | 微信表情包 | [Instagram](https://www.instagram.com/reel/DfV5T8YgJuD/) | 最简精灵表写法：3×2 共 6 帧、末帧接回首帧、6 帧每帧 200 毫秒、1.2 秒循环 | — |
| [insp-053](insp-053-veevid-gpt-image-26-gif-guide/) | Veevid：GPT Image 2.6 做 GIF 的提示词结构与实测参数 | 多类型 | [Veevid](https://veevid.ai/blog/gpt-image-2-6-gif) | 五段式提示词结构：开场白、分步动作、固定项、风格、排除项、9 帧×200 毫秒、1.8 秒循环的参数、Flare 与 Sunburst 按用途选型的思路 | — |
| [insp-054](insp-054-devto-four-ways-photo-to-gif/) | dev.to：四种路线把一张照片变成 GIF 的横向对比 | 多类型 | [dev.to](https://dev.to/deepfox/4-ways-to-turn-one-photo-into-a-gif-free-frames-sprite-sheets-gpt-image-26-and-video-ai-4fld) | 四条路线的对比维度：帧数、成本、适用场景、精灵表 16 帧 4×4 的写法、照片转 GIF 只写动作的四条规则：一个动作、写清收尾、固定机位、背景干净 | — |
| [insp-055](insp-055-foxlab-one-photo-one-gif/) | foxlab 实测：GPT Image 2.6 一张照片一步出 GIF | 微信表情包 | [Medium](https://medium.com/@foxlab/one-photo-one-step-one-gif-trying-gpt-image-2-6s-new-gif-mode-3feccf47fce1) | 照片转 GIF 四条规则：一个动作、写清收尾、固定机位、背景干净、精灵表做法与直出 GIF 的取舍对照、产品图只动蒸汽或反光的克制做法 | — |
| [insp-056](insp-056-openart-ai-gif-generator/) | OpenArt AI GIF 生成器：一句话或一张照片出循环 GIF | 多类型 | [OpenArt](https://openart.ai/features/ai-gif-generator/) | 一句话只描述一个动作的写法、已生成图片复用为 GIF 底图的工作流、按场景给的示例组织：猫、霓虹灯牌、咖啡蒸汽 | — |
| [insp-057](insp-057-gemini-gif-cli/) | gemini-gif：用 Gemini API 从文字提示词生成 GIF 的开源 CLI | 多类型 | [PyPI](https://pypi.org/project/gemini-gif/0.1.0/) | 用 Gemini 2.0 Flash 做 GIF 的模型路线、提示词模板参数化的做法、CLI 工具的形态参考 | — |
| [insp-058](insp-058-civitai-animatediff-lightning-dance/) | Civitai：AnimateDiff Lightning 把视频变成舞蹈循环动画 | 多类型 | [Civitai](https://civitai.com/articles/4769/animatediff-lightning-dance-animations) | 视频先行再风格化的路线：原视频动作加 AnimateDiff 重绘、AnimateDiff Lightning 8 步运动模块的选型、LoopMaker 做无缝循环的前处理思路 | — |
| [insp-059](insp-059-kavel-animate-illustrations/) | Kavel AI：让绘本插画动起来，只动故事该动的部分 | 动态绘本 | [Kavel AI](https://www.kavel.ai/video/animate-illustrations) | 先定不动清单、再挑两三个小动作的提示词写法、文字不动、角色笔触不动的验收标准、只动封面与结尾页、其余页保持静态的克制思路 | — |
| [insp-060](insp-060-woshipm-seedream-55-sticker/) | 人人都是产品经理：Seedream 5.5 连改 20 轮仍是同一个人，附 GIF 表情包教程 | 微信表情包 | [人人都是产品经理](https://www.woshipm.com/ai/6491515.html) | 多轮编辑一致性的压力测试方法：连改再改回去对照、GPT GIF 直出等于 4×3 多格图加切帧的拆解思路、角色设定图加八格精灵图、每格底部同字幕的做法 | — |
| [insp-061](insp-061-picassoia-storybook-generator/) | PicassoIA：免费 AI 绘本生成器，十二页同角色与动效取舍 | 动态绘本 | [PicassoIA](https://blog.picassoia.com/ai-storybook-generator-free-with-pictures-for-kids) | 连续模式一次出多张同角色页面的做法、多页一致性的模型选型对照：Seedream 5 Lite、Nano Banana 2、动效只放封面与结尾页的取舍 | — |
| [insp-062](insp-062-tryvitrine-lenticular-card/) | Vitrine 光栅卡组件：两张图竖条交错、指针驱动翻面 | 光栅变画卡 | [Vitrine](https://www.tryvitrine.dev/components/lenticular-card) | 6px 竖条纹交错遮罩的光栅实现、指针位置映射过渡变量、中间段平滑过渡的交互写法、同卡两面（例如白天与夜晚同一海报）的构图思路 | — |
| [insp-063](insp-063-recharm-flip-transition/) | Recharm：卡片翻面转场，0.8 秒 3D 翻转的逐帧脚本 | 光栅变画卡 | [Recharm](https://www.recharm.com/effects/flip-transition) | 0.8 秒翻面的帧参数：24 帧、三次缓动、绕竖轴 180 度、透视投影与边缘变暗的逐帧写法、A 面翻到 90 度后换 B 面的衔接思路 | — |
| [insp-064](insp-064-pixelfx-pixel-effects/) | pixelfx：244 个像素风特效代码库，带 Claude Skill 与 GIF 导出 | 多类型 | [GitHub](https://github.com/patch-gg/pixelfx) | 代码逐帧算特效、再导出精灵表的路线、特效的表演结构：蓄势、命中定格、受击回摆、恢复、导出精灵表加帧信息 JSON 的组织方式 | — |
| [insp-065](insp-065-image-use-animate-cli/) | image-use：零依赖 CLI 加 Skill，用已有 ChatGPT 订阅做图与 GIF | 多类型 | [GitHub](https://github.com/leeguooooo/image-use) | 用已有订阅当生图后端、不用 API Key 的工具形态、animate 命令：严格 4×2 精灵表、裁 8 帧、校验主体漂移、往返循环、源精灵图随动画一起保留的交付做法 | — |
| [insp-066](insp-066-ray-sticker-shop/) | ray-sticker-shop：面向微信上架的动态表情包 Skill，含全套投稿素材 | 微信表情包 | [GitHub](https://github.com/imraywang/ray-sticker-shop) | 一图锁定形象、批量出整套的流程、240×240、500KB 以内自动压缩加规格自检的做法、封面、图标、横幅、打赏图五件套一起交付的组织方式 | — |
| [insp-067](insp-067-capafy-gif-sticker-maker/) | Capafy AI GIF 贴纸生成器：一张照片出 2 到 8 张循环贴纸 | 微信表情包 | [Capafy AI](http://capafyai.io/tools/emoji-generator/gif-sticker-maker) | 先定角色静帧、再逐表情出 GIF 的顺序、8 帧、512×512、透明底的贴纸默认值、微信 240×240、WhatsApp 512×512 加托盘图标的分平台导出组织 | — |
| [insp-068](insp-068-texttogif-sticker-maker/) | texttogif 贴纸工坊：一个角色出一整套，文案与动作可改不花 AI 点数 | 微信表情包 | [texttogif](https://texttogif.com/sticker-maker) | 先出四张样片、定稿后再批量出的流程、改文案与动作不花 AI 点数的编辑分层、按平台分包导出、微信包带横幅封面图标的组织方式 | — |
| [insp-069](insp-069-stickersmaker-seedream-seedance/) | StickersMaker：Seedream 画角色、Seedance 做动画的两段式贴纸工具 | 微信表情包 | [StickersMaker](https://meme.ransomz.dev/about) | 角色模型与动画模型分开的两段式路线、Seedream 5 Flash 做角色、Seedance 2 Mini 做动画的模型搭配、WhatsApp 用 WebP、微信用 GIF、Telegram 用 WebM、Discord 用 APNG 的分平台格式对照 | — |
| [insp-070](insp-070-animtool-gif-studio/) | AnimTool：浏览器本地做的 GIF 工作室，不上传文件 | 多类型 | [Product Hunt](https://www.producthunt.com/products/animtool?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+upvote0+%28ID%3A+205296%29) | 浏览器本地处理、不上传文件的工具形态、视频转 GIF、图片拼动画、剪辑一体的工作室组织、GIF、WebP、APNG、AVIF 多格式导出的对照 | — |
| [insp-071](insp-071-codearia-images-26-gif-references/) | Codearia：ChatGPT Images 2.6 的 GIF 与保存参考图五步教程 | 微信表情包 | [Codearia Academy](https://academy.codearia.com/en/articles/chatgpt-images-2-6-gif-saved-references) | 保存参考图加 GIF 叠加的贴纸包流程、一次保存角色、多次复用的角色一致性做法、GIF 只能改自己做的、不能改外部导入 GIF 的边界提醒 | — |
| [insp-072](insp-072-da-motion-sticker-skill/) | DA Motion Sticker Skill：一张角色图出 9 张透明 GIF 套装 | 微信表情包 | [GitHub](https://github.com/avocadotear/da-motion-sticker-skill) | 3×3 九宫格、9 个反应的整套规划法、关键姿势路线组帧做法、打包前强制校验 | — |
| [insp-073](insp-073-atomm-lenticular-card-generator/) | Atomm 光栅卡生成器：激光切割滑动动画卡 | 光栅变画卡 | [Atomm](https://www.atomm.com/creativetools/lenticular-card-generator) | 条纹栅栏滑动动画替代透镜片的卡片结构、帧数与狭缝宽度的权衡参数 | — |
| [insp-074](insp-074-sprite-animation-assets/) | Sprite Animation Assets Skill：定身份锚点再出多状态精灵表 | 多类型 | [GitHub](https://github.com/DwDestiny/codex-visual-asset-skills/tree/main/skills/sprite-animation-assets) | 先定身份锚点再分状态生帧的流程、manifest 与验收报告的组织方式 | — |
| [insp-075](insp-075-ofox-gpt-image-26-gif-guide/) | Ofox 实测：GPT Image 2.6 做 GIF 的三路线对比 | 多类型 | [Ofox](https://ofox.ai/blog/gpt-image-2-6-gif-guide/) | ChatGPT / 原生 API / 精灵表拼装三路线选择表、六段式提示词结构 | — |
| [insp-076](insp-076-pixazo-8bit-sprite-sheet-gif/) | Pixazo：自拍变 8-bit 精灵表循环 GIF | 微信表情包 | [Pixazo](https://www.pixazo.ai/blog/how-to-make-8-bit-sprite-sheet-gif) | 4×4 十六帧按动作分格的制表要求、纯色背景加细网格线便于切片 | — |
| [insp-077](insp-077-ludo-sprite-generator/) | Ludo AI 精灵图生成器：四种动作驱动方式 | 多类型 | [Ludo](https://ludo.ai/features/sprite-generator) | 四种动作驱动方式、关键帧首尾同姿势成环、透明 PNG 加 JSON 导出 | — |
| [insp-078](insp-078-startai-gpt-image-26-nine-gif-plays/) | StartAI：GPT Image 2.6 九个 GIF 实战玩法 | 多类型 | [StartAI](https://istarry.com.cn/ps/gpt-images-2-6-gif-tutorial/) | 固定镜头、仅局部运动、首尾帧对齐的三条循环原则、粗白边加纯色底做法 | — |
| [insp-079](insp-079-sugarcube-sprite-sheet-gif-guide/) | SugarCube：用精灵图做 AI GIF 的全流程 | 多类型 | [SugarCube](https://sugarcube.art/blog/zh/how-to-make-ai-gifs-from-sprite-sheets/) | 3×3 九帧精灵图四段式提示词结构、先检查网格再拆帧编码的验收顺序 | — |
| [insp-080](insp-080-yihook-ecommerce-gif-test/) | Yihook 实测：GPT Image 2.6 电商 GIF 的 8 个案例与参数 | 动态海报 | [Yihook](https://www.yihook.ai/zh-cn/ai-gif-generator) | 按场景选尺寸、帧数、帧时长的参数搭配、按拼图网格档位计费的成本判断 | — |
| [insp-081](insp-081-juejin-yupi-images-26-gif-test/) | 掘金鱼皮首发实测：Images 2.6 直出 7 张 GIF | 多类型 | [掘金](https://juejin.cn/post/7704505142818078783) | 起手、峰值、收尾、回到起点的四段动作结构、精灵图切换逐帧改台词 | — |
| [insp-082](insp-082-hand-drawn-storybook-animation-skill/) | 手绘动画绘本 Skill：代码实时画绘本，接豆包配音 | 动态绘本 | [dgnewlive.com](https://dgnewlive.com/github/hand-drawn-storybook-animation-skill) | 剧本三轮打磨再拆分镜的工作流、代码实时绘制线稿晕染与翻页转场 | — |
| [insp-083](insp-083-cocoloop-six-frame-sheet/) | Cocoloop 实测：六帧精灵表加本地切片拼 GIF | 多类型 | [Cocoloop](https://news.cocoloop.cn/en/2026/11/chatgpt-gif-six-frame-sheet/) | 3×2 六帧精灵表加本地切片拼 GIF 的保底路线、六帧规格参考 | — |
| [insp-084](insp-084-opusly-chatgpt-gif-guide/) | Opusly：ChatGPT 做 GIF 全流程，精灵表优先法 | 多类型 | [Opusly](https://www.opusly.ai/blog/how-to-make-a-gif-in-chatgpt) | 复杂动作先要精灵表、再转 GIF 的分支判断、故障排查清单 | — |
| [insp-085](insp-085-supermaker-images-25-sprite-to-gif/) | SuperMaker：GPT Images 2.5 精灵表转 GIF 的两种路线 | 多类型 | [SuperMaker](https://supermaker.ai/blog/how-to-turn-gpt-images-25-sprite-sheets-into-animated-gifs/) | 精灵表转视频模型与切帧拼 GIF 的双路线、Sunburst 与 Flare 分工 | — |
| [insp-086](insp-086-futurepedia-product-photo-loop-ad/) | Futurepedia：单张产品照变循环广告 GIF 的定格动画法 | 动态海报 | [Futurepedia](https://newsletter.futurepedia.io/p/chatgpt-can-now-make-gifs-from-your-photos-11-13-2026) | 只动一个局部的定格动画构图、同一主体换背景批量出多版 | — |
| [insp-087](insp-087-agent-workshop-loop-prompt/) | The Agent Workshop：ChatGPT 直出 GIF 与循环提示词技巧 | 微信表情包 | [YouTube](https://www.youtube.com/watch?v=Kkg3KESwb0s) | 按顺序列动作的翻页书式提示词结构、末帧接回首帧的循环锁定写法 | — |
| [insp-088](insp-088-zzo-ai-gif-generator/) | zzo.ai：GPT Image 2.6 直出 GIF 工具，4/6/9 帧与按帧计价实测 | 微信表情包 | [zzo.ai](https://zzo.ai/ai-gif-generator) | 4/6/9 帧、每帧 200ms 的帧数搭配、一个主体加一个回到起点的动作的提示词结构、按帧计价的成本估算思路 | — |
| [insp-089](insp-089-cvy-gpt-image-26-gif-guide/) | CVY.AI：GPT Image 2.6 GIF 实测，Flare 与 Sunburst 对比 | 微信表情包 | [CVY.AI](https://cvy.ai/blog/gpt-image-2-6-gif) | Flare 与 Sunburst 按用途选型、主体加动作加回起点加纯白底加固定机位的提示词结构、GIF 模式限制清单 | — |
| [insp-090](insp-090-pwz-gpt-image-26-gif-guide/) | pwz.com：GPT Image 2.6 GIF 实用指南，含动态文字 GIF | 多类型 | [pwz.com](https://www.pwz.com/blog/gpt-image-2-6-ai-gif-guide) | 按输入类型分流的工作流表、动态文字 GIF 的做法、无缝循环检查思路 | — |
| [insp-091](insp-091-sharkly-chatgpt-gif-free/) | Sharkly：免费账号实测 ChatGPT Images 2.6 做 GIF | 微信表情包 | [Sharkly](https://sharkly.ai/blog/make-gifs-chatgpt-images-2-6-free/) | 真 GIF 文件验收写法、8 帧 1.28 秒循环的实测参数、播放速度可调的用法 | — |
| [insp-092](insp-092-laozhang-chatgpt-gif-guide/) | 老张博客：ChatGPT 做 GIF 的五要素提示词公式与 API 成本实测 | 微信表情包 | [blog.laozhang.ai](https://blog.laozhang.ai/en/posts/how-to-make-a-gif-in-chatgpt) | 五要素提示词公式、9-16 帧选帧法则、GIF API 默认 9 帧乘 200ms | — |
| [insp-093](insp-093-aiagentslibrary-gif-prompts/) | AI Agents Library：100 条 ChatGPT GIF 提示词，分 10 类 | 微信表情包 | [aiagentslibrary.com](https://www.aiagentslibrary.com/blog/chatgpt-gif-prompts/) | 按场景分类组织提示词库、主体加唯一动作加固定项加回首帧的公式、四段式结构 | — |
| [insp-094](insp-094-runcomfy-animatediff-comfyui/) | RunComfy：ComfyUI 里用 AnimateDiff 做动画的完整教程 | 多类型 | [RunComfy](https://www.runcomfy.com/tutorials/how-to-use-animatediff-to-create-ai-animations-in-comfyui) | V3 与 SDXL 与 V2 运动模块对比、Prompt Travel 调度写法、MotionLoRA 八种运镜 | — |
| [insp-095](insp-095-holo-card-studio/) | Holo Card Studio：双图光栅翻转卡与镭射闪卡 Skill | 光栅变画卡 | [GitHub](https://github.com/EverettFish/holo-card-studio) | 双图光栅工作流：先生成 A 图再由 A 编辑出 B 图、身份锁定与对齐检查、分 Z 轴视差构图 | — |
| [insp-096](insp-096-ai-cartoon-storybook-generator/) | AI Cartoon Generator：角色一致的插画故事书生成器 | 动态绘本 | [AI Cartoon Generator](https://aicartoongenerator.io/ai-storybook-generator) | 角色一致性锁定再逐页生成的分镜工作流、逐页可编辑与页级旁白再合成动画 | — |
| [insp-097](insp-097-fairygen-child-drawing-story-video/) | FairyGen：只用一张儿童手绘角色生成多镜头故事视频 | 动态绘本 | [arXiv](https://export.arxiv.org/pdf/2506.21272) | MLLM 生成结构化分镜、角色建模与背景解耦、两阶段运动定制适配器 | — |
| [insp-098](insp-098-glowsig-animated-email-signature/) | GlowSig：带动态横幅的免费邮件签名生成器 | 动态签名 | [GlowSig](https://glowsig.com/) | 首帧必须自成完整设计的规则、动态横幅只在签名页播放的取舍、一键复制邮件安全 HTML | — |
| [insp-099](insp-099-letsmeme-ai-meme-gif/) | LetsMeme：AI 模板匹配加文案生成的免费表情包工具 | 微信表情包 | [Product Hunt](https://www.producthunt.com/p/letsmeme/letsmeme) | AI 模板匹配加文案生成加拖拽编辑的组合流程、多语言描述输入、带文字真动态 GIF 导出 | — |
| [insp-100](insp-100-hera-motion-graphics-launch/) | Hera：用 AI 动态图形做发布视频与 GIF 循环缩略图 | 动态海报 | [Hera](https://hera.video/blog/ai-motion-graphics-for-product-hunt-launch) | 先讲清产品再读标语的构图、结尾可循环品牌帧作 GIF 缩略图、成套工作流 | — |
| [insp-101](insp-101-airmore-best-ai-gif-generators/) | Airmore：2026 年 5 款 AI GIF 生成器横评 | 多类型 | [Airmore](https://airmore.ai/ai-review/best-ai-gif-generators) | 按输入类型分流推荐的横评组织、Moxion 的 GIF 专属控制、Rewind.ai 极简提示词优先工作流 | — |
| [insp-102](insp-102-stickman-animation/) | stickman-animation：手绘定格风火柴人动画工具加 Claude Skill | 多类型 | [GitHub](https://github.com/ittahad/stickman-animation) | 用代码画循环 GIF 的做法、白线黑底火柴人讲流程的极简叙事、场景配方文件组织 | — |
| [insp-103](insp-103-pxl-pixel-code-gif/) | pxl：像素画即代码，写脚本出精灵表与动画 GIF | 多类型 | [GitHub](https://github.com/uilianks/pxl) | 帧等于基础精灵加补丁的动画组织、strips 加 JSON tags 加 GIF 的导出结构、从参考 GIF 反推像素结构 | — |
| [insp-104](insp-104-sprite-forge/) | sprite-forge：像素图切干净精灵、做新姿势与动画的工具加 Skill | 多类型 | [GitHub](https://github.com/isabellagreco1997/sprite-forge) | 抠图、找原生像素网格、量化调色板的三步流程、视角与轮廓与接缝与时间的质检清单 | — |
| [insp-105](insp-105-qwen-asset-studio/) | qwen-asset-studio：本地批量生成 2D 游戏素材，JSON 驱动 | 多类型 | [GitHub](https://github.com/Jaro1910/qwen-asset-studio) | JSON 提示词文件驱动批量生成、可复跑跳过已完成、动画条加自动抠图 | — |
| [insp-106](insp-106-anicraft-2d-animation/) | anicraft：纯 Rust 开源 2D 动画工具，兼容 Adobe Animate | 多类型 | [GitHub](https://github.com/soof-golan/anicraft) | 时间轴动画转 GIF 的结构、导出 GIF 与 MP4 与 PNG 序列与精灵表的分流、MCP 接口形态 | — |
| [insp-107](insp-107-slack-gif-creator/) | slack-gif-creator：为 Slack 优化的动画 GIF 制作 Skill | 多类型 | [OpenDesign](https://open-design.ai/skills/slack-gif-creator/) | 小尺寸 GIF 规格表：尺寸、体积、时长、帧率、色数、两遍调色板压缩、可组合动画原语 | — |
| [insp-108](insp-108-agent-sprite-forge/) | agent-sprite-forge：从提示词生成精灵表、透明帧与动画 GIF 的 Skill | 多类型 | [GitHub](https://github.amrom.workers.dev/0x0funky/agent-sprite-forge.git) | 先审定 master still 再批量出动作的主流程、确定性脚本做抠像与配准与循环的后处理 | — |
| [insp-109](insp-109-make-gif-two-pass-palette/) | make-gif Skill：视频转高质量 GIF 的两遍调色板工作流 | 多类型 | [TypingMind](https://www.typingmind.com/skills/gupsammy-make-gif) | 两遍调色板工作流、视频源 GIF 的通用收尾规范 | — |
| [insp-110](insp-110-recursive-gif-with-wan/) | recursive-gif-with-wan：Qwen-Image 加 Wan 图生视频复现递归梗 GIF | 多类型 | [GitHub Gist](https://gist.github.com/bezo97/e54813eeb01933242ed51163abd14a0d) | 先生图定文字首帧、再图生视频续运动的分工、文字加循环 GIF 的可复现路线 | — |
| [insp-111](insp-111-stickerpix-agent-kit/) | StickerPix Agent Kit：让 coding agent 设计贴纸表并驱动打印裁切 | 多类型 | [GitHub Gist](https://gist.github.com/pedramamini/913f981bc1087bc87d0eb8ddd14765d9) | 贴纸表排版规格、本地人像抠像、名字逐字母拼写防拼错的提示词技巧 | — |
| [insp-112](insp-112-animate-procedural-animation/) | animate：给 AI coding agent 的程序化动画 Skill，7 种内置风格 | 多类型 | [GitHub](https://github.com/authrain-cloud-abdullahformuli/animate) | 7 种风格插件化的组织、故事语法与时间控制与渲染器分离、像素风真分辨率绘制 | — |
| [insp-113](insp-113-animatediff-diffusers-docs/) | AnimateDiff 官方文档：diffusers 四条管线与 export_to_gif | 多类型 | [Hugging Face](https://huggingface.co/docs/diffusers/api/pipelines/animatediff.md) | MotionAdapter 注入时间注意力的原理、16 帧与 1024 档规格、export_to_gif 标准出口 | — |
| [insp-114](insp-114-huggingface-gpt-image-26-explained/) | Hugging Face：解析 GPT Image 2.6 原生 GIF 的原理与三条路线 | 多类型 | [Hugging Face Blog](https://huggingface.co/blog/a2aprotocol/gpt-image-26-explained-how-an-image-model-creates) | 循环时长等于帧数乘帧延迟的换算、三条路线对比、帧数上下限与权限要求的验收依据 | — |
| [insp-115](insp-115-gifbook-studio/) | GifBook Studio：手绘翻页书式 GIF 动画应用 | 多类型 | [Product Hunt](https://www.hunted.space/dashboard/gifbook-studio) | 手绘逐帧加洋葱皮的动画组织、三图层与每帧时长参数、分享 GIF 与打印翻页书的双交付 | — |
| [insp-116](insp-116-gif-labs/) | GIF Labs：浏览器本地 GIF 工作室加 AI 循环 GIF 生成 | 多类型 | [Product Hunt](https://webmail.hunted.space/dashboard/gif-labs) | 浏览器本地处理不上传的工具形态、视频转 GIF 与图片拼动画与剪辑一体、多格式导出对照 | — |
| [insp-117](insp-117-text-to-gif-shipyard/) | Text to GIF：文字直出 2-16 帧 GIF，含多平台贴纸工坊 | 微信表情包 | [Shipyard](https://shipyardhq.dev/products/text-to-gif) | 2-16 帧与帧时长可调的参数设计、五种输出格式组织、多平台贴纸工坊分包思路 | — |
| [insp-118](insp-118-vocus-chatgpt-gif-tutorial/) | 方格子：ChatGPT GIF 制作教学，6 格往返动作提示词 | 微信表情包 | [方格子](https://vocus.cc/article/6afc07eafd89780001194c7e) | 原图、一点点变化、回到原图的往返动作结构、6 格每格 0.12 秒的参数、动作词可替换的模板写法 | — |
| [insp-119](insp-119-eufymake-lenticular-printing/) | eufyMake：家里做光栅印刷，翻转、动画与 3D 效果指南 | 光栅变画卡 | [eufyMake](https://www.eufymake.com/blogs/printing-guides/lenticular-printing) | 翻转与动画与 3D 三种光栅效果分类、动画效果 15-20 帧交错的帧数思路、按观看距离选 LPI | — |
| [insp-120](insp-120-contra-lenticular-card-threejs/) | Contra：Webflow 加 Three.js 做鼠标驱动的光栅卡效果 | 光栅变画卡 | [Contra](https://contra.com/p/N33lNPUO-lenticular-card-effect-or-webflow-threejs-and-gsap) | 鼠标位置映射混合变量的翻面思路、两张纹理按视角阈值切换、GSAP 尘埃转场衔接 | — |
| [insp-121](insp-121-91zhibo-seedream-sticker/) | 91直播：Seedream 5.5 先锁角色再做四格循环表情包 | 微信表情包 | [91直播](https://91zhibo.net/articles/tool_tip_2026-11-12-ayi-ainotes.html) | 角色设定表做法、从聊天记录找选题缺口、四宫格一次画齐防闪烁、文案拆四帧动作表 | — |
| [insp-122](insp-122-homaclass-wechat-sticker-business/) | 河马工作室：一套表情包的长尾生意，AI 做微信表情包全流程拆解 | 微信表情包 | [河馬創作工作室](https://homaclass.com/%E4%B8%97%E5%A5%97%E8%A1%A8%E6%83%85%E5%8C%85%E7%9A%84%E9%95%B7%E5%B0%BE%E7%94%9F%E6%84%8F%EF%BC%9Aai%E6%99%82%E4%BB%A3%E5%81%9A%E5%BE%AE%E4%BF%A1%E8%A1%A8%E6%83%85%E5%8C%85%EF%BC%8C%E5%BE%9E%E8%A3%BD/) | 角色设定图三视图加标准表情锁定一致性、多做一倍候选的筛选法、7 天上手路线组织 | — |
| [insp-123](insp-123-juejin-images-26-gif-guide/) | 掘金：ChatGPT Image 2.6 直接生成 GIF 表情包实测 | 微信表情包 | [掘金](https://juejin.cn/post/7704455397478891555) | 官方示例拆解写法、Sunburst 与 Flare 选型、complexity 与 quality 参数说明、GIF 输出接口区别提醒 | — |
| [insp-124](insp-124-maplefeather-ai-gif-routes/) | MapleFeather：ChatGPT、Canva、Grok 三条 AI 动图路线怎么选 | 多类型 | [MapleFeather](https://maplefeather.com/article/ai-gif-chatgpt-canva-grok-guide-2026) | 按用途选工具的决策表、Canva 免费版 GIF 上限规格、跨平台发布坑点清单 | — |
| [insp-125](insp-125-nextoriginweb-images-26-gif/) | 编程导航：GPT Images 2.6 一键生成 GIF 动图首发实测 | 微信表情包 | [编程导航](https://nextoriginweb.codefather.cn/post/2118243160973983745) | 微信聊天记录 GIF 的做法、精灵图机制揭示、逐帧改台词与调速的用法 | — |
| [insp-126](insp-126-trae-bao-sticker-skill/) | TRAE 宝表情包生成 Skill：MIT 开源，四种基础风格加两种彩蛋 | 微信表情包 | [TRAE 社区](https://forum.trae.cn/t/topic/464129) | 风格预设加批量成套加文章插图复用的 Skill 结构、Python 中文合成流程、基础风格加彩蛋风格的成套规划 | — |
| [insp-127](insp-127-cuiqingcai-ace-data-sticker-pack/) | 静觅：用 Ace Data Cloud Studio 做一套微信动态表情包 | 微信表情包 | [静觅博客](https://cuiqingcai.com/4936306.html) | 九宫格选稿定角色的工作流、Agent 对话式全流程、微信横幅 750x400 的规格 | — |
| [insp-128](insp-128-youmind-wechat-sticker-publishing/) | YouMind：微信表情包制作与上架助手 Skill，分步确认式 | 微信表情包 | [YouMind](https://youmind.com/zh-TW/skills/wechat-sticker-publishing-generator-aFNisEIuhRhy85) | 一梗一套的玩法、分步确认防跑偏的流程设计、横幅与封面与图标与赞赏图一次备齐的交付组织 | — |
| [insp-129](insp-129-minimax-gif-sticker-maker/) | MiniMax 官方 gif-sticker-maker Skill：照片转 4 张盲盒风动态贴纸 | 微信表情包 | [GitHub](https://github.com/MiniMax-AI/skills/tree/main/skills/gif-sticker-maker) | 三段式流水线拆分：生图、图生视频、转 GIF、固定 4 情绪加文案对照表的成套规划、盲盒 3D 风格的造型规范写法 | — |
| [insp-130](insp-130-spritesheet-to-gif/) | spritesheet-to-gif：精灵图一键按行列转 GIF 的开源网页工具 | 多类型 | [GitHub](https://github.com/collidingScopes/spritesheet-to-gif) | 行列、帧时长、边距三参数的合成界面、图集到 GIF 最后一公里的工具形态 | — |
| [insp-131](insp-131-varg-gpt-image-2-6-model-guide/) | vargHQ 的 GPT Image 2.6 模型指南 Skill：Flare 与 Sunburst 分工 | 多类型 | [Skills Directory](https://www.skillsdirectory.com/skills/varghq-gpt-image-2-6) | Flare 求快、Sunburst 求稳的选型分工、16 帧上限等硬约束清单、海报、明信片、分镜表等可迁移的构图配方类型 | — |
| [insp-132](insp-132-animatediff-repo/) | AnimateDiff：给文生图模型插运动模块的开源动画框架 | 多类型 | [GitHub](https://github.com/guoyww/AnimateDiff) | 运动模块即插即用的思路、MotionLoRA 低成本适配新动作、提示词加负提示词加帧数的参数结构 | — |
| [insp-133](insp-133-felo-ai-gif-generator/) | Felo AI GIF 生成器：一句话出短循环 GIF 的极简工具 | 多类型 | [Felo AI](https://felo.ai/tools/ai-gif-generator) | 一个瞬间、一句话输入的极简交互、循环接缝与帧数体积的四项质检清单、短循环、无音频的产品定位写法 | — |
| [insp-134](insp-134-foxlab-cnblogs-images-26-gif-test/) | 博客园 foxlab 实测：GPT Image 2.6 的 GIF 帧数与时长边界 | 多类型 | [博客园](https://www.cnblogs.com/foxlab/p/23593779) | 帧数与时长参数的设置方法、纯色背景加小动作最稳的适用场景判断、帧间抖动的规避思路 | — |
| [insp-135](insp-135-dong-gif-prompt-templates/) | 懂AI：8 个出图提示词模板，六格序列帧的模块化写法 | 微信表情包 | [懂AI](https://dong.xs91.com/archives/13015.html) | 提示词的模块化结构：方括号替换位、六格序列帧的四句硬约束写法、局部重绘只改一格的迭代思路 | — |
| [insp-136](insp-136-aiproducthub-sticker-prompt-guide/) | AI 产品库：表情包提示词五段式骨架与六类模板 | 微信表情包 | [AI 产品库](https://aiproducthub.cn/zt/75426.html) | 五段式提示词骨架、按情绪场景分类的模板组织方式、中文长提示词模型的选型经验 | — |
| [insp-137](insp-137-picassoia-free-ai-gif-generator/) | PicassoIA：免费 AI GIF 生成器，Hotshot XL / Wan / Seedance 三路线 | 多类型 | [PicassoIA 博客](https://blog.picassoia.com/ai-gif-generator-free-make-gifs-from-images-or-text) | 文生 GIF、图生视频、首尾同帧三路线分工、首尾同帧做无缝循环、GIF 的 256 色与文件体积约束下的参数取舍 | — |
| [insp-138](insp-138-kavel-best-free-ai-gif-generators/) | Kavel：2026 年 12 款免费 AI GIF 生成器横评 | 多类型 | [Kavel 博客](https://www.kavel.ai/blog/best-free-ai-gif-generators-2026) | 原生 GIF 的循环稳定性逻辑、免费额度对照表的收录维度、一句话加一个动作的提示词结构 | — |
| [insp-139](insp-139-postermywall-ai-gif/) | PosterMyWall AI：现成海报改动画 GIF 的对话式做法 | 动态海报 | [PosterMyWall 官方帮助中心](https://support.postermywall.com/hc/en-us/articles/49406950230029-What-can-you-do-with-PosterMyWall-AI) | 海报元素的动效拆分：标题闪烁、局部动、生成后调速、对话式改稿流程 | — |
| [insp-140](insp-140-atomm-raster-card-generator/) | Atomm 光栅卡生成器：翻转、动画、3D 四种效果的打印卡 | 光栅变画卡 | [Atomm](https://www.atomm.com/creativetools/raster-card-generator/) | 四种效果的产品化分类、同一组照片出多种卡的复用思路、打印对齐规格 | — |
| [insp-141](insp-141-my-storybook-ai-devpost/) | My Storybook AI：孩子照片变多画风动画故事书 | 动态绘本 | [Devpost](https://devpost.com/software/bb-3mzyo0) | 照片转角色的 5 画风并行做法、故事梗概三风格、分场景配音加字幕烧录的合成管线 | — |
| [insp-142](insp-142-pixel-art-gif-generator-app/) | Pixel Art GIF Maker：GPT Image 2.6 一次出 16 帧像素风 GIF | 多类型 | [gifgenerator.app](https://gifgenerator.app/pixel-art-gif) | 16 帧加变帧率调循环时长、一个地点加一个重复动作加像素风格的提示结构、像素风不等于可编辑精灵表的边界说明 | — |
| [insp-143](insp-143-pixwit-pixel-art-video/) | Pixwit：浏览器本地视频转像素风 GIF，20 种复古调色板 | 多类型 | [Pixwit](https://www.pixwit.ai/tools/pixel-art-video) | 复古调色板库、像素尺寸、抖动、帧率的参数组合、GIF 作为社交分享导出格式的定位 | — |
| [insp-144](insp-144-videotogifcreator-palette-gif/) | Video to GIF Creator：ffmpeg 两遍调色板转 GIF 工具 | 多类型 | [usefulweb.site](https://videotogifcreator.usefulweb.site/) | 两段式调色板方法、帧率、宽度、抖动的画质与体积权衡、API 化的思路 | — |
| [insp-145](insp-145-dreamina-seedance-gif/) | Dreamina：Seedance 图生视频再转 GIF 的实测数据 | 多类型 | [Dreamina（CapCut）](https://dreamina.capcut.com/ai-video/ai-animated-gif-tools) | 图生视频加离线转 GIF 的两段流程、抽帧数与尺寸的取舍、多工具路线对照 | — |
| [insp-146](insp-146-iconking-lottie-to-gif-email/) | IconKing：Lottie 转邮件 GIF，rlottie 加 gifski 的实现 | 动态签名 | [IconKing](https://www.iconking.net/tools/lottie-to-gif-for-email) | rlottie 加 gifski 的技术组合、矢量动效转 GIF 的通用出口、邮件 GIF 的兼容性思路 | — |
| [insp-147](insp-147-plugmatrix-animated-signatures/) | PlugMatrix Signatures：6 秒循环的动态邮件签名做法 | 动态签名 | [PlugMatrix](https://www.plugmatrix.io/products/signatures/) | 6 秒循环加 500KB 以内的签名规格、首帧必须自成设计的兜底规则、按客户端列兼容表的做法 | — |
| [insp-148](insp-148-gemini-omni-video-to-sticker-gif/) | gemini-omni-video-to-sticker-gif Skill：视频转贴纸 GIF 的坐标校准工作流 | 微信表情包 | [GitHub](https://github.com/cafe3310/public-agent-skills/tree/main/skills_parked/gemini-omni-video-to-sticker-gif) | 坐标校准再裁剪的工作流、视频片段裁剪缩放变速做 GIF 的参数思路 | — |
| [insp-149](insp-149-spritix-sprite-generator/) | Spritix：一张角色图出 Idle/Walk/Run/Jump/Attack 五动作精灵表 | 多类型 | [dev.to](https://dev.to/chenxer97/ai-sprite-generator-turn-2d-character-art-into-game-ready-animations-3mjm) | 同一张参考图锚定全部动作防走样的做法、逐动作设帧数、格子尺寸、裁剪再导出的参数组织、浏览器里修循环不花生成点数的流程 | — |
| [insp-150](insp-150-spritey-ai-sprite-workbench/) | Spritey AI：先审身份锚点再出动作的精灵图生产台 | 多类型 | [Spritey AI](https://www.spritey.ai/) | 身份锚点审定一次再扩动作的流程、被拒动作留记录、只导出通过帧的评审纪律、API 与 Skill 暴露任务进度与下载的 agent 调用形态 | — |
| [insp-151](insp-151-wobbleimage-motion-mask-gif/) | WobbleImage：涂一块会动的区域，静图变弹簧感 GIF 循环 | 多类型 | [Product Hunt](https://www.producthunt.com/products/wobbleimage?launch=wobbleimage) | 涂遮罩定动区、其余锁死的做法、六种弹簧动效的动效词表、浏览器本地处理不上传的工具形态 | — |
| [insp-152](insp-152-magichour-ai-gif-generator/) | Magic Hour：文字直出 GIF，每天 3 次免费免注册 | 多类型 | [Magic Hour](https://magichour.ai/products/ai-gif-generator) | 一句话一个动作的极简输入、每天免费 3 次、无水印的试玩门槛、按张计价的 API 形态 | — |
| [insp-153](insp-153-aigifmaker-meme-gif-guide/) | Nerdbot 横评：aigifmaker.ai 文字一字不差的梗图 GIF | 多类型 | [Nerdbot](https://nerdbot.com/2026/11/12/the-best-meme-gif-generators-in-2026-how-fandoms-make-reaction-gifs-nobody-has-seen-yet/) | 文案逐字拼对的验收标准、按梗图版式点名要格式的做法、反应 GIF 加 Discord 表情加名字 GIF 的成套组织 | — |
| [insp-154](insp-154-wan22-comfyui-perfect-loop/) | Wan 2.2：ComfyUI 首尾同帧做无缝循环动画 | 多类型 | [YouTube](https://youtubetotranscript.com/transcript?v=a2Of6_Wcd74) | 首尾同帧加删最后一帧的无缝循环做法、只写循环类动作的提示词取向、RIFE 补帧加颜色匹配的收尾流程、低显存 GGUF 替代路线 | — |
| [insp-155](insp-155-seedance-extend-seamless-loop/) | Seedance 2.5：末帧接续加首尾归位做无缝循环 | 多类型 | [Seedance](https://www.seedance.tv/blog/how-to-extend-video-seedance-2-5) | 末帧当下一段起点的接续流程、循环等于结尾回到开头构图的定义、只在必要时用短交叉淡化的收尾取舍 | — |
| [insp-156](insp-156-xtool-lenticular-printing-guide/) | xTool：家用打印机做光栅卡，测 LPI 再印 | 光栅变画卡 | [xTool 支持中心](https://support.xtool.com/article/3802) | 先实测 LPI 再印的校准流程、按效果分档的帧数取舍：换图/动画/3D、光栅条纹须与 X 轴平行的对齐要求 | — |
| [insp-157](insp-157-fotomaster-fmx-lenticular-photos/) | FotoMaster FMX：活动现场照片直出 4×6 光栅卡 | 光栅变画卡 | [FotoMaster 支持中心](https://support.fotomaster.com/articles/how-to-create-and-print-lenticular-photos-in-fmx-for-windows) | 两到三张同场照片合成光栅卡的产品形态、源图必须各不相同的约束、预览播原始帧动画的验收做法 | — |
| [insp-158](insp-158-unyson-motion-gallery-lenticular/) | Unyson+ Motion Gallery：CSS 3D 光栅卡组件，指针驱动翻面 | 光栅变画卡 | [Unyson+](https://docs.unysonplus.com/animation-engine/motion-gallery) | 指针位置映射翻面变量的交互写法、脊纹数与倾斜角度的参数范围、CSS 3D 与 WebGL 两档实现的取舍 | — |
| [insp-159](insp-159-prismposter-cinemagraph-guide/) | PrismPoster：只动一个元素的 Cinemagraph 指南 | 动态海报 | [PrismPoster](https://www.prismposter.com/blog/how-to-make-a-cinemagraph-with-ai) | 只动一个元素、其余锁死的构图原则、倒放接续与首尾交叉淡化两种循环办法、按渠道选 MP4 或 GIF 的导出取舍 | — |
| [insp-160](insp-160-genlive-cinemagraph-maker/) | GenLive Studio：浏览器里做 Cinemagraph 活照片 | 动态海报 | [GenLive Studio](https://genlive.app/studio/templates/cinemagraph-maker) | 点名动什么的模板交互、锁定机位做无缝循环的提示词取向、模型可换的模板组织 | — |
| [insp-161](insp-161-deep-nostalgia-cinemagraph-maker/) | Deep Nostalgia：点名一个细节让静照活起来 | 动态海报 | [Deep Nostalgia AI](https://deep-nostalgia-ai.com/cinemagraph-maker) | 只动一个细节的提示词写法、Subtle Movement 与 Gentle Sway 两个预设、先说明接缝可能不完美的预期管理 | — |
| [insp-162](insp-162-figma-weave-cinemagraph-workflow/) | Figma Weave：图生视频加遮罩节点的 Cinemagraph 工作流 | 动态海报 | [Figma](https://www.figma.com/resource-library/how-to-make-a-cinemagraph/) | 生成动效与遮罩定区拆节点的串联思路、Mask by Text 自动取动区的办法、一次搭好、换照片复用的工作流组织 | — |
| [insp-163](insp-163-aituts-animatediff-vid2vid/) | Aituts：ComfyUI AnimateDiff 视频转视频四套工作流 | 多类型 | [Aituts](https://aituts.com/animatediff-comfyui/) | 视频转视频加 ControlNet 的路线、提示词调度随时间换提示词的做法、closed_loop 与 pingpong 的循环参数 | — |
| [insp-164](insp-164-efficiency-nodes-animatediff-gif/) | Efficiency Nodes：AnimateDiff 脚本节点的循环与 GIF 参数 | 多类型 | [DeepWiki](https://deepwiki.com/jags111/efficiency-nodes-comfyui/2.3.5-animatediff) | batch_size 即帧数的参数对应、loop_count、closed_loop、pingpong 的循环参数组合、format 直出 GIF 的节点出口 | — |
| [insp-165](insp-165-10100-wechat-sticker-monetization/) | 大数跨境：AI 表情包变现案例，24 张成套与打赏数据 | 微信表情包 | [大数跨境](https://www.10100.com/article/154913507) | 批量出 50-100 张再筛的选稿做法、每组 24 张、16 静加 8 动的成套规格、抠图加字加动效包装的后期顺序、按下载与打赏数据复盘迭代的运营闭环 | — |
| [insp-166](insp-166-hailuo-image-to-video-stable/) | Hailuo 图生视频：先稳住主体再谈动效 | 多类型 | [Hailuo AI](https://www.ai-hailuo.com/blog/hailuo-image-to-video/) | 只写动效的提示词纪律、主体漂移时降强度、重挂参考图的纠偏步骤、先短片段验证再延长的流程 | — |
| [insp-167](insp-167-dreamdrive-image-to-video-guides/) | Dreamdrive：38 篇图生视频指南合集，含循环设置 | 多类型 | [Dreamdrive](https://www.dreamdrive.ai/learn/topics/image-to-video/) | 按模型分栏、按任务取用的合集组织、首尾帧支持情况的跨平台对照、抽象材质动效的循环设置写法 | — |
| [insp-168](insp-168-convertify4u-how-to-make-a-gif/) | Convertify4u：浏览器 GIF 工作室，正播倒播往返播参数 | 多类型 | [Convertify4u](https://www.convertify4u.com/how-to-make-a-gif) | 往返播做短动作无缝循环的做法、延迟与质量的默认值与取值范围、先默认出一张、再一次只调一个参数的调试纪律 | — |

### 已落地（2）

| 编号 | 标题 | 类型 | 出处 | 借什么 | 审批 / 落地 |
|---|---|---|---|---|---|
| [insp-001](insp-001-gif-factory/) | gif-factory 的动图类型清单 | 多类型 | [GitHub](https://github.com/WoYun520/gif-factory) | 类型划分、光栅卡规格、动态海报规格、像素和黏土画风 | 向明 2026-11-18；→ trials/2026-11-18-gif-factory-styles |
| [insp-002](insp-002-snail-cat-memes/) | 橘猫 P 人类五官的照片梗图 | 微信表情包 | 未知 | 照片梗图形式、P图五官笑点 | 向明 2026-11-18；→ trials/2026-11-18-snail-cat-remix |

<!-- board:end -->
