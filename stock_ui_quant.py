#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票UI量化策略模块
包含量化策略相关函数
"""

import os
import sys
from typing import Dict, Any

def run_quant_strategy():
    """
    运行量化策略管理 - 现在用于总结交易规律
    """
    print(f"\n{'='*60}")
    print(f"交易规律总结")
    print(f"{'='*60}")
    print("功能：从您提供的股票分析中总结交易规律")
    print("注意：请提供包含股票代码和分析的文本")
    
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
        
        # 显示当前规律总结
        try:
            latest_summary = quant_module.get_latest_pattern_summary()
            if latest_summary:
                print(f"\n【最新规律总结】")
                print(latest_summary[:500] + "..." if len(latest_summary) > 500 else latest_summary)
                print()
        except:
            pass
        
        # 提供选项
        print("\n请选择操作:")
        print("1. 从分析文本中总结规律")
        print("2. 查看历史规律总结")
        print("3. 返回主菜单")
        
        choice = input("请输入选项: ").strip()
        
        if choice == "1":
            print("\n请输入您的股票分析文本（支持多行输入）:")
            print("请确保文本中包含股票代码（如002115）和您的分析")
            print("例如：")
            print("2025-01-14 002115 三维通信：一字板涨停，封板极强")
            print("2025-01-13 002131 利欧股份：高开涨停，有炸板但回封")
            print("- 金风科技：大高开加速上板，多次炸板后封板...")
            print("等等...")
            print("注意：日期格式可以是YYYY-MM-DD或YYYYMMDD")
            
            from stock_ui_input import get_multiline_input
            user_input = get_multiline_input("", "END")
            
            # 清理用户输入中的不可编码字符
            if user_input.strip():
                # 先清理输入
                cleaned_input = user_input.encode('utf-8', 'ignore').decode('utf-8')
                print("\n正在从您的分析中总结规律...")
                print("（这将提取股票代码、日期，获取数据，并让大模型总结规律）")
                
                # 提取股票代码和日期
                extracted_symbols = quant_module.extract_stock_symbols_from_text(cleaned_input)
                extracted_dates = quant_module.extract_dates_from_text(cleaned_input)
                
                print(f"\n【提取到的信息】")
                print(f"股票代码: {extracted_symbols}")
                # 只显示第一个日期
                if extracted_dates:
                    print(f"分析日期: {extracted_dates[0]}")
                else:
                    print("分析日期: 未找到，将使用最近日期")
                
                # 使用第一个股票代码作为主要分析对象
                if extracted_symbols:
                    # 获取数据并总结规律，只使用第一个日期
                    # 因为所有分析都是同一时间进行的
                    date_to_use = extracted_dates[0] if extracted_dates else None
                    
                    # 询问用户输入规律名称
                    print(f"\n【请输入规律名称】")
                    print(f"按回车使用自动生成名称，或输入自定义名称:")
                    custom_name = input("规律名称: ").strip()
                    
                    # 调用函数，传递自定义名称
                    new_strategy = quant_module.upgrade_strategy_with_stock_and_dates(
                        cleaned_input, 
                        extracted_symbols, 
                        [date_to_use] if date_to_use else [],
                        custom_name if custom_name else None
                    )
                    
                    if "error" in new_strategy:
                        print(f"总结规律失败: {new_strategy['error']}")
                    else:
                        print(f"\n【规律总结完成】")
                        print(f"名称: {new_strategy.get('name', '新总结')}")
                        print(f"描述: {new_strategy.get('description', '无描述')}")
                        print(f"\n【总结内容】")
                        content = new_strategy.get('content', '')
                        # 显示前800个字符
                        print(content[:800] + "..." if len(content) > 800 else content)
                        print(f"\n规律已保存，可在LLM分析功能中使用！")
                else:
                    print("未提取到股票代码，使用默认方式总结规律")
                    new_strategy = quant_module.upgrade_strategy(cleaned_input)
                    
                    if "error" in new_strategy:
                        print(f"总结规律失败: {new_strategy['error']}")
                    else:
                        print(f"\n【规律总结完成】")
                        print(f"名称: {new_strategy.get('name', '新总结')}")
                        print(f"描述: {new_strategy.get('description', '无描述')}")
                        print(f"\n【总结内容】")
                        content = new_strategy.get('content', '')
                        # 显示前800个字符
                        print(content[:800] + "..." if len(content) > 800 else content)
                        print(f"\n规律已保存，可在LLM分析功能中使用！")
            else:
                print("输入为空，跳过")
        elif choice == "2":
            try:
                strategies = quant_module.view_current_strategies()
                print(f"\n【历史策略/总结】")
                if strategies:
                    for i, strategy in enumerate(strategies, 1):
                        print(f"{i}. {strategy.get('name', '未命名')}")
                        print(f"   描述: {strategy.get('description', '无描述')}")
                        print(f"   创建时间: {strategy.get('created_at', '未知')}")
                        print(f"   类型: {strategy.get('type', '策略')}")
                        print()
                    
                    # 提供操作选项
                    print("\n请选择操作:")
                    print("1. 查看详细内容")
                    print("2. 删除策略/规律")
                    print("3. 重命名策略/规律")
                    print("4. 返回上一级")
                    
                    sub_choice = input("请输入选项 (1-4): ").strip()
                    
                    if sub_choice == "1":
                        # 查看详细内容
                        try:
                            idx = int(input(f"请输入要查看的策略序号 (1-{len(strategies)}): ").strip()) - 1
                            if 0 <= idx < len(strategies):
                                strategy = strategies[idx]
                                print(f"\n【{strategy.get('name', '未命名')}】")
                                print(f"描述: {strategy.get('description', '无描述')}")
                                print(f"创建时间: {strategy.get('created_at', '未知')}")
                                print(f"类型: {strategy.get('type', '策略')}")
                                print("\n【内容】")
                                content = strategy.get('content', '')
                                # 显示完整内容
                                print(content)
                                print("\n" + "="*60)
                                
                                # 询问是否继续查看
                                input("\n按回车键继续...")
                            else:
                                print("序号无效")
                        except ValueError:
                            print("请输入有效的数字")
                    
                    elif sub_choice == "2":
                        # 删除策略/规律
                        try:
                            idx = int(input(f"请输入要删除的策略序号 (1-{len(strategies)}): ").strip()) - 1
                            if 0 <= idx < len(strategies):
                                strategy = strategies[idx]
                                strategy_name = strategy.get('name', '')
                                confirm = input(f"确认删除 '{strategy_name}'？(y/n): ").strip().lower()
                                if confirm == 'y':
                                    success = quant_module.delete_strategy(strategy_name)
                                    if success:
                                        print(f"已成功删除: {strategy_name}")
                                    else:
                                        print(f"删除失败: {strategy_name}")
                                else:
                                    print("取消删除")
                            else:
                                print("序号无效")
                        except ValueError:
                            print("请输入有效的数字")
                    
                    elif sub_choice == "3":
                        # 重命名策略/规律
                        try:
                            idx = int(input(f"请输入要重命名的策略序号 (1-{len(strategies)}): ").strip()) - 1
                            if 0 <= idx < len(strategies):
                                strategy = strategies[idx]
                                old_name = strategy.get('name', '')
                                print(f"当前名称: {old_name}")
                                new_name = input("请输入新名称: ").strip()
                                if new_name:
                                    success = quant_module.rename_strategy(old_name, new_name)
                                    if success:
                                        print(f"已成功重命名: {old_name} -> {new_name}")
                                    else:
                                        print(f"重命名失败")
                                else:
                                    print("新名称不能为空")
                            else:
                                print("序号无效")
                        except ValueError:
                            print("请输入有效的数字")
                    
                    elif sub_choice == "4":
                        # 返回上一级
                        pass
                    else:
                        print("无效选项")
                        
                else:
                    print("暂无历史记录")
            except Exception as e:
                print(f"查看历史记录失败: {e}")
                import traceback
                traceback.print_exc()
                
    except Exception as e:
        print(f"功能执行失败: {e}")
        import traceback
        traceback.print_exc()

def create_quant_strategy_manager():
    """创建量化策略管理器文件"""
    # 这个函数现在在quant_strategy_manager.py中已经存在
    # 我们只需要确保文件存在即可
    pass
