# 股票助手策略计算逻辑详解

## 一、技术指标计算方式

### 1. 均线 (MA) 计算

#### MA5 (5日均线)
```
MA5 = (昨日收盘价 + 前日收盘价 + ... + 4日前收盘价 + 今日收盘价) / 5

实际实现：
- 取最近 4 个历史收盘价（prices[-5:-1]）
- 加上今日收盘价（current_price）
- 求和后除以 5
```

#### MA10 (10日均线)
```
MA10 = (前9日收盘价之和 + 今日收盘价) / 10

实际实现：
- 取最近 9 个历史收盘价（prices[-10:-1]）
- 加上今日收盘价（current_price）
- 求和后除以 10
```

#### 多头排列判断
```
is_bullish = MA5 > MA10

如果 MA5 > MA10：多头排列（看涨）
如果 MA5 < MA10：空头排列（看跌）
```

---

### 2. MACD 计算

#### DIF (快线)
```
EMA12 = 12日指数移动平均
EMA26 = 26日指数移动平均
DIF = EMA12 - EMA26
```

#### DEA (慢线/信号线)
```
DEA = DIF 的 9 日指数移动平均
```

#### MACD柱状图
```
MACD = 2 * (DIF - DEA)
```

#### 金叉/死叉判断
```
金叉：DIF > DEA （快线上穿慢线）
死叉：DIF < DEA （快线下穿慢线）
```

---

### 3. KDJ 计算

#### RSV (未成熟随机值)
```
RSV = (今日收盘价 - 最近9日最低价) / (最近9日最高价 - 最近9日最低价) * 100
```

#### K值
```
K = 2/3 * 昨日K值 + 1/3 * RSV
```

#### D值
```
D = 2/3 * 昨日D值 + 1/3 * K
```

#### J值
```
J = 3K - 2D
```

#### 超买超卖判断
```
J < 0：超卖区（可能反弹）
J > 100：超买区（可能回调）
```

---

## 二、策略条件判断逻辑

### 1. 买入条件判断

#### 股价站上MA5
```python
def check_price_above_ma5(current_price, ma5_value):
    """
    判断股价是否站上MA5
    允许1%的误差（股价可以略低于MA5）
    """
    threshold = ma5_value * 0.99  # 99%的MA5值
    
    if current_price >= threshold:
        return True  # 已站上MA5
    else:
        return False  # 未站上MA5
        # 需要上涨 (ma5_value - current_price) / current_price * 100%
```

**示例：**
- 当前股价：10.00元
- MA5值：10.50元
- 判断：10.00 < 10.50 * 0.99 = 10.395
- 结果：❌ 未站上MA5，需要上涨约5%

#### 均线上穿（MA5金叉MA10）
```python
def check_ma_golden_cross(ma5, ma10):
    """
    判断MA5是否上穿MA10（金叉）
    """
    if ma5 > ma10:
        return True  # 多头排列，金叉状态
    else:
        return False  # 空头排列，等待金叉
```

#### MACD金叉
```python
def check_macd_golden_cross(dif, dea):
    """
    判断DIF是否上穿DEA（金叉）
    """
    if dif > dea:
        return True  # MACD金叉
    else:
        return False  # 等待金叉
```

#### KDJ超卖
```python
def check_kdj_oversold(j_value):
    """
    判断KDJ是否超卖
    """
    if j_value < 0:
        return True  # 超卖区，可能反弹
    else:
        return False  # 未超卖
```

---

### 2. 止损条件判断

#### 跌破MA5
```python
def check_price_below_ma5(current_price, ma5_value):
    """
    判断是否跌破MA5
    允许1%的缓冲
    """
    threshold = ma5_value * 0.99
    
    if current_price < threshold:
        return True  # 已跌破MA5，触发止损
    else:
        return False  # 未跌破
```

#### 均线死叉
```python
def check_ma_death_cross(ma5, ma10):
    """
    判断MA5是否下穿MA10（死叉）
    """
    if ma5 < ma10:
        return True  # 空头排列，触发止损
    else:
        return False  # 多头排列，持有
```

