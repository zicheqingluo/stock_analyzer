#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票分析UI格式化模块
包含所有格式化函数
"""

from typing import Dict, List, Any

def format_analysis_result(analysis: Dict[str, Any]) -> str:
    """格式化分析结果为字符串"""
    if not analysis:
        return "分析结果为空"
    
    lines = []
    lines.append("=" * 60)
    lines.append(f"【个股综合分析】")
    lines.append("=" * 60)
    
    # 综合评级
    lines.append(f"\n【综合评级】")
    lines.append(f"评级: {analysis.get('综合评级', '未知')}")
    lines.append(f"说明: {analysis.get('评级说明', '未知')}")
    lines.append(f"建议: {analysis.get('投资建议', '未知')}")
    
    # 涨停异动分析
    lines.append(f"\n【涨停异动分析】")
    change_info = analysis.get('涨停异动分析', {})
    lines.extend(_format_change_info(change_info))
    
    # 炸板检测
    lines.append(f"\n【炸板检测】")
    炸板_info = analysis.get('炸板检测', {})
    lines.extend(_format_炸板_info(炸板_info))
    
    # 强势股判断
    lines.append(f"\n【强势股判断】")
    strong_info = analysis.get('强势股判断', {})
    lines.extend(_format_strong_info(strong_info))
    
    # 关键指标
    lines.append(f"\n【关键指标总结】")
    key_metrics = analysis.get('关键指标', {})
    lines.extend(_format_key_metrics(key_metrics))
    
    # 系统信息
    lines.append(f"\n【系统信息】")
    lines.append(f"分析时间: {analysis.get('分析时间', '未知')}")
    lines.append(f"查询日期: {analysis.get('查询日期', '未知')}")
    
    return "\n".join(lines)

def _format_change_info(change_info: Dict[str, Any]) -> List[str]:
    """格式化涨停异动信息"""
    lines = []
    
    if change_info.get('是否涨停', False):
        lines.append(f"✓ 今日涨停")
        if change_info.get('涨停时间'):
            lines.append(f"  涨停时间: {change_info['涨停时间']}")
        if change_info.get('涨停信息'):
            lines.append(f"  涨停信息: {change_info['涨停信息']}")
    else:
        lines.append(f"✗ 今日未涨停")
    
    if change_info.get('是否有炸板', False):
        lines.append(f"⚠ 有炸板异动")
        lines.append(f"  炸板次数: {change_info.get('炸板次数', 0)}")
        if change_info.get('炸板时间'):
            times = ', '.join(change_info['炸板时间'])
            lines.append(f"  炸板时间: {times}")
    
    if change_info.get('是否大笔卖出', False):
        lines.append(f"⚠ 有大笔卖出（漏单）")
        lines.append(f"  大笔卖出次数: {change_info.get('大笔卖出次数', 0)}")
        if change_info.get('大笔卖出时间'):
            times = ', '.join(change_info['大笔卖出时间'][:3])
            lines.append(f"  大笔卖出时间: {times}")
    
    return lines

def _format_炸板_info(炸板_info: Dict[str, Any]) -> List[str]:
    """格式化炸板信息"""
    lines = []
    
    if 炸板_info.get('是否在炸板股池', False):
        lines.append(f"⚠ 在炸板股池中")
        lines.append(f"  炸板次数: {炸板_info.get('炸板次数', 0)}")
        if 炸板_info.get('首次封板时间'):
            lines.append(f"  首次封板时间: {炸板_info['首次封板时间']}")
        if 炸板_info.get('涨跌幅'):
            lines.append(f"  涨跌幅: {炸板_info['涨跌幅']}%")
        if 炸板_info.get('炸板详情'):
            lines.append(f"  详情: {炸板_info['炸板详情']}")
    else:
        lines.append(f"✓ 不在炸板股池中")
        # 添加说明：盘中炸板次数与收盘后炸板池的区别
        if 炸板_info.get('炸板次数', 0) > 0:
            lines.append(f"  注: 盘中炸板{炸板_info.get('炸板次数', 0)}次，但收盘未在炸板股池中，可能已回封")
    
    return lines

def _format_strong_info(strong_info: Dict[str, Any]) -> List[str]:
    """格式化强势股信息"""
    lines = []
    
    if strong_info.get('是否在强势股池', False):
        lines.append(f"✓ 在强势股池中")
        if strong_info.get('入选理由'):
            lines.append(f"  入选理由: {strong_info['入选理由']}")
        if strong_info.get('是否新高'):
            lines.append(f"  是否新高: {strong_info['是否新高']}")
        if strong_info.get('涨停统计'):
            lines.append(f"  涨停统计: {strong_info['涨停统计']}")
        if strong_info.get('涨跌幅'):
            lines.append(f"  涨跌幅: {strong_info['涨跌幅']}%")
    else:
        lines.append(f"✗ 不在强势股池中")
    
    return lines

def _format_key_metrics(key_metrics: Dict[str, Any]) -> List[str]:
    """格式化关键指标"""
    lines = []
    
    metrics = [
        ("是否涨停", key_metrics.get('是否涨停', False)),
        ("是否一字板", key_metrics.get('是否一字板', False)),
        ("是否有炸板", key_metrics.get('是否有炸板', False)),
        ("是否漏单", key_metrics.get('是否漏单', False)),
        ("是否强势股", key_metrics.get('是否强势股', False)),
        ("炸板次数", key_metrics.get('炸板次数', 0)),
        ("最终是否涨停", key_metrics.get('最终是否涨停', False)),
        ("几连板", key_metrics.get('几连板', 0))
    ]
    
    for name, value in metrics:
        if isinstance(value, bool):
            display_value = "✓ 是" if value else "✗ 否"
        else:
            display_value = value
        lines.append(f"  {name}: {display_value}")
    
    return lines
