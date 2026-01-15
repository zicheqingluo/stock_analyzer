#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票分析用户界面模块 - 精简版
"""

import os
import sys
from typing import Optional, List, Tuple, Dict, Any

# 导入格式化模块
try:
    from stock_ui_formatters import format_analysis_result
except ImportError:
    # 如果导入失败，定义简单的替代函数
    def format_analysis_result(analysis: Dict[str, Any]) -> str:
        """简化版格式化函数"""
        if not analysis:
            return "分析结果为空"
        return f"股票代码: {analysis.get('股票代码', '未知')}\n综合评级: {analysis.get('综合评级', '未知')}"


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
        
        try:
            choice = input("\n请输入选项: ").strip()
        except EOFError:
            # 处理Ctrl+D/Ctrl+Z
            print("\n检测到输入结束，退出程序")
            return "4"
        
        # 只取第一行，并移除可能的空白字符
        if "\n" in choice:
            choice = choice.split("\n")[0].strip()
        
        # 只取第一个字符（防止用户输入多行文本）
        if choice:
            choice = choice[0]
        
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
            # 清理不可编码字符
            cleaned_line = line.encode('utf-8', 'ignore').decode('utf-8')
            if cleaned_line.strip() == end_marker:
                break
            lines.append(cleaned_line)
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
    运行量化策略管理 - 现在用于总结交易规律
    """
    # 直接使用stock_ui_quant模块中的函数
    try:
        from stock_ui_quant import run_quant_strategy as run_quant_strategy_ui
        return run_quant_strategy_ui()
    except ImportError as e:
        print(f"无法导入量化策略UI模块: {e}")
        print("请确保stock_ui_quant.py文件存在")
        return

def create_quant_strategy_manager():
    """创建量化策略管理器文件"""
    # 委托给stock_ui_quant模块
    try:
        from stock_ui_quant import create_quant_strategy_manager as create_func
        return create_func()
    except ImportError:
        print("无法导入stock_ui_quant模块，无法创建量化策略管理器")
        return None

def run_llm_analysis():
    """
    运行LLM智能分析 - 增强版
    支持三个功能：
    1. 数据收集
    2. 提示词优化（通过案例学习）
    3. 智能分析
    """
    # 直接使用stock_ui_llm模块中的函数
    try:
        from stock_ui_llm import run_llm_analysis as run_llm_analysis_ui
        return run_llm_analysis_ui()
    except ImportError as e:
        print(f"无法导入LLM分析UI模块: {e}")
        print("请确保stock_ui_llm.py文件存在")
        return

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
            # 直接退出函数，让调用者处理退出
            return


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
    
    # 程序正常退出
    import sys
    sys.exit(0)
