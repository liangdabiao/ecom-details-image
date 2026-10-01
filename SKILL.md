---
name: ecom-details-image
description: Create visual concepts, image-generation prompts, and optional AI-generated images for product hero images, marketing creatives, social posts, ads, ecommerce PDP visuals, and general visual design tasks. Use when the user asks for visual strategy, image prompt writing, product/marketing image direction, or direct text-to-image generation with their own OpenAI-compatible API.
---

# ecom-details-image Skill

当用户需要视觉策略、图片 Prompt、商品主图、营销图、社媒图、广告图、电商 PDP 视觉，或要求直接 AI 生图时，使用这个 Skill。

这个 Skill 有两种模式：

1. **Brief / Prompt 模式**：只输出视觉简报和可执行图片 Prompt。
2. **Generate 模式**：当用户明确要求“生图、生成图片、出图、render image”时，先输出最终 Prompt，再调用 `scripts/generate_image.py`。

不要暴露、索要、写入、提交或回显真实 API key。使用者必须通过自己的环境变量配置 API。

---

## 生图配置

直接生图使用 apimart.ai 图像生成接口（GPT-Image-2，异步轮询模式）。优先在 `.claude/skills/ecom-details-image/` 放 `.env`，不要把真实 API key 写进仓库：

```dotenv
IMG_BASE_URL=https://api.apimart.ai/v1
IMG_MODEL=gpt-image-2
IMG_API_KEY=your-api-key
```

脚本也兼容常见别名：`OPENAI_BASE_URL`、`OPENAI_API_BASE`、`OPENAI_IMAGE_MODEL`、`OPENAI_MODEL`、`OPENAI_API_KEY`。

生图脚本：

```bash
python3 scripts/generate_image.py --prompt "clean product hero image..." --size 1:1 --resolution 2k
python3 scripts/generate_image.py --prompt-file prompt.txt --output-dir outputs
python3 scripts/generate_image.py --env-file .env --prompt-file prompt.txt
```

**参考图片**：如果用户提供了产品照片路径，使用 `--image` 参数传入以提升产品一致性。参考图对保证产品外观准确非常有效。

如果缺少任何生图配置，说明需要在 `.env` 里配置什么，并把最终 Prompt 交给用户，方便用户稍后自行运行。

---

## 核心流程

1. 判断视觉任务类型和场景（见下方**场景模板系统**）。
2. 从 `references/templates/` 匹配对应模板，读取 `prompt_template`、`variants`、`category_tips` 作为 Prompt 基础结构。
3. 只收集会实质影响图片结果的缺失信息。
4. 构建视觉简报。
5. 如果任务包含多张图，先建立 **Campaign Style Lock**，锁定整套图的色板、冷暖调、字体、背景、光线、布局和图标风格。
6. 写出可执行图片 Prompt（**保持简洁**，见下方 Prompt 精简原则）；多图任务必须把同一段 Campaign Style Lock 原样放进每张 Prompt。
7. 如果任务是商品图、详情页图或营销图，先做转化驱动力诊断。
8. 如果用户要求电商详情页、PDP、主图堆栈或整套商品图，默认输出 **5 张主图 + 7-9 张详情页图片** 的图片包。
9. 如果用户要求直接出图，调用 `scripts/generate_image.py`；如果用户提供了参考产品图，传入 `--image`。
10. 返回 Prompt、生成文件路径和关键假设。

---

## 最小输入

任何视觉任务都优先确认这些信息：

- 目标：图片要达成什么效果。
- 用途：商品主图、广告图、社媒图、Banner、PDP 模块、缩略图、概念图等。
- 主体：产品、人物、场景、物体或抽象概念。
- 受众和使用语境。
- 风格：真实摄影、编辑部风格、高级棚拍、UGC、3D 渲染、插画等。
- 构图、比例、平台尺寸。
- 是否需要图片内文字。
- 负面约束：避免 logo、避免文字、避免杂乱、避免医疗承诺等。

如果缺少非关键字段，明确假设后继续，不要无谓阻塞。

