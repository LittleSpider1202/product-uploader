"""
字段绑定模型
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class FieldType(Enum):
    """字段类型"""
    TEXT = "text"           # 单行文本
    NUMBER = "number"       # 数字
    TEXTAREA = "textarea"   # 多行文本
    IMAGE = "image"         # 单张图片
    IMAGES = "images"       # 多张图片
    SELECT = "select"       # 下拉选择
    RICHTEXT = "richtext"   # 富文本


@dataclass
class FieldBinding:
    """字段绑定"""
    name: str                          # 用户定义的字段名
    field_type: FieldType              # 字段类型
    required: bool                     # 是否必填
    target_selector: str               # 目标页面选择器（千牛）
    source_selector: str | None = None # 来源页面选择器（淘宝）

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "field_type": self.field_type.value,
            "required": self.required,
            "target_selector": self.target_selector,
            "source_selector": self.source_selector
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'FieldBinding':
        return cls(
            name=data["name"],
            field_type=FieldType(data["field_type"]),
            required=data["required"],
            target_selector=data["target_selector"],
            source_selector=data.get("source_selector")
        )


@dataclass
class BindingConfig:
    """绑定配置（一套完整的字段映射）"""
    id: str                            # 配置 ID
    name: str                          # 配置名称（如"女装类目配置"）
    fields: list[FieldBinding] = field(default_factory=list)

    # 元信息
    target_url_pattern: str = ""       # 千牛页面 URL 模式
    source_url_pattern: str = ""       # 淘宝页面 URL 模式
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def add_field(self, binding: FieldBinding):
        """添加字段绑定"""
        self.fields.append(binding)
        self.updated_at = datetime.now()

    def get_required_fields(self) -> list[FieldBinding]:
        """获取必填字段"""
        return [f for f in self.fields if f.required]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "fields": [f.to_dict() for f in self.fields],
            "target_url_pattern": self.target_url_pattern,
            "source_url_pattern": self.source_url_pattern,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'BindingConfig':
        return cls(
            id=data["id"],
            name=data["name"],
            fields=[FieldBinding.from_dict(f) for f in data.get("fields", [])],
            target_url_pattern=data.get("target_url_pattern", ""),
            source_url_pattern=data.get("source_url_pattern", ""),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now()
        )
