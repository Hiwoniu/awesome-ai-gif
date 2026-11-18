# 奶牛猫复刻试做（3 张）

日期：2026-11-18。主角：用户自家的黑白奶牛猫（照片 `_work/photo.jpg`）。动作来源：`~/Downloads/wechat_stickers` 里一套商业 3D 吉祥物表情（**仅练手，不可提交微信**）。

## 出图（Codex CLI 0.169，内置 image_gen，共 5 次）

| 次 | 内容 | 输入 | 结果 |
|---|---|---|---|
| 1 | 角色定稿 `character.png` | 照片 + `_work/prompts/character.md` | 一次通过，透明底 |
| 2 | thanks 六帧 | 定稿 + `ref.png` + `gen-prompt.md` | 通过 |
| 3 | dinner 六帧 | 同上 | 通过（耳机、围巾按提示词不沿用） |
| 4 | cover-eyes 六帧 v1 | 同上 | **不合格**：爪子捂的是嘴，眼睛露着（留存为 `new-v1.png`） |
| 5 | cover-eyes 六帧 v2 | 同上 + 动作重点一句（`gen-prompt-v2.md`） | 通过 |

调用方式（提示词走 stdin，因为 `-i` 会吞掉后面的位置参数）：

```sh
echo "<指令>" | codex exec --skip-git-repo-check -s workspace-write -C <试做目录> -i character.png -i ref.png -
```

原始输出在 `~/.codex/generated_images/`，Codex 按指令复制成 `new.png`。日志在 `logs/`。

## 和 Skill 默认流程的差异

- **透明底代替白底**：3D 毛绒风格没有描边，白围兜、白爪贴着白底会被 `--key-white` 一起抠掉。改为让 image_gen 直接出透明底（`transparent_background=true`），`gen-prompt.md` 把背景那行换成透明，合成时不加 `--key-white`。
- **加字**：thanks「谢谢！」顶部逐字、dinner「开饭了」左侧竖排逐字，用 `scripts/caption.py` + 得意黑；cover-eyes 原图无字，不加。

## 结果

3 张 GIF，74–98KB。`check_assets.py`：0 FAIL；首尾 WARN ×3 是原 GIF 本来就是一次性动画（原图 seam 97–100%），沿用即可。

## 待人工确认

- 黑猫放在黑色聊天背景上轮廓偏弱（原套是黄色角色没这问题）。
- cover-eyes v2 嘴边的小白块淡了些。
- thanks 角色缩到 0.8 后鞠躬帧偏小。
