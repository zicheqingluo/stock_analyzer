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
from datetime import datetime

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

def extract_dates_from_text(text: str) -> List[str]:
    """
    从文本中提取日期
    
    Args:
        text: 输入的文本
        
    Returns:
        日期列表（格式：YYYYMMDD），只返回第一个找到的日期
    """
    # 匹配多种日期格式
    patterns = [
        r'\b(\d{4})-(\d{1,2})-(\d{1,2})\b',  # YYYY-MM-DD
        r'\b(\d{4})/(\d{1,2})/(\d{1,2})\b',  # YYYY/MM/DD
        r'\b(\d{4})(\d{2})(\d{2})\b',        # YYYYMMDD
        r'\b(\d{4})年(\d{1,2})月(\d{1,2})日\b',  # YYYY年MM月DD日
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if len(match) == 3:
                year, month, day = match
                # 标准化月份和日期为两位数
                month = month.zfill(2)
                day = day.zfill(2)
                # 格式化为YYYYMMDD
                date_str = f"{year}{month}{day}"
                # 只返回第一个找到的日期
                return [date_str]
    
    # 如果没有找到日期，返回空列表
    return []

def upgrade_strategy_with_stock_and_dates(user_input: str, symbols: List[str], dates: List[str]) -> Dict[str, Any]:
    """
    基于股票代码、日期和用户输入总结规律
    
    Args:
        user_input: 用户输入的策略优化想法
        symbols: 股票代码列表
        dates: 日期列表
        
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
    
    print(f"\n【开始处理】")
    print(f"提取到的股票代码: {symbols}")
    print(f"提取到的日期: {dates}")
    
    # 收集所有股票的数据
    stocks_data = []
    
    # 尝试导入数据收集器
    try:
        from stock_data_collector import StockDataCollector
        data_collector = StockDataCollector()
        
        # 只使用第一个日期（如果存在），因为所有分析都是同一时间进行的
        target_date = None
        if dates:
            target_date = dates[0]
            print(f"使用统一分析日期: {target_date}")
        else:
            print("未找到日期，使用最近日期")
        
        for i, symbol in enumerate(symbols):
            print(f"\n【获取股票数据 {i+1}/{len(symbols)}】")
            print(f"股票代码: {symbol}")
            
            # 所有股票使用同一个日期
            print(f"使用日期: {target_date}")
            
            try:
                # 收集股票数据
                stock_data = data_collector.collect_stock_data(symbol, days_back=5, target_date=target_date)
                
                if "error" in stock_data:
                    print(f"获取股票 {symbol} 数据失败: {stock_data['error']}")
                    stocks_data.append({
                        "symbol": symbol,
                        "name": "未知",
                        "date": target_date,
                        "data": {"error": stock_data['error']}
                    })
                else:
                    print(f"✓ 成功获取数据: {stock_data.get('name', symbol)}")
                    print(f"  分析日期: {stock_data.get('analysis_date', '未知')}")
                    print(f"  关键指标: {stock_data.get('key_metrics', {})}")
                    
                    stocks_data.append({
                        "symbol": symbol,
                        "name": stock_data.get('name', '未知'),
                        "date": target_date,
                        "data": stock_data
                    })
            except Exception as e:
                print(f"获取股票 {symbol} 数据异常: {e}")
                stocks_data.append({
                    "symbol": symbol,
                    "name": "未知",
                    "date": target_date,
                    "data": {"error": str(e)}
                })
    except ImportError:
        print("无法导入StockDataCollector，尝试使用stock_data_fetcher")
        try:
            from stock_data_fetcher import get_stock_info
            for symbol in symbols:
                try:
                    stock_data = get_stock_info(symbol)
                    stocks_data.append({
                        "symbol": symbol,
                        "name": stock_data.get("股票名称", "未知"),
                        "date": None,
                        "data": stock_data
                    })
                except Exception as e:
                    print(f"获取股票 {symbol} 数据失败: {e}")
                    stocks_data.append({
                        "symbol": symbol,
                        "name": "未知",
                        "date": None,
                        "data": {"symbol": symbol, "name": "未知"}
                    })
        except ImportError:
            print("无法导入get_stock_info")
            # 添加基本信息
            for symbol in symbols:
                stocks_data.append({
                    "symbol": symbol,
                    "name": "未知",
                    "date": None,
                    "data": {"symbol": symbol, "name": "未知"}
                })
    
    print(f"\n【数据收集完成】")
    print(f"共收集到 {len(stocks_data)} 只股票的数据")
    
    # 构建提示词 - 强调从用户输入中总结规律，使用few-shot学习
    prompt = f"""你是一名专业的量化策略分析师。请基于用户提供的多个股票案例和分析文本，通过few-shot学习的方式总结出其中的交易规律和逻辑。

【用户提供的分析文本（案例）】
{user_input}

【相关股票的实际数据】
"""
    
    # 添加股票数据
    for stock in stocks_data:
        prompt += f"\n=== 股票代码: {stock['symbol']}, 股票名称: {stock['name']}, 日期: {stock['date']} ==="
        
        data = stock['data']
        if 'error' in data:
            prompt += f"\n数据获取失败: {data['error']}"
        else:
            # 添加关键数据
            if 'key_metrics' in data:
                prompt += f"\n关键指标:"
                for key, value in data['key_metrics'].items():
                    prompt += f"\n  {key}: {value}"
            
            if 'history_summary' in data:
                prompt += f"\n历史数据摘要:\n{data['history_summary']}"
            
            if 'limit_up_data' in data:
                limit_data = data['limit_up_data']
                prompt += f"\n涨停板池数据:"
                prompt += f"\n  是否在涨停板池: {limit_data.get('in_today_pool', False)}"
                prompt += f"\n  连板天数: {limit_data.get('streak_days', 0)}"
                prompt += f"\n  炸板次数: {limit_data.get('blow_up_count', 0)}"
    
    prompt += f"""

【任务要求 - 通过few-shot学习总结规律】
1. 仔细分析用户提供的案例文本，理解每个案例中的市场现象、操作逻辑和结果
2. 结合对应的股票实际数据，验证案例中的描述是否与数据相符
3. 通过对比多个案例，找出其中的共同模式和规律
4. 总结出可复用的交易逻辑和识别模式
5. 注意：要基于案例和数据，而不是自己创造规律

【输出格式】
请按照以下格式输出：

【规律总结】
（基于案例和数据总结的核心规律，300字以内）

【few-shot学习过程】
1. 案例1分析：[股票代码] 的案例表明：[分析]
   数据验证：[数据如何支持或修正这个观察]
2. 案例2分析：[股票代码] 的案例表明：[分析]
   数据验证：[数据如何支持或修正这个观察]
...（根据实际案例数量）

【关键特征识别】
1. [特征1]: [描述]
2. [特征2]: [描述]
3. [特征3]: [描述]

【适用条件】
- [条件1]
- [条件2]
- [条件3]

【风险提示】
- [风险1]
- [风险2]"""
    
    print(f"\n【正在调用大模型进行few-shot学习总结...】")
    
    # 调用LLM生成策略
    try:
        llm_core = StockLLMCore(llm_provider="deepseek")
        response = llm_core._generate_quant_strategy(prompt)
        
        # 解析响应
        summary_content = response
        
        # 生成策略ID
        timestamp = datetime.now().strftime("%Y%m%d-%H%M")
        strategy_id = f"规律总结-{'-'.join(symbols[:3])}-{timestamp}"
        if len(symbols) > 3:
            strategy_id = f"规律总结-多股票-{timestamp}"
        
        # 保存总结到专门目录
        summary_dir = "pattern_summaries"
        os.makedirs(summary_dir, exist_ok=True)
        
        summary_file = os.path.join(summary_dir, f"summary_{strategy_id}.json")
        
        summary_data = {
            "id": strategy_id,
            "name": strategy_id,
            "description": f"基于用户对{len(symbols)}只股票的案例分析和实际数据总结的交易规律",
            "stock_symbols": symbols,
            "stock_dates": dates,
            "stocks_data": stocks_data,
            "user_input": user_input,
            "summary": summary_content,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "pattern_summary_few_shot"
        }
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 规律总结已保存到: {summary_file}")
        
        # 同时保存一个简化的版本供功能3使用
        simple_file = os.path.join(summary_dir, "latest_pattern_summary.txt")
        with open(simple_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        print(f"✓ 最新规律总结已保存到: {simple_file}，可供LLM分析功能使用")
        
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

def upgrade_strategy_with_stock(stock_symbol: str, user_input: str) -> Dict[str, Any]:
    """
    基于特定股票数据和用户输入升级策略（兼容旧版本）
    
    Args:
        stock_symbol: 股票代码
        user_input: 用户输入的策略优化想法
        
    Returns:
        生成的策略信息
    """
    # 从用户输入中提取股票代码
    extracted_symbols = extract_stock_symbols_from_text(user_input)
    extracted_dates = extract_dates_from_text(user_input)
    
    # 如果没有提取到股票代码，使用传入的stock_symbol
    all_symbols = extracted_symbols if extracted_symbols else [stock_symbol]
    
    print(f"从输入中提取到股票代码: {all_symbols}")
    print(f"从输入中提取到日期: {extracted_dates}")
    
    # 使用新的函数处理
    return upgrade_strategy_with_stock_and_dates(user_input, all_symbols, extracted_dates)

def get_latest_pattern_summary() -> Optional[str]:
    """
    获取最新的规律总结
    
    Returns:
        规律总结内容，如果没有则返回None
    """
    import os
    summary_dir = "pattern_summaries"
    
    # 确保目录存在
    if not os.path.exists(summary_dir):
        return None
    
    latest_file = os.path.join(summary_dir, "latest_pattern_summary.txt")
    
    if os.path.exists(latest_file):
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return None
    return None

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
    test_input = """2025-01-14 002115 三维通信：一字板涨停，封板极强
2025-01-13 002131 利欧股份：高开涨停，有炸板但回封"""
    new_strategy = upgrade_strategy_with_stock_and_dates(
        test_input, 
        ["002115", "002131"], 
        ["20250114", "20250113"]
    )
    print(f"\n新策略: {new_strategy.get('name', '未知')}")
