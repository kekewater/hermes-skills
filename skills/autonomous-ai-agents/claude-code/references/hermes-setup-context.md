# Claude Code — Hermes 环境配置参考

## 当前状态（2026-05-18）

| 项目 | 状态 |
|------|------|
| Claude Code 安装 | ❌ 未安装（npm 可用） |
| ANTHROPIC_API_KEY | ❌ 未设置 |
| Claude 订阅 | 需 Keke 确认（Pro/Max/API） |
| OAuth 登录 | 浏览器交互不可行（无图形终端） |

## 安装命令

```bash
npm install -g @anthropic-ai/claude-code
```

## 认证方式

### 方式A：API Key（推荐，适合 Hermes 自动化）

1. 用户上 console.anthropic.com → Settings → API Keys → 创建新 Key
2. Keke 将 Key 发来后，存入 `~/.hermes/credentials.json` 或设为环境变量
3. 在 Hermes 配置中设置: 参考 `~/.hermes/config.yaml` 的 `ENV.ANTHROPIC_API_KEY` 字段
4. 验证: `ANTHROPIC_API_KEY=sk-ant-... claude -p "Hello" --bare`

### 方式B：OAuth 登录（需订阅）

```bash
# 需要用户打开浏览器登录 Cli
claude auth login --console
# 然后输入 OAuth token
```

## Hermes 集成方式

### 方式1：Print Mode（单次任务，推荐）

```python
terminal("ANTHROPIC_API_KEY=... claude -p '分析这份数据' --allowedTools 'Read,Edit' --max-turns 10")
```

### 方式2：ACP 子Agent通道

修改 `config.yaml` 的 `acp_command` 字段指向 Claude：

```yaml
delegation:
  acp_command: claude  # 替换默认的子Agent提供方
  acp_environment:
    ANTHROPIC_API_KEY: "sk-ant-..."
```

### 方式3：delegate_task 临时指定

```python
delegate_task(
    tasks=[{..., acp_command="ANTHROPIC_API_KEY=... claude"}]
)
```

## 与 Anthropic 框架的关系

Keke 安装的 66 个 Anthropic financial-services 技能（`~/.hermes/skills/financial/anthropic-*`）原始指令针对 Claude 编写（引用 CapIQ MCP / FactSet MCP 等）。用 Claude Code 运行它们效果最好，因为：

- Claude 天然理解原版 prompt 中的 CapIQ/FactSet 指令
- 不需要像在 DeepSeek 上那样手动替换数据源

但注意：即使 Claude 理解指令，实际数据源（CapIQ/FactSet MCP）我们仍然没有。Claude 只是能更好理解"你要我做什么"，但拉数据还是要靠我们自己的数据接入。

## 成本考虑

- Claude Sonnet: $3.00/百万输出tokens（vs DeepSeek ¥2.00 ≈ $0.28）
- Claude Opus: $15.00/百万输出tokens
- 约 DeepSeek 的 10-50 倍成本
- 仅在复杂金融分析场景值得用 Claude
- 日常对话继续用 DeepSeek 省钱
