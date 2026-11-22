# 笔记

## 它是怎么做的

指南列出 GPT Image 2.6 API 的 flare/sunburst 两个模型 ID、GIF 输出三字段（output_format=gif、frame_count、frame_duration_ms）、SVG 输出与 complexity 参数，另附测试清单（含 frame_count=17 应记录返回的边界测试）与 Python/cURL 请求示例。

## 我们怎么用

借它的参数表当接口依据：批量出 GIF 前先按表定帧数与帧时长，再跑一遍边界测试（比如 frame_count=17 的返回），避免上线后报错。

## 截图

截图、录屏放在本目录的 `media/`，只留在本地，不入库。
