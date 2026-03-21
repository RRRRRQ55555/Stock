# UI 风格参考

完整 67 种 UI 风格清单。

## 通用风格 (49 种)

| # | 风格 | 最佳适用场景 |
|---|------|-------------|
| 1 | Minimalism & Swiss Style | 企业应用、仪表板、文档 |
| 2 | Neumorphism | 健康/养生应用、冥想平台 |
| 3 | Glassmorphism | 现代 SaaS、金融仪表板 |
| 4 | Brutalism | 设计作品集、艺术项目 |
| 5 | 3D & Hyperrealism | 游戏、产品展示、沉浸式体验 |
| 6 | Vibrant & Block-based | 初创公司、创意机构、游戏 |
| 7 | Dark Mode (OLED) | 夜间模式应用、编码平台 |
| 8 | Accessible & Ethical | 政府、医疗、教育 |
| 9 | Claymorphism | 教育应用、儿童应用、SaaS |
| 10 | Aurora UI | 现代 SaaS、创意机构 |
| 11 | Retro-Futurism | 游戏、娱乐、音乐平台 |
| 12 | Flat Design | Web 应用、移动应用、初创 MVP |
| 13 | Skeuomorphism | 传统应用、游戏、高端产品 |
| 14 | Liquid Glass | 高端 SaaS、高端电商 |
| 15 | Motion-Driven | 作品集网站、叙事平台 |
| 16 | Micro-interactions | 移动应用、触摸屏 UI |
| 17 | Inclusive Design | 公共服务、教育、医疗 |
| 18 | Zero Interface | 语音助手、AI 平台 |
| 19 | Soft UI Evolution | 现代企业应用、SaaS |
| 20 | Neubrutalism | Z 世代品牌、初创公司、Figma 风格 |
| 21 | Bento Box Grid | 仪表板、产品页面、作品集 |
| 22 | Y2K Aesthetic | 时尚品牌、音乐、Z 世代 |
| 23 | Cyberpunk UI | 游戏、科技产品、加密应用 |
| 24 | Organic Biophilic | 养生应用、可持续品牌 |
| 25 | AI-Native UI | AI 产品、聊天机器人、Copilots |
| 26 | Memphis Design | 创意机构、音乐、年轻品牌 |
| 27 | Vaporwave | 音乐平台、游戏、作品集 |
| 28 | Dimensional Layering | 仪表板、卡片布局、模态框 |
| 29 | Exaggerated Minimalism | 时尚、建筑、作品集 |
| 30 | Kinetic Typography | Hero 区域、营销网站 |
| 31 | Parallax Storytelling | 品牌叙事、产品发布 |
| 32 | Swiss Modernism 2.0 | 企业网站、建筑、编辑 |
| 33 | HUD / Sci-Fi FUI | 科幻游戏、太空科技、网络安全 |
| 34 | Pixel Art | 独立游戏、复古工具、创意 |
| 35 | Bento Grids | 产品功能、仪表板、个人 |
| 36 | Spatial UI (VisionOS) | 空间计算应用、VR/AR |
| 37 | E-Ink / Paper | 阅读应用、数字报纸 |
| 38 | Gen Z Chaos / Maximalism | Z 世代生活方式、音乐艺术家 |
| 39 | Biomimetic / Organic 2.0 | 可持续科技、生物科技、健康 |
| 40 | Anti-Polish / Raw Aesthetic | 创意作品集、艺术家网站 |
| 41 | Tactile Digital / Deformable UI | 现代移动应用、趣味品牌 |
| 42 | Nature Distilled | 养生品牌、可持续产品 |
| 43 | Interactive Cursor Design | 创意作品集、互动体验 |
| 44 | Voice-First Multimodal | 语音助手、无障碍应用 |
| 45 | 3D Product Preview | 电商、家具、时尚 |
| 46 | Gradient Mesh / Aurora Evolved | Hero 区域、背景、创意 |
| 47 | Editorial Grid / Magazine | 新闻网站、博客、杂志 |
| 48 | Chromatic Aberration / RGB Split | 音乐平台、游戏、科技 |
| 49 | Vintage Analog / Retro Film | 摄影、音乐/黑胶品牌 |

## 落地页风格 (8 种)

| # | 风格 | 最佳适用场景 |
|---|------|-------------|
| 1 | Hero-Centric Design | 视觉识别强的产品 |
| 2 | Conversion-Optimized | 潜在客户生成、销售页面 |
| 3 | Feature-Rich Showcase | SaaS、复杂产品 |
| 4 | Minimal & Direct | 简单产品、应用 |
| 5 | Social Proof-Focused | 服务、B2C 产品 |
| 6 | Interactive Product Demo | 软件、工具 |
| 7 | Trust & Authority | B2B、企业、咨询 |
| 8 | Storytelling-Driven | 品牌、机构、非营利 |

## BI/分析仪表板风格 (10 种)

