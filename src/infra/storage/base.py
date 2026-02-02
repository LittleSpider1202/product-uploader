"""
存储层基类
"""
import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TypeVar, Generic

from src.models import Result

T = TypeVar('T')


class BaseStorage(ABC, Generic[T]):
    """存储基类"""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self._ensure_dir()

    def _ensure_dir(self):
        """确保目录存在"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        # 确保索引文件存在
        index_path = self.data_dir / "index.json"
        if not index_path.exists():
            self._write_json(index_path, self._empty_index())

    @abstractmethod
    def _empty_index(self) -> dict:
        """返回空索引结构"""
        pass

    @abstractmethod
    def _to_index_entry(self, item: T) -> dict:
        """转换为索引条目"""
        pass

    def _read_json(self, path: Path) -> dict | list | None:
        """读取 JSON 文件"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def _write_json(self, path: Path, data: dict | list):
        """写入 JSON 文件"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _get_index(self) -> dict:
        """获取索引"""
        index_path = self.data_dir / "index.json"
        data = self._read_json(index_path)
        return data if data else self._empty_index()

    def _save_index(self, index: dict):
        """保存索引"""
        index_path = self.data_dir / "index.json"
        self._write_json(index_path, index)

    def _item_path(self, item_id: str) -> Path:
        """获取单项文件路径"""
        return self.data_dir / f"{item_id}.json"
