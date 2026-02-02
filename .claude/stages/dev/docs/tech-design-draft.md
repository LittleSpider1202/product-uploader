# 技术方案设计

---

## 概览

### 文档信息

| 项目 | 内容 |
|------|------|
| 版本 | v1.0 |
| 状态 | 已完成 |
| 更新日期 | 2026-01-30 |

### 目录结构

| # | 章节 | 概要 |
|---|------|------|
| 1 | 方案框架 | 架构、选型、协议、数据结构四大模块 |
| 2 | 技术选型 | ✅ Python + Playwright + JSON |
| 3 | 架构设计 | ✅ 三层架构（CLI / Core / Infra） |
| 4 | 协议设计 | ✅ 调用协议、事件机制、错误处理 |
| 5 | 数据结构设计 | ✅ Product、Problem、Solution |
| 6 | Playwright 特性 | 跨浏览器、自动等待、codegen 录制 |
| 7 | 待解决问题 | 登录态管理（编码阶段验证） |
| 8 | 下一步 | 开始编码 |

### 快速导航

- **技术选型**：见第 2 节
- **架构设计**：见第 3 节
- **协议设计**：见第 4 节
- **数据模型**：见第 5 节
- **目录结构**：见第 3.4 节
- **错误码规范**：见第 4.4 节
- **信任等级**：见第 5.5 节

---

## 1. 方案框架

| 章节 | 内容 | 状态 |
|------|------|------|
| 1. 架构设计 | 模块划分、整体结构 | ✅ 已完成 |
| 2. 技术选型 | 语言、框架、依赖库 | ✅ 已确定 |
| 3. 协议设计 | 模块间通信、事件/消息格式、错误处理 | ✅ 已完成 |
| 4. 数据结构设计 | 核心实体字段定义、存储格式 | ✅ 已完成 |

---

## 2. 技术选型（已确定）

| 项目 | 选型 | 理由 |
|------|------|------|
| 开发语言 | **Python** | 简单易用，Playwright 支持良好 |
| 浏览器控制 | **Playwright** | 跨浏览器、自动等待、codegen 录制 |
| 数据存储 | **JSON 文件** | MVP 简单可调试，后续可迁移 SQLite |

---

## 3. 架构设计（已完成）

### 3.1 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI 层                               │
│  ┌─────────────────┐  ┌─────────────────────────────────┐  │
│  │ InteractiveShell│  │            Flows                 │  │
│  │   (主入口)       │  │  ┌─────────┐ ┌─────────────┐   │  │
│  │                 │──▶│  │ Collect │ │   Upload    │   │  │
│  │  - 欢迎界面     │  │  │  Flow   │ │    Flow     │   │  │
│  │  - 菜单导航     │  │  └─────────┘ └─────────────┘   │  │
│  │  - 快捷命令     │  │  ┌─────────┐ ┌─────────────┐   │  │
│  └─────────────────┘  │  │  Learn  │ │  Knowledge  │   │  │
│                       │  │  Flow   │ │    Flow     │   │  │
│                       │  └─────────┘ └─────────────┘   │  │
│                       └─────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                        Core 层                               │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────────────┐  │
│  │  Collector  │  │   Filler    │  │  LearningEngine   │  │
│  │             │  │             │  │                   │  │
│  │ - 页面解析  │  │ - 表单填充  │  │ - 批量学习(初始化)│  │
│  │ - 数据提取  │  │ - 问题检测  │  │ - 增量学习(问题)  │  │
│  │ - 格式转换  │  │ - 进度追踪  │  │ - codegen 集成    │  │
│  └─────────────┘  └─────────────┘  └───────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                       Infra 层                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │
│  │   Browser   │  │ KnowledgeBase│  │    Storage     │    │
│  │             │  │             │  │                 │    │
│  │ - Playwright│  │ - 问题库    │  │ - 商品数据      │    │
│  │ - 会话管理  │  │ - 方案库    │  │ - 配置文件      │    │
│  │ - 登录态    │  │ - 信任等级  │  │ - 日志记录      │    │
│  └─────────────┘  └─────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 模块职责

#### CLI 层

