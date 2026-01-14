#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据收集器 - 专门负责收集股票数据
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import akshare as ak
import warnings
warnings.filterwarnings('ignore')

class StockDataCollector:
    """股票数据收集器"""
    
    def __init__(self):
        """初始化"""
        pass
    
    def collect_stock_data(self, symbol: str, days_back: int = 5, target_date: str = None) -> Dict[str, Any]:
        """
        收集股票的详细数据
        
        Args:
            symbol: 股票代码
            days_back: 回溯天数
            target_date: 目标分析日期（格式：YYYYMMDD），如果为None则使用当前日期
            
        Returns:
            股票数据字典
        """
        try:
            # 清理股票代码
            symbol_clean = str(symbol).zfill(6)
            
            # 1. 获取股票基本信息
            stock_name = self._get_stock_name(symbol_clean)
            
            # 2. 获取历史日线数据（支持指定日期）
            history_data = self._get_detailed_history(symbol_clean, days_back, target_date)
            
            # 3. 获取涨停板池数据（支持指定日期）
            limit_up_data = self._get_limit_up_data(symbol_clean, target_date)
            
            # 4. 计算关键指标
            key_metrics = self._calculate_key_metrics(history_data, limit_up_data)
            
            # 5. 生成历史数据摘要
            history_summary = self._generate_history_summary(history_data)
            
            # 确定分析日期
            if target_date:
                # 将YYYYMMDD转换为YYYY-MM-DD
                try:
                    analysis_date = f"{target_date[:4]}-{target_date[4:6]}-{target_date[6:]}"
                except:
                    analysis_date = datetime.now().strftime('%Y-%m-%d')
            else:
                analysis_date = datetime.now().strftime('%Y-%m-%d')
            
            return {
                "symbol": symbol_clean,
                "name": stock_name,
                "analysis_date": analysis_date,
                "target_date": target_date,
                "history_data": history_data,
                "limit_up_data": limit_up_data,
                "key_metrics": key_metrics,
                "history_summary": history_summary
            }
            
        except Exception as e:
            print(f"收集股票数据失败: {e}")
            return {"error": f"数据收集失败: {str(e)}"}
    
    def _get_stock_name(self, symbol: str) -> str:
        """获取股票名称"""
        try:
            stock_info = ak.stock_individual_info_em(symbol=symbol)
            if not stock_info.empty:
                for _, row in stock_info.iterrows():
                    if row['item'] == '股票简称':
                        return row['value']
            return symbol
        except:
            return symbol
    
    def _get_detailed_history(self, symbol: str, days_back: int, target_date: str = None) -> List[Dict[str, Any]]:
        """
        获取详细的日线历史数据
        
        Args:
            symbol: 股票代码
            days_back: 回溯天数
            target_date: 目标日期（格式：YYYYMMDD），如果为None则使用当前日期
        """
        try:
            # 确定查询日期
            if target_date:
                # 将字符串转换为datetime对象
                try:
                    query_date = datetime.strptime(target_date, '%Y%m%d')
                except:
                    query_date = datetime.now()
            else:
                query_date = datetime.now()
            
            # 计算开始日期（获取足够多的数据，然后筛选）
            start_date = query_date - timedelta(days=days_back * 3)
            
            # 获取日线数据
            df = ak.stock_zh_a_hist(
                symbol=symbol, 
                period="daily", 
                start_date=start_date.strftime('%Y%m%d'), 
                end_date=query_date.strftime('%Y%m%d'),
                adjust="qfq"
            )
            
            if df.empty:
                print(f"警告: 无法获取股票 {symbol} 的日线数据")
                return []
            
            # 重命名列
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount',
                '振幅': 'amplitude',
                '涨跌幅': 'pct_change',
                '涨跌额': 'change',
                '换手率': 'turnover'
            })
            
            # 按日期排序（最近的在前）
            df = df.sort_values('date', ascending=False)
            
            # 按日期排序（最近的在前）
            df = df.sort_values('date', ascending=False)
            
            # 只保留最近days_back天的数据（相对于目标日期）
            df = df.head(days_back)
            
            # 转换为字典列表
            history_list = []
            for _, row in df.iterrows():
                # 判断是否涨停
                pct_change = row.get('pct_change', 0)
                is_limit_up = False
                if isinstance(pct_change, (int, float)):
                    is_limit_up = abs(pct_change - 10.0) < 0.5 or pct_change >= 9.8
                
                # 判断涨停类型
                limit_type = "非涨停"
                if is_limit_up:
                    open_price = row.get('open', 0)
                    close_price = row.get('close', 0)
                    high_price = row.get('high', 0)
                    low_price = row.get('low', 0)
                    
                    # 计算前一日收盘价（近似）
                    prev_close = close_price / (1 + pct_change/100) if pct_change != 0 else close_price
                    
                    # 计算涨停价
                    limit_price = prev_close * 1.1
                    
                    # 判断是否一字板
                    if abs(open_price - limit_price) < 0.01 and abs(high_price - limit_price) < 0.01:
                        limit_type = "一字板"
                    # 判断是否T字板
                    elif abs(high_price - limit_price) < 0.01 and low_price < open_price:
                        limit_type = "T字板"
                    else:
                        limit_type = "普通涨停"
                
                history_list.append({
                    'date': row['date'],
                    'open': float(row['open']),
                    'close': float(row['close']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'volume': float(row['volume']),
                    'amount': float(row['amount']),
                    'pct_change': float(pct_change),
                    'turnover': float(row['turnover']) if 'turnover' in row and pd.notna(row['turnover']) else 0.0,
                    'is_limit_up': is_limit_up,
                    'limit_type': limit_type
                })
            
            return history_list
            
        except Exception as e:
            print(f"获取详细历史数据失败: {e}")
            return []
    
    def _get_limit_up_data(self, symbol: str, target_date: str = None) -> Dict[str, Any]:
        """
        获取涨停板池相关数据
        
        Args:
            symbol: 股票代码
            target_date: 目标日期（格式：YYYYMMDD），如果为None则使用当前日期
        """
        try:
            if target_date:
                current_date = target_date
            else:
                current_date = datetime.now().strftime('%Y%m%d')
            
            # 获取指定日期的涨停板池数据
            df_today = ak.stock_zt_pool_em(date=current_date)
            
            result = {
                'in_today_pool': False,
                'streak_days': 0,
                'first_limit_time': None,
                'blow_up_count': 0
            }
            
            if df_today is not None and not df_today.empty:
                # 查找代码列
                code_col = None
                for col in ['代码', 'symbol', '股票代码']:
                    if col in df_today.columns:
                        code_col = col
                        break
                
                if code_col:
                    df_today[code_col] = df_today[code_col].astype(str).str.zfill(6)
                    if symbol in df_today[code_col].values:
                        result['in_today_pool'] = True
                        
                        # 获取该股票的数据
                        stock_row = df_today[df_today[code_col] == symbol].iloc[0]
                        
                        # 获取连板数
                        for col in ['连板数', '连续涨停天数']:
                            if col in stock_row and pd.notna(stock_row[col]):
                                try:
                                    result['streak_days'] = int(stock_row[col])
                                    break
                                except:
                                    continue
                        
                        # 获取首次封板时间
                        if '首次封板时间' in stock_row:
                            result['first_limit_time'] = str(stock_row['首次封板时间'])
                        
                        # 获取炸板次数
                        if '炸板次数' in stock_row:
                            try:
                                result['blow_up_count'] = int(stock_row['炸板次数'])
                            except:
                                pass
            
            return result
            
        except Exception as e:
            print(f"获取涨停板池数据失败: {e}")
            return {'in_today_pool': False, 'streak_days': 0}
    
    def _calculate_key_metrics(self, history_data: List[Dict], limit_up_data: Dict) -> Dict[str, Any]:
        """
        计算关键指标
        """
        if not history_data:
            return {}
        
        # 提取最近3天的数据
        recent_days = min(3, len(history_data))
        recent_data = history_data[:recent_days]
        
        # 计算换手率趋势
        turnover_rates = []
        for day in recent_data:
            if 'turnover' in day:
                turnover = day['turnover']
                if isinstance(turnover, (int, float)):
                    turnover_rates.append(turnover)
        
        # 计算涨停天数
        limit_up_days = 0
        for day in recent_data:
            if day.get('is_limit_up', False):
                limit_up_days += 1
        
        # 计算量价关系
        volume_trend = "unknown"
        if len(turnover_rates) >= 2:
            if turnover_rates[0] < turnover_rates[1]:
                volume_trend = "缩量"
            elif turnover_rates[0] > turnover_rates[1]:
                volume_trend = "放量"
            else:
                volume_trend = "平量"
        
        # 获取最近涨停类型
        recent_limit_type = "非涨停"
        if limit_up_data.get('in_today_pool', False):
            if history_data and history_data[0].get('is_limit_up', False):
                recent_limit_type = history_data[0].get('limit_type', '普通涨停')
            else:
                recent_limit_type = "普通涨停"
        
        # 确保数据一致性
        streak_days = limit_up_data.get('streak_days', 0)
        today_in_pool = limit_up_data.get('in_today_pool', False)
        
        return {
            "连续涨停天数": streak_days,
            "今日是否涨停": today_in_pool,
            "最近3天涨停天数": limit_up_days,
            "最近涨停类型": recent_limit_type,
            "换手率趋势": volume_trend,
            "最近换手率": turnover_rates[0] if turnover_rates else 0,
            "炸板次数": limit_up_data.get('blow_up_count', 0),
            "首次涨停时间": limit_up_data.get('first_limit_time', '未知')
        }
    
    def _generate_history_summary(self, history_data: List[Dict]) -> str:
        """
        生成历史数据摘要文本
        """
        if not history_data:
            return "无历史数据"
        
        summary_lines = []
        for i, day in enumerate(history_data[:5]):
            date_str = day['date']
            pct_change = day['pct_change']
            turnover = day.get('turnover', 0)
            limit_type = day.get('limit_type', '非涨停')
            is_limit_up = day.get('is_limit_up', False)
            
            line = f"{date_str}: "
            if is_limit_up:
                line += f"涨停({limit_type})，涨幅{pct_change:.2f}%，换手率{turnover:.2f}%"
            else:
                line += f"涨幅{pct_change:.2f}%，换手率{turnover:.2f}%"
            
            summary_lines.append(line)
        
        return "\n".join(summary_lines)
