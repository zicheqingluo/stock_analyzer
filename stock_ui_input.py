#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票分析输入模块 - 处理用户输入和交互
"""

from typing import Optional
from stock_name_resolver import get_stock_code_by_name, interactive_select_stock


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
        
        # 尝试自动查找
        code = get_stock_code_by_name(name)
        if code:
            print(f"找到股票: {name} ({code})")
            return code
        
        # 如果自动查找失败，进行交互式选择
        print(f"正在搜索股票 '{name}'...")
        code = interactive_select_stock(name)
        if code:
            return code
        
        print("未找到匹配的股票，请重新输入")
        
        # 询问是否继续
        choice = input("是否继续搜索？(y/n): ").strip().lower()
        if choice != 'y':
            return None


def get_menu_choice() -> str:
    """
    获取用户菜单选择
    
    Returns:
        用户选择
    """
    while True:
        print(f"\n请选择操作:")
        print(f"1. 个股综合分析 (推荐)")
        print(f"2. 退出")
        
        choice = input("\n请输入选项: ").strip()
        
        if choice in ["1", "2"]:
            return choice
        else:
            print("无效选项，请重新输入")


def get_batch_input() -> list:
    """
    获取批量分析输入
    
    Returns:
        股票代码列表
    """
    while True:
        input_str = input("请输入多个股票名称（用逗号分隔，如：茅台,平安银行,宁德时代）: ").strip()
        if not input_str:
            print("输入不能为空")
            continue
        
        names = [name.strip() for name in input_str.split(',')]
        codes = []
        
        for name in names:
            code = get_stock_code_by_name(name)
            if code:
                codes.append(code)
                print(f"找到: {name} -> {code}")
            else:
                print(f"未找到股票: {name}")
        
        if codes:
            return codes
        else:
            print("未找到任何有效股票，请重新输入")


def confirm_exit() -> bool:
    """确认退出"""
    choice = input("确定要退出吗？(y/n): ").strip().lower()
    return choice == 'y'