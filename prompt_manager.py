#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提示词管理器 - 用于优化和更新LLM分析提示词
"""

import json
import os
from typing import Dict, List, Any
from datetime import datetime

class PromptManager:
    """提示词管理器"""
    
    def __init__(self, prompt_file: str = "prompt_library.json"):
        """
        初始化提示词管理器
        
        Args:
            prompt_file: 提示词库文件路径
        """
        self.prompt_file = prompt_file
        self.prompts = self._load_prompts()
        
    def _load_prompts(self) -> Dict[str, Any]:
        """加载提示词库"""
        if os.path.exists(self.prompt_file):
            try:
                with open(self.prompt_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载提示词库失败: {e}")
        
        # 返回默认提示词
        return self._get_default_prompts()
    
    def _get_default_prompts(self) -> Dict[str, Any]:
        """获取默认提示词"""
        return {
            "version": "1.0",
            "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
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
            "experience_rules": [],
            "case_studies": []
        }
    
    def save_prompts(self):
        """保存提示词库"""
        try:
            self.prompts["last_updated"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(self.prompt_file, 'w', encoding='utf-8') as f:
                json.dump(self.prompts, f, ensure_ascii=False, indent=2)
            print(f"提示词库已保存到: {self.prompt_file}")
            return True
        except Exception as e:
            print(f"保存提示词库失败: {e}")
            return False
    
    def add_experience_rule(self, rule: str, source: str = "manual"):
        """添加经验规则"""
        if "experience_rules" not in self.prompts:
            self.prompts["experience_rules"] = []
        
        self.prompts["experience_rules"].append({
            "rule": rule,
            "source": source,
            "added_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        print(f"已添加经验规则: {rule[:50]}...")
        self.save_prompts()
    
    def add_case_study(self, symbol: str, analysis: str, summary: str):
        """添加案例分析"""
        if "case_studies" not in self.prompts:
            self.prompts["case_studies"] = []
        
        self.prompts["case_studies"].append({
            "symbol": symbol,
            "analysis": analysis,
            "summary": summary,
            "added_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        print(f"已添加案例分析: {symbol}")
        self.save_prompts()
    
    def get_enhanced_prompt(self, stock_data: Dict[str, Any]) -> str:
        """获取增强的提示词（包含所有经验规则）"""
        basic_template = self.prompts.get("basic_template", "")
        
        # 构建经验规则部分
        experience_rules = self.prompts.get("experience_rules", [])
        rules_text = "\n【经验规则总结】\n"
        
        if experience_rules:
            for i, rule_data in enumerate(experience_rules[-10:], 1):  # 只取最近10条
                rule = rule_data.get("rule", "")
                source = rule_data.get("source", "")
                rules_text += f"{i}. {rule}"
                if source:
                    rules_text += f" (来源: {source})"
                rules_text += "\n"
        else:
            rules_text += "暂无经验规则，请手动添加。\n"
        
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
        
        # 添加经验规则
        prompt += rules_text
        
        return prompt
    
    def update_from_llm(self, case_text: str, llm_response: str):
        """
        通过LLM从案例中提取经验规则
        
        Args:
            case_text: 案例文本（股票数据）
            llm_response: LLM分析结果
        """
        # 这里可以调用LLM来从案例中提取规则
        # 目前先简单添加整个分析作为案例
        self.add_case_study("从案例提取", case_text, llm_response)
        print("已记录案例，需要手动提取规则")

# 创建全局实例
prompt_manager = PromptManager()

def update_prompt_from_case(symbol: str, stock_data: Dict[str, Any], analysis_result: str):
    """从案例更新提示词"""
    # 将股票数据转换为文本
    case_text = f"股票{symbol}分析案例\n数据:{json.dumps(stock_data, ensure_ascii=False, indent=2)}"
    prompt_manager.update_from_llm(case_text, analysis_result)
    return True

def get_enhanced_prompt_for_stock(stock_data: Dict[str, Any]) -> str:
    """获取股票的增强提示词"""
    return prompt_manager.get_enhanced_prompt(stock_data)
