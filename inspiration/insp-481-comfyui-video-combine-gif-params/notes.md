# 笔记

## 它是怎么做的

Video Combine 是 VideoHelperSuite 里把帧序列合成输出的节点：format 选 image/gif 就直接出 GIF，loop_count 设 0 为无限循环，还支持 pingpong 往返播放，帧率与尺寸参数都在文档里列清楚了。

## 我们怎么用

借它的参数表当收尾清单：我们用 ComfyUI 出 GIF 时按这张表定循环次数、帧率与是否 pingpong，避免每次凭感觉调。

## 截图

截图、录屏放在本目录的 `media/`，只留在本地，不入库。
