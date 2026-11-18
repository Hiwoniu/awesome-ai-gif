# awesome-ai-gif

AI 生成 GIF 的精选提示词库：可复用的 GIF 案例 + Skill + 可视化站。

> 定位：GIF 版 awesome-gpt-image。微信表情包是第一期，不是全部。
> 引擎：GPT Image 2.6（2026-11-04 发布）起步，案例结构不绑死单一模型。

## 当前状态

阶段 0：骨架已建好，正在做第一套微信表情包。脚本目前只用合成测试图验证过，还没有真实案例。排期见 [仓库规划.md](仓库规划.md)。

<!-- cases:start -->
案例总数：**0**（已上架 0）

| 系列 | 案例数 | 索引 |
|---|---|---|
| 微信表情包 | 0 | [查看](cases/wechat-stickers/README.md) |
<!-- cases:end -->

## 两种用法

**只要提示词**：打开 [prompts/](prompts/) 里的公式，换掉角色和动作，复制到 ChatGPT 出图。

| 公式 | 用途 |
|---|---|
| [角色定稿](prompts/character-sheet.md) | 第一步，定下整套的角色参考图 |
| [4×4 姿势图集](prompts/atlas-4x4.md) | 一次出 16 个姿势，再由脚本加点头、弹跳、摇摆 |
| [六帧序列图](prompts/sprite-sheet-6-frame.md) | 一个真实动作的 6 帧，合成循环 GIF |

**要整条流水线**：用 [微信表情包 Skill](skills/wechat-sticker/SKILL.md)。把 `skills/wechat-sticker/` 整个文件夹拷到 `~/.claude/skills/`（Claude Code）或 Codex 的 skills 目录，然后说“把这个角色做成一套微信表情包”。没有 API Key 也能用：Skill 给提示词，你在 ChatGPT 出图后把图交回来，它负责切图、合成、压体积和机检。

依赖只有 Python 3 和 Pillow。

## 怎么做一套（混合打法）

1. 出一张角色定稿图，之后整套都用它当参考。
2. 用 4×4 图集一次定下 16 个姿势，逐格验货。
3. 切图，给每格加轻动效，得到一套 GIF。
4. 挑几张需要真实动作的，用六帧序列图重做。
5. 做封面、图标、横幅，填含义词和专辑文案。
6. 机检，FAIL 清零后提交微信表情开放平台。

完整步骤见 [上架指南](docs/wechat-publishing.md)。

## 目录

- `prompts/`：通用提示词公式
- `skills/wechat-sticker/`：微信表情包 Skill，自带脚本和规格配置
- `cases/`：案例库，按“系列 / 分组 / 案例”组织；`cases/index.json` 是全量索引
- `tools/`：仓库维护脚本
- `docs/`：[上架指南](docs/wechat-publishing.md)、[被拒原因](docs/rejections.md)、[成本实测表](docs/cost-log.md)
- `site/`：可视化站（阶段 2，未开始）

## 贡献

只收原创角色，每个案例都要有提示词原文、成品 GIF、成本和验收记录。详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## License

MIT

## 致谢

对标苍何 awesome-gpt-image-2（提示词库三件套结构）；方法论参考 gif-factory（图集轻动效、Skill 组织方式）、ray-sticker-shop（上架流水线）、charmoji-sticker-skill（机检分级与差异哈希）、animated-sticker-studio（多平台规格）。六帧公式的骨架来自 OpenAI《Introducing Images 2.6》。
