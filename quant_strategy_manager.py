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
    strategies = load_strategies()
    
    # 也添加规律总结
    import os
    import json
    from datetime import datetime
    
    summary_dir = "pattern_summaries"
    if os.path.exists(summary_dir):
        for filename in os.listdir(summary_dir):
            if filename.endswith('.json') and filename.startswith('summary_'):
                filepath = os.path.join(summary_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        summary_data = json.load(f)
                    strategies.append({
                        "name": summary_data.get("name", "规律总结"),
                        "description": summary_data.get("description", "交易规律总结"),
                        "created_at": summary_data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                        "content": summary_data.get("summary", ""),
                        "type": "pattern_summary"
                    })
                except:
                    pass
    
    return strategies

import re
from typing import List, Dict, Any, Optional

def extract_stock_symbols_from_text(text: str) -> List[str]:
    """
    从文本中提取股票代码
    
    Args:
        text: 输入的文本
        
    Returns:
        股票代码列表
    """
    # 匹配6位数字代码
    pattern = r'\b(00[0-9]{4}|60[0-9]{4}|30[0-9]{4})\b'
    matches = re.findall(pattern, text)
    
    # 去重
    unique_matches = list(set(matches))
    
    return unique_matches

def upgrade_strategy_with_stock(stock_symbol: str, user_input: str) -> Dict[str, Any]:
    """
    基于特定股票数据和用户输入升级策略
    
    Args:
        stock_symbol: 股票代码
        user_input: 用户输入的策略优化想法
        
    Returns:
        生成的策略信息
    """
    import os
    from datetime import datetime
    import json
    
    # 导入必要的模块
    try:
        from stock_llm_core import StockLLMCore
    except ImportError:
        print("无法导入StockLLMCore，将使用简单文本生成")
        return {"error": "缺少LLM核心模块"}
    
    # 从用户输入中提取股票代码
    extracted_symbols = extract_stock_symbols_from_text(user_input)
    
    # 如果没有提取到股票代码，使用传入的stock_symbol
    all_symbols = extracted_symbols if extracted_symbols else [stock_symbol]
    
    print(f"从输入中提取到股票代码: {all_symbols}")
    
    # 收集所有股票的数据
    stocks_data = []
    try:
        from stock_data_fetcher import get_stock_info
        for symbol in all_symbols:
            try:
                stock_data = get_stock_info(symbol)
                stocks_data.append({
                    "symbol": symbol,
                    "name": stock_data.get("name", "未知"),
                    "data": stock_data
                })
            except Exception as e:
                print(f"获取股票 {symbol} 数据失败: {e}")
                stocks_data.append({
                    "symbol": symbol,
                    "name": "未知",
                    "data": {"symbol": symbol, "name": "未知"}
                })
    except ImportError:
        print("无法导入get_stock_info")
        # 添加基本信息
        for symbol in all_symbols:
            stocks_data.append({
                "symbol": symbol,
                "name": "未知",
                "data": {"symbol": symbol, "name": "未知"}
            })
    
    # 构建提示词 - 强调从用户输入中总结规律
    prompt = f"""你是一名专业的量化策略分析师。请基于用户提供的多个股票案例和分析文本，总结出其中的交易规律和逻辑。

【用户提供的分析文本】
{user_input}

【相关股票数据】
"""
    
    # 添加股票数据
    for stock in stocks_data:
        prompt += f"\n股票代码: {stock['symbol']}, 股票名称: {stock['name']}"
        # 只添加关键数据，避免太长
        key_data = {
            k: v for k, v in stock['data'].items() 
            if k in ['symbol', 'name', 'close', 'pct_chg', 'turnover_rate', 'limit_up_days']
        }
        if key_data:
            prompt += f"\n关键数据: {json.dumps(key_data, ensure_ascii=False)}"
    
    prompt += f"""

【任务要求】
1. 仔细阅读用户提供的分析文本，理解用户观察到的市场现象和规律
2. 基于用户的分析（而不是自己创造），总结出核心的交易逻辑
3. 结合提供的股票数据，验证用户观察的规律是否在数据上有体现
4. 生成一个简短、中肯的交易逻辑总结（不超过300字）
5. 不要生成完整的量化策略模板，只总结规律

请按照以下格式输出：
【规律总结】
（这里写你的总结，要简短、中肯）

【关键特征】
1. ...
2. ...
3. ...

【适用条件】
- ...
- ...

【风险提示】
- ...
- ..."""
    
    # 调用LLM生成策略
    try:
        llm_core = StockLLMCore(llm_provider="deepseek")
        response = llm_core._generate_quant_strategy(prompt)
        
        # 解析响应
        summary_content = response
        
        # 生成策略ID
        timestamp = datetime.now().strftime("%Y%m%d-%H%M")
        strategy_id = f"规律总结-{'-'.join(all_symbols[:3])}-{timestamp}"
        if len(all_symbols) > 3:
            strategy_id = f"规律总结-多股票-{timestamp}"
        
        # 保存总结到专门目录
        summary_dir = "pattern_summaries"
        os.makedirs(summary_dir, exist_ok=True)
        
        summary_file = os.path.join(summary_dir, f"summary_{strategy_id}.json")
        
        summary_data = {
            "id": strategy_id,
            "name": strategy_id,
            "description": f"基于用户对{len(all_symbols)}只股票的分析总结的交易规律",
            "stock_symbols": all_symbols,
            "stocks_data": stocks_data,
            "user_input": user_input,
            "summary": summary_content,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "pattern_summary"
        }
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
        
        print(f"规律总结已保存到: {summary_file}")
        
        # 同时保存一个简化的版本供功能3使用
        simple_file = os.path.join(summary_dir, "latest_pattern_summary.txt")
        with open(simple_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        print(f"最新规律总结已保存到: {simple_file}，可供LLM分析功能使用")
        
        return {
            "id": strategy_id,
            "name": strategy_id,
            "description": summary_data["description"],
            "content": summary_content,
            "file_path": summary_file,
            "simple_file": simple_file
        }
        
    except Exception as e:
        print(f"生成策略时出错: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"生成策略失败: {str(e)}"}

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
    try:
        return upgrade_strategy_with_stock(default_stock, user_input)
    except Exception as e:
        print(f"升级策略失败: {e}")
        # 返回一个简单的错误策略
        return {
            "name": f"错误策略-{datetime.datetime.now().strftime('%Y%m%d-%H%M')}",
            "description": f"策略生成失败: {str(e)}",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": f"策略生成失败，请检查API密钥设置。错误信息: {str(e)}",
            "source": "error"
        }

if __name__ == "__main__":
    # 测试代码
    print("量化策略管理器测试")
    strategies = view_current_strategies()
    print(f"当前有 {len(strategies)} 个策略")
    
    # 测试升级策略
    test_input = "请优化买入条件，增加对成交量的要求"
    new_strategy = upgrade_strategy_with_stock("000001", test_input)
    print(f"\n新策略: {new_strategy['name']}")
