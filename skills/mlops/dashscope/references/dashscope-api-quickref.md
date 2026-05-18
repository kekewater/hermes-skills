# DashScope API Quick Reference

## Image Generation — Quick Snippet

```python
import cloudscraper, json, time, os, requests

SCRAPER = cloudscraper.create_scraper()
API_KEY = os.getenv('DASHSCOPE_API_KEY')

def generate_image(prompt: str, model: str = "wanx2.1-t2i-turbo") -> bytes:
    """提交通义万相异步任务并等待结果，返回图片二进制数据"""
    # 提交
    resp = SCRAPER.post(
        'https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis',
        headers={
            'Authorization': f'Bearer {API_KEY}',
            'X-DashScope-Async': 'enable'
        },
        json={
            'model': model,
            'input': {'prompt': prompt},
            'parameters': {'n': 1, 'size': '1024*1024'}
        }
    )
    task_id = resp.json()['output']['task_id']
    
    # 轮询
    for _ in range(10):
        time.sleep(5)
        resp = SCRAPER.get(
            f'https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}',
            headers={'Authorization': f'Bearer {API_KEY}'}
        )
        result = resp.json()
        status = result['output']['task_status']
        if status == 'SUCCEEDED':
            url = result['output']['results'][0]['url']
            return requests.get(url).content
        elif status == 'FAILED':
            raise RuntimeError(f"任务失败: {result.get('code')} {result.get('message')}")
    raise TimeoutError("任务超时")
```

## Vision Analysis — Quick Snippet (Primary: Qwen-VL-Max)

```python
import base64, json, requests

def analyze_image(image_path: str, question: str = "描述这张图片") -> str:
    """用qwen-vl-max分析图片"""
    with open(image_path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode()
    
    resp = requests.post(
        'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
        headers={
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json'
        },
        json={
            'model': 'qwen-vl-max',
            'messages': [{
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': question},
                    {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{b64}'}}
                ]
            }]
        }
    )
    return resp.json()['choices'][0]['message']['content']
```

## Vision Analysis — Fallback (GLM-4V-Plus)

当 Qwen-VL-Max 返回 `unknown variant \`image_url\`, expected \`text\`` 错误时，切换至智谱 GLM-4V-Plus：

```python
def analyze_image_glm(image_path: str, question: str = "描述这张图片") -> str:
    """用GLM-4V-Plus分析图片（Qwen-VL-Max的备用方案）"""
    import os
    GLM_API_KEY = os.getenv('GLM_API_KEY')  # 或硬编码 static key
    
    with open(image_path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode()
    
    resp = requests.post(
        'https://open.bigmodel.cn/api/paas/v4/chat/completions',
        headers={
            'Authorization': f'Bearer {GLM_API_KEY}',
            'Content-Type': 'application/json'
        },
        json={
            'model': 'glm-4v-plus',
            'messages': [{
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': question},
                    {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{b64}'}}
                ]
            }]
        },
        timeout=30
    )
    return resp.json()['choices'][0]['message']['content']
```

两套API使用完全相同的 `data:image/jpeg;base64,{b64}` 格式，可直接替换。

## Hermes Config Integration

```yaml
# ~/.hermes/config.yaml
auxiliary:
  vision:
    provider: dashscope
    model: qwen-vl-max
```

## Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| `InvalidParameter` | 参数错误（常见于size格式） | 检查size用`1024*1024` |
| `AccessDenied` | API Key无权限 | 检查Key是否开通了该模型服务 |
| `Throttling.RateQuota` | 短时间高频请求触发（约3-5次/分钟） | 停止请求15-30秒再试 |
| `RequestTooLarge` | 图片base64数据过大 | 压缩图片至2MB以下 |
| `TaskNotFound` | task_id无效 | 检查task_id是否拼写错误 |
