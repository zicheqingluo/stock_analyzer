#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票评级和建议生成模块 - 从stock_monitor_analysis.py拆分出来
"""

from typing import Dict

def generate_rating(is_limit_up: bool, has_open_limit: bool, 
                   has_big_sell: bool, is_in_炸板_pool: bool, 
                   is_in_strong_pool: bool, has_re_limit: bool = False,
                   is_one_word_limit: bool = False) -> Dict[str, str]:
    """生成综合评级"""
    # 如果有炸板但没有重新封板，评级较低
    if has_open_limit and not has_re_limit:
        return {
            'rating': "D-",
            'description': "炸板后未重新封板，走势疲弱"
        }
    
    # 一字板特殊处理
    if is_one_word_limit:
        if not has_big_sell and not is_in_炸板_pool:
            return {
                'rating': "A++",
                'description': "一字板涨停，封板极强，无漏单"
            }
        else:
            return {
                'rating': "A+",
                'description': "一字板涨停，但需关注异动"
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

def generate_investment_advice(is_limit_up: bool, has_open_limit: bool,
                              has_big_sell: bool, is_in_炸板_pool: bool,
                              is_in_strong_pool: bool, has_re_limit: bool = False,
                              is_one_word_limit: bool = False) -> str:
    """生成投资建议"""
    # 如果有炸板但没有重新封板
    if has_open_limit and not has_re_limit:
        return "炸板后未重新封板，走势疲弱，建议回避"
    
    # 一字板特殊建议
    if is_one_word_limit:
        if not has_big_sell and not is_in_炸板_pool:
            return "一字板涨停，封板极强，但需注意次日开板风险，谨慎参与"
        else:
            return "一字板涨停，但存在异动，需密切关注"
    
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
