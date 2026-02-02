# 淘宝商品一键上架工具

帮助天猫卖家快速复制淘宝商品到自己店铺的工具。

## 项目结构

```
product_uploader/
├── frontend/              # Next.js 前端应用
│   ├── src/
│   │   ├── app/           # 页面路由
│   │   │   ├── upload/    # 上架流程（5步）
│   │   │   ├── records/   # 上架记录
│   │   │   ├── templates/ # 模板管理
│   │   │   ├── settings/  # 系统设置
│   │   │   └── onboarding/# 新手引导
│   │   ├── components/    # 通用组件
│   │   └── lib/           # 工具函数
│   └── package.json
├── src/                   # Python 后端（CLI）
│   ├── cli/               # CLI 交互层
│   ├── core/              # 业务逻辑层
│   ├── infra/             # 基础设施层
│   └── models/            # 数据模型
├── data/                  # 数据存储
├── logs/                  # 日志文件
└── .claude/               # 项目阶段管理
    └── stages/            # 各阶段产出文档
```

## 前端页面

基于 Next.js 14 + Tailwind CSS + shadcn/ui 构建，橙色主题风格。

### 上架流程（5步）

| 步骤 | 页面 | 功能 |
|------|------|------|
| Step 1 | `/upload` | 采集商品：输入链接采集、关联数据源、关联模板 |
| Step 2 | `/upload/step2` | 选择类目：三级类目选择器 |
| Step 3 | `/upload/step3` | 确认字段：必填标记、图片上传到千牛素材库 |
| Step 4 | `/upload/step4` | 编辑SKU：价格策略、库存设置 |
| Step 5 | `/upload/step5` | 提交上架：上架检查、上架方式选择 |

### 核心功能

**Step 1 - 采集商品**
- 输入淘宝链接一键采集
- 预览：SKU规格、参数信息、主图/视频、商详图片
- 关联数据源：匹配商家编码、有机编码等
- 关联模板：预填发货地、物流模板等

**Step 3 - 确认字段**
- 根据淘宝 schema 标记必填项（红色 *）
- 树形目录选择器：上传图片到千牛素材库
- 一键上传所有图片

**Step 4 - 编辑SKU**
- 定价方式：固定值 / 价格策略
- 内置策略：上调10%/20%/30%、下调10%、整数抹零.9
- 实时显示价格变动百分比

**Step 5 - 提交上架**
- 上架前检查清单
- 商品预览
- 上架方式：立刻上架 / 定时上架 / 放入仓库

### 其他页面

- `/` - 首页：快捷入口、最近记录
- `/records` - 上架记录：历史记录查询
- `/settings` - 系统设置：店铺授权、数据源配置、类目模板管理
- `/onboarding` - 新手引导：首次使用引导流程

## 快速开始

### 前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:3000

### 后端（CLI）

```bash
pip install -r requirements.txt
playwright install chromium
python src/main.py
```

## 技术栈

**前端**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui
- Lucide Icons

**后端**
- Python 3.10+
- Playwright (浏览器自动化)
- Rich (CLI UI)

## 开发文档

- MRD（市场需求）: `.claude/stages/requirement/mrd-v2.md`
- PRD（产品设计）: `.claude/stages/design/prd-v3.md`
- 技术设计: `.claude/stages/develop/docs/tech-design-draft.md`

## License

MIT
