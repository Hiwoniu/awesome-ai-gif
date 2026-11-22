# 笔记

## 它是怎么做的

Skill 包共 64 个 Agent Skill，动效制作方向；loop-cover：封面图做成 896×640、180 帧@20fps 无缝循环 GIF，含接缝测量；animated-chart：循环动态图表；编码用 ffmpeg、无 dithering；验收指标有接缝（seam）与动幅（excursion）量化值；规则包括首帧即成品图、只动一个元素。

## 我们怎么用

动态海报/封面照搬 loop-cover 参数做试做：896×640、180 帧@20fps、无 dithering 编码；验收时量化接缝与动幅，而不是凭肉眼感觉。

## 截图

截图、录屏放在本目录的 `media/`，只留在本地，不入库。
