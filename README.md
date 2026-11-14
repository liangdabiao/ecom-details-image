# ecom-details-image Skill

一个面向 claude code / Codex / workbuddy 的跨境电商和国内电商通用视觉创作 Skill。GPT-Image-2 /Seedream 5.5 上线以来，电商圈已经被刷屏了。图像生成的边界，如今又被推了一大步。下面是我精选的 25个高质量案例，涵盖纯色底产品主图、场景化生活图、平铺图、电商详情图、真实场景等等，全部配完整提示词，都可以利用 GPT-Image-2 /Seedream 5.5 API生成最终效果。 

一键生成电商相关图片:
输入产品图片和需求描述，自动生成完整的电商主图、详情页图片、社媒推广图、直播间场景图等全套视觉素材。
与众不同之处是：Campaign Style Lock 机制 和 强推广和重视转化效果。

它可以做两件事：

- 生成可执行的视觉简报和 AI 生图 Prompt。
- 直接生成图片：Codex 环境使用 agent 内置 `imagegen` 工具；其他环境（claude code / workbuddy 等）默认走 **即梦 dreamina-canvas CLI（Seedream 5.5）**，如果使用 gpt image2 则安装 `apiz` CLI 生图。

未安装任何生图 CLI 时，它仍然可以正常输出 Prompt；CLI 就绪后，可以直接出图。 建议请先安装[apiz](https://apiz.ai) 官方 CLI 或即梦 [dreamina-canvas CLI](https://jimeng.jianying.com/ai-tool/install?from_page=explore) 。

### 兄弟项目 - 跨境电商调研skill:
https://github.com/liangdabiao/Amazon-Skills-Liang

## 实战案例：陶瓷手冲滤杯整套 PDP（即梦 Seedream 5.5 实测）

2026-11-14 用本 Skill + 即梦 `dreamina-canvas` CLI + Seedream 5.5，从一张参考图出发生成的完整电商图片包（5 主图 + 8 详情图），Prompt 全部保留在 [`prompts/pour-over-dripper/`](prompts/pour-over-dripper/)，统一 Campaign Style Lock（暖米白 `#F7F4EF` + 深炭 `#2D2D2D` + 木色 `#B08350` + 灰绿 `#8A9B8E`）。

### 主图（Hero Images）

| 主图 1 · 白底 Packshot | 主图 2 · 木纹特写 | 主图 3 · 生活场景 |
|---|---|---|
| ![主图1](docs/case/hero-01-packshot.jpg) | ![主图2](docs/case/hero-02-feature-closeup.jpg) | ![主图3](docs/case/hero-03-lifestyle.jpg) |

| 主图 4 · 竞品对比 | 主图 5 · 促销 CTA |
|---|---|
| ![主图4](docs/case/hero-04-comparison.jpg) | ![主图5](docs/case/hero-05-offer-cta.jpg) |

### 详情页（PDP Infographics）

| 首屏承接 | 痛点放大 | 机制解释 | 核心利益 |
|---|---|---|---|
| ![首屏](docs/case/detail-01-opening.jpg) | ![痛点](docs/case/detail-02-pain-points.jpg) | ![机制](docs/case/detail-03-mechanism.jpg) | ![利益](docs/case/detail-04-benefits.jpg) |

| 使用步骤 | 场景覆盖 | 信任背书 | 收尾 CTA |
|---|---|---|---|
| ![步骤](docs/case/detail-05-steps.jpg) | ![场景](docs/case/detail-06-scenes.jpg) | ![信任](docs/case/detail-07-trust.jpg) | ![收尾](docs/case/detail-08-cta.jpg) |

### 本次实测数据

| 指标 | 数值 |
|---|---|
| 生成张数 | 13 张（含 2 张单图测试 + 1 张返修）|
| 积分消耗 | 90 积分（Seedream 5.5 @2K 实扣 6 积分/张）|
| 单张耗时 | 约 60–90 秒（含参考图上传、报价、生成、下载）|
| 中文渲染 | 信息图中文标题/标签**全部正确**（「一杯好咖啡 从好滤杯开始」等 30+ 处）|
| 参考图 | i2i 模式挂 1 张参考图，13 张图产品形态一致性保持良好 |
| 交付物 | 2K PNG（2048×2048 / 1664×2496）|

### 实测踩坑与经验

1. **i2i 通道容易生成乱码装饰文字**：即使 Prompt 写了 `no text`，图生图模式仍倾向添加海报式英文乱码。解法：把负面约束升级为整段 `Strictly forbidden: any text, any letters, any words, any numbers, any typography, any labels...`（见 [`prompts/pour-over-dripper/hero-02.txt`](prompts/pour-over-dripper/hero-02.txt)），实测一次修复。
2. **t2i 反而更干净**：纯白底 Packshot 用文生图（不挂参考图）出图最干净；图生图留给需要产品一致性的场景。
3. **中文短文案渲染可靠**：Seedream 5.5 对 `「」` 包裹的 6–10 字中文标题渲染准确率非常高，适合详情页信息图。
4. **国内版合规水印**：产物左上角自带「AI生成」浅色水印，上线前需裁切或修补。
5. **报价即实扣**：CLI 通道报价上限 = 实扣积分（2K 6 积分/张），批量前用 `dreamina-canvas auth account` 查余额即可精确预算。

## 场景模板轮测：同一只滤杯 × 17 个电商场景（Seedream 5.5）

对 `references/templates/` 中适配非服装类目的 17 个场景做了全量实测（剔除试穿、隐形模特、设备 mockup、门店门面 4 个服装/SaaS 专属场景），全部挂在**同一张参考图**上出图。Prompt 见 [`prompts/pour-over-dripper/templates/`](prompts/pour-over-dripper/templates/)。

| 场景 | 示例 | 一句话结论 |
|---|---|---|
| 03 平铺图 flat-lay | ![t03](docs/case/templates/t03-flat-lay.jpg) | ✅ 俯拍构图、道具搭配稳定，可直接用 |
| 04 细节微距 macro | ![t04](docs/case/templates/t04-detail-macro.jpg) | ✅ 木纹/釉面质感极强，最惊艳的场景之一 |
| 05 海报 Banner | ![t05](docs/case/templates/t05-poster.jpg) | ✅ 「上新 8 折」「马上抢」中文全对，可直接用 |
| 06 社媒图 小红书 | ![t06](docs/case/templates/t06-social.jpg) | ⚠️ 版式好看，但 bullet 标签出现重复文案 |
| 07 UGC 买家秀 | ![t07](docs/case/templates/t07-ugc.jpg) | ✅ 初版出现双人四手+木圈乱码刻字，改用小云雀通道单图重选修复，现单人双手、无刻字 |
| 08 模特展示 | ![t08](docs/case/templates/t08-model-showcase.jpg) | ✅ 手持产品、浅景深、人物自然，可用 |
| 09 before/after 对比 | ![t09](docs/case/templates/t09-before-after.jpg) | ✅ 上下分层+标签全对，叙事清楚 |
| 10 礼盒包装 | ![t10](docs/case/templates/t10-packaging.jpg) | ✅ 牛皮礼盒+丝带质感好，可直接用 |
| 12 创意概念 | ![t12](docs/case/templates/t12-creative.jpg) | ⚠️ 悬浮水螺旋视觉冲击强，但木圈有小畸形 |
| 13 尺寸规格图 | ![t13](docs/case/templates/t13-size-spec.jpg) | ✅ 标注线+「高 12cm」「口径 8.5cm」等 5 处文字全对 |
| 14 多规格 SKU 卡 | ![t14](docs/case/templates/t14-multi-product.jpg) | ✅ 三色木圈变体+标签全对，SKU 卡一步到位 |
| 15 直播间场景 | ![t15](docs/case/templates/t15-livestream.jpg) | ✅ 首次大标题「专」字渲染错误，按逐字约束重做一次修复，现文字全对 |
| 17 爆炸图 | ![t17](docs/case/templates/t17-exploded.jpg) | ✅ 三层拆分+标注全对，产品结构清晰 |
| 19 多角度网格 | ![t19](docs/case/templates/t19-multi-angle.jpg) | ⚠️ 2×2 网格规整，但四个角度差异偏小 |
| 20 杂志封面 | ![t20](docs/case/templates/t20-magazine.jpg) | ✅ 中英文刊头+光影氛围，质感最高级 |
| 21 季节 campaign | ![t21](docs/case/templates/t21-seasonal.jpg) | ✅ 「冬季暖冬限定」+节日氛围到位 |
| 22 奢华氛围 | ![t22](docs/case/templates/t22-luxury.jpg) | ✅ 低调棚拍+烟雾光束，高级感强 |

### 轮测数据与结论

| 指标 | 数值 |
|---|---|
| 测试场景数 | 17 个（一次通过 17/17，无任务失败）|
| 积分消耗 | 即梦 108 积分（17 张 + t15 返修）+ 小云雀 1 次（t07 重做，4 候选挑 1）|
| 单张耗时 | 约 60–90 秒，批量串行约 30 分钟 |
| 产品一致性 | 17 张全部挂同一参考图，木圈位置/陶瓷形态保持稳定 |
| 中文渲染 | 14 处标题/标签正确（t15 重做一次修复）；t06 标签重复待返修 |
| 主要风险 | 人手持/场景类（UGC、直播、创意）仍会出现局部乱码刻字或小畸形，需人工筛选或重做 |

**场景难度分级（实测）**：纯产品摄影（平铺/微距/包装/SKU/多角度）≈ 信息图（规格/爆炸/对比）> 氛围图（杂志/季节/奢华/海报）> 人物场景（模特/UGC/直播）——人物场景文字和细节翻车率最高，建议出 2–4 张候选挑最好的。

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
4. 按**生图通道判断**出图：Codex 环境直接调用 agent 内置 `imagegen`；其他环境调用 `scripts/generate_image.py`（默认走即梦 Seedream 5.5，自动回退 apiz）。
5. 输出生成文件路径。

## 生图通道（Codex imagegen / 即梦 dreamina / apiz CLI）

这个 Skill 不内置任何 API，也不共享任何密钥。生图前先判断环境：

### 通道速查

| | 通道 A · Codex imagegen | 通道 B · 即梦（默认）| 通道 C · apiz（回退）|
|---|---|---|---|
| 环境 | Codex 内置工具 | claude code / workbuddy 等 | 同左 |
| 默认模型 | — | Seedream 5.5 | apiz/gpt-image-2.5-flare |
| 参考图 | 按工具参数 | **最多 10 张**（多角度一致性更强）| 1 张 |
| 比例 | 按工具参数 | 8 种，`4:5` 等自动换算 | 10 种 |
| 分辨率 | — | 1.5K / 2K | 1K / 2K / 4K |
| 批量 | — | 单节点 1–8 张 | 单次 1 张 |
| 计费 | — | 约 6 积分/张（2K）| 约 30–90 积分/张 |
| 选择方式 | 自动 | `--channel dreamina` 或默认 auto | `--channel apiz` |

### 通道 A：Codex 环境 → agent 内置 imagegen

如果 agent 会话中具备内置 `imagegen` 工具（即 Codex 环境），直接调用它生成图片：

- 把最终 Prompt（含 Campaign Style Lock）作为 prompt 传入，工具支持比例参数时传入对应比例。
- 用户提供了参考产品图时，按 imagegen 工具的参考图/编辑参数传入。
- 不运行 Python 脚本。

### 通道 B：其他环境 → 即梦 dreamina-canvas CLI（默认优先）

claude code / workbuddy 等环境通过 `scripts/generate_image.py` 生图，`--channel auto`（默认）时优先走即梦通道，脚本转交 `scripts/generate_image_dreamina.py` 执行：

1. 解析目标画布：`DREAMINA_CANVAS_ID` → 当前画布 → 自动创建 `ecom-details-image` 画布。
2. 本地参考图先经 `resource upload` 登记为画布素材（支持最多 10 张）。
3. `node create image --run --wait` 保存节点、报价（不超过积分上限）、运行并等待终态。
4. `resource download` 把节点产物下载到本地输出目录。

前置条件：

```bash
dreamina-canvas --version      # 确认已安装
dreamina-canvas auth login     # OAuth 登录（认证由 CLI 处理，脚本不接触密钥）
dreamina-canvas auth account   # 查看积分余额
```

可选配置（在 Skill 目录放 `.env`，全部可省略）：

```dotenv
DREAMINA_IMAGE_MODEL=seedream_5.5
# DREAMINA_CANVAS_ID=<画布UUID>     # 不设置时用当前画布或自动创建
DREAMINA_RESOLUTION=2K
DREAMINA_CREDIT_CEILING=10
# DREAMINA_BIN=C:\path\to\dreamina-canvas.exe
```

能力边界（以 `dreamina-canvas model list --type image` 实时结果为准）：

- 默认模型 `seedream_5.5`：文生图 + 图生图，比例 `1:1 / 3:4 / 4:3 / 16:9 / 9:16 / 2:3 / 3:2 / 21:9`，分辨率 `1.5K / 2K`，单节点 1-8 张，参考图最多 10 张（单张 ≤50MB / 8192px），Prompt 上限 5000 字符。
- 不支持的比例如 `4:5` 会自动换算到最接近的支持比例（`3:4`）并在日志中说明。
- 计费按积分：**Seedream 5.5 实测 2K 约 6 积分/张**（报价为上限，实扣以节点 `creditsAmount` 为准）。
- 国内版产物左上角带「AI生成」合规水印，上线前需自行裁切或修补。

### 通道 C：其他环境 → apiz CLI

即梦 CLI 未安装/未登录，或显式 `--channel apiz` 时，脚本内部调用 [apiz](https://apiz.ai) 官方 CLI：

1. 本地参考图先经 `apiz upload` 上传到 apiz CDN 换取公网 URL。
2. `apiz generate <prompt> --model <model> --aspect-ratio <ratio> --wait --json` 提交并等待任务完成。
3. 脚本解析任务 JSON，把 `result.images[].url` 下载到本地输出目录。

前置条件：

```bash
apiz --version     # 确认已安装
apiz auth login    # 登录并保存 API key（本机通常已就绪）
apiz account balance  # 查看积分余额
```

认证由 CLI 自行处理（`apiz auth login` 保存的配置文件，或 `APIZ_API_KEY` 环境变量），脚本不接触密钥。

可选配置（在 Skill 目录放 `.env`，全部可省略）：

```dotenv
APIZ_IMAGE_MODEL=apiz/gpt-image-2.5-flare
# APIZ_API_KEY=sk-xxx     # 仅未使用 apiz auth login 时需要
# APIZ_BASE_URL=https://api.apiz.ai
# APIZ_BIN=C:\path\to\apiz.exe
```

- `APIZ_IMAGE_MODEL`：图片模型 id，默认 `apiz/gpt-image-2.5-flare`；`apiz models list` 可查看全部图片模型（如 `openai/gpt-image-2`、`fal-ai/nano-banana-pro`、`apiz/gpt-image-2.5-sunburst`）。兼容旧别名 `IMG_MODEL`、`OPENAI_IMAGE_MODEL`、`OPENAI_MODEL`。
- `APIZ_API_KEY`：未登录时使用。兼容旧别名 `IMG_API_KEY`、`OPENAI_API_KEY`。
- `APIZ_BIN`：apiz 不在 PATH 时指定可执行文件路径。

不要把真实 API key 写进 README、`SKILL.md`、脚本、Git 提交或聊天记录。

### 费用与异步机制

- 生图按 apiz 积分计费，单张图约 30–90 秒完成；脚本用 `--wait` 阻塞等待任务结束后自动下载。
- 任务状态可用 `apiz tasks get <task_id>` / `apiz tasks wait <task_id>` 查询。
- 执行 `apiz account balance` 查看积分余额；批量出图前先确认 Image Pack Plan 与预计消耗。

## 生图脚本用法

统一入口（`--channel auto` 默认优先即梦，apiz 回退；`ECOM_IMAGE_CHANNEL` 环境变量可覆盖）：

```bash
python3 scripts/generate_image.py --prompt "clean product hero image, premium studio lighting, white background" --size 1:1
```

即梦通道（Seedream 5.5，支持多参考图与单节点批量）：

```bash
python3 scripts/generate_image_dreamina.py --prompt-file prompt.txt --size 1:1
python3 scripts/generate_image_dreamina.py --prompt "..." --size 2:3 \
  --image data/product-front.jpg --image data/product-side.jpg --count 4
python3 scripts/generate_image_dreamina.py --prompt "..." --size 1:1 \
  --canvas-id <画布UUID> --resolution 1.5K
```

apiz 通道：

```bash
python3 scripts/generate_image.py --channel apiz --prompt "clean product hero image, premium studio lighting, white background" --size 1:1
```

从文件读取 Prompt：

```bash
python3 scripts/generate_image.py --prompt-file prompt.txt --output-dir outputs
```

带参考产品图（图生图模式，本地文件自动上传 apiz CDN）：

```bash
python3 scripts/generate_image.py --prompt "..." --size 1:1 --image data/product.jpg
```

已有公网参考图 URL 时：

```bash
python3 scripts/generate_image.py --prompt "..." --size 4:5 --image-url https://cdn.example.com/product.jpg
```

更多参数：

```bash
python3 scripts/generate_image.py \
  --prompt-file prompt.txt \
  --output-dir generated-images \
  --size 4:5 \
  --model apiz/gpt-image-2.5-flare \
  --image data/product.jpg \
  --timeout 420
```

指定其它 `.env` 文件：

```bash
python3 scripts/generate_image.py --env-file .env --prompt-file prompt.txt
```

脚本参数：

- `--prompt`：直接传入 Prompt。
- `--prompt-file`：从文本文件读取 Prompt。
- `--output-dir`：输出目录，默认 `generated-images/`。
- `--env-file`：指定 `.env` 配置文件；不指定时从当前目录向上查找（可选）。
- `--size`：图片比例，默认 `1:1`，如 `16:9`、`9:16`、`2:3`、`4:5`；也兼容 `1024x1024` 这类像素写法（自动换算成比例）。
- `--model`：apiz 图片模型 id，默认 `apiz/gpt-image-2.5-flare`（可用 `APIZ_IMAGE_MODEL` 覆盖）。
- `--image`：本地参考产品图片路径，传入后自动上传并走图生图模式，提升产品一致性。
- `--image-url`：参考图公网 URL（与 `--image` 二选一，URL 优先）。
- `--timeout`：单个生成任务等待上限秒数，默认 `420`。
- `--format`：保存格式的默认扩展名（实际以后缀/类型为准），默认 `png`。
- `--channel`：生图通道 `auto / dreamina / apiz`，默认 `auto`（优先即梦，回退 apiz）。

### 常用图片比例

| size | 建议用途 |
|---|---|
| `1:1` | 主图、Amazon / 淘宝主图 |
| `4:5` / `2:3` | 详情页竖屏、移动端信息流 |
| `3:4` | 详情页、社媒竖图 |
| `16:9` | Banner、官网 Hero、直播间封面 |
| `9:16` | 短视频封面、Story |
| `3:2` / `4:3` | 场景图、 lifestyle 图 |

实际输出像素由所选模型决定（默认 `apiz/gpt-image-2.5-flare` 支持 1K/2K/4K 三档，最高 4K）。

脚本只使用 Python 标准库，不需要安装第三方依赖。

## 电商 PDP 图片包规则

当用户提到“详情页、PDP、Amazon A+、Shopify 商品页、主图堆栈、整套商品图、商品详情图片”时，Skill 默认不会只生成 5 张主图，而是输出完整图片包：

- 5 张主图：首图卖点、机制/功能、利益证明、对比或场景、优惠/保障。
- 7-9 张详情页图片：首屏承接、痛点放大、机制解释、核心利益、使用步骤、场景覆盖、对比选择、信任背书、FAQ/风险逆转/CTA。
- 主图默认 `1:1`。
- 详情页图片默认 `2:3`，适合移动端纵向浏览。
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

- 每个使用者使用自己的 apiz 账户和凭据；认证由 apiz CLI 的配置文件或 `APIZ_API_KEY` 处理。
- 仓库不会保存 API key。
- 不要提交 `.env` 文件；仓库已用 `.gitignore` 忽略 `.env` 和 `.env.*`。
- 分享 Skill 时，只分享代码和文档，不分享任何真实密钥。
- 如果你在公共终端或录屏环境中操作，不要直接展示 `APIZ_API_KEY`。

## 局限性

- apiz 生成为异步任务，单张图通常 30–90 秒完成；脚本通过 `--wait` 阻塞等待后自动下载。
- 实际输出像素由所选模型决定；默认 `apiz/gpt-image-2.5-flare` 支持 1K/2K/4K 三档。
- 单个任务每次返回 1 张图；参考图走 `--image` / `--image-url` 单张传入。
- 生图质量、速度和积分消耗取决于所选模型。
- 结果 URL 有时效，脚本会自动下载到本地。
- 商品营销图中的效果承诺必须有证据支持；不要让图片文案虚构资质、认证或结果。

## 推荐工作流

1. 先让 Skill 生成视觉简报和 Prompt。
2. 人工确认画面目标、主体、平台尺寸和禁用内容。
3. Codex 环境直接用内置 imagegen 出图；其他环境 `apiz auth login` 后生成图片。
4. 对商品或广告图保留 2–3 个创意变体做 A/B 测试。
