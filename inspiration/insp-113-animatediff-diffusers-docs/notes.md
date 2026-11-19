# 笔记

## 它是怎么做的

官方文档：MotionAdapter 在 UNet 各层注入时间注意力，四条管线是 AnimateDiffPipeline、ControlNet、SDXL、V2V；规格是 16 帧、1024x1024 档；export_to_gif 是标准出口。

## 我们怎么用

当作静态角色转短循环的对照基线：先按官方管线跑通 16 帧循环，再对比 GPT Image 路线的效果与成本。选型时按四条管线对照表选。

## 截图

截图、录屏放在本目录的 `media/`，只留在本地，不入库。
