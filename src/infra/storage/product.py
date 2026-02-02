"""
商品数据存储
"""
import uuid
from pathlib import Path

from src.models import Product, ProductStatus, Result
from .base import BaseStorage


class ProductStorage(BaseStorage[Product]):
    """商品数据存储"""

    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            data_dir = Path("data/products")
        super().__init__(data_dir)

    def _empty_index(self) -> dict:
        return {"products": []}

    def _to_index_entry(self, product: Product) -> dict:
        return {
            "id": product.id,
            "title": product.title,
            "status": product.status.value,
            "collected_at": product.collected_at.isoformat()
        }

    def generate_id(self) -> str:
        """生成唯一 ID"""
        return f"prod_{uuid.uuid4().hex[:8]}"

    def save(self, product: Product) -> Result[Product]:
        """保存商品"""
        try:
            # 保存商品文件
            item_path = self._item_path(product.id)
            self._write_json(item_path, product.to_dict())

            # 更新索引
            index = self._get_index()
            entries = index["products"]
            # 移除旧条目
            entries = [e for e in entries if e["id"] != product.id]
            # 添加新条目
            entries.append(self._to_index_entry(product))
            index["products"] = entries
            self._save_index(index)

            return Result.ok(product)
        except Exception as e:
            return Result.fail_with(
                code="S_WRITE_FAILED",
                message=f"保存商品失败: {e}",
                recoverable=False
            )

    def get(self, product_id: str) -> Result[Product]:
        """获取商品"""
        try:
            item_path = self._item_path(product_id)
            data = self._read_json(item_path)
            if data is None:
                return Result.fail_with(
                    code="S_NOT_FOUND",
                    message=f"商品不存在: {product_id}",
                    recoverable=False
                )
            return Result.ok(Product.from_dict(data))
        except Exception as e:
            return Result.fail_with(
                code="S_READ_FAILED",
                message=f"读取商品失败: {e}",
                recoverable=False
            )

    def list(self, status: ProductStatus = None) -> Result[list[dict]]:
        """列出商品（返回索引条目）"""
        try:
            index = self._get_index()
            entries = index["products"]
            if status:
                entries = [e for e in entries if e["status"] == status.value]
            return Result.ok(entries)
        except Exception as e:
            return Result.fail_with(
                code="S_READ_FAILED",
                message=f"列出商品失败: {e}",
                recoverable=False
            )

    def delete(self, product_id: str) -> Result[bool]:
        """删除商品"""
        try:
            item_path = self._item_path(product_id)
            if item_path.exists():
                item_path.unlink()

            # 更新索引
            index = self._get_index()
            index["products"] = [e for e in index["products"] if e["id"] != product_id]
            self._save_index(index)

            return Result.ok(True)
        except Exception as e:
            return Result.fail_with(
                code="S_WRITE_FAILED",
                message=f"删除商品失败: {e}",
                recoverable=False
            )
