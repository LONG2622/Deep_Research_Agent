# Deep Research Agent

一个类似 ChatGPT Deep Research 的 AI 深度研究智能体，能够自主进行多步骤网络搜索、推理分析，并生成结构化研究报告。

## ✨ 简介

Deep Research Agent 是一款基于大语言模型的智能研究工具，能够：

- 🧠 **自主规划**：将复杂研究问题分解为可执行的研究计划
- 🔍 **多轮搜索**：通过搜索引擎获取最新、最相关的信息
- 📖 **内容提取**：自动阅读和提取网页中的关键信息
- 📊 **深度分析**：对收集到的信息进行交叉验证和推理分析
- 📝 **生成报告**：输出结构化、带有引用来源的专业研究报告

## 🔄 核心架构

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

## 🌟 功能亮点

| 功能 | 说明 |
|------|------|
| **多轮迭代搜索** | 不同于传统 RAG 的单次查询，本项目采用多轮搜索策略，根据分析结果动态调整搜索关键词 |
| **智能查询规划** | 将复杂问题自动分解为研究大纲和搜索关键词，覆盖问题的各个方面 |
| **信息质量评估** | 自动评估搜索结果的充足性，决定是否需要继续搜索 |
| **结构化报告生成** | 输出包含引言、方法、核心发现、讨论、结论和参考文献的完整报告 |
| **实时进度展示** | Web UI 提供实时进度条和中间结果展示 |

## 🛠️ 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| **语言** | Python 3.10+ | 核心开发语言 |
| **大语言模型** | OpenAI API 兼容模型 | 支持 DeepSeek、Qwen2 等 |
| **搜索引擎** | Tavily Search API | 专为 AI Agent 设计的搜索引擎 |
| **网页解析** | BeautifulSoup4 | HTML 内容提取 |
| **Web UI** | Streamlit | 快速原型开发 |
| **配置管理** | python-dotenv | 环境变量管理 |

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

### 3. 运行方式

#### 命令行模式

```bash
python main.py
```

#### Web UI 模式

```bash
streamlit run ui.py
```

**首次启动提示**：Streamlit 首次启动会询问邮箱，直接按 Enter 跳过即可。

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
├── main.py                 # 核心研究逻辑
└── ui.py                   # Streamlit Web UI
```

### 文件说明

| 文件 | 职责 |
|------|------|
| `config.py` | 加载和管理环境变量配置 |
| `main.py` | DeepResearchAgent 核心类，实现研究循环 |
| `ui.py` | Streamlit Web 界面，提供可视化交互 |

## ⚠️ 已知限制

1. **API 密钥需求**：需要有效的 LLM API 密钥和 Tavily API 密钥才能正常运行
2. **网络依赖**：依赖外部搜索引擎，需要稳定的网络连接
3. **内容提取**：部分网页可能存在反爬机制，导致内容提取失败
4. **报告质量**：报告质量受限于所用 LLM 模型的能力和搜索结果的质量

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

## 📄 输出示例

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

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

*本项目为学习研究目的开发，请勿用于商业用途。*