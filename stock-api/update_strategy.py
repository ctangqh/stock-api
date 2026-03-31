#!/usr/bin/env python3
"""
更新 stock_choose_strategy 表中的策略配置为新的策略条件格式
"""
from data.stock_choose_strategy import StockChooseStrategyORM
from conf.Config import DB_CONFIG
import json

# 新的策略配置示例 - 使用新的原子条件格式
example_strategy = {
    "name": "灵活选股策略",
    "value": {
        "type": "and",
        "conditions": [
            {
                "type": "change_percent",
                "operator": ">=",
                "target_value": 3.0
            },
            {
                "type": "change_percent",
                "operator": "<=",
                "target_value": 6.0
            },
            {
                "type": "market_cap",
                "operator": ">=",
                "target_value": 60.0
            },
            {
                "type": "market_cap",
                "operator": "<=",
                "target_value": 800.0
            },
            {
                "type": "ma",
                "ma_period": 20,
                "operator": "<="
            }
        ]
    },
    "status": "active"
}

# 同时也保留一个旧格式的策略，用于兼容性测试
legacy_strategy = {
    "name": "旧格式兼容策略",
    "value": {
        "filters": [
            {
                "type": "change_percent",
                "params": {
                    "min_change": 3.0,
                    "max_change": 6.0
                }
            },
            {
                "type": "market_cap",
                "params": {
                    "min_cap": 60.0,
                    "max_cap": 800.0
                }
            }
        ]
    },
    "status": "active"
}

print("=== 更新 stock_choose_strategy 表 ===")

orm = StockChooseStrategyORM(DB_CONFIG)

try:
    # 批量插入/更新策略
    strategies_to_update = [example_strategy, legacy_strategy]
    
    result_ids = orm.batch_insert(strategies_to_update)
    
    # 打印策略配置
    print("\n=== 新格式策略配置 ===")
    print(json.dumps(example_strategy['value'], indent=2, ensure_ascii=False))
    
    print("\n=== 旧格式策略配置（兼容） ===")
    print(json.dumps(legacy_strategy['value'], indent=2, ensure_ascii=False))
    
    print(f"\n✓ 策略更新成功！处理了 {len([i for i in result_ids if i])} 个策略")
    
except Exception as e:
    print(f"✗ 更新失败: {e}")
    import traceback
    traceback.print_exc()
finally:
    orm.close()
