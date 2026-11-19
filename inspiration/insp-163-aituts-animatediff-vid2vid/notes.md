# 笔记

## 它是怎么做的

教程给四套 ComfyUI 工作流文件，核心是文生视频与视频转视频（vid2vid），后者可接 ControlNet 做风格化重绘，提示词调度可以在生成过程中换提示词。关键参数：context_length 16 效果较好、context_overlap 默认 4、closed_loop 尝试做无限循环（vid2vid 下不生效）、loop_count 设循环次数（0 为无限）、format 可切 GIF/MP4/WebM、pingpong 正播再倒播。运动模块要另下载，v1.5 v2 版较常用。

## 我们怎么用

借视频转视频的路线：已有视频素材时，用 AnimateDiff 重绘成循环 GIF，比从零文生更稳；提示词调度可以按动作分段写，适合多段小动作的 GIF。

## 截图

截图、录屏放在本目录的 `media/`，只留在本地，不入库。