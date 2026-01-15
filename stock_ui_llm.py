#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票UI LLM分析模块
包含LLM分析相关函数
"""

import os
import sys
from typing import Optional, Dict, Any

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
    
    # 显示LLM提供商选项
    print("\n请选择LLM提供商:")
    print("1. DeepSeek API（需要API密钥）")
    print("2. OpenAI API（需要API密钥）")
    print("3. 硅基流动 API（需要API密钥）")
    
    llm_choice = input("\n请选择LLM提供商 (1-3): ").strip()
    if not llm_choice:
        llm_choice = "1"
    
    # 根据选择配置LLM
    use_local = False
    llm_provider = "deepseek"
    
    if llm_choice == "1":
        # 检查是否配置了DeepSeek API密钥
        deepseek_key = os.environ.get("DEEPSEEK_API_KEY")
        if not deepseek_key:
            print("\n错误: 未设置DeepSeek API密钥")
            print("请在环境变量中设置 DEEPSEEK_API_KEY")
            print("例如: export DEEPSEEK_API_KEY='your-api-key-here'")
            print("或输入您的API密钥（输入后仅本次会话有效）:")
            temp_key = input("DeepSeek API密钥: ").strip()
            if temp_key:
                os.environ["DEEPSEEK_API_KEY"] = temp_key
                os.environ["LLM_PROVIDER"] = "deepseek"
                llm_provider = "deepseek"
                print("已使用临时API密钥")
            else:
                print("错误: 需要API密钥才能继续")
                return
        else:
            os.environ["LLM_PROVIDER"] = "deepseek"
            llm_provider = "deepseek"
    
    elif llm_choice == "2":
        # 检查是否配置了OpenAI API密钥
        openai_key = os.environ.get("OPENAI_API_KEY")
        if not openai_key:
            print("\n错误: 未设置OpenAI API密钥")
            print("请在环境变量中设置 OPENAI_API_KEY")
            print("例如: export OPENAI_API_KEY='your-api-key-here'")
            print("或输入您的API密钥（输入后仅本次会话有效）:")
            temp_key = input("OpenAI API密钥: ").strip()
            if temp_key:
                os.environ["OPENAI_API_KEY"] = temp_key
                os.environ["LLM_PROVIDER"] = "openai"
                llm_provider = "openai"
                print("已使用临时API密钥")
            else:
                print("错误: 需要API密钥才能继续")
                return
        else:
            os.environ["LLM_PROVIDER"] = "openai"
            llm_provider = "openai"
    
    elif llm_choice == "3":
        # 检查是否配置了硅基流动API密钥
        siliconflow_key = os.environ.get("SILICONFLOW_API_KEY")
        if not siliconflow_key:
            print("\n错误: 未设置硅基流动API密钥")
            print("请在环境变量中设置 SILICONFLOW_API_KEY")
            print("例如: export SILICONFLOW_API_KEY='your-api-key-here'")
            print("或输入您的API密钥（输入后仅本次会话有效）:")
            temp_key = input("硅基流动API密钥: ").strip()
            if temp_key:
                os.environ["SILICONFLOW_API_KEY"] = temp_key
                os.environ["LLM_PROVIDER"] = "siliconflow"
                llm_provider = "siliconflow"
                print("已使用临时API密钥")
            else:
                print("错误: 需要API密钥才能继续")
                return
        else:
            os.environ["LLM_PROVIDER"] = "siliconflow"
            llm_provider = "siliconflow"
    else:
        print("错误: 无效的选择")
        return
    
    # 显示功能选项
    print(f"\n当前使用: {llm_provider}")
    print("\n请选择分析模式:")
    print("1. 标准分析（使用API进行智能分析）")
    print("2. 分析并优化提示词（将本次分析加入案例库）")
    print("3. 仅收集数据（不进行LLM分析）")
    
    mode_choice = input("\n请选择模式 (1-3, 默认1): ").strip()
    if not mode_choice:
        mode_choice = "1"
    
    # 询问是否使用特定规律
    use_specific_pattern = False
    pattern_choice = None
    
    if mode_choice in ["1", "2"]:
        try:
            # 尝试获取可用的规律
            from quant_strategy_manager import view_current_strategies
            strategies = view_current_strategies()
            pattern_strategies = [s for s in strategies if s.get("type") == "pattern_summary_few_shot"]
            
            if pattern_strategies:
                print(f"\n发现 {len(pattern_strategies)} 条用户总结的交易规律:")
                for i, strategy in enumerate(pattern_strategies[:10], 1):
                    print(f"{i}. {strategy.get('name', '未命名')}")
                    print(f"   描述: {strategy.get('description', '无描述')[:50]}...")
                
                print(f"{len(pattern_strategies)+1}. 不使用特定规律（默认使用最新规律）")
                print(f"{len(pattern_strategies)+2}. 查看所有规律详情")
                
                pattern_input = input(f"\n请选择要使用的规律 (1-{len(pattern_strategies)+2}, 默认{len(pattern_strategies)+1}): ").strip()
                
                if pattern_input:
                    try:
                        choice_idx = int(pattern_input) - 1
                        if 0 <= choice_idx < len(pattern_strategies):
                            use_specific_pattern = True
                            pattern_choice = pattern_strategies[choice_idx]["name"]
                            print(f"✓ 将使用规律: {pattern_choice}")
                        elif choice_idx == len(pattern_strategies):
                            print("✓ 将使用最新规律（默认）")
                        elif choice_idx == len(pattern_strategies) + 1:
                            # 查看所有规律详情
                            print("\n【所有规律详情】")
                            for i, strategy in enumerate(pattern_strategies, 1):
                                print(f"\n{i}. {strategy.get('name', '未命名')}")
                                print(f"   描述: {strategy.get('description', '无描述')}")
                                content = strategy.get('content', '')
                                print(f"   内容摘要: {content[:100]}...")
                            
                            # 重新询问选择
                            pattern_input2 = input(f"\n请选择要使用的规律 (1-{len(pattern_strategies)}, 或按回车跳过): ").strip()
                            if pattern_input2:
                                choice_idx2 = int(pattern_input2) - 1
                                if 0 <= choice_idx2 < len(pattern_strategies):
                                    use_specific_pattern = True
                                    pattern_choice = pattern_strategies[choice_idx2]["name"]
                                    print(f"✓ 将使用规律: {pattern_choice}")
                                else:
                                    print("✓ 将使用最新规律（默认）")
                            else:
                                print("✓ 将使用最新规律（默认）")
                        else:
                            print("✓ 将使用最新规律（默认）")
                    except ValueError:
                        print("✓ 将使用最新规律（默认）")
                else:
                    print("✓ 将使用最新规律（默认）")
            else:
                print("未找到用户总结的规律")
                print("✓ 将不使用特定规律")
        except Exception as e:
            print(f"获取规律列表失败: {e}")
            print("✓ 将使用最新规律（默认）")
    
    # 获取股票名称并转换为代码
    from stock_ui_input import get_stock_name_input
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
            print(f"\n正在使用{llm_provider + ' API'}进行智能分析...")
                    
            # 创建配置好的分析器
            if llm_provider == "deepseek":
                api_key = os.environ.get("DEEPSEEK_API_KEY")
                base_url = "https://api.deepseek.com"
            elif llm_provider == "openai":
                api_key = os.environ.get("OPENAI_API_KEY")
                base_url = "https://api.openai.com/v1"
            elif llm_provider == "siliconflow":
                api_key = os.environ.get("SILICONFLOW_API_KEY")
                base_url = "https://api.siliconflow.cn/v1"
            else:
                print(f"错误: 不支持的LLM提供商: {llm_provider}")
                return
                    
            custom_analyzer = llm_module.StockLLMAnalyzer(
                llm_provider=llm_provider,
                api_key=api_key,
                base_url=base_url
            )
            # 传递选择的规律名称
            result = custom_analyzer.analyze_with_llm(
                code, 
                use_local=False, 
                update_prompt=update_prompt, 
                include_pattern_summary=True,
                specific_pattern_name=pattern_choice if use_specific_pattern else None
            )
            
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
