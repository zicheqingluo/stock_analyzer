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
        print(f"2. 模式分析 (量化分析股票走势模式)")
        print(f"3. LLM智能分析 (基于大模型的智能分析)")
        print(f"4. 退出")
        
        choice = input("\n请输入选项: ").strip()
        
        if choice in ["1", "2", "3", "4"]:
            return choice
        else:
            print("无效选项，请重新输入")


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
    print("版本: 7.0 (集成LLM智能分析)")
    print("=" * 60)
    print("核心功能:")
    print("  1. 个股综合分析 (涨停判断+异动监控+炸板检测+强势股判断)")
    print("  2. 模式分析 (量化分析股票走势模式)")
    print("  3. LLM智能分析 (基于大模型的智能分析)")
    print("  4. 退出")
    print("=" * 60)


def run_pattern_analysis():
    """
    运行模式分析
    """
    print(f"\n{'='*60}")
    print(f"模式分析")
    print(f"{'='*60}")
    
    # 获取股票名称并转换为代码
    code = get_stock_name_input()
    if not code:
        print("操作已取消")
        return
    
    try:
        # 尝试导入模式分析模块
        current_dir = os.path.dirname(os.path.abspath(__file__))
        pattern_path = os.path.join(current_dir, "stock_pattern_analyzer.py")
        
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        import importlib.util
        spec = importlib.util.spec_from_file_location("stock_pattern_analyzer", pattern_path)
        pattern_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pattern_module)
        
        # 执行分析
        analysis = pattern_module.analyze_stock_pattern(code)
        
        if "error" in analysis:
            print(f"模式分析失败: {analysis['error']}")
            return
        
        # 显示结果
        print(f"\n【模式分析结果】")
        print(f"股票代码: {analysis['symbol']}")
        print(f"分析日期: {analysis['analysis_date']}")
        print(f"回溯天数: {analysis['history_days']}")
        print(f"\n综合推荐: {analysis['recommendation']}")
        print(f"置信度: {analysis['confidence']*100:.1f}%")
        
        print(f"\n【详细分析】")
        patterns = analysis['patterns']
        
        print(f"1. 换手率模式: {patterns['turnover_pattern']['description']}")
        print(f"2. 强弱转换模式: {patterns['strength_pattern']['description']}")
        print(f"3. 量价关系模式: {patterns['volume_price_pattern']['description']}")
        print(f"4. 连板类型模式: {patterns['limit_up_pattern']['description']}")
        
        print(f"\n【关键因素】")
        for factor in patterns['comprehensive_assessment']['key_factors']:
            print(f"  • {factor}")
            
    except Exception as e:
        print(f"模式分析过程出错: {e}")
        import traceback
        traceback.print_exc()

def run_llm_analysis():
    """
    运行LLM智能分析
    """
    print(f"\n{'='*60}")
    print(f"LLM智能分析")
    print(f"{'='*60}")
    
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
        
        # 执行分析
        print("正在使用LLM进行智能分析...")
        result = llm_module.analyze_stock_with_llm(code, use_local=True)
        
        if "error" in result:
            print(f"LLM分析失败: {result['error']}")
            return
        
        # 显示结果
        print(f"\n【LLM智能分析结果】")
        print(f"股票代码: {result['symbol']}")
        print(f"股票名称: {result['name']}")
        print(f"分析日期: {result['analysis_date']}")
        
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
        
        # 询问是否保存经验
        save_choice = input("\n是否保存本次分析经验？(y/n): ").strip().lower()
        if save_choice == 'y':
            llm_module.llm_analyzer.save_experience(
                code, 
                result.get('llm_response', ''),
                tags=['llm_analysis', result.get('name', '')]
            )
            print("经验已保存")
            
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
            run_pattern_analysis()
        
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
    # 测试代码
    print("股票分析UI模块测试")
    # 这里可以添加测试代码
