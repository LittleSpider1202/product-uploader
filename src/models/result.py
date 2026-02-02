"""
统一返回结构
"""
from dataclasses import dataclass, field
from typing import TypeVar, Generic

T = TypeVar('T')


@dataclass
class Error:
    """错误信息"""
    code: str           # 错误码，如 "B_TIMEOUT"
    message: str        # 人类可读的错误信息
    recoverable: bool   # 是否可恢复
    context: dict = field(default_factory=dict)  # 上下文信息


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
    def fail(error: Error) -> 'Result[T]':
        return Result(success=False, error=error)

    @staticmethod
    def fail_with(code: str, message: str, recoverable: bool = True, context: dict = None) -> 'Result[T]':
        """便捷方法：直接用参数创建失败结果"""
        return Result.fail(Error(
            code=code,
            message=message,
            recoverable=recoverable,
            context=context or {}
        ))
