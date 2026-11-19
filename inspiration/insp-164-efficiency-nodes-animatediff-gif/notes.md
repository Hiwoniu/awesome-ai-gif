# 笔记

## 它是怎么做的

AnimateDiff 在 Efficiency Nodes 里是一个脚本节点，接在 Efficient KSampler 后面，底层用 Kosinkadink 的 AnimateDiff Evolved。参数表：batch_size 即帧数；loop_count 循环次数；format 输出格式（GIF/MP4 等）；pingpong 正播再倒播；closed_loop 做无缝循环。示例工作流用 mm_sd_v15_v2 运动模块、context 长度 12、sqrt_linear 调度、25 步 DDIM 采样，VHS VideoCombine 以 12fps 合成。文档还给了带 HiResFix 的组合示例。

## 我们怎么用

借这张参数表当 ComfyUI 循环 GIF 的检查清单：帧数、循环次数、往返播、闭环、格式五个开关一次确认，再出图。

## 截图

截图、录屏放在本目录的 `media/`，只留在本地，不入库。