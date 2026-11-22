# 笔记

## 它是怎么做的

工作流把 AnimateDiff 与 Depth、SoftEdge、Lineart、OpenPose 四路 ControlNet 串起来做图生视频，附可下载的工作流文件；收尾用 Video Combine，format 选 image/gif，closed_loop 参数控制首尾闭环。

## 我们怎么用

借它的 ControlNet 串联顺序：需要控姿势或控线稿的动图先按这四路搭，再开 closed_loop 验循环；工作流文件可对照着复刻。

## 截图

截图、录屏放在本目录的 `media/`，只留在本地，不入库。
