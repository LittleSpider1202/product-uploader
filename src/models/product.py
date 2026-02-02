"""
商品数据模型
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ProductStatus(Enum):
    """商品状态"""
    DRAFT = "draft"           # 已采集，未上架
    UPLOADED = "uploaded"     # 已上架
    FAILED = "failed"         # 上架失败


@dataclass
class SKU:
    """SKU 规格"""
    id: str
    name: str                 # 规格名，如 "颜色: 红色"
    price: float
    stock: int
    image: str | None = None  # 规格图片


@dataclass
class Product:
    """商品数据"""
    id: str                           # 唯一标识
    source_url: str                   # 来源链接
    title: str                        # 商品标题
    price: float                      # 价格
    original_price: float | None = None   # 原价
    category: str | None = None           # 类目
    skus: list[SKU] = field(default_factory=list)
    images: list[str] = field(default_factory=list)         # 主图列表
    detail_images: list[str] = field(default_factory=list)  # 详情图
    description: str = ""             # 商品描述

    # 元信息
    status: ProductStatus = ProductStatus.DRAFT
    collected_at: datetime = field(default_factory=datetime.now)
    uploaded_at: datetime | None = None

    # 扩展字段（平台特有属性）
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """转换为字典（用于 JSON 序列化）"""
        return {
            "id": self.id,
            "source_url": self.source_url,
            "title": self.title,
            "price": self.price,
            "original_price": self.original_price,
            "category": self.category,
            "skus": [
                {
                    "id": sku.id,
                    "name": sku.name,
                    "price": sku.price,
                    "stock": sku.stock,
                    "image": sku.image
                }
                for sku in self.skus
            ],
            "images": self.images,
            "detail_images": self.detail_images,
            "description": self.description,
            "status": self.status.value,
            "collected_at": self.collected_at.isoformat(),
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "extra": self.extra
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Product':
        """从字典创建实例"""
        return cls(
            id=data["id"],
            source_url=data["source_url"],
            title=data["title"],
            price=data["price"],
            original_price=data.get("original_price"),
            category=data.get("category"),
            skus=[
                SKU(
                    id=sku["id"],
                    name=sku["name"],
                    price=sku["price"],
                    stock=sku["stock"],
                    image=sku.get("image")
                )
                for sku in data.get("skus", [])
            ],
            images=data.get("images", []),
            detail_images=data.get("detail_images", []),
            description=data.get("description", ""),
            status=ProductStatus(data.get("status", "draft")),
            collected_at=datetime.fromisoformat(data["collected_at"]) if "collected_at" in data else datetime.now(),
            uploaded_at=datetime.fromisoformat(data["uploaded_at"]) if data.get("uploaded_at") else None,
            extra=data.get("extra", {})
        )
