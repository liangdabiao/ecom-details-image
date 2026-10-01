# ecom-details-image Skill

一个面向 claude code / Codex / OpenClaw 的跨境电商和国内电商通用视觉创作 Skill。GPT-Image-2 上线以来，电商圈已经被刷屏了。图像生成的边界，如今又被推了一大步。下面是我精选的 25个高质量案例，涵盖纯色底产品主图、场景化生活图、平铺图、电商详情图、真实场景等等，全部配完整提示词，都可以利用 GPT-Image-2 API生成最终效果。一键生成电商相关图片！一键生成电商相关图片！输入产品图片和需求描述，自动生成完整的电商主图、详情页图片、社媒推广图、直播间场景图等全套视觉素材。
与众不同之处是：Campaign Style Lock 机制 和 强推广和重视转化效果。

它可以做两件事：

- 生成可执行的视觉简报和 AI 生图 Prompt。
- 在使用者配置自己的 OpenAI 兼容图片 API 后，直接调用 API 生成图片。

未配置 API 时，它仍然可以正常输出 Prompt；配置 API 后，可以直接出图。



## 适用场景

- 商品主图、详情页视觉、Amazon / Shopify / TikTok Shop 图片。
- 广告图、社媒图、活动 Banner、缩略图。
- 品牌视觉方向、创意概念、图像模型 Prompt。
- 跨境电商 PDP 转化视觉：诊断视觉驱动、痛点驱动、情感价值驱动。
- 电商整套图片包：默认规划 5 张主图 + 7-9 张详情页图片。

## 它的工作方式

### 1. Prompt / Brief 模式

当你只需要策略、视觉方向或 Prompt 时，Skill 会输出：

1. 视觉简报。
2. 最终图片 Prompt。
3. 负面约束。
4. 假设说明。

如果是商品或营销图，还会补充：

- 转化驱动力诊断。
- Campaign Style Lock，用来锁定整套图的色板、冷暖调、字体、背景、光线和布局。
- 主图 / 创意序列。
- PDP 详情页图片序列。
- 图片内文案建议。
- 测试优先级。

### 2. Generate 模式

当你明确要求“生图、生成图片、出图、render image”时，Skill 会：

1. 先生成最终 Prompt。
2. 如果是电商详情页或整套商品图，先建立 Campaign Style Lock。
3. 再拆成独立图片 Prompt，并把同一段 Campaign Style Lock 原样放进每张 Prompt。
4. 调用 `scripts/generate_image.py`。
5. 输出生成文件路径。

## API 配置

