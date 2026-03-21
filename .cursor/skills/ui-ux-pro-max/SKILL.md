---
name: ui-ux-pro-max
description: Provides design intelligence for building professional UI/UX across multiple platforms and frameworks. Use when building landing pages, dashboards, mobile apps, websites, or when the user mentions UI design, UX improvement, styling, color schemes, typography, or component design.
---

# UI/UX Pro Max

智能设计系统生成器，为多种平台提供专业 UI/UX 设计指导。

## 核心功能

- **67 种 UI 风格** - Glassmorphism, Claymorphism, Minimalism, Brutalism, Neumorphism, Bento Grid, Dark Mode 等
- **161 种配色方案** - 与产品类型一一对应的行业专用配色
- **57 种字体配对** - 精心策划的字体组合
- **25 种图表类型** - 仪表板和分析推荐
- **99 条 UX 指导原则** - 最佳实践、反模式和可访问性规则

## 使用场景

当用户请求以下任务时自动激活：
- 构建落地页、仪表板、移动端应用 UI
- 设计网站、选择配色方案、优化排版
- 改进 UI 组件、动画效果、交互体验

## 设计系统生成流程

```
用户请求 → 多域搜索 → 推理引擎 → 完整设计系统输出
```

### 1. 分析用户需求

识别关键信息：
- **产品类型**：SaaS、电商、金融、医疗、创意等
- **目标用户**：B2B、B2C、企业、消费者
- **平台**：Web、iOS、Android、小程序
- **风格偏好**：现代、简约、华丽、专业

### 2. 匹配设计要素

根据产品类型自动匹配：
- **页面模式**：落地页结构（Hero-Centric、Feature-Rich、Social Proof 等）
- **UI 风格**：从 67 种风格中选择最适合的
- **配色方案**：从 161 种配色中选择行业匹配的
- **字体配对**：从 57 种组合中选择

### 3. 生成设计系统

输出完整设计规范：

```markdown
## 设计系统: [产品名称]

### 页面模式
- 类型: [Hero-Centric / Feature-Rich / Social Proof]
- 结构: [Hero → Services → Testimonials → CTA]
- 转化策略: [Emotion-driven / Trust elements]

### UI 风格
- 主风格: [Soft UI Evolution / Glassmorphism / Minimalism]
- 关键词: [Soft shadows, subtle depth, calming]
- 性能: [Excellent] | 可访问性: [WCAG AA]

### 配色方案
- Primary: #[色值] (名称)
- Secondary: #[色值] (名称)
- CTA: #[色值] (名称)
- Background: #[色值] (名称)
- Text: #[色值] (名称)
- 说明: [配色理念]

### 字体配对
- 标题: [字体名称]
- 正文: [字体名称]
- 氛围: [Mood 描述]
- Google Fonts: [链接]

### 关键效果
- 阴影: [Soft shadows]
- 过渡: [Smooth transitions 200-300ms]
- 悬停状态: [Gentle hover states]

### 需要避免的反模式
- [反模式 1]
- [反模式 2]
- [反模式 3]

### 交付前检查清单
- [ ] 不使用表情符号作为图标（使用 SVG: Heroicons/Lucide）
- [ ] 所有可点击元素有 cursor-pointer
- [ ] 悬停状态有平滑过渡 (150-300ms)
- [ ] 浅色模式: 文本对比度最低 4.5:1
- [ ] 焦点状态对键盘导航可见
- [ ] 尊重 prefers-reduced-motion
- [ ] 响应式: 375px, 768px, 1024px, 1440px
```

## 技术栈支持

| 类别 | 技术栈 |
|------|--------|
| Web (HTML) | HTML + Tailwind (默认) |
| React 生态 | React, Next.js, shadcn/ui |
| Vue 生态 | Vue, Nuxt.js, Nuxt UI |
| 其他 Web | Svelte, Astro |
| iOS | SwiftUI |
| Android | Jetpack Compose |
| 跨平台 | React Native, Flutter |

用户可在提示中提及首选技术栈，或默认使用 HTML + Tailwind。

## 反模式清单（必须避免）

### 通用反模式
- ❌ 使用表情符号代替图标
- ❌ 缺少悬停/焦点状态
- ❌ 文本对比度不足
- ❌ 忽略键盘导航
- ❌ 忽略减少动画偏好

### 行业特定反模式
- **金融/银行**: 避免 AI 紫色/粉色渐变、霓虹色
- **医疗**: 避免过于鲜艳的颜色、复杂动画
- **企业/SaaS**: 避免过于华丽的效果

## 响应式断点

必须支持以下断点：
- **Mobile**: 375px
- **Tablet**: 768px
- **Desktop**: 1024px
- **Large**: 1440px

## 交互规范

### 过渡时间
- 快速反馈: 150ms
- 标准过渡: 200-300ms
- 复杂动画: 400-500ms

### 悬停状态
- 所有可点击元素必须有悬停状态
- 使用 `cursor: pointer`
- 平滑的颜色/阴影/缩放变化

### 焦点状态
- 键盘导航必须可见
- 使用 outline 或 ring 效果
- 对比度充足

## 资源参考

- **风格列表**: [styles.md](styles.md)
- **配色方案**: [colors.md](colors.md)
- **字体配对**: [typography.md](typography.md)
- **页面模式**: [patterns.md](patterns.md)
- **UX 指导原则**: [ux-guidelines.md](ux-guidelines.md)
- **使用示例**: [examples.md](examples.md)

## 示例提示词

```
为我的 SaaS 产品构建一个落地页
创建医疗分析仪表板
设计深色模式的金融科技应用
构建电商移动应用 UI
```

## 快速决策表

| 产品类型 | 推荐风格 | 推荐配色 | 推荐字体 |
|---------|---------|---------|---------|
| SaaS/B2B | Minimalism, Soft UI | 蓝色系、灰色系 | Inter, Roboto |
| 电商 | Clean, Modern | 品牌色+中性色 | Poppins, Open Sans |
| 金融科技 | Glassmorphism, Dark Mode | 深蓝、金色、绿色 | SF Pro, Inter |
| 医疗 | Soft UI, Clean | 蓝绿色、白色 | Roboto, Open Sans |
| 创意/设计 | Brutalism, Aurora | 鲜艳多彩 | Playfair, Montserrat |
| 美容/SPA | Soft UI Evolution | 柔粉色、鼠尾草绿 | Cormorant, Montserrat |
