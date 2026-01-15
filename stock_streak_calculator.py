#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连板天数计算模块 - 从stock_monitor_analysis.py拆分出来
"""

import re
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional

def calculate_streak_days(symbol: str, query_date: str) -> int:
    """
    计算连板天数
    
    Args:
        symbol: 股票代码或名称
        query_date: 查询日期 (YYYYMMDD)
        
    Returns:
        连板天数，如果无法获取则返回0
    """
    try:
        # 首先尝试解析股票代码
        stock_code = None
        
        # 如果输入看起来像股票代码（6位数字）
        if re.match(r'^\d{6}$', str(symbol)):
            stock_code = str(symbol).zfill(6)
        else:
            # 尝试使用股票名称解析器
            try:
                from stock_name_resolver import get_stock_code_by_name
                stock_code = get_stock_code_by_name(str(symbol))
                if stock_code:
                    print(f"解析股票名称 '{symbol}' 得到代码: {stock_code}")
                else:
                    # 如果解析失败，尝试直接使用输入
                    stock_code = str(symbol).zfill(6)
            except ImportError:
                print("无法导入 stock_name_resolver，将直接使用输入")
                stock_code = str(symbol).zfill(6)
        
        if not stock_code:
            print(f"无法解析股票代码: {symbol}")
            return 0
        
        # 首先尝试从 stock_data_fetcher 获取准确的连板信息
        try:
            from stock_data_fetcher import get_stock_info
            stock_info = get_stock_info(stock_code)
            if stock_info:
                # 尝试从多个可能的字段中提取连板天数
                for field in ['连板数', '连续涨停天数', 'streak', '连板天数', '涨停天数', '连板高度']:
                    if field in stock_info:
                        value = stock_info[field]
                        if isinstance(value, (int, float)):
                            result = int(value)
                            # 确保结果至少为1（如果今天涨停）
                            if result >= 1:
                                print(f"从 stock_data_fetcher 获取到连板天数: {result}")
                                return result
                        elif isinstance(value, str):
                            # 提取数字
                            match = re.search(r'(\d+)', value)
                            if match:
                                result = int(match.group(1))
                                if result >= 1:
                                    print(f"从 stock_data_fetcher 字段 {field} 提取到连板天数: {result}")
                                    return result
        except ImportError:
            print("无法导入 stock_data_fetcher，将使用备用方法")
        except Exception as e:
            print(f"从 stock_data_fetcher 获取连板天数失败: {e}")
        
        # 备用方法：使用 akshare 的涨停板池历史数据，改进版
        try:
            import akshare as ak
            
            current_date = query_date
            current_dt = datetime.strptime(current_date, '%Y%m%d')
            
            streak_days = 0
            max_days_to_check = 30  # 最多检查30个交易日
            
            print(f"开始使用备用方法计算连板天数: {stock_code}")
            
            # 检查今天是否在涨停板池中
            today_in_pool = False
            try:
                df_today = ak.stock_zt_pool_em(date=current_date)
                if df_today is not None and not df_today.empty:
                    # 检查列名
                    code_col = None
                    for col in ['代码', 'symbol', '股票代码']:
                        if col in df_today.columns:
                            code_col = col
                            break
                    
                    if code_col:
                        # 标准化代码
                        df_today[code_col] = df_today[code_col].astype(str).str.zfill(6)
                        codes_today = df_today[code_col].tolist()
                        if stock_code in codes_today:
                            today_in_pool = True
                            # 尝试从今天的数据中获取连板数
                            if '连板数' in df_today.columns or '连续涨停天数' in df_today.columns:
                                for col in ['连板数', '连续涨停天数']:
                                    if col in df_today.columns:
                                        # 找到该股票的行
                                        stock_row = df_today[df_today[code_col] == stock_code]
                                        if not stock_row.empty:
                                            value = stock_row.iloc[0][col]
                                            if pd.notna(value):
                                                try:
                                                    result = int(value)
                                                    if result >= 1:
                                                        print(f"从今天涨停板池获取到连板天数: {result}")
                                                        return result
                                                except:
                                                    pass
                            streak_days = 1
                            print(f"  今天 ({current_date}) 涨停，开始向前检查连板")
            except Exception as e:
                print(f"检查今天涨停板池失败: {e}")
            
            # 如果今天涨停，向前检查历史连板
            if today_in_pool:
                for i in range(1, max_days_to_check):
                    check_date = current_dt - timedelta(days=i)
                    check_date_str = check_date.strftime('%Y%m%d')
                    
                    # 尝试获取该日期的涨停板池数据
                    try:
                        df = ak.stock_zt_pool_em(date=check_date_str)
                        
                        # 检查是否为空（可能是非交易日）
                        if df is None or df.empty:
                            # 可能是非交易日，继续检查前一天
                            continue
                        
                        # 检查股票是否在涨停板池中
                        code_col = None
                        for col in ['代码', 'symbol', '股票代码']:
                            if col in df.columns:
                                code_col = col
                                break
                        
                        if code_col:
                            df[code_col] = df[code_col].astype(str).str.zfill(6)
                            codes_in_pool = df[code_col].tolist()
                            if stock_code in codes_in_pool:
                                streak_days += 1
                                print(f"  发现 {check_date_str} 涨停，当前累计 {streak_days} 连板")
                            else:
                                # 遇到未涨停日，停止计数
                                print(f"  {check_date_str} 未涨停，停止向前检查")
                                break
                        else:
                            # 没有代码列，可能是数据格式问题
                            print(f"  {check_date_str} 数据格式异常，停止检查")
                            break
                            
                    except Exception as e:
                        # 获取数据失败，可能是非交易日或网络问题
                        continue
                
                # 确保 streak_days 至少为1（今天涨停）
                if streak_days == 0:
                    streak_days = 1
            
            # 如果今天没涨停，检查昨天是否涨停（可能今天还没收盘）
            if streak_days == 0:
                print(f"今天未涨停，检查历史连板")
                # 从昨天开始向前检查
                for i in range(max_days_to_check):
                    check_date = current_dt - timedelta(days=i)
                    check_date_str = check_date.strftime('%Y%m%d')
                    
                    try:
                        df = ak.stock_zt_pool_em(date=check_date_str)
                        
                        if df is None or df.empty:
                            continue
                        
                        code_col = None
                        for col in ['代码', 'symbol', '股票代码']:
                            if col in df.columns:
                                code_col = col
                                break
                        
                        if code_col:
                            df[code_col] = df[code_col].astype(str).str.zfill(6)
                            codes_in_pool = df[code_col].tolist()
                            if stock_code in codes_in_pool:
                                # 找到涨停日，开始向前检查连板
                                streak_days = 1
                                print(f"  发现 {check_date_str} 涨停，开始向前检查连板")
                                
                                # 继续向前检查
                                for j in range(1, max_days_to_check - i):
                                    prev_date = check_date - timedelta(days=j)
                                    prev_date_str = prev_date.strftime('%Y%m%d')
                                    
                                    try:
                                        df_prev = ak.stock_zt_pool_em(date=prev_date_str)
                                        if df_prev is None or df_prev.empty:
                                            continue
                                        
                                        code_col_prev = None
                                        for col in ['代码', 'symbol', '股票代码']:
                                            if col in df_prev.columns:
                                                code_col_prev = col
                                                break
                                        
                                        if code_col_prev:
                                            df_prev[code_col_prev] = df_prev[code_col_prev].astype(str).str.zfill(6)
                                            codes_prev = df_prev[code_col_prev].tolist()
                                            if stock_code in codes_prev:
                                                streak_days += 1
                                                print(f"  发现 {prev_date_str} 涨停，当前累计 {streak_days} 连板")
                                            else:
                                                break
                                    except:
                                        break
                                break
                    except:
                        continue
            
            if streak_days > 0:
                print(f"备用方法计算完成: {stock_code} 当前{streak_days}连板")
            else:
                print(f"备用方法未检测到连板")
            
            return streak_days
            
        except Exception as e:
            print(f"备用方法计算连板天数失败: {e}")
            import traceback
            traceback.print_exc()
            return 0
            
    except Exception as e:
        print(f"获取连板天数失败: {e}")
        return 0

def _get_streak_days_inline(self, symbol: str) -> int:
    """
    内联实现（用于stock_monitor_analysis.py中的兼容性）
    """
    # 这是一个占位符，实际实现应该调用calculate_streak_days
    # 但为了保持兼容性，我们在这里提供一个简化的实现
    try:
        # 尝试导入本模块的函数
        return calculate_streak_days(symbol, self.get_query_date())
    except:
        # 如果失败，返回0
        return 0
