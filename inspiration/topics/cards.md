# 光栅卡、全息卡与贺卡（22 条）

能借到什么：两态对齐、翻转节奏、共享调色板、节日题材。

用法只有一种：借手法，换成原创角色重做。[规则](../README.md) · [全部主题](README.md)

| 编号 | 标题 | 出处 | 借什么 |
|---|---|---|---|
| [insp-062](../insp-062-tryvitrine-lenticular-card/) | Vitrine 光栅卡组件：两张图竖条交错、指针驱动翻面 | [Vitrine](https://www.tryvitrine.dev/components/lenticular-card) | 6px 竖条纹交错遮罩的光栅实现、指针位置映射过渡变量、中间段平滑过渡的交互写法、同卡两面（例如白天与夜晚同一海报）的构图思路 |
| [insp-063](../insp-063-recharm-flip-transition/) | Recharm：卡片翻面转场，0.8 秒 3D 翻转的逐帧脚本 | [Recharm](https://www.recharm.com/effects/flip-transition) | 0.8 秒翻面的帧参数：24 帧、三次缓动、绕竖轴 180 度、透视投影与边缘变暗的逐帧写法、A 面翻到 90 度后换 B 面的衔接思路 |
| [insp-073](../insp-073-atomm-lenticular-card-generator/) | Atomm 光栅卡生成器：激光切割滑动动画卡 | [Atomm](https://www.atomm.com/creativetools/lenticular-card-generator) | 条纹栅栏滑动动画替代透镜片的卡片结构、帧数越多越平滑但画面越暗的权衡关系、狭缝宽 0.6–1mm 适配多数激光切割机的参数、高对比简洁图形才读得清的选图原则 |
| [insp-095](../insp-095-holo-card-studio/) | Holo Card Studio：双图光栅翻转卡与镭射闪卡 Skill | [GitHub](https://github.com/EverettFish/holo-card-studio) | 双图光栅工作流：先生成 A 图再由 A 编辑出 B 图、身份锁定与对齐检查的做法、全息路线按 Z 轴分层做视差的构图思路、尺寸与 alpha 密度校验的验收方法 |
| [insp-1048](../insp-1048-upgpts-chatgpt-image-26-guide/) | UPGPTs：ChatGPT Image 2.6 新玩法，参考图生成 GIF 表情包、贺卡和电商动图 | [UPGPTs](https://upgpts.com/tutorials/chatgpt/chatgpt-image-2.6-guide) | 定妆图工作流、五段式模板、节日贺卡换场景模板、电商动图三种：360°旋转、开箱、细节 |
| [insp-1070](../insp-1070-holoizer-holographic-gif-cards/) | holoizer：一张图出 48 帧全息 GIF 卡的 Python 工具 | [PyPI](https://pypi.org/project/holoizer/) | 48 帧透视循环规格、共享 256 色 GIF 调色板、全息卡批量管线、光栅卡动效结构 |
| [insp-119](../insp-119-eufymake-lenticular-printing/) | eufyMake：家里做光栅印刷，翻转、动画与 3D 效果指南 | [eufyMake](https://www.eufymake.com/blogs/printing-guides/lenticular-printing) | 翻转、动画、3D 三种光栅效果的分类、动画效果用 15-20 帧交错的帧数思路、按观看距离选透镜 LPI 的方法、先锁 LPI 与效果、再准备对齐帧的工作流 |
| [insp-120](../insp-120-contra-lenticular-card-threejs/) | Contra：Webflow 加 Three.js 做鼠标驱动的光栅卡效果 | [Contra](https://contra.com/p/N33lNPUO-lenticular-card-effect-or-webflow-threejs-and-gsap) | 鼠标位置映射混合变量的光栅翻面思路、两张纹理按视角阈值切换的做法、GSAP 尘埃转场的衔接写法 |
| [insp-140](../insp-140-atomm-raster-card-generator/) | Atomm 光栅卡生成器：翻转、动画、3D 四种效果的打印卡 | [Atomm](https://www.atomm.com/creativetools/raster-card-generator/) | 四种效果的产品化分类、同一组照片出多种卡的复用思路、打印对齐规格 |
| [insp-156](../insp-156-xtool-lenticular-printing-guide/) | xTool：家用打印机做光栅卡，测 LPI 再印 | [xTool 支持中心](https://support.xtool.com/article/3802) | 先实测 LPI 再印的校准流程、按效果分档的帧数取舍：换图/动画/3D、光栅条纹须与 X 轴平行的对齐要求 |
| [insp-157](../insp-157-fotomaster-fmx-lenticular-photos/) | FotoMaster FMX：活动现场照片直出 4×6 光栅卡 | [FotoMaster 支持中心](https://support.fotomaster.com/articles/how-to-create-and-print-lenticular-photos-in-fmx-for-windows) | 两到三张同场照片合成光栅卡的产品形态、源图必须各不相同的约束、预览播原始帧动画的验收做法 |
| [insp-158](../insp-158-unyson-motion-gallery-lenticular/) | Unyson+ Motion Gallery：CSS 3D 光栅卡组件，指针驱动翻面 | [Unyson+](https://docs.unysonplus.com/animation-engine/motion-gallery) | 指针位置映射翻面变量的交互写法、脊纹数与倾斜角度的参数范围、CSS 3D 与 WebGL 两档实现的取舍 |
| [insp-170](../insp-170-gvm-animated-greeting-cards/) | 远见杂志：ChatGPT 免费做动态贺卡全教学 | [遠見雜誌](https://www.gvm.com.tw/article/134582) | “场景/主体/细节/限制”四段式提示词结构、节日动态贺卡：固定背景+局部动效的构图、免费版可用性的核实写法 |
| [insp-270](../insp-270-xtool-o1-lenticular-cards-course/) | xTool O1 光栅卡打印教程：局部变画 | [xTool Support Center](https://support.xtool.com/academy/course?id=416&from=academy_home_view_all) | 局部变画（只变一部分、其余不变）、光栅纹路与打印机 X 轴平行对齐、双线检测对齐法、节日卡/邀请卡等落地场景 |
| [insp-310](../insp-310-4over4-lenticular-print-guide/) | 4OVER4：光栅印刷全流程指南（LPI 与帧数取舍） | [4OVER4](https://www.4over4.com/guide/how-to-make-lenticular-prints) | 翻转与动画两种效果的帧准备方法 |
| [insp-327](../insp-327-ruic-card-skill-holo-card/) | RuiC-card-skill：AI 生成 3D 全息收藏卡的 Skill | [SkillsLLM](https://skillsllm.com/skill/ruic-card-skill) | 按深度分层的卡面结构、视差来自图层深度差、而非把彩虹效果 baked 进图的原则 |
| [insp-353](../insp-353-cmu-lenticular-animation-course/) | CMU 课程：光栅动画作业（10 帧循环规格） | [卡内基梅隆大学课程页](https://ems.andrew.cmu.edu/2014/assignments/project-1/lenticular-animation/index.html) | 10 帧循环的规格、光栅打印的帧间重影提醒、GIF 与实体卡同源产出的思路 |
| [insp-393](../insp-393-laphotoparty-lenticular-print-from-gif/) | LA Photo Party：从 GIF 做光栅印刷 | [LA Photo Party](https://support.laphotoparty.com/support/solutions/articles/5000858776-create-a-lenticular-print-from-a-gif) | GIF 转光栅配置法、三种光栅做法、LPI 选型 |
| [insp-394](../insp-394-darkroomsoftware-lenticular-printing/) | Darkroom Booth：光栅印刷上手指南 | [Darkroom Software](https://darkroomsoftware.com/lenticular-printing-in-darkroom-booth/) | 线下直出流程、光栅设置、GIF 与实体卡同源 |
| [insp-399](../insp-399-stoatworks-lenticular-physics-guide/) | Stoatworks Lenticular：光栅卡翻转效果的物理模拟指南 | [Stoatworks Labs](https://stoatworks-labs.com/guides/lenticular.pdf) | 双图交错加倾斜翻转的物理模型、翻转边缘扫过卡面的时序、透镜间距失配导致摩尔纹与重影的成因、OpenFX/Resolume 落地形态 |
| [insp-608](../insp-608-facebook-shannon-whitaker-birthday-gif/) | Facebook：Shannon Whitaker，生日 GIF：照片 → ChatGPT Q 版娃娃 → Canva 1080×1080 加闪烁动画 | [Facebook](https://www.facebook.com/reel/1507761804000231/) | 照片到 Q 版娃娃到 Canva 排版的三段式、1080×1080 方形尺寸与品牌色、文字的排版要素、Canva 动画效果（Flicker）做最后动效、生日场景文案可换中文节日场景 |
| [insp-753](../insp-753-ig-flora-holographic-sticker-workflow/) | Instagram @asia.does.uxui：Flora.ai 全息贴纸 7 步工作流 | [Instagram](https://www.instagram.com/reel/DfpR_NfK--1) | 草图→矢量→批量同风格的贴纸工作流 |
