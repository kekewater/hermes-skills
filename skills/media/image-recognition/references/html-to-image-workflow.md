# HTML → Chrome 截图工作流

用于生成精确数据 + 精致设计的A股早报信息图。

## 原理

- HTML+CSS 能完美排版表格数据、卡片布局、渐变色、字体
- 用 headless Chrome 的 `--screenshot` 参数渲染为 PNG
- 兼具数据准确性 + 专业级 UI 设计

## 前置条件

- Chromium（snap 安装）：`/snap/bin/chromium`

## 步骤

### 1. 创建HTML模板

确保 HTML 的 body 尺寸正好是目标图片尺寸：

```html
<style>
body {
  width: 900px; height: 1200px;
  margin: 0; padding: 28px;
  /* 设计随意，CSS完全可控 */
}
</style>
```

### 2. 保存到用户目录

snap版 Chromium 受 AppArmor 隔离，**不能访问 /tmp**。HTML文件必须放在 `/home/ubuntu/` 下：

```bash
cp /tmp/template.html /home/ubuntu/briefing.html
```

### 3. 截图

```bash
/snap/bin/chromium --headless --no-sandbox --disable-gpu \
  --screenshot=/home/ubuntu/output.png \
  --window-size=900,1200 \
  file:///home/ubuntu/briefing.html
```

成功标志：`xxx bytes written to file /home/ubuntu/output.png`

失败排查：
- 文件全白 → HTML 路径不对或 Chrome 无法访问
- 先确保 HTML 在 `~/` 下，然后用 `file:///home/ubuntu/xxx.html`
- DBus/AppArmor 警告可忽略（不影响截图）

### 4. 验证

```python
from PIL import Image
img = Image.open('/home/ubuntu/output.png')
# 检查是否有内容（非白色像素比例）
pixels = list(img.getdata())
dark = sum(1 for p in pixels if sum(p) < 150)
ratio = 100 * dark / len(pixels)
print(f'内容占比: {ratio:.1f}%')  # 应 >80%
```

### 5. 发送

通过 WeChat/平台发送，使用 MEDIA 关键字：

```
MEDIA:/home/ubuntu/output.png
```

## 关键参数说明

| 参数 | 说明 |
|:---|:---|
| `--headless` | 无头模式，不显示窗口 |
| `--no-sandbox` | 禁用沙箱（容器/VPS环境必需） |
| `--disable-gpu` | 禁用GPU加速（服务器环境） |
| `--screenshot=路径` | 输出PNG路径 |
| `--window-size=W,H` | 视口尺寸（应与HTML的body尺寸匹配） |
| `--default-background-color=000000` | 可选，强制背景色 |

## 已知限制

- 文件路径必须在用户家目录：snap版 Chrome 不能读写 /tmp
- 生成的 PNG 不可交互（纯静态图片）
- 复杂 CSS 动画/动态内容不会渲染（截图是单帧）
- 中文字体依赖系统安装的字体（fonts-wqy-zenhei / fonts-noto-cjk）