---

## 通用图片 Prompt 结构

默认用英文写 Prompt，除非用户要求其他语言。

Prompt 按这个结构组织：

1. Campaign Style Lock，多图任务必填且每张图完全一致。
2. 主体和场景。
3. 图片目的和情绪意图。
4. 构图、镜头和取景。
5. 光线、颜色、材质和纹理。
6. 风格和真实感等级。
7. 平台限制和画幅比例。
8. 图片内文字处理。
9. 负面约束。

Prompt 要足够具体，可以直接执行；也不要过度规定无关细节，避免和用户目标冲突。

---

## GPT-Image-2 Prompt 铁律（必须遵守）

以下规则来自大量实战验证，每条 Prompt 都必须逐条检查。

### 1. 颜色用 hex 码，不用形容词

"白底"出来是淡灰，"金色"出来有 8 种金。必须写 hex：

- 白底 → `#FFFFFF`
- 深灰文字 → `#2D2D2D`
- 金色强调 → `#D4AF37`
- 浅米色背景 → `#F5F1E8`
- 深绿背景 → `#1A3A2E`

### 2. 产品占比必须数字化

不同图型的产品占比黄金区间：

| 图型 | 产品占比 | 说明 |
|---|---|---|
| 白底主图 | 35-40% | 太小显廉价，太大显拥挤 |
| 卖点副图 | 25-30% | 左图右文布局，产品在左 |
| 场景氛围图 | 20-25% | 场景图不是产品图，氛围才是主角 |
| 信息流广告 | 40% | 环境干扰多，产品要更突出 |
| 搜索广告 | 45% | 搜索图比信息流再大一点 |
| SKU 多规格卡 | 60-70%（整体） | 多个产品横排 |

### 3. 留白必须显式声明

不写留白，AI 一定把画面填满。每张图必须写：

- 白底主图 / 卖点副图 / 广告图：`留白至少 45%`
- 场景氛围图：`留白至少 50%`
- 详情页长图：`留白 50%+`

### 4. 否定清单不能省

每条 Prompt 结尾必须加负面约束，写具体禁止项而不是笼统的"不要多余的"：

```
不要添加：道具、手、水印、假 logo、额外文字、装饰元素、渐变背景
```

### 5. 平台预留空间

国内电商主图必须预留：

- `顶部中央 200×100 区域留空（平台价格叠加区）` — 不写产品会把整个画面填满
- `左上角 200×100 像素区域完全留白` — logo 区域（如需要）

### 6. 3 层信息架构

电商图内文字必须遵循：

- 核心承诺 ≤15 字（主标题）
- 关键证据 2-3 个（图标 + 短标签）
- 行动指令 ≤8 字（CTA 按钮）

### 7. 批量出图优于反复调参

一次 `--resolution 2k` 出图，让 CTR 数据选风格，不要凭审美反复调参。

---

## Prompt 精简原则

**GPT-Image-2 在结构清晰、信息具体的 Prompt 下表现最佳。**

- 只包含核心信息，去除冗余约束和重复描述。
- 自然语言优于关键词堆砌。
- 明确描述材质纹理（磨砂玻璃、拉丝金属、哑光饰面、丝绸光泽）。
- 始终包含光线方向和质量，场景图指定色温（如 `色温 5500K`）。
- 不要在一个 Prompt 里塞入太多场景、风格、情绪要求。
- 如果用户提供了参考产品图，传入 `--image` 比文字描述更有效。
- 中文字用「」中文引号包裹，渲染准确率明显高于英文引号或无引号。
- 复杂笔画的中文字（赢、鬱、餮等）尽量换成简单同义字，95% 准确率不是 100%。

---

## 场景模板系统

`references/templates/` 目录包含 25 个场景模板，每个模板提供 `prompt_template`、`variants`（风格变体）、`category_tips`（品类建议）、`examples` 和 `anti_ai_tips`。

### 模板匹配表

