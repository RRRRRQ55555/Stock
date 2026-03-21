# 使用示例

实际使用场景示例。

## 示例 1: SaaS 落地页

### 用户需求
"为我的 B2B SaaS 产品创建一个落地页，产品是项目管理工具，面向小型团队。"

### 生成的设计系统

```markdown
## 设计系统: TeamFlow (项目管理 SaaS)

### 页面模式
- 类型: Feature-Rich Showcase
- 结构: Hero → Quick Overview → Detailed Features → Testimonials → Pricing → CTA
- 转化策略: 免费试用 + 功能展示

### UI 风格
- 主风格: Soft UI Evolution
- 关键词: 柔和阴影、微妙深度、专业、现代
- 性能: Excellent | 可访问性: WCAG AA

### 配色方案
- Primary: #2563EB (科技蓝)
- Secondary: #3B82F6 (亮蓝)
- CTA: #1D4ED8 (深蓝)
- Background: #F8FAFC (极浅灰)
- Text: #1E293B (深 slate)
- 说明: 专业、可信赖的科技风格

### 字体配对
- 标题: Poppins (600, 700)
- 正文: Inter (400, 500)
- 氛围: 几何、现代、友好
- Google Fonts: https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&family=Inter:wght@400;500&display=swap

### 关键效果
- 阴影: 柔和阴影 (0 2px 8px rgba(0,0,0,0.04))
- 过渡: 平滑过渡 200-300ms
- 悬停状态: 微妙的颜色/阴影变化

### 页面结构
1. Hero Section
   - 大标题: "让团队协作更简单"
   - 副标题: "小型团队的项目管理利器"
   - 双 CTA: "免费试用" (Primary) + "观看演示" (Secondary)

2. Logo Cloud
   - 信任客户标志

3. Quick Overview
   - 3 个核心功能卡片
   - 图标 + 标题 + 简短描述

4. Detailed Features
   - 功能 1: 任务管理 (左图右文)
   - 功能 2: 团队协作 (右图左文)
   - 功能 3: 进度追踪 (左图右文)
   - 功能 4: 报告分析 (右图左文)

5. Testimonials
   - 3 个客户评价卡片
   - 头像 + 姓名 + 职位 + 评价

6. Pricing
   - 3 档定价卡片
   - 突出推荐方案

7. Final CTA
   - "开始免费试用"
   - 14 天免费，无需信用卡

8. Footer
   - 产品链接、公司信息、社交媒体

### 需要避免的反模式
- 不使用表情符号作为图标（使用 Lucide Icons）
- 不过度使用动画
- 不使用 AI 紫色/粉色渐变

### 响应式策略
- 桌面: 完整布局，侧边展示
- 平板: 简化布局，2 列网格
- 移动: 单列，汉堡菜单
```

## 示例 2: 金融科技仪表板

### 用户需求
"创建一个投资跟踪仪表板，深色主题，显示股票组合和收益。"

### 生成的设计系统

```markdown
## 设计系统: WealthTrack (投资仪表板)

### 页面模式
- 类型: Financial Dashboard
- 结构: Header → KPI Cards → Portfolio → Performance → Transactions
- 数据密度: 高

### UI 风格
- 主风格: Dark Mode (OLED)
- 关键词: 纯黑背景、高对比度、数据可视化
- 性能: Excellent | 可访问性: WCAG AA

### 配色方案
- Primary: #60A5FA (亮蓝)
- Secondary: #34D399 (翠绿 - 涨)
- Accent: #F87171 (红 - 跌)
- CTA: #A78BFA (柔和紫)
- Background: #000000 (纯黑)
- Surface: #111827 (深灰)
- Text Primary: #FAFAFA (近白)
- Text Secondary: #94A3B8 (slate)
- 说明: OLED 节能、数据清晰

### 字体配对
- 标题: Inter (500, 600, 700)
- 正文: Inter (400, 500)
- 数字: JetBrains Mono (tabular-nums)
- 氛围: 专业、数据驱动

### 关键效果
- 卡片: 微妙边框 (1px solid rgba(255,255,255,0.1))
- 图表: 渐变填充
- 悬停: 背景高亮
- 数据更新: 平滑动画

### 组件清单

1. Header
   - 搜索栏
   - 通知图标
   - 用户头像

2. KPI Cards (4 列)
   - 总资产
   - 今日收益 (+/-)
   - 本周收益
   - 本月收益

3. Portfolio Allocation
   - 饼图/环形图
   - 资产类别占比
   - 点击查看详情

4. Performance Chart
   - 折线图 (时间序列)
   - 时间范围切换 (1D/1W/1M/1Y/ALL)
   - 涨跌颜色区分

5. Holdings Table
   - 股票列表
   - 持仓/价格/涨跌幅
   - 排序功能

6. Recent Transactions
   - 最近交易记录
   - 类型/金额/时间

### 图表颜色
- 涨: #34D399 (翠绿)
- 跌: #F87171 (红)
- 主线条: #60A5FA (蓝)
- 网格线: rgba(255,255,255,0.1)

### 需要避免的反模式
- 不使用霓虹色
- 不过度使用红色/绿色（色盲友好）
- 不使用复杂动画干扰数据阅读

### 可访问性考虑
- 涨跌同时用图标表示（↑↓）
- 颜色不是唯一的区分方式
- 数据表格支持键盘导航
```

