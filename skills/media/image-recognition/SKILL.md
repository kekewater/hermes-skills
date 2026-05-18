---
name: image-recognition
description: 图片识别、OCR文字提取、图表/表格识别、截图分析、AI图像生成（GLM-Image）
version: 1.1.0
---

# 图片识别技能 (Image Recognition)

## 环境说明

当前环境系统Python为3.12，安装依赖请用：
```bash
pip3 install --break-system-packages pymupdf Pillow
```
OCR需tesseract：`sudo apt install tesseract-ocr tesseract-ocr-chi-sim` (需root)

## 适用场景

- 用户发送图片 → 需要识别图片中的文字、表格、图表数据
- 截图分析 → 识别UI截图、数据截图、微信截图等
- 扫描件OCR → 扫描版PDF/图片的文字提取
- 图表数据提取 → 从柱状图、折线图、饼图等提取数据
- 表格识别 → 从图片表格中提取结构化数据
- **AI图像生成** → 用 GLM-Image API 生成图片（详见 `references/glm-image-api.md`）

---

## 配置视觉模型（让AI真正"看懂"图片）

如果当前模型不支持图片输入（如 DeepSeek V4 Flash），可以在 Hermes Agent 中配置一个独立的辅助视觉模型。

### 配置方法

```bash
# 辅助视觉模型配置
hermes config set auxiliary.vision.provider <provider>
hermes config set auxiliary.vision.model <model>
```

支持的 provider 和模型：

### Provider 选择对比

| 方案 | 网络要求 | 成本 | 授权方式 | 适合场景 |
|:----|:--------|:----|:--------|:--------|
| **阿里通义 (dashscope)** | ✅ 大陆直连 | 免费额度大 | 一个 API Key | ⭐首选，中文场景强 |
| **智谱 GLM-4V** | ✅ 大陆直连 | 免费额度 | 一个 API Key | 同步有图像生成能力 |
| **腾讯混元 (hunyuan)** | ✅ 大陆直连 | 按量计费 | 建CAM子账号 | 有腾讯云账号时 |
| **OpenRouter 中转** | ⚠️ 大陆不稳定 | 按量付费 | 需绑支付方式 | 200+模型但国内500错误 |
| **Google Gemini** | ❌ 需代理 | 免费额度大 | 需海外 VPS | 配合 Vultr 效果最好 |

### 大陆可用视觉模型配置

```bash
# 🅰 阿里通义千问（推荐：免费额度大，Hermes原生支持）
echo 'DASHSCOPE_API_KEY=你的Key' >> ~/.hermes/.env
hermes config set auxiliary.vision.provider dashscope
hermes config set auxiliary.vision.model qwen-vl-max


# 🅱 智谱 GLM-4V（视觉识别 + 图像生成两用Key）
echo 'GLM_API_KEY=你的Key' >> ~/.hermes/.env
# 注意：GLM 作为 vision provider 可能需要自定义 provider 配置
# 在 config.yaml 的 providers: 段添加：
#   glm-vision:
#     base_url: https://open.bigmodel.cn/api/paas/v4
#     api_key: ${GLM_API_KEY}
#     model: glm-4v-plus
#     model_display_name: 智谱GLM-4V
#     available_models_json: '[{"id":"glm-4v-plus","name":"glm-4v-plus"}]'
# 然后 set auxiliary.vision.provider glm-vision


# 🅲 腾讯混元视觉（有腾讯云账号时）
# ⚠️ 不要用主账号 API Key！建 CAM 子账号，仅授权 QcloudHunyuanFullAccess
# 在 config.yaml 的 providers: 段添加：
#   hunyuan:
#     base_url: https://api.hunyuan.cloud.tencent.com/v1
#     api_key: 子账号SecretId:SecretKey
#     model: hunyuan-vision
#     model_display_name: 腾讯混元视觉
#     available_models_json: '[{"id":"hunyuan-vision","name":"hunyuan-vision"}]'
hermes config set auxiliary.vision.provider hunyuan
hermes config set auxiliary.vision.model hunyuan-vision


# 🅳 OpenRouter 中转
# ⚠️ 2026年实测：从中国大陆调用 OpenRouter 所有模型返回 500 Internal Server Error
#    非网络封锁，而是账户层面问题（免费Key无绑支付方式导致）
#    Key本身有效（auth接口返回200），但chat接口全部500
echo 'OPENROUTER_API_KEY=sk-or-xxx' >> ~/.hermes/.env
hermes config set auxiliary.vision.provider openrouter
hermes config set auxiliary.vision.model openai/gpt-4o
```

