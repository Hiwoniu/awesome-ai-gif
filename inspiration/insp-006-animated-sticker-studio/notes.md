# 笔记

## 它是怎么做的

- 流水线：plan → reference → atlases → cut → build → look → fix → deliver，用 manifest 描述整套。
- 平台预设包含通用 GIF、微信（240x240、≤500KB）、Telegram、LINE、Discord、Slack、WhatsApp，各自尺寸/帧数/时长/体积不同。
- 案例饭团猫 24 张已提交微信审核（2026-11-05），微信导出平均 368KB。

## 我们怎么用

- 我们阶段 0 先只做微信，多平台是阶段 2 的事；先借它的预设表结构，给 specs 留多平台扩展位。
- 对照它的 look/fix 环节，看我们的视觉自查是否缺项。

## 截图

截图、录屏放在本目录的 `media/`，只留在本地，不入库。