---

## 三、策略匹配算法

### 1. 整体匹配逻辑

```python
def check_strategy_match(current_price, indicators, strategy_conditions):
    """
    检查策略是否全部匹配
    
    策略匹配 = 所有启用的条件都满足
    """
    enabled_conditions = [c for c in strategy_conditions if c.enabled]
    
    satisfied_count = 0
    for condition in enabled_conditions:
        if check_single_condition(current_price, indicators, condition):
            satisfied_count += 1
    
    # 全部满足才算匹配
    return satisfied_count == len(enabled_conditions)
```

### 2. 单条件检查

```python
def check_single_condition(current_price, indicators, condition):
    """
    检查单个条件是否满足
    """
    if condition.type == "priceAboveMA5":
        return current_price >= indicators.ma.ma_short * 0.99
    
    elif condition.type == "priceAboveMA10":
        return current_price >= indicators.ma.ma_long * 0.99
    
    elif condition.type == "maGolden":
        return indicators.ma.is_bullish  # MA5 > MA10
    
    elif condition.type == "macdGolden":
        return indicators.macd.dif > indicators.macd.dea
    
    elif condition.type == "kdjOversold":
        return indicators.kdj.j < 0
    
    elif condition.type == "priceBelowMA5":
        return current_price < indicators.ma.ma_short * 0.99
    
    elif condition.type == "maDeath":
        return not indicators.ma.is_bullish  # MA5 < MA10
    
    return False
```

---

## 四、触发价格计算

### 1. 站上MA5的目标价格

```python
def calculate_target_for_ma5(current_price, ma_history_prices):
    """
    计算站上MA5所需的目标价格
    
    MA5 = (前4日收盘价之和 + 目标价) / 5
    目标价 = MA5 * 5 - 前4日收盘价之和
    
    当股价站上MA5时：股价 >= MA5
    所以目标价 >= (前4日收盘价之和) / 4
    """
    sum_4days = sum(ma_history_prices)  # 前4日收盘价之和
    target_price = sum_4days / 4  # 简化的目标价计算
    
    return target_price
```

### 2. 均线金叉的目标价格

```python
def calculate_golden_cross_price(prices_short, prices_long, short_period, long_period):
    """
    计算MA5上穿MA10（金叉）所需的目标价格
    
    推导：
    MA_short = (sum_short + P) / N_short
    MA_long = (sum_long + P) / N_long
    
    金叉条件：MA_short >= MA_long
    (sum_short + P) / N_short >= (sum_long + P) / N_long
    
    解得：
    P >= (sum_long * N_short - sum_short * N_long) / (N_long - N_short)
    """
    sum_short = sum(prices_short)
    sum_long = sum(prices_long)
    n_short = short_period
    n_long = long_period
    
    # 临界价格
    critical_price = (sum_long * n_short - sum_short * n_long) / (n_long - n_short)
    
    return critical_price
```

---

## 五、策略区间计算

### 买入区间计算

```python
def calculate_buy_range(current_price, conditions, indicators):
    """
    计算满足所有买入条件的股价区间
    
    返回：
    - current_satisfied: 当前是否已满足所有条件
    - price_min: 可买入的最低价格
    - price_max: 可买入的最高价格
    - critical_prices: 各条件的临界价格列表
    """
    critical_prices = []
    
    for condition in conditions:
        if not check_single_condition(current_price, indicators, condition):
            # 条件未满足，计算需要达到的目标价
            target = calculate_target_price(condition, indicators)
            critical_prices.append({
                "condition": condition.name,
                "target_price": target,
                "direction": "above",  # 需要上涨才能满足
                "distance_pct": (target - current_price) / current_price * 100
            })
    
    # 当前满足 = 没有未满足的条件
    current_satisfied = len(critical_prices) == 0
    
    if critical_prices:
        # 需要满足最难的条件（最高目标价）
        min_price = max([p["target_price"] for p in critical_prices])
        return {
            "current_satisfied": False,
            "price_min": min_price,
            "price_max": current_price * 2,  # 上限设为当前价2倍
            "critical_prices": critical_prices
        }
    else:
        return {
            "current_satisfied": True,
            "message": "所有买入条件已满足"
        }
```

