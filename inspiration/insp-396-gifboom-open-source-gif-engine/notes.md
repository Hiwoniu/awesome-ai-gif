# 笔记

## 它是怎么做的

一个 Python 包同时提供三样东西：命令行、MCP 服务器和一份 Skill 说明；agent 按 Skill 里的指引自己去搜 GIF、转格式、下载，视频和 GIF 互转走 FFmpeg。装法是 pip/pipx，一句话就能装好。

## 我们怎么用

借它的双接入形态：我们做 GIF 相关 Skill 时，同时给 CLI 用法和 MCP 用法两种入口；FFmpeg 互转链路可作为导出环节的参考实现。

## 截图

截图、录屏放在本目录的 `media/`，只留在本地，不入库。
