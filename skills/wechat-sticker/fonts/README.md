# 字体

`scripts/caption.py` 加字时会先在这个目录里找字体。把可免费商用的中文字体文件（.ttf / .otf / .ttc）放进来即可，文件名保留原名，脚本按文件名认：

| 字体 | 授权 | 风格 |
|---|---|---|
| 得意黑 Smiley Sans | SIL OFL 1.1 | 斜体黑体，活泼，适合表情 |
| 站酷快乐体 ZCOOL KuaiLe | SIL OFL 1.1 | 圆润手写感 |
| 站酷庆科黄油体 ZCOOL QingKe HuangYou | SIL OFL 1.1 | 粗壮醒目 |
| 思源黑体 Source Han Sans / Noto Sans CJK | SIL OFL 1.1 | 规整黑体 |

**已自带**：`SmileySans-Oblique.ttf`（得意黑 v2.0.1，来自 github.com/atelier-anchor/smiley-sans 官方发布，授权全文见 `SmileySans-LICENSE.txt`）。它只收录简体常用字（GB 2312），生僻字会缺；脚本发现缺字会报 WARN，这时换个说法或用 `--font` 换思源黑体。

其他字体请去官方发布页（GitHub 或 Google Fonts），用之前再看一眼授权条款。

这里找不到时，脚本退回系统字体（苹方、华文黑体、微软雅黑等）并报 WARN：系统字体的授权不一定允许商用，只适合练手。
