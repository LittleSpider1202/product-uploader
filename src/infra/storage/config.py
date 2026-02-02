"""
配置管理
"""
import json
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class Config:
    """应用配置"""
    # 浏览器配置
    browser_headless: bool = False        # 是否无头模式
    browser_slow_mo: int = 0              # 操作延迟（ms）
    browser_timeout: int = 30000          # 默认超时（ms）

    # 存储路径
    data_dir: str = "data"

    # 重试策略
    max_retry: int = 3
    retry_delay: float = 1.0

    # 用户状态目录（保存登录态等）
    user_data_dir: str = "user_data"

    def to_dict(self) -> dict:
        return {
            "browser_headless": self.browser_headless,
            "browser_slow_mo": self.browser_slow_mo,
            "browser_timeout": self.browser_timeout,
            "data_dir": self.data_dir,
            "max_retry": self.max_retry,
            "retry_delay": self.retry_delay,
            "user_data_dir": self.user_data_dir
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Config':
        return cls(
            browser_headless=data.get("browser_headless", False),
            browser_slow_mo=data.get("browser_slow_mo", 0),
            browser_timeout=data.get("browser_timeout", 30000),
            data_dir=data.get("data_dir", "data"),
            max_retry=data.get("max_retry", 3),
            retry_delay=data.get("retry_delay", 1.0),
            user_data_dir=data.get("user_data_dir", "user_data")
        )


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_path: Path = None):
        self.config_path = config_path or Path("data/config.json")
        self._config: Config | None = None

    def load(self) -> Config:
        """加载配置"""
        if self._config:
            return self._config

        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._config = Config.from_dict(data)
            except (json.JSONDecodeError, KeyError):
                self._config = Config()
        else:
            self._config = Config()

        return self._config

    def save(self, config: Config = None):
        """保存配置"""
        if config:
            self._config = config
        if self._config is None:
            self._config = Config()

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self._config.to_dict(), f, ensure_ascii=False, indent=2)

    def get(self) -> Config:
        """获取当前配置"""
        if self._config is None:
            return self.load()
        return self._config

    def update(self, **kwargs):
        """更新配置"""
        config = self.get()
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        self.save(config)
