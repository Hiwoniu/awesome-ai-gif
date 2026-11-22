# 笔记

## 它是怎么做的

这是 Stable Diffusion WebUI 的 AnimateDiff 扩展（continue-revolution）的使用指南，经 DeepWiki 镜像页核实。核心是一套围绕运动模块的参数体系：选运动模块、设帧数与 FPS、上下文批量（batch/stride/overlap）控制长片段；闭环有四档——N 不循环、R-P 倒放不重复枢轴帧、R+P 倒放重复枢轴帧、A 追加倒放做无缝循环，指南建议循环动画用 R-P。输出支持 GIF/MP4/WebP/WebM/PNG 多格式同出；另有 FreeInit 降闪烁、FILM 插帧提顺滑、img2img 的首尾帧 latent 控制、Prompt Travel 跨帧换提示词、ControlNet 视频转视频。

## 我们怎么用

池里 AnimateDiff 此前多是 ComfyUI 路线，这条补的是 WebUI 用户的路径。借三点：闭环三模式的选型（先试 R-P）、FreeInit + FILM 的组合降闪烁思路、首尾帧 latent 控制做循环收尾。注意这是本地 SD 1.5/SDXL 的老路线，出图风格与我们现在主力的 Images 2.6 直出 GIF 不同，适合作为“已有 SD 工作流时怎么出循环 GIF”的参考，不必为它另搭环境。

## 截图

截图、录屏放在本目录的 `media/`，只留在本地，不入库。
