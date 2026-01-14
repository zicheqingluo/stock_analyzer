#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量化模式工具模块
包含模式提取和工具函数
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime

def extract_stock_symbols_from_text(text: str) -> List[str]:
    """
    从文本中提取股票代码
    
    Args:
        text: 输入的文本
        
    Returns:
        股票代码列表
    """
    # 匹配6位数字代码
    pattern = r'\b(00[0-9]{4}|60[0-9]{4}|30[0-9]{4})\b'
    matches = re.findall(pattern, text)
    
    # 去重
    unique_matches = list(set(matches))
    
    return unique_matches

def extract_dates_from_text(text: str) -> List[str]:
    """
    从文本中提取日期
    
    Args:
        text: 输入的文本
        
    Returns:
        日期列表（格式：YYYYMMDD），只返回第一个找到的日期
    """
    # 匹配多种日期格式
    patterns = [
        r'\b(\d{4})-(\d{1,2})-(\d{1,2})\b',  # YYYY-MM-DD
        r'\b(\d{4})/(\d{1,2})/(\d{1,2})\b',  # YYYY/MM/DD
        r'\b(\d{4})(\d{2})(\d{2})\b',        # YYYYMMDD
        r'\b(\d{4})年(\d{1,2})月(\d{1,2})日\b',  # YYYY年MM月DD日
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if len(match) == 3:
                year, month, day = match
                # 标准化月份和日期为两位数
                month = month.zfill(2)
                day = day.zfill(2)
                # 格式化为YYYYMMDD
                date_str = f"{year}{month}{day}"
                # 只返回第一个找到的日期
                return [date_str]
    
    # 如果没有找到日期，返回空列表
    return []

def _make_json_serializable(obj):
    """将对象转换为JSON可序列化的格式"""
    import datetime
    import pandas as pd
    import numpy as np
    
    # 处理基本类型
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    # 处理日期时间类型
    elif isinstance(obj, (datetime.datetime, datetime.date)):
        try:
            return obj.strftime("%Y-%m-%d")
        except:
            return str(obj)
    # 处理列表和元组
    elif isinstance(obj, (list, tuple)):
        return [_make_json_serializable(item) for item in obj]
    # 处理字典
    elif isinstance(obj, dict):
        return {key: _make_json_serializable(value) for key, value in obj.items()}
    # 处理pandas类型
    elif isinstance(obj, (pd.Timestamp, pd.Timedelta)):
        return str(obj)
    elif isinstance(obj, pd.Series):
        return _make_json_serializable(obj.tolist())
    elif isinstance(obj, pd.DataFrame):
        return _make_json_serializable(obj.to_dict(orient='records'))
    # 处理numpy类型
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return _make_json_serializable(obj.tolist())
    # 处理其他类型
    else:
        # 尝试转换为字符串
        try:
            return str(obj)
        except:
            # 如果无法转换，返回None
            return None
