#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量化策略核心模块
包含核心策略管理功能
"""

import os
import json
import datetime
from typing import Dict, List, Any, Optional

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
    strategies = load_strategies()
    
    # 也添加规律总结
    import os
    import json
    from datetime import datetime
    
    summary_dir = "pattern_summaries"
    if os.path.exists(summary_dir):
        pattern_summary_count = 0
        for filename in os.listdir(summary_dir):
            if filename.endswith('.json') and filename.startswith('summary_'):
                filepath = os.path.join(summary_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        summary_data = json.load(f)
                    
                    # 检查是否是pattern_summary_few_shot类型
                    strategy_type = summary_data.get("type", "pattern_summary")
                    
                    strategies.append({
                        "name": summary_data.get("name", "规律总结"),
                        "description": summary_data.get("description", "交易规律总结"),
                        "created_at": summary_data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                        "content": summary_data.get("summary", ""),
                        "type": strategy_type,
                        "file_path": filepath,
                        "id": summary_data.get("id", "")
                    })
                    
                    if strategy_type == "pattern_summary_few_shot":
                        pattern_summary_count += 1
                        
                except json.JSONDecodeError as e:
                    print(f"加载规律总结文件 {filename} 失败（JSON格式错误）: {e}")
                    # 尝试修复或删除损坏的文件
                    try:
                        # 读取文件内容
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        # 尝试找到并修复常见的JSON问题
                        # 这里可以添加更复杂的修复逻辑
                        print(f"文件 {filename} 可能已损坏，建议删除或修复")
                    except:
                        pass
                    continue
                except Exception as e:
                    print(f"加载规律总结文件 {filename} 失败: {e}")
                    continue
        
        # 如果没有找到pattern_summary_few_shot类型的规律，确保返回空列表
        # 这个信息会在调用函数中处理
    else:
        # 如果目录不存在，创建它
        os.makedirs(summary_dir, exist_ok=True)
    
    return strategies

def delete_strategy(strategy_name: str) -> bool:
    """删除策略或规律总结"""
    # 首先检查是否是规律总结
    summary_dir = "pattern_summaries"
    if os.path.exists(summary_dir):
        for filename in os.listdir(summary_dir):
            if filename.endswith('.json') and filename.startswith('summary_'):
                filepath = os.path.join(summary_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        summary_data = json.load(f)
                    if summary_data.get("name") == strategy_name or summary_data.get("id") == strategy_name:
                        os.remove(filepath)
                        print(f"已删除规律总结: {strategy_name}")
                        
                        # 同时删除对应的txt文件
                        txt_file = os.path.join(summary_dir, "latest_pattern_summary.txt")
                        if os.path.exists(txt_file):
                            # 检查是否是当前删除的规律
                            try:
                                with open(txt_file, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                # 简单检查：如果内容匹配，删除txt文件
                                if summary_data.get("summary", "") in content:
                                    os.remove(txt_file)
                                    print(f"已删除对应的txt文件")
                            except:
                                pass
                        return True
                except:
                    continue
    
    # 如果不是规律总结，尝试从策略文件中删除
    strategies = load_strategies()
    new_strategies = [s for s in strategies if s.get("name") != strategy_name]
    
    if len(new_strategies) < len(strategies):
        save_strategies(new_strategies)
        print(f"已删除策略: {strategy_name}")
        return True
    
    print(f"未找到策略或规律总结: {strategy_name}")
    return False

def rename_strategy(old_name: str, new_name: str) -> bool:
    """重命名策略或规律总结"""
    # 首先检查是否是规律总结
    summary_dir = "pattern_summaries"
    if os.path.exists(summary_dir):
        for filename in os.listdir(summary_dir):
            if filename.endswith('.json') and filename.startswith('summary_'):
                filepath = os.path.join(summary_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        summary_data = json.load(f)
                    
                    if summary_data.get("name") == old_name or summary_data.get("id") == old_name:
                        summary_data["name"] = new_name
                        # 更新文件名
                        new_filename = f"summary_{new_name}.json"
                        new_filepath = os.path.join(summary_dir, new_filename)
                        
                        with open(new_filepath, 'w', encoding='utf-8') as f:
                            json.dump(summary_data, f, ensure_ascii=False, indent=2)
                        
                        # 删除旧文件
                        os.remove(filepath)
                        print(f"已重命名规律总结: {old_name} -> {new_name}")
                        return True
                except:
                    continue
    
    # 如果不是规律总结，尝试从策略文件中重命名
    strategies = load_strategies()
    for strategy in strategies:
        if strategy.get("name") == old_name:
            strategy["name"] = new_name
            save_strategies(strategies)
            print(f"已重命名策略: {old_name} -> {new_name}")
            return True
    
    print(f"未找到策略或规律总结: {old_name}")
    return False

def get_strategy_details(strategy_name: str) -> Optional[Dict[str, Any]]:
    """获取策略或规律总结的详细信息"""
    # 首先检查是否是规律总结
    summary_dir = "pattern_summaries"
    if os.path.exists(summary_dir):
        for filename in os.listdir(summary_dir):
            if filename.endswith('.json') and filename.startswith('summary_'):
                filepath = os.path.join(summary_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        summary_data = json.load(f)
                    if summary_data.get("name") == strategy_name or summary_data.get("id") == strategy_name:
                        return summary_data
                except:
                    continue
    
    # 如果不是规律总结，尝试从策略文件中查找
    strategies = load_strategies()
    for strategy in strategies:
        if strategy.get("name") == strategy_name:
            return strategy
    
    return None