### ⚠️ OpenRouter 实测结果（2026-05）

从中国大陆服务器调用 OpenRouter API 的实测结果：
- **Auth API** (`/api/v1/auth/key`) ✅ 正常返回200，Key有效
- **Chat API** (`/api/v1/chat/completions`) ❌ **所有模型返回500 Internal Server Error**
- 测试过的模型：`openai/gpt-4o`、`qwen/qwen3-vl-32b-instruct`、`google/gemini-2.0-flash-001` 全部500
- 响应头显示请求到了 Cloudflare(`cf-ray`)，但后端直接500
- 非网络封锁（TLS握手正常），而是账户/Billing层面的限制

**结论：不要依赖 OpenRouter 作为中国服务器的视觉方案。** 即使 Key 有效，也无法成功调用模型。

### 海外模型 + Vultr 代理方案

```bash
# 1. 在 Vultr 上装代理
ssh root@你的VULTR_IP
apt update && apt install tinyproxy -y
sed -i 's/^Allow /#Allow /g' /etc/tinyproxy/tinyproxy.conf
systemctl restart tinyproxy

# 2. 本机配置代理和 Gemini Key
echo 'HTTP_PROXY=http://你的VULTR_IP:8888' >> ~/.hermes/.env
echo 'HTTPS_PROXY=http://你的VULTR_IP:8888' >> ~/.hermes/.env
echo 'GOOGLE_API_KEY=你的GeminiKey' >> ~/.hermes/.env

# 3. 配置视觉模型
hermes config set auxiliary.vision.provider google
hermes config set auxiliary.vision.model gemini-2.5-flash
```

**可能踩坑：**
- Vultr 防火墙要放行 8888 端口（UFW/iptables + 云控制台安全组）
- 裸代理最好加 IP 白名单或简单鉴权，防滥用
- Vultr 某些机房到 Google 线路可能也不稳
- 本机到 Vultr 的连通性受国内网络影响，有时丢包

### 重启生效

配置后 `hermes restart` 或 `/reset` 新会话生效。`vision_analyze` 工具会自动使用辅助视觉模型。

---

## AI 图像生成（GLM-Image）

本技能不仅用于"看"图片，也支持**生成**图片。

### GLM-Image

智谱AI的 GLM-Image 模型可以从文本描述生成高质量图像。详见 `references/glm-image-api.md`。

**核心特点：**
- ✅ 国内直连，速度快
- ✅ 支持中文文字渲染（在图像中写对中文标题、标签等）
- ❌ 不擅长精确数据表/数字渲染（数字可能错位、重复）
- ❌ 有有效期水印URL，需及时下载

### 使用场景

| 场景 | 推荐方案 |
|:----|:--------|
| 概念图、海报、宣传图 | 纯 GLM-Image 生成 |
| 金融信息图（需要精确数据） | Pillow 渲染数据层 + GLM-Image 装饰层（混合方案） |
| 数据图表 | Python matplotlib/seaborn |

---

## 核心工具

### 1. vision_analyze（首选，需模型支持图片）

```bash
vision_analyze(
    image_url="path/to/image.jpg",
    question="这张图里有什么数据？请提取所有文字内容"
)
```

**识别内容类型：**

