# 笔记

## 它是怎么做的

官方文档讲 LCM 与 AnimateDiff 的结合：LCM-LoRA 让每帧只需 4–8 步推理，大幅加速动画生成；示例代码含 MotionAdapter、LCMScheduler 与 zoom-in 运动 LoRA，export_to_gif 直接出 GIF。

## 我们怎么用

借它的加速路线：本地批量出动画先上 LCM-LoRA 把每帧推理步数压到 4–8 步，再叠运动 LoRA 控动作；代码骨架可以直接拿来跑通第一版。

## 截图

截图、录屏放在本目录的 `media/`，只留在本地，不入库。