| 模块 | 职责 | 说明 |
|------|------|------|
| InteractiveShell | 主入口 | 欢迎界面、菜单导航、状态显示 |
| CollectFlow | 采集流程 | 引导用户完成商品采集 |
| UploadFlow | 上架流程 | 引导用户完成商品上架 |
| LearnFlow | 学习流程 | 批量学习 / 问题学习入口 |
| KnowledgeFlow | 知识库管理 | 查看、编辑、导出知识库 |

#### Core 层

| 模块 | 职责 | 说明 |
|------|------|------|
| Collector | 商品采集 | 解析淘宝页面，提取商品信息 |
| Filler | 表单填充 | 自动填写上架表单，检测异常 |
| LearningEngine | 学习引擎 | 统一处理批量学习和增量学习 |

#### Infra 层

| 模块 | 职责 | 说明 |
|------|------|------|
| Browser | 浏览器控制 | Playwright 封装，会话管理 |
| KnowledgeBase | 知识库 | 问题库、方案库、信任等级管理 |
| Storage | 存储 | 商品数据、配置、日志的持久化 |

### 3.3 调用关系

```
用户
  │
  ▼
InteractiveShell ──▶ Flows ──▶ Core ──▶ Infra
                       │         │         │
                       │         │         ▼
                       │         │     Browser (Playwright)
                       │         │         │
                       │         ▼         ▼
                       │    LearningEngine ◀──▶ KnowledgeBase
                       │         │
                       ▼         ▼
                    Collector / Filler ──▶ Storage
```

**关键调用链：**

1. **采集流程**：Shell → CollectFlow → Collector → Browser → Storage
2. **上架流程**：Shell → UploadFlow → Filler → Browser → KnowledgeBase
3. **学习流程**：Shell → LearnFlow → LearningEngine → Browser → KnowledgeBase
4. **问题处理**：Filler 检测异常 → LearningEngine → codegen → KnowledgeBase

### 3.4 目录结构

```
ecom/
├── main.py                     # 入口
├── cli/
│   ├── __init__.py
│   ├── shell.py                # InteractiveShell
│   ├── ui.py                   # 终端 UI 组件（菜单、进度条等）
│   ├── flows/                  # 交互流程
│   │   ├── __init__.py
│   │   ├── base.py             # BaseFlow 基类
│   │   ├── collect.py          # CollectFlow
│   │   ├── upload.py           # UploadFlow
│   │   ├── learn.py            # LearnFlow
│   │   └── knowledge.py        # KnowledgeFlow
│   └── shortcuts/              # 快捷命令（高级用户）
│       ├── __init__.py
│       └── commands.py
├── core/
│   ├── __init__.py
│   ├── collector.py            # 商品采集
│   ├── filler.py               # 表单填充
│   └── learning_engine.py      # 统一学习引擎
├── infra/
│   ├── __init__.py
│   ├── browser.py              # Playwright 封装
│   ├── knowledge/
│   │   ├── __init__.py
│   │   ├── base.py             # KnowledgeBase
│   │   ├── problem.py          # 问题库
│   │   └── solution.py         # 方案库
│   └── storage/
│       ├── __init__.py
│       ├── product.py          # 商品数据存储
│       └── config.py           # 配置管理
├── models/
│   ├── __init__.py
│   ├── product.py              # 商品数据模型
│   ├── problem.py              # 问题数据模型
│   └── solution.py             # 方案数据模型
├── data/                       # 数据目录
│   ├── products/               # 商品数据
│   ├── problems/               # 问题记录
│   ├── solutions/              # 解决方案
│   └── config.json             # 全局配置
└── tests/
    └── ...
```

### 3.5 核心类设计

#### LearningEngine（统一学习引擎）

