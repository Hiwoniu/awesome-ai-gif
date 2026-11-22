# 笔记

## 它是怎么做的

这个分支在 AnimateDiff 基础上加了 Evolved 采样与滑动上下文窗口：长动画按段生成、上下文滑动衔接，突破原来 16 帧的限制；BatchPromptSchedule 支持 prompt travel，让提示词随帧变化；最后用 VideoHelperSuite 把帧序列合成 GIF。

## 我们怎么用

借它的分段生成思路：长循环先分段、再滑动衔接，避免一次生成过长导致崩坏；循环类表情包用 Looped Context 锁定首尾衔接。

## 截图

截图、录屏放在本目录的 `media/`，只留在本地，不入库。