这个 Skill 不内置任何 API，也不共享任何密钥。当前默认使用 [apimart.ai](https://apimart.ai) 图像生成接口（GPT-Image-2），采用异步轮询模式。

在 `.claude/skills/ecom-details-image/` 目录下创建 `.env`：

```dotenv
IMG_BASE_URL=https://api.apimart.ai/v1
IMG_MODEL=gpt-image-2
IMG_API_KEY=你的APIKey
```

变量说明：

- `IMG_BASE_URL`：API 根地址，默认 `https://api.apimart.ai/v1`。
- `IMG_MODEL`：图片模型名，固定 `gpt-image-2`。
- `IMG_API_KEY`：使用者在 [apimart.ai/keys](https://apimart.ai/keys) 获取的 API key。

脚本也兼容常见别名：`OPENAI_BASE_URL`、`OPENAI_API_BASE`、`OPENAI_IMAGE_MODEL`、`OPENAI_MODEL`、`OPENAI_API_KEY`。

不要把真实 API key 写进 README、`SKILL.md`、脚本、Git 提交或聊天记录。

### 异步轮询机制

apimart.ai 图像生成采用异步处理模式：

1. 提交任务 → 返回 `task_id`
2. 等待 15 秒后开始轮询 `GET /v1/tasks/{task_id}`
3. 每 5 秒查询一次，通常 30–60 秒完成
4. 任务完成后从返回的图片 URL 下载到本地

单张图费用约 $0.05（2K 分辨率），失败不扣费。

## 生图脚本用法

直接传入 Prompt：

```bash
python3 scripts/generate_image.py --prompt "clean product hero image, premium studio lighting, white background" --size 1:1
```

从文件读取 Prompt：

```bash
python3 scripts/generate_image.py --prompt-file prompt.txt --output-dir outputs
```

带参考产品图（图生图模式）：

```bash
python3 scripts/generate_image.py --prompt "..." --size 1:1 --image data/product.jpg --resolution 2k
```

更多参数：

```bash
python3 scripts/generate_image.py \
  --prompt-file prompt.txt \
  --output-dir generated-images \
  --size 4:5 \
  --resolution 2k \
  --image data/product.jpg \
  --poll-interval 5 \
  --timeout 180
```

指定其它 `.env` 文件：

```bash
python3 scripts/generate_image.py --env-file .env --prompt-file prompt.txt
```

脚本参数：

- `--prompt`：直接传入 Prompt。
- `--prompt-file`：从文本文件读取 Prompt。
- `--output-dir`：输出目录，默认 `generated-images/`。
- `--env-file`：指定 `.env` 配置文件；不指定时从当前目录向上查找 `.env`。
- `--size`：图片比例，默认 `1:1`。可选值：`auto`、`1:1`、`3:2`、`2:3`、`4:3`、`3:4`、`5:4`、`4:5`、`16:9`、`9:16`、`2:1`、`1:2`、`21:9`、`9:21`。
- `--resolution`：输出分辨率档位，默认 `2k`。可选值：`1k`、`2k`、`4k`（4K 仅支持 6 个宽幅比例）。
- `--image`：参考产品图片路径，传入后走图生图模式，提升产品一致性。
- `--poll-interval`：轮询间隔秒数，默认 `5`。
- `--timeout`：轮询超时秒数，默认 `180`。
- `--format`：图片保存格式，仅影响文件扩展名，默认 `png`。

### 支持的图片比例与分辨率

| size | 1K | 2K | 4K |
|---|---|---|---|
| `1:1` | 1024×1024 | 2048×2048 | — |
| `3:2` | 1536×1024 | 2048×1360 | — |
| `2:3` | 1024×1536 | 1360×2048 | — |
| `4:3` | 1024×768 | 2048×1536 | — |
| `3:4` | 768×1024 | 1536×2048 | — |
| `5:4` | 1280×1024 | 2560×2048 | — |
| `4:5` | 1024×1280 | 2048×2560 | — |
| `16:9` | 1536×864 | 2048×1152 | 3840×2160 |
| `9:16` | 864×1536 | 1152×2048 | 2160×3840 |
| `2:1` | 2048×1024 | 2688×1344 | 3840×1920 |
| `1:2` | 1024×2048 | 1344×2688 | 1920×3840 |
| `21:9` | 2016×864 | 2688×1152 | 3840×1648 |
| `9:21` | 864×2016 | 1152×2688 | 1648×3840 |

脚本只使用 Python 标准库，不需要安装第三方依赖。

## 电商 PDP 图片包规则

当用户提到“详情页、PDP、Amazon A+、Shopify 商品页、主图堆栈、整套商品图、商品详情图片”时，Skill 默认不会只生成 5 张主图，而是输出完整图片包：

- 5 张主图：首图卖点、机制/功能、利益证明、对比或场景、优惠/保障。
- 7-9 张详情页图片：首屏承接、痛点放大、机制解释、核心利益、使用步骤、场景覆盖、对比选择、信任背书、FAQ/风险逆转/CTA。
- 主图默认 `1:1`（2K = 2048×2048）。
- 详情页图片默认 `2:3`（2K = 1360×2048），适合移动端纵向浏览。
- 每张图都使用独立 Prompt 文件，避免把多屏详情页挤在一张拼图里。

如果没有真实证据，Skill 只允许使用占位式证明表达，不编造认证、实验数据、评分、销量或真实评价。

## 多图风格一致性

整套图片生成前必须先创建 **Campaign Style Lock**，并把同一段风格锁定文本放进每一张图的 Prompt。它用于固定：

- 色板：背景色、文字色、强调色保持一致。
- 冷暖调：全套统一为冷调、暖调或中性调。
- 字体：统一一种字体风格，不混用衬线、手写、复古或卡通字体。
- 背景：统一棚拍背景、桌面场景或室内空间逻辑。
- 光线：统一光源方向、阴影强度和反光质感。
- 布局：统一留白、圆角、标签、编号、信息图组件。
- 图标：统一线宽、颜色和复杂度。

如果用户没有品牌规范，Skill 会使用一个保守的高级电商默认风格锁：

```text
Campaign Style Lock: consistent premium ecommerce visual system across the entire image set; fixed palette of clean off-white background, deep charcoal text, one product-matched accent color, and one soft secondary accent; neutral-cool studio lighting; modern geometric sans-serif headline placeholders only; consistent rounded rectangular info labels; consistent thin-line icon style; clean high-end product photography mixed with minimal infographic elements; stable product scale and placement; generous whitespace; no color palette changes, no mixed fonts, no random backgrounds, no inconsistent lighting, no mismatched icon styles.
```

## 输入示例

商品营销图：

```text
产品：自发热眼罩
类别：睡眠与健康
价格区间：19–29 美元
受众：压力大的上班族
差异化点：40 分钟持续发热，无香可选，皮肤安全材料
证明资产：4.7 星评价，皮肤科测试报告，30 天保障
渠道：亚马逊 PDP + 主图堆栈
当前弱点：点击量尚可，加购率低
目标：提高转化率和信任感知
要求：生成 1 张主图 Prompt，并在已配置 API 时直接出图
```

电商整套详情页图片：

```text
产品：洗衣凝珠
类别：家居清洁
受众：忙碌家庭、租房用户、宿舍用户
差异化点：一颗一洗，预配比，减少倒液和脏手，香味清新
渠道：Shopify PDP + 商品主图
目标：让详情页也生成独立图片，不只生成 5 张主图
要求：生成完整图片包，并在已配置 API 时直接出图
```

通用视觉图：

```text
为一个 AI 写作工具生成官网首屏视觉。
风格：干净、现代、轻量科技感。
主体：笔记、文档、自动整理的知识卡片。
用途：官网 Hero 背景图。
尺寸：16:9。
不要出现可读文字。
```

## 输出示例

```text
1. Visual Brief
   - 目标：突出轻量、可信、自动整理
   - 主体：文档、知识卡片、柔和界面层次
   - 风格：现代 SaaS、干净、低噪声

2. Final Image Prompt
   Clean modern SaaS hero background image...

3. Negative Constraints
   No readable text, no logos, no clutter...

4. Generated Files
   generated-images/image-20260506-180000-01.png
```

## 安全说明

- 每个使用者使用自己的 `IMG_*` 环境变量。
- 仓库不会保存 API key。
- 不要提交 `.env` 文件；仓库已用 `.gitignore` 忽略 `.env` 和 `.env.*`。
- 分享 Skill 时，只分享代码和文档，不分享任何真实密钥。
- 如果你在公共终端或录屏环境中操作，不要直接展示 `IMG_API_KEY`。

## 局限性

- apimart.ai 采用异步轮询模式，单张图通常 30–60 秒完成。
- 4K 分辨率仅支持 6 个宽幅比例（`16:9`、`9:16`、`2:1`、`1:2`、`21:9`、`9:21`）。
- 参考图最多 16 张，支持 URL 与 base64 混填。
- 生图质量、速度和费用取决于所选分辨率档位（1K / 2K / 4K）。
- 图片结果 URL 有效期 24 小时，脚本会自动下载到本地。
- 商品营销图中的效果承诺必须有证据支持；不要让图片文案虚构资质、认证或结果。

## 推荐工作流

1. 先让 Skill 生成视觉简报和 Prompt。
2. 人工确认画面目标、主体、平台尺寸和禁用内容。
3. 配置 `IMG_*` 环境变量后生成图片。
4. 对商品或广告图保留 2–3 个创意变体做 A/B 测试。
