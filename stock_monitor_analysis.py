# stock_monitor_analysis.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票综合分析模块
包含综合分析和批量分析
"""

import pandas as pd
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
            symbol_clean = str(symbol).zfill(6)
            
            print(f"\n{'='*60}")
            print(f"开始对 {symbol_clean} 进行综合分析...")
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
                    '最终是否涨停': final_is_limit_up
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
    
    def get_board_changes(self) -> pd.DataFrame:
        """获取板块异动数据"""
        return self.pool_module.get_board_changes()
