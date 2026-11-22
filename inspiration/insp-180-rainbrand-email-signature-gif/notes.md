# Rainbrand：用品牌简报做动态邮件签名 GIF（MCP Skill）

- 来源：Rainbrand Docs · Rainbrand · https://docs.rainbrand.com/use-cases/email-signature-gif
- 类型：signatures · 状态：pending 待审

## 它是怎么做的

通过 MCP 接入的 Skill：编码 Agent 按品牌 Brief 做 600×200、约 11 秒循环的签名横幅，Headless Chrome 逐帧截图+FFmpeg 编码，成品 200–310 KB。
“品牌资产→Brief→HTML 动画→逐帧渲染 GIF”的签名工作流；“文字用遮罩滑入、不用淡入淡出（GIF 会糊）”的渲染经验可直接复用。

## 我们怎么用

只借类型、手法、构图、提示词结构，换原创角色重做；不照搬对方画面、角色、文案、提示词原文。具体可借的点：

- 品牌资产→Brief→HTML 动画→逐帧渲染 GIF 的工作流
- 文字遮罩滑入、不用淡入淡出的 GIF 渲染经验
- 首帧即成品静帧的兜底做法

## 截图说明

未下载对方图片/GIF/视频；演示见来源链接：https://docs.rainbrand.com/use-cases/email-signature-gif

## 风险提示

附 Ramp、Supabase 概念示例
许可/出处：官方文档，引用注明出处