| 触发词 | 模板文件 |
|---|---|
| 白底图, 主图, hero image, packshot | `01-hero-image.json` |
| 场景图, 生活图, lifestyle | `02-lifestyle-scene.json` |
| 平铺图, flat lay, 俯拍 | `03-flat-lay.json` |
| 细节图, 微距, macro, 特写 | `04-detail-macro.json` |
| 海报, poster, banner, 促销 | `05-poster-banner.json` |
| 社交媒体, 小红书, Instagram, TikTok | `06-social-media.json` |
| UGC, 买家秀, GRWM | `07-ugc-style.json` |
| 模特, model, 人物展示 | `08-model-showcase.json` |
| 对比, before after, 前后 | `09-before-after.json` |
| 包装, packaging, 礼盒 | `10-packaging.json` |
| 信息图, A+, 详情页 | `11-infographic.json` |
| 创意, 概念, creative | `12-creative-concept.json` |
| 尺寸, 规格, 使用步骤 | `13-size-spec.json` |
| 套装, 组合, bundle | `14-multi-product.json` |
| 直播, livestream | `15-livestream.json` |
| 试穿, 融入, try on | `16-try-on-virtual.json` |
| 拆解图, 爆炸图, exploded view | `17-exploded-view.json` |
| 隐形模特, ghost mannequin, 3D服装 | `18-ghost-mannequin.json` |
| 多角度, 网格, grid, 多色展示 | `19-multi-angle-grid.json` |
| 杂志, 封面, editorial, magazine | `20-magazine-editorial.json` |
| 季节, 四季, campaign, 春夏秋冬 | `21-seasonal-campaign.json` |
| 奢华, 氛围, 烟雾, luxury, atmospheric | `22-luxury-atmospherics.json` |
| 设备模型, 界面, mockup, SaaS, APP | `23-device-mockup.json` |
| 店铺, 门面, 空间, storefront, 实体店 | `24-storefront.json` |
| 运动, 健身, sports, fitness | `25-sports-campaign.json` |

无匹配 → 默认 `01-hero-image.json`。**只读取匹配到的模板文件**，不要一次性加载全部。

### 模板使用方式

1. 取 `prompt_template` 作为 Prompt 基础结构。
2. 用用户产品信息替换 `{variables}`。
3. 用户指定风格变体 → 应用 `variants.<name>.overrides`。
4. 已知产品品类 → 应用 `category_tips.<category>`。
5. 简化：只保留有值的字段，输出简洁的自然语言 Prompt。

### 风格变体速查

每个模板通常包含 3-4 个风格变体，常用变体类型：
- **luxury** — 高端奢华（Rembrandt 光线、金色点缀、深色渐变）
- **minimal** — 极简现代（纯白/浅色、干净线条、大留白）
- **fresh** — 清新自然（明亮自然光、柔和粉彩、通透感）
- **tech** — 科技感（戏剧性侧光、深色背景、金属质感）

---

## Anti-AI 技巧（UGC / 直播 / 社媒场景）

生成 UGC、直播或社媒内容时，必须遵循以下规则让图片看起来真实：

- 指定具体手机型号：`iPhone 14 Pro`、`iPhone 15 Pro`。
- 添加可见瑕疵：毛孔、轻微噪点、暖色偏移、不完美构图。
- 使用真实感语言：`NOT professional photography`、`NOT AI-generated look`。
- 展示真实环境：略微凌乱、真实物品、水渍、用过的毛巾。
- 参考胶片色调：`Kodak Portra 400 color feel`。
- 明确声明：`NOT retouched, NOT smoothed`。
- 避免典型 AI 词汇：不用 `perfect`、`flawless`、`stunning`、`hyper-realistic`。
- 各模板中如有 `anti_ai_tips` 字段，生成对应场景时必须遵循。

---

## 整套图片风格一致性规则

当生成主图 + 详情页、PDP 图片包、广告组图、社媒组图或任何多张图片时，必须先定义一个 **Campaign Style Lock**。这是整套图的视觉合同，不是灵感描述。

### Campaign Style Lock 必填字段

