"""
日志模块

特性：
- run_id: 每次程序运行生成唯一 ID，追踪本次运行的所有日志
- trace_id: 追踪单个操作/请求的完整链路
- layer: 标记代码层级 (cli/core/infra)
- 自动文件轮转
- 结构化日志（JSON）
"""
import logging
import sys
import uuid
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from contextvars import ContextVar
import json
import traceback

# 全局 run_id - 程序启动时生成，标识本次运行
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:8]

# 上下文变量
_trace_id: ContextVar[str] = ContextVar("trace_id", default="")
_context: ContextVar[dict] = ContextVar("log_context", default={})

# 层级定义
class Layer:
    CLI = "cli"
    CORE = "core"
    INFRA = "infra"

# 模块 -> 层级映射
LAYER_MAP = {
    # CLI 层
    "shell": Layer.CLI,
    "ui": Layer.CLI,
    "flows": Layer.CLI,
    "collect_flow": Layer.CLI,
    "upload_flow": Layer.CLI,
    "learn_flow": Layer.CLI,
    "knowledge_flow": Layer.CLI,
    # Core 层
    "collector": Layer.CORE,
    "filler": Layer.CORE,
    "learning": Layer.CORE,
    "learning_engine": Layer.CORE,
    "events": Layer.CORE,
    # Infra 层
    "browser": Layer.INFRA,
    "storage": Layer.INFRA,
    "knowledge": Layer.INFRA,
    "logger": Layer.INFRA,
}


def get_layer(module_name: str) -> str:
    """根据模块名获取层级"""
    # 直接匹配
    if module_name in LAYER_MAP:
        return LAYER_MAP[module_name]
    # 尝试匹配最后一段
    parts = module_name.split(".")
    for part in reversed(parts):
        if part in LAYER_MAP:
            return LAYER_MAP[part]
    return "unknown"


def get_run_id() -> str:
    """获取当前运行 ID"""
    return RUN_ID


def new_trace_id() -> str:
    """生成新的 trace_id"""
    return uuid.uuid4().hex[:12]


def set_trace_id(trace_id: str):
    """设置当前 trace_id"""
    _trace_id.set(trace_id)


def get_trace_id() -> str:
    """获取当前 trace_id"""
    return _trace_id.get()


class LogConfig:
    """日志配置"""
    def __init__(
        self,
        log_dir: str = "logs",
        log_level: str = "DEBUG",
        console_level: str = "INFO",
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        console_output: bool = True,
    ):
        self.log_dir = Path(log_dir)
        self.log_level = getattr(logging, log_level.upper(), logging.DEBUG)
        self.console_level = getattr(logging, console_level.upper(), logging.INFO)
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.console_output = console_output


class JsonFormatter(logging.Formatter):
    """JSON 格式器 - 用于文件日志"""

    def format(self, record: logging.LogRecord) -> str:
        # 提取模块名（去掉 uploader. 前缀）
        logger_name = record.name
        module = logger_name.replace("uploader.", "") if logger_name.startswith("uploader.") else logger_name

        # 获取层级
        layer = getattr(record, "layer", None) or get_layer(module)

        log_data = {
            "time": datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "run_id": RUN_ID,
            "trace_id": _trace_id.get() or "-",
            "level": record.levelname,
            "layer": layer,
            "module": module,
            "message": record.getMessage(),
            "func": record.funcName,
            "line": record.lineno,
        }

        # 上下文数据
        ctx = _context.get()
        if ctx:
            log_data["ctx"] = ctx

        # 额外数据
        if hasattr(record, "data") and record.data:
            log_data["data"] = record.data

        # 异常信息
        if record.exc_info:
            log_data["exc"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "msg": str(record.exc_info[1]) if record.exc_info[1] else None,
                "stack": traceback.format_exception(*record.exc_info)
            }

        return json.dumps(log_data, ensure_ascii=False)


class ConsoleFormatter(logging.Formatter):
    """控制台格式器"""

    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    LAYER_COLORS = {
        "cli": "\033[94m",       # Blue
        "core": "\033[93m",      # Yellow
        "infra": "\033[95m",     # Magenta
    }
    RESET = "\033[0m"
    DIM = "\033[2m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, "")
        time_str = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        trace = _trace_id.get()

        # 提取模块名
        logger_name = record.name
        module = logger_name.replace("uploader.", "") if logger_name.startswith("uploader.") else logger_name

        # 获取层级
        layer = getattr(record, "layer", None) or get_layer(module)
        layer_color = self.LAYER_COLORS.get(layer, "")

        # 格式: 时间 | LEVEL | [layer:module] | [trace_id] | 消息
        parts = [
            f"{self.DIM}{time_str}{self.RESET}",
            f"{color}{record.levelname:8}{self.RESET}",
            f"{layer_color}[{layer}:{module}]{self.RESET}",
        ]

        if trace:
            parts.append(f"{self.DIM}[{trace[:8]}]{self.RESET}")

        parts.append(record.getMessage())

        msg = " | ".join(parts)

        # 额外数据
        if hasattr(record, "data") and record.data:
            msg += f" {self.DIM}| {record.data}{self.RESET}"

        # 异常
        if record.exc_info:
            msg += f"\n{color}{''.join(traceback.format_exception(*record.exc_info))}{self.RESET}"

        return msg


