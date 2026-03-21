# 新增技术指标说明

系统现已扩展支持 **13个技术指标**，覆盖趋势、动量、波动率、成交量等多维度分析。

## 新增指标列表

| 指标 | 名称 | 功能 | 临界价格 |
|------|------|------|----------|
| **RSI** | 相对强弱指数 | 超买超卖判断 | RSI>70超买/RSI<30超卖 |
| **Bollinger** | 布林带 | 波动率通道 | 触及上轨/下轨的价格 |
| **Volume** | 成交量 | 量价分析 | VWAP偏离临界 |
| **CCI** | 商品通道指标 | 趋势强度 | CCI>100超买/CCI<-100超卖 |
| **ATR** | 真实波幅 | 波动率/止损 | 突破区间临界 |
| **ADX** | 平均趋向指数 | 趋势强度 | 弱趋势→强趋势临界 |
| **Stochastic** | 随机指标 | 区间位置 | %K>80超买/%K<20超卖 |
| **Momentum** | 动量指标 | 动能判断 | 动量转正/转负价格 |
| **Parabolic SAR** | 抛物线转向 | 止损追踪 | SAR穿越价格 |
| **Ichimoku** | 一目均衡表 | 综合趋势 | 云图穿越价格 |

## API 使用示例

### 1. 获取可用指标列表

```http
GET /api/indicators/list
```

响应：
```json
{
  "count": 13,
  "indicators": [
    {"name": "rsi", "display_name": "RSI", "description": "..."},
    {"name": "bollinger", "display_name": "布林带", "description": "..."},
    ...
  ]
}
```

### 2. 计算增强版触发矩阵

```http
POST /api/matrix/enhanced/000001.SZ?mock=true
```

响应：
```json
{
  "symbol": "000001.SZ",
  "current_price": 10.77,
  "indicators": {
    "rsi": {
      "current_value": 45.3,
      "zone": "neutral",
      "bullish_trigger_price": 10.45,
      "bearish_trigger_price": 11.20,
      "metadata": {"period": 14}
    },
    "bollinger": {
      "current_value": 55.0,
      "zone": "neutral",
      "bullish_trigger_price": 10.25,
      "bearish_trigger_price": 11.50,
      "metadata": {
        "upper_band": 11.52,
        "middle_band": 10.88,
        "lower_band": 10.25
      }
    },
    "cci": {...},
    "atr": {...},
    "adx": {...},
    ...
  },
  "resonance": [
    {
      "type": "resonance",
      "indicators": ["rsi_oversold", "bollinger_lower"],
      "price_min": 10.25,
      "price_max": 10.45,
      "price_center": 10.35,
      "confidence": 0.75
    }
  ],
  "summary": {
    "total_indicators": 13,
    "bullish_signals": 5,
    "bearish_signals": 3,
    "neutral_signals": 5,
    "overall_sentiment": "neutral",
    "closest_bullish_trigger": {
      "indicator": "rsi",
      "price": 10.45,
      "distance": -2.97
    }
  }
}
```

### 3. 指定指标计算

```http
POST /api/matrix/enhanced/000001.SZ?indicators=rsi,bollinger,cci
```

### 4. 增强版压力测试

```http
POST /api/stress-test/enhanced/000001.SZ?hypothetical_price=11.50
```

响应：
```json
{
  "hypothetical_price": 11.50,
  "indicators": {
    "rsi": {
      "indicator_value": 78.5,
      "zone": "overbought",
      "is_bullish": false,
      "is_bearish": true
    },
    "bollinger": {
      "indicator_value": 95.0,
      "zone": "overbought",
      "is_bullish": false,
      "is_bearish": true,
      "metadata": {
        "upper": 11.52,
        "percent_b": 95
      }
    },
    ...
  },
  "summary": {
    "bullish_signals": 2,
    "bearish_signals": 8,
    "overall": "bearish"
  }
}
```

## 指标详解

### RSI (相对强弱指数)

**公式**: RSI = 100 - 100/(1 + RS)

**临界价格求解**:
- 使用二分法求解使 RSI = 30/70 的价格
- 上涨至RSI=70的价格为看跌触发
- 下跌至RSI=30的价格为看涨触发

**示例**:
```
当前价格: 100
RSI: 45 (中性)
上涨临界(RSI=70): 115.5 (需上涨15.5%)
下跌临界(RSI=30): 85.2 (需下跌14.8%)
```

### 布林带

**公式**:
- 上轨 = MA(20) + 2 × STD(20)
- 下轨 = MA(20) - 2 × STD(20)

**临界价格求解**:
- 使用数值方法求解使价格触及上轨/下轨
- 触及上轨 = 超买/回调信号
- 触及下轨 = 超卖/反弹信号

### CCI (商品通道指标)

**公式**: CCI = (TP - MA) / (0.015 × MAD)

**阈值**:
- > +100: 超买
- < -100: 超卖

### ATR (真实波幅)

**用途**:
- 设置止损位
- 判断波动率
- 预测突破范围

**输出**:
```
ATR: 0.52
日内波动范围: ±1.04 (±9.6%)
止损建议: 10.25
突破上轨: 11.81
突破下轨: 9.33
```

### Ichimoku Cloud (一目均衡表)

**信号系统**:
- 价格在云上: 看涨
- 价格在云下: 看跌
- 价格在云中: 震荡
- 转换线上穿基准线: 看涨信号
- 价格上穿云顶: 强烈看涨

## 扩展自定义指标

如需添加新指标，只需：

1. 创建求解器类继承 `BaseSolver`
2. 使用 `@IndicatorRegistry.register` 装饰器注册
3. 实现 `calculate`、`solve_trigger_prices`、`simulate` 方法

示例:
```python
@IndicatorRegistry.register
class MyIndicatorSolver(BaseSolver):
    name = "my_indicator"
    display_name = "我的指标"
    
    def calculate(self, prices, current_price):
        # 计算指标值
        return indicator_value
    
    def solve_trigger_prices(self, prices, current_price):
        # 求解临界价格
        return TriggerResult(...)
```

注册后自动出现在API中，无需修改其他代码。

## 共振检测增强

新版共振检测支持：
- 更多指标组合
- 动态置信度计算
- 多层级共振区间

示例共振区间:
```json
{
  "indicators": ["rsi_oversold", "bollinger_lower", "cci_oversold"],
  "price_min": 10.20,
  "price_max": 10.45,
  "confidence": 0.85,
  "signal": "强烈超卖共振区"
}
```
