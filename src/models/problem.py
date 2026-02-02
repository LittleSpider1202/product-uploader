"""
问题记录模型
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


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
    element_selector: str | None = None     # 目标元素选择器
    expected_value: str | None = None       # 期望值
    actual_value: str | None = None         # 实际值
    screenshot: str | None = None           # 截图路径
    html_snapshot: str | None = None        # HTML 片段

    def to_dict(self) -> dict:
        return {
            "page_url": self.page_url,
            "element_selector": self.element_selector,
            "expected_value": self.expected_value,
            "actual_value": self.actual_value,
            "screenshot": self.screenshot,
            "html_snapshot": self.html_snapshot
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ProblemContext':
        return cls(
            page_url=data["page_url"],
            element_selector=data.get("element_selector"),
            expected_value=data.get("expected_value"),
            actual_value=data.get("actual_value"),
            screenshot=data.get("screenshot"),
            html_snapshot=data.get("html_snapshot")
        )


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

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "message": self.message,
            "context": self.context.to_dict(),
            "product_id": self.product_id,
            "solution_id": self.solution_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Problem':
        return cls(
            id=data["id"],
            type=ProblemType(data["type"]),
            message=data["message"],
            context=ProblemContext.from_dict(data["context"]),
            product_id=data.get("product_id"),
            solution_id=data.get("solution_id"),
            status=ProblemStatus(data.get("status", "open")),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            resolved_at=datetime.fromisoformat(data["resolved_at"]) if data.get("resolved_at") else None
        )