1. **视觉方向**：例如 premium tech ecommerce、clean household care、warm gift editorial。
2. **固定色板**：限制为 2-3 个主色 + 1 个强调色；写清楚背景色、文字色、强调色，不要每张图重新配色。
3. **冷暖调**：明确 warm / cool / neutral，并要求全套一致。
4. **字体系统**：统一为一种字体风格，例如 modern geometric sans-serif；禁止混用衬线、手写、复古、卡通字体。
5. **背景系统**：统一背景材质、空间和深浅，例如 clean light gray studio background 或 deep navy premium tech background。
6. **光线系统**：统一光源方向、阴影强度、反光质感和氛围。
7. **布局系统**：统一留白、圆角、分栏、标签、编号和信息图组件风格。
8. **图标 / 插画系统**：如果用图标，统一线宽、形状、颜色和复杂度。
9. **产品呈现规则**：产品角度、大小比例、材质表现和是否居中必须稳定。
10. **禁止漂移项**：明确禁止 changing color palette, mixed fonts, inconsistent lighting, random backgrounds, mismatched icon styles。

### 默认 Style Lock 模板

如果用户没有给品牌规范，使用保守统一的电商视觉系统：

```text
Campaign Style Lock: consistent premium ecommerce visual system across the entire image set; fixed palette of clean off-white background, deep charcoal text, one product-matched accent color, and one soft secondary accent; neutral-cool studio lighting; modern geometric sans-serif headline placeholders only; consistent rounded rectangular info labels; consistent thin-line icon style; clean high-end product photography mixed with minimal infographic elements; stable product scale and placement; generous whitespace; no color palette changes, no mixed fonts, no random backgrounds, no inconsistent lighting, no mismatched icon styles.
```

### 多图 Prompt 强制规则

- 每张图 Prompt 的第一段必须是同一段 Campaign Style Lock，不能改写、缩短或换同义词。
- 单张图只能改变：画面目的、主体动作、局部构图和短文案。
- 单张图不能改变：色板、冷暖调、字体风格、背景系统、光线系统、图标风格和信息标签样式。
- 如果用户要求重生其中一张图，必须复用原来的 Campaign Style Lock。
- 如果已生成图片风格不一致，优先重写 Prompt 包，而不是逐张随意补描述。

---

## 商品和营销转化流程

商品主图、电商图片、广告图和 PDP 视觉不要从固定模板开始，要先判断转化驱动力。

选择一个主要驱动力：

### A. 视觉驱动型

适用于购买决策依赖外观、风格匹配、光洁度、质感、前后对比或礼品属性的产品。

重点：

- 一眼抓住产品吸引力。
- 质感、细节、工艺和质量信号。
- 使用场景和视觉层级。
- 简短利益点。

### B. 痛点驱动型

适用于买家有明确摩擦、风险、时间损失、不适或反复烦恼的产品。

强制顺序：

1. 痛点挖掘 / 风险触发。
2. 利益 / 解决方案。
3. 信任和证明。
4. 优惠 + CTA。

重点是具体问题、缓解机制、证据和风险逆转。

### C. 情感价值驱动型

适用于购买和身份、信心、归属、地位、关怀、快乐、新奇或冲动相关的产品。

重点：

- 情绪钩子。
- 身份或向往。
- 产品作为实现方式。
- 社交证明和低摩擦行动。

---

## 商品图序列模板

当用户提到“详情页、PDP、Amazon A+、Shopify 商品页、主图堆栈、整套商品图、商品详情图片”时，不要只停留在 5 张主图。必须追加详情页图片序列，并把每一屏都写成可单独生图的 Prompt。

### 视觉驱动主图序列

1. 一眼可懂的视觉主张。
2. 核心功能或质感特写。
3. 使用场景匹配。
4. 普通方案 vs 升级方案对比。
5. 优惠、物流、保障或 CTA 画面。

### 痛点驱动主图序列

1. 问题快照。
2. 解决机制。
3. 利益证明。
4. 信任画面。
5. 优惠 + 紧迫 CTA。

