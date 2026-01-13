#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【修正版】股票连板状态数据获取模块
修复交易日历获取问题
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import time
from typing import Dict, List, Optional, Any
import warnings
warnings.filterwarnings('ignore')


class StockDataFetcher:
    """股票数据获取器 (优化版)"""
    
    def __init__(self):
        """初始化，设置东八区时区"""
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
            query_date = self.get_previous_trading_date()
        else:
            # 16点后，查询当天
            query_date = self.current_time.strftime('%Y%m%d')
        
        print(f"当前时间: {self.current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"查询日期: {query_date} ({'16点后，查询当天' if current_hour >= self.data_update_hour else '16点前，查询上一交易日'})")
        return query_date
    
    def get_previous_trading_date(self, date_str: str = None) -> str:
        """
        获取前一个交易日 - 修正版
        """
        if date_str is None:
            date_str = self.current_time.strftime('%Y%m%d')
        
        try:
            # 尝试不同的交易日历接口
            try:
                # 方法1: 使用东方财富的交易日历
                trade_date_df = ak.tool_trade_date_hist_sina()
                # 检查返回的数据结构
                if 'trade_date' in trade_date_df.columns:
                    trade_dates = trade_date_df['trade_date'].tolist()
                else:
                    # 可能是不同的列名
                    trade_dates = trade_date_df.iloc[:, 0].tolist()
                    
                # 转换为字符串格式
                trade_dates = [str(date).replace('-', '')[:8] for date in trade_dates]
                
            except Exception as e:
                print(f"使用tool_trade_date_hist_sina失败: {e}")
                # 方法2: 使用备选接口
                try:
                    # 尝试其他交易日历接口
                    trade_date_df = ak.tool_trade_date_hist_em()
                    if '日期' in trade_date_df.columns:
                        trade_dates = trade_date_df['日期'].tolist()
                    else:
                        trade_dates = trade_date_df.iloc[:, 0].tolist()
                    trade_dates = [str(date).replace('-', '')[:8] for date in trade_dates]
                except:
                    # 方法3: 使用简单的日期推算（最后手段）
                    print("使用日期推算作为备选方案")
                    return self._simple_previous_date(date_str)
            
            # 排序日期
            trade_dates = sorted(set(trade_dates))
            
            # 找到小于等于当前日期的最后一个交易日
            date_num = int(date_str)
            prev_trade_date = None
            
            for trade_date in reversed(trade_dates):
                trade_date_num = int(trade_date)
                if trade_date_num <= date_num:
                    prev_trade_date = trade_date
                    break
            
            if prev_trade_date and prev_trade_date == date_str:
                # 如果当前日期就是交易日，需要再往前找一个
                idx = trade_dates.index(prev_trade_date)
                if idx > 0:
                    return trade_dates[idx - 1]
            
            return prev_trade_date if prev_trade_date else self._simple_previous_date(date_str)
            
        except Exception as e:
            print(f"获取交易日历失败: {e}")
            return self._simple_previous_date(date_str)
    
    def _simple_previous_date(self, date_str: str) -> str:
        """简单的日期推算（当交易日历接口失败时使用）"""
        try:
            current_date = datetime.strptime(date_str, '%Y%m%d')
            # 简单的逻辑：如果今天是周一，前一个交易日是上周五
            weekday = current_date.weekday()
            if weekday == 0:  # 周一
                prev_date = current_date - timedelta(days=3)
            elif weekday == 6:  # 周日
                prev_date = current_date - timedelta(days=2)
            else:
                prev_date = current_date - timedelta(days=1)
            
            return prev_date.strftime('%Y%m%d')
        except:
            # 最简备份：直接返回昨天
            current_date = datetime.strptime(date_str, '%Y%m%d')
            prev_date = current_date - timedelta(days=1)
            return prev_date.strftime('%Y%m%d')
    
    def get_next_trading_date(self, date_str: str = None) -> str:
        """
        获取下一个交易日 - 修正版
        """
        if date_str is None:
            date_str = self.current_time.strftime('%Y%m%d')
        
        try:
            # 尝试不同的交易日历接口
            try:
                trade_date_df = ak.tool_trade_date_hist_sina()
                if 'trade_date' in trade_date_df.columns:
                    trade_dates = trade_date_df['trade_date'].tolist()
                else:
                    trade_dates = trade_date_df.iloc[:, 0].tolist()
                    
                trade_dates = [str(date).replace('-', '')[:8] for date in trade_dates]
                
            except Exception as e:
                print(f"使用tool_trade_date_hist_sina失败: {e}")
                try:
                    trade_date_df = ak.tool_trade_date_hist_em()
                    if '日期' in trade_date_df.columns:
                        trade_dates = trade_date_df['日期'].tolist()
                    else:
                        trade_dates = trade_date_df.iloc[:, 0].tolist()
                    trade_dates = [str(date).replace('-', '')[:8] for date in trade_dates]
                except:
                    print("使用日期推算作为备选方案")
                    return self._simple_next_date(date_str)
            
            # 排序日期
            trade_dates = sorted(set(trade_dates))
            
            # 找到大于当前日期的第一个交易日
            date_num = int(date_str)
            
            for trade_date in trade_dates:
                trade_date_num = int(trade_date)
                if trade_date_num > date_num:
                    return trade_date
            
            # 如果没有找到，使用简单推算
            return self._simple_next_date(date_str)
            
        except Exception as e:
            print(f"获取交易日历失败: {e}")
            return self._simple_next_date(date_str)
    
    def _simple_next_date(self, date_str: str) -> str:
        """简单的下一个日期推算"""
        try:
            current_date = datetime.strptime(date_str, '%Y%m%d')
            weekday = current_date.weekday()
            
            # 简单的逻辑
            if weekday == 4:  # 周五
                next_date = current_date + timedelta(days=3)
            elif weekday == 5:  # 周六
                next_date = current_date + timedelta(days=2)
            else:
                next_date = current_date + timedelta(days=1)
            
            return next_date.strftime('%Y%m%d')
        except:
            # 最简备份：直接返回明天
            current_date = datetime.strptime(date_str, '%Y%m%d')
            next_date = current_date + timedelta(days=1)
            return next_date.strftime('%Y%m%d')
    
    def get_stock_basic_info(self, symbol: str) -> Dict[str, Any]:
        """
        获取股票基本信息
        """
        try:
            # 清理股票代码
            if '.' in symbol:
                symbol_clean = symbol.split('.')[0]
            else:
                symbol_clean = symbol
            
            # 获取股票信息 - 使用更稳定的方法
            try:
                stock_info = ak.stock_individual_info_em(symbol=symbol_clean)
            except:
                # 备选方法
                stock_info = ak.stock_individual_info_et(symbol=symbol_clean)
            
            # 转换为字典格式
            info_dict = {}
            if hasattr(stock_info, 'iterrows'):
                for _, row in stock_info.iterrows():
                    info_dict[row['item']] = row['value']
            elif isinstance(stock_info, dict):
                info_dict = stock_info
            
            return {
                '股票代码': symbol_clean,
                '股票名称': info_dict.get('股票简称', info_dict.get('name', '')),
                '所属行业': info_dict.get('行业', info_dict.get('sector', ''))
            }
            
        except Exception as e:
            print(f"获取股票基本信息失败 {symbol}: {e}")
            return {
                '股票代码': symbol,
                '股票名称': '',
                '所属行业': ''
            }
    
    def get_zt_pool_data(self, date: str) -> pd.DataFrame:
        """
        获取指定日期的涨停股池数据
        """
        try:
            # 调用涨停股池接口
            df = ak.stock_zt_pool_em(date=date)
            
            if df.empty:
                print(f"涨停股池接口返回空数据，日期: {date}")
                return pd.DataFrame()
            
            # 确保代码列为字符串并填充为6位
            if '代码' in df.columns:
                df['代码'] = df['代码'].astype(str).str.zfill(6)
            elif 'symbol' in df.columns:
                df.rename(columns={'symbol': '代码'}, inplace=True)
                df['代码'] = df['代码'].astype(str).str.zfill(6)
            
            return df
            
        except Exception as e:
            print(f"获取涨停股池数据失败，日期 {date}: {e}")
            # 尝试备选日期格式
            try:
                alt_date = f"{date[:4]}-{date[4:6]}-{date[6:]}"
                df = ak.stock_zt_pool_em(date=alt_date)
                if not df.empty:
                    return df
            except:
                pass
            
            return pd.DataFrame()
    
    def get_stock_data_from_zt_pool(self, symbol: str, date: str = None) -> Dict[str, Any]:
        """
        从涨停股池获取股票数据
        """
        if date is None:
            date = self.get_query_date()
        
        # 清理股票代码
        symbol_clean = symbol.split('.')[0] if '.' in symbol else symbol
        symbol_clean = str(symbol_clean).zfill(6)
        
        try:
            # 获取涨停股池数据
            zt_pool_df = self.get_zt_pool_data(date)
            
            if zt_pool_df.empty:
                print(f"涨停股池无数据，日期: {date}")
                return {
                    '数据来源': '涨停股池无数据',
                    '连板数': 0,
                    '连板阶段': "无连板",
                    '查询日期': date
                }
            
            # 查找目标股票
            stock_data = None
            
            # 尝试不同的列名来查找股票
            for code_col in ['代码', 'symbol', '股票代码']:
                if code_col in zt_pool_df.columns:
                    # 标准化代码列
                    zt_pool_df[code_col] = zt_pool_df[code_col].astype(str).str.zfill(6)
                    stock_data = zt_pool_df[zt_pool_df[code_col] == symbol_clean]
                    if not stock_data.empty:
                        break
            
            if stock_data is None or stock_data.empty:
                return {
                    '数据来源': '不在涨停股池',
                    '连板数': 0,
                    '连板阶段': "无连板",
                    '首次封板时间': '',
                    '炸板次数': 0,
                    '查询日期': date
                }
            
            # 获取股票数据
            stock_row = stock_data.iloc[0]
            
            # 获取连板数 - 优先从涨停股池获取
            streak_count = 1  # 默认值
            
            # 尝试不同的列名
            for col in ['连板数', '连续涨停天数', 'streak', '涨停天数']:
                if col in stock_row and pd.notna(stock_row[col]):
                    try:
                        # 尝试转换为整数
                        val = stock_row[col]
                        if isinstance(val, (int, float)):
                            streak_count = int(val)
                        elif isinstance(val, str):
                            # 提取数字
                            import re
                            match = re.search(r'(\d+)', val)
                            if match:
                                streak_count = int(match.group(1))
                            else:
                                streak_count = int(float(val))
                        else:
                            streak_count = int(float(val))
                        break
                    except Exception as e:
                        print(f"转换连板数失败 {col}: {val}, 错误: {e}")
                        continue
            
            # 确保连板数至少为1（如果在涨停股池中）
            if streak_count < 1:
                streak_count = 1
            
            # 计算连板阶段
            streak_stage = self._calculate_streak_stage(streak_count)
            
            result = {
                '数据来源': '涨停股池',
                '连板数': streak_count,
                '连板阶段': streak_stage,
                '查询日期': date
            }
            
            # 添加其他可选信息
            for col, key in [
                ('首次封板时间', '首次封板时间'),
                ('最后封板时间', '最后封板时间'),
                ('炸板次数', '炸板次数'),
                ('涨停统计', '涨停统计'),
                ('涨跌幅', '当日涨跌幅'),
                ('换手率', '当日换手率'),
                ('封板资金', '封板资金')
            ]:
                if col in stock_row and pd.notna(stock_row[col]):
                    result[key] = stock_row[col]
            
            return result
            
        except Exception as e:
            print(f"从涨停股池获取股票数据失败 {symbol_clean}: {e}")
            return {
                '数据来源': '获取失败',
                '连板数': 0,
                '连板阶段': "无连板",
                '查询日期': date
            }
    
    def _calculate_streak_stage(self, count: int) -> str:
        """根据连板数计算阶段（如'二进三'）"""
        if count <= 0:
            return "无连板"
        if count == 1:
            return "首板"
        stage_map = {2: "一进二", 3: "二进三", 4: "三进四", 5: "四进五", 6: "五进六", 7: "六进七"}
        # 确保 count 在合理范围内
        if count in stage_map:
            return stage_map[count]
        else:
            # 对于更高的连板数，使用通用格式
            return f"{count-1}进{count}"
    
    def get_complete_stock_info(self, symbol: str) -> Dict[str, Any]:
        """
        获取完整的股票信息（基本信息 + 连板状态）
        """
        print(f"\n正在获取股票 {symbol} 的信息...")
        
        # 获取基本信息
        basic_info = self.get_stock_basic_info(symbol)
        print(f"基本信息获取完成: {basic_info.get('股票名称', '未知')}")
        
        # 获取涨停数据
        zt_data = self.get_stock_data_from_zt_pool(symbol)
        print(f"涨停数据获取完成: 连板数={zt_data.get('连板数', 0)}, 阶段={zt_data.get('连板阶段', '未知')}")
        
        # 获取下一个交易日
        query_date = zt_data.get('查询日期', self.get_query_date())
        next_trading_date = self.get_next_trading_date(query_date)
        print(f"下一个交易日: {next_trading_date}")
        
        # 合并信息
        complete_info = {
            **basic_info,
            **zt_data,
            '预测日期': next_trading_date,
            '数据获取时间': self.current_time.strftime('%Y-%m-%d %H:%M:%S'),
            '当前时间是否超过16点': self.current_time.hour >= self.data_update_hour
        }
        
        print(f"信息整合完成")
        return complete_info
    
    def get_multiple_stocks_info(self, symbols: List[str]) -> pd.DataFrame:
        """
        获取多只股票的完整信息
        """
        print(f"\n开始批量获取 {len(symbols)} 只股票信息...")
        all_data = []
        query_date = self.get_query_date()
        
        # 批量获取涨停股池数据
        zt_pool_df = self.get_zt_pool_data(query_date)
        
        for i, symbol in enumerate(symbols, 1):
            try:
                print(f"处理第 {i}/{len(symbols)} 只股票: {symbol}")
                
                # 清理股票代码
                symbol_clean = symbol.split('.')[0] if '.' in symbol else symbol
                symbol_clean = str(symbol_clean).zfill(6)
                
                # 获取基本信息
                basic_info = self.get_stock_basic_info(symbol)
                
                # 从涨停股池中查找
                stock_info = {}
                if not zt_pool_df.empty:
                    # 查找股票
                    stock_data = None
                    if '代码' in zt_pool_df.columns:
                        stock_data = zt_pool_df[zt_pool_df['代码'] == symbol_clean]
                    
                    if stock_data is None or stock_data.empty:
                        stock_info = {
                            '连板数': 0,
                            '连板阶段': "无连板",
                            '数据来源': '不在涨停股池'
                        }
                    else:
                        stock_row = stock_data.iloc[0]
                        
                        # 获取连板数
                        streak_count = 1
                        for col in ['连板数', '连续涨停天数']:
                            if col in stock_row and pd.notna(stock_row[col]):
                                try:
                                    streak_count = int(stock_row[col])
                                    break
                                except:
                                    continue
                        
                        stock_info = {
                            '连板数': streak_count,
                            '连板阶段': self._calculate_streak_stage(streak_count),
                            '数据来源': '涨停股池'
                        }
                        
                        # 添加可选信息
                        for col, key in [('首次封板时间', '首次封板时间'), ('炸板次数', '炸板次数')]:
                            if col in stock_row and pd.notna(stock_row[col]):
                                stock_info[key] = stock_row[col]
                else:
                    stock_info = {
                        '连板数': 0,
                        '连板阶段': "数据获取失败",
                        '数据来源': '接口无数据'
                    }
                
                # 合并信息
                complete_info = {
                    **basic_info,
                    **stock_info,
                    '预测日期': self.get_next_trading_date(query_date),
                    '查询基准日期': query_date
                }
                
                all_data.append(complete_info)
                
                # 短暂暂停，避免请求过快
                time.sleep(0.1)
                
            except Exception as e:
                print(f"处理 {symbol} 时出错: {e}")
                continue
        
        print(f"批量处理完成，成功获取 {len(all_data)} 只股票信息")
        
        if all_data:
            return pd.DataFrame(all_data)
        else:
            return pd.DataFrame()


# 创建全局实例
fetcher = StockDataFetcher()

# 快捷函数
def get_stock_info(symbol: str) -> Dict[str, Any]:
    """获取单只股票信息的快捷函数"""
    return fetcher.get_complete_stock_info(symbol)

def get_stocks_info(symbols: List[str]) -> pd.DataFrame:
    """获取多只股票信息的快捷函数"""
    return fetcher.get_multiple_stocks_info(symbols)

def get_next_trading_date(date_str: str = None) -> str:
    """获取下一个交易日的快捷函数"""
    return fetcher.get_next_trading_date(date_str)

def get_zt_pool_data(date: str = None) -> pd.DataFrame:
    """获取涨停股池数据的快捷函数"""
    if date is None:
        date = fetcher.get_query_date()
    return fetcher.get_zt_pool_data(date)

def get_query_date() -> str:
    """获取当前查询日期的快捷函数"""
    return fetcher.get_query_date()

def test_trade_date():
    """测试交易日历功能"""
    print("测试交易日历功能...")
    print(f"当前查询日期: {get_query_date()}")
    print(f"下一个交易日: {get_next_trading_date()}")
    print(f"前一个交易日: {fetcher.get_previous_trading_date()}")


if __name__ == "__main__":
    print("股票数据获取模块测试")
    print("=" * 60)
    
    # 测试交易日历
    test_trade_date()
    
    # 测试涨停股池接口
    test_date = get_query_date()
    print(f"\n测试涨停股池，日期: {test_date}")
    
    zt_data = get_zt_pool_data(test_date)
    
    if not zt_data.empty:
        print(f"涨停股池数据形状: {zt_data.shape}")
        print(f"涨停股票数量: {len(zt_data)}")
        
        # 显示前5只股票
        if len(zt_data) > 0:
            print("\n涨停股池前5只股票:")
            display_cols = []
            for col in ['代码', '名称', '连板数', '首次封板时间']:
                if col in zt_data.columns:
                    display_cols.append(col)
            
            if display_cols:
                print(zt_data[display_cols].head().to_string(index=False))
    
    # 测试单只股票
    test_symbols = ["000001", "002624"]
    
    for symbol in test_symbols:
        print(f"\n{'='*50}")
        print(f"测试股票: {symbol}")
        info = get_stock_info(symbol)
        
        # 显示关键信息
        key_info = {
            '股票代码': info.get('股票代码', ''),
            '股票名称': info.get('股票名称', ''),
            '连板数': info.get('连板数', 0),
            '连板阶段': info.get('连板阶段', ''),
            '数据来源': info.get('数据来源', ''),
            '预测日期': info.get('预测日期', '')
        }
        
        for key, value in key_info.items():
            if value is not None:
                print(f"{key}: {value}")
