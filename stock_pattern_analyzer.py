#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票模式分析器 - 量化分析规则逻辑
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import akshare as ak
import warnings
warnings.filterwarnings('ignore')

class StockPatternAnalyzer:
    """股票模式分析器"""
    
    def __init__(self):
        """初始化"""
        pass
    
    def analyze_stock_pattern(self, symbol: str, days_back: int = 5) -> Dict[str, Any]:
        """
        分析股票的模式
        
        Args:
            symbol: 股票代码
            days_back: 回溯天数
            
        Returns:
            模式分析结果
        """
        try:
            # 获取历史数据
            history_data = self._get_stock_history(symbol, days_back)
            if history_data.empty:
                return {"error": "无法获取历史数据"}
            
            # 分析各种模式
            patterns = {}
            
            # 1. 分析换手率模式
            patterns["turnover_pattern"] = self._analyze_turnover_pattern(history_data)
            
            # 2. 分析强弱转换模式
            patterns["strength_pattern"] = self._analyze_strength_pattern(history_data)
            
            # 3. 分析量价关系
            patterns["volume_price_pattern"] = self._analyze_volume_price_pattern(history_data)
            
            # 4. 分析连板类型
            patterns["limit_up_pattern"] = self._analyze_limit_up_pattern(history_data)
            
            # 5. 综合评估
            patterns["comprehensive_assessment"] = self._comprehensive_assessment(patterns, history_data)
            
            return {
                "symbol": symbol,
                "analysis_date": datetime.now().strftime('%Y-%m-%d'),
                "history_days": days_back,
                "patterns": patterns,
                "recommendation": patterns["comprehensive_assessment"]["recommendation"],
                "confidence": patterns["comprehensive_assessment"]["confidence"]
            }
            
        except Exception as e:
            return {"error": f"分析失败: {str(e)}"}
    
    def _get_stock_history(self, symbol: str, days_back: int) -> pd.DataFrame:
        """
        获取股票历史数据（包括涨停、换手率等信息）
        使用更准确的数据源：akshare的日线数据
        """
        try:
            # 清理股票代码
            symbol_clean = str(symbol).zfill(6)
            
            # 获取股票日线数据
            try:
                # 获取最近days_back*2天的数据，确保有足够交易日
                end_date = datetime.now().strftime('%Y%m%d')
                start_date = (datetime.now() - timedelta(days=days_back*3)).strftime('%Y%m%d')
                
                # 获取日线数据
                stock_zh_a_hist_df = ak.stock_zh_a_hist(
                    symbol=symbol_clean, 
                    period="daily", 
                    start_date=start_date, 
                    end_date=end_date,
                    adjust="qfq"
                )
                
                if stock_zh_a_hist_df.empty:
                    print(f"无法获取股票 {symbol_clean} 的日线数据")
                    return pd.DataFrame()
                
                # 重命名列
                stock_zh_a_hist_df = stock_zh_a_hist_df.rename(columns={
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
                
                # 确保有需要的列
                if 'turnover' not in stock_zh_a_hist_df.columns:
                    # 尝试其他可能的列名
                    for col in ['换手率', 'turnover_rate', '换手']:
                        if col in stock_zh_a_hist_df.columns:
                            stock_zh_a_hist_df['turnover'] = stock_zh_a_hist_df[col]
                            break
                
                # 添加是否涨停的标记
                stock_zh_a_hist_df['is_limit_up'] = stock_zh_a_hist_df.apply(
                    lambda row: self._is_limit_up(row), axis=1
                )
                
                # 添加涨停类型标记
                stock_zh_a_hist_df['limit_type'] = stock_zh_a_hist_df.apply(
                    lambda row: self._get_limit_type(row), axis=1
                )
                
                # 只保留最近days_back天的数据
                stock_zh_a_hist_df = stock_zh_a_hist_df.head(days_back)
                
                # 按日期排序（最近的在前）
                stock_zh_a_hist_df = stock_zh_a_hist_df.sort_values('date', ascending=False)
                
                return stock_zh_a_hist_df
                
            except Exception as e:
                print(f"获取日线数据失败: {e}")
                # 备用方案：使用涨停板池数据
                return self._get_stock_history_fallback(symbol_clean, days_back)
                
        except Exception as e:
            print(f"获取历史数据失败: {e}")
            return pd.DataFrame()
    
    def _get_stock_history_fallback(self, symbol_clean: str, days_back: int) -> pd.DataFrame:
        """备用方法：从涨停板池获取数据"""
        all_data = []
        
        current_date = datetime.now()
        for i in range(days_back):
            check_date = current_date - timedelta(days=i)
            date_str = check_date.strftime('%Y%m%d')
            
            try:
                df = ak.stock_zt_pool_em(date=date_str)
                if df is not None and not df.empty:
                    # 标准化代码列
                    if '代码' in df.columns:
                        df['代码'] = df['代码'].astype(str).str.zfill(6)
                        # 筛选目标股票
                        stock_data = df[df['代码'] == symbol_clean]
                        if not stock_data.empty:
                            stock_row = stock_data.iloc[0].to_dict()
                            stock_row['date'] = date_str
                            stock_row['is_limit_up'] = True
                            all_data.append(stock_row)
            except:
                continue
        
        # 转换为DataFrame
        if all_data:
            history_df = pd.DataFrame(all_data)
            # 按日期排序
            history_df = history_df.sort_values('date', ascending=False)
            return history_df
        else:
            return pd.DataFrame()
    
    def _is_limit_up(self, row) -> bool:
        """判断是否涨停"""
        try:
            # 如果涨跌幅接近10%（考虑四舍五入）
            pct_change = row.get('pct_change', 0)
            if isinstance(pct_change, (int, float)):
                return abs(pct_change - 10.0) < 0.5 or pct_change >= 9.8
            return False
        except:
            return False
    
    def _get_limit_type(self, row) -> str:
        """判断涨停类型"""
        try:
            if not self._is_limit_up(row):
                return "非涨停"
            
            open_price = row.get('open', 0)
            close_price = row.get('close', 0)
            high_price = row.get('high', 0)
            low_price = row.get('low', 0)
            
            # 计算涨停价（假设是10%涨停）
            prev_close = close_price / 1.1  # 近似计算
            
            # 判断是否一字板
            if abs(open_price - high_price) < 0.01 and abs(open_price - prev_close * 1.1) < 0.01:
                return "一字板"
            # 判断是否T字板
            elif abs(open_price - high_price) < 0.01 and low_price < open_price:
                return "T字板"
            else:
                return "普通涨停"
        except:
            return "未知"
    
    def _analyze_turnover_pattern(self, history_data: pd.DataFrame) -> Dict[str, Any]:
        """
        分析换手率模式 - 改进版
        """
        result = {
            "pattern_type": "unknown",
            "description": "",
            "indicators": {}
        }
        
        if history_data.empty:
            return result
        
        # 提取换手率数据
        turnover_rates = []
        for _, row in history_data.iterrows():
            try:
                # 尝试从不同字段获取换手率
                turnover = None
                for field in ['turnover', '换手率', 'turnover_rate']:
                    if field in row and pd.notna(row[field]):
                        val = row[field]
                        if isinstance(val, (int, float)):
                            turnover = float(val)
                            break
                        elif isinstance(val, str):
                            # 提取数字
                            import re
                            match = re.search(r'([\d\.]+)', val)
                            if match:
                                turnover = float(match.group(1))
                                break
                
                if turnover is None:
                    turnover = 0.0
                turnover_rates.append(turnover)
            except:
                turnover_rates.append(0.0)
        
        if len(turnover_rates) < 2:
            return result
        
        result["indicators"]["turnover_rates"] = turnover_rates
        
        # 分析换手率趋势
        # 计算最近3天的换手率变化
        recent_turnover = turnover_rates[:min(3, len(turnover_rates))]
        
        # 判断模式
        if len(recent_turnover) >= 3:
            # 检查是否是爆量->缩量->缩量模式
            if recent_turnover[0] < 5.0 and recent_turnover[1] < recent_turnover[2] and recent_turnover[2] > 10.0:
                result["pattern_type"] = "volume_decrease_strengthen"
                result["description"] = "首板爆量，随后缩量走强，良性换手"
            elif recent_turnover[0] < recent_turnover[1] < recent_turnover[2]:
                result["pattern_type"] = "volume_increasing"
                result["description"] = "换手率逐步增加，需要关注承接"
            elif recent_turnover[0] > recent_turnover[1] > recent_turnover[2]:
                result["pattern_type"] = "volume_decreasing"
                result["description"] = "换手率逐步降低，缩量走强"
            elif recent_turnover[0] < 3.0 and recent_turnover[1] < 3.0:
                result["pattern_type"] = "low_volume"
                result["description"] = "连续低换手，可能一字板或快速涨停"
            else:
                result["pattern_type"] = "variable_volume"
                result["description"] = "换手率变化不定"
        else:
            # 简单判断
            if len(recent_turnover) >= 2:
                if recent_turnover[0] < recent_turnover[1]:
                    result["pattern_type"] = "volume_decreasing_recent"
                    result["description"] = "近期缩量，走强信号"
                else:
                    result["pattern_type"] = "volume_increasing_recent"
                    result["description"] = "近期放量，需要关注"
        
        return result
    
    def _analyze_strength_pattern(self, history_data: pd.DataFrame) -> Dict[str, Any]:
        """
        分析强弱转换模式 - 改进版
        """
        result = {
            "pattern_type": "unknown",
            "description": "",
            "indicators": {}
        }
        
        if history_data.empty:
            return result
        
        # 检查是否连续涨停
        limit_up_days = 0
        for _, row in history_data.iterrows():
            if row.get('is_limit_up', False):
                limit_up_days += 1
        
        # 检查涨停类型
        limit_types = []
        for _, row in history_data.iterrows():
            if row.get('is_limit_up', False):
                limit_type = row.get('limit_type', '普通涨停')
                limit_types.append(limit_type)
        
        result["indicators"]["limit_up_days"] = limit_up_days
        result["indicators"]["limit_types"] = limit_types
        
        # 判断模式
        if limit_up_days >= 2:
            # 检查涨停类型变化
            if len(limit_types) >= 2:
                # 检查是否从放量板到缩量板到一字板
                if (len(limit_types) >= 3 and 
                    limit_types[0] == "一字板" and 
                    limit_types[1] in ["普通涨停", "T字板"] and
                    limit_types[2] in ["普通涨停", "T字板"]):
                    result["pattern_type"] = "strengthening_pattern"
                    result["description"] = "从放量到缩量到一字，明显走强"
                elif limit_types[0] == "一字板" and limit_up_days >= 2:
                    result["pattern_type"] = "strong_continuation"
                    result["description"] = "连续一字板，极强走势"
                elif "T字板" in limit_types[:2]:
                    result["pattern_type"] = "t_word_pattern"
                    result["description"] = "有T字板，需要换手"
                else:
                    result["pattern_type"] = "continuous_limit_up"
                    result["description"] = "连续涨停，表现强势"
            else:
                result["pattern_type"] = "continuous_limit_up"
                result["description"] = "连续涨停，表现强势"
        elif limit_up_days == 1:
            result["pattern_type"] = "single_limit_up"
            result["description"] = "单日涨停，需观察后续"
        else:
            result["pattern_type"] = "no_limit_up"
            result["description"] = "近期无涨停"
        
        return result
    
    def _analyze_volume_price_pattern(self, history_data: pd.DataFrame) -> Dict[str, Any]:
        """
        分析量价关系模式 - 改进版
        """
        result = {
            "pattern_type": "unknown",
            "description": "",
            "indicators": {}
        }
        
        if history_data.empty or len(history_data) < 2:
            return result
        
        # 获取换手率数据
        turnover_rates = []
        for _, row in history_data.iterrows():
            try:
                turnover = None
                for field in ['turnover', '换手率', 'turnover_rate']:
                    if field in row and pd.notna(row[field]):
                        val = row[field]
                        if isinstance(val, (int, float)):
                            turnover = float(val)
                            break
                        elif isinstance(val, str):
                            import re
                            match = re.search(r'([\d\.]+)', val)
                            if match:
                                turnover = float(match.group(1))
                                break
                if turnover is None:
                    turnover = 0.0
                turnover_rates.append(turnover)
            except:
                turnover_rates.append(0.0)
        
        result["indicators"]["turnover_rates"] = turnover_rates
        
        # 分析量价关系
        if len(turnover_rates) >= 3:
            # 检查是否是爆量->缩量->缩量模式（标准走强模式）
            if turnover_rates[2] > 15.0 and turnover_rates[1] < turnover_rates[2] and turnover_rates[0] < turnover_rates[1]:
                result["pattern_type"] = "standard_strengthening"
                result["description"] = "首板爆量释放套牢盘，随后缩量走强，标准模式"
            # 检查是否是连续缩量
            elif turnover_rates[0] < turnover_rates[1] < turnover_rates[2]:
                result["pattern_type"] = "continuous_volume_decrease"
                result["description"] = "连续缩量，筹码锁定良好，走强信号"
            # 检查是否是放量->缩量
            elif turnover_rates[0] < turnover_rates[1] and turnover_rates[1] > 10.0:
                result["pattern_type"] = "volume_decrease_after_high"
                result["description"] = "高换手后缩量，良性换手"
            else:
                result["pattern_type"] = "other_pattern"
                result["description"] = "量价关系需结合其他因素判断"
        elif len(turnover_rates) >= 2:
            if turnover_rates[0] < turnover_rates[1]:
                result["pattern_type"] = "recent_volume_decrease"
                result["description"] = "近期缩量，走强信号"
            else:
                result["pattern_type"] = "recent_volume_increase"
                result["description"] = "近期放量，需要关注承接"
        
        return result
    
    def _analyze_limit_up_pattern(self, history_data: pd.DataFrame) -> Dict[str, Any]:
        """
        分析连板类型模式 - 改进版
        """
        result = {
            "pattern_type": "unknown",
            "description": "",
            "indicators": {}
        }
        
        if history_data.empty:
            return result
        
        # 获取涨停类型
        limit_types = []
        for _, row in history_data.iterrows():
            if row.get('is_limit_up', False):
                limit_type = row.get('limit_type', '普通涨停')
                limit_types.append(limit_type)
            else:
                limit_types.append("非涨停")
        
        result["indicators"]["limit_types"] = limit_types
        
        # 分析最近3天的涨停类型
        recent_limit_types = []
        for i in range(min(3, len(limit_types))):
            if limit_types[i] != "非涨停":
                recent_limit_types.append(limit_types[i])
        
        # 判断模式
        if len(recent_limit_types) >= 2:
            if recent_limit_types[0] == "一字板" and len(recent_limit_types) >= 2 and recent_limit_types[1] == "一字板":
                result["pattern_type"] = "continuous_one_word"
                result["description"] = "连续一字板，极强走势"
            elif recent_limit_types[0] == "一字板":
                result["pattern_type"] = "recent_one_word"
                result["description"] = "近期一字板，表现强势"
            elif "T字板" in recent_limit_types:
                result["pattern_type"] = "has_t_word"
                result["description"] = "有T字板，需要换手"
            elif len(recent_limit_types) >= 3:
                # 检查模式：普通涨停 -> 缩量板 -> 一字板
                if (recent_limit_types[0] == "一字板" and 
                    recent_limit_types[1] in ["普通涨停", "T字板"] and
                    recent_limit_types[2] in ["普通涨停", "T字板"]):
                    result["pattern_type"] = "strengthening_sequence"
                    result["description"] = "从放量到缩量到一字，标准走强模式"
                else:
                    result["pattern_type"] = "mixed_pattern"
                    result["description"] = "混合涨停类型"
            else:
                result["pattern_type"] = "normal_limit"
                result["description"] = "普通涨停模式"
        else:
            result["pattern_type"] = "insufficient_data"
            result["description"] = "数据不足，无法判断"
        
        return result
    
    def _comprehensive_assessment(self, patterns: Dict[str, Any], history_data: pd.DataFrame) -> Dict[str, Any]:
        """
        综合评估 - 改进版
        """
        assessment = {
            "recommendation": "观望",
            "confidence": 0.5,
            "key_factors": [],
            "risk_level": "medium"
        }
        
        # 收集关键因素
        key_factors = []
        
        # 1. 换手率因素
        turnover_pattern = patterns.get("turnover_pattern", {})
        turnover_type = turnover_pattern.get("pattern_type", "")
        
        if turnover_type in ["volume_decrease_strengthen", "volume_decreasing", "continuous_volume_decrease"]:
            key_factors.append("换手率逐步降低，缩量走强")
            assessment["confidence"] *= 1.3
        elif turnover_type == "volume_increasing":
            key_factors.append("换手率逐步增加，需要关注承接")
            assessment["confidence"] *= 0.8
        
        # 2. 强弱因素
        strength_pattern = patterns.get("strength_pattern", {})
        strength_type = strength_pattern.get("pattern_type", "")
        
        if strength_type in ["strengthening_pattern", "strong_continuation", "continuous_limit_up"]:
            key_factors.append("连续涨停，表现强势")
            assessment["confidence"] *= 1.4
        elif strength_type == "t_word_pattern":
            key_factors.append("有T字板，需要换手")
            assessment["confidence"] *= 1.1
        
        # 3. 量价因素
        volume_pattern = patterns.get("volume_price_pattern", {})
        volume_type = volume_pattern.get("pattern_type", "")
        
        if volume_type in ["standard_strengthening", "continuous_volume_decrease", "volume_decrease_after_high"]:
            key_factors.append("量价配合良好，缩量走强")
            assessment["confidence"] *= 1.3
            assessment["recommendation"] = "继续走强"
        elif volume_type == "recent_volume_increase":
            key_factors.append("近期放量，需要关注承接")
            assessment["confidence"] *= 0.9
        
        # 4. 连板类型因素
        limit_pattern = patterns.get("limit_up_pattern", {})
        limit_type = limit_pattern.get("pattern_type", "")
        
        if limit_type in ["continuous_one_word", "recent_one_word"]:
            key_factors.append("一字板涨停，表现极强")
            assessment["confidence"] *= 1.5
            assessment["recommendation"] = "继续一字或大高开"
        elif limit_type == "strengthening_sequence":
            key_factors.append("从放量到缩量到一字，标准走强模式")
            assessment["confidence"] *= 1.4
            assessment["recommendation"] = "良性换手，继续走强"
        elif limit_type == "has_t_word":
            key_factors.append("有T字板，需要换手预期")
            assessment["recommendation"] = "换手预期"
        
        # 综合判断
        if not history_data.empty:
            # 计算连续涨停天数
            limit_up_count = 0
            for _, row in history_data.iterrows():
                if row.get('is_limit_up', False):
                    limit_up_count += 1
            
            if limit_up_count > 0:
                key_factors.append(f"连续{limit_up_count}天涨停")
            
            # 根据多个因素调整推荐
            if "一字板涨停" in key_factors and "缩量走强" in key_factors:
                assessment["recommendation"] = "继续一字或大高开快速涨停"
                assessment["confidence"] = min(assessment["confidence"] * 1.2, 0.95)
            elif "连续涨停" in key_factors and "缩量走强" in key_factors:
                assessment["recommendation"] = "良性换手，继续走强"
                assessment["confidence"] = min(assessment["confidence"] * 1.1, 0.9)
        
        assessment["key_factors"] = key_factors
        
        # 限制置信度范围
        assessment["confidence"] = max(0.1, min(0.95, assessment["confidence"]))
        
        return assessment
    
    def analyze_multiple_stocks(self, symbols: List[str]) -> pd.DataFrame:
        """
        批量分析多只股票
        """
        results = []
        
        for symbol in symbols:
            print(f"分析股票: {symbol}")
            analysis = self.analyze_stock_pattern(symbol)
            
            if "error" not in analysis:
                results.append({
                    "股票代码": symbol,
                    "推荐": analysis.get("recommendation", "未知"),
                    "置信度": f"{analysis.get('confidence', 0)*100:.1f}%",
                    "关键因素": "; ".join(analysis.get("patterns", {}).get("comprehensive_assessment", {}).get("key_factors", [])),
                    "换手模式": analysis.get("patterns", {}).get("turnover_pattern", {}).get("description", ""),
                    "强弱模式": analysis.get("patterns", {}).get("strength_pattern", {}).get("description", ""),
                    "连板模式": analysis.get("patterns", {}).get("limit_up_pattern", {}).get("description", "")
                })
        
        return pd.DataFrame(results)


# 创建全局实例
pattern_analyzer = StockPatternAnalyzer()

def analyze_stock_pattern(symbol: str) -> Dict[str, Any]:
    """分析股票模式的快捷函数"""
    return pattern_analyzer.analyze_stock_pattern(symbol)

def batch_pattern_analysis(symbols: List[str]) -> pd.DataFrame:
    """批量分析股票模式的快捷函数"""
    return pattern_analyzer.analyze_multiple_stocks(symbols)

if __name__ == "__main__":
    # 测试代码
    print("股票模式分析器测试")
    print("=" * 60)
    
    # 测试几只股票
    test_symbols = ["002123", "002202", "600637"]
    
    for symbol in test_symbols:
        print(f"\n分析股票 {symbol}:")
        result = analyze_stock_pattern(symbol)
        
        if "error" in result:
            print(f"  分析失败: {result['error']}")
        else:
            print(f"  推荐: {result['recommendation']}")
            print(f"  置信度: {result['confidence']*100:.1f}%")
            print(f"  关键因素: {', '.join(result['patterns']['comprehensive_assessment']['key_factors'])}")
    
    # 批量分析
    print(f"\n批量分析结果:")
    df = batch_pattern_analysis(test_symbols)
    if not df.empty:
        print(df.to_string(index=False))
