# 笔记

## 它是怎么做的

这篇是机制拆解，不是教程。核心论点是 Images 2.6 把“想多少”（complexity）和“画多精”（quality）拆成了两个独立参数：complexity 管出图前的规划量（low/medium/high，默认 high），quality 管渲染质量。编辑类任务适合低 complexity + 高 quality，构图复杂的海报适合高 complexity 先排布局。

GIF 部分：设 output_format=gif，frame_count 2–64（默认 9）、frame_duration_ms 20–2000ms（默认 200），各帧共享整次请求的像素预算。作者推测 GIF 很可能是在一张大画布上把所有帧一起规划、一起画再切帧，一致性来自“同一张图里的元素本来就一致”——这只是推测，没有官方确认。另附系统卡数据：GIF 审核召回率 77.7%。

## 我们怎么用

借“规划与渲染分开调”的参数思路：以后做复杂表情包先高 complexity 定布局草稿、再低 complexity + 高 quality 精修；做 GIF 时按像素预算反推帧数与单帧尺寸的取舍。帧图集一次规划的推测如果成立，提示词里写“一张 3×2 精灵图、固定机位”就是在帮模型做规划，值得在案例里验证。

## 截图

截图、录屏放在本目录的 `media/`，只留在本地，不入库。