```python
class LearningEngine:
    """统一学习引擎，支持批量学习和增量学习"""

    def __init__(self, browser: Browser, knowledge_base: KnowledgeBase):
        self.browser = browser
        self.knowledge_base = knowledge_base

    # === 批量学习（初始化阶段）===
    def batch_learn(self, target_url: str) -> LearnResult:
        """批量学习：初始化时探索页面结构"""
        pass

    # === 增量学习（问题处理）===
    def learn_from_problem(self, problem: Problem) -> Solution:
        """增量学习：从问题中学习解决方案"""
        pass

    # === Codegen 集成 ===
    def start_recording(self) -> RecordingSession:
        """启动 codegen 录制"""
        pass

    def stop_recording(self, session: RecordingSession) -> Solution:
        """停止录制，生成方案"""
        pass

    # === 方案验证 ===
    def verify_solution(self, solution: Solution) -> VerifyResult:
        """验证方案有效性"""
        pass

    def promote_solution(self, solution_id: str, new_level: TrustLevel):
        """提升方案信任等级"""
        pass
```

#### BaseFlow（交互流程基类）

```python
class BaseFlow:
    """交互流程基类"""

    def __init__(self, ui: UI):
        self.ui = ui

    def run(self) -> FlowResult:
        """执行流程"""
        raise NotImplementedError

    def confirm(self, message: str) -> bool:
        """确认操作"""
        return self.ui.confirm(message)

    def select(self, options: List[str], prompt: str) -> int:
        """选择菜单"""
        return self.ui.select(options, prompt)

    def input(self, prompt: str, default: str = None) -> str:
        """输入文本"""
        return self.ui.input(prompt, default)
```

---

## 4. 协议设计（已完成）

### 4.1 模块间调用协议

```
┌────────────────────────────────────────────────────────────┐
│  调用方向：CLI → Core → Infra（单向依赖）                   │
├────────────────────────────────────────────────────────────┤
│  返回方式：                                                 │
│  ├─ 同步返回：Result 对象（成功/失败 + 数据/错误）          │
│  └─ 异步通知：Event 回调（进度、状态变化）                  │
└────────────────────────────────────────────────────────────┘
```

**设计原则：**
- 上层调用下层，禁止反向依赖
- 下层通过事件通知上层，解耦通信
- 所有调用返回统一的 Result 结构

### 4.2 统一返回结构

```python
from dataclasses import dataclass
from typing import TypeVar, Generic

T = TypeVar('T')

@dataclass
class Result(Generic[T]):
    """统一返回结构"""
    success: bool
    data: T | None = None
    error: Error | None = None

    @staticmethod
    def ok(data: T) -> 'Result[T]':
        return Result(success=True, data=data)

    @staticmethod
    def fail(error: 'Error') -> 'Result[T]':
        return Result(success=False, error=error)


@dataclass
class Error:
    """错误信息"""
    code: str           # 错误码，如 "B_TIMEOUT"
    message: str        # 人类可读的错误信息
    recoverable: bool   # 是否可恢复
    context: dict       # 上下文信息（用于调试/学习）
```

### 4.3 事件机制

#### 事件定义

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

@dataclass
class Event:
    """事件基类"""
    type: str
    timestamp: datetime
    payload: dict


class EventListener(Protocol):
    """事件监听器协议"""
    def on_event(self, event: Event) -> None: ...


class EventBus:
    """事件总线"""
    def __init__(self):
        self._listeners: list[EventListener] = []

    def subscribe(self, listener: EventListener) -> None:
        self._listeners.append(listener)

    def publish(self, event: Event) -> None:
        for listener in self._listeners:
            listener.on_event(event)
