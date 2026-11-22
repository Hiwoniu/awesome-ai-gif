# 笔记

## 它是怎么做的

Loopchain 给 ComfyUI 加了一组循环节点：Loop 节点把一串节点包起来重复执行，EmptyLatentImageLoop 生成循环用的潜空间，Image/Latent Storage Import/Export 节点在循环内外存取帧，拼起来就是一条自动跑多帧的链路。

## 我们怎么用

借它的循环链组织法：批量出表情包时把单帧流程包进循环，帧间只换动作参数；循环海报也可以照这个结构搭自动出帧的链路。

## 截图

截图、录屏放在本目录的 `media/`，只留在本地，不入库。
