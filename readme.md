# Deep Research Agent

![Deep Research Agent](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-1.0%2B-purple.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0%2B-red.svg)

一个类似 ChatGPT Deep Research 的 AI 深度研究智能体，能够自主进行多步骤网络搜索、推理分析，并生成结构化研究报告。

---

## 📋 项目介绍

### 什么是 Deep Research Agent？

Deep Research Agent 是一款基于大语言模型的**自主研究智能体**，它模拟了人类研究人员的工作流程：

1. **理解问题** → 将复杂问题分解为结构化的研究计划
2. **收集信息** → 通过搜索引擎获取最新、最相关的资料
3. **分析验证** → 对收集到的信息进行交叉验证和深度分析
4. **生成报告** → 输出专业、结构化的研究报告

### 为什么选择 Deep Research Agent？

- **智能规划**：自动将复杂问题分解为可执行的研究步骤
- **多轮迭代**：不同于传统 RAG 的单次查询，采用多轮搜索策略
- **信息评估**：自动判断信息充足性，动态调整搜索策略
- **结构化输出**：生成包含引言、方法、发现、讨论和参考文献的完整报告
- **可视化界面**：提供 Streamlit Web UI，支持实时进度展示

### 应用场景

- 📚 **学术研究**：辅助论文写作和文献综述
- 💼 **商业分析**：市场调研和竞争分析
- 📰 **新闻聚合**：快速了解某个话题的最新动态
- 🎯 **决策支持**：为决策提供全面的信息支撑

---

## ✨ 核心功能

| 功能 | 说明 |
|------|------|
| **智能查询规划** | 将复杂问题自动分解为研究大纲和搜索关键词 |
| **多轮迭代搜索** | 根据分析结果动态调整搜索关键词，深度挖掘信息 |
| **网页内容提取** | 自动提取网页中的主要内容，过滤噪音 |
| **信息质量评估** | 评估搜索结果的充足性，决定是否继续搜索 |
| **结构化报告生成** | 输出包含引言、方法、核心发现、讨论、结论和参考文献的完整报告 |
| **LangGraph 工作流** | 基于 LangGraph 的状态图工作流，支持条件路由和检查点 |

---

## 🔄 核心架构

### 原始模式架构

系统遵循"搜索 → 阅读 → 推理 → 生成"的核心循环：

```
用户问题
    ↓
查询规划器 (Query Planner)
    ↓ 生成研究大纲和搜索关键词
搜索引擎 (Search Engine)
    ↓ 获取网页搜索结果
内容提取器 (Content Extractor)
    ↓ 提取网页文本内容
推理引擎 (Reasoning Engine)
    ↓ 分析信息、评估充足性
[信息不足？] → 是 → 返回继续搜索
    ↓ 否
报告生成器 (Report Generator)
    ↓
结构化研究报告 + 引用来源
```

### LangGraph 模式架构

基于 LangGraph 的状态图工作流：

```
┌─────────────┐
│   Start     │
└──────┬──────┘
       ↓
┌─────────────┐
│ plan_node   │ ← 查询规划
└──────┬──────┘
       ↓
┌─────────────┐
│ search_node │ ← 网络搜索
└──────┬──────┘
       ↓
┌─────────────┐
│analyze_node │ ← 分析综合
└──────┬──────┘
       ↓
  ┌────┴────┐
  ↓         ↓
[继续搜索]  [生成报告]
  ↓         ↓
search_node report_node
  ↓         ↓
  └────┬────┘
       ↓
    End
```

---

## 🌟 功能亮点

### 智能查询规划
- 将复杂问题分解为 3-6 个章节的研究大纲
- 生成 5-10 个搜索关键词，覆盖问题的各个方面

### 多轮迭代搜索
- 支持最多 5 轮搜索迭代
- 根据分析结果动态调整搜索关键词
- 信息充足时自动停止搜索

### 信息质量评估
- 评估当前信息的充足性（充足/部分充足/不足）
- 列出已获取的关键信息和缺失信息
- 生成新的搜索关键词建议

### 结构化报告生成
- 包含引言、研究方法、核心发现、分析讨论、结论、参考文献
- 每个关键结论都有来源支持
- 支持报告下载

### LangGraph 模式优势
| 特性 | 原始模式 | LangGraph 模式 |
|------|---------|---------------|
| 状态管理 | 类属性 | TypedDict，清晰定义 |
| 流程控制 | while 循环 | 条件边，可视化 |
| 扩展性 | 代码修改 | 添加节点/边 |
| 检查点 | 不支持 | 支持中断/恢复 |
| Human-in-the-loop | 不支持 | 支持 |

---

## 🛠️ 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| **语言** | Python 3.10+ | 核心开发语言 |
| **大语言模型** | OpenAI API 兼容模型 | 支持 DeepSeek、Qwen2、TJU-LLM 等 |
| **搜索引擎** | Tavily Search API | 专为 AI Agent 设计的搜索引擎 |
| **网页解析** | BeautifulSoup4 | HTML 内容提取 |
| **工作流框架** | LangGraph | 状态图工作流管理 |
| **Web UI** | Streamlit | 快速原型开发 |
| **配置管理** | python-dotenv | 环境变量管理 |

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/your-username/Deep_Research_Agent.git
cd Deep_Research_Agent

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API 密钥

