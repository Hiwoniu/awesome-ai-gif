# AnimateQR：首个可扫的动态二维码生成框架（NeurIPS 2025）

- 来源：NeurIPS 2025 论文 · mulns 等 · https://papers.neurips.cc/paper_files/paper/2025/file/0524ee0a5f7b9f68eebe0b1740479491-Paper-Conference.pdf
- 类型：posters · 状态：pending 待审

## 它是怎么做的

用分层亮度引导与渐进时空控制生成每帧都可扫的动态二维码，解码成功率 96%。
“码本身逐帧变化、每帧都可扫”是动态二维码最难的构图点，方法可借鉴到海报/名片类 GIF。

## 我们怎么用

只借类型、手法、构图、提示词结构，换原创角色重做；不照搬对方画面、角色、文案、提示词原文。具体可借的点：

- 分层亮度引导（HLG）保可扫性的思路
- 渐进时空控制：逐帧分配控制强度
- 解码成功率 96% vs 基线 56% 的验收写法

## 截图说明

未下载对方图片/GIF/视频；演示见来源链接：https://papers.neurips.cc/paper_files/paper/2025/file/0524ee0a5f7b9f68eebe0b1740479491-Paper-Conference.pdf

## 风险提示

论文方法较重，落地需简化
许可/出处：论文与代码 github.com/mulns/AnimateQR，许可未注明，只借方法