### 情感价值主图序列

1. 情绪场景钩子。
2. 身份 / 价值表达。
3. 产品作为实现方式。
4. 归属、地位或社交信号。
5. 带情绪强化的优惠 + CTA。

---

## 详情页图片序列模板

详情页图片用于移动端纵向浏览，默认每张图独立成屏，尺寸优先使用 `2:3` 或平台指定竖版比例。除非用户明确只要文案，否则每个模块都要输出对应图片 Prompt。

### 通用 PDP 详情页图片序列

1. 首屏承接：延续主图卖点，说明产品为谁解决什么问题。
2. 痛点放大：展示用户当前的不便、损失、风险或反复烦恼。
3. 机制解释：用视觉化结构说明产品如何发挥作用，避免虚构无法证明的数据。
4. 核心利益：把 2-4 个主要利益做成易扫读的信息图。
5. 使用步骤：用 3-4 步说明怎么用，降低理解成本。
6. 场景覆盖：展示典型使用场景、适用对象或使用前后状态。
7. 对比选择：普通方案 vs 本产品，突出可观察差异和体验差异。
8. 信任背书：展示材料、包装、质检、保障、真实评价等已有证据；没有证据就写“proof placeholder”，不要编造认证。
9. FAQ / 风险逆转 / CTA：处理残留、适用范围、售后、组合优惠等临门疑虑。

### 驱动力适配

- 视觉驱动型：增加质感细节、尺寸比例、使用场景和礼品感。
- 痛点驱动型：严格按“问题严重性 → 解决机制 → 利益证明 → 信任 → CTA”推进。
- 情感价值驱动型：增加生活方式、身份表达、社交场景和情绪回报。

### 图片内文字规则

- 详情页图片可以有短文案，但必须短、清楚、适合移动端。
- 每屏主标题建议 3-7 个英文词或 6-12 个中文字。
- 说明性文字用 2-4 个短标签，不要生成大段小字。
- 每一区文字量严格控制：标题 + 副标题 + 小标注不超过 50 个字。
- 中文字用「」中文引号包裹，如「修护屏障」「72h 深层锁水」，渲染准确率更高。
- 指定字体大小：标题 28-48pt，副标题 16-20pt，标注 10-14pt。
- 颜色用 hex 码：深灰标题 `#2D2D2D`，浅灰标注 `#888888`，金色强调 `#D4AF37`。
- 如果模型容易生成乱码，Prompt 中明确要求 “clean layout with short readable headline placeholders, no dense body text”。
- 出图后必须放大 200% 逐字核对中文笔画，复杂字换简单同义字。

### 视觉节奏规则（多图任务）

连续多张图的背景色不能完全一样，否则消费者视觉疲劳。多图任务必须交替使用 2-3 种背景色：

- 白底主图 / 卖点副图：`#FFFFFF`
- 成分解析 / 质地展示：`#F5F1E8`（浅米色）
- 品牌主视觉 / 促销图：品牌深色（如 `#1A3A2E`）

### 多角度镜头规则（多图任务）

**全套图片绝不能全部使用同一个拍摄角度。** AI 生图默认倾向生成正面 3/4 角度，如果不显式指定镜头角度，整套图会看起来千篇一律。多图任务必须在 Prompt 中为每张图分配不同的镜头角度和景别。

#### 角度清单（按用途选择 4-6 种组合）

| 角度 | Prompt 写法 | 适用场景 |
|---|---|---|
| 正面 3/4 | `at a slight 3/4 angle showing full front facade` | 主图、首图 |
| 正上方俯视 | `photographed directly from above at a 90-degree overhead angle` | 展示布局、内部结构、平铺 |
| 侧面 90° | `photographed from a clean 90-degree side profile` | 展示深度、层次、侧面细节 |
| 后侧 45° | `photographed from behind at a 45-degree rear angle` | 展示背面细节、码头、尾部构造 |
| 仰视低角度 | `photographed from a very low angle looking upward` | 英雄镜头、气势感、儿童视角 |
| 高角度俯视 | `photographed from a high 45-degree angle looking down` | 展示顶部、整体规模、桌面视角 |

