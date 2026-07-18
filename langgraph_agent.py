"""
Deep Research Agent LangGraph 实现
使用 LangGraph 重构原有的研究工作流
"""

import json
import logging
from typing import List, Dict, Any, TypedDict, Literal
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from tavily import TavilyClient
from langgraph.graph import StateGraph, END

from config import config

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ResearchState(TypedDict):
    query: str
    plan: Dict[str, Any]
    search_queries: List[str]
    current_iteration: int
    search_results: List[Dict[str, Any]]
    research_history: List[Dict[str, Any]]
    analysis: str
    should_continue: bool
    final_report: str


class ResearchNodes:
    def __init__(self):
        self.llm_client = OpenAI(
            api_key=config.LLM_API_KEY,
            base_url=config.LLM_BASE_URL
        )
        self.search_client = TavilyClient(api_key=config.TAVILY_API_KEY) if config.TAVILY_API_KEY else None

    def _call_llm(self, messages: List[Dict[str, str]], model: str = None, max_tokens: int = 4096) -> str:
        try:
            response = self.llm_client.chat.completions.create(
                model=model or config.LLM_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            raise

    def extract_content(self, url: str) -> str:
        logger.info(f"正在提取网页内容: {url}")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
            if main_content:
                text = main_content.get_text(separator='\n', strip=True)
            else:
                text = soup.get_text(separator='\n', strip=True)
            clean_text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
            return clean_text[:3000]
        except Exception as e:
            logger.error(f"网页内容提取失败: {e}")
            return ""

    def plan_node(self, state: ResearchState) -> Dict[str, Any]:
        logger.info(f"开始查询规划: {state['query']}")
        prompt = f"""
你是一个专业的研究规划师。请分析以下研究问题，并生成详细的研究计划。

研究问题：{state['query']}

请按照以下 JSON 格式输出：
{{
  "research_outline": ["章节1标题", "章节2标题", ...],
  "search_queries": ["搜索关键词1", "搜索关键词2", ...],
  "estimated_iterations": 预估需要的研究迭代次数
}}

要求：
1. research_outline 应该包含 3-6 个章节，覆盖问题的主要方面
2. search_queries 应该包含 5-10 个搜索关键词，覆盖各个章节
3. estimated_iterations 应该是 2-4 之间的整数
"""
        messages = [{"role": "user", "content": prompt}]
        response = self._call_llm(messages)
        try:
            if "{" in response and "}" in response:
                start = response.index("{")
                end = response.rindex("}") + 1
                plan = json.loads(response[start:end])
            else:
                plan = {
                    "research_outline": ["引言", "核心分析", "结论"],
                    "search_queries": [state['query']],
                    "estimated_iterations": 2
                }
        except json.JSONDecodeError:
            plan = {
                "research_outline": ["引言", "核心分析", "结论"],
                "search_queries": [state['query']],
                "estimated_iterations": 2
            }
        logger.info(f"研究计划生成完成: {plan['research_outline']}")
        return {
            "plan": plan,
            "search_queries": plan.get("search_queries", [state['query']]),
            "current_iteration": 0,
            "research_history": []
        }

    def search_node(self, state: ResearchState) -> Dict[str, Any]:
        queries = state['search_queries']
        iteration = state['current_iteration']
        if iteration < len(queries):
            search_query = queries[iteration]
        else:
            if state['research_history'] and state['analysis']:
                analysis = state['analysis']
                if "建议的搜索关键词" in analysis:
                    start = analysis.index("建议的搜索关键词") + len("建议的搜索关键词")
                    search_query = analysis[start:].strip().split('\n')[0]
                else:
                    return {"search_results": [], "should_continue": False}
            else:
                return {"search_results": [], "should_continue": False}
        logger.info(f"正在搜索 (迭代 {iteration + 1}): {search_query}")
        if not self.search_client:
            logger.warning("未配置 Tavily 搜索 API，跳过搜索")
            return {"search_results": [], "should_continue": False}
        try:
            results = self.search_client.search(
                query=search_query,
                max_results=config.MAX_SEARCH_RESULTS,
                search_depth="advanced"
            )
            search_results = results.get("results", [])
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            search_results = []
        return {
            "search_results": search_results,
            "current_iteration": iteration + 1
        }

    def analyze_node(self, state: ResearchState) -> Dict[str, Any]:
        logger.info("正在分析搜索结果")
        formatted_results = ""
        for i, result in enumerate(state['search_results'], 1):
            content = self.extract_content(result.get("url", ""))
            if content:
                formatted_results += f"""
来源 {i}:
标题: {result.get("title", "")}
URL: {result.get("url", "")}
摘要: {result.get("content", "")}
详细内容: {content[:500]}
---
"""
        prompt = f"""
你是一个专业的研究分析师。请分析以下搜索结果，并判断是否足以回答研究问题。

研究问题：{state['query']}

搜索结果：
{formatted_results}

请按照以下格式输出：
1. 当前信息评估：(充足/部分充足/不足)
2. 已获取的关键信息：列出3-5条关键发现
3. 缺失的信息：如果信息不足，请列出还需要获取的信息
4. 是否需要继续搜索：(是/否)
5. 如果需要继续搜索，建议的搜索关键词：列出2-3个新关键词
"""
        messages = [{"role": "user", "content": prompt}]
        analysis = self._call_llm(messages)
        should_continue = False
        if "是否需要继续搜索：是" in analysis and state['current_iteration'] < config.MAX_RESEARCH_ITERATIONS:
            should_continue = True
        elif "信息评估：不足" in analysis and state['current_iteration'] < config.MAX_RESEARCH_ITERATIONS:
            should_continue = True
        research_history = state['research_history'].copy()
        research_history.append({
            "iteration": state['current_iteration'],
            "search_query": state['search_queries'][state['current_iteration'] - 1] if state['current_iteration'] > 0 else "",
            "search_results": state['search_results'],
            "analysis": analysis
        })
        return {
            "analysis": analysis,
            "should_continue": should_continue,
            "research_history": research_history
        }

    def report_node(self, state: ResearchState) -> Dict[str, Any]:
        logger.info("正在生成研究报告")
        formatted_history = ""
        for i, iteration in enumerate(state['research_history'], 1):
            formatted_history += f"""
=== 研究迭代 {i} ===
搜索关键词: {iteration.get('search_query', '')}
搜索结果数量: {len(iteration.get('search_results', []))}
分析结果: {iteration.get('analysis', '')}
"""
        prompt = f"""
你是一个专业的研究报告撰写专家。请根据以下研究计划和研究历史，生成一份结构化的研究报告。

研究问题：{state['query']}

研究大纲：{state['plan'].get('research_outline', [])}

研究历史：
{formatted_history}

请按照以下结构生成报告：
1. 引言：介绍研究背景和目的
2. 研究方法：简要说明研究过程
3. 核心发现：按照大纲章节详细阐述
4. 分析与讨论：对发现进行深入分析
5. 结论：总结研究结果
6. 参考文献：列出所有引用的来源

要求：
- 报告内容详实，有深度
- 每个关键结论都要有来源支持
- 语言专业但易懂
- 结构清晰，逻辑严密
"""
        messages = [{"role": "user", "content": prompt}]
        report = self._call_llm(messages, max_tokens=8192)
        return {"final_report": report}


def should_continue_search(state: ResearchState) -> Literal["search_node", "report_node"]:
    if state.get("should_continue", False):
        return "search_node"
    return "report_node"


def create_research_graph() -> StateGraph:
    nodes = ResearchNodes()
    workflow = StateGraph(ResearchState)
    workflow.add_node("plan_node", nodes.plan_node)
    workflow.add_node("search_node", nodes.search_node)
    workflow.add_node("analyze_node", nodes.analyze_node)
    workflow.add_node("report_node", nodes.report_node)
    workflow.set_entry_point("plan_node")
    workflow.add_edge("plan_node", "search_node")
    workflow.add_edge("search_node", "analyze_node")
    workflow.add_conditional_edges(
        "analyze_node",
        should_continue_search,
        {
            "search_node": "search_node",
            "report_node": "report_node"
        }
    )
    workflow.add_edge("report_node", END)
    return workflow


def run_research(query: str) -> Dict[str, Any]:
    logger.info(f"开始深度研究任务: {query}")
    workflow = create_research_graph()
    app = workflow.compile()
    initial_state: ResearchState = {
        "query": query,
        "plan": {},
        "search_queries": [],
        "current_iteration": 0,
        "search_results": [],
        "research_history": [],
        "analysis": "",
        "should_continue": False,
        "final_report": ""
    }
    try:
        result = app.invoke(initial_state)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"research_report_{timestamp}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# 深度研究报告\n\n**研究问题**: {query}\n\n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n{result.get('final_report', '')}")
        logger.info(f"报告已保存到: {filename}")
        return result
    except Exception as e:
        logger.error(f"研究过程中发生错误: {e}")
        raise


if __name__ == "__main__":
    if not config.validate():
        exit(1)
    query = input("请输入研究问题：")
    if not query:
        print("研究问题不能为空")
        exit(1)
    try:
        result = run_research(query)
        print("\n" + "="*80)
        print("深度研究报告")
        print("="*80)
        print(result.get("final_report", ""))
    except Exception as e:
        print(f"研究失败: {e}")