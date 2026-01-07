# stock_monitor.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票异动监控与综合分析模块
主入口文件
"""

import sys
import os

# 添加当前目录到Python路径，确保可以导入模块
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from stock_monitor_analysis import StockMonitorAnalysis
from typing import Dict, List, Any
import pandas as pd

# 创建全局实例
monitor = StockMonitorAnalysis()

# 快捷函数 - 保持上层调用接口不变
def analyze_stock_changes(symbol: str) -> Dict[str, Any]:
    """分析股票异动情况的快捷函数"""
    return monitor.analyze_limit_up_changes(symbol)

def check_炸板_stock(symbol: str, date: str = None) -> Dict[str, Any]:
    """检查股票是否炸板的快捷函数"""
    return monitor.check_if_炸板(symbol, date)

def check_strong_stock(symbol: str, date: str = None) -> Dict[str, Any]:
    """检查股票是否强势股的快捷函数"""
    return monitor.check_if_strong_stock(symbol, date)

def comprehensive_analysis(symbol: str) -> Dict[str, Any]:
    """综合分析股票的快捷函数"""
    return monitor.comprehensive_stock_analysis(symbol)

def batch_analysis(symbols: List[str]) -> pd.DataFrame:
    """批量分析股票的快捷函数"""
    return monitor.batch_analysis(symbols)

def get_炸板_pool(date: str = None) -> pd.DataFrame:
    """获取炸板股池的快捷函数"""
    return monitor.get_炸板_stocks(date)

def get_strong_pool(date: str = None) -> pd.DataFrame:
    """获取强势股池的快捷函数"""
    return monitor.get_strong_stocks(date)

def get_changes_data(change_type: str = "封涨停板") -> pd.DataFrame:
    """获取异动数据的快捷函数"""
    return monitor.get_stock_changes(change_type)

def get_board_changes_data() -> pd.DataFrame:
    """获取板块异动数据的快捷函数"""
    return monitor.get_board_changes()

if __name__ == "__main__":
    # 测试代码
    print("股票监控模块测试")
    print("=" * 60)
    
    # 测试综合分析
    test_symbol = "000001"
    print(f"\n测试股票: {test_symbol}")
    
    analysis = comprehensive_analysis(test_symbol)
    
    print(f"\n测试结果:")
    print(f"股票代码: {analysis['股票代码']}")
    print(f"综合评级: {analysis['综合评级']}")
    print(f"评级说明: {analysis['评级说明']}")
    print(f"投资建议: {analysis['投资建议']}")
    print(f"是否涨停: {analysis['关键指标']['是否涨停']}")
    print(f"是否有炸板: {analysis['关键指标']['是否有炸板']}")
    print(f"是否漏单: {analysis['关键指标']['是否漏单']}")
    print(f"是否重新封板: {analysis['关键指标']['是否重新封板']}")
    print(f"是否强势股: {analysis['关键指标']['是否强势股']}")