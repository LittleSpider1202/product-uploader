"""
交互流程基类
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from src.cli.ui import UI


class FlowStatus(Enum):
    """流程状态"""
    SUCCESS = "success"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class FlowResult:
    """流程结果"""
    status: FlowStatus
    message: str = ""
    data: dict = None

    @staticmethod
    def success(message: str = "", data: dict = None) -> 'FlowResult':
        return FlowResult(FlowStatus.SUCCESS, message, data)

    @staticmethod
    def cancelled(message: str = "") -> 'FlowResult':
        return FlowResult(FlowStatus.CANCELLED, message)

    @staticmethod
    def failed(message: str) -> 'FlowResult':
        return FlowResult(FlowStatus.FAILED, message)


class BaseFlow(ABC):
    """交互流程基类"""

    def __init__(self, ui: UI):
        self.ui = ui

    @abstractmethod
    async def run(self) -> FlowResult:
        """执行流程"""
        pass

    def confirm(self, message: str, default: bool = True) -> bool:
        """确认操作"""
        return self.ui.confirm(message, default)

    def select(self, options: list[str], prompt: str = "请选择") -> int:
        """选择菜单"""
        return self.ui.select(options, prompt)

    def input(self, prompt: str, default: str = None) -> str:
        """输入文本"""
        return self.ui.input(prompt, default)