| 类型 | 提问示例 |
|:--|:--|
| 纯文字截图 | "请提取图中所有文字" |
| 表格图片 | "提取表格数据，输出为结构化格式" |
| 图表（柱/线/饼图） | "读取图表中的数据点和数值" |
| UI/APP截图 | "描述这个界面的布局和功能" |
| 手写文字 | "识别手写文字内容" |

**注意：** 如果 `vision_analyze` 报错 `unknown variant 'image_url'`，说明当前模型不支持图片 → 先配置辅助视觉模型，或改用OCR方案。

---

### 2. OCR（图片文字提取）

当模型不支持图片或需要更高精度文字识别时：

#### 方案A: pymupdf（轻量，适合文字清晰的截图/扫描件）

```bash
# 安装
pip install pymupdf

# 提取图片中的文字
python3 -c "
import fitz
doc = fitz.open('image.jpg')  # 也支持.png,.pdf
for page in doc:
    print(page.get_text())
"
```

#### 方案B: marker-pdf（高质量OCR，适合复杂排版/手写）

```bash
# 安装（需~5GB空间）
pip install marker-pdf

# OCR识别
marker_single image.jpg --output_dir ./output
```

#### 方案D: EasyOCR（基于PyTorch，中文识别好，已验证✅）

```bash
# 安装（含 PyTorch）
pip3 install easyocr

# 使用（CPU模式，首次运行会自动下载模型）
python3 -c "
import easyocr
reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
result = reader.readtext('image.jpg')
for (bbox, text, conf) in result:
    print(f'{conf:.0%} {text}')
"
```

**注意：** 首次运行会下载检测和识别模型（~200MB），需联网。CPU模式推理较慢，大图建议先缩放到 1024px。

#### 方案E: PaddleOCR（百度方案，中英混合强，⚠️v3.5+可能有兼容问题）

```bash
# 安装
pip3 install paddleocr paddlepaddle

# 使用（v3.5 新版 API 变化）
python3 -c "
from paddleocr import PaddleOCR
ocr = PaddleOCR(lang='ch')
result = ocr.ocr('image.jpg')
for line_group in result:
    for line in line_group:
        text = line[1][0]
        print(text)
"
```

**坑：** paddlepaddle 3.3.1 + paddleocr 3.5.0 在部分环境有 `ConvertPirAttribute2RuntimeAttribute not supported` 错误，目前建议优先用 Tesseract 或 EasyOCR。

```bash
# 如果系统已安装tesseract
pip install pytesseract Pillow
python3 -c "
from PIL import Image
import pytesseract
text = pytesseract.image_to_string(Image.open('image.jpg'), lang='chi_sim+eng')
print(text)
"
```

---

### 3. 图片预处理

OCR前先预处理图片可显著提高识别率：

```bash
# 使用Pillow进行预处理
python3 -c "
from PIL import Image, ImageEnhance, ImageFilter

img = Image.open('input.jpg')

# 转灰度
img = img.convert('L')

# 增强对比度
enhancer = ImageEnhance.Contrast(img)
img = enhancer.enhance(2.0)

# 增强锐度
enhancer = ImageEnhance.Sharpness(img)
img = enhancer.enhance(2.0)

# 二值化（适合文字清晰的图片）
img = img.point(lambda x: 0 if x < 128 else 255)

img.save('processed.jpg')
"
```

---

### 4. 图片格式转换

```bash
# 检查图片格式
file image.jpg

# 转换格式（Pillow）
python3 -c "
from PIL import Image
img = Image.open('input.webp')
img.save('output.jpg', 'JPEG', quality=95)
img.save('output.png', 'PNG')
"
```

---

## 常见问题处理

### 模型不支持图片
```
错误: unknown variant 'image_url', expected 'text'
```
→ 当前模型是纯文本模型（如DeepSeek-V3），不支持直接看图片
→ 改用OCR方案（pymupdf/tesseract）提取文字后分析

### 图片太大
- 自动resize通常处理不了超大图片
- 先用 `file` 命令检查尺寸
- 用Pillow缩小：`img.thumbnail((1024, 1024))`

