#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票LLM智能分析器 - 基于大模型的智能分析
重构为三个功能：
1. 数据收集功能
2. 提示词优化功能  
3. 智能分析功能
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import akshare as ak
import warnings
import json
import os
import sys
warnings.filterwarnings('ignore')

# 添加当前目录到路径，以便导入prompt_manager
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
    
try:
    from prompt_manager import prompt_manager, get_enhanced_prompt_for_stock, update_prompt_from_case
except ImportError:
    # 如果导入失败，创建虚拟函数
    print("提示词管理器模块导入失败，将使用基本功能")
    def get_enhanced_prompt_for_stock(stock_data):
        return "基本提示词"
    def update_prompt_from_case(symbol, stock_data, analysis_result):
        print(f"记录案例: {symbol}")
        return True
    prompt_manager = None

class StockLLMAnalyzer:
    """股票LLM智能分析器"""
    
    def __init__(self, llm_provider: str = "openai"):
        """
        初始化
        
        Args:
            llm_provider: LLM提供商，目前支持 "openai" 或 "local"
        """
        self.llm_provider = llm_provider
        self.experience_prompts = self._load_experience_prompts()
        
    def _load_experience_prompts(self) -> Dict[str, str]:
        """
        加载经验总结的提示词模板
        这些是从之前的分析中总结出来的规则
        """
        prompts = {
            "basic_template": """你是一个资深的股票分析师，擅长分析连板股票走势。
请根据以下股票数据进行分析：

股票代码: {symbol}
股票名称: {name}
分析日期: {analysis_date}

【历史数据】
{history_summary}

【关键指标】
{key_metrics}

【分析要求】
请基于以下经验规则进行分析：
1. 换手率分析：
   - 首板爆量（换手率>15%）是正常的，释放套牢盘
   - 随后换手率逐步降低是缩量走强的信号
   - 连续一字板换手率很低（<3%）是强势表现
   - 换手率逐步增加需要关注承接能力

2. 连板类型分析：
   - 一字板：极强走势，可能继续一字或大高开
   - T字板：有炸板，强度较弱，需要换手预期
   - 普通涨停：正常涨停，需结合其他指标判断

3. 量价关系分析：
   - 爆量->缩量->缩量：标准走强模式
   - 连续缩量：筹码锁定良好，走强信号
   - 放量->缩量：良性换手
   - 连续放量：需要关注承接

4. 强弱转换分析：
   - 大高开+炸板+回封：该弱不弱视为强
   - 连续一字板：强更强
   - 有炸板但能回封：显示承接有力

请给出：
1. 综合结论（一句话总结）
2. 详细分析（分点说明）
3. 明日预期（可能的走势）
4. 操作建议（买入/持有/卖出/观望）
5. 风险提示
""",
            
            "specific_rules": """
【具体经验规则（从历史分析中总结）】
1. 鲁信创投模式：连续多日一字板，换手率逐步增加超过1%，今天需要看承接能否封板
2. 金风科技模式：大高开加速上板，多次炸板后封板，强转弱再转强，本质是该弱不弱视为强
3. 东方明珠模式：连续两天一字板，板上有炸板漏单，连续缩量，要么预期一致走一字，要么换手分歧继续向上
4. 中国一重模式：连续放量上板，今天需要高开缩量晋级
5. 巨力索具模式：连续两个一字，可能会换手，强的话继续一字
6. 中衡设计模式：一板放量，二板加速缩量一字，三板大高开放量，如果真强势三板应该一字板，前面有压力位必须爆量换手释放套牢盘
7. 锋龙股份模式：连续一字，没有炸板，虽有漏单但属于良性的，竞价一字表现了强度，无炸板表现了强度，板上换手有量能承接，综合三点所以锋龙股份强更强
8. 银河电子模式：T字板，本身强度没有一字板那么强，至少说明有炸板才是T字，一路是换手过来，经历了两轮放量换手到缩量但始终没有一字，目前又经历了1天放量两天的缩量T字，今天又是放量的预期
"""
        }
        return prompts
    
    def collect_stock_data(self, symbol: str, days_back: int = 5) -> Dict[str, Any]:
        """
        收集股票的详细数据
        
        Args:
            symbol: 股票代码
            days_back: 回溯天数
            
        Returns:
            股票数据字典
        """
        try:
            # 清理股票代码
            symbol_clean = str(symbol).zfill(6)
            
            # 1. 获取股票基本信息
            stock_name = self._get_stock_name(symbol_clean)
            
            # 2. 获取历史日线数据
            history_data = self._get_detailed_history(symbol_clean, days_back)
            
            # 3. 获取涨停板池数据
            limit_up_data = self._get_limit_up_data(symbol_clean)
            
            # 4. 计算关键指标
            key_metrics = self._calculate_key_metrics(history_data, limit_up_data)
            
            # 5. 生成历史数据摘要
            history_summary = self._generate_history_summary(history_data)
            
            return {
                "symbol": symbol_clean,
                "name": stock_name,
                "analysis_date": datetime.now().strftime('%Y-%m-%d'),
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
            # 尝试从akshare获取
            stock_info = ak.stock_individual_info_em(symbol=symbol)
            if not stock_info.empty:
                for _, row in stock_info.iterrows():
                    if row['item'] == '股票简称':
                        return row['value']
            return symbol
        except:
            return symbol
    
    def _get_detailed_history(self, symbol: str, days_back: int) -> List[Dict[str, Any]]:
        """
        获取详细的日线历史数据 - 修复版
        确保获取最近的实际交易日数据，并处理日期格式
        """
        try:
            # 获取当前日期，但使用股票数据获取模块的查询日期
            # 首先尝试从stock_data_fetcher获取正确的查询日期
            try:
                from stock_data_fetcher import get_query_date
                query_date_str = get_query_date()
                # 将查询日期转换为datetime对象
                query_date = datetime.strptime(query_date_str, '%Y%m%d')
                print(f"使用股票数据获取模块的查询日期: {query_date_str}")
            except:
                # 如果失败，使用当前日期
                query_date = datetime.now()
                print(f"使用当前日期: {query_date.strftime('%Y%m%d')}")
            
            # 计算开始日期（days_back个交易日之前）
            # 由于交易日可能不连续，我们多取一些天数
            start_date = query_date - timedelta(days=days_back * 2)
            
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
            
            # 确保有date列
            if 'date' not in df.columns:
                print("错误: 数据中没有日期列")
                return []
            
            # 按日期排序（最近的在前）
            df = df.sort_values('date', ascending=False)
            
            # 只保留最近days_back天的数据
            df = df.head(days_back)
            
            # 检查日期是否合理
            if len(df) > 0:
                # 确保日期不是未来日期
                current_date = datetime.now()
                for date_str in df['date']:
                    try:
                        # 尝试解析日期字符串
                        if isinstance(date_str, str):
                            # 处理不同的日期格式
                            if '-' in date_str:
                                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                            else:
                                date_obj = datetime.strptime(date_str, '%Y%m%d')
                            
                            # 如果日期在未来，可能是数据源问题
                            if date_obj > current_date:
                                print(f"警告: 发现未来日期 {date_str}，可能是数据源问题")
                    except:
                        pass
                
                print(f"获取到的历史数据日期范围: {df['date'].iloc[0] if len(df) > 0 else '无数据'} 到 {df['date'].iloc[-1] if len(df) > 0 else '无数据'}")
            
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
            import traceback
            traceback.print_exc()
            return []
    
    def _get_limit_up_data(self, symbol: str) -> Dict[str, Any]:
        """
        获取涨停板池相关数据
        """
        try:
            current_date = datetime.now().strftime('%Y%m%d')
            
            # 获取今天涨停板池数据
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
        计算关键指标 - 修复版
        确保指标计算准确且一致
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
        
        # 判断涨停类型
        limit_types = []
        for day in recent_data:
            if day.get('is_limit_up', False):
                limit_types.append(day.get('limit_type', '普通涨停'))
            else:
                limit_types.append('非涨停')
        
        # 计算量价关系
        volume_trend = "unknown"
        if len(turnover_rates) >= 2:
            # 比较最近两天的换手率
            if turnover_rates[0] < turnover_rates[1]:
                volume_trend = "缩量"
            elif turnover_rates[0] > turnover_rates[1]:
                volume_trend = "放量"
            else:
                volume_trend = "平量"
        
        # 获取最近涨停类型（从涨停数据中获取，而不是从历史数据）
        recent_limit_type = "非涨停"
        if limit_up_data.get('in_today_pool', False):
            # 如果今天在涨停板池中，尝试获取涨停类型
            if history_data and history_data[0].get('is_limit_up', False):
                recent_limit_type = history_data[0].get('limit_type', '普通涨停')
            else:
                recent_limit_type = "普通涨停"  # 默认
        
        # 确保数据一致性
        streak_days = limit_up_data.get('streak_days', 0)
        today_in_pool = limit_up_data.get('in_today_pool', False)
        
        # 如果显示连续涨停但最近涨停天数为0，进行调整
        if streak_days > 0 and limit_up_days == 0:
            # 尝试从历史数据中重新计算
            all_limit_up_days = sum(1 for day in history_data if day.get('is_limit_up', False))
            if all_limit_up_days > 0:
                limit_up_days = min(all_limit_up_days, recent_days)
        
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
        for i, day in enumerate(history_data[:5]):  # 最多显示5天
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
    
    def analyze_with_llm(self, symbol: str, use_local: bool = False, 
                        update_prompt: bool = False) -> Dict[str, Any]:
        """
        使用LLM分析股票 - 重构版
        
        Args:
            symbol: 股票代码
            use_local: 是否使用本地模拟（当没有真实LLM API时）
            update_prompt: 是否将本次分析用于更新提示词
            
        Returns:
            分析结果
        """
        try:
            # 1. 数据收集功能
            print(f"【功能1】正在收集 {symbol} 的数据...")
            stock_data = self.collect_stock_data(symbol)
            
            if "error" in stock_data:
                return {"error": stock_data["error"]}
            
            # 2. 构建增强提示词（结合经验规则）
            print(f"【功能2】构建增强提示词...")
            if prompt_manager:
                prompt = get_enhanced_prompt_for_stock(stock_data)
            else:
                prompt = self._build_llm_prompt(stock_data)
            
            # 3. 智能分析功能
            print(f"【功能3】正在调用大模型进行智能分析...")
            if use_local or self.llm_provider == "local":
                llm_response = self._call_local_llm(prompt)
            else:
                llm_response = self._call_external_llm(prompt)
            
            # 4. 解析结果
            analysis_result = self._parse_llm_response(llm_response)
            
            # 5. 如果启用，更新提示词库
            if update_prompt and prompt_manager:
                print(f"【功能2扩展】将本次分析用于优化提示词...")
                update_prompt_from_case(symbol, stock_data, llm_response)
            
            # 6. 合并结果
            result = {
                **stock_data,
                "llm_prompt": prompt[:500] + "..." if len(prompt) > 500 else prompt,  # 截断长提示词
                "llm_response": llm_response,
                "analysis": analysis_result,
                "analysis_type": "enhanced" if prompt_manager else "basic"
            }
            
            return result
            
        except Exception as e:
            print(f"LLM分析失败: {e}")
            import traceback
            traceback.print_exc()
            return {"error": f"LLM分析失败: {str(e)}"}
    
    def _build_llm_prompt(self, stock_data: Dict[str, Any]) -> str:
        """构建LLM提示词"""
        basic_template = self.experience_prompts["basic_template"]
        specific_rules = self.experience_prompts["specific_rules"]
        
        # 准备数据
        symbol = stock_data.get("symbol", "")
        name = stock_data.get("name", symbol)
        analysis_date = stock_data.get("analysis_date", "")
        history_summary = stock_data.get("history_summary", "")
        key_metrics = stock_data.get("key_metrics", {})
        
        # 格式化关键指标
        key_metrics_str = "\n".join([f"{k}: {v}" for k, v in key_metrics.items()])
        
        # 填充模板
        prompt = basic_template.format(
            symbol=symbol,
            name=name,
            analysis_date=analysis_date,
            history_summary=history_summary,
            key_metrics=key_metrics_str
        )
        
        # 添加具体规则
        prompt += specific_rules
        
        return prompt
    
    def _call_local_llm(self, prompt: str) -> str:
        """
        本地模拟LLM调用（当没有真实API时）
        使用规则引擎生成分析
        """
        # 这是一个简化的模拟版本
        # 在实际使用中，应该替换为真实的LLM API调用
        
        # 检查是否是量化策略生成请求
        if "量化策略" in prompt or "交易策略" in prompt or "买入条件" in prompt:
            return self._generate_quant_strategy(prompt)
        
        # 解析prompt中的关键信息
        lines = prompt.split('\n')
        symbol = ""
        for line in lines:
            if "股票代码:" in line:
                symbol = line.split(":")[1].strip()
                break
        
        # 基于规则的简单分析
        analysis = f"""
基于数据对股票 {symbol} 的分析：

【综合结论】
该股票近期表现强势，符合缩量走强模式。

【详细分析】
1. 换手率分析：换手率逐步降低，显示筹码锁定良好
2. 连板类型：近期有一字板，表现极强
3. 量价关系：符合爆量->缩量->缩量的标准走强模式
4. 强弱转换：连续涨停，无炸板，表现强势

【明日预期】
大概率继续走强，可能继续一字板或大高开快速涨停

【操作建议】
如果持有可继续持有，如果未持有可考虑在合适时机参与

【风险提示】
注意市场整体风险，避免追高
"""
        
        return analysis
    
    def _generate_quant_strategy(self, prompt: str) -> str:
        """
        生成量化策略的专门方法
        """
        # 解析用户需求
        user_input = ""
        for line in prompt.split('\n'):
            if "用户的新需求：" in line:
                user_input = line.split("：")[1].strip()
                break
        
        # 基于用户需求生成策略
        strategy_name = "智能量化策略"
        if "涨停" in user_input:
            strategy_name = "涨停板优化策略"
        elif "连板" in user_input:
            strategy_name = "连板股策略"
        elif "回调" in user_input:
            strategy_name = "回调买入策略"
        elif "风险" in user_input:
            strategy_name = "风险控制策略"
        
        strategy = f"""
【策略名称】
{strategy_name}

【策略描述】
基于用户需求"{user_input}"生成的量化交易策略，专注于中国A股市场的短线交易机会。

【核心逻辑】
1. 结合技术指标与市场情绪进行综合判断
2. 利用涨停板、成交量、换手率等多维度数据
3. 动态调整买入卖出条件以适应市场变化

【买入条件】
1. 股票当日涨停或接近涨停（涨幅>9.5%）
2. 成交量较前一日放大1.5倍以上
3. 换手率在5%-20%之间，显示活跃但不过度
4. 股价突破关键压力位或创近期新高
5. 市场整体情绪积极，板块有联动效应

【卖出条件】
1. 止损条件：股价跌破买入价5%立即止损
2. 止盈条件：盈利达到15%考虑部分止盈，20%全部止盈
3. 时间止损：持有超过3个交易日未达目标考虑减仓
4. 技术止损：出现放量滞涨或跌破重要均线

【风险控制】
1. 单只股票仓位不超过总资金的20%
2. 每日最大亏损不超过总资金的2%
3. 避免在重大利空消息发布时交易
4. 关注市场整体风险，大盘下跌时降低仓位
5. 设置硬性止损线，严格执行纪律

【适用市场环境】
1. 适用于震荡市和牛市初期
2. 在单边下跌市中应谨慎使用或暂停
3. 最适合中小盘活跃股
4. 需要实时数据支持和快速执行能力

【策略优化建议】
1. 定期回测策略表现，根据市场变化调整参数
2. 结合基本面分析提高胜率
3. 关注政策面和资金面变化
4. 建立策略组合，分散风险
"""
        
        return strategy
    
    def _call_external_llm(self, prompt: str) -> str:
        """
        调用外部LLM API
        这里需要根据实际的LLM提供商进行实现
        """
        # 这里是一个示例，实际使用时需要替换为真实的API调用
        # 例如：OpenAI API, Claude API, 本地部署的LLM等
        
        print("注意：当前使用本地模拟LLM，如需真实LLM请配置API")
        return self._call_local_llm(prompt)
    
    def _parse_llm_response(self, response: str) -> Dict[str, str]:
        """
        解析LLM响应，提取结构化信息
        """
        # 简单的解析逻辑
        sections = {
            "综合结论": "",
            "详细分析": "",
            "明日预期": "",
            "操作建议": "",
            "风险提示": ""
        }
        
        current_section = None
        current_content = []
        
        for line in response.split('\n'):
            line = line.strip()
            
            # 检查是否是新的章节
            for section in sections.keys():
                if line.startswith(section) or f"【{section}】" in line:
                    if current_section:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = section
                    current_content = []
                    break
            else:
                if current_section and line:
                    current_content.append(line)
        
        # 处理最后一个章节
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def generate_quant_strategy(self, user_input: str, existing_strategies: List[Dict] = None) -> Dict[str, Any]:
        """
        专门生成量化策略的方法
        
        Args:
            user_input: 用户输入的优化想法
            existing_strategies: 现有策略列表
            
        Returns:
            生成的策略字典
        """
        try:
            # 构建提示词
            prompt = f"""
用户需求：{user_input}

请生成一个专业的量化交易策略，专注于中国A股市场。
要求策略具体、可执行、可量化。
"""
            
            # 调用LLM
            if self.llm_provider == "local":
                strategy_content = self._call_local_llm(prompt)
            else:
                strategy_content = self._call_external_llm(prompt)
            
            # 创建策略对象
            from datetime import datetime
            strategy = {
                "name": f"量化策略-{datetime.now().strftime('%Y%m%d-%H%M')}",
                "description": f"基于用户需求生成: {user_input[:50]}...",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "content": strategy_content,
                "user_input": user_input,
                "source": "llm_generated"
            }
            
            return strategy
            
        except Exception as e:
            print(f"生成量化策略失败: {e}")
            # 返回一个简单的策略
            return {
                "name": "基础策略",
                "description": "生成失败时的默认策略",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "content": "策略生成失败，请重试。",
                "user_input": user_input,
                "source": "error_fallback"
            }
    
    def save_experience(self, symbol: str, analysis: str, tags: List[str] = None):
        """
        保存分析经验到本地文件
        """
        try:
            experience_dir = "stock_experiences"
            if not os.path.exists(experience_dir):
                os.makedirs(experience_dir)
            
            filename = f"{experience_dir}/experience_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            experience_data = {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "analysis": analysis,
                "tags": tags or [],
                "source": "llm_analysis"
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(experience_data, f, ensure_ascii=False, indent=2)
            
            print(f"经验已保存到: {filename}")
            
        except Exception as e:
            print(f"保存经验失败: {e}")


# 创建全局实例
llm_analyzer = StockLLMAnalyzer()

def analyze_stock_with_llm(symbol: str, use_local: bool = True) -> Dict[str, Any]:
    """使用LLM分析股票的快捷函数"""
    return llm_analyzer.analyze_with_llm(symbol, use_local)

def collect_stock_data(symbol: str) -> Dict[str, Any]:
    """收集股票数据的快捷函数"""
    return llm_analyzer.collect_stock_data(symbol)

if __name__ == "__main__":
    # 测试代码
    print("股票LLM分析器测试")
    print("=" * 60)
    
    # 测试股票
    test_symbol = "002115"
    
    print(f"\n测试股票: {test_symbol}")
    
    # 收集数据
    print("1. 收集数据...")
    data = collect_stock_data(test_symbol)
    
    if "error" in data:
        print(f"数据收集失败: {data['error']}")
    else:
        print(f"数据收集成功: {data['name']}")
        print(f"历史数据天数: {len(data['history_data'])}")
        print(f"关键指标: {data['key_metrics']}")
    
    # LLM分析
    print("\n2. LLM分析...")
    result = analyze_stock_with_llm(test_symbol, use_local=True)
    
    if "error" in result:
        print(f"分析失败: {result['error']}")
    else:
        print("\n【LLM分析结果】")
        analysis = result.get("analysis", {})
        for section, content in analysis.items():
            if content:
                print(f"\n{section}:")
                print(content)
        
        # 保存经验
        llm_analyzer.save_experience(test_symbol, result.get("llm_response", ""))
