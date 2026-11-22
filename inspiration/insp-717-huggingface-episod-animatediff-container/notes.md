# 笔记

## 它是怎么做的

Tenstorrent 上跑的 AnimateDiff 文生视频服务：输入文字描述，直接出 512×512 的 GIF 循环；支持风格 LoRA 换画风、prompt travel 让提示词随时间渐变、MotionAdapter 控制运动。

## 我们怎么用

借 prompt travel 做渐变类循环的写法（比如颜色、光线随时间慢慢变），换原创角色重做；512×512 可作在线服务出 GIF 的规格参考。

## 截图

截图、录屏放在本目录的 `media/`，只留在本地，不入库。
