"""
Deep Research Agent Streamlit UI
提供用户交互界面
"""

import streamlit as st
import time
import logging
from datetime import datetime

from main import DeepResearchAgent
from config import config

logger = logging.getLogger(__name__)

def main():
    st.set_page_config(
        page_title="Deep Research Agent",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("🔍 Deep Research Agent")
    st.subheader("智能深度研究助手")
    
    # 检查配置
    if not config.validate():
        st.error("请配置 API 密钥。复制 .env.example 为 .env 并填写相关配置。")
        return
    
    # 会话状态
    if "agent" not in st.session_state:
        st.session_state.agent = DeepResearchAgent()
    
    if "report" not in st.session_state:
        st.session_state.report = ""
    
    if "is_researching" not in st.session_state:
        st.session_state.is_researching = False
    
    if "research_history" not in st.session_state:
        st.session_state.research_history = []
    
    # 用户输入
    query = st.text_area(
        "请输入您的研究问题",
        placeholder="例如：分析人工智能在医疗领域的应用现状和未来趋势",
        height=100
    )
    
    col1, col2 = st.columns(2)
    with col1:
        max_iterations = st.slider(
            "最大研究迭代次数",
            min_value=1,
            max_value=5,
            value=3,
            help="设置研究过程中最多进行多少次搜索迭代"
        )
    
    # 开始研究按钮
    if st.button("开始深度研究", disabled=st.session_state.is_researching or not query):
        st.session_state.is_researching = True
        st.session_state.report = ""
        st.session_state.research_history = []
        
        # 更新配置
        config.MAX_RESEARCH_ITERATIONS = max_iterations
        
        # 创建进度条
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # 创建新的智能体实例
            agent = DeepResearchAgent()
            
            # 步骤1: 查询规划
            status_text.text("🔄 正在分析问题，生成研究计划...")
            progress_bar.progress(10)
            plan = agent.plan_research(query)
            
            st.success(f"📋 研究计划已生成，包含 {len(plan['research_outline'])} 个章节")
            st.write("**研究大纲**:")
            for i, section in enumerate(plan["research_outline"], 1):
                st.write(f"{i}. {section}")
            
            # 步骤2-4: 多轮搜索和推理
            for iteration in range(max_iterations):
                status_text.text(f"🔍 正在进行第 {iteration + 1}/{max_iterations} 轮搜索...")
                progress_bar.progress(10 + (iteration + 1) * 20)
                
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
                
                st.info(f"🔎 正在搜索: {search_query}")
                
                # 搜索
                search_results = agent.search(search_query)
                
                if not search_results:
                    st.warning("未找到搜索结果，尝试下一个关键词")
                    continue
                
                st.write(f"📄 找到 {len(search_results)} 个相关来源")
                
                # 分析和综合
                status_text.text("🧠 正在分析搜索结果...")
                analysis = agent.analyze_and_synthesize(query, plan, search_results)
                
                # 记录历史
                agent.research_history.append({
                    "iteration": iteration + 1,
                    "search_query": search_query,
                    "search_results": search_results,
                    "analysis": analysis
                })
                
                st.session_state.research_history = agent.research_history
                
                # 显示分析结果
                with st.expander(f"第 {iteration + 1} 轮分析结果"):
                    st.write(analysis)
                
                # 检查是否需要继续
                if "是否需要继续搜索：否" in analysis or "信息评估：充足" in analysis:
                    st.success("✅ 信息已充足，停止搜索")
                    break
                
                time.sleep(1)
            
            # 步骤5: 生成报告
            status_text.text("📝 正在生成研究报告...")
            progress_bar.progress(90)
            
            report = agent.generate_report(query, plan, agent.research_history)
            
            st.session_state.report = report
            
            # 完成
            status_text.text("✅ 研究完成！")
            progress_bar.progress(100)
            
            # 显示报告
            st.markdown("---")
            st.title("📊 研究报告")
            st.markdown(report)
            
            # 保存按钮
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