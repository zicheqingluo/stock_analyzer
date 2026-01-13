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
        """
        try:
            # 清理股票代码
            symbol_clean = str(symbol).zfill(6)
            
            # 获取最近几天的涨停板池数据
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days_back*2)).strftime('%Y%m%d')
            
            all_data = []
            
            # 获取每日的涨停板池数据
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
                
        except Exception as e:
            print(f"获取历史数据失败: {e}")
            return pd.DataFrame()
    
    def _analyze_turnover_pattern(self, history_data: pd.DataFrame) -> Dict[str, Any]:
        """
        分析换手率模式
        """
        result = {
            "pattern_type": "unknown",
            "description": "",
            "indicators": {}
        }
        
        if history_data.empty or '换手率' not in history_data.columns:
            return result
        
        # 提取换手率数据
        turnover_rates = []
        for _, row in history_data.iterrows():
            try:
                turnover_str = str(row['换手率'])
                # 提取数字
                import re
                match = re.search(r'([\d\.]+)', turnover_str)
                if match:
                    turnover_rates.append(float(match.group(1)))
                else:
                    turnover_rates.append(0.0)
            except:
                turnover_rates.append(0.0)
        
        if len(turnover_rates) < 2:
            return result
        
        # 分析换手率趋势
        result["indicators"]["turnover_rates"] = turnover_rates
        result["indicators"]["turnover_trend"] = "increasing" if turnover_rates[0] > turnover_rates[-1] else "decreasing"
        
        # 判断模式
        if all(rate > 1.0 for rate in turnover_rates[:2]):  # 最近两天换手率都超过1%
            result["pattern_type"] = "high_turnover"
            result["description"] = "连续高换手，需要关注承接能力"
        elif turnover_rates[0] > turnover_rates[1] and turnover_rates[0] > 1.0:
            result["pattern_type"] = "increasing_turnover"
            result["description"] = "换手率逐步增加，超过1%，需要看承接"
        elif all(rate < 0.5 for rate in turnover_rates[:2]):
            result["pattern_type"] = "low_turnover"
            result["description"] = "连续缩量，要么预期一致走一字，要么换手分歧"
        else:
            result["pattern_type"] = "normal_turnover"
            result["description"] = "换手率正常"
        
        return result
    
    def _analyze_strength_pattern(self, history_data: pd.DataFrame) -> Dict[str, Any]:
        """
        分析强弱转换模式
        """
        result = {
            "pattern_type": "unknown",
            "description": "",
            "indicators": {}
        }
        
        if history_data.empty:
            return result
        
        # 检查是否有炸板数据
        has_blow_up = False
        blow_up_count = 0
        
        for _, row in history_data.iterrows():
            # 检查炸板次数
            if '炸板次数' in row:
                try:
                    blow_up = int(row['炸板次数'])
                    if blow_up > 0:
                        has_blow_up = True
                        blow_up_count += blow_up
                except:
                    pass
        
        # 检查是否重新封板（通过是否在涨停板池中判断）
        re_limit_count = len(history_data)
        
        result["indicators"]["has_blow_up"] = has_blow_up
        result["indicators"]["blow_up_count"] = blow_up_count
        result["indicators"]["re_limit_count"] = re_limit_count
        
        # 判断模式
        if has_blow_up and re_limit_count > 0:
            result["pattern_type"] = "weak_to_strong"
            result["description"] = "有炸板但能回封，该弱不弱视为强"
        elif not has_blow_up and re_limit_count > 0:
            result["pattern_type"] = "strong_continuation"
            result["description"] = "无炸板连续涨停，表现强势"
        elif has_blow_up and re_limit_count == 0:
            result["pattern_type"] = "strong_to_weak"
            result["description"] = "有炸板且未回封，走势疲弱"
        else:
            result["pattern_type"] = "neutral"
            result["description"] = "无明显强弱特征"
        
        return result
    
    def _analyze_volume_price_pattern(self, history_data: pd.DataFrame) -> Dict[str, Any]:
        """
        分析量价关系模式
        """
        result = {
            "pattern_type": "unknown",
            "description": "",
            "indicators": {}
        }
        
        if history_data.empty or len(history_data) < 3:
            return result
        
        # 简化分析：检查是否有放量->缩量->放量的模式
        # 这里需要实际成交量数据，但涨停板池数据可能不包含
        # 使用换手率作为替代指标
        
        if '换手率' in history_data.columns:
            turnover_pattern = []
            for i in range(min(3, len(history_data))):
                try:
                    turnover_str = str(history_data.iloc[i]['换手率'])
                    import re
                    match = re.search(r'([\d\.]+)', turnover_str)
                    if match:
                        turnover = float(match.group(1))
                        if turnover > 2.0:
                            turnover_pattern.append("high")
                        elif turnover > 1.0:
                            turnover_pattern.append("medium")
                        else:
                            turnover_pattern.append("low")
                except:
                    turnover_pattern.append("unknown")
            
            result["indicators"]["turnover_pattern"] = turnover_pattern
            
            # 判断模式
            if len(turnover_pattern) >= 3:
                if turnover_pattern[0] == "high" and turnover_pattern[1] == "low" and turnover_pattern[2] == "high":
                    result["pattern_type"] = "high_low_high"
                    result["description"] = "放量-缩量-放量模式，需要爆量换手释放压力"
                elif turnover_pattern[0] == "low" and turnover_pattern[1] == "low":
                    result["pattern_type"] = "continuous_low"
                    result["description"] = "连续缩量，需要高开缩量晋级"
                elif turnover_pattern[0] == "high":
                    result["pattern_type"] = "recent_high"
                    result["description"] = "近期放量，需要换手预期"
                else:
                    result["pattern_type"] = "variable"
                    result["description"] = "量能变化不定"
        
        return result
    
    def _analyze_limit_up_pattern(self, history_data: pd.DataFrame) -> Dict[str, Any]:
        """
        分析连板类型模式
        """
        result = {
            "pattern_type": "unknown",
            "description": "",
            "indicators": {}
        }
        
        if history_data.empty:
            return result
        
        # 检查涨停类型（一字板、T字板、普通涨停）
        limit_types = []
        
        for _, row in history_data.iterrows():
            # 通过首次封板时间和最后封板时间判断
            first_limit = str(row.get('首次封板时间', ''))
            last_limit = str(row.get('最后封板时间', ''))
            
            if first_limit.startswith('09:25') and last_limit.startswith('09:25'):
                limit_types.append("一字板")
            elif first_limit != last_limit and first_limit != '':
                limit_types.append("T字板")
            else:
                limit_types.append("普通涨停")
        
        result["indicators"]["limit_types"] = limit_types
        result["indicators"]["continuous_one_word"] = all(t == "一字板" for t in limit_types[:min(2, len(limit_types))])
        result["indicators"]["has_t_word"] = any(t == "T字板" for t in limit_types)
        
        # 判断模式
        if result["indicators"]["continuous_one_word"]:
            result["pattern_type"] = "continuous_one_word"
            result["description"] = "连续一字板，强更强，可能继续一字"
        elif result["indicators"]["has_t_word"]:
            result["pattern_type"] = "has_t_word"
            result["description"] = "有T字板，强度较弱，需要换手预期"
        elif len(limit_types) >= 2 and limit_types[0] == "一字板":
            result["pattern_type"] = "recent_one_word"
            result["description"] = "近期一字板，表现强势"
        else:
            result["pattern_type"] = "normal_limit"
            result["description"] = "普通涨停模式"
        
        return result
    
    def _comprehensive_assessment(self, patterns: Dict[str, Any], history_data: pd.DataFrame) -> Dict[str, Any]:
        """
        综合评估
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
        if turnover_pattern.get("pattern_type") == "increasing_turnover":
            key_factors.append("换手率逐步增加，需要关注承接")
            assessment["confidence"] *= 0.8
        elif turnover_pattern.get("pattern_type") == "low_turnover":
            key_factors.append("连续缩量，可能一字或换手分歧")
        
        # 2. 强弱因素
        strength_pattern = patterns.get("strength_pattern", {})
        if strength_pattern.get("pattern_type") == "weak_to_strong":
            key_factors.append("该弱不弱视为强")
            assessment["confidence"] *= 1.2
        elif strength_pattern.get("pattern_type") == "strong_continuation":
            key_factors.append("无炸板连续涨停，表现强势")
            assessment["confidence"] *= 1.3
        
        # 3. 量价因素
        volume_pattern = patterns.get("volume_price_pattern", {})
        if volume_pattern.get("pattern_type") == "high_low_high":
            key_factors.append("放量-缩量-放量模式，需要爆量换手")
            assessment["recommendation"] = "爆量换手上板"
        elif volume_pattern.get("pattern_type") == "continuous_low":
            key_factors.append("连续缩量，需要高开缩量晋级")
            assessment["recommendation"] = "高开缩量晋级"
        
        # 4. 连板类型因素
        limit_pattern = patterns.get("limit_up_pattern", {})
        if limit_pattern.get("pattern_type") == "continuous_one_word":
            key_factors.append("连续一字板，强更强")
            assessment["recommendation"] = "继续一字"
        elif limit_pattern.get("pattern_type") == "has_t_word":
            key_factors.append("有T字板，需要换手预期")
            assessment["recommendation"] = "换手预期"
        
        # 综合判断
        if not history_data.empty:
            days_limit_up = len(history_data)
            key_factors.append(f"连续{days_limit_up}天涨停")
            
            # 根据模式给出推荐
            if "继续一字" in assessment["recommendation"]:
                assessment["confidence"] = min(assessment["confidence"] * 1.5, 0.9)
            elif "换手预期" in assessment["recommendation"]:
                assessment["confidence"] = min(assessment["confidence"] * 1.1, 0.8)
        
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
