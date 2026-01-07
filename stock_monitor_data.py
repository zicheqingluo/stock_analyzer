# stock_monitor_data.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据获取模块
修复akshare接口返回None的问题
"""

import akshare as ak
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime, time
from stock_monitor_base import StockMonitorBase

class StockMonitorData(StockMonitorBase):
    """股票数据获取类（修复版）"""
    
    def get_stock_changes(self, change_type: str = "封涨停板") -> pd.DataFrame:
        """
        获取股票盘口异动数据（修复返回None的问题）
        """
        try:
            df = ak.stock_changes_em(symbol=change_type)
            
            # 修复：检查返回是否为None或空DataFrame
            if df is None:
                print(f"获取异动数据返回None: {change_type}")
                return pd.DataFrame()
            
            if df.empty:
                print(f"未获取到 '{change_type}' 异动数据")
                return pd.DataFrame()
            
            # 标准化代码列
            if '代码' in df.columns:
                df['代码'] = df['代码'].astype(str).str.zfill(6)
            
            print(f"获取到 '{change_type}' 异动数据 {len(df)} 条")
            return df
            
        except Exception as e:
            print(f"获取异动数据失败 ({change_type}): {e}")
            return pd.DataFrame()
    
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
    
    def get_tick_data(self, symbol: str, date: str = None) -> pd.DataFrame:
        """
        获取股票分时成交数据（用于漏单判断）
        
        Args:
            symbol: 股票代码
            date: 查询日期
            
        Returns:
            分时成交数据
        """
        if date is None:
            date = self.get_query_date()
        
        try:
            # 尝试获取分时成交数据
            df = ak.stock_zh_a_tick_tx_js(symbol=symbol, trade_date=date)
            
            if df is None or df.empty:
                print(f"未获取到 {symbol} 的分时成交数据")
                return pd.DataFrame()
            
            return df
            
        except Exception as e:
            print(f"获取分时成交数据失败 {symbol}: {e}")
            return pd.DataFrame()