# 笔记

## 它是怎么做的

Skill 的做法是把用户照片转成 4 张 Funko Pop/盲盒风动画 GIF 贴纸，默认 hi、laugh、cry、love 四个动作，底部加黑字白边 1–3 词 caption；提示词模板用 {action}/{caption} 填空，caption 按用户语言查 captions.md 匹配；仓库含 SKILL.md 全文、image-prompt-template.txt 与 captions.md，MIT 协议。

## 我们怎么用

借它的映射表结构：我们做表情包也先定动作清单再配文案表，一张角色图对应多个动作加 caption；模板填空写法可以照搬进自己的 Skill。

## 截图

截图、录屏放在本目录的 `media/`，只留在本地，不入库。
