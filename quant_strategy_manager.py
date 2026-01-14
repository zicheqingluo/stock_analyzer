#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量化策略管理器
功能：
1. 查看当前的量化策略
2. 升级优化策略（根据用户输入结合历史策略，通过大模型生成最新策略并存储到本地）
"""

import os
import json
import datetime
from typing import Dict, List, Any, Optional
import importlib.util

# 策略存储文件
STRATEGY_FILE = "quant_strategies.json"

def load_strategies() -> List[Dict[str, Any]]:
    """加载所有策略"""
    if not os.path.exists(STRATEGY_FILE):
        # 创建默认策略
        default_strategies = [
            {
                "name": "基础涨停板策略",
                "description": "基于涨停板突破的简单策略",
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "content": """
策略逻辑：
1. 选择当日涨停的股票
2. 检查成交量是否放大（前一日1.5倍以上）
3. 检查是否突破关键压力位
4. 次日开盘价在涨停价±2%范围内考虑买入
5. 止损：跌破涨停价5%卖出
6. 止盈：上涨15%或出现放量滞涨卖出
                """
            },
            {
                "name": "连板股回调策略",
                "description": "针对连板后回调的买入策略",
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "content": """
策略逻辑：
1. 选择连续2-3个涨停板的股票
2. 等待回调至第一个涨停板开盘价附近
3. 成交量萎缩至涨停日50%以下
4. 出现止跌信号（长下影线或小阳线）时买入
5. 止损：跌破第一个涨停板最低价
6. 止盈：反弹至最近涨停价附近卖出
                """
            }
        ]
        save_strategies(default_strategies)
        return default_strategies
    
    try:
        with open(STRATEGY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载策略文件失败: {e}")
        return []

def save_strategies(strategies: List[Dict[str, Any]]) -> bool:
    """保存策略到文件"""
    try:
        with open(STRATEGY_FILE, 'w', encoding='utf-8') as f:
            json.dump(strategies, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存策略文件失败: {e}")
        return False

def view_current_strategies() -> List[Dict[str, Any]]:
    """查看当前所有策略"""
    return load_strategies()

def upgrade_strategy(user_input: str) -> Dict[str, Any]:
    """升级优化策略
    
    Args:
        user_input: 用户输入的优化想法
        
    Returns:
        新生成的策略
    """
    # 加载现有策略
    existing_strategies = load_strategies()
    
    # 构建提示词
    prompt = f"""
你是一个专业的量化策略分析师。请根据以下信息生成一个新的股票交易策略：

现有策略摘要：
{json.dumps([s['name'] + ': ' + s['description'] for s in existing_strategies[:3]], ensure_ascii=False, indent=2)}

用户的新需求：
{user_input}

请生成一个完整的量化交易策略，包含以下部分：
1. 策略名称
2. 策略描述
3. 核心逻辑
4. 买入条件
5. 卖出条件（止损和止盈）
6. 风险控制
7. 适用市场环境

请用中文回答，内容要具体、可执行。
"""
    
    # 调用LLM生成新策略
    try:
        # 尝试导入LLM分析器
        current_dir = os.path.dirname(os.path.abspath(__file__))
        llm_path = os.path.join(current_dir, "stock_llm_analyzer.py")
        
        spec = importlib.util.spec_from_file_location("stock_llm_analyzer", llm_path)
        llm_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(llm_module)
        
        # 调用LLM
        llm_response = llm_module.llm_analyzer._call_local_llm(prompt)
        
        # 解析响应
        strategy_content = llm_response
        
        # 创建新策略对象
        new_strategy = {
            "name": f"优化策略-{datetime.datetime.now().strftime('%Y%m%d-%H%M')}",
            "description": f"基于用户需求生成的策略: {user_input[:50]}...",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": strategy_content,
            "user_input": user_input,
            "source": "llm_generated"
        }
        
        # 保存新策略
        existing_strategies.append(new_strategy)
        save_strategies(existing_strategies)
        
        return new_strategy
        
    except Exception as e:
        print(f"调用LLM失败: {e}")
        # 如果LLM调用失败，创建一个简单的策略
        new_strategy = {
            "name": f"手动策略-{datetime.datetime.now().strftime('%Y%m%d-%H%M')}",
            "description": f"基于用户需求生成的策略: {user_input[:50]}...",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": f"""
策略名称：基于用户输入的策略
用户需求：{user_input}

策略逻辑：
1. 结合用户需求与现有策略框架
2. 优化买入卖出条件
3. 加强风险控制

具体规则待进一步细化。
            """,
            "user_input": user_input,
            "source": "manual_fallback"
        }
        
        existing_strategies.append(new_strategy)
        save_strategies(existing_strategies)
        
        return new_strategy

if __name__ == "__main__":
    # 测试代码
    print("量化策略管理器测试")
    strategies = view_current_strategies()
    print(f"当前有 {len(strategies)} 个策略")
    for i, s in enumerate(strategies):
        print(f"{i+1}. {s['name']}")
