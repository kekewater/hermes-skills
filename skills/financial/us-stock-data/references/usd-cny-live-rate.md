# USD/CNY 实时汇率获取

## API: open.er-api.com (免费，国内直连)

```python
import requests

r = requests.get('https://open.er-api.com/v6/latest/USD', timeout=5)
data = r.json()
if data.get('result') == 'success' and 'CNY' in data.get('rates', {}):
    rate = round(data['rates']['CNY'], 4)
    # rate ≈ 6.8180
```

- **国内直连**: ✅ 可用，无需代理
- **免费**: ✅ 无需API Key
- **限流**: 无公开限制，保守每5分钟查一次
- **缓存**: 建议本地缓存5-10分钟，避免每次请求都重复调用

## 带缓存的完整函数

```python
_rate_cache = {'rate': 6.83, 'time': 0}

def get_usd_cny():
    import time
    now = time.time()
    if now - _rate_cache['time'] < 300:
        return _rate_cache['rate']
    try:
        r = requests.get('https://open.er-api.com/v6/latest/USD', timeout=5)
        data = r.json()
        if data.get('result') == 'success' and 'CNY' in data.get('rates', {}):
            _rate_cache['rate'] = round(data['rates']['CNY'], 4)
            _rate_cache['time'] = now
    except:
        pass  # 用上次缓存值（或初始值6.83）
    return _rate_cache['rate']
```

## 备选源

- **AKShare**: `ak.currency_boc_safe()` — 中国银行中间价（直连，但接口参数有变动，2026-05-18测试时报错）
- **Alpha Vantage**: `CURRENCY_EXCHANGE_RATE` — 需API Key，25次/天
- **exchangerate.host**: 另一个免费API，备选

## 在报表/看板中使用

H5看板中已集成在 `portfolio_h5.py` 的 `get_usd_cny()` 函数，显示在页面右上角。
