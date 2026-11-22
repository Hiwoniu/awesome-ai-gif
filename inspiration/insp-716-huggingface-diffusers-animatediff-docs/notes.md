# 笔记

## 它是怎么做的

Diffusers 官方 AnimateDiff 文档：底模型管画风，MotionAdapter 运动模块管动作，两者组合出视频帧序列；最后用 export_to_gif 把帧序列直接存成 GIF。

## 我们怎么用

借官方的调用写法搭本地 AnimateDiff 出 GIF 的最小链路：运动模块与底模型分离，换风格只换底模型；export_to_gif 可作导出环节的参考实现。

## 截图

截图、录屏放在本目录的 `media/`，只留在本地，不入库。