## 示例 3: 美容 SPA 预约网站

### 用户需求
"为我的美容 SPA 创建一个网站，需要预约功能和在线展示。"

### 生成的设计系统

```markdown
## 设计系统: Serenity Spa (美容养生)

### 页面模式
- 类型: Hero-Centric + Social Proof
- 结构: Hero → Services → Testimonials → Booking → Contact
- 转化策略: 情感驱动 + 信任元素

### UI 风格
- 主风格: Soft UI Evolution
- 关键词: 柔和阴影、微妙深度、平静、奢华感、有机形状
- 性能: Excellent | 可访问性: WCAG AA

### 配色方案
- Primary: #E8B4B8 (柔粉)
- Secondary: #A8D5BA (鼠尾草绿)
- CTA: #D4AF37 (金)
- Background: #FFF5F5 (暖白)
- Surface: #FFFFFF (白)
- Text: #2D3436 (炭灰)
- Text Light: #636E72 (灰)
- 说明: 平静配色，金色点缀增添奢华感

### 字体配对
- 标题: Cormorant Garamond (600, 700)
- 正文: Montserrat (400, 500)
- 氛围: 优雅、平静、精致
- Google Fonts: https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Montserrat:wght@400;500&display=swap

### 关键效果
- 圆角: 大圆角 (16-24px)
- 阴影: 柔和扩散
- 过渡: 平滑 (200-300ms)
- 图片: 有机形状蒙版

### 页面结构

1. Hero Section
   - 全屏背景图片 (SPA 环境)
   - 居中文字: "找到内心的平静"
   - CTA: "立即预约"
   - 向下滚动指示器

2. Services Section
   - 标题: "我们的服务"
   - 服务卡片网格:
     - 面部护理
     - 身体按摩
     - 美甲服务
     - 水疗套餐
   - 每张卡片: 图片 + 标题 + 描述 + 价格

3. Testimonials
   - 标题: "客户评价"
   - 3 列评价卡片
   - 星级评分 + 评价文字 + 客户姓名

4. Booking Section
   - 预约表单:
     - 服务选择 (下拉)
     - 日期选择 (日历组件)
     - 时间选择 (时段按钮)
     - 联系信息
   - 实时可用性检查

5. Gallery
   - 图片网格展示
   - 灯箱查看

6. Contact Section
   - 地址、电话、营业时间
   - 联系表单
   - 地图嵌入

7. Footer
   - 社交媒体链接
   - 快速链接
   - 版权信息

### 需要避免的反模式
- 不使用明亮霓虹色
- 不使用刺眼动画
- 不使用深色模式（与平静氛围不符）
- 不使用 AI 紫色/粉色渐变

### 图片风格
- 柔和自然光
- 有机形状蒙版
- 温暖色调滤镜
- 真实环境照片
```

## 示例 4: 移动端电商应用

### 用户需求
"创建一个移动端电商应用 UI，销售时尚服装。"

### 生成的设计系统

