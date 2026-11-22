# 笔记

## 它是怎么做的

这篇综述先把定位讲清：AnimateDiff 只是一个运动模块，不是完整视频模型；然后对比了 8 个官方运动 LoRA 与 Lightning 蒸馏版的取舍，并把 AnimateDiff、AnimateDiff-Lightning、ComfyUI-Evolved 与 A1111 扩展之间的关系一次梳理清楚，还附了许可证提醒。

## 我们怎么用

借它的运动模块选型表，做本地动图管线选型时对照；短循环定位在 16 帧约 2 秒，可以作为我们 AnimateDiff 路线的起测参数。

## 截图

截图、录屏放在本目录的 `media/`，只留在本地，不入库。
