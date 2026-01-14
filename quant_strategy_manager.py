#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量化策略管理器 - 增强版
集成股票数据收集和DeepSeek调用
"""

import os
import json
import datetime
from typing import Dict, List, Any, Optional

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

def upgrade_strategy_with_stock(stock_symbol: str, user_input: str) -> Dict[str, Any]:
    """
    基于股票数据升级优化策略
    
    Args:
        stock_symbol: 股票代码
        user_input: 用户输入的优化想法
        
    Returns:
        新生成的策略
    """
    try:
        # 导入LLM分析器
        import sys
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # 使用新的量化策略生成功能
        from stock_llm_analyzer import generate_quant_strategy
        
        # 生成量化策略
        strategy = generate_quant_strategy(stock_symbol, user_input)
        
        if "error" in strategy:
            print(f"生成策略失败: {strategy['error']}")
            # 创建备用策略
            strategy = create_fallback_strategy(stock_symbol, user_input)
        
        # 保存到策略列表
        existing_strategies = load_strategies()
        existing_strategies.append(strategy)
        save_strategies(existing_strategies)
        
        return strategy
        
    except Exception as e:
        print(f"升级策略失败: {e}")
        # 创建备用策略
        return create_fallback_strategy(stock_symbol, user_input)

def create_fallback_strategy(stock_symbol: str, user_input: str) -> Dict[str, Any]:
    """创建备用策略"""
    return {
        "name": f"备用策略-{stock_symbol}-{datetime.datetime.now().strftime('%Y%m%d-%H%M')}",
        "description": f"基于股票{stock_symbol}和用户需求生成的策略",
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "content": f"""
策略名称：基于{stock_symbol}的量化策略
用户需求：{user_input}

策略逻辑：
1. 分析{stock_symbol}的历史走势
2. 结合用户需求优化交易规则
3. 设置合理的风险控制参数

具体规则：
- 买入条件：技术指标出现买入信号
- 卖出条件：达到止盈或止损目标
- 风险控制：单笔交易最大亏损5%
        """,
        "stock_symbol": stock_symbol,
        "user_input": user_input,
        "source": "fallback"
    }

def upgrade_strategy(user_input: str) -> Dict[str, Any]:
    """
    升级优化策略（兼容旧版本）
    
    Args:
        user_input: 用户输入的优化想法
        
    Returns:
        新生成的策略
    """
    # 默认使用一个测试股票
    default_stock = "000001"  # 平安银行
    return upgrade_strategy_with_stock(default_stock, user_input)

if __name__ == "__main__":
    # 测试代码
    print("量化策略管理器测试")
    strategies = view_current_strategies()
    print(f"当前有 {len(strategies)} 个策略")
    
    # 测试升级策略
    test_input = "请优化买入条件，增加对成交量的要求"
    new_strategy = upgrade_strategy_with_stock("000001", test_input)
    print(f"\n新策略: {new_strategy['name']}")
