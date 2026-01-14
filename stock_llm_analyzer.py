#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票LLM智能分析器 - 精简版
整合数据收集、LLM核心和量化策略功能
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 导入新模块
try:
    from stock_llm_core import StockLLMCore
    from stock_data_collector import StockDataCollector
except ImportError:
    print("警告: 无法导入核心模块，某些功能可能不可用")
    StockLLMCore = None
    StockDataCollector = None

# 尝试导入提示词管理器
try:
    from prompt_manager import prompt_manager, get_enhanced_prompt_for_stock, update_prompt_from_case
except ImportError:
    print("提示词管理器模块导入失败，将使用基本功能")
    def get_enhanced_prompt_for_stock(stock_data):
        return "基本提示词"
    def update_prompt_from_case(symbol, stock_data, analysis_result):
        print(f"记录案例: {symbol}")
        return True
    prompt_manager = None

class StockLLMAnalyzer:
    """股票LLM智能分析器（精简版）"""
    
    def __init__(self, llm_provider: str = "local", api_key: str = None, base_url: str = None):
        """
        初始化
        
        Args:
            llm_provider: LLM提供商
            api_key: API密钥
            base_url: API基础URL
        """
        self.llm_provider = llm_provider
        self.api_key = api_key
        self.base_url = base_url
        
        # 初始化核心模块
        self.llm_core = StockLLMCore(llm_provider, api_key, base_url) if StockLLMCore else None
        self.data_collector = StockDataCollector() if StockDataCollector else None
        
        # 加载经验提示词
        self.experience_prompts = self._load_experience_prompts()
    
    def _load_experience_prompts(self) -> Dict[str, str]:
        """加载经验提示词"""
        return {
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
    
    def collect_stock_data(self, symbol: str, days_back: int = 5) -> Dict[str, Any]:
        """
        收集股票数据
        
        Args:
            symbol: 股票代码
            days_back: 回溯天数
            
        Returns:
            股票数据
        """
        if not self.data_collector:
            return {"error": "数据收集器未初始化"}
        
        return self.data_collector.collect_stock_data(symbol, days_back)
    
    def analyze_with_llm(self, symbol: str, use_local: bool = False, 
                        update_prompt: bool = False) -> Dict[str, Any]:
        """
        使用LLM分析股票
        
        Args:
            symbol: 股票代码
            use_local: 是否使用本地模拟
            update_prompt: 是否更新提示词
            
        Returns:
            分析结果
        """
        try:
            # 1. 数据收集功能
            print(f"【功能1】正在收集 {symbol} 的数据...")
            stock_data = self.collect_stock_data(symbol)
            
            if "error" in stock_data:
                return {"error": stock_data["error"]}
            
            # 2. 构建增强提示词
            print(f"【功能2】构建增强提示词...")
            if prompt_manager:
                prompt = get_enhanced_prompt_for_stock(stock_data)
            else:
                prompt = self._build_llm_prompt(stock_data)
            
            # 3. 智能分析功能
            print(f"【功能3】正在调用大模型进行智能分析...")
            if not self.llm_core:
                return {"error": "LLM核心模块未初始化"}
            
            # 调用LLM API，不使用本地模拟
            llm_response = self.llm_core.call_llm(prompt, use_local=False)
            
            # 4. 解析结果
            analysis_result = self.llm_core.parse_llm_response(llm_response)
            
            # 5. 更新提示词库
            if update_prompt and prompt_manager:
                print(f"【功能2扩展】将本次分析用于优化提示词...")
                update_prompt_from_case(symbol, stock_data, llm_response)
            
            # 6. 合并结果
            result = {
                **stock_data,
                "llm_prompt": prompt[:500] + "..." if len(prompt) > 500 else prompt,
                "llm_response": llm_response,
                "analysis": analysis_result,
                "analysis_type": "enhanced" if prompt_manager else "basic"
            }
            
            return result
            
        except Exception as e:
            print(f"LLM分析失败: {e}")
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
    
    def generate_quant_strategy(self, stock_symbol: str, user_input: str, 
                               days_back: int = 5) -> Dict[str, Any]:
        """
        生成量化策略 - 增强版
        
        Args:
            stock_symbol: 股票代码
            user_input: 用户输入的分析需求
            days_back: 回溯天数
            
        Returns:
            量化策略
        """
        try:
            # 1. 收集股票数据
            print(f"【量化策略】收集股票 {stock_symbol} 的数据...")
            stock_data = self.collect_stock_data(stock_symbol, days_back)
            
            if "error" in stock_data:
                return {"error": stock_data["error"]}
            
            # 2. 构建量化策略提示词
            print(f"【量化策略】构建提示词...")
            if not self.llm_core:
                return {"error": "LLM核心模块未初始化"}
            
            prompt = self.llm_core.generate_quant_strategy_prompt(stock_data, user_input)
            
            # 3. 调用LLM生成策略
            print(f"【量化策略】调用LLM生成策略...")
            # 调用LLM API，不使用本地模拟
            llm_response = self.llm_core.call_llm(prompt, use_local=False)
            
            # 4. 创建策略对象
            strategy = {
                "name": f"量化策略-{stock_symbol}-{datetime.now().strftime('%Y%m%d-%H%M')}",
                "description": f"基于股票{stock_symbol}数据和用户需求生成的量化策略",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "content": llm_response,
                "stock_symbol": stock_symbol,
                "user_input": user_input,
                "stock_data_summary": {
                    "symbol": stock_data.get("symbol"),
                    "name": stock_data.get("name"),
                    "key_metrics": stock_data.get("key_metrics", {})
                },
                "source": "llm_generated"
            }
            
            # 5. 保存策略到本地
            self._save_quant_strategy(strategy)
            
            return strategy
            
        except Exception as e:
            print(f"生成量化策略失败: {e}")
            return {
                "name": "基础策略",
                "description": "生成失败时的默认策略",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "content": "策略生成失败，请重试。",
                "user_input": user_input,
                "source": "error_fallback"
            }
    
    def _save_quant_strategy(self, strategy: Dict[str, Any]):
        """保存量化策略到本地文件"""
        try:
            strategy_dir = "quant_strategies"
            if not os.path.exists(strategy_dir):
                os.makedirs(strategy_dir)
            
            filename = f"{strategy_dir}/strategy_{strategy['name']}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(strategy, f, ensure_ascii=False, indent=2)
            
            print(f"量化策略已保存到: {filename}")
            
        except Exception as e:
            print(f"保存量化策略失败: {e}")
    
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
def create_llm_analyzer():
    """创建LLM分析器实例"""
    
    # 从环境变量获取配置
    llm_provider = os.environ.get("LLM_PROVIDER", "deepseek").lower()
    api_key = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("LLM_BASE_URL")
    
    # 检查API密钥
    if not api_key:
        print("错误: 未设置API密钥")
        print("请设置环境变量 DEEPSEEK_API_KEY 或 OPENAI_API_KEY")
        print("例如: export DEEPSEEK_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    if llm_provider == "deepseek":
        print(f"使用DeepSeek作为LLM提供商")
        return StockLLMAnalyzer(
            llm_provider="deepseek",
            api_key=api_key,
            base_url=base_url or "https://api.deepseek.com"
        )
    elif llm_provider == "openai":
        print(f"使用OpenAI作为LLM提供商")
        return StockLLMAnalyzer(
            llm_provider="openai",
            api_key=api_key,
            base_url=base_url or "https://api.openai.com/v1"
        )
    else:
        print(f"错误: 不支持的LLM提供商: {llm_provider}")
        print("支持的提供商: deepseek, openai")
        sys.exit(1)

llm_analyzer = create_llm_analyzer()

def analyze_stock_with_llm(symbol: str, use_local: bool = True) -> Dict[str, Any]:
    """使用LLM分析股票的快捷函数"""
    return llm_analyzer.analyze_with_llm(symbol, use_local)

def collect_stock_data(symbol: str) -> Dict[str, Any]:
    """收集股票数据的快捷函数"""
    return llm_analyzer.collect_stock_data(symbol)

def generate_quant_strategy(stock_symbol: str, user_input: str) -> Dict[str, Any]:
    """生成量化策略的快捷函数"""
    return llm_analyzer.generate_quant_strategy(stock_symbol, user_input)

if __name__ == "__main__":
    # 测试代码
    print("股票LLM分析器测试")
    print("=" * 60)
    
    # 显示配置信息
    print("\n当前LLM配置:")
    print(f"提供商: {llm_analyzer.llm_provider}")
    
    # 检查API密钥
    api_key = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("错误: 未设置API密钥")
        print("请设置环境变量 DEEPSEEK_API_KEY 或 OPENAI_API_KEY")
        print("例如: export DEEPSEEK_API_KEY='your-api-key-here'")
        sys.exit(1)
    
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
    
    # 测试量化策略生成
    print("\n2. 测试量化策略生成...")
    user_input = "请生成一个基于涨停板的量化策略，要求考虑换手率和成交量"
    strategy = generate_quant_strategy(test_symbol, user_input)
    
    if "error" in strategy:
        print(f"策略生成失败: {strategy['error']}")
    else:
        print(f"策略生成成功: {strategy['name']}")
        print(f"策略描述: {strategy['description']}")
