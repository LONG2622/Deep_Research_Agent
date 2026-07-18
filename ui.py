"""
Deep Research Agent Streamlit UI
支持原始模式和 LangGraph 模式
"""

import streamlit as st
import time
import logging
from datetime import datetime

from main import DeepResearchAgent
from langgraph_agent import run_research
from config import config

logger = logging.getLogger(__name__)

def run_original_mode(query, max_iterations):
    agent = DeepResearchAgent()
    plan = agent.plan_research(query)
    st.success(f"📋 研究计划已生成，包含 {len(plan['research_outline'])} 个章节")
    st.write("**研究大纲**:")
    for i, section in enumerate(plan["research_outline"], 1):
        st.write(f"{i}. {section}")
    for iteration in range(max_iterations):
        st.info(f"🔍 正在进行第 {iteration + 1}/{max_iterations} 轮搜索...")
        queries = plan.get("search_queries", [])
        if iteration < len(queries):
            search_query = queries[iteration]
        else:
            if agent.research_history:
                last_analysis = agent.research_history[-1].get("analysis", "")
                if "建议的搜索关键词" in last_analysis:
                    start = last_analysis.index("建议的搜索关键词") + len("建议的搜索关键词")
                    search_query = last_analysis[start:].strip().split('\n')[0]
                else:
                    break
            else:
                break
        st.info(f"🔎 搜索关键词: {search_query}")
        search_results = agent.search(search_query)
        if not search_results:
            st.warning("未找到搜索结果，尝试下一个关键词")
            continue
        st.write(f"📄 找到 {len(search_results)} 个相关来源")
        st.info("🧠 正在分析搜索结果...")
        analysis = agent.analyze_and_synthesize(query, plan, search_results)
        agent.research_history.append({
            "iteration": iteration + 1,
            "search_query": search_query,
            "search_results": search_results,
            "analysis": analysis
        })
        with st.expander(f"第 {iteration + 1} 轮分析结果"):
            st.write(analysis)
        if "是否需要继续搜索：否" in analysis or "信息评估：充足" in analysis:
            st.success("✅ 信息已充足，停止搜索")
            break
        time.sleep(1)
    st.info("📝 正在生成研究报告...")
    report = agent.generate_report(query, plan, agent.research_history)
    return report

def run_langgraph_mode(query):
    result = run_research(query)
    plan = result.get("plan", {})
    if plan:
        st.success(f"📋 研究计划已生成，包含 {len(plan.get('research_outline', []))} 个章节")
        st.write("**研究大纲**:")
        for i, section in enumerate(plan.get("research_outline", []), 1):
            st.write(f"{i}. {section}")
    research_history = result.get("research_history", [])
    for i, iteration in enumerate(research_history, 1):
        with st.expander(f"第 {i} 轮分析结果"):
            st.write(f"🔎 搜索关键词: {iteration.get('search_query', '')}")
            st.write(f"📄 搜索结果数量: {len(iteration.get('search_results', []))}")
            st.write(f"分析: {iteration.get('analysis', '')}")
    return result.get("final_report", "")

def main():
    st.set_page_config(
        page_title="Deep Research Agent",
        page_icon="🔍",
        layout="wide"
    )
    st.title("🔍 Deep Research Agent")
    st.subheader("智能深度研究助手")
    if not config.validate():
        st.error("请配置 API 密钥。复制 .env.example 为 .env 并填写相关配置。")
        return
    if "report" not in st.session_state:
        st.session_state.report = ""
    if "is_researching" not in st.session_state:
        st.session_state.is_researching = False
    query = st.text_area(
        "请输入您的研究问题",
        placeholder="例如：分析人工智能在医疗领域的应用现状和未来趋势",
        height=100
    )
    col1, col2 = st.columns(2)
    with col1:
        mode = st.selectbox(
            "选择运行模式",
            ["原始模式", "LangGraph 模式"],
            help="原始模式使用传统的循环实现，LangGraph 模式使用状态图工作流"
        )
    with col2:
        max_iterations = st.slider(
            "最大研究迭代次数",
            min_value=1,
            max_value=5,
            value=3,
            help="设置研究过程中最多进行多少次搜索迭代"
        )
    if st.button("开始深度研究", disabled=st.session_state.is_researching or not query):
        st.session_state.is_researching = True
        st.session_state.report = ""
        progress_bar = st.progress(0)
        status_text = st.empty()
        try:
            if mode == "原始模式":
                status_text.text(f"🔄 使用原始模式运行研究...")
                progress_bar.progress(10)
                report = run_original_mode(query, max_iterations)
            else:
                status_text.text(f"🔄 使用 LangGraph 模式运行研究...")
                progress_bar.progress(10)
                report = run_langgraph_mode(query)
            st.session_state.report = report
            status_text.text("✅ 研究完成！")
            progress_bar.progress(100)
            st.markdown("---")
            st.title("📊 研究报告")
            st.markdown(report)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"research_report_{timestamp}.md"
            st.download_button(
                label="📥 下载报告",
                data=report,
                file_name=filename,
                mime="text/markdown"
            )
        except Exception as e:
            st.error(f"研究过程中发生错误: {e}")
            logger.error(f"研究失败: {e}")
        finally:
            st.session_state.is_researching = False

if __name__ == "__main__":
    main()