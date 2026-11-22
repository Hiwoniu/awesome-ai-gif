# 笔记

## 它是怎么做的

文档给出标准调用流程：加载基础模型后挂 MotionAdapter，再按需叠加 Motion LoRA 控制动作风格，最后用 export_to_gif 把帧序列导出为 GIF；参数围绕帧数、步数与运动强度展开。

## 我们怎么用

作为本地 AnimateDiff 路线的权威对照：搭工作流时按文档核对 MotionAdapter 与 LoRA 的加载顺序，export_to_gif 的导出参数作为我们的 GIF 导出基准。

## 截图

截图、录屏放在本目录的 `media/`，只留在本地，不入库。