```markdown
## 设计系统: StyleHub (时尚电商)

### 平台
- 类型: iOS & Android 应用
- 技术栈: React Native / Flutter

### UI 风格
- 主风格: Clean Modern
- 关键词: 简洁、大胆、时尚、易浏览
- 性能: Excellent | 可访问性: WCAG AA

### 配色方案
- Primary: #E11D48 (玫瑰红)
- Secondary: #FB7185 (浅玫瑰)
- CTA: #9F1239 (深玫瑰)
- Background: #FFFFFF (白)
- Surface: #F8FAFC (浅灰)
- Text: #1F2937 (深灰)
- Text Light: #6B7280 (灰)
- Border: #E5E7EB (边框灰)
- 说明: 时尚、优雅、女性向

### 字体配对
- 标题: Montserrat (700, 800)
- 正文: Inter (400, 500, 600)
- 氛围: 几何、现代、都市

### 核心页面

1. 首页
   - 顶部搜索栏
   - 轮播 Banner
   - 分类快捷入口 (网格)
   - 热门商品横向滚动
   - 限时优惠卡片
   - 底部导航栏

2. 商品列表
   - 筛选按钮 (顶部)
   - 排序选项
   - 双列网格布局
   - 商品卡片:
     - 图片
     - 品牌名
     - 商品名
     - 价格
     - 收藏按钮
   - 无限滚动加载

3. 商品详情
   - 图片轮播 (可缩放)
   - 商品信息
   - 尺码选择 (水平滚动)
   - 颜色选择
   - 加入购物车按钮
   - 商品描述
   - 评价摘要
   - 相关推荐

4. 购物车
   - 商品列表
   - 数量调整
   - 删除选项
   - 优惠券输入
   - 价格明细
   - 结算按钮

5. 结算
   - 地址选择
   - 配送方式
   - 支付方式
   - 订单摘要
   - 确认支付

6. 个人中心
   - 用户信息
   - 订单历史
   - 收藏列表
   - 地址管理
   - 设置

### 组件规范

**商品卡片**:
```
- 圆角: 12px
- 图片比例: 3:4
- 阴影: 无（扁平设计）
- 悬停: 轻微缩放 (1.02)
```

**按钮**:
```
- Primary: 玫瑰红背景 + 白字
- Secondary: 白背景 + 玫瑰红边框
- 圆角: 8px
- 高度: 48px (触摸友好)
- 字体: 600 weight
```

**底部导航**:
```
- 5 个标签: 首页、分类、购物车、收藏、我的
- 图标 + 标签
- 选中状态: 玫瑰红
- 未选中: 灰色
```

### 触摸目标
- 最小 48x48px
- 按钮间距 12px
- 列表项高度 64px

### 需要避免的反模式
- 不使用汉堡菜单（移动端用底部导航）
- 不隐藏价格和加入购物车按钮
- 不使用复杂的结账流程
- 不过度使用动画（性能考虑）
```

## 快速查询表

### 产品类型 → 设计系统

| 产品类型 | 风格 | 配色 | 字体 |
|---------|------|------|------|
| B2B SaaS | Soft UI | 科技蓝 | Poppins + Inter |
| 金融科技 | Dark Mode | 深蓝+金 | Inter |
| 电商 | Clean Modern | 品牌色 | Montserrat |
| 医疗 | Soft UI | 青蓝/Teal | Open Sans |
| 美容/SPA | Soft UI Evolution | 柔粉+鼠尾草绿 | Cormorant + Montserrat |
| 教育 | Claymorphism | 天蓝 | Nunito |
| 游戏 | Cyberpunk | 靛蓝+紫 | Rajdhani |
| 社交 | Vibrant | 多彩 | 系统字体 |

### 常见提示词 → 预期输出

| 用户提示 | 设计系统重点 |
|---------|-------------|
| "创建一个落地页" | 页面模式 + Hero + CTA 策略 |
| "设计一个仪表板" | 布局模式 + 数据可视化 + 导航 |
| "需要移动应用" | 触摸目标 + 底部导航 + 响应式 |
| "深色模式" | OLED 优化 + 高对比 + 配色调整 |
| "专业/企业" | 保守风格 + 蓝灰配色 + 系统字体 |
| "年轻/活力" | 大胆色彩 + 圆角 + 友好字体 |
| "奢华/高端" | 优雅字体 + 金/黑配色 + 大留白 |
