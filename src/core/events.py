"""
事件机制
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol, Callable


@dataclass
class Event:
    """事件基类"""
    type: str
    timestamp: datetime = field(default_factory=datetime.now)
    payload: dict = field(default_factory=dict)


class EventListener(Protocol):
    """事件监听器协议"""
    def on_event(self, event: Event) -> None: ...


class EventBus:
    """事件总线"""

    def __init__(self):
        self._listeners: list[EventListener] = []
        self._handlers: dict[str, list[Callable[[Event], None]]] = {}

    def subscribe(self, listener: EventListener) -> None:
        """订阅所有事件"""
        self._listeners.append(listener)

    def on(self, event_type: str, handler: Callable[[Event], None]) -> None:
        """订阅特定类型事件"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def publish(self, event: Event) -> None:
        """发布事件"""
        # 通知全局监听器
        for listener in self._listeners:
            listener.on_event(event)

        # 通知特定类型处理器
        if event.type in self._handlers:
            for handler in self._handlers[event.type]:
                handler(event)

    def emit(self, event_type: str, **payload) -> None:
        """便捷方法：发送事件"""
        self.publish(Event(type=event_type, payload=payload))


# 预定义事件类型
class EventTypes:
    """事件类型常量"""
    PROGRESS = "progress"              # 进度更新
    PROBLEM = "problem"                # 发现问题
    SOLUTION = "solution"              # 方案执行结果
    LOGIN_EXPIRED = "login_expired"    # 登录过期
    STATUS_CHANGE = "status_change"    # 状态变化
    RECORDING_START = "recording_start"  # 开始录制
    RECORDING_STOP = "recording_stop"    # 停止录制