### 图片格式不支持
- 支持的格式：JPEG, PNG, WebP, BMP, GIF
- GIF只取第一帧，动图需逐帧处理
- HEIC/RAW格式需额外转换

### 中文OCR效果差
- 确保OCR引擎加载了中文语言包
- Tesseract: `lang='chi_sim'`
- 预处理增强对比度后再OCR

### GLM-Image生成的图像URL过期
- GLM-Image 返回的水印URL有有效期（Expires参数）
- 生成后应立即下载保存到本地

---

## 工作流示例

### 提取截图中的数据表格

```
用户发了一张表格截图

1. 先用 vision_analyze 尝试直接识别
   （如果模型支持图片）

2. 如果失败 → 用 pymupdf OCR 提取文字
   如果文字不清晰 → 预处理增强对比度

3. 将提取的文字整理为结构化格式（CSV/Markdown表格/Excel）

4. 用户确认数据准确性
```

### 识别图表数据

```
用户发了一张柱状图/折线图

1. vision_analyze 读取图中的数据点
   提问："请读取图表中所有数据系列的数值"

2. 将数据整理为表格格式

3. 如需进一步分析，用提取的数据生成Excel
```

### 微信截图文字提取

```
用户从微信发了一张图片

1. 保存到本地路径 /home/ubuntu/.hermes/image_cache/img_xxx.jpg
2. OCR提取文字或用 vision_analyze 识别
3. 返回识别结果
```

### AI生成早报图片（混合方案）
### AI生成早报图片（混合方案）

**⚠️ 用户偏好优先：先问用户要不要图，默认只给数据文本。**
需要生成A股早报信息图时，先给出清晰可复制的数据文本（markdown表格），让用户自己扔GPT。用户主动要求生图时，才用以下方案选型：

**方案A（数据精确·设计一般）：Pillow 渲染**
```
→ scripts/daily_briefing_image.py
→ 数据100%准确，设计师一般（纯代码绘制）
→ 适合：需要精确数据的内部报告
```

**方案B（视觉好看·数据不准）：GLM-Image AI生成**
```
→ 调用 POST /paas/v4/images/generations model=glm-image
→ 视觉漂亮，但数据表格可能错位/重复/单位错误
→ 适合：不需要精确数字的宣传类图文
```

**⚠️ 用户偏好：不要自己生成图片**  
用户明确要求：**只给数据文本，不渲染/截图/生图**。用户自己扔 GPT 生成图片，比我渲染的好看。所有 Pillow/Chrome 截图/AI生图方案只在用户主动要求时才用，默认只输干净可复制的数据文本。

**方案C（数据精准·视觉精致但用户可能不用）：HTML渲染 → Chrome截图**
```
→ 编写精确的HTML+CSS排版（数据100%人工填写/可按需更新）
→ 用 headless Chrome 截图为PNG
→ 兼具数据准确性 + 专业级UI设计
→ 适合：每日A股早报等需要精确数据+美观展示的场景
```

**方案C 详细步骤如下（参见 `references/html-to-image-workflow.md`）：**
1. 用 HTML+CSS 精确排版所有数据（表格、卡片、KPI）
2. HTML文件放到 `~/` 下（snap版Chrome不能访问 /tmp）
3. 截图命令：
   ```bash
   chromium --headless --no-sandbox --disable-gpu \\
     --screenshot=/home/ubuntu/output.png \\
     --window-size=900,1200 \\
     file:///home/ubuntu/template.html
   ```
4. 生成的 PNG 通过 MEDIA:/path 发送给用户
```

## References

| 文件 | 内容 |
|------|------|
| `references/glm-image-api.md` | GLM-Image API 文档：端点、参数、调用示例、限制与最佳实践 |
| `references/html-to-image-workflow.md` | HTML → Chrome 截图工作流：用于生成数据精确+设计精致的A股早报图 |
