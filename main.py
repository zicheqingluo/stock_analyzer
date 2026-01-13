#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票连板分析主程序 - 精简版
只保留个股综合分析功能，支持股票名称查询
支持命令行参数直接分析股票
"""

import os
import sys
import importlib.util


def import_module(module_name, file_path):
    """
    动态导入模块
    
    Args:
        module_name: 模块名称
        file_path: 模块文件路径
        
    Returns:
        导入的模块对象，如果失败返回None
    """
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"{module_name}模块导入成功！")
        return module
    except Exception as e:
        print(f"导入{module_name}模块失败: {e}")
        return None


def analyze_stock_directly(symbol, analysis_type="comprehensive"):
    """
    直接分析股票，不通过交互式菜单
    
    Args:
        symbol: 股票代码
        analysis_type: 分析类型，可选值: "comprehensive", "pattern", "llm"
    """
    # 获取当前脚本所在的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 导入必要的模块
    data_fetcher_path = os.path.join(current_dir, "stock_data_fetcher.py")
    stock_data_fetcher = import_module("stock_data_fetcher", data_fetcher_path)
    
    monitor_path = os.path.join(current_dir, "stock_monitor.py")
    stock_monitor = import_module("stock_monitor", monitor_path)
    
    if analysis_type == "comprehensive":
        if stock_monitor:
            print(f"\n正在对 {symbol} 进行综合分析...")
            print("=" * 60)
            
            # 使用监控模块进行综合分析
            try:
                analysis = stock_monitor.comprehensive_analysis(symbol)
                
                # 导入UI模块来格式化显示结果
                ui_path = os.path.join(current_dir, "stock_analysis_ui.py")
                ui_module = import_module("stock_analysis_ui", ui_path)
                
                if ui_module and analysis:
                    result_str = ui_module.format_analysis_result(analysis)
                    print(result_str)
                else:
                    # 直接打印分析结果
                    print(f"股票代码: {analysis.get('股票代码', '未知')}")
                    print(f"综合评级: {analysis.get('综合评级', '未知')}")
                    print(f"评级说明: {analysis.get('评级说明', '未知')}")
                    print(f"投资建议: {analysis.get('投资建议', '未知')}")
                    
                    # 打印关键指标
                    print(f"\n关键指标:")
                    key_metrics = analysis.get('关键指标', {})
                    for key, value in key_metrics.items():
                        print(f"  {key}: {value}")
            except Exception as e:
                print(f"综合分析失败: {e}")
                import traceback
                traceback.print_exc()
    
    elif analysis_type == "pattern":
        # 模式分析
        pattern_path = os.path.join(current_dir, "stock_pattern_analyzer.py")
        pattern_module = import_module("stock_pattern_analyzer", pattern_path)
        
        if pattern_module:
            print(f"\n正在对 {symbol} 进行模式分析...")
            print("=" * 60)
            
            try:
                analysis = pattern_module.analyze_stock_pattern(symbol)
                
                if "error" in analysis:
                    print(f"模式分析失败: {analysis['error']}")
                    return
                
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
                print(f"模式分析失败: {e}")
                import traceback
                traceback.print_exc()
    
    elif analysis_type == "llm":
        # LLM智能分析
        llm_path = os.path.join(current_dir, "stock_llm_analyzer.py")
        llm_module = import_module("stock_llm_analyzer", llm_path)
        
        if llm_module:
            print(f"\n正在对 {symbol} 进行LLM智能分析...")
            print("=" * 60)
            
            try:
                result = llm_module.analyze_stock_with_llm(symbol, use_local=True)
                
                if "error" in result:
                    print(f"LLM分析失败: {result['error']}")
                    return
                
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
            except Exception as e:
                print(f"LLM分析失败: {e}")
                import traceback
                traceback.print_exc()


def main():
    """主函数"""
    # 获取当前脚本所在的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        # 检查是否是帮助请求
        if sys.argv[1] in ["-h", "--help", "help"]:
            print("股票连板分析系统 - 使用说明")
            print("=" * 50)
            print("用法:")
            print("  python main.py [股票代码] [分析类型]")
            print()
            print("参数说明:")
            print("  股票代码: 6位股票代码，例如: 002115")
            print("  分析类型: (可选) comprehensive, pattern, llm")
            print("           默认: comprehensive (综合分析)")
            print()
            print("示例:")
            print("  python main.py 002115              # 综合分析三维通信")
            print("  python main.py 002115 pattern      # 模式分析三维通信")
            print("  python main.py 002115 llm          # LLM智能分析三维通信")
            print("  python main.py                     # 进入交互式菜单")
            return
        
        # 有命令行参数，直接分析股票
        symbol = sys.argv[1]
        
        # 检查是否有第二个参数指定分析类型
        analysis_type = "comprehensive"  # 默认综合分析
        if len(sys.argv) > 2:
            analysis_type = sys.argv[2].lower()
            if analysis_type not in ["comprehensive", "pattern", "llm"]:
                print(f"未知的分析类型: {analysis_type}，使用默认综合分析")
                analysis_type = "comprehensive"
        
        print(f"股票连板分析系统启动...")
        print(f"当前目录: {current_dir}")
        print(f"分析股票: {symbol}")
        print(f"分析类型: {analysis_type}")
        print("=" * 60)
        
        # 直接分析股票
        analyze_stock_directly(symbol, analysis_type)
        
        # 询问是否进行其他分析
        if len(sys.argv) <= 3:  # 如果没有指定不询问
            choice = input("\n是否进行其他分析？(y/n): ").strip().lower()
            if choice == 'y':
                print("进入交互模式...")
                # 继续执行下面的交互模式代码
            else:
                return
    
    # 如果没有命令行参数或用户选择继续，进入交互模式
    print(f"股票连板分析系统启动...")
    print(f"当前目录: {current_dir}")
    
    # ==================== 动态导入数据获取模块 ====================
    data_fetcher_path = os.path.join(current_dir, "stock_data_fetcher.py")
    stock_data_fetcher = import_module("stock_data_fetcher", data_fetcher_path)
    
    # ==================== 动态导入监控模块 ====================
    monitor_path = os.path.join(current_dir, "stock_monitor.py")
    stock_monitor = import_module("stock_monitor", monitor_path)
    
    # ==================== 导入股票名称解析模块 ====================
    resolver_path = os.path.join(current_dir, "stock_name_resolver.py")
    resolver_module = import_module("stock_name_resolver", resolver_path)
    
    # ==================== 导入用户界面模块 ====================
    ui_path = os.path.join(current_dir, "stock_analysis_ui.py")
    ui_module = import_module("stock_analysis_ui", ui_path)
    
    # ==================== 导入模式分析模块 ====================
    pattern_path = os.path.join(current_dir, "stock_pattern_analyzer.py")
    pattern_module = import_module("stock_pattern_analyzer", pattern_path)
    
    if ui_module:
        # 运行用户界面
        ui_module.main_ui(stock_monitor, stock_data_fetcher)
    else:
        print("用户界面模块导入失败，无法启动系统")


if __name__ == "__main__":
    main()
