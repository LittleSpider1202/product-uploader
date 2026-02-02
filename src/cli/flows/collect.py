"""
采集流程
"""
from src.cli.ui import UI
from src.core import Collector, EventBus, EventTypes
from src.infra import BrowserManager, ProductStorage
from .base import BaseFlow, FlowResult


class CollectFlow(BaseFlow):
    """商品采集流程"""

    def __init__(
        self,
        ui: UI,
        browser: BrowserManager,
        storage: ProductStorage,
        event_bus: EventBus = None
    ):
        super().__init__(ui)
        self.browser = browser
        self.storage = storage
        self.event_bus = event_bus or EventBus()
        self.collector = Collector(browser, self.event_bus)

        # 监听进度事件
        self.event_bus.on(EventTypes.PROGRESS, self._on_progress)

    async def run(self) -> FlowResult:
        """执行采集流程"""
        self.ui.print_header("商品采集")
        self.ui.print()

        # 获取商品链接
        url = self.input("请输入淘宝商品链接")
        if not url:
            return FlowResult.cancelled("未输入商品链接")

        self.ui.print()
        self.ui.print_info("正在采集商品信息...")
        self.ui.print()

        # 执行采集
        result = await self.collector.collect(url)

        if not result.success:
            self.ui.print_error(result.error.message)
            return FlowResult.failed(result.error.message)

        product = result.data

        # 显示采集结果
        self.ui.print()
        self.ui.print_success("采集成功！")
        self.ui.print()
        self.ui.print(f"  标题: {product.title}")
        self.ui.print(f"  价格: ¥{product.price:.2f}")
        self.ui.print(f"  图片: {len(product.images)} 张")
        self.ui.print()

        # 确认保存
        if self.confirm("是否保存该商品？"):
            save_result = self.storage.save(product)
            if save_result.success:
                self.ui.print_success(f"已保存，商品 ID: {product.id}")
                return FlowResult.success(
                    "采集并保存成功",
                    {"product_id": product.id}
                )
            else:
                self.ui.print_error(save_result.error.message)
                return FlowResult.failed(save_result.error.message)
        else:
            return FlowResult.cancelled("用户取消保存")

    def _on_progress(self, event):
        """处理进度事件"""
        payload = event.payload
        self.ui.progress(
            payload.get("step", 0),
            payload.get("total", 1),
            payload.get("message", "")
        )
