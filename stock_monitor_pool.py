# stock_monitor_pool.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票池数据查询模块
修复时间类型错误
"""

import akshare as ak
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pytz

class StockMonitorPool:
    """股票池数据查询类（修复版）"""
    
    def __init__(self):
        """初始化"""
        self.tz_shanghai = pytz.timezone('Asia/Shanghai')
        self.current_time = datetime.now(self.tz_shanghai)
        self.data_update_hour = 16
        
    def get_query_date(self) -> str:
        """
        根据当前时间确定查询日期
        规则: 16点前查前一个交易日，16点后查当天
        """
        current_hour = self.current_time.hour
        
        if current_hour < self.data_update_hour:
            # 16点前，查询前一个交易日
            query_date = (self.current_time - timedelta(days=1)).strftime('%Y%m%d')
        else:
            # 16点后，查询当天
            query_date = self.current_time.strftime('%Y%m%d')
        
        print(f"监控模块查询日期: {query_date}")
        return query_date
    
    def get_炸板_stocks(self, date: str = None) -> pd.DataFrame:
        """
        获取炸板股池数据（修复返回None的问题）
        """
        if date is None:
            date = self.get_query_date()
        
        try:
            df = ak.stock_zt_pool_zbgc_em(date=date)
            
            if df is None:
                print(f"获取炸板股池数据返回None，日期: {date}")
                return pd.DataFrame()
            
            if df.empty:
                print(f"未获取到炸板股池数据，日期: {date}")
                return pd.DataFrame()
            
            if '代码' in df.columns:
                df['代码'] = df['代码'].astype(str).str.zfill(6)
            
            print(f"获取到炸板股池数据 {len(df)} 条，日期: {date}")
            return df
            
        except Exception as e:
            print(f"获取炸板股池数据失败，日期 {date}: {e}")
            return pd.DataFrame()
    
    def check_if_炸板(self, symbol: str, date: str = None) -> Dict[str, Any]:
        """
        检查个股是否有炸板（修复时间类型）
        """
        symbol_clean = str(symbol).zfill(6)
        
        if date is None:
            date = self.get_query_date()
        
        print(f"\n开始检查 {symbol_clean} 是否炸板...")
        
        # 获取炸板股池数据
        炸板_df = self.get_炸板_stocks(date)
        
        result = {
            '股票代码': symbol_clean,
            '查询日期': date,
            '是否在炸板股池': False,
            '炸板次数': 0,
            '首次封板时间': None,
            '涨停价': None,
            '最新价': None,
            '涨跌幅': None,
            '换手率': None,
            '炸板详情': None
        }
        
        if not 炸板_df.empty and '代码' in 炸板_df.columns:
            stock_data = 炸板_df[炸板_df['代码'] == symbol_clean]
            
            if not stock_data.empty:
                stock_row = stock_data.iloc[0]
                
                # 修复：格式化时间字段
                first_limit_time_raw = stock_row.get('首次封板时间', None)
                first_limit_time = self._format_time(first_limit_time_raw)
                
                result.update({
                    '是否在炸板股池': True,
                    '炸板次数': int(stock_row.get('炸板次数', 0)) if pd.notna(stock_row.get('炸板次数')) else 0,
                    '首次封板时间': first_limit_time,
                    '涨停价': stock_row.get('涨停价', None),
                    '最新价': stock_row.get('最新价', None),
                    '涨跌幅': stock_row.get('涨跌幅', None),
                    '换手率': stock_row.get('换手率', None),
                    '振幅': stock_row.get('振幅', None)
                })
                
                # 生成炸板详情
                detail = f"炸板{result['炸板次数']}次"
                if result['首次封板时间']:
                    detail += f"，首次封板{result['首次封板时间']}"
                if result['涨跌幅']:
                    detail += f"，涨跌幅{result['涨跌幅']}%"
                
                result['炸板详情'] = detail
                
                print(f"检查完成: 在炸板股池中，{detail}")
            else:
                print(f"检查完成: 不在炸板股池中")
        else:
            print(f"检查完成: 炸板股池无数据")
        
        return result
    
    def _format_time(self, time_value) -> str:
        """
        格式化时间，确保返回字符串
        """
        if time_value is None:
            return ""
        
        try:
            if isinstance(time_value, str):
                return time_value
            
            from datetime import time as datetime_time
            
            if isinstance(time_value, datetime_time):
                return time_value.strftime('%H:%M:%S')
            
            if isinstance(time_value, datetime):
                return time_value.strftime('%H:%M:%S')
            
            return str(time_value)
        except Exception as e:
            print(f"格式化时间失败: {time_value}, 错误: {e}")
            return str(time_value)
    
    def get_strong_stocks(self, date: str = None) -> pd.DataFrame:
        """
        获取强势股池数据（修复返回None的问题）
        """
        if date is None:
            date = self.get_query_date()
        
        try:
            df = ak.stock_zt_pool_strong_em(date=date)
            
            if df is None:
                print(f"获取强势股池数据返回None，日期: {date}")
                return pd.DataFrame()
            
            if df.empty:
                print(f"未获取到强势股池数据，日期: {date}")
                return pd.DataFrame()
            
            if '代码' in df.columns:
                df['代码'] = df['代码'].astype(str).str.zfill(6)
            
            print(f"获取到强势股池数据 {len(df)} 条，日期: {date}")
            return df
            
        except Exception as e:
            print(f"获取强势股池数据失败，日期 {date}: {e}")
            return pd.DataFrame()
    
    def check_if_strong_stock(self, symbol: str, date: str = None) -> Dict[str, Any]:
        """
        检查个股是否为强势股
        """
        symbol_clean = str(symbol).zfill(6)
        
        if date is None:
            date = self.get_query_date()
        
        print(f"\n开始检查 {symbol_clean} 是否为强势股...")
        
        # 获取强势股池数据
        strong_df = self.get_strong_stocks(date)
        
        result = {
            '股票代码': symbol_clean,
            '查询日期': date,
            '是否在强势股池': False,
            '入选理由': None,
            '是否新高': None,
            '涨停统计': None,
            '涨跌幅': None,
            '换手率': None,
            '量比': None
        }
        
        if not strong_df.empty and '代码' in strong_df.columns:
            stock_data = strong_df[strong_df['代码'] == symbol_clean]
            
            if not stock_data.empty:
                stock_row = stock_data.iloc[0]
                
                result.update({
                    '是否在强势股池': True,
                    '入选理由': stock_row.get('入选理由', '未知'),
                    '是否新高': stock_row.get('是否新高', '未知'),
                    '涨停统计': stock_row.get('涨停统计', '未知'),
                    '涨跌幅': stock_row.get('涨跌幅', None),
                    '换手率': stock_row.get('换手率', None),
                    '量比': stock_row.get('量比', None),
                    '涨速': stock_row.get('涨速', None)
                })
                
                print(f"检查完成: 在强势股池中，入选理由: {result['入选理由']}")
            else:
                print(f"检查完成: 不在强势股池中")
        else:
            print(f"检查完成: 强势股池无数据")
        
        return result
    
    def get_board_changes(self) -> pd.DataFrame:
        """
        获取板块异动数据（修复返回None的问题）
        """
        try:
            df = ak.stock_board_change_em()
            
            if df is None:
                print("获取板块异动数据返回None")
                return pd.DataFrame()
            
            if df.empty:
                print("未获取到板块异动数据")
                return pd.DataFrame()
            
            print(f"获取到板块异动数据 {len(df)} 条")
            return df
            
        except Exception as e:
            print(f"获取板块异动数据失败: {e}")
            return pd.DataFrame()