#### 景别清单（按用途选择 2-3 种组合）

| 景别 | Prompt 写法 | 适用场景 |
|---|---|---|
| 全景 | `full product visible, product occupies 35-40%` | 主图、场景图 |
| 中景 | `showing the [section name] area, product occupies 45-50%` | 功能展示、结构说明 |
| 特写 | `tight zoom on [specific detail], product detail occupies 55-60%` | 材质纹理、工艺细节、按钮/接口 |
| 微距 | `extreme close-up macro shot, shallow depth of field` | 面料编织、接缝工艺、表面纹理 |
| 局部 | `close-up detail shot focusing on [specific part]` | 灯塔信标、大炮、拉链、标签 |

#### 多角度分配原则

1. **主图序列（5 张）**：至少使用 3 种不同角度，其中 1 张必须是特写或微距。
2. **详情页序列（7-9 张）**：至少使用 4 种不同角度，其中 2 张必须是特写/微距。
3. **不能连续 3 张图使用相同角度**，否则消费者视觉疲劳。
4. **全景图不超过整套的 40%**，必须穿插中景、特写和微距增加节奏感。
5. **仰视和俯视各至少 1 张**，打破平视拍摄的单一感。
6. 每张 Prompt 必须显式写明角度关键词（如 `side profile`、`from above`、`low angle`），不要假设模型会自动变换角度。

#### 角度 Prompt 模板

在每张图片 Prompt 的「构图、镜头和取景」段落中，直接嵌入角度描述：

```text
# 俯视图
Bird's eye top-down view. The [product] photographed directly from above at a 90-degree overhead angle, showing the full layout [specific details visible from above]. Deep even lighting from directly above minimizing shadows.

# 侧视图
Side profile view. The [product] photographed from a clean 90-degree side profile, showing [what's visible from side]. Strong side lighting from the left creating dramatic depth.

# 仰视图
Dramatic low-angle hero shot. The [product] photographed from a very low angle looking upward, making [tower/building] appear tall and imposing. Strong upward lighting creating heroic dramatic shadows.

# 微距特写
Extreme close-up macro shot. Tight zoom on the [specific detail], showing [texture/mechanism/individual elements]. Shallow depth of field with the foreground in sharp focus and background slightly blurred. Warm directional side lighting highlighting surface texture.

# 后侧角度
Rear angled view. The [product] photographed from behind at a 45-degree rear angle, revealing [back details not visible from front]. This angle shows construction details not visible from the front.
```

### 详情页信息图结构规则（关键！）

**详情页图片 ≠ 多角度产品照片。** 详情页图片必须是电商信息图格式，包含卖点文案、图标、标签、对比、步骤、信任徽章等信息图元素，产品在不同信息图中展示不同角度。多角度是为信息图服务的展示手段，不是目的。

#### 错误做法（只换角度，没有信息图结构）

```
# 错误：这只是"同一产品换个角度拍"，缺少电商转化元素
Prompt: Side profile view of the product on white background. Product occupies 38%. Whitespace 50%+.
```

#### 正确做法（电商信息图 + 多角度产品展示）

```
# 正确：有标题、卖点图标、标签、信息图布局，产品在其中展示特定角度
E-commerce infographic benefits screen on #FAF7F2 background.
Top headline in #2D2D2D at 28pt reading 「Core Benefits」.
Left side: the product shown from an elevated overhead angle.
Right side: four benefit rows stacked vertically with thin-line icons:
  (1) icon + 「Feature One」 in #7A9E7E
  (2) icon + 「Feature Two」 in #8B6F47
  (3) icon + 「Feature Three」 in #7A9E7E
  (4) icon + 「Feature Four」 in #8B6F47
Clean two-column layout. Product occupies 35%. Whitespace 48%+.
```

#### 详情页每屏必须包含的信息图元素

