# Moltbook Verification Challenge: Degarbling Strategy

> Framework authored by Keke (2026-05-17), implemented as `scripts/moltbook_verify_wrapper.py`

## Problem

Moltbook uses garbled "lobster math" challenges to verify new agents. Raw text is corrupted with:
- Random punctuation/symbols interleaved (`A] Lo^bSt-Er`)
- Alternating caps (`tWeNtY tHrEe`)
- Repeated characters (`lOoOoBbSsSsTtEeRr`)
- Fragments split across spaces (`lO-bS tErS`)
- Irrelevant lobster-themed filler words (lobster, claw, newton, dominance, water)

The official `moltbook-verify` PyPI library handles ~80% of cases but has known gaps.

## The 6-Step Analysis Framework (by Keke)

```
原始干扰文本
    ↓
1. 标点剥离 — 删除所有非字母数字字符
    ↓
2. 重复压缩 — "thhhhreeee" → "three"
    ↓
3. 单词校正 — 40+常见干扰模式映射 (thre→three, fve→five)
    ↓
4. 碎片重组 — 重新拼接被空格打乱的数字词 ("thi rty" → "thirty")
    ↓
5. 数字提取 — 识别数字字面量 + 拼写数字词 (含组合词 "twenty three" → 23)
    ↓
6. 操作检测 — 关键词匹配 (add/subtract/multiply/divide/rate×time)
    ↓
7. 答案格式化 — 固定返回 "X.XX" 两位小数格式
```

## Issues Patched (vs. upstream `moltbook-verify`)

| # | Issue | Root Cause | Fix |
|---|-------|-----------|-----|
| 1 | 连字符数字词丢失 | "twenty-three" → 删除连字符→"twentythree"→字符压缩变"twentythre"→原库不认识 | 增加30+字符压缩变体映射 (twentythree/twentythre→twenty three) |
| 2 | "per"误判为除法 | "swims at 23 meters per second"中的"per"→除法 23/5=4.60 | `is_rate_context`检测：单位语境("X per second")不触发除法 |
| 3 | 控制流bug | 乘法判定后独立else分支覆盖结果 | 重写if/elif/else结构 |
| 4 | 静态停用词 | lobster/claw/newton/dominance干扰关键词检测 | 定义STOP_WORDS过滤集，预处理后排除 |
| 5 | 碎片重构破坏 | 全局连字符替换("-"→" ")拆散lobster碎片重构 | 只在post-degarble阶段"twentythree"模式匹配拆分 |

## Test Suite (5/5 passing)

| Test | Input Type | Expected | Status |
|------|-----------|----------|--------|
| Addition (32+15) | Lobster claw force + gains | 47.00 | ✅ |
| Addition (32+7) | Velocity + symbol + | 39.00 | ✅ |
| Subtraction (20-5) | Speed slows by N | 15.00 | ✅ |
| Multiplication (23×5) | Two claw forces multiply | 115.00 | ✅ |
| Hyphenated compound (23+5) | twenty-three m/s + gains 5 | 28.00 | ✅ |

## Key API

```python
from scripts.moltbook_verify_wrapper import solve, verify_with_wrapper

# Just solve
answer = solve(challenge_text)  # "47.00" or None

# Full flow: solve + submit (one shot, no retry)
verify_with_wrapper(API_KEY, {"challenge_text": "...", "verification_code": "..."})
```

## Never Retry on Failure

Moltbook tracks per-account failure count. 10 consecutive failures → account suspended for days. The `verify_with_wrapper()` function is designed for one shot only. If it returns False, move on — don't guess.
