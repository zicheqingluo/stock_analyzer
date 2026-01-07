# stock_monitor_base.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票异动监控基础模块
包含基础功能、日期处理等
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import time
from typing import Dict, List, Optional, Any, Union
import warnings
warnings.filterwarnings('ignore')

class StockMonitorBase:
    """股票异动监控基础类"""
    
    def __init__(self):
        """初始化"""
        self.tz_shanghai = pytz.timezone('Asia/Shanghai')
        self.current_time = datetime.now(self.tz_shanghai)
        self.data_update_hour = 16  # 数据更新时间点
        
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
    
    def get_previous_trading_date(self, date_str: str = None) -> str:
        """获取前一个交易日"""
        if date_str is None:
            date_str = self.current_time.strftime('%Y%m%d')
        
        try:
            current_date = datetime.strptime(date_str, '%Y%m%d')
            weekday = current_date.weekday()
            
            if weekday == 0:  # 周一
                prev_date = current_date - timedelta(days=3)
            elif weekday == 6:  # 周日
                prev_date = current_date - timedelta(days=2)
            else:
                prev_date = current_date - timedelta(days=1)
            
            return prev_date.strftime('%Y%m%d')
        except Exception as e:
            print(f"获取前一个交易日失败: {e}")
            current_date = datetime.strptime(date_str, '%Y%m%d')
            prev_date = current_date - timedelta(days=1)
            return prev_date.strftime('%Y%m%d')