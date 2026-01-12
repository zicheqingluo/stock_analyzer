#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票连板分析主程序 - 精简版
只保留个股综合分析功能，支持股票名称查询
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


def main():
    """主函数"""
    # 获取当前脚本所在的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"股票连板分析系统启动...")
    print(f"当前目录: {current_dir}")
    
    # ==================== 动态导入数据获取模块 ====================
    data_fetcher_path = os.path.join(current_dir, "stock_data_fetcher.py")
    stock_data_fetcher = import_module("stock_data_fetcher", data_fetcher_path)
    
    # ==================== 动态导入监控分析模块 ====================
    # 注意：stock_monitor.py 可能导出了函数，但我们需要分析类的实例
    # 首先尝试导入 stock_monitor_analysis.py 来获取 StockMonitorAnalysis 类
    monitor_analysis_path = os.path.join(current_dir, "stock_monitor_analysis.py")
    monitor_analysis_module = import_module("stock_monitor_analysis", monitor_analysis_path)
    
    # 创建分析实例
    stock_monitor = None
    if monitor_analysis_module:
        try:
            # 创建 StockMonitorAnalysis 实例
            stock_monitor = monitor_analysis_module.StockMonitorAnalysis()
            print("股票监控分析模块初始化成功！")
        except Exception as e:
            print(f"创建监控分析实例失败: {e}")
            # 尝试导入 stock_monitor.py 作为备选
            monitor_path = os.path.join(current_dir, "stock_monitor.py")
            stock_monitor = import_module("stock_monitor", monitor_path)
    else:
        # 如果无法导入分析模块，尝试导入 stock_monitor.py
        monitor_path = os.path.join(current_dir, "stock_monitor.py")
        stock_monitor = import_module("stock_monitor", monitor_path)
    
    # ==================== 导入股票名称解析模块 ====================
    resolver_path = os.path.join(current_dir, "stock_name_resolver.py")
    resolver_module = import_module("stock_name_resolver", resolver_path)
    
    # ==================== 导入用户界面模块 ====================
    ui_path = os.path.join(current_dir, "stock_analysis_ui.py")
    ui_module = import_module("stock_analysis_ui", ui_path)
    
    if ui_module and stock_monitor and stock_data_fetcher:
        # 运行用户界面
        ui_module.main_ui(stock_monitor, stock_data_fetcher)
    else:
        print("用户界面模块导入失败，无法启动系统")
        print(f"UI模块: {'已导入' if ui_module else '未导入'}")
        print(f"监控模块: {'已导入' if stock_monitor else '未导入'}")
        print(f"数据获取模块: {'已导入' if stock_data_fetcher else '未导入'}")


if __name__ == "__main__":
    main()
