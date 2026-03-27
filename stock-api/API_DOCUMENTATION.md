# Stock API 完整调用文档

## 概述

Stock API 是一个基于 FastAPI 的股票数据服务接口，提供股票行情、新闻线索、推荐数据、实时价格等功能。

**基础 URL:** `http://localhost:8000` (默认端口 8000)

**API 版本:** 1.0.0

---

## 目录

- [内置交互式文档](#内置交互式文档)
- [主 API 端点](#主-api-端点)
- [新闻线索 API](#新闻线索-api)
- [股票推荐 API](#股票推荐-api)
- [实时行情 API](#实时行情-api)
- [股票技术分析 API](#股票技术分析-api)
- [选股扫描 API](#选股扫描-api)
- [提示词记忆 API](#提示词记忆-api)
- [定时任务](#定时任务)
- [错误处理](#错误处理)

---

## 内置交互式文档

FastAPI 自动生成了两个交互式 API 文档页面：

### Swagger UI (推荐)

访问 `http://localhost:8000/docs` 查看 Swagger UI 界面，提供：

- 所有 API 端点的完整列表
- 可交互的测试工具
- 详细的请求参数说明
- 示例请求和响应

### ReDoc

访问 `http://localhost:8000/redoc` 查看 ReDoc 界面，提供：

- 更美观的文档展示
- 清晰的 API 说明
- 请求和响应示例

---

## 主 API 端点

### 1. 获取股票市场概要

**端点:** `GET /get_stock_summary`

**描述:** 获取 A 股、美股、板块资金流向等市场概要数据

**查询参数:**

| 参数名 | 别名 | 类型 | 默认值 | 说明 |
|--------|------|------|--------|------|
| market | m | string | cn | 市场类型：`cn`(A股), `us`(美股), `bk`(板块), `fund`(资金流向) |
| format | f | string | json | 返回格式：`json`(JSON格式), `text`(文本格式) |

**请求示例:**

```bash
# 获取 A 股概要数据（JSON 格式）
curl "http://localhost:8000/get_stock_summary?m=cn&f=json"

# 获取美股概要数据（文本格式）
curl "http://localhost:8000/get_stock_summary?m=us&f=text"

# 获取板块资金流向
curl "http://localhost:8000/get_stock_summary?m=bk"

# 获取资金流向数据
curl "http://localhost:8000/get_stock_summary?m=fund"
```

**响应示例 (JSON):**

```json
[
  {
    "name": "上证指数",
    "code": "sh000001",
    "price": 3050.23,
    "change": 15.45,
    "change_percent": 0.51
  },
  {
    "name": "深证成指",
    "code": "sz399001",
    "price": 10250.67,
    "change": -20.33,
    "change_percent": -0.20
  }
]
```

**响应示例 (text):**

```
上证指数 (sh000001): 3050.23 (+15.45, +0.51%)
深证成指 (sz399001): 10250.67 (-20.33, -0.20%)
```

---

### 2. 获取 A 股资金流向

**端点:** `GET /get_astock_funds_flow`

**描述:** 获取 A 股市场资金流向和交易汇总数据

**查询参数:**

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| brief | boolean | false | 是否返回简洁版本 |

**请求示例:**

```bash
# 获取完整资金流向数据
curl "http://localhost:8000/get_astock_funds_flow"

# 获取简洁版本
curl "http://localhost:8000/get_astock_funds_flow?brief=true"
```

**响应示例:**

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "日期": "20240322",
      "主力净流入": 123.45,
      "超大单净流入": 45.67,
      "大单净流入": 78.90,
      "中单净流入": -12.34,
      "小单净流入": -111.11
    }
  ]
}
```

---

### 3. 获取资金流向文件数据

**端点:** `GET /get_funds_flow`

**描述:** 从本地文件读取资金流向数据

**查询参数:**

| 参数名 | 别名 | 类型 | 默认值 | 说明 |
|--------|------|------|--------|------|
| date | d | string | 今日日期 | 日期格式：YYYYMMDD |
| flow_direction | fd | string | in | 流向类型：`in`(流入), `out`(流出) |

**请求示例:**

```bash
# 获取今日资金流入数据
curl "http://localhost:8000/get_funds_flow"

# 获取指定日期资金流出数据
curl "http://localhost:8000/get_funds_flow?d=20240322&fd=out"
```

**响应示例:**

```json
{
  "date": "20240322",
  "stocks": [
    {
      "code": "000001",
      "name": "平安银行",
      "amount": 123456789,
      "percent": 5.67
    }
  ]
}
```

**错误响应:**

```
Error: file=/app/stock-api/fund_flow_in_20240322.json not found
```

---

### 4. 获取提示词模板

**端点:** `GET /get_prompt`

**描述:** 获取股票分析提示词模板文件内容

**请求示例:**

```bash
curl "http://localhost:8000/get_prompt"
```

**响应示例:**

```markdown
# 股票分析提示词

请分析以下股票数据：
- 价格走势
- 技术指标
- 资金流向
...
```

**错误响应:**

```
Error: prompt_stock_field.md file not found
```

---

## 新闻线索 API

### 5. 插入新闻线索

**端点:** `POST /api/news/clue`

**描述:** 批量插入新闻线索数据到数据库

**请求头:**

```
Content-Type: application/json
```

**请求体 (JSON 数组):**

```json
[
  {
    "title": "新闻标题1",
    "content": "新闻内容摘要",
    "source": "新闻来源",
    "url": "新闻链接",
    "publish_time": "发布时间"
  },
  {
    "title": "新闻标题2",
    "content": "新闻内容摘要",
    "source": "新闻来源",
    "url": "新闻链接",
    "publish_time": "发布时间"
  }
]
```

**说明:** 系统会自动为每条新闻添加 `recommend_date` 字段（当前日期）

**请求示例:**

```bash
curl -X POST "http://localhost:8000/api/news/clue" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "title": "某公司发布利好消息",
      "content": "公司公告...",
      "source": "证券时报",
      "url": "https://example.com/news/123",
      "publish_time": "2024-03-22 10:00:00"
    }
  ]'
```

**响应示例:**

```json
{
  "message": "处理完成，成功: 1/1",
  "ids": [1, 2, 3]
}
```

**错误响应:**

```json
{
  "error": "请求数据不能为空"
}
```

---

### 6. 获取新闻线索

**端点:** `GET /api/news/clue/get`

**描述:** 获取最近 N 天的新闻线索

**查询参数:**

| 参数名 | 别名 | 类型 | 默认值 | 说明 |
|--------|------|------|--------|------|
| days | d | integer | 6 | 查询最近天数 |

**请求示例:**

```bash
# 获取最近 6 天的新闻
curl "http://localhost:8000/api/news/clue/get"

# 获取最近 3 天的新闻
curl "http://localhost:8000/api/news/clue/get?d=3"
```

**响应示例:**

```json
{
  "message": "处理完成，成功: 15",
  "data": [
    {
      "id": 1,
      "title": "新闻标题",
      "content": "新闻内容",
      "source": "来源",
      "url": "链接",
      "publish_time": "2024-03-22 10:00:00",
      "recommend_date": "2024-03-22"
    }
  ]
}
```

---

## 股票推荐 API

### 7. 插入股票推荐

**端点:** `POST /api/stock/recommend`

**描述:** 批量插入股票推荐数据到数据库

**请求头:**

```
Content-Type: application/json
```

**请求体 (JSON 数组，每个元素为 JSON 字符串):**

```json
[
  "{\"code\": \"000001\", \"name\": \"平安银行\", \"recommend_reason\": \"技术面突破\"}",
  "{\"code\": \"600519\", \"name\": \"贵州茅台\", \"recommend_reason\": \"资金大幅流入\"}"
]
```

**说明:**
- 系统会自动添加：`in_date`(推荐日期), `recommend_date`(推荐日期), `recommend_status`(进行中), `out_date`(推荐日期+3天), `in_price`(0), `out_price`(0), `profit_rate`(0)
- `recommend_reason` 为推荐理由

**请求示例:**

```bash
curl -X POST "http://localhost:8000/api/stock/recommend" \
  -H "Content-Type: application/json" \
  -d '[
    "{\"code\": \"000001\", \"name\": \"平安银行\", \"recommend_reason\": \"技术面突破\"}",
    "{\"code\": \"600519\", \"name\": \"贵州茅台\", \"recommend_reason\": \"资金大幅流入\"}"
  ]'
```

**响应示例:**

```json
{
  "message": "处理完成，成功: 2"
}
```

**错误响应:**

```json
{
  "error": "请求数据不能为空"
}
```

---

### 8. 获取股票推荐

**端点:** `GET /api/stock/recommend/get`

**描述:** 获取最近 N 天的股票推荐记录

**查询参数:**

| 参数名 | 别名 | 类型 | 默认值 | 说明 |
|--------|------|------|--------|------|
| days | d | integer | 6 | 查询最近天数 |

**请求示例:**

```bash
# 获取最近 6 天的推荐
curl "http://localhost:8000/api/stock/recommend/get"

# 获取最近 10 天的推荐
curl "http://localhost:8000/api/stock/recommend/get?d=10"
```

**响应示例:**

```json
{
  "message": "处理完成，成功: 5",
  "data": [
    {
      "id": 1,
      "name": "平安银行",
      "code": "000001",
      "in_price": 0,
      "in_date": "2024-03-22",
      "recommend_date": "2024-03-22",
      "recommend_reason": "技术面突破",
      "recommend_status": "进行中",
      "out_price": 0,
      "out_date": "2024-03-25",
      "profit_rate": 0
    }
  ]
}
```

---

## 实时行情 API

### 9. 获取实时股票价格

**端点:** `GET /api/stock/price`

**描述:** 获取单只股票的实时行情数据

**查询参数:**

| 参数名 | 别名 | 类型 | 默认值 | 说明 |
|--------|------|------|--------|------|
| symbol | s | string | sz000001 | 股票代码，格式：市场+代码（如 sh600000, sz000001） |

**请求示例:**

```bash
# 获取平安银行实时价格
curl "http://localhost:8000/api/stock/price?s=sz000001"

# 获取浦发银行实时价格
curl "http://localhost:8000/api/stock/price?s=sh600000"
```

**响应示例:**

```json
{
  "code": "000001",
  "name": "平安银行",
  "price": 12.45,
  "change": 0.23,
  "change_percent": 1.88,
  "open": 12.30,
  "high": 12.50,
  "low": 12.20,
  "volume": 12345678,
  "time": "2024-03-22 14:30:00"
}
```

---

## 股票技术分析 API

### 12. 获取股票历史行情数据

**端点:** `GET /api/stock/history/{code}`

**描述:** 获取股票的历史行情数据，包括开盘价、收盘价、最高价、最低价、成交量等

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 股票代码，格式：6位数字.(SH\|SZ)，例如 000001.SZ |

**查询参数:**

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| start_date | string | 无 | 开始日期，格式 yyyy-mm-dd |
| end_date | string | 无 | 结束日期，格式 yyyy-mm-dd |
| limit | integer | 100 | 返回记录数，默认 100，最大 1000 |

**请求示例:**

```bash
# 获取平安银行最近 100 条历史数据
curl "http://localhost:8000/api/stock/history/000001.SZ"

# 获取指定日期范围的历史数据
curl "http://localhost:8000/api/stock/history/000001.SZ?start_date=2024-01-01&end_date=2024-03-22"

# 限制返回 50 条记录
curl "http://localhost:8000/api/stock/history/000001.SZ?limit=50"
```

**响应示例:**

```json
[
  {
    "id": 1,
    "code": "000001.SZ",
    "name": "平安银行",
    "trade_date": "2024-03-22",
    "open": 12.30,
    "high": 12.50,
    "low": 12.20,
    "close": 12.45,
    "volume": 12345678,
    "amount": 123456789.00,
    "turnover": 2.5,
    "amplitude": 2.4,
    "change_rate": 1.22
  }
]
```

**错误响应:**

```json
{
  "detail": "股票代码格式不正确，应为 6位数字.(SH|SZ)，例如 000001.SZ"
}
```

---

### 13. 获取股票技术指标

**端点:** `GET /api/stock/indicators/{code}`

**描述:** 获取股票的技术指标，包括均线（MA5/MA10/MA20/MA60）和 MACD 指标

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 股票代码，格式：6位数字.(SH\|SZ)，例如 000001.SZ |

**查询参数:**

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| days | integer | 250 | 获取数据的天数，默认 250 |

**请求示例:**

```bash
# 获取平安银行的技术指标（默认 250 天）
curl "http://localhost:8000/api/stock/indicators/000001.SZ"

# 获取最近 60 天的技术指标
curl "http://localhost:8000/api/stock/indicators/000001.SZ?days=60"
```

**响应示例:**

```json
{
  "code": "000001.SZ",
  "dates": ["2024-01-01", "2024-01-02", "..."],
  "ma5": [12.30, 12.35, 12.40, "..."],
  "ma10": [12.25, 12.30, 12.35, "..."],
  "ma20": [12.20, 12.25, 12.30, "..."],
  "ma60": [12.10, 12.15, 12.20, "..."],
  "macd_dif": [0.05, 0.08, 0.10, "..."],
  "macd_dea": [0.03, 0.05, 0.07, "..."],
  "macd_hist": [0.04, 0.06, 0.06, "..."]
}
```

---

### 14. 获取股票形态检测结果

**端点:** `GET /api/stock/pattern/{code}`

**描述:** 获取股票的形态检测结果，包括金叉、死叉、多头排列、MACD 信号等

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 股票代码，格式：6位数字.(SH\|SZ)，例如 000001.SZ |

**查询参数:**

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| days | integer | 60 | 获取数据的天数，默认 60 |

**请求示例:**

```bash
# 获取平安银行的形态检测结果（默认 60 天）
curl "http://localhost:8000/api/stock/pattern/000001.SZ"

# 获取最近 120 天的形态检测结果
curl "http://localhost:8000/api/stock/pattern/000001.SZ?days=120"
```

**响应示例:**

```json
{
  "code": "000001.SZ",
  "dates": ["2024-01-01", "2024-01-02", "..."],
  "golden_crosses": ["2024-02-15", "2024-03-10"],
  "death_crosses": ["2024-01-20", "2024-02-28"],
  "bullish_arrangements": ["2024-03-15", "2024-03-16", "2024-03-17"],
  "macd_signals": {
    "golden_cross": ["2024-02-10"],
    "death_cross": ["2024-01-25"],
    "bullish_momentum": ["2024-03-18", "2024-03-19"],
    "bearish_momentum": ["2024-01-15", "2024-01-16"]
  },
  "latest_state": {
    "date": "2024-03-22",
    "ma5": 12.45,
    "ma10": 12.40,
    "ma20": 12.30,
    "ma60": 12.20,
    "is_bullish_arrangement": true,
    "macd_dif": 0.15,
    "macd_dea": 0.10,
    "macd_hist": 0.10
  }
}
```

---

## 选股扫描 API

### 15. 获取选股扫描结果

**端点:** `GET /api/stock/scan-results`

**描述:** 获取选股扫描结果

**查询参数:**

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| date | string | 今天 | 扫描日期，格式 yyyy-mm-dd，默认为今天 |
| limit | integer | 100 | 返回记录数，默认 100，最大 1000 |

**请求示例:**

```bash
# 获取今天的选股结果
curl "http://localhost:8000/api/stock/scan-results"

# 获取指定日期的选股结果
curl "http://localhost:8000/api/stock/scan-results?date=2024-03-24"

# 限制返回 50 条记录
curl "http://localhost:8000/api/stock/scan-results?limit=50"
```

**响应示例:**

```json
[
  {
    "id": 1,
    "code": "000001",
    "name": "平安银行",
    "scan_date": "2024-03-24",
    "choose_reason": {
      "strategy": "默认策略",
      "strategy_params": {
        "min_change_rate": 3.0,
        "max_change_rate": 6.0,
        "check_ma20": true,
        "check_macd": true,
        "check_recent_rise": true,
        "recent_days": 3
      },
      "scan_date": "2024-03-24",
      "stock_info": {
        "code": "000001",
        "name": "平安银行",
        "close": 12.45,
        "change_rate": 4.5,
        "ma20": 12.0
      }
    }
  }
]
```

---

## 提示词记忆 API

### 10. 插入提示词上下文

**端点:** `POST /api/prompt/in`

**描述:** 保存提示词上下文和分类到数据库

**请求类型:** `multipart/form-data`

**表单参数:**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| context | string | 是 | - | 提示词上下文内容 |
| prompt_class | string | 否 | 涨停聚焦 | 提示词分类 |

**请求示例:**

```bash
curl -X POST "http://localhost:8000/api/prompt/in" \
  -F "context=分析股票的资金流向和价格走势" \
  -F "prompt_class=涨停聚焦"
```

**响应示例:**

```json
{
  "message": "处理完成，成功: 1"
}
```

**错误响应:**

```json
{
  "error": "请求数据不能为空"
}
```

---

### 11. 获取提示词上下文

**端点:** `GET /api/prompt/get`

**描述:** 根据分类获取提示词上下文

**查询参数:**

| 参数名 | 别名 | 类型 | 默认值 | 说明 |
|--------|------|------|--------|------|
| cls_name | cls | string | 涨停聚焦 | 提示词分类名称 |

**请求示例:**

```bash
# 获取"涨停聚焦"分类的提示词
curl "http://localhost:8000/api/prompt/get"

# 获取指定分类的提示词
curl "http://localhost:8000/api/prompt/get?cls=技术分析"
```

**响应示例:**

```json
{
  "message": "处理完成，成功: 1",
  "data": "分析股票的资金流向和价格走势，判断是否为涨停板..."
}
```

---

## 定时任务

### 股票筛选任务 (选股 Job)

**文件位置:** 
- 任务逻辑: `/app/stock-api/job/stock_scan.py`
- 执行脚本: `/app/stock-api/run_screen.py`

**功能描述:**
- 根据配置的选股策略筛选股票
- 保存筛选结果到数据库
- 支持多种筛选条件：涨跌幅、MA20、MACD、近期上涨等

**执行方式:**

```bash
# 方式1: 使用 run_screen.py (默认使用昨天的日期)
cd /app/stock-api
python run_screen.py

# 方式2: 直接调用 job/stock_scan.py (默认使用今天的日期)
cd /app/stock-api
python -m job.stock_scan
```

**策略配置:**
- 策略存储在 `stock_choose_strategy` 表
- 默认策略包含：
  - 涨跌幅范围：3.0% - 6.0%
  - MA20 检查：收盘价 > MA20
  - MACD 检查：近期无死叉
  - 近期上涨检查：连续3天上涨

**结果查询:**
- 使用 `/api/stock/scan-results` API 端点查询选股结果
- 结果存储在 `stock_best_choose` 表

---

## 错误处理

### 统一错误格式

所有 API 在发生错误时会返回以下格式：

```json
{
  "error": "错误描述信息"
}
```

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 404 | 资源未找到 |
| 500 | 服务器内部错误 |

### 常见错误示例

**请求数据为空:**

```json
{
  "error": "请求数据不能为空"
}
```

**数据格式错误:**

```json
{
  "error": "数据格式错误，需要数组格式"
}
```

**文件未找到:**

```
Error: file=/path/to/file.json not found
```

---

## 技术说明

### CORS 配置

API 已配置跨域资源共享 (CORS)，允许所有来源访问：

```python
allow_origins=["*"]
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```

### 缓存机制

部分 API 使用 Redis 进行数据缓存：

- 股票指数数据缓存时间：24 小时
- 资金流向数据缓存时间：24 小时
- 盘中数据会实时更新，盘外数据使用缓存

### 数据库

所有数据持久化操作使用 PostgreSQL 数据库：

- 新闻线索表：`news_clue`
- 股票推荐表：`stock_recommend`
- 提示词表：`ai_prompt`
- 股票历史行情表：`stock_cn_history_market`
- 选股策略表：`stock_choose_strategy`
- 选股结果表：`stock_best_choose`

---

## 快速开始

### 使用 curl 测试

```bash
# 测试市场概要
curl "http://localhost:8000/get_stock_summary?m=cn"

# 测试实时行情
curl "http://localhost:8000/api/stock/price?s=sz000001"

# 测试新闻线索
curl -X POST "http://localhost:8000/api/news/clue" \
  -H "Content-Type: application/json" \
  -d '[{"title": "测试新闻", "content": "测试内容"}]'

# 测试获取新闻
curl "http://localhost:8000/api/news/clue/get?d=3"

# 测试选股结果
curl "http://localhost:8000/api/stock/scan-results"
```

### 使用 Python requests 测试

```python
import requests

# 获取市场概要
response = requests.get("http://localhost:8000/get_stock_summary", params={"m": "cn"})
print(response.json())

# 获取实时行情
response = requests.get("http://localhost:8000/api/stock/price", params={"s": "sz000001"})
print(response.json())

# 插入新闻线索
news_data = [
    {
        "title": "测试新闻",
        "content": "测试内容",
        "source": "测试来源",
        "url": "https://example.com",
        "publish_time": "2024-03-22 10:00:00"
    }
]
response = requests.post("http://localhost:8000/api/news/clue", json=news_data)
print(response.json())

# 获取选股结果
response = requests.get("http://localhost:8000/api/stock/scan-results")
print(response.json())
```

### 使用 JavaScript fetch 测试

```javascript
// 获取市场概要
fetch('http://localhost:8000/get_stock_summary?m=cn')
  .then(response => response.json())
  .then(data => console.log(data));

// 获取实时行情
fetch('http://localhost:8000/api/stock/price?s=sz000001')
  .then(response => response.json())
  .then(data => console.log(data));

// 插入新闻线索
fetch('http://localhost:8000/api/news/clue', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify([{
    title: "测试新闻",
    content: "测试内容",
    source: "测试来源"
  }])
})
  .then(response => response.json())
  .then(data => console.log(data));

// 获取选股结果
fetch('http://localhost:8000/api/stock/scan-results')
  .then(response => response.json())
  .then(data => console.log(data));
```

---

## 更新日志

### v1.2.0 (2024-03-25)

- 新增股票筛选功能 (选股 Job)
- 新增选股策略配置表
- 新增选股结果存储表
- 新增选股结果查询 API 端点 /api/stock/scan-results
- 新增执行脚本 run_screen.py
- 更新 API 文档，包含选股功能说明

### v1.1.0 (2024-03-24)

- 新增股票历史行情数据接口
- 新增技术指标计算接口（MACD、均线）
- 新增形态检测接口（金叉、死叉、多头排列）
- 新增数据库模型和 Alembic 迁移
- 新增数据获取和定时任务模块
- 新增完整的 pytest 测试套件
- 更新 API 文档，包含新技术分析接口

### v1.0.0 (2024-03-22)

- 初始版本发布
- 实现市场概要数据接口
- 实现资金流向接口
- 实现新闻线索管理
- 实现股票推荐功能
- 实现实时行情查询
- 实现提示词记忆功能

---

## 联系方式

如有问题或建议，请联系项目维护者。
