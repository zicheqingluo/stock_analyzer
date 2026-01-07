#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票名称解析模块 - 根据股票名称查询股票代码
使用akshare的stock_zh_a_spot_em接口
"""

import re
import pandas as pd
from typing import Optional, List, Tuple, Dict
import json
import os
import time
import akshare as ak


class StockNameResolver:
    """股票名称解析器 - 基于akshare接口"""
    
    def __init__(self, cache_days: int = 1):
        """
        初始化解析器
        
        Args:
            cache_days: 缓存天数
        """
        self.cache_file = "stock_name_cache.json"
        self.cache_days = cache_days
        self.stock_dict = {}  # 代码->名称映射
        self.name_to_codes = {}  # 名称->代码列表映射
        self._init_cache()
    
    def _init_cache(self):
        """初始化缓存"""
        # 检查缓存文件是否存在且未过期
        if self._is_cache_valid():
            self._load_from_cache()
        else:
            self._refresh_from_akshare()
    
    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        if not os.path.exists(self.cache_file):
            return False
        
        try:
            # 检查文件修改时间
            mtime = os.path.getmtime(self.cache_file)
            cache_age_days = (time.time() - mtime) / (24 * 3600)
            return cache_age_days <= self.cache_days
        except:
            return False
    
    def _load_from_cache(self):
        """从缓存加载数据"""
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            self.stock_dict = cache_data.get('stock_dict', {})
            self.name_to_codes = cache_data.get('name_to_codes', {})
            print(f"已加载缓存数据: {len(self.stock_dict)} 只股票")
        except Exception as e:
            print(f"加载缓存失败: {e}")
            self._refresh_from_akshare()
    
    def _save_to_cache(self):
        """保存数据到缓存"""
        try:
            cache_data = {
                'stock_dict': self.stock_dict,
                'name_to_codes': self.name_to_codes,
                'timestamp': time.time()
            }
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            print(f"已保存缓存数据: {len(self.stock_dict)} 只股票")
        except Exception as e:
            print(f"保存缓存失败: {e}")
    
    def _refresh_from_akshare(self):
        """从akshare获取最新股票数据"""
        try:
            print("正在从akshare获取A股实时行情数据...")
            
            # 使用stock_zh_a_spot_em接口获取所有A股实时数据
            df = ak.stock_zh_a_spot_em()
            
            if df is None or df.empty:
                print("获取数据失败，尝试备用接口...")
                self._get_from_backup()
                return
            
            # 确保必要的列存在
            required_cols = ['代码', '名称']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                print(f"数据列缺失: {missing_cols}")
                self._get_from_backup()
                return
            
            # 构建映射关系
            self.stock_dict.clear()
            self.name_to_codes.clear()
            
            for _, row in df.iterrows():
                code = str(row['代码']).strip()
                name = str(row['名称']).strip()
                
                if code and name and name != 'nan' and code != 'nan':
                    # 标准化代码
                    code = self._normalize_code(code)
                    
                    # 添加到代码->名称映射
                    self.stock_dict[code] = name
                    
                    # 添加到名称->代码映射
                    if name not in self.name_to_codes:
                        self.name_to_codes[name] = []
                    
                    # 避免重复添加
                    if code not in self.name_to_codes[name]:
                        self.name_to_codes[name].append(code)
            
            print(f"成功获取 {len(self.stock_dict)} 只股票数据")
            self._save_to_cache()
            
        except Exception as e:
            print(f"从akshare获取数据失败: {e}")
            self._get_from_backup()
    
    def _get_from_backup(self):
        """备用数据获取方法"""
        try:
            print("尝试备用数据源...")
            
            # 尝试其他接口
            df = ak.stock_info_a_code_name()
            
            if df is not None and not df.empty:
                self.stock_dict.clear()
                self.name_to_codes.clear()
                
                for _, row in df.iterrows():
                    code = str(row['code']).strip()
                    name = str(row['name']).strip()
                    
                    if code and name:
                        code = self._normalize_code(code)
                        self.stock_dict[code] = name
                        
                        if name not in self.name_to_codes:
                            self.name_to_codes[name] = []
                        if code not in self.name_to_codes[name]:
                            self.name_to_codes[name].append(code)
                
                print(f"从备用接口获取 {len(self.stock_dict)} 只股票数据")
                self._save_to_cache()
                return
            
            # 如果都失败，使用本地缓存
            self._create_local_cache()
            
        except Exception as e:
            print(f"备用数据源也失败: {e}")
            self._create_local_cache()
    
    def _create_local_cache(self):
        """创建本地缓存（最后备选）"""
        print("使用本地缓存数据...")
        common_stocks = {
            "000001": "平安银行",
            "000002": "万科A",
            "000858": "五粮液",
            "002415": "海康威视",
            "002475": "立讯精密",
            "300059": "东方财富",
            "300750": "宁德时代",
            "600036": "招商银行",
            "600519": "贵州茅台",
            "601318": "中国平安",
            "603259": "药明康德",
            "688981": "中芯国际"
        }
        
        self.stock_dict = common_stocks
        self.name_to_codes = {}
        
        for code, name in common_stocks.items():
            if name not in self.name_to_codes:
                self.name_to_codes[name] = []
            self.name_to_codes[name].append(code)
    
    def _normalize_code(self, code: str) -> str:
        """标准化股票代码格式"""
        code = str(code).strip()
        
        # 去掉交易所后缀
        if '.' in code:
            code = code.split('.')[0]
        
        # 补齐6位
        if len(code) < 6:
            code = code.zfill(6)
        
        return code
    
    def search_by_name(self, name: str, max_results: int = 10) -> List[Tuple[str, str]]:
        """
        根据股票名称搜索股票
        
        Args:
            name: 股票名称（支持模糊搜索）
            max_results: 最大返回结果数
            
        Returns:
            List[Tuple[代码, 名称]]
        """
        name = name.strip()
        if not name or not self.name_to_codes:
            return []
        
        results = []
        
        # 1. 精确匹配
        if name in self.name_to_codes:
            for code in self.name_to_codes[name]:
                stock_name = self.stock_dict.get(code, name)
                results.append((code, stock_name))
        
        # 2. 包含匹配（如果精确匹配没有或结果较少）
        if len(results) < max_results:
            for stock_name, codes in self.name_to_codes.items():
                if name in stock_name:
                    for code in codes:
                        if (code, stock_name) not in results:
                            results.append((code, stock_name))
        
        # 3. 拼音首字母匹配（如果结果还不够）
        if len(results) < max_results and len(name) <= 4:
            for stock_name, codes in self.name_to_codes.items():
                if self._match_pinyin_initials(name, stock_name):
                    for code in codes:
                        if (code, stock_name) not in results:
                            results.append((code, stock_name))
        
        return results[:max_results]
    
    def _match_pinyin_initials(self, input_str: str, stock_name: str) -> bool:
        """拼音首字母匹配"""
        try:
            # 简单实现：取每个字的首字母
            initials = ''.join([word[0] for word in stock_name])
            return input_str.lower() in initials.lower()
        except:
            return False
    
    def get_stock_code(self, name: str) -> Optional[str]:
        """根据股票名称获取股票代码"""
        results = self.search_by_name(name, max_results=1)
        if results:
            return results[0][0]
        return None
    
    def get_stock_name(self, code: str) -> Optional[str]:
        """根据股票代码获取股票名称"""
        code = self._normalize_code(code)
        return self.stock_dict.get(code)
    
    def get_all_stocks(self) -> List[Tuple[str, str]]:
        """获取所有股票列表"""
        return [(code, name) for code, name in self.stock_dict.items()]
    
    def interactive_search(self, name: str) -> Optional[str]:
        """交互式搜索股票"""
        results = self.search_by_name(name, max_results=20)
        
        if not results:
            print(f"未找到名称包含 '{name}' 的股票")
            return None
        
        if len(results) == 1:
            code, stock_name = results[0]
            print(f"找到股票: {stock_name} ({code})")
            return code
        
        # 显示多个结果让用户选择
        print(f"\n找到 {len(results)} 个相关股票:")
        print("-" * 40)
        for i, (code, stock_name) in enumerate(results, 1):
            print(f"{i:2d}. {stock_name:10s} ({code})")
        
        while True:
            choice = input("\n请输入序号选择股票 (输入q退出): ").strip()
            if choice.lower() == 'q':
                return None
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(results):
                    code, stock_name = results[idx]
                    print(f"已选择: {stock_name} ({code})")
                    return code
                else:
                    print(f"序号无效，请输入 1-{len(results)} 之间的数字")
            except ValueError:
                print("请输入有效的数字")


# 创建全局解析器实例
resolver = StockNameResolver()


# 快捷函数
def get_stock_code_by_name(name: str) -> Optional[str]:
    return resolver.get_stock_code(name)


def search_stocks_by_name(name: str, max_results: int = 10) -> List[Tuple[str, str]]:
    return resolver.search_by_name(name, max_results)


def interactive_select_stock(name: str) -> Optional[str]:
    return resolver.interactive_search(name)


def get_stock_name_by_code(code: str) -> Optional[str]:
    return resolver.get_stock_name(code)


if __name__ == "__main__":
    # 测试代码
    test_cases = [
        "茅台",  # 模糊搜索
        "贵州茅台",  # 精确搜索
        "银行",  # 行业搜索
        "平安",  # 多结果测试
    ]
    
    for test_name in test_cases:
        print(f"\n搜索 '{test_name}':")
        results = search_stocks_by_name(test_name, max_results=5)
        for i, (code, name) in enumerate(results, 1):
            print(f"  {i}. {code}: {name}")