---

## 六、实际案例

### 案例1：站上MA5策略

**股票数据：**
- 当前股价：10.00元
- MA5值：10.50元
- MA10值：10.30元

**策略设置：**
- 启用条件：股价站上MA5

**判断过程：**
```
1. 计算阈值：10.50 * 0.99 = 10.395元
2. 比较：10.00 < 10.395
3. 结果：未站上MA5
4. 需要上涨：(10.50 - 10.00) / 10.00 = 5.0%
```

**显示结果：**
- 买入状态：❌ 观望
- 需满足：站上MA5（目标价10.50元，需涨5.0%）

---

### 案例2：MACD金叉 + 站上MA5

**股票数据：**
- 当前股价：10.00元
- MACD：DIF=0.5, DEA=0.3（已金叉）
- MA5=10.50元, MA10=10.30元

**策略设置：**
- 启用条件：MACD金叉 + 股价站上MA5

**判断过程：**
```
1. MACD金叉检查：
   DIF(0.5) > DEA(0.3) → ✅ 已满足

2. 站上MA5检查：
   10.00 < 10.50 * 0.99 = 10.395 → ❌ 未满足
   需要上涨5.0%
```

**显示结果：**
- 买入状态：❌ 观望
- 已满足：MACD金叉
- 需满足：站上MA5（需涨5.0%）

---

### 案例3：全部条件满足

**股票数据：**
- 当前股价：10.60元
- MACD：DIF=0.5, DEA=0.3（金叉）
- MA5=10.50元, MA10=10.30元（多头排列）

**策略设置：**
- 启用条件：MACD金叉 + 均线上穿 + 站上MA5

**判断过程：**
```
1. MACD金叉：0.5 > 0.3 → ✅
2. 均线上穿：10.50 > 10.30 → ✅
3. 站上MA5：10.60 > 10.50 * 0.99 = 10.395 → ✅

全部条件满足！
```

**显示结果：**
- 买入状态：✅ 可买
- 所有条件已满足

---

## 七、常见问题排查

### 问题1：股价明显低于MA5，但显示"可买"

**可能原因：**
1. MA计算错误（使用了错误的历史数据）
2. 策略判断条件有误（未正确比较）
3. 使用了缓存的过期数据

**排查步骤：**
```bash
# 1. 检查API返回的MA5值
GET /api/v1/indicators/000001.SZ

# 2. 验证计算
手动计算：(前4日收盘价 + 今日价) / 5

# 3. 检查策略判断
GET /api/v1/strategy/calculate-range?symbol=000001.SZ&current_price=10.0
```

### 问题2：临界价格计算错误

**检查点：**
1. 历史价格数据是否正确（prices数组）
2. 周期设置是否正确（5日/10日）
3. 当前价格是否传入正确

---

## 八、代码文件对应

| 功能 | 文件路径 |
|------|----------|
| MA计算 | `backend/app/core/ma_solver.py` |
| MACD计算 | `backend/app/core/macd_solver.py` |
| KDJ计算 | `backend/app/core/kdj_solver.py` |
| 策略匹配 | `backend/app/core/indicator_engine.py` |
| 策略区间 | `backend/app/core/indicator_engine.py` |
| 前端判断 | `miniprogram/pages/index/index.js` |

---

## 九、关键配置参数

```python
# 均线周期（可配置）
MA_SHORT_PERIOD = 5   # MA5
MA_LONG_PERIOD = 10   # MA10

# MACD参数
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# 误差容忍度（1%）
THRESHOLD_TOLERANCE = 0.99

# KDJ周期
KDJ_PERIOD = 9
```