| # | 风格 | 最佳适用场景 |
|---|------|-------------|
| 1 | Data-Dense Dashboard | 复杂数据分析 |
| 2 | Heat Map & Heatmap Style | 地理/行为数据 |
| 3 | Executive Dashboard | C 级摘要 |
| 4 | Real-Time Monitoring | 运营、DevOps |
| 5 | Drill-Down Analytics | 详细探索 |
| 6 | Comparative Analysis Dashboard | 并排比较 |
| 7 | Predictive Analytics | 预测、ML 洞察 |
| 8 | User Behavior Analytics | UX 研究、产品分析 |
| 9 | Financial Dashboard | 金融、会计 |
| 10 | Sales Intelligence Dashboard | 销售团队、CRM |

## 风格详细说明

### Glassmorphism

**特点**: 半透明背景、模糊效果、微妙边框
**技术实现**:
```css
background: rgba(255, 255, 255, 0.1);
backdrop-filter: blur(10px);
border: 1px solid rgba(255, 255, 255, 0.2);
```
**适用**: 现代 SaaS、金融仪表板、需要层次感的界面

### Neumorphism

**特点**: 柔和的阴影创造凸起/凹陷效果
**技术实现**:
```css
/* 凸起 */
box-shadow: 5px 5px 10px #d1d1d1, -5px -5px 10px #ffffff;

/* 凹陷 */
box-shadow: inset 5px 5px 10px #d1d1d1, inset -5px -5px 10px #ffffff;
```
**适用**: 健康应用、冥想平台、需要柔和触感的界面

### Brutalism

**特点**: 高对比度、粗边框、未加工的美学
**技术实现**:
```css
border: 3px solid #000;
box-shadow: 4px 4px 0 #000;
background: #ff00ff;
```
**适用**: 设计作品集、艺术项目、需要大胆声明的界面

### Minimalism

**特点**: 大量留白、简洁排版、有限的色彩
**技术实现**:
```css
background: #ffffff;
color: #1a1a1a;
font-family: system-ui, -apple-system, sans-serif;
```
**适用**: 企业应用、仪表板、内容为主的网站

### Claymorphism

**特点**: 柔和圆角、双色阴影、友好的外观
**技术实现**:
```css
border-radius: 20px;
box-shadow: 
  0 4px 0 rgba(0,0,0,0.1),
  0 8px 20px rgba(0,0,0,0.1);
background: linear-gradient(145deg, #ffffff, #f0f0f0);
```
**适用**: 教育应用、儿童应用、友好的 SaaS

### Dark Mode (OLED)

**特点**: 纯黑背景、高对比度、节能
**技术实现**:
```css
background: #000000;
color: #ffffff;
/* 避免纯黑上的纯灰，使用深色灰 */
secondary-bg: #1a1a1a;
```
**适用**: 夜间模式应用、编码平台、媒体消费应用

### Aurora UI

**特点**: 流动的渐变背景、动态色彩
**技术实现**:
```css
background: 
  radial-gradient(ellipse at top, #ff00ff, transparent),
  radial-gradient(ellipse at bottom, #00ffff, transparent);
animation: aurora 10s ease infinite;
```
**适用**: 现代 SaaS、创意机构、需要视觉冲击力的界面

### Soft UI Evolution

**特点**: 柔和的阴影、微妙的深度、平静的感觉
**技术实现**:
```css
box-shadow: 0 2px 8px rgba(0,0,0,0.04), 0 8px 24px rgba(0,0,0,0.06);
border-radius: 12px;
background: #ffffff;
```
**适用**: 现代企业应用、SaaS、需要专业但友好外观的界面

### Bento Grid

**特点**: 网格布局、卡片式组织、视觉层次
**技术实现**:
```css
display: grid;
grid-template-columns: repeat(4, 1fr);
gap: 16px;
.bento-card {
  border-radius: 16px;
  padding: 20px;
}
```
**适用**: 仪表板、产品页面、功能展示、作品集

### AI-Native UI

**特点**: 渐变边框、发光效果、未来感
**技术实现**:
```css
border: 1px solid transparent;
background: linear-gradient(#000, #000) padding-box,
            linear-gradient(135deg, #ff00ff, #00ffff) border-box;
box-shadow: 0 0 20px rgba(128, 0, 255, 0.3);
```
**适用**: AI 产品、聊天机器人、Copilots、科技产品

## 风格选择指南

### 根据产品类型选择

| 产品类型 | 首选风格 | 备选风格 |
|---------|---------|---------|
| 企业 SaaS | Minimalism | Soft UI Evolution |
| 金融科技 | Glassmorphism | Dark Mode |
| 医疗健康 | Soft UI | Clean/Minimal |
| 电商 | Clean Modern | Vibrant |
| 创意设计 | Brutalism | Aurora |
| 游戏 | Cyberpunk | 3D/Hyperrealism |
| 教育 | Claymorphism | Soft UI |
| 社交媒体 | Vibrant | Aurora |

### 根据目标用户选择

| 目标用户 | 推荐风格 |
|---------|---------|
| 企业/B2B | Minimalism, Swiss Style |
| 消费者/B2C | Soft UI, Clean |
| 开发者 | Dark Mode, Minimalism |
| 设计师 | Brutalism, Aurora |
| 儿童/教育 | Claymorphism, Playful |
| Z 世代 | Neubrutalism, Y2K, Maximalism |
