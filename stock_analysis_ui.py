#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票分析用户界面模块 - 整合所有UI功能到一个文件中
"""

import os
import sys
from typing import Optional, List, Tuple, Dict, Any


# ==================== 显示功能模块 ====================
def format_analysis_result(analysis: Dict[str, Any]) -> str:
    """格式化分析结果为字符串"""
    if not analysis:
        return "分析结果为空"
    
    lines = []
    lines.append("=" * 60)
    lines.append(f"【个股综合分析】")
    lines.append("=" * 60)
    
    # 综合评级
    lines.append(f"\n【综合评级】")
    lines.append(f"评级: {analysis.get('综合评级', '未知')}")
    lines.append(f"说明: {analysis.get('评级说明', '未知')}")
    lines.append(f"建议: {analysis.get('投资建议', '未知')}")
    
    # 涨停异动分析
    lines.append(f"\n【涨停异动分析】")
    change_info = analysis.get('涨停异动分析', {})
    lines.extend(_format_change_info(change_info))
    
    # 炸板检测
    lines.append(f"\n【炸板检测】")
    炸板_info = analysis.get('炸板检测', {})
    lines.extend(_format_炸板_info(炸板_info))
    
    # 强势股判断
    lines.append(f"\n【强势股判断】")
    strong_info = analysis.get('强势股判断', {})
    lines.extend(_format_strong_info(strong_info))
    
    # 关键指标
    lines.append(f"\n【关键指标总结】")
    key_metrics = analysis.get('关键指标', {})
    lines.extend(_format_key_metrics(key_metrics))
    
    # 系统信息
    lines.append(f"\n【系统信息】")
    lines.append(f"分析时间: {analysis.get('分析时间', '未知')}")
    lines.append(f"查询日期: {analysis.get('查询日期', '未知')}")
    
    return "\n".join(lines)


def _format_change_info(change_info: Dict[str, Any]) -> List[str]:
    """格式化涨停异动信息"""
    lines = []
    
    if change_info.get('是否涨停', False):
        lines.append(f"✓ 今日涨停")
        if change_info.get('涨停时间'):
            lines.append(f"  涨停时间: {change_info['涨停时间']}")
        if change_info.get('涨停信息'):
            lines.append(f"  涨停信息: {change_info['涨停信息']}")
    else:
        lines.append(f"✗ 今日未涨停")
    
    if change_info.get('是否有炸板', False):
        lines.append(f"⚠ 有炸板异动")
        lines.append(f"  炸板次数: {change_info.get('炸板次数', 0)}")
        if change_info.get('炸板时间'):
            times = ', '.join(change_info['炸板时间'])
            lines.append(f"  炸板时间: {times}")
    
    if change_info.get('是否大笔卖出', False):
        lines.append(f"⚠ 有大笔卖出（漏单）")
        lines.append(f"  大笔卖出次数: {change_info.get('大笔卖出次数', 0)}")
        if change_info.get('大笔卖出时间'):
            times = ', '.join(change_info['大笔卖出时间'][:3])
            lines.append(f"  大笔卖出时间: {times}")
    
    return lines


def _format_炸板_info(炸板_info: Dict[str, Any]) -> List[str]:
    """格式化炸板信息"""
    lines = []
    
    if 炸板_info.get('是否在炸板股池', False):
        lines.append(f"⚠ 在炸板股池中")
        lines.append(f"  炸板次数: {炸板_info.get('炸板次数', 0)}")
        if 炸板_info.get('首次封板时间'):
            lines.append(f"  首次封板时间: {炸板_info['首次封板时间']}")
        if 炸板_info.get('涨跌幅'):
            lines.append(f"  涨跌幅: {炸板_info['涨跌幅']}%")
        if 炸板_info.get('炸板详情'):
            lines.append(f"  详情: {炸板_info['炸板详情']}")
    else:
        lines.append(f"✓ 不在炸板股池中")
        # 添加说明：盘中炸板次数与收盘后炸板池的区别
        if 炸板_info.get('炸板次数', 0) > 0:
            lines.append(f"  注: 盘中炸板{炸板_info.get('炸板次数', 0)}次，但收盘未在炸板股池中，可能已回封")
    
    return lines


def _format_strong_info(strong_info: Dict[str, Any]) -> List[str]:
    """格式化强势股信息"""
    lines = []
    
    if strong_info.get('是否在强势股池', False):
        lines.append(f"✓ 在强势股池中")
        if strong_info.get('入选理由'):
            lines.append(f"  入选理由: {strong_info['入选理由']}")
        if strong_info.get('是否新高'):
            lines.append(f"  是否新高: {strong_info['是否新高']}")
        if strong_info.get('涨停统计'):
            lines.append(f"  涨停统计: {strong_info['涨停统计']}")
        if strong_info.get('涨跌幅'):
            lines.append(f"  涨跌幅: {strong_info['涨跌幅']}%")
    else:
        lines.append(f"✗ 不在强势股池中")
    
    return lines


def _format_key_metrics(key_metrics: Dict[str, Any]) -> List[str]:
    """格式化关键指标"""
    lines = []
    
    metrics = [
        ("是否涨停", key_metrics.get('是否涨停', False)),
        ("是否一字板", key_metrics.get('是否一字板', False)),
        ("是否有炸板", key_metrics.get('是否有炸板', False)),
        ("是否漏单", key_metrics.get('是否漏单', False)),
        ("是否强势股", key_metrics.get('是否强势股', False)),
        ("炸板次数", key_metrics.get('炸板次数', 0)),
        ("最终是否涨停", key_metrics.get('最终是否涨停', False)),
        ("几连板", key_metrics.get('几连板', 0))
    ]
    
    for name, value in metrics:
        if isinstance(value, bool):
            display_value = "✓ 是" if value else "✗ 否"
        else:
            display_value = value
        lines.append(f"  {name}: {display_value}")
    
    return lines


# ==================== 输入处理模块 ====================
def get_stock_name_input() -> Optional[str]:
    """
    获取用户输入的股票名称并转换为代码
    
    Returns:
        股票代码，如果用户取消则返回None
    """
    while True:
        name = input("请输入股票名称（如：茅台、平安银行等）: ").strip()
        if not name:
            print("股票名称不能为空")
            continue
        
        # 尝试查找股票
        code = _find_stock_by_name(name)
        if code:
            return code
        
        print("未找到匹配的股票，请重新输入")
        
        # 询问是否继续
        choice = input("是否继续搜索？(y/n): ").strip().lower()
        if choice != 'y':
            return None


def _find_stock_by_name(name: str) -> Optional[str]:
    """查找股票"""
    # 尝试导入股票名称解析模块
    try:
        # 动态导入股票名称解析模块
        current_dir = os.path.dirname(os.path.abspath(__file__))
        resolver_path = os.path.join(current_dir, "stock_name_resolver.py")
        
        # 将当前目录添加到sys.path
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # 动态导入
        import importlib.util
        spec = importlib.util.spec_from_file_location("stock_name_resolver", resolver_path)
        resolver = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(resolver)
        
        # 查找股票
        results = resolver.search_stocks_by_name(name, max_results=10)
        
        if not results:
            return None
        
        if len(results) == 1:
            code, stock_name = results[0]
            print(f"找到股票: {stock_name} ({code})")
            return code
        
        # 显示多个结果让用户选择
        print(f"\n找到 {len(results)} 个相关股票:")
        print("-" * 40)
        for i, (code, stock_name) in enumerate(results, 1):
            print(f"{i:2d}. {stock_name:10s} ({code})")
        
        while True:
            choice = input("\n请输入序号选择股票 (输入q退出): ").strip()
            if choice.lower() == 'q':
                return None
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(results):
                    code, stock_name = results[idx]
                    print(f"已选择: {stock_name} ({code})")
                    return code
                else:
                    print(f"序号无效，请输入 1-{len(results)} 之间的数字")
            except ValueError:
                print("请输入有效的数字")
                
    except Exception as e:
        print(f"名称解析模块不可用: {e}")
        # 备选方案：直接输入代码
        print("请直接输入股票代码:")
        code = input("股票代码: ").strip()
        return code if code else None
    
    return None


def get_menu_choice() -> str:
    """获取用户菜单选择"""
    while True:
        print(f"\n请选择操作:")
        print(f"1. 个股综合分析 (推荐)")
        print(f"2. 量化策略 (查看和升级优化策略)")
        print(f"3. LLM智能分析 (基于大模型的智能分析)")
        print(f"4. 退出")
        
        choice = input("\n请输入选项: ").strip()
        
        if choice in ["1", "2", "3", "4"]:
            return choice
        else:
            print("无效选项，请重新输入")

def get_multiline_input(prompt: str, end_marker: str = "END") -> str:
    """
    获取多行输入，直到遇到结束标记
    
    Args:
        prompt: 提示信息
        end_marker: 结束标记（用户输入这个标记表示输入结束）
    
    Returns:
        用户输入的多行文本（不包含结束标记）
    """
    print(prompt)
    print(f"输入完成后，请在新的一行单独输入 '{end_marker}' 并按回车结束输入")
    print("开始输入:")
    
    lines = []
    while True:
        try:
            line = input()
            if line.strip() == end_marker:
                break
            lines.append(line)
        except EOFError:
            # 用户按Ctrl+D/Ctrl+Z
            print(f"\n检测到输入结束")
            break
    
    return "\n".join(lines)


# ==================== 主UI模块 ====================
def run_analysis(stock_monitor, stock_data_fetcher):
    """
    运行个股综合分析
    
    Args:
        stock_monitor: 监控模块
        stock_data_fetcher: 数据获取模块
    """
    print(f"\n{'='*60}")
    print(f"个股综合分析")
    print(f"{'='*60}")
    
    # 获取股票名称并转换为代码
    code = get_stock_name_input()
    if not code:
        print("操作已取消")
        return
    
    # 执行分析
    if stock_monitor is None:
        print("监控模块未加载，无法进行综合分析")
        return
    
    try:
        analysis = stock_monitor.comprehensive_analysis(code)
    except Exception as e:
        print(f"分析过程出错: {e}")
        import traceback
        traceback.print_exc()
        return
    
    if analysis:
        result_str = format_analysis_result(analysis)
        print(result_str)
    else:
        print("分析失败")


def show_original_function(stock_data_fetcher):
    """
    显示原始系统功能
    
    Args:
        stock_data_fetcher: 数据获取模块
    """
    if stock_data_fetcher is None:
        print("原始系统模块未加载")
        return
    
    # 获取股票名称并转换为代码
    code = get_stock_name_input()
    if not code:
        print("操作已取消")
        return
    
    info = stock_data_fetcher.get_stock_info(code)
    print(f"\n原始系统信息:")
    for key, value in info.items():
        if value:
            print(f"{key}: {value}")


def show_menu():
    """显示菜单"""
    print("股票连板分析系统 - 智能版")
    print("版本: 8.0 (集成量化策略管理)")
    print("=" * 60)
    print("核心功能:")
    print("  1. 个股综合分析 (涨停判断+异动监控+炸板检测+强势股判断)")
    print("  2. 量化策略 (查看和升级优化策略)")
    print("  3. LLM智能分析 (基于大模型的智能分析)")
    print("  4. 退出")
    print("=" * 60)


def run_quant_strategy():
    """
    运行量化策略管理
    """
    print(f"\n{'='*60}")
    print(f"量化策略管理")
    print(f"{'='*60}")
    
    try:
        # 尝试导入量化策略模块
        current_dir = os.path.dirname(os.path.abspath(__file__))
        quant_path = os.path.join(current_dir, "quant_strategy_manager.py")
        
        # 检查文件是否存在
        if not os.path.exists(quant_path):
            print("量化策略模块不存在，正在创建...")
            # 创建量化策略管理器文件
            create_quant_strategy_manager()
        
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        import importlib.util
        spec = importlib.util.spec_from_file_location("quant_strategy_manager", quant_path)
        quant_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(quant_module)
        
        # 显示当前策略
        strategies = quant_module.view_current_strategies()
        print(f"\n【当前量化策略】")
        if strategies:
            for i, strategy in enumerate(strategies, 1):
                print(f"{i}. {strategy.get('name', '未命名策略')}")
                print(f"   描述: {strategy.get('description', '无描述')}")
                print(f"   创建时间: {strategy.get('created_at', '未知')}")
                print()
        else:
            print("暂无策略，请创建新策略")
        
        # 提供选项
        print("\n请选择操作:")
        print("1. 升级优化策略")
        print("2. 查看策略详情")
        print("3. 返回主菜单")
        
        choice = input("请输入选项: ").strip()
        
        if choice == "1":
            print("\n请输入您的策略优化想法（支持多行输入）:")
            print("例如：")
            print("- 增加对成交量的要求")
            print("- 优化止损条件")
            print("- 结合市场情绪指标")
            print("- 等等...")
            
            user_input = get_multiline_input("", "END")
            
            if user_input.strip():
                print("\n正在生成优化策略...")
                new_strategy = quant_module.upgrade_strategy(user_input)
                print(f"\n【新生成的策略】")
                print(f"名称: {new_strategy.get('name', '新策略')}")
                print(f"描述: {new_strategy.get('description', '无描述')}")
                print(f"内容:\n{new_strategy.get('content', '无内容')}")
                print(f"\n策略已保存到本地!")
            else:
                print("输入为空，跳过策略升级")
        elif choice == "2":
            if strategies:
                try:
                    idx = int(input(f"请输入要查看的策略编号 (1-{len(strategies)}): ").strip())
                    if 1 <= idx <= len(strategies):
                        strategy = strategies[idx-1]
                        print(f"\n【策略详情】")
                        print(f"名称: {strategy.get('name', '未命名策略')}")
                        print(f"描述: {strategy.get('description', '无描述')}")
                        print(f"创建时间: {strategy.get('created_at', '未知')}")
                        print(f"内容:\n{strategy.get('content', '无内容')}")
                    else:
                        print("编号超出范围")
                except ValueError:
                    print("请输入有效的数字")
            else:
                print("暂无策略可查看")
                
    except Exception as e:
        print(f"量化策略功能失败: {e}")
        import traceback
        traceback.print_exc()

def create_quant_strategy_manager():
    """创建量化策略管理器文件"""
    quant_content = '''#!/usr/bin/env python3
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
        user_input: 用户输入的优化想法（可能包含多行）
        
    Returns:
        新生成的策略
    """
    # 加载现有策略
    existing_strategies = load_strategies()
    
    # 清理用户输入，移除可能的空白行
    user_input_clean = "\n".join([line.strip() for line in user_input.split("\n") if line.strip()])
    
    # 构建更专业的量化策略提示词
    prompt = f"""
你是一个专业的量化策略分析师，专注于中国A股市场的短线交易策略。
请根据以下信息生成一个新的、可执行的量化交易策略：

【现有策略库摘要】
{json.dumps([{'name': s['name'], 'desc': s['description']} for s in existing_strategies[:3]], ensure_ascii=False, indent=2)}

【用户的新需求与优化方向】
{user_input_clean}

【市场背景】
当前A股市场以短线交易为主，涨停板策略、连板股策略、回调买入策略等较为有效。
需要结合技术分析、资金流向、市场情绪等多维度因素。

【请生成完整的量化交易策略，必须包含以下部分：】
1. 策略名称（体现策略核心特点）
2. 策略描述（简要说明策略原理和适用场景）
3. 核心逻辑（策略的核心理念和理论基础）
4. 买入条件（具体、可量化的买入信号，至少5个条件）
5. 卖出条件（包括止盈、止损、时间止损等具体规则）
6. 风险控制（仓位管理、最大回撤控制、风险规避措施）
7. 适用市场环境（说明在何种市场环境下表现最佳）
8. 策略优化建议（如何回测、调整参数、持续改进）

【要求】
1. 内容必须具体、可执行、可量化
2. 针对中国A股市场的特点设计
3. 考虑实际交易中的滑点、手续费等因素
4. 提供明确的参数和阈值
5. 用中文回答，结构清晰

请开始生成策略：
"""
    
    # 调用LLM生成新策略 - 使用专门的方法
    try:
        # 尝试导入LLM分析器
        current_dir = os.path.dirname(os.path.abspath(__file__))
        llm_path = os.path.join(current_dir, "stock_llm_analyzer.py")
            
        spec = importlib.util.spec_from_file_location("stock_llm_analyzer", llm_path)
        llm_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(llm_module)
            
        # 使用专门的量化策略生成方法
        new_strategy = llm_module.llm_analyzer.generate_quant_strategy(user_input_clean, existing_strategies)
            
        # 如果生成失败，使用备用方法
        if new_strategy.get("source") == "error_fallback":
            # 使用原来的方法
            llm_response = llm_module.llm_analyzer._call_local_llm(prompt)
            strategy_content = llm_response
                
            new_strategy = {
                "name": f"优化策略-{datetime.datetime.now().strftime('%Y%m%d-%H%M')}",
                "description": f"基于用户需求生成的策略: {user_input_clean[:50]}...",
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "content": strategy_content,
                "user_input": user_input_clean,
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
            "description": f"基于用户需求生成的策略: {user_input_clean[:50]}...",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": f"""
策略名称：基于用户输入的策略
用户需求：{user_input_clean}

策略逻辑：
1. 结合用户需求与现有策略框架
2. 优化买入卖出条件
3. 加强风险控制

具体规则待进一步细化。
            """,
            "user_input": user_input_clean,
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
'''
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    quant_path = os.path.join(current_dir, "quant_strategy_manager.py")
    
    with open(quant_path, 'w', encoding='utf-8') as f:
        f.write(quant_content)
    
    print(f"量化策略管理器已创建: {quant_path}")

def run_llm_analysis():
    """
    运行LLM智能分析 - 增强版
    支持三个功能：
    1. 数据收集
    2. 提示词优化（通过案例学习）
    3. 智能分析
    """
    print(f"\n{'='*60}")
    print(f"LLM智能分析 - 三功能版")
    print(f"{'='*60}")
    
    # 显示功能选项
    print("\n请选择分析模式:")
    print("1. 标准分析（仅使用现有经验规则）")
    print("2. 分析并优化提示词（将本次分析加入案例库）")
    print("3. 仅收集数据（不进行LLM分析）")
    
    mode_choice = input("\n请选择模式 (1-3, 默认1): ").strip()
    if not mode_choice:
        mode_choice = "1"
    
    # 获取股票名称并转换为代码
    code = get_stock_name_input()
    if not code:
        print("操作已取消")
        return
    
    try:
        # 尝试导入LLM分析模块
        current_dir = os.path.dirname(os.path.abspath(__file__))
        llm_path = os.path.join(current_dir, "stock_llm_analyzer.py")
        
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        import importlib.util
        spec = importlib.util.spec_from_file_location("stock_llm_analyzer", llm_path)
        llm_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(llm_module)
        
        # 根据模式执行分析
        update_prompt = (mode_choice == "2")
        only_collect_data = (mode_choice == "3")
        
        if only_collect_data:
            print("\n【功能1】仅收集数据模式...")
            # 只收集数据
            stock_data = llm_module.llm_analyzer.collect_stock_data(code)
            
            if "error" in stock_data:
                print(f"数据收集失败: {stock_data['error']}")
                return
            
            print(f"\n【数据收集结果】")
            print(f"股票代码: {stock_data['symbol']}")
            print(f"股票名称: {stock_data['name']}")
            print(f"分析日期: {stock_data['analysis_date']}")
            
            print(f"\n【关键指标】")
            key_metrics = stock_data.get('key_metrics', {})
            for key, value in key_metrics.items():
                print(f"  {key}: {value}")
            
            print(f"\n【历史数据摘要】")
            print(stock_data.get('history_summary', '无数据'))
            
            print(f"\n【数据验证】")
            print("请检查以上数据是否正确，特别是日期和涨停信息")
            
        else:
            # 执行完整分析
            print(f"\n正在使用LLM进行智能分析...")
            result = llm_module.analyze_stock_with_llm(code, use_local=True, update_prompt=update_prompt)
            
            if "error" in result:
                print(f"LLM分析失败: {result['error']}")
                return
            
            # 显示结果
            print(f"\n【LLM智能分析结果】")
            print(f"股票代码: {result['symbol']}")
            print(f"股票名称: {result['name']}")
            print(f"分析日期: {result['analysis_date']}")
            print(f"分析类型: {result.get('analysis_type', '标准')}")
            
            print(f"\n【关键指标】")
            key_metrics = result.get('key_metrics', {})
            for key, value in key_metrics.items():
                print(f"  {key}: {value}")
            
            print(f"\n【历史数据摘要】")
            print(result.get('history_summary', '无数据'))
            
            print(f"\n【LLM分析结论】")
            analysis = result.get('analysis', {})
            if analysis:
                for section, content in analysis.items():
                    if content:
                        print(f"\n{section}:")
                        print(content)
            else:
                print(result.get('llm_response', '无分析结果'))
            
            if update_prompt:
                print(f"\n✓ 本次分析已用于优化提示词库")
            
            # 询问是否保存经验
            save_choice = input("\n是否保存本次分析经验到文件？(y/n): ").strip().lower()
            if save_choice == 'y':
                llm_module.llm_analyzer.save_experience(
                    code, 
                    result.get('llm_response', ''),
                    tags=['llm_analysis', result.get('name', ''), f'mode_{mode_choice}']
                )
                print("经验已保存到文件")
                
    except Exception as e:
        print(f"LLM分析过程出错: {e}")
        import traceback
        traceback.print_exc()

def main_ui(stock_monitor, stock_data_fetcher):
    """
    主用户界面函数
    
    Args:
        stock_monitor: 监控模块
        stock_data_fetcher: 数据获取模块
    """
    show_menu()
    
    # 检查模块加载状态
    if stock_monitor is None:
        print("警告: 监控模块未加载，部分功能不可用")
    
    while True:
        choice = get_menu_choice()
        
        if choice == "1":
            if stock_monitor is not None:
                run_analysis(stock_monitor, stock_data_fetcher)
            else:
                print("监控模块未加载，无法进行综合分析")
        
        elif choice == "2":
            run_quant_strategy()
        
        elif choice == "3":
            run_llm_analysis()
        
        elif choice == "4":
            print("感谢使用，再见！")
            # 先跳出循环
            break
    
    # 退出程序
    import sys
    sys.exit(0)


if __name__ == "__main__":
    # 主程序入口
    print("股票分析UI模块启动...")
    
    # 尝试导入必要的模块
    try:
        # 导入监控模块
        import importlib.util
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 尝试导入stock_monitor_analysis
        monitor_path = os.path.join(current_dir, "stock_monitor_analysis.py")
        if os.path.exists(monitor_path):
            spec = importlib.util.spec_from_file_location("stock_monitor_analysis", monitor_path)
            stock_monitor_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(stock_monitor_module)
            stock_monitor = stock_monitor_module.StockMonitorAnalysis()
            print("✓ 监控模块加载成功")
        else:
            print("✗ 监控模块文件不存在")
            stock_monitor = None
        
        # 尝试导入stock_data_fetcher
        fetcher_path = os.path.join(current_dir, "stock_data_fetcher.py")
        if os.path.exists(fetcher_path):
            spec = importlib.util.spec_from_file_location("stock_data_fetcher", fetcher_path)
            stock_data_fetcher_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(stock_data_fetcher_module)
            stock_data_fetcher = stock_data_fetcher_module
            print("✓ 数据获取模块加载成功")
        else:
            print("✗ 数据获取模块文件不存在")
            stock_data_fetcher = None
        
        # 运行主UI
        main_ui(stock_monitor, stock_data_fetcher)
        
    except Exception as e:
        print(f"启动过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        
        # 尝试使用简化版本
        print("\n尝试使用简化版本...")
        # 创建虚拟模块
        class DummyMonitor:
            def comprehensive_analysis(self, symbol):
                return {
                    '股票代码': symbol,
                    '分析时间': '2024-01-01 00:00:00',
                    '综合评级': '测试',
                    '评级说明': '测试模式',
                    '投资建议': '请检查模块加载',
                    '关键指标': {
                        '是否涨停': False,
                        '是否有炸板': False,
                        '是否漏单': False,
                        '是否重新封板': False,
                        '是否强势股': False,
                        '炸板次数': 0,
                        '最终是否涨停': False,
                        '几连板': 0
                    }
                }
        
        class DummyFetcher:
            def get_stock_info(self, symbol):
                return {'代码': symbol, '名称': '测试股票'}
        
        dummy_monitor = DummyMonitor()
        dummy_fetcher = DummyFetcher()
        
        # 运行简化UI
        show_menu()
        while True:
            choice = get_menu_choice()
            
            if choice == "1":
                code = get_stock_name_input()
                if code:
                    analysis = dummy_monitor.comprehensive_analysis(code)
                    print(f"\n【测试分析结果】")
                    print(f"股票代码: {analysis['股票代码']}")
                    print(f"综合评级: {analysis['综合评级']}")
                    print(f"投资建议: {analysis['投资建议']}")
            
            elif choice == "2":
                run_quant_strategy()
            
            elif choice == "3":
                run_llm_analysis()
            
            elif choice == "4":
                print("感谢使用，再见！")
                break
