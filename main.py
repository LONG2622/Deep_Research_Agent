"""
Deep Research Agent 核心原型
实现核心循环：查询规划 → 搜索 → 内容提取 → 推理 → 报告生成
"""

import os
import json
import logging
from typing import List, Dict, Any
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from tavily import TavilyClient

from config import config

# 配置日志
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class DeepResearchAgent:
    """深度研究智能体"""
    
    def __init__(self):
        # 初始化 LLM 客户端
        self.llm_client = OpenAI(
            api_key=config.LLM_API_KEY,
            base_url=config.LLM_BASE_URL
        )
        
        # 初始化搜索客户端
        self.search_client = TavilyClient(api_key=config.TAVILY_API_KEY)
        
        # 研究状态
        self.research_history: List[Dict[str, Any]] = []
        self.current_iteration: int = 0
    
    def _call_llm(self, messages: List[Dict[str, str]], model: str = None, max_tokens: int = 4096) -> str:
        """调用 LLM 模型"""
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
    
    def plan_research(self, query: str) -> Dict[str, Any]:
        """
        查询规划：将复杂问题分解为研究计划
        返回包含研究大纲和搜索关键词的字典
        """
        logger.info(f"开始查询规划: {query}")
        
        prompt = f"""
你是一个专业的研究规划师。请分析以下研究问题，并生成详细的研究计划。

研究问题：{query}

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
            # 尝试提取 JSON
            if "{" in response and "}" in response:
                start = response.index("{")
                end = response.rindex("}") + 1
                plan = json.loads(response[start:end])
            else:
                # 如果不是 JSON，返回默认结构
                plan = {
                    "research_outline": ["引言", "核心分析", "结论"],
                    "search_queries": [query],
                    "estimated_iterations": 2
                }
        except json.JSONDecodeError:
            plan = {
                "research_outline": ["引言", "核心分析", "结论"],
                "search_queries": [query],
                "estimated_iterations": 2
            }
        
        logger.info(f"研究计划生成完成: {plan['research_outline']}")
        return plan
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """使用 Tavily 搜索引擎进行搜索"""
        logger.info(f"正在搜索: {query}")
        
        try:
            results = self.search_client.search(
                query=query,
                max_results=config.MAX_SEARCH_RESULTS,
                search_depth="advanced"
            )
            return results.get("results", [])
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []
    
    def extract_content(self, url: str) -> str:
        """从网页提取文本内容"""
        logger.info(f"正在提取网页内容: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取主要内容
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
            
            if main_content:
                text = main_content.get_text(separator='\n', strip=True)
            else:
                text = soup.get_text(separator='\n', strip=True)
            
            # 清理文本，保留前 3000 字符
            clean_text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
            return clean_text[:3000]
        
        except Exception as e:
            logger.error(f"网页内容提取失败: {e}")
            return ""
    
    def analyze_and_synthesize(self, query: str, plan: Dict[str, Any], search_results: List[Dict[str, Any]]) -> str:
        """
        分析和综合搜索结果
        评估信息是否充足，决定是否需要进一步搜索
        """
        logger.info("正在分析搜索结果")
        
        # 整理搜索结果
        formatted_results = ""
        for i, result in enumerate(search_results, 1):
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

研究问题：{query}

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
        
        return analysis
    
    def generate_report(self, query: str, plan: Dict[str, Any], research_history: List[Dict[str, Any]]) -> str:
        """生成结构化研究报告"""
        logger.info("正在生成研究报告")
        
        # 整理研究历史
        formatted_history = ""
        for i, iteration in enumerate(research_history, 1):
            formatted_history += f"""
=== 研究迭代 {i} ===
搜索关键词: {iteration.get('search_query', '')}
搜索结果数量: {len(iteration.get('search_results', []))}
分析结果: {iteration.get('analysis', '')}
"""
        
        prompt = f"""
你是一个专业的研究报告撰写专家。请根据以下研究计划和研究历史，生成一份结构化的研究报告。

研究问题：{query}

研究大纲：{plan.get('research_outline', [])}

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
        
        return report
    
    def run(self, query: str) -> str:
        """
        运行完整的深度研究流程
        """
        logger.info(f"开始深度研究任务: {query}")
        
        # 步骤1: 查询规划
        plan = self.plan_research(query)
        
        # 步骤2-4: 多轮搜索和推理
        for iteration in range(config.MAX_RESEARCH_ITERATIONS):
            self.current_iteration = iteration + 1
            logger.info(f"研究迭代 {self.current_iteration}/{config.MAX_RESEARCH_ITERATIONS}")
            
            # 获取当前需要搜索的关键词
            queries = plan.get("search_queries", [])
            if iteration < len(queries):
                search_query = queries[iteration]
            else:
                # 如果关键词用完了，使用之前分析建议的新关键词
                if self.research_history:
                    last_analysis = self.research_history[-1].get("analysis", "")
                    if "建议的搜索关键词" in last_analysis:
                        start = last_analysis.index("建议的搜索关键词") + len("建议的搜索关键词")
                        search_query = last_analysis[start:].strip().split('\n')[0]
                    else:
                        break
                else:
                    break
            
            # 搜索
            search_results = self.search(search_query)
            
            if not search_results:
                logger.warning("未找到搜索结果，尝试下一个关键词")
                continue
            
            # 分析和综合
            analysis = self.analyze_and_synthesize(query, plan, search_results)
            
            # 记录研究历史
            self.research_history.append({
                "iteration": iteration + 1,
                "search_query": search_query,
                "search_results": search_results,
                "analysis": analysis
            })
            
            # 检查是否需要继续搜索
            if "是否需要继续搜索：否" in analysis or "信息评估：充足" in analysis:
                logger.info("信息已充足，停止搜索")
                break
        
        # 步骤5: 生成报告
        report = self.generate_report(query, plan, self.research_history)
        
        logger.info("深度研究任务完成")
        return report

def main():
    """主函数"""
    # 验证配置
    if not config.validate():
        return
    
    # 创建研究智能体
    agent = DeepResearchAgent()
    
    # 获取用户输入
    query = input("请输入研究问题：")
    
    if not query:
        print("研究问题不能为空")
        return
    
    # 运行研究
    try:
        report = agent.run(query)
        
        # 输出报告
        print("\n" + "="*80)
        print("深度研究报告")
        print("="*80)
        print(report)
        
        # 保存报告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"research_report_{timestamp}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# 深度研究报告\n\n**研究问题**: {query}\n\n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n{report}")
        
        print(f"\n报告已保存到: {filename}")
        
    except Exception as e:
        logger.error(f"研究过程中发生错误: {e}")
        print(f"研究失败: {e}")

if __name__ == "__main__":
    main()