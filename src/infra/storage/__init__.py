"""
存储层模块
"""
from .base import BaseStorage
from .product import ProductStorage
from .config import Config, ConfigManager

__all__ = [
    "BaseStorage",
    "ProductStorage",
    "Config",
    "ConfigManager",
]
