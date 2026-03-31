# Job 使用方法

## 目录
- [ScanJob (股票筛选任务)](#scanjob-股票筛选任务)
- [策略条件模块](#策略条件模块)

---

## ScanJob (股票筛选任务)

### 概述
`ScanJob` 是一个灵活的股票筛选任务框架，支持通过 JSON 配置定义多个过滤器组合来筛选股票。

### 位置
`/app/stock-api/job/scan/run.py`

### 核心类与函数

#### 1. ScanJob 类
主要的股票筛选任务类。

**方法**：
- `register_filter(name, filter_func)`: 注册自定义过滤器
- `get_registered_filters()`: 获取已注册的过滤器列表
- `run(strategy_config, stocks, scan_date, **kwargs)`: 执行筛选任务

#### 2. get_scan_job()
获取单例的 ScanJob 实例。

#### 3. run_scan_job(strategy_config, stocks, scan_date, **kwargs)
便捷函数，直接执行筛选任务。

### 使用示例

```python
from datetime import date
from job.scan.run import run_scan_job

# 策略配置
strategy_config = {
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
}

# 执行筛选
result = run_scan_job(
    strategy_config,
    stocks,  # 股票数据列表
    date(2026, 3, 30),
    stock_market_caps=stock_market_caps  # 可选，市值数据
)
```

### 内置过滤器

| 过滤器类型 | 说明 | 参数 |
|-----------|------|------|
| `change_percent` | 涨跌幅筛选 | `min_change`, `max_change` |
| `market_cap` | 市值筛选 | `min_cap`, `max_cap` |
| `ma` | 均线筛选 | `ma_period`, `operator` |
| `continuous_up` | 连续上涨筛选 | `days` |

---

## 策略条件模块

### 概述
策略条件模块提供了更灵活的条件组合方式，支持通过 AND/OR 逻辑组合多个原子条件。

### 位置
`/app/stock-api/strategy/conditions/`

### 核心条件类

#### 1. 基础条件
- `ChangePercentCondition`: 涨跌幅条件
- `MarketCapCondition`: 市值条件
- `MACondition`: 均线条件
- `ContinuousRiseCondition`: 连续上涨条件

#### 2. 组合条件
- `AndCompositeCondition`: AND 逻辑组合（所有条件都满足）
- `OrCompositeCondition`: OR 逻辑组合（至少一个条件满足）

### 使用示例

#### 单个条件
```python
from strategy.conditions import ChangePercentCondition, Operator

# 涨跌幅 >= 3.0%
cond = ChangePercentCondition(Operator.GREATER_OR_EQUAL, 3.0)
```

#### 组合条件 (AND)
```python
from strategy.conditions import (
    ChangePercentCondition,
    MarketCapCondition,
    AndCompositeCondition,
    Operator
)

# 3.0% <= 涨跌幅 <= 6.0% 且 200亿 <= 市值 <= 350亿
cond1 = ChangePercentCondition(Operator.GREATER_OR_EQUAL, 3.0)
cond2 = ChangePercentCondition(Operator.LESS_OR_EQUAL, 6.0)
cond3 = MarketCapCondition(Operator.GREATER_OR_EQUAL, 200.0)
cond4 = MarketCapCondition(Operator.LESS_OR_EQUAL, 350.0)

and_cond = AndCompositeCondition([cond1, cond2, cond3, cond4])
```

#### JSON 配置示例
```json
{
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
      "target_value": 200.0
    },
    {
      "type": "ma",
      "ma_period": 20,
      "operator": "<="
    }
  ]
}
```

### Operator 枚举

| 操作符 | 说明 |
|-------|------|
| `>` | 大于 |
| `>=` | 大于等于 |
| `<` | 小于 |
| `<=` | 小于等于 |
| `==` | 等于 |

### 条件序列化与反序列化

所有条件类都支持 `to_dict()` 和 `from_dict()` 方法，用于 JSON 序列化和反序列化：

```python
# 序列化
cond = ChangePercentCondition(Operator.GREATER_OR_EQUAL, 3.0)
cond_dict = cond.to_dict()

# 反序列化
restored_cond = ChangePercentCondition.from_dict(cond_dict)
```
