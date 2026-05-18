# Featherless AI 写作相关资源笔记

来源：https://featherless.ai/blog （2026年5月）

---

## 1. OpenElla-NovelWriter-8B-merged 模型

- **模型链接**: https://featherless.ai/models/N-Bot-Int/OpenElla-NovelWriter-8B-merged
- **HuggingFace**: N-Bot-Int/OpenElla-NovelWriter-8B-merged
- **架构**: Llama 3.1 8B，FP8量化
- **基座**: p-e-w/Llama-3.1-8B-Instruct-heretic
- **数据集**: RPG Mixed V1-V2-V3（角色扮演混合内容）
- **训练工具**: Unsloth + Huggingface TRL（加速训练）
- **上下文**: 8K tokens
- **许可证**: AGPL-3.0
- **状态**: 实验性模型，尚未部署在Featherless上
- **用途**: 创意写作、叙事生成、角色对话、文本冒险
- 适合用于小说创作中的剧情构建和角色扮演场景

## 2. 写作工具集成方案

**NovelCrafter + Featherless AI**
- NovelCrafter是专门为长篇小说设计的写作平台（大纲、角色管理、场景写作）
- 原生支持Featherless集成（直接选Provider即可）
- 可以在同一项目中切换不同模型，为不同角色/场景找到合适的AI"缪斯"

**Mikupad + Featherless AI**
- 轻量级浏览器端LLM前端（单个HTML文件运行）
- 适合快速实验、写作测试
- 配置：Server = https://api.featherless.ai/v1, API = OpenAI Compatible

## 3. Prompt Engineering 核心框架：CLEAR

| 要素 | 说明 |
|------|------|
| **C**ontext | 提供必要的背景信息 |
| **L**ength | 指定期望的输出长度 |
| **E**xamples | 包含相关演示/样例 |
| **A**udience | 定义目标受众 |
| **R**ole | 建立AI角色/身份 |

**低质量 prompt**："写个函数排序数据"
**高质量 prompt**："写一个TypeScript函数，接收包含'name'和'age'属性的对象数组，按age升序排序，返回新数组不修改原数组，包含完整类型注解，处理空数组和null值等边界情况"

## 4. Context Engineering（上下文工程）

Andrej Karpathy定义："上下文工程是以恰到好处的信息填充上下文窗口的微妙艺术和科学"

**两层架构**：
- **确定性上下文**：开发者直接控制（prompts、文档、系统指令）
- **概率性上下文**：AI自主发现和整合（网页搜索、数据库查询、检索文档）

**四种上下文管理策略**：
1. **Writing**：在上下文窗口外保存信息（scratchpads、memory blocks）
2. **Pulling**：将相关信息拉入上下文窗口
3. **Compressing**：只保留必要token
4. **Isolating**：将复杂上下文拆分为多个专用agent

**RAG模式**：small-to-big检索、parent document检索、多模态RAG

## 5. 对历史故事写作的启发

- 用CLEAR框架构造写作prompt：明确Context（历史背景）、Role（叙事者角色）、Audience（AI Agent读者）、Length（字数控制）、Examples（风格示范）
- Context Engineering思路：历史故事需要丰富的背景知识注入（时代背景、人物关系、历史事件），可采用检索增强确保史实准确
- 可考虑用NovelCrafter/Mikupad等专业写作工具辅助长篇小说创作
