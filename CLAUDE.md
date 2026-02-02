# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

**淘宝商品一键上架工具** - 帮助天猫卖家快速复制淘宝商品到自己店铺的 CLI 工具。

## 框架依赖

本项目遵循 `D:\ai\CLAUDE.md` 中定义的 AI Agent 协作框架，采用阶段制开发：

- 需求(req) → 设计(design) → 研发(dev) → 测试(test)

## 阶段管理

使用 `/stage` 命令管理项目阶段：

| 命令 | 说明 |
|------|------|
| `/stage` | 查看当前阶段状态 |
| `/stage ok` | 提交产出，请求 review |
| `/stage pass` | 审核通过，进入下一阶段 |

## 当前状态

- **阶段**: 研发阶段 (v3)
- **状态**: MVP 代码框架已完成
- **技术设计**: `.claude/stages/develop/docs/tech-design-draft.md`

## 代码结构

```
src/
├── main.py                 # 入口
├── cli/                    # CLI 交互层
│   ├── shell.py            # 主 Shell
│   ├── ui.py               # UI 组件
│   └── flows/              # 交互流程
│       ├── collect.py      # 采集流程
│       ├── upload.py       # 上架流程
│       ├── learn.py        # 学习流程
│       └── knowledge.py    # 知识库管理
├── core/                   # 业务逻辑层
│   ├── collector.py        # 商品采集
│   ├── filler.py           # 表单填充
│   ├── learning_engine.py  # 学习引擎
│   └── events.py           # 事件机制
├── infra/                  # 基础设施层
│   ├── browser.py          # Playwright 封装
│   ├── storage/            # 数据存储
│   └── knowledge/          # 知识库
└── models/                 # 数据模型
    ├── product.py          # 商品模型
    ├── problem.py          # 问题模型
    ├── solution.py         # 方案模型
    └── result.py           # 统一返回结构
```

## 运行方式

```bash
# 安装依赖
pip install -r requirements.txt
playwright install chromium

# 运行
python src/main.py
```

## 下一步

1. 测试核心流程
2. 完善页面选择器（淘宝/天猫页面结构）
3. 优化用户体验
