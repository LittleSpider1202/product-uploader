"""
商品采集器
"""
import re
import uuid
from datetime import datetime

from src.models import Product, SKU, Result
from src.infra.browser import BrowserManager
from src.infra.logger import logger
from .events import EventBus, EventTypes

log = logger.get("collector")


class Collector:
    """商品采集器：从淘宝页面提取商品信息"""

    def __init__(self, browser: BrowserManager, event_bus: EventBus = None):
        self.browser = browser
        self.event_bus = event_bus or EventBus()

    async def collect(self, url: str) -> Result[Product]:
        """采集商品信息"""
        # 验证 URL
        if not self._is_valid_url(url):
            return Result.fail_with(
                code="C_INVALID_URL",
                message=f"无效的商品链接: {url}",
                recoverable=False
            )

        # 发送进度事件
        self._emit_progress(1, 5, "正在打开商品页面...")

        # 导航到页面
        result = await self.browser.goto(url)
        if not result.success:
            return result

        self._emit_progress(2, 5, "正在解析商品标题...")

        # 提取商品信息
        product_id = f"prod_{uuid.uuid4().hex[:8]}"
        product_data = {
            "id": product_id,
            "source_url": url,
            "title": "",
            "price": 0.0,
            "images": [],
            "skus": []
        }

        # 提取标题
        title_result = await self._extract_title()
        if title_result.success:
            product_data["title"] = title_result.data

        self._emit_progress(3, 5, "正在解析价格...")

        # 提取价格
        price_result = await self._extract_price()
        if price_result.success:
            product_data["price"] = price_result.data

        self._emit_progress(4, 5, "正在解析图片...")

        # 提取图片
        images_result = await self._extract_images()
        if images_result.success:
            product_data["images"] = images_result.data

        self._emit_progress(5, 5, "采集完成")

        # 创建商品对象
        product = Product(
            id=product_data["id"],
            source_url=product_data["source_url"],
            title=product_data["title"],
            price=product_data["price"],
            images=product_data["images"],
            collected_at=datetime.now()
        )

        return Result.ok(product)

    def _is_valid_url(self, url: str) -> bool:
        """验证是否为淘宝商品链接"""
        patterns = [
            r"https?://item\.taobao\.com",
            r"https?://detail\.tmall\.com",
            r"https?://.*\.taobao\.com/item",
        ]
        return any(re.match(p, url) for p in patterns)

    async def _extract_title(self) -> Result[str]:
        """提取商品标题"""
        # 尝试多个可能的选择器
        selectors = [
            "h1.tb-main-title",
            ".tb-detail-hd h1",
            "div[data-spm='1000983'] h1",
            ".ItemHeader--mainTitle--3CIjqW5",
        ]

        for selector in selectors:
            result = await self.browser.get_content(selector)
            if result.success and result.data:
                return Result.ok(result.data.strip())

        # 使用页面标题作为备选
        if self.browser.page:
            title = await self.browser.page.title()
            # 移除后缀
            title = re.sub(r"-.*$", "", title).strip()
            if title:
                return Result.ok(title)

        return Result.fail_with(
            code="C_PARSE_FAILED",
            message="无法提取商品标题",
            recoverable=True
        )

    async def _extract_price(self) -> Result[float]:
        """提取商品价格"""
        selectors = [
            ".tb-rmb-num",
            ".tm-price",
            ".tm-promo-price .tm-price",
            ".Price--priceText--2nLbVda",
        ]

        for selector in selectors:
            result = await self.browser.get_content(selector)
            if result.success and result.data:
                # 提取数字
                match = re.search(r"[\d.]+", result.data)
                if match:
                    try:
                        return Result.ok(float(match.group()))
                    except ValueError:
                        continue

        return Result.fail_with(
            code="C_PARSE_FAILED",
            message="无法提取商品价格",
            recoverable=True
        )

    async def _extract_images(self) -> Result[list[str]]:
        """提取商品图片"""
        images = []

        if not self.browser.page:
            return Result.ok(images)

        # 尝试获取主图列表
        selectors = [
            "#J_UlThumb img",
            ".tb-thumb img",
            ".PicGallery--thumbnails--2XJVxAf img",
        ]

        for selector in selectors:
            try:
                elements = await self.browser.page.query_selector_all(selector)
                for el in elements:
                    src = await el.get_attribute("src")
                    if src:
                        # 转换为大图
                        src = self._to_large_image(src)
                        if src not in images:
                            images.append(src)
                if images:
                    break
            except Exception:
                continue

        return Result.ok(images)

    def _to_large_image(self, url: str) -> str:
        """转换为大图 URL"""
        # 移除尺寸后缀
        url = re.sub(r"_\d+x\d+\.[a-z]+$", "", url)
        # 确保使用 https
        if url.startswith("//"):
            url = "https:" + url
        return url

    def _emit_progress(self, step: int, total: int, message: str):
        """发送进度事件"""
        if self.event_bus:
            self.event_bus.emit(
                EventTypes.PROGRESS,
                step=step,
                total=total,
                message=message
            )
