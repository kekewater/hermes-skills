# Hermes Agent 技能包 - 墨渊Flux同款配置 🚀

## 快速开始

```bash
# 1. 安装 Hermes Agent
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# 2. 下载本技能包
# (把这个目录打包发给对方)

# 3. 复制技能到Hermes目录
cp -r skills/* ~/.hermes/skills/

# 4. 配置API Key
cp config.yaml ~/.hermes/config.yaml
# 然后编辑 config.yaml 填入你的API Key

# 5. 启动
hermes
```

## 内置技能清单（195个）

### 📈 金融分析（84个）
基础数据：A股行情、美股数据、Tushare Pro MCP
分析框架：10个投行/PE/基金会计Agent模板
66个专业方法论：DCF估值、Comps可比分析、LBO、盈利分析等
日报系统：每日投资日报自动生成

### 🎨 创意设计（20个）
小说写作、历史故事、漫画/信息图生成、ASCII艺术、手绘图表

### 🔧 开发运维（12个）
系统调试、代理隧道、云存储备份、API用量监控

### 🤖 AI/ML（14个）
阿里云百炼(TTS/生图)、本地LLM推理、模型微调、HuggingFace

### 💻 软件开发（12个）
浏览器自动化、TDD、代码审查、系统调试

### 📱 社交（4个）
Moltbook、The Colony、InStreet、X/Twitter

### 📊 生产力（10个）
Excel分析、PPT制作、OCR文档、读书俱乐部

### 其他（39个）
邮件、研究、媒体处理、GitHub工具等

## API Key 获取指南

| 服务 | 用途 | 获取地址 | 推荐 |
|------|------|---------|------|
| DeepSeek | 日常对话（便宜） | platform.deepseek.com | ⭐ 首选 |
| OpenAI | 生图/备用 | platform.openai.com | 需翻墙 |
| OpenRouter | Claude/多模型 | openrouter.ai | 免KYC |
| 阿里云百炼 | TTS语音/生图 | dashscope.console.aliyun.com | 国内直连 |

## 切换模型

```bash
hermes model           # 交互式选择
hermes chat -p "..."   # 用默认模型对话
```

## 加载技能

对话中输入：
```
/skill <技能名>
```

或在启动时：
```bash
hermes -s comps-analysis -s dcf-model
```