```

#### 事件类型

| 事件类型 | 触发者 | 监听者 | payload |
|----------|--------|--------|---------|
| `progress` | Core 层 | Flow | `{step: int, total: int, message: str}` |
| `problem` | Filler | Flow / LearningEngine | `{problem_type: str, element: str, context: dict}` |
| `solution` | LearningEngine | KnowledgeBase | `{solution_id: str, success: bool, execution_time: float}` |
| `login_expired` | Browser | Flow | `{session_id: str}` |
| `status_change` | Core 层 | Flow | `{old_status: str, new_status: str}` |

### 4.4 错误码规范

| 前缀 | 模块 | 错误码示例 | 说明 |
|------|------|------------|------|
| `B_` | Browser | `B_TIMEOUT` | 请求超时 |
| | | `B_LOGIN_EXPIRED` | 登录态失效 |
| | | `B_NETWORK_ERROR` | 网络错误 |
| `C_` | Collector | `C_PARSE_FAILED` | 页面解析失败 |
| | | `C_ELEMENT_NOT_FOUND` | 元素未找到 |
| | | `C_INVALID_URL` | 无效的商品链接 |
| `F_` | Filler | `F_FIELD_MISMATCH` | 字段不匹配 |
| | | `F_SUBMIT_BLOCKED` | 提交被阻止 |
| | | `F_VALIDATION_ERROR` | 表单验证失败 |
| `K_` | KnowledgeBase | `K_SOLUTION_NOT_FOUND` | 方案未找到 |
| | | `K_SOLUTION_FAILED` | 方案执行失败 |
| `S_` | Storage | `S_WRITE_FAILED` | 写入失败 |
| | | `S_READ_FAILED` | 读取失败 |
| | | `S_NOT_FOUND` | 记录不存在 |

### 4.5 错误处理策略

| 错误码 | 处理策略 | recoverable | 处理层 |
|--------|----------|-------------|--------|
| `B_TIMEOUT` | 自动重试 3 次，间隔递增 | true | Infra |
| `B_NETWORK_ERROR` | 自动重试 3 次 | true | Infra |
| `B_LOGIN_EXPIRED` | 暂停任务，触发 `login_expired` 事件 | true | Core → Flow |
| `C_ELEMENT_NOT_FOUND` | 触发 `problem` 事件，等待方案 | true | Core |
| `F_FIELD_MISMATCH` | 触发 `problem` 事件，等待方案 | true | Core |
| `F_SUBMIT_BLOCKED` | 记录日志，人工介入 | false | Flow |
| `S_WRITE_FAILED` | 抛出异常，终止流程 | false | Flow |

### 4.6 重试机制

```python
from dataclasses import dataclass, field

@dataclass
class RetryPolicy:
    """重试策略"""
    max_attempts: int = 3
    base_delay: float = 1.0           # 基础延迟（秒）
    exponential: bool = True          # 是否指数退避
    max_delay: float = 30.0           # 最大延迟（秒）
    retryable_codes: list[str] = field(default_factory=lambda: [
        "B_TIMEOUT",
        "B_NETWORK_ERROR",
    ])

    def get_delay(self, attempt: int) -> float:
        """计算第 n 次重试的延迟"""
        if self.exponential:
            delay = self.base_delay * (2 ** attempt)
        else:
            delay = self.base_delay
        return min(delay, self.max_delay)
```

**重试流程：**

```
请求失败
    │
    ▼
错误码在 retryable_codes 中？
    │
   是 ────▶ 重试次数 < max_attempts？
    │              │
   否             是 ────▶ 等待 delay ────▶ 重试
    │              │
    ▼             否
返回错误          │
    ◀─────────────┘
```

---

## 5. 数据结构设计（已完成）

### 5.1 实体关系

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   Product   │       │   Problem   │       │  Solution   │
│  (商品数据)  │       │  (问题记录)  │       │ (解决方案)   │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id          │       │ id          │──────▶│ id          │
│ source_url  │       │ type        │       │ problem_type│
│ title       │       │ element     │       │ steps[]     │
│ price       │       │ context     │       │ trust_level │
│ skus[]      │       │ product_id? │       │ stats       │
│ images[]    │       │ solution_id?│       │ created_at  │
│ ...         │       │ status      │       │ updated_at  │
└─────────────┘       └─────────────┘       └─────────────┘
```

### 5.2 Product（商品数据）

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class ProductStatus(Enum):
    DRAFT = "draft"           # 已采集，未上架
    UPLOADED = "uploaded"     # 已上架
    FAILED = "failed"         # 上架失败

@dataclass
class SKU:
    """SKU 规格"""
    id: str
    name: str                 # 规格名，如 "颜色: 红色"
    price: float
    stock: int
    image: str | None = None  # 规格图片

@dataclass
class Product:
    """商品数据"""
    id: str                           # 唯一标识
    source_url: str                   # 来源链接
    title: str                        # 商品标题
    price: float                      # 价格
    original_price: float | None      # 原价
    category: str | None              # 类目
    skus: list[SKU] = field(default_factory=list)
    images: list[str] = field(default_factory=list)         # 主图列表
    detail_images: list[str] = field(default_factory=list)  # 详情图
    description: str = ""             # 商品描述

    # 元信息
    status: ProductStatus = ProductStatus.DRAFT
    collected_at: datetime = field(default_factory=datetime.now)
    uploaded_at: datetime | None = None

    # 扩展字段（平台特有属性）
    extra: dict = field(default_factory=dict)
