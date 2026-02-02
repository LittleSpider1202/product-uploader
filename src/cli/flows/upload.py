"""
上架流程
"""
from src.cli.ui import UI
from src.core import Filler, EventBus, EventTypes
from src.infra import BrowserManager, ProductStorage, KnowledgeBase
from src.models import ProductStatus
from .base import BaseFlow, FlowResult


class UploadFlow(BaseFlow):
    """商品上架流程"""

    def __init__(
        self,
        ui: UI,
        browser: BrowserManager,
        storage: ProductStorage,
        knowledge_base: KnowledgeBase,
        event_bus: EventBus = None
    ):
        super().__init__(ui)
        self.browser = browser
        self.storage = storage
        self.knowledge_base = knowledge_base
        self.event_bus = event_bus or EventBus()
        self.filler = Filler(browser, knowledge_base, self.event_bus)

        # 监听事件
        self.event_bus.on(EventTypes.PROGRESS, self._on_progress)
        self.event_bus.on(EventTypes.LOGIN_EXPIRED, self._on_login_expired)

    async def run(self) -> FlowResult:
        """执行上架流程"""
        self.ui.print_header("商品上架")
        self.ui.print()

        # 列出可上架的商品
        list_result = self.storage.list(ProductStatus.DRAFT)
        if not list_result.success:
            self.ui.print_error(list_result.error.message)
            return FlowResult.failed(list_result.error.message)

        products = list_result.data
        if not products:
            self.ui.print_warning("没有待上架的商品")
            self.ui.print_info("请先使用「采集商品」功能添加商品")
            return FlowResult.cancelled("无待上架商品")

        # 选择商品
        options = [f"{p['title'][:30]}..." for p in products]
        options.append("返回")

        idx = self.select(options, "选择要上架的商品")
        if idx >= len(products):
            return FlowResult.cancelled("用户返回")

        product_id = products[idx]["id"]

        # 获取商品详情
        get_result = self.storage.get(product_id)
        if not get_result.success:
            self.ui.print_error(get_result.error.message)
            return FlowResult.failed(get_result.error.message)

        product = get_result.data

        # 显示商品信息
        self.ui.print()
        self.ui.print(f"  标题: {product.title}")
        self.ui.print(f"  价格: ¥{product.price:.2f}")
        self.ui.print()

        if not self.confirm("确认上架该商品？"):
            return FlowResult.cancelled("用户取消")

        self.ui.print()
        self.ui.print_info("正在填写上架表单...")
        self.ui.print()

        # 执行填充
        result = await self.filler.fill(product)

        if not result.success:
            if result.error.code == "B_LOGIN_EXPIRED":
                self.ui.print_warning("请在浏览器中登录后，按回车继续...")
                input()
                # 重试
                result = await self.filler.fill(product)

        if result.success:
            self.ui.print()
            self.ui.print_success("表单填写完成！")
            self.ui.print_info("请在浏览器中检查并提交")

            # 更新商品状态
            product.status = ProductStatus.UPLOADED
            from datetime import datetime
            product.uploaded_at = datetime.now()
            self.storage.save(product)

            return FlowResult.success("上架成功", {"product_id": product.id})
        else:
            self.ui.print()
            self.ui.print_error(result.error.message)
            return FlowResult.failed(result.error.message)

    def _on_progress(self, event):
        """处理进度事件"""
        payload = event.payload
        self.ui.progress(
            payload.get("step", 0),
            payload.get("total", 1),
            payload.get("message", "")
        )

    def _on_login_expired(self, event):
        """处理登录过期事件"""
        self.ui.print()
        self.ui.print_warning("登录已过期，请在浏览器中重新登录")
