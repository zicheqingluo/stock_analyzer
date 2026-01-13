# stock_monitor_analysis.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票综合分析模块
包含综合分析和批量分析
"""

import pandas as pd
import os
from typing import Dict, List, Any
from datetime import datetime, timedelta
import pytz

class StockMonitorAnalysis:
    """股票综合分析类"""
    
    def __init__(self):
        """初始化"""
        self.tz_shanghai = pytz.timezone('Asia/Shanghai')
        self.current_time = datetime.now(self.tz_shanghai)
        self.data_update_hour = 16
        
        # 导入其他模块的类，添加错误处理
        try:
            from stock_monitor_changes import StockMonitorChanges
            from stock_monitor_pool import StockMonitorPool
            
            self.changes_module = StockMonitorChanges()
            self.pool_module = StockMonitorPool()
        except ImportError as e:
            print(f"导入监控模块失败: {e}")
            print("尝试从当前目录导入...")
            # 尝试相对导入
            try:
                from .stock_monitor_changes import StockMonitorChanges
                from .stock_monitor_pool import StockMonitorPool
                self.changes_module = StockMonitorChanges()
                self.pool_module = StockMonitorPool()
            except ImportError:
                print("无法导入必要的监控模块，某些功能可能不可用")
                # 创建空对象以避免后续错误
                class DummyModule:
                    def __getattr__(self, name):
                        def dummy_method(*args, **kwargs):
                            print(f"警告: {name} 方法不可用，因为模块导入失败")
                            return {}
                        return dummy_method
                self.changes_module = DummyModule()
                self.pool_module = DummyModule()
    
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
    
    def comprehensive_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        综合分析个股的别名方法，用于兼容现有代码
        调用 comprehensive_stock_analysis 方法
        """
        return self.comprehensive_stock_analysis(symbol)
    
    def comprehensive_stock_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        综合分析个股：涨停判断 + 异动情况 + 是否炸板 + 是否强势股
        """
        try:
            # 首先尝试解析股票代码
            import re
            if re.match(r'^\d{6}$', str(symbol)):
                symbol_clean = str(symbol).zfill(6)
            else:
                # 尝试使用股票名称解析器
                try:
                    from stock_name_resolver import get_stock_code_by_name
                    resolved_code = get_stock_code_by_name(str(symbol))
                    if resolved_code:
                        symbol_clean = resolved_code
                        print(f"解析股票名称 '{symbol}' 得到代码: {symbol_clean}")
                    else:
                        symbol_clean = str(symbol).zfill(6)
                except ImportError:
                    print("无法导入 stock_name_resolver，将直接使用输入")
                    symbol_clean = str(symbol).zfill(6)
            
            print(f"\n{'='*60}")
            print(f"开始对 {symbol} (代码: {symbol_clean}) 进行综合分析...")
            print(f"{'='*60}")
            
            # 1. 分析异动情况（涨停判断、炸板、漏单）
            print(f"1. 分析异动情况...")
            change_analysis = self.changes_module.analyze_limit_up_changes(symbol_clean)
            
            # 2. 检查是否炸板
            print(f"2. 检查是否炸板...")
            炸板_check = self.pool_module.check_if_炸板(symbol_clean)
            
            # 3. 检查是否强势股
            print(f"3. 检查是否强势股...")
            strong_check = self.pool_module.check_if_strong_stock(symbol_clean)
            
            # 4. 综合评估
            is_limit_up = change_analysis.get('是否涨停', False) if isinstance(change_analysis, dict) else False
            has_open_limit = change_analysis.get('是否有炸板', False) if isinstance(change_analysis, dict) else False
            has_big_sell = change_analysis.get('是否大笔卖出', False) if isinstance(change_analysis, dict) else False
            has_re_limit = change_analysis.get('是否重新封板', False) if isinstance(change_analysis, dict) else False
            is_in_limit_pool = change_analysis.get('是否在涨停板池中', False) if isinstance(change_analysis, dict) else False
            is_in_炸板_pool = 炸板_check.get('是否在炸板股池', False) if isinstance(炸板_check, dict) else False
            is_in_strong_pool = strong_check.get('是否在强势股池', False) if isinstance(strong_check, dict) else False
            
            # 最终是否涨停：如果在涨停板池中，或者有涨停且没有炸板，或者有炸板但重新封板
            final_is_limit_up = is_in_limit_pool or (is_limit_up and not has_open_limit) or (has_open_limit and has_re_limit)
            
            # 获取连板天数
            streak_days = self._get_streak_days(symbol_clean)
            
            # 获取首次涨停时间（尝试从stock_data_fetcher获取）
            first_limit_up_time = None
            try:
                from stock_data_fetcher import get_stock_info
                stock_info = get_stock_info(symbol_clean)
                if stock_info:
                    # 尝试从多个字段获取首次涨停时间
                    for field in ['首次涨停时间', 'first_limit_up_time', '首板时间']:
                        if field in stock_info:
                            value = stock_info[field]
                            if value:
                                first_limit_up_time = str(value)
                                break
            except:
                pass
            
            # 如果无法获取，尝试计算（使用最近一次涨停的日期）
            if not first_limit_up_time and streak_days > 0:
                try:
                    import akshare as ak
                    from datetime import datetime, timedelta
                    current_date = self.get_query_date()
                    current_dt = datetime.strptime(current_date, '%Y%m%d')
                    
                    # 向前查找涨停日
                    for i in range(streak_days + 5):  # 多查几天以防非交易日
                        check_date = current_dt - timedelta(days=i)
                        check_date_str = check_date.strftime('%Y%m%d')
                        try:
                            df = ak.stock_zt_pool_em(date=check_date_str)
                            if df is not None and not df.empty and '代码' in df.columns:
                                codes = df['代码'].astype(str).str.zfill(6).tolist()
                                if symbol_clean in codes:
                                    # 找到涨停日，这是最近的一次
                                    # 首次涨停应该是这个日期减去(streak_days-1)天
                                    # 但为了简单，我们只记录最近涨停日
                                    first_limit_up_time = check_date_str
                                    break
                        except:
                            continue
                except:
                    pass
            
            # 生成综合评级
            rating_info = self._generate_rating(
                is_limit_up, has_open_limit, has_big_sell, 
                is_in_炸板_pool, is_in_strong_pool, has_re_limit
            )
            
            # 生成投资建议
            advice = self._generate_investment_advice(
                is_limit_up, has_open_limit, has_big_sell, 
                is_in_炸板_pool, is_in_strong_pool, has_re_limit
            )
            
            # 合并结果
            comprehensive_result = {
                '股票代码': symbol_clean,
                '分析时间': self.current_time.strftime('%Y-%m-%d %H:%M:%S'),
                '查询日期': self.get_query_date(),
                '综合评级': rating_info['rating'],
                '评级说明': rating_info['description'],
                '投资建议': advice,
                '涨停异动分析': change_analysis,
                '炸板检测': 炸板_check,
                '强势股判断': strong_check,
                '关键指标': {
                    '是否涨停': is_limit_up,
                    '是否有炸板': has_open_limit or is_in_炸板_pool,
                    '是否漏单': has_big_sell,
                    '是否重新封板': has_re_limit,
                    '是否强势股': is_in_strong_pool,
                    '炸板次数': max(
                        change_analysis.get('炸板次数', 0) if isinstance(change_analysis, dict) else 0,
                        炸板_check.get('炸板次数', 0) if isinstance(炸板_check, dict) else 0
                    ),
                    '最终是否涨停': final_is_limit_up,
                    '几连板': streak_days,
                    '首次涨停时间': first_limit_up_time if first_limit_up_time else '未知'
                }
            }
            
            print(f"\n综合分析完成!")
            print(f"综合评级: {comprehensive_result['综合评级']}")
            print(f"投资建议: {comprehensive_result['投资建议']}")
            
            return comprehensive_result
        except Exception as e:
            print(f"综合分析过程中发生错误: {e}")
            # 返回一个基本的错误结果
            return {
                '股票代码': str(symbol).zfill(6),
                '分析时间': self.current_time.strftime('%Y-%m-%d %H:%M:%S'),
                '查询日期': self.get_query_date(),
                '综合评级': 'E',
                '评级说明': f'分析过程中发生错误: {str(e)}',
                '投资建议': '分析失败，请检查输入或网络连接',
                '涨停异动分析': {},
                '炸板检测': {},
                '强势股判断': {},
                '关键指标': {
                    '是否涨停': False,
                    '是否有炸板': False,
                    '是否漏单': False,
                    '是否重新封板': False,
                    '是否强势股': False,
                    '炸板次数': 0
                }
            }
    
    def _generate_rating(self, is_limit_up: bool, has_open_limit: bool, 
                        has_big_sell: bool, is_in_炸板_pool: bool, 
                        is_in_strong_pool: bool, has_re_limit: bool = False) -> Dict[str, str]:
        """生成综合评级"""
        # 如果有炸板但没有重新封板，评级较低
        if has_open_limit and not has_re_limit:
            return {
                'rating': "D-",
                'description': "炸板后未重新封板，走势疲弱"
            }
        
        # 其他评级逻辑保持不变，但需要考虑重新封板的情况
        if is_limit_up and not has_open_limit and not is_in_炸板_pool and not has_big_sell and is_in_strong_pool:
            return {
                'rating': "A+",
                'description': "强势涨停，封板稳固，无漏单，属于强势股"
            }
        elif is_limit_up and not has_open_limit and not is_in_炸板_pool and not has_big_sell:
            return {
                'rating': "A",
                'description': "强势涨停，封板稳固，无漏单"
            }
        elif is_limit_up and has_re_limit and not has_big_sell and is_in_strong_pool:
            return {
                'rating': "A-",
                'description': "炸板后重新封板，无漏单，属于强势股"
            }
        elif is_limit_up and has_re_limit and not has_big_sell:
            return {
                'rating': "B+",
                'description': "炸板后重新封板，无漏单"
            }
        elif is_limit_up and is_in_strong_pool:
            return {
                'rating': "B",
                'description': "涨停且为强势股，但需关注异动"
            }
        elif is_limit_up:
            return {
                'rating': "B-",
                'description': "涨停，但需关注异动情况"
            }
        elif is_in_strong_pool and not is_in_炸板_pool:
            return {
                'rating': "C+",
                'description': "非涨停，但属于强势股"
            }
        elif is_in_strong_pool:
            return {
                'rating': "C",
                'description': "属于强势股，但有炸板风险"
            }
        elif has_big_sell:
            return {
                'rating': "E",
                'description': "存在大笔卖出（漏单）"
            }
        else:
            return {
                'rating': "F",
                'description': "无显著异动"
            }
    
    def _generate_investment_advice(self, is_limit_up: bool, has_open_limit: bool,
                                   has_big_sell: bool, is_in_炸板_pool: bool,
                                   is_in_strong_pool: bool, has_re_limit: bool = False) -> str:
        """生成投资建议"""
        # 如果有炸板但没有重新封板
        if has_open_limit and not has_re_limit:
            return "炸板后未重新封板，走势疲弱，建议回避"
        
        # 其他建议逻辑
        if is_limit_up and not has_open_limit and not is_in_炸板_pool and not has_big_sell and is_in_strong_pool:
            return "封板质量优秀，可考虑持有或适量参与"
        elif is_limit_up and not has_open_limit and not is_in_炸板_pool:
            return "封板稳固，可关注次日表现"
        elif is_limit_up and has_re_limit and not has_big_sell and is_in_strong_pool:
            return "炸板后重新封板，显示承接有力，可谨慎关注"
        elif is_limit_up and has_re_limit and not has_big_sell:
            return "炸板后重新封板，显示一定承接，但需注意风险"
        elif is_limit_up and is_in_strong_pool:
            return "涨停且为强势股，但需注意异动，谨慎参与"
        elif is_limit_up:
            return "涨停但需警惕异动，建议观察"
        elif is_in_strong_pool and not is_in_炸板_pool:
            return "非涨停但属强势股，可关注回调机会"
        elif is_in_strong_pool:
            return "属于强势股，但有炸板风险"
        elif has_big_sell:
            return "存在漏单，主力可能出逃，建议回避"
        else:
            return "无明显异动，建议继续观察"
    
    def batch_analysis(self, symbols: List[str]) -> pd.DataFrame:
        """
        批量分析多只股票
        """
        print(f"\n开始批量分析 {len(symbols)} 只股票...")
        
        all_results = []
        
        for i, symbol in enumerate(symbols, 1):
            try:
                print(f"\n分析第 {i}/{len(symbols)} 只股票: {symbol}")
                
                # 获取综合分析
                analysis = self.comprehensive_stock_analysis(symbol)
                
                # 提取关键信息
                stock_result = {
                    '股票代码': symbol,
                    '股票名称': analysis.get('涨停异动分析', {}).get('股票代码', ''),
                    '是否涨停': analysis['关键指标']['是否涨停'],
                    '是否有炸板': analysis['关键指标']['是否有炸板'],
                    '是否漏单': analysis['关键指标']['是否漏单'],
                    '是否重新封板': analysis['关键指标']['是否重新封板'],
                    '是否强势股': analysis['关键指标']['是否强势股'],
                    '炸板次数': analysis['关键指标']['炸板次数'],
                    '综合评级': analysis['综合评级'],
                    '投资建议': analysis['投资建议']
                }
                
                all_results.append(stock_result)
                
            except Exception as e:
                print(f"分析股票 {symbol} 时出错: {e}")
                continue
        
        if all_results:
            df = pd.DataFrame(all_results)
            print(f"\n批量分析完成，成功分析 {len(df)} 只股票")
            return df
        else:
            print("未成功分析任何股票")
            return pd.DataFrame()
    
    # 代理方法，用于提供与原模块相同的接口
    def analyze_limit_up_changes(self, symbol: str) -> Dict[str, Any]:
        """分析股票异动情况"""
        return self.changes_module.analyze_limit_up_changes(symbol)
    
    def check_if_炸板(self, symbol: str, date: str = None) -> Dict[str, Any]:
        """检查股票是否炸板"""
        return self.pool_module.check_if_炸板(symbol, date)
    
    def check_if_strong_stock(self, symbol: str, date: str = None) -> Dict[str, Any]:
        """检查股票是否强势股"""
        return self.pool_module.check_if_strong_stock(symbol, date)
    
    def get_stock_changes(self, change_type: str = "封涨停板") -> pd.DataFrame:
        """获取异动数据"""
        return self.changes_module.get_stock_changes(change_type)
    
    def get_炸板_stocks(self, date: str = None) -> pd.DataFrame:
        """获取炸板股池数据"""
        return self.pool_module.get_炸板_stocks(date)
    
    def get_strong_stocks(self, date: str = None) -> pd.DataFrame:
        """获取强势股池数据"""
        return self.pool_module.get_strong_stocks(date)
    
    def _get_streak_days(self, symbol: str) -> int:
        """
        获取连板天数 - 改进版
        
        Args:
            symbol: 股票代码或名称
            
        Returns:
            连板天数，如果无法获取则返回0
        """
        try:
            # 首先尝试解析股票代码
            stock_code = None
            
            # 如果输入看起来像股票代码（6位数字）
            import re
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
                    for field in ['连板天数', '连板数', '连板', 'streak_days', 'streak', '连续涨停天数', '涨停天数', '连板高度']:
                        if field in stock_info:
                            value = stock_info[field]
                            if isinstance(value, (int, float)):
                                result = int(value)
                                # 直接返回结果，不额外加1
                                # 因为数据源应该已经包含了今天的状态
                                if result > 0:
                                    print(f"从 stock_data_fetcher 获取到连板天数: {result}")
                                    return result
                            elif isinstance(value, str):
                                # 提取数字
                                match = re.search(r'(\d+)', value)
                                if match:
                                    result = int(match.group(1))
                                    if result > 0:
                                        print(f"从 stock_data_fetcher 字段 {field} 提取到连板天数: {result}")
                                        return result
            except ImportError:
                print("无法导入 stock_data_fetcher，将使用备用方法")
            except Exception as e:
                print(f"从 stock_data_fetcher 获取连板天数失败: {e}")
            
            # 备用方法：使用 akshare 的涨停板池历史数据，改进版
            try:
                import akshare as ak
                import pandas as pd
                from datetime import datetime, timedelta
                
                # 获取当前查询日期
                current_date = self.get_query_date()
                current_dt = datetime.strptime(current_date, '%Y%m%d')
                
                streak_days = 0
                max_days_to_check = 30  # 最多检查30个交易日
                consecutive_failures = 0
                
                print(f"开始使用备用方法计算连板天数: {stock_code}")
                
                # 首先检查今天是否涨停
                today_in_pool = False
                try:
                    df_today = ak.stock_zt_pool_em(date=current_date)
                    if df_today is not None and not df_today.empty and '代码' in df_today.columns:
                        codes_today = df_today['代码'].astype(str).str.zfill(6).tolist()
                        if stock_code in codes_today:
                            today_in_pool = True
                            streak_days = 1
                            print(f"  今天 ({current_date}) 涨停，开始向前检查连板")
                except:
                    pass
                
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
                                consecutive_failures += 1
                                if consecutive_failures > 5:
                                    print(f"  连续 {consecutive_failures} 天无法获取数据，停止检查")
                                    break
                                continue
                            
                            # 重置连续失败计数
                            consecutive_failures = 0
                            
                            # 检查股票是否在涨停板池中
                            if '代码' in df.columns:
                                codes_in_pool = df['代码'].astype(str).str.zfill(6).tolist()
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
                            consecutive_failures += 1
                            if consecutive_failures > 5:
                                print(f"  连续 {consecutive_failures} 次获取数据失败，停止检查")
                                break
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
                            
                            if '代码' in df.columns:
                                codes_in_pool = df['代码'].astype(str).str.zfill(6).tolist()
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
                                            if '代码' in df_prev.columns:
                                                codes_prev = df_prev['代码'].astype(str).str.zfill(6).tolist()
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
    
    def _check_if_in_limit_pool_on_date(self, symbol: str, date_str: str):
        """
        检查指定日期股票是否在涨停板池中
        
        Args:
            symbol: 股票代码
            date_str: 日期字符串 (YYYYMMDD)
            
        Returns:
            True: 在涨停板池中
            False: 不在涨停板池中（有数据）
            None: 无法获取数据（可能是非交易日）
        """
        try:
            # 使用 akshare 的 stock_zt_pool_em 接口获取指定日期的涨停板池数据
            import akshare as ak
            
            # 检查缓存
            cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stock_data_cache")
            cache_key = f"limit_pool_{date_str}"
            cache_file = os.path.join(cache_dir, f"{cache_key}.csv")
            
            df = None
            if os.path.exists(cache_file):
                try:
                    df = pd.read_csv(cache_file)
                    # 检查缓存是否有效（非空）
                    if df is not None and not df.empty:
                        # 检查股票是否在涨停板池中
                        if '代码' in df.columns:
                            symbol_clean = str(symbol).zfill(6)
                            is_in_pool = symbol_clean in df['代码'].values
                            return is_in_pool
                        else:
                            return False
                except Exception as e:
                    print(f"读取涨停板池缓存失败: {e}")
                    df = None
            
            # 如果缓存不存在或无效，从接口获取
            try:
                df = ak.stock_zt_pool_em(date=date_str)
                
                if df is None:
                    # 接口返回None，可能是非交易日或数据不可用
                    return None
                
                if df.empty:
                    # 空DataFrame，可能是非交易日
                    return None
                
                # 保存到缓存
                try:
                    if not os.path.exists(cache_dir):
                        os.makedirs(cache_dir)
                    df.to_csv(cache_file, index=False, encoding='utf-8-sig')
                except Exception as e:
                    print(f"保存涨停板池缓存失败: {e}")
                
                # 检查股票是否在涨停板池中
                if '代码' in df.columns:
                    symbol_clean = str(symbol).zfill(6)
                    is_in_pool = symbol_clean in df['代码'].values
                    return is_in_pool
                else:
                    return False
                    
            except Exception as e:
                # 接口调用失败，可能是非交易日或网络问题
                return None
                
        except Exception as e:
            print(f"检查涨停板池失败: {e}")
            return None
    
    def get_board_changes(self) -> pd.DataFrame:
        """获取板块异动数据"""
        return self.pool_module.get_board_changes()