| 屏幕 | 电商结构 | 信息图元素 | 产品角度建议 |
|---|---|---|---|
| 首屏承接 | 标题 + 产品 + 4个特色图标 + 副标题 | 图标+标签环绕产品 | Front 3/4 |
| 痛点对比 | 3个痛点图标 → 3个解决方案 + 产品 | 上下对比布局 | Side profile |
| 核心特色 | 多栏并列展示 + 每栏标签和描述 | 网格/三栏布局 | 各元素独立特写 |
| 核心利益 | 左产品 + 右利益列表（图标+短文案） | 双栏信息图 | Elevated overhead |
| 使用步骤 | 4步时间线/编号圆 + 最终成品展示 | 步骤流程图 | Low-angle (最终效果) |
| 场景覆盖 | 3个场景照片 + 场景标签 | 三行场景卡 | 不同使用环境 |
| 信任/工艺 | 微距细节图 + 标注圆 + 信任徽章 | 细节标注图 | Macro特写 |
| CTA/礼品 | 标题 + 产品 + 卖点徽章 + CTA按钮 | 转化闭合布局 | Front 3/4 |

#### 信息图 Prompt 必须包含的要素

1. **布局关键词**：`e-commerce infographic`, `structured grid layout`, `two-column layout`, `three-row layout`, `timeline`, `comparison layout`
2. **标题和文案**：`headline in #2D2D2D at 28pt reading 「...」`, `label in #7A9E7E at 14pt reading 「...」`
3. **信息图元素**：`feature callout icons`, `thin connecting lines`, `numbered circles`, `trust badges`, `CTA button placeholder`
4. **产品角度**：每张信息图中产品从不同角度展示，但角度是为信息图内容服务的
5. **电商 Prompt 开头**：每张详情页 Prompt 必须以 `E-commerce infographic [screen type]` 开头，而不是 `Close-up shot` 或 `Side view`

### 字体搭配规则

- 主标题用衬线体（如 Didot），副标题和正文用无衬线体（如 SF Pro Display）。
- 这是奢侈品画册的标准组合，高级感强。
- 整套图只能用这 2 种字体，禁止混用第三种。

---

## 多图生成执行规则

当用户要求直接生成整套电商图片：

1. 先建立 Campaign Style Lock，并写入图片包计划。
2. 再为每张图建立编号、用途、画幅、图片内短文案和独立 Prompt。
3. 主图默认 `1:1`（2K）；详情页图片默认 `2:3`（2K）。
4. 每张图使用独立 Prompt 文件，避免一次 Prompt 生成多屏拼图。
5. 每张独立 Prompt 必须以同一段 Campaign Style Lock 开头。
6. 输出目录用产品英文 slug，例如 `generated-images/laundry-detergent-pods-pdp/`。
7. 如果 API 或模型不支持某个尺寸，改用最接近的支持尺寸，并在结果中说明。
8. 如果缺少 `.env` 或生图配置，只输出完整 Prompt 包，不调用脚本。
9. 不要虚构认证、实验数据、评分、销量、真实评价或品牌授权。

---

## 直接生图规则

当用户要求生成图片：

1. 先输出最终 Prompt。
2. 短 Prompt 用 `--prompt`，长 Prompt 用 `--prompt-file`。
3. 根据平台选择 `--size`（比例格式），没有要求时默认 `1:1`。
4. `--resolution` 默认 `2k`，4K 仅限 6 个宽幅比例。
5. 只有用户指定目录时才使用 `--output-dir`，否则使用 `generated-images/`。
6. 如果缺少 `IMG_API_KEY` 等配置，不要调用脚本；返回 Prompt 和配置命令示例。

命令形状：

```bash
python3 scripts/generate_image.py --prompt "..." --size 1:1 --resolution 2k
```

脚本支持：

- `--prompt`
- `--prompt-file`
- `--output-dir`
- `--size`：比例格式（`1:1`、`16:9`、`2:3`、`4:5` 等 14 种）
- `--resolution`：`1k` / `2k` / `4k`，默认 `2k`
- `--image`：参考产品图片路径
- `--poll-interval`：轮询间隔秒数，默认 `5`
- `--timeout`：轮询超时秒数，默认 `180`
- `--format`：保存格式（仅影响扩展名），默认 `png`

