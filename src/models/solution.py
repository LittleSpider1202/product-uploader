"""
解决方案模型
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .problem import ProblemType


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

    def to_dict(self) -> dict:
        return {
            "action": self.action.value,
            "selector": self.selector,
            "value": self.value,
            "timeout": self.timeout,
            "optional": self.optional
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Step':
        return cls(
            action=StepAction(data["action"]),
            selector=data["selector"],
            value=data.get("value"),
            timeout=data.get("timeout", 5000),
            optional=data.get("optional", False)
        )


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

    def record_run(self, success: bool):
        """记录一次执行"""
        self.total_runs += 1
        self.last_run_at = datetime.now()
        if success:
            self.success_count += 1
            self.last_success_at = datetime.now()
        else:
            self.fail_count += 1

    def to_dict(self) -> dict:
        return {
            "total_runs": self.total_runs,
            "success_count": self.success_count,
            "fail_count": self.fail_count,
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "last_success_at": self.last_success_at.isoformat() if self.last_success_at else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'SolutionStats':
        return cls(
            total_runs=data.get("total_runs", 0),
            success_count=data.get("success_count", 0),
            fail_count=data.get("fail_count", 0),
            last_run_at=datetime.fromisoformat(data["last_run_at"]) if data.get("last_run_at") else None,
            last_success_at=datetime.fromisoformat(data["last_success_at"]) if data.get("last_success_at") else None
        )


@dataclass
class Solution:
    """解决方案"""
    id: str
    problem_type: ProblemType         # 解决的问题类型
    name: str                         # 方案名称
    description: str                  # 方案描述

    # 匹配条件
    match_rules: dict = field(default_factory=dict)  # 匹配规则（如 URL 模式、元素特征）

    # 执行步骤
    steps: list[Step] = field(default_factory=list)

    # 信任等级
    trust_level: TrustLevel = TrustLevel.NEW

    # 统计
    stats: SolutionStats = field(default_factory=SolutionStats)

    # 元信息
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "codegen"       # 创建方式：codegen / manual

    # 用于信任等级流转的计数
    _consecutive_success: int = field(default=0, repr=False)
    _consecutive_fail: int = field(default=0, repr=False)

    def record_execution(self, success: bool):
        """记录执行结果，自动更新信任等级"""
        self.stats.record_run(success)
        self.updated_at = datetime.now()

        if success:
            self._consecutive_success += 1
            self._consecutive_fail = 0
            self._try_promote()
        else:
            self._consecutive_fail += 1
            self._consecutive_success = 0
            self._try_demote()

    def _try_promote(self):
        """尝试提升信任等级"""
        if self.trust_level == TrustLevel.NEW and self._consecutive_success >= 1:
            self.trust_level = TrustLevel.TESTING
        elif self.trust_level == TrustLevel.TESTING and self._consecutive_success >= 3:
            self.trust_level = TrustLevel.TRUSTED

    def _try_demote(self):
        """尝试降低信任等级"""
        if self.trust_level == TrustLevel.TESTING:
            self.trust_level = TrustLevel.FAILED
        elif self.trust_level == TrustLevel.TRUSTED and self._consecutive_fail >= 2:
            self.trust_level = TrustLevel.FAILED

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "problem_type": self.problem_type.value,
            "name": self.name,
            "description": self.description,
            "match_rules": self.match_rules,
            "steps": [step.to_dict() for step in self.steps],
            "trust_level": self.trust_level.value,
            "stats": self.stats.to_dict(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "_consecutive_success": self._consecutive_success,
            "_consecutive_fail": self._consecutive_fail
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Solution':
        solution = cls(
            id=data["id"],
            problem_type=ProblemType(data["problem_type"]),
            name=data["name"],
            description=data["description"],
            match_rules=data.get("match_rules", {}),
            steps=[Step.from_dict(s) for s in data.get("steps", [])],
            trust_level=TrustLevel(data.get("trust_level", "new")),
            stats=SolutionStats.from_dict(data.get("stats", {})),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now(),
            created_by=data.get("created_by", "codegen")
        )
        solution._consecutive_success = data.get("_consecutive_success", 0)
        solution._consecutive_fail = data.get("_consecutive_fail", 0)
        return solution
