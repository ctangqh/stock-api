#!/usr/bin/env python3
"""
验证 stock_choose_strategy 表中的策略
"""
from data.stock_choose_strategy import StockChooseStrategyORM
from conf.Config import DB_CONFIG
import json

print("=== 验证 stock_choose_strategy 表中的策略 ===")

orm = StockChooseStrategyORM(DB_CONFIG)

try:
    # 获取所有激活策略
    strategies = orm.get_all_active()
    print(f"找到 {len(strategies)} 个激活策略\n")
    
    for i, strategy in enumerate(strategies, 1):
        print("="*80)
        print(f"策略 {i}:")
        print(f"  ID: {strategy['id']}")
        print(f"  名称: {strategy['name']}")
        print(f"  状态: {strategy['status']}")
        print(f"  创建时间: {strategy['created_at']}")
        print(f"  更新时间: {strategy['updated_at']}")
        print(f"\n  策略配置 (value):")
        print(json.dumps(strategy['value'], indent=4, ensure_ascii=False))
        print("="*80)
        print()
    
    print("\n✓ 验证完成！")
    
except Exception as e:
    print(f"✗ 验证失败: {e}")
    import traceback
    traceback.print_exc()
finally:
    orm.close()
