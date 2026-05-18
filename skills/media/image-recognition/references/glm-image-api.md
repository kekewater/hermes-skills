# GLM-Image API — AI图像生成

## 概述

[GLM-Image](https://open.bigmodel.cn/) 是智谱AI推出的文本到图像生成模型。支持从文字提示生成高质量图像，主打"写对文字"能力（在图像中生成可读的文本）。

## 前置条件

- 智谱AI API Key (`GLM_API_KEY`)
- 购买了 GLM-Image 资源包（智谱开放平台 → 模型广场 → GLM-Image）

## API 接口

```bash
POST https://open.bigmodel.cn/api/paas/v4/images/generations
Authorization: Bearer <GLM_API_KEY>
Content-Type: application/json
```

### 请求体

```json
{
  "model": "glm-image",
  "prompt": "描述要生成的图像内容",
  "size": "1280x1280",
  "n": 1
}
```

### 支持的模型（model 字段）

| 模型编码 | 说明 |
|---------|------|
| `glm-image` | 最新图像生成模型，文字渲染能力突出 |
| `cogview-4` | 早期 CogView 系列 |
| `cogview-4-250304` | CogView-4 特定版本 |
| `cogview-3-flash` | 快速生成版 |

### 支持的尺寸

- `1024x1024`（默认）
- `1280x1280`
- 其他尺寸可能支持但未在文档中列出

### 响应

```json
{
  "created": 1778725243,
  "data": [
    {
      "url": "https://...水印图.png?UCloudPublicKey=...&Signature=...&Expires=..."
    }
  ],
  "id": "请求ID",
  "request_id": "请求ID"
}
```

生成的图片有有效期限（URL 中的 Expires 参数），需及时下载保存到本地。

## Python 调用示例

```python
import requests

GLM_KEY = "你的API Key"
resp = requests.post(
    "https://open.bigmodel.cn/api/paas/v4/images/generations",
    headers={
        "Authorization": f"Bearer {GLM_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": "glm-image",
        "prompt": "专业金融数据信息图风格，深蓝底色，白色/蓝色文字",
        "size": "1280x1280",
        "n": 1
    },
    timeout=60  # 图像生成通常需要30-60秒
)

if resp.status_code == 200:
    url = resp.json()['data'][0]['url']
    # 下载到本地
    img_resp = requests.get(url, timeout=30)
    with open('output.png', 'wb') as f:
        f.write(img_resp.content)
```

## 已知限制

### ⚠️ 不擅长精确数据表/数字渲染

GLM-Image 能生成**视觉上很漂亮的图**，但在**精确渲染大量结构化数据**时有问题：
- 数字可能错误/重复（如同一个指数出现两次）
- 表格布局混乱
- 百分比单位错误（如 "3029.66%" 而不是 "-0.58%"）
- 数据行可能重复或遗漏

**原因**：AI图像生成模型理解的是语义概念，不是结构化数据。它"看懂"了"上证指数 4223"这个意思，但渲染成像素时可能把多行数据搞混。

### 文字渲染能力

GLM-Image 的优势是"写对文字"——它可以在图像中生成**可读的中文文本**（标题、标签、摘要文字）。这点比其他模型（如 DALL-E、Midjourney 混入无意义字符）强很多。

但"写对文字"不等于"正确排列表格中的每一行数据"——它擅长**独立文本片段**，不擅长**表格中的多行关联数据**。

## 最佳实践：混合方案

对于需要精确数据的金融信息图，推荐**混合方案**：

1. **步骤A: Pillow 渲染** — 用 Python + Pillow 精确绘制数据表格、数字、KPI指标（保证数据100%准确）
2. **步骤B: GLM-Image 优化背景/装饰** — 用 GLM-Image 生成科技风格背景、装饰元素，叠加到 Pillow 生成的精确数据上
3. **步骤C: 纯 AI 方案** — 对于不需要精确数字的图文（海报、宣传图、概念图），可以直接用 GLM-Image 生成

### 方案对比

| 方案 | 数据精度 | 视觉美观度 | 适用场景 |
|:---|:--------:|:--------:|:--------|
| 纯 Pillow | ⭐⭐⭐⭐⭐ | ⭐⭐ | 数据报告、表格、K线图 |
| 纯 GLM-Image | ⭐⭐ | ⭐⭐⭐⭐⭐ | 概念图、海报、宣传图 |
| 混合方案 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 金融信息图（推荐） |
