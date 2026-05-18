# DeepSeek 前缀缓存机制与优化策略

来源：Keke提供的DeepSeek官方文档研究（2026-05-17）

## 缓存工作原理

### 核心机制：前缀精确匹配（Prefix-Match）

DeepSeek V4 Flash的缓存基于**前缀匹配**，不是基于时间TTL。

```
请求A: "System: 你是助手... User: 帮我查股票 ABC..."
       ↑ 缓存命中 (system prompt完全匹配)
                    ↑ 缓存命中 (前段对话相同)
                               ↑ 缓存未命中 (新问题)
```

- **64-token粒度**：缓存以64 tokens为最小块。
- **前缀必须从头开始**：只有从头开始的连续token序列能命中。
- **跨会话共享**：同一system prompt在不同会话间复用缓存。

### 缓存区间段（Evaluation Window）

缓存以**4K tokens为一个评估段**。前4K tokens被检查最频繁。

## 优化策略

### 1. System Prompt前置

静态内容前置，动态内容后置。

```
✅ [静态: persona] [静态: 工具定义] [可变: memory] [可变: 会话]
❌ [可变: 时间戳] [静态: persona] ← 前4K含可变→缓存全部失效
```

### 2. 前4K tokens最重要

前4000 tokens是缓存收益最高的区域，必须全部是静态内容。

### 3. 避免动态指令

不要在system prompt头部插入时间戳、会话ID。改从user message传入。

### 4. 稳定tool definitions

修改工具schema会使整个system prompt缓存失效。

## 实测结果

| 指标 | 数值 |
|------|------|
| 命中率 | **94.3%** (5天8,122次) |
| 日均费用 | **¥13.91** |
| 费用大头 | cache miss input占68% |

**关键：降费最佳方法是减少cache miss体积，不是提高命中率。**

### 优化实践

1. 合并terminal命令（`&&`链式），减少API轮次
2. 读文件用offset/limit截断
3. 搜索用grep/search_files代替全读
4. terminal输出大时pipe head -50

参考：DeepSeek Platform Docs (2026-05-17) · Keke
