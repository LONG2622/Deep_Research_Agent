"""
配置管理模块
负责加载和管理项目的配置信息
"""

import os
from dotenv import load_dotenv
from typing import Optional

# 加载环境变量
load_dotenv()

class Config:
    """项目配置类"""
    
    # LLM 配置
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "deepseek-chat")
    
    # Tavily 搜索配置
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    
    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # 搜索配置
    MAX_SEARCH_RESULTS: int = 5
    MAX_RESEARCH_ITERATIONS: int = 3
    
    # 报告配置
    MAX_REPORT_SECTIONS: int = 8
    
    @classmethod
    def validate(cls) -> bool:
        """验证配置是否完整"""
        required_keys = ["LLM_API_KEY", "TAVILY_API_KEY"]
        
        missing_keys = [key for key in required_keys if not getattr(cls, key)]
        
        if missing_keys:
            print(f"缺少必要的配置项: {', '.join(missing_keys)}")
            print("请复制 .env.example 为 .env 并填写相关配置")
            return False
        
        return True

config = Config()