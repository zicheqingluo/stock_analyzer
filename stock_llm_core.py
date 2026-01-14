#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票LLM核心功能模块 - 处理LLM调用和响应解析
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

class StockLLMCore:
    """股票LLM核心功能类"""
    
    def __init__(self, llm_provider: str = "local", api_key: str = None, base_url: str = None):
        """
        初始化LLM核心
        
        Args:
            llm_provider: LLM提供商
            api_key: API密钥
            base_url: API基础URL
        """
        self.llm_provider = llm_provider
        self.api_key = api_key
        self.base_url = base_url
        self.deepseek_client = None
        
        # 初始化DeepSeek客户端
        if llm_provider == "deepseek":
            self._init_deepseek_client()
    
    def _init_deepseek_client(self):
        """初始化DeepSeek客户端"""
        try:
            from openai import OpenAI
            self.deepseek_client = OpenAI(
                api_key=self.api_key or os.environ.get("DEEPSEEK_API_KEY"),
                base_url=self.base_url or "https://api.deepseek.com"
            )
            print("DeepSeek客户端初始化成功")
        except ImportError:
            print("警告: 未安装openai包，DeepSeek功能将不可用")
            self.deepseek_client = None
        except Exception as e:
            print(f"DeepSeek客户端初始化失败: {e}")
            self.deepseek_client = None
    
    def call_llm(self, prompt: str, use_local: bool = False) -> str:
        """
        调用LLM API
        
        Args:
            prompt: 提示词
            use_local: 是否使用本地模拟（已弃用，保留参数以兼容）
            
        Returns:
            LLM响应
        """
        if use_local:
            print("错误: 本地模拟功能已移除，请使用API")
            raise RuntimeError("本地模拟功能已移除，请设置API密钥")
        
        if self.llm_provider == "deepseek":
            return self._call_deepseek_api(prompt)
        elif self.llm_provider == "openai":
            return self._call_openai_api(prompt)
        else:
            print(f"错误: 不支持的LLM提供商: {self.llm_provider}")
            print("支持的提供商: deepseek, openai")
            raise ValueError(f"不支持的LLM提供商: {self.llm_provider}")
    
    def _call_local_llm(self, prompt: str) -> str:
        """
        本地模拟LLM调用（已弃用）
        """
        print("错误: 本地模拟功能已移除")
        print("请设置API密钥以使用LLM功能")
        raise RuntimeError("本地模拟功能已移除，请使用API调用")
    
    def _generate_quant_strategy(self, prompt: str) -> str:
        """
        生成量化策略（已弃用，仅用于兼容）
        """
        print("警告: _generate_quant_strategy 方法已弃用，请使用API")
        raise RuntimeError("本地模拟功能已移除，请使用API调用")
    
    def _call_deepseek_api(self, prompt: str) -> str:
        """
        调用DeepSeek API
        """
        if not self.deepseek_client:
            print("错误: DeepSeek客户端未初始化")
            print("请检查API密钥设置")
            raise RuntimeError("DeepSeek客户端未初始化，请检查API密钥")
        
        try:
            print("正在调用DeepSeek API...")
            
            # 构建消息
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的股票分析师，擅长分析中国A股市场，特别是涨停板、连板股、炸板等短线交易模式。请根据提供的数据进行专业分析。"
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
            
            # 调用API
            response = self.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                max_tokens=2000,
                temperature=0.7,
                stream=False
            )
            
            # 提取回复内容
            if response and response.choices:
                content = response.choices[0].message.content
                print("DeepSeek API调用成功")
                return content
            else:
                print("错误: DeepSeek API返回空响应")
                raise RuntimeError("DeepSeek API返回空响应")
                
        except Exception as e:
            print(f"DeepSeek API调用失败: {e}")
            print("错误: API调用失败，请检查网络连接和API密钥")
            raise RuntimeError(f"DeepSeek API调用失败: {e}")
    
    def _call_openai_api(self, prompt: str) -> str:
        """
        调用OpenAI API
        """
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.api_key or os.environ.get("OPENAI_API_KEY"))
            
            print("正在调用OpenAI API...")
            
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的股票分析师，擅长分析中国A股市场，特别是涨停板、连板股、炸板等短线交易模式。请根据提供的数据进行专业分析。"
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=2000,
                temperature=0.7,
                stream=False
            )
            
            if response and response.choices:
                content = response.choices[0].message.content
                print("OpenAI API调用成功")
                return content
            else:
                print("错误: OpenAI API返回空响应")
                raise RuntimeError("OpenAI API返回空响应")
                
        except Exception as e:
            print(f"OpenAI API调用失败: {e}")
            print("错误: API调用失败，请检查网络连接和API密钥")
            raise RuntimeError(f"OpenAI API调用失败: {e}")
    
    def parse_llm_response(self, response: str) -> Dict[str, str]:
        """
        解析LLM响应，提取结构化信息
        """
        sections = {
            "综合结论": "",
            "详细分析": "",
            "明日预期": "",
            "操作建议": "",
            "风险提示": ""
        }
        
        # 如果响应为空，返回空字典
        if not response:
            return sections
        
        current_section = None
        current_content = []
        
        for line in response.split('\n'):
            line = line.strip()
            
            # 检查是否是新的章节
            section_found = False
            for section in sections.keys():
                # 检查多种可能的格式
                if (line.startswith(section) or 
                    f"【{section}】" in line or 
                    f"{section}：" in line or
                    f"{section}:" in line):
                    if current_section:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = section
                    current_content = []
                    section_found = True
                    break
            
            if not section_found:
                if current_section and line:
                    current_content.append(line)
        
        # 处理最后一个章节
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        # 如果所有章节都为空，但响应不为空，将整个响应放入"详细分析"
        if not any(sections.values()) and response:
            sections["详细分析"] = response[:1000]  # 限制长度
        
        return sections
    
    def generate_quant_strategy_prompt(self, stock_data: Dict[str, Any], user_input: str) -> str:
        """
        生成量化策略提示词
        
        Args:
            stock_data: 股票数据
            user_input: 用户输入的分析需求
            
        Returns:
            提示词
        """
        # 构建量化策略提示词
        prompt = f"""
你是一个专业的量化策略分析师，专注于中国A股市场的短线交易策略。

【股票数据】
股票代码: {stock_data.get('symbol', '未知')}
股票名称: {stock_data.get('name', '未知')}
分析日期: {stock_data.get('analysis_date', '未知')}

【历史数据摘要】
{stock_data.get('history_summary', '无数据')}

【关键指标】
{stock_data.get('key_metrics', {})}

【用户需求】
{user_input}

请基于以上股票数据和用户需求，生成一个专业的量化交易策略。
策略必须具体、可执行、可量化，包含以下部分：
1. 策略名称
2. 策略描述
3. 核心逻辑
4. 买入条件（具体、可量化）
5. 卖出条件（止盈、止损、时间止损）
6. 风险控制（仓位管理、最大回撤）
7. 适用市场环境
8. 策略优化建议

请用中文回答，结构清晰。
"""
        return prompt