```

### 5.3 Problem（问题记录）

```python
class ProblemType(Enum):
    """问题类型"""
    ELEMENT_NOT_FOUND = "element_not_found"    # 元素未找到
    FIELD_MISMATCH = "field_mismatch"          # 字段不匹配
    VALIDATION_ERROR = "validation_error"      # 验证失败
    UNEXPECTED_POPUP = "unexpected_popup"      # 意外弹窗
    PAGE_CHANGED = "page_changed"              # 页面结构变化
    UNKNOWN = "unknown"                        # 未知问题

class ProblemStatus(Enum):
    """问题状态"""
    OPEN = "open"           # 待处理
    SOLVING = "solving"     # 处理中（录制中）
    SOLVED = "solved"       # 已解决
    IGNORED = "ignored"     # 已忽略

@dataclass
class ProblemContext:
    """问题上下文"""
    page_url: str                    # 发生问题的页面
    element_selector: str | None     # 目标元素选择器
    expected_value: str | None       # 期望值
    actual_value: str | None         # 实际值
    screenshot: str | None           # 截图路径
    html_snapshot: str | None        # HTML 片段

@dataclass
class Problem:
    """问题记录"""
    id: str
    type: ProblemType
    message: str                      # 问题描述
    context: ProblemContext

    # 关联
    product_id: str | None = None     # 关联的商品
    solution_id: str | None = None    # 匹配的方案

    # 状态
    status: ProblemStatus = ProblemStatus.OPEN
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: datetime | None = None
```

### 5.4 Solution（解决方案）

```python
class TrustLevel(Enum):
    """信任等级"""
    NEW = "new"             # 新方案，需人工确认
    TESTING = "testing"     # 测试中，自动执行但需验证
    TRUSTED = "trusted"     # 可信任，完全自动执行
    FAILED = "failed"       # 已失效

class StepAction(Enum):
    """操作类型"""
    CLICK = "click"
    FILL = "fill"
    SELECT = "select"
    WAIT = "wait"
    SCROLL = "scroll"
    HOVER = "hover"
    PRESS = "press"         # 按键

@dataclass
class Step:
    """操作步骤"""
    action: StepAction
    selector: str                     # 元素选择器
    value: str | None = None          # 输入值（fill/select 用）
    timeout: int = 5000               # 超时时间（ms）
    optional: bool = False            # 是否可选步骤

@dataclass
class SolutionStats:
    """方案统计"""
    total_runs: int = 0               # 总执行次数
    success_count: int = 0            # 成功次数
    fail_count: int = 0               # 失败次数
    last_run_at: datetime | None = None
    last_success_at: datetime | None = None

    @property
    def success_rate(self) -> float:
        if self.total_runs == 0:
            return 0.0
        return self.success_count / self.total_runs

@dataclass
class Solution:
    """解决方案"""
    id: str
    problem_type: ProblemType         # 解决的问题类型
    name: str                         # 方案名称
    description: str                  # 方案描述

    # 匹配条件
    match_rules: dict                 # 匹配规则（如 URL 模式、元素特征）

    # 执行步骤
    steps: list[Step]

    # 信任等级
    trust_level: TrustLevel = TrustLevel.NEW

    # 统计
    stats: SolutionStats = field(default_factory=SolutionStats)

    # 元信息
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "codegen"       # 创建方式：codegen / manual
```

### 5.5 信任等级流转规则

```
┌─────┐   录制完成   ┌─────────┐   连续成功3次   ┌─────────┐
│ NEW │ ──────────▶ │ TESTING │ ──────────────▶ │ TRUSTED │
└─────┘             └─────────┘                 └─────────┘
                         │                           │
                         │ 失败                      │ 失败2次
                         ▼                           ▼
                    ┌────────┐                  ┌────────┐
                    │ FAILED │ ◀────────────── │ FAILED │
                    └────────┘   降级回 NEW     └────────┘
