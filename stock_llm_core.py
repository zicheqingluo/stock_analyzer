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
            use_local: 是否使用本地模拟
            
        Returns:
            LLM响应
        """
        if use_local or self.llm_provider == "local":
            return self._call_local_llm(prompt)
        elif self.llm_provider == "deepseek":
            return self._call_deepseek_api(prompt)
        elif self.llm_provider == "openai":
            return self._call_openai_api(prompt)
        else:
            print(f"警告: 不支持的LLM提供商: {self.llm_provider}，使用本地模拟")
            return self._call_local_llm(prompt)
    
    def _call_local_llm(self, prompt: str) -> str:
        """
        本地模拟LLM调用
        """
        # 检查是否是量化策略生成请求
        if "量化策略" in prompt or "交易策略" in prompt or "买入条件" in prompt:
            return self._generate_quant_strategy(prompt)
        
        # 解析prompt中的关键信息
        lines = prompt.split('\n')
        symbol = ""
        for line in lines:
            if "股票代码:" in line:
                parts = line.split(":")
                if len(parts) > 1:
                    symbol = parts[1].strip()
                break
        
        # 基于规则的简单分析
        analysis = f"""
基于数据对股票 {symbol if symbol else '未知'} 的分析：

【综合结论】
该股票近期表现强势，符合缩量走强模式。

【详细分析】
1. 换手率分析：换手率逐步降低，显示筹码锁定良好
2. 连板类型：近期有一字板，表现极强
3. 量价关系：符合爆量->缩量->缩量的标准走强模式
4. 强弱转换：连续涨停，无炸板，表现强势

【明日预期】
大概率继续走强，可能继续一字板或大高开快速涨停

【操作建议】
如果持有可继续持有，如果未持有可考虑在合适时机参与

【风险提示】
注意市场整体风险，避免追高
"""
        
        return analysis
    
    def _generate_quant_strategy(self, prompt: str) -> str:
        """
        生成量化策略
        """
        # 解析用户需求
        user_input = ""
        for line in prompt.split('\n'):
            if "用户的新需求：" in line:
                cleaned_line = line.encode('utf-8', 'ignore').decode('utf-8')
                parts = cleaned_line.split("：")
                if len(parts) > 1:
                    user_input = parts[1].strip()
                break
            elif "用户需求：" in line:
                cleaned_line = line.encode('utf-8', 'ignore').decode('utf-8')
                parts = cleaned_line.split("：")
                if len(parts) > 1:
                    user_input = parts[1].strip()
                break
        
        # 基于用户需求生成策略
        strategy_name = "智能量化策略"
        if "涨停" in user_input:
            strategy_name = "涨停板优化策略"
        elif "连板" in user_input:
            strategy_name = "连板股策略"
        elif "回调" in user_input:
            strategy_name = "回调买入策略"
        elif "风险" in user_input:
            strategy_name = "风险控制策略"
        
        strategy = f"""
【策略名称】
{strategy_name}

【策略描述】
基于用户需求"{user_input}"生成的量化交易策略，专注于中国A股市场的短线交易机会。

【核心逻辑】
1. 结合技术指标与市场情绪进行综合判断
2. 利用涨停板、成交量、换手率等多维度数据
3. 动态调整买入卖出条件以适应市场变化

【买入条件】
1. 股票当日涨停或接近涨停（涨幅>9.5%）
2. 成交量较前一日放大1.5倍以上
3. 换手率在5%-20%之间，显示活跃但不过度
4. 股价突破关键压力位或创近期新高
5. 市场整体情绪积极，板块有联动效应

【卖出条件】
1. 止损条件：股价跌破买入价5%立即止损
2. 止盈条件：盈利达到15%考虑部分止盈，20%全部止盈
3. 时间止损：持有超过3个交易日未达目标考虑减仓
4. 技术止损：出现放量滞涨或跌破重要均线

【风险控制】
1. 单只股票仓位不超过总资金的20%
2. 每日最大亏损不超过总资金的2%
3. 避免在重大利空消息发布时交易
4. 关注市场整体风险，大盘下跌时降低仓位
5. 设置硬性止损线，严格执行纪律

【适用市场环境】
1. 适用于震荡市和牛市初期
2. 在单边下跌市中应谨慎使用或暂停
3. 最适合中小盘活跃股
4. 需要实时数据支持和快速执行能力

【策略优化建议】
1. 定期回测策略表现，根据市场变化调整参数
2. 结合基本面分析提高胜率
3. 关注政策面和资金面变化
4. 建立策略组合，分散风险
"""
        
        return strategy
    
    def _call_deepseek_api(self, prompt: str) -> str:
        """
        调用DeepSeek API
        """
        if not self.deepseek_client:
            print("DeepSeek客户端未初始化，使用本地模拟")
            return self._call_local_llm(prompt)
        
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
                print("DeepSeek API返回空响应")
                return self._call_local_llm(prompt)
                
        except Exception as e:
            print(f"DeepSeek API调用失败: {e}")
            print("将使用本地模拟LLM")
            return self._call_local_llm(prompt)
    
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
                print("OpenAI API返回空响应")
                return self._call_local_llm(prompt)
                
        except Exception as e:
            print(f"OpenAI API调用失败: {e}")
            print("将使用本地模拟LLM")
            return self._call_local_llm(prompt)
    
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
        
        current_section = None
        current_content = []
        
        for line in response.split('\n'):
            line = line.strip()
            
            # 检查是否是新的章节
            for section in sections.keys():
                if line.startswith(section) or f"【{section}】" in line:
                    if current_section:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = section
                    current_content = []
                    break
            else:
                if current_section and line:
                    current_content.append(line)
        
        # 处理最后一个章节
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
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
