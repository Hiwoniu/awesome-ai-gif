# 笔记

## 它是怎么做的

ComfyUI AnimateDiff 文生视频课：帧数取 8–32 帧、帧率 8fps，beta_schedule 选 sqrt_linear 让运动更平滑，最后用 Video Combine 节点把帧序列合成为 GIF 或 MP4。

## 我们怎么用

借 8–32 帧、8fps 的参数取向与 beta_schedule 的选择经验，做 AnimateDiff 路线的 GIF 时先按这个范围起测；Video Combine 出 GIF 的收尾流程可作本地 ComfyUI 工作流的参考。

## 截图

截图、录屏放在本目录的 `media/`，只留在本地，不入库。
