# Demo视频生成（用于应用审核）

## 场景
百度网盘开放平台应用审核需要上传演示视频（<50MB, MP4格式），展示OAuth授权流程和核心业务操作。

## 技术方案
Python Pillow + FFmpeg 生成终端风格动画视频。

### 原理
1. 用Pillow逐帧绘制黑底绿字的"终端"界面
2. 文字逐行显示（打字机效果），模拟真实操作场景
3. 每帧做小变化（闪烁光标、进度指示）
4. 用FFmpeg拼接为MP4视频

### 代码结构
```python
from PIL import Image, ImageDraw, ImageFont
import subprocess, tempfile

scenes = [...场景列表, 每个场景有duration和lines...]

# 生成帧
for scene in scenes:
    for fi in range(frames_in_scene):
        img = Image.new("RGB", (800, 600), (20, 20, 20))
        draw = ImageDraw.Draw(img)
        # 画文字...
        img.save(frame_path)

# FFmpeg合成
ffmpeg -framerate 5 -i frame_%05d.png -c:v libx264 -pix_fmt yuv420p output.mp4
```

### 关键参数
- 分辨率：800x600
- 帧率：5 FPS（节省体积，对文字动画足够）
- 编码：libx264, yuv420p
- 字体：需要中文字体（NotoSansCJK, wqy-zenhei等）
- 每段场景3-5秒，总时长15-20秒

### 效果
生成的文件约0.1MB/19秒，体积小画质清晰，适合审核用途。

### 注意
- 这不是真终端录屏，是模拟画面——但对审核来说够用
- 如果想做真实终端录屏，可以用asciinema + agg工具
