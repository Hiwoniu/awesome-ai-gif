# 笔记

## 它是怎么做的

这篇指南对照三条本地路线：AnimateDiff 给 SD 检查点加运动模块；SVD 单张静帧出 14/25 帧短片，不用文字提示，用 motion bucket ID（0 静止、约 127 中等、255 剧烈）控制运动幅度；CogVideoX 是文生/图生视频 DiT，默认 49 帧 6 秒；并给出 ComfyUI 接法与显存门槛。

## 我们怎么用

借它的选型表：我们本地出 GIF 也可以按任务选模型——单图加动作用 SVD、长提示词用 CogVideoX、已有 SD 检查点用 AnimateDiff；motion bucket ID 的幅度控制法可以直接借用。

## 截图

截图、录屏放在本目录的 `media/`，只留在本地，不入库。