复制 `.env.example` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# LLM API 配置
LLM_API_KEY=your-llm-api-key
LLM_BASE_URL=https://api.deepseek.com/v1  # 或其他 OpenAI 兼容端点
LLM_MODEL=deepseek-chat

# Tavily 搜索 API 配置（需从 https://tavily.com 获取）
TAVILY_API_KEY=your-tavily-api-key

# 日志配置
LOG_LEVEL=INFO
```

**示例配置（天津大学 TJU-LLM）**：

```env
LLM_API_KEY=your-tju-llm-key
LLM_BASE_URL=https://ai.tju.edu.cn/api/v3
LLM_MODEL=tju-llm
```

> ⚠️ 注意：TJU-LLM 需要在天津大学校园网或 VPN 环境下访问

### 3. 运行方式

#### 命令行模式（原始实现）

```bash
python main.py
```

#### 命令行模式（LangGraph）

```bash
python langgraph_agent.py
```

#### Web UI 模式

```bash
streamlit run ui.py
```

在 Web UI 中可以选择运行模式：
- **原始模式**：使用传统的循环实现
- **LangGraph 模式**：使用状态图工作流

**首次启动提示**：Streamlit 首次启动会询问邮箱，直接按 Enter 跳过即可。

---

## 📁 项目结构

```
Deep_Research_Agent/
├── .env                    # 环境变量配置
├── .env.example            # 环境变量模板
├── .gitignore              # Git 忽略配置
├── requirements.txt        # 依赖列表
├── readme.md               # 项目说明
├── __init__.py             # 包初始化
├── config.py               # 配置管理模块
├── main.py                 # 核心研究逻辑（原始实现）
├── langgraph_agent.py      # LangGraph 实现
└── ui.py                   # Streamlit Web UI
```

### 文件说明

| 文件 | 职责 |
|------|------|
| `config.py` | 加载和管理环境变量配置 |
| `main.py` | DeepResearchAgent 核心类，原始循环实现 |
| `langgraph_agent.py` | LangGraph 状态图实现，支持条件路由 |
| `ui.py` | Streamlit Web 界面，支持模式切换 |

---

## 🧪 使用示例

### 输入示例

```
分析人工智能在医疗领域的应用现状和未来趋势
```

### 输出示例

系统会生成类似以下结构的研究报告：

```markdown
# 深度研究报告

**研究问题**: 分析人工智能在医疗领域的应用现状和未来趋势

**生成时间**: 2024-01-15 10:30:00

---

## 1. 引言

随着人工智能技术的快速发展，医疗领域正经历着深刻的变革...

## 2. 研究方法

本报告通过多轮网络搜索，收集了来自学术论文、行业报告和新闻媒体的信息...

## 3. 核心发现

### 3.1 诊断辅助
- 人工智能在医学影像诊断中的准确率已达到或超过人类专家水平

### 3.2 药物研发
- AI 加速了药物分子的设计和筛选过程...

## 4. 分析与讨论

虽然人工智能在医疗领域取得了显著进展，但仍面临数据隐私、监管合规等挑战...

## 5. 结论

人工智能正在深刻改变医疗行业，未来将在个性化医疗、精准诊断等方面发挥更大作用...

## 6. 参考文献

1. [来源标题](https://example.com)
2. [来源标题](https://example.com)
...
```

---

## ⚠️ 已知限制

1. **API 密钥需求**：需要有效的 LLM API 密钥才能正常运行，Tavily API 密钥为可选
2. **网络依赖**：依赖外部搜索引擎和 LLM API，需要稳定的网络连接
3. **内容提取**：部分网页可能存在反爬机制，导致内容提取失败
4. **报告质量**：报告质量受限于所用 LLM 模型的能力和搜索结果的质量
5. **校园网限制**：某些 LLM API（如 TJU-LLM）可能需要特定网络环境

---

## 🛑 故障排除

### Streamlit 首次启动问题

**问题**：启动时出现邮箱输入提示，阻塞进程

**解决**：直接按 Enter 键跳过即可

### API 密钥错误

**问题**：收到 "Invalid API key" 或认证失败错误

**解决**：
- 确保 `.env` 文件中的 API 密钥正确
- Tavily API 密钥需要从 [tavily.com](https://tavily.com) 单独获取，不能复用 LLM 密钥

### LLM 端点兼容性

**问题**：LLM 调用失败，提示 API 格式不兼容

**解决**：
- 确保使用的 LLM 端点支持 OpenAI API 格式
- 可以通过以下命令测试：

```bash
python -c "
from openai import OpenAI
client = OpenAI(api_key='your-key', base_url='your-url')
response = client.chat.completions.create(
    model='your-model',
    messages=[{'role': 'user', 'content': 'hello'}]
)
print(response.choices[0].message.content)
"
```

### 网络连接问题

**问题**：无法连接到 LLM API 服务器

**解决**：
- 检查网络连接
- 如果使用校园网 API（如 TJU-LLM），确保连接了校园网或 VPN

---

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

*本项目为学习研究目的开发，请勿用于商业用途。*