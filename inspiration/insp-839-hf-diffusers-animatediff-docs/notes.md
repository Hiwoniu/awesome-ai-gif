# 笔记

## 它是怎么做的

官方文档介绍 AnimateDiff 框架：把新初始化的运动建模模块插入冻结的文生图模型，在视频片段上训练以蒸馏运动先验；训练好后注入该模块，同一底座衍生的个性化模型都能变成文本驱动的动画模型。文档给出 AnimateDiffPipeline、ControlNet 与 SparseCtrl 管线、可用检查点列表，以及用 MotionAdapter.from_pretrained 加载 guoyww 运动适配器、再用 export_to_gif 导出 animation.gif 的完整代码示例。

## 我们怎么用

本地文生 GIF 路线以此为基准实现：先按文档跑通最小管线，再换自己的底模型与运动模块；借运动模块与底模型分离的思路，不照搬文档的示例提示词。

## 截图

截图、录屏放在本目录的 `media/`，只留在本地，不入库。
