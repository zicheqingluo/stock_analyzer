#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票分析主UI模块 - 协调各UI模块
由于导入问题，这里重新设计为独立模块
"""

import os
import sys
from typing import Optional


def import_sub_module(module_name):
    """动态导入子模块"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    module_path = os.path.join(current_dir, f"{module_name}.py")
    
    try:
        # 将当前目录添加到sys.path
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # 动态导入
        import importlib
        module = importlib.import_module(module_name)
        return module
    except Exception as e:
        print(f"导入{module_name}模块失败: {e}")
        return None


# 尝试导入依赖模块
try:
    import stock_ui_display as display
except ImportError:
    print("警告: 无法导入display模块，将使用简化显示")
    display = None

try:
    import stock_ui_input as input_handler
except ImportError:
    print("警告: 无法导入input模块，将使用简化输入")
    input_handler = None


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
        return
    
    if analysis:
        result_str = format_analysis_result(analysis)
        print(result_str)
    else:
        print("分析失败")


def get_stock_name_input():
    """获取股票名称输入"""
    if input_handler and hasattr(input_handler, 'get_stock_name_input'):
        return input_handler.get_stock_name_input()
    else:
        # 简化版本
        while True:
            name = input("请输入股票名称（如：茅台、平安银行等）: ").strip()
            if not name:
                print("股票名称不能为空")
                continue
            
            # 尝试导入resolver模块
            try:
                import stock_name_resolver as resolver
                code = resolver.get_stock_code_by_name(name)
                if code:
                    print(f"找到股票: {name} ({code})")
                    return code
                else:
                    print(f"未找到股票: {name}")
            except ImportError:
                print("名称解析模块不可用，请直接输入股票代码: ")
                code = input("股票代码: ").strip()
                if code:
                    return code
            
            # 询问是否继续
            choice = input("是否继续搜索？(y/n): ").strip().lower()
            if choice != 'y':
                return None


def format_analysis_result(analysis):
    """格式化分析结果"""
    if display and hasattr(display, 'format_analysis_result'):
        return display.format_analysis_result(analysis)
    else:
        # 简化版本
        lines = []
        lines.append("=" * 60)
        lines.append(f"【个股综合分析】")
        lines.append("=" * 60)
        
        # 基本信息
        lines.append(f"\n【综合评级】")
        lines.append(f"评级: {analysis.get('综合评级', '未知')}")
        lines.append(f"说明: {analysis.get('评级说明', '未知')}")
        
        # 关键指标
        lines.append(f"\n【关键指标】")
        key_metrics = analysis.get('关键指标', {})
        for key, value in key_metrics.items():
            if isinstance(value, bool):
                display_value = "✓ 是" if value else "✗ 否"
            else:
                display_value = value
            lines.append(f"{key}: {display_value}")
        
        # 系统信息
        lines.append(f"\n【系统信息】")
        lines.append(f"分析时间: {analysis.get('分析时间', '未知')}")
        
        return "\n".join(lines)


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
    print("股票连板分析系统 - 专业版")
    print("版本: 5.0 (集成异动监控与综合分析)")
    print("=" * 60)
    print("核心功能:")
    print("  1. 个股综合分析 (涨停判断+异动监控+炸板检测+强势股判断)")
    print("  2. 退出")
    print("=" * 60)


def get_menu_choice():
    """获取菜单选择"""
    while True:
        print(f"\n请选择操作:")
        print(f"1. 个股综合分析 (推荐)")
        print(f"2. 退出")
        
        choice = input("\n请输入选项: ").strip()
        
        if choice in ["1", "2"]:
            return choice
        else:
            print("无效选项，请重新输入")


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
            print("感谢使用，再见！")
            break