---

## QA 检查

最终输出前确认：

- Prompt 符合用户真实目标。
- 已匹配正确的场景模板，Prompt 基于模板的 `prompt_template` 组装。
- Prompt 保持简洁，只包含核心信息，没有冗余约束。
- 主体、构图、风格和用途明确。
- 商品 / 营销任务包含转化驱动力诊断。
- 证据缺失时不虚构效果、认证或数据。
- 图片内文字短且必要。
- UGC / 直播 / 社媒场景已应用 anti-AI 技巧（模板中的 `anti_ai_tips` 字段）。
- 如有用户参考图片，已传入 `--image` 参数。
- 负面约束覆盖常见失败点。
- 输出和文件里没有 API key 或私密凭据。
- 已应用 GPT-Image-2 铁律：hex 颜色、数字占比、显式留白、否定清单、平台预留空间。
- 多图任务已分配不同角度和景别，无连续 3 张相同角度，全景图占比 ≤ 40%。
- **详情页图片必须是电商信息图格式**（含标题、图标、标签、利益点、步骤或信任徽章），不是单纯的多角度产品照片。每张详情页 Prompt 以 `E-commerce infographic` 开头。
- 出图后提醒用户放大 200% 逐字核对中文笔画。

---

## 常见翻车点与防护

| 翻车 | 原因 | 防护 |
|---|---|---|
| 中文字笔画错 | 模型中文准确率约 95%，复杂字容易少笔画 | 放大 200% 逐字核对；复杂字换简单同义字 |
| 品牌色漂移 | 写"金色"出来 8 种金 | 全部用 hex 码（`#D4AF37`） |
| Logo 区域被填满 | 写"留空间"模型当没看见 | 写精确坐标：`左上角 200×100 像素区域完全留白` |
| 背景不是纯白 | 写"白底"出来是淡灰 | 写 `#FFFFFF` |
| 产品太大或太小 | 没指定占比 | 写具体百分比：`产品占画面 38%` |
| 画面填满无留白 | 没写留白要求 | 显式声明：`留白至少 50%` |
| 连续多张视觉疲劳 | 背景色全部一样 | 交替使用 2-3 种背景色 |
| 全套图角度雷同 | AI 默认生成正面 3/4 角度，不指定就千篇一律 | 每张 Prompt 显式写明角度关键词；主图 ≥3 种角度，详情页 ≥4 种，穿插特写/微距 |
| 衣服/3C 翻车率高 | 对面料垂坠感、人体比例、接口按键细节要求太高 | 优先测护肤品、家居、食品等稳定品类；衣服用参考图 `--image` 提升一致性 |
| 详情页变成纯产品图 | 只写了多角度关键词，没有电商信息图结构（标题、图标、标签、卖点列表） | 每张详情页 Prompt 以 `E-commerce infographic` 开头，包含布局、文案、图标等电商元素；多角度是信息图内的展示手段而非目的 |

---

## 输出格式

Brief / Prompt 模式返回：

1. **匹配模板**：使用的模板文件名和场景类型
2. **Visual Brief**
3. **Final Image Prompt**
4. **Negative Constraints**
5. **Assumptions**

商品或营销任务追加：

1. **Conversion Driver Diagnosis**
2. **Campaign Style Lock**，当任务包含多张图片
3. **Hero Image Sequence**（标注每张图对应的模板文件）
4. **PDP Detail Image Sequence**，当请求涉及详情页、PDP 或整套商品图
5. **Copy Lines**，如果图片需要文字
6. **Test Priorities**

Generate 模式返回：

1. **匹配模板**：使用的模板文件名和场景类型
2. **Final Image Prompt**
3. **Campaign Style Lock**，多图任务必须返回
4. **Image Pack Plan**，包含每张图的编号、用途、尺寸、对应模板和短文案
5. **Generated Files**
6. **Assumptions / Notes**