class _LoggerWrapper:
    """Logger 包装器"""

    def __init__(self, lg: logging.Logger, layer: str = None):
        self._lg = lg
        self._layer = layer

    def _log(self, level: int, msg: str, **kwargs):
        exc_info = kwargs.pop("exc_info", None)
        record = self._lg.makeRecord(
            self._lg.name, level,
            "(unknown)", 0, msg, (), exc_info
        )
        if self._layer:
            record.layer = self._layer
        if kwargs:
            record.data = kwargs
        self._lg.handle(record)

    def debug(self, msg: str, **kwargs):
        self._log(logging.DEBUG, msg, **kwargs)

    def info(self, msg: str, **kwargs):
        self._log(logging.INFO, msg, **kwargs)

    def warning(self, msg: str, **kwargs):
        self._log(logging.WARNING, msg, **kwargs)

    def error(self, msg: str, **kwargs):
        self._log(logging.ERROR, msg, **kwargs)

    def exception(self, msg: str, **kwargs):
        kwargs["exc_info"] = sys.exc_info()
        self._log(logging.ERROR, msg, **kwargs)


class Logger:
    """
    日志管理器

    使用示例:
        from src.infra.logger import logger, trace

        # 获取模块 logger（自动推断层级）
        log = logger.get("collector")  # layer=core
        log.info("开始采集")

        # 手动指定层级
        log = logger.get("my_module", layer="core")

        # 追踪操作
        with trace("采集商品", url=url):
            log.info("开始")
            log.info("完成", count=10)
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if Logger._initialized:
            return
        Logger._initialized = True

        self._config = LogConfig()
        self._loggers: dict[str, logging.Logger] = {}
        self._root: logging.Logger = None
        self._setup()

    def _setup(self):
        """初始化日志系统"""
        self._config.log_dir.mkdir(parents=True, exist_ok=True)

        # 根 logger
        self._root = logging.getLogger("uploader")
        self._root.setLevel(self._config.log_level)
        self._root.handlers.clear()

        # 主日志文件 - JSON 格式
        main_handler = RotatingFileHandler(
            self._config.log_dir / "app.log",
            maxBytes=self._config.max_file_size,
            backupCount=self._config.backup_count,
            encoding="utf-8"
        )
        main_handler.setFormatter(JsonFormatter())
        main_handler.setLevel(logging.DEBUG)
        self._root.addHandler(main_handler)

        # 错误日志单独文件
        error_handler = RotatingFileHandler(
            self._config.log_dir / "error.log",
            maxBytes=self._config.max_file_size,
            backupCount=self._config.backup_count,
            encoding="utf-8"
        )
        error_handler.setFormatter(JsonFormatter())
        error_handler.setLevel(logging.ERROR)
        self._root.addHandler(error_handler)

        # 控制台
        if self._config.console_output:
            console = logging.StreamHandler(sys.stdout)
            console.setFormatter(ConsoleFormatter())
            console.setLevel(self._config.console_level)
            self._root.addHandler(console)

        # 记录启动
        self._root.info(f"程序启动 run_id={RUN_ID}")

    def configure(self, **kwargs):
        """重新配置"""
        self._config = LogConfig(**kwargs)
        Logger._initialized = False
        self._setup()
        Logger._initialized = True

    def get(self, name: str, layer: str = None) -> _LoggerWrapper:
        """
        获取子 logger

        Args:
            name: 模块名（如 collector, browser）
            layer: 可选，手动指定层级（cli/core/infra）
        """
        if name not in self._loggers:
            self._loggers[name] = self._root.getChild(name)

        # 自动推断或使用指定的层级
        resolved_layer = layer or get_layer(name)
        return _LoggerWrapper(self._loggers[name], resolved_layer)

    def _log(self, level: int, msg: str, layer: str = None, **kwargs):
        exc_info = kwargs.pop("exc_info", None)
        record = self._root.makeRecord(
            self._root.name, level,
            "(unknown)", 0, msg, (), exc_info
        )
        if layer:
            record.layer = layer
        if kwargs:
            record.data = kwargs
        self._root.handle(record)

    def debug(self, msg: str, **kwargs):
        self._log(logging.DEBUG, msg, **kwargs)

    def info(self, msg: str, **kwargs):
        self._log(logging.INFO, msg, **kwargs)

    def warning(self, msg: str, **kwargs):
        self._log(logging.WARNING, msg, **kwargs)

    def error(self, msg: str, **kwargs):
        self._log(logging.ERROR, msg, **kwargs)

    def critical(self, msg: str, **kwargs):
        self._log(logging.CRITICAL, msg, **kwargs)

    def exception(self, msg: str, **kwargs):
        kwargs["exc_info"] = sys.exc_info()
        self._log(logging.ERROR, msg, **kwargs)


class trace:
    """
    追踪上下文管理器

    使用:
        with trace("采集商品", url=url):
            log.info("开始")
            log.info("完成")

        # 指定层级
        with trace("采集商品", layer="core"):
            ...
    """

    def __init__(self, operation: str, layer: str = "cli", **ctx):
        self.operation = operation
        self.layer = layer
        self.ctx = ctx
        self.trace_id = new_trace_id()
        self._old_trace = None
        self._old_ctx = None
        self._log = None

    def __enter__(self):
        self._old_trace = _trace_id.get()
        self._old_ctx = _context.get()
        _trace_id.set(self.trace_id)
        _context.set({**self._old_ctx, **self.ctx})

        # 使用指定层级的 logger
        self._log = logger.get("trace", layer=self.layer)
        self._log.info(f"[开始] {self.operation}", trace_id=self.trace_id, **self.ctx)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            # 用户中断类异常不记录为错误
            if exc_type in (KeyboardInterrupt, SystemExit) or \
               (exc_type.__name__ in ('CancelledError', 'TimeoutError')):
                self._log.info(f"[取消] {self.operation}")
            elif str(exc_val):  # 只有有实际错误信息时才记录
                self._log.error(f"[失败] {self.operation}", error=str(exc_val))
            else:
                self._log.info(f"[中断] {self.operation}")
        else:
            self._log.info(f"[完成] {self.operation}")

        _trace_id.set(self._old_trace)
        _context.set(self._old_ctx)


# 全局单例
logger = Logger()
