# 笔记

## 它是怎么做的

节点文档：BlendVideoCombine 把多帧合成为 GIF/WebP，带平滑过渡、预览、loop_count（0=无限循环）。定位是 ComfyUI 里帧到 GIF 的导出节点。

## 我们怎么用

本地工作流的导出环节多一个选择：需要过渡效果时用 BlendVideoCombine，不用时仍走 Video Combine；loop_count 设 0 即无限循环。

## 截图

截图、录屏放在本目录的 `media/`，只留在本地，不入库。