```

**流转条件：**

| 当前状态 | 目标状态 | 条件 |
|----------|----------|------|
| NEW | TESTING | 录制完成，首次验证通过 |
| TESTING | TRUSTED | 连续成功执行 3 次 |
| TESTING | FAILED | 执行失败 |
| TRUSTED | FAILED | 连续失败 2 次 |
| FAILED | NEW | 人工修复后重新录制 |

### 5.6 存储结构

**MVP 采用 JSON 文件存储：**

```
data/
├── products/
│   ├── {product_id}.json       # 单个商品数据
│   └── index.json              # 索引文件（id, title, status, collected_at）
├── problems/
│   ├── {problem_id}.json       # 单个问题记录
│   └── index.json              # 索引文件
├── solutions/
│   ├── {solution_id}.json      # 单个方案
│   └── index.json              # 索引文件（含 trust_level 便于筛选）
└── config.json                 # 全局配置
```

**索引文件示例（solutions/index.json）：**

```json
{
  "solutions": [
    {
      "id": "sol_001",
      "name": "处理类目选择弹窗",
      "problem_type": "unexpected_popup",
      "trust_level": "trusted",
      "success_rate": 0.95,
      "updated_at": "2026-01-30T10:00:00"
    }
  ]
}
```

---

## 6. Playwright 关键特性

### 6.1 核心能力

| 特性 | 说明 |
|------|------|
| 跨浏览器 | Chromium / Firefox / WebKit |
| 自动等待 | 内置智能等待，无需手动 sleep |
| 网络拦截 | 可拦截/修改请求响应 |
| 多上下文 | 单浏览器多账号隔离 |
| 截图/录屏 | 内置截图和视频录制 |

### 6.2 Codegen 录制工具

**启动命令：**

```bash
playwright codegen https://www.taobao.com
```

**功能：**
- 操作录制：自动记录点击、输入、选择等操作
- 代码生成：实时生成 Python 代码
- 选择器推荐：自动生成最优选择器
- 断言生成：可添加断言验证

**对本项目的价值：**
- 学习页面结构，了解淘宝上架页面的元素选择器
- 快速原型，先录制再优化代码
- 问题调试，遇到定位失败时找到正确选择器
- **知识库沉淀**：人工解决后，用 codegen 录制操作，沉淀为自动化方案

---

## 7. 待解决问题

### 7.1 已解决

| 问题 | 状态 | 说明 |
|------|------|------|
| codegen 交互设计 | ✅ 已完成 | 见 PRD v1.4 第 6.4 节 |
| 模块划分 | ✅ 已完成 | 见第 3 节架构设计 |
| 错误处理机制 | ✅ 已完成 | 见第 4.5 节 |
| 知识库存储格式 | ✅ 已完成 | JSON 文件，见第 5.6 节 |

### 7.2 待解决

| 问题 | 说明 | 计划 |
|------|------|------|
| 登录态管理 | 如何获取和维护淘宝登录状态 | 编码阶段验证 |

---

## 8. 下一步

1. ✅ ~~技术选型~~（已完成）
2. ✅ ~~架构设计~~（已完成）
3. ✅ ~~协议设计~~（已完成）
4. ✅ ~~数据结构设计~~（已完成）
5. **开始编码**：从 Infra 层开始，自底向上实现

**编码顺序建议：**

```
1. models/          # 数据模型
2. infra/storage/   # 存储层
3. infra/browser/   # 浏览器封装
4. infra/knowledge/ # 知识库
5. core/            # 业务逻辑
6. cli/             # 交互层
```

---

## 更新记录

| 日期 | 内容 |
|------|------|
| 2026-01-29 | 初始草稿，确定 Python + Playwright 选型 |
| 2026-01-30 | codegen 交互设计已补充到 PRD v1.1 |
| 2026-01-30 | 学习驱动初始化设计已补充到 PRD v1.2 |
| 2026-01-30 | 新增概览章节，支持动态加载 |
| 2026-01-30 | 完成架构设计 v2（三层架构 + 统一学习引擎） |
| 2026-01-30 | 完成协议设计（调用协议、事件机制、错误处理） |
| 2026-01-30 | 完成数据结构设计（Product、Problem、Solution） |
