# 笔记

## 它是怎么做的

AnimateDiff 长文指南：本地部署（Python 3.10/CUDA 匹配）、ComfyUI 工作流节点接线（Checkpoint→AnimateDiff Loader→KSampler→VAE Decode→Video Combine，帧率 8/12）、ControlNet/IP-Adapter 约束、显存配置表。

## 我们怎么用

借 ComfyUI 里 AnimateDiff 出 GIF 的最小节点链与帧率设置口径；需要本地可控动效时按这条链搭，ControlNet/IP-Adapter 用来约束主体与构图。

## 截图

截图、录屏放在本目录的 `media/`，只留在本地，不入库。
