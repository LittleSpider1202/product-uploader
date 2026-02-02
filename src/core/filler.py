"""
表单填充器
"""
from datetime import datetime
from pathlib import Path

from src.models import Product, Problem, ProblemContext, ProblemType, ProblemStatus, Result
from src.infra.browser import BrowserManager
from src.infra.knowledge import KnowledgeBase
from src.infra.logger import logger
from .events import EventBus, EventTypes

log = logger.get("filler")


class Filler:
    """表单填充器：自动填写上架表单"""

    # 天猫发布商品页面
    PUBLISH_URL = "https://upload.taobao.com/auction/container/publish.htm"

    def __init__(
        self,
        browser: BrowserManager,
        knowledge_base: KnowledgeBase,
        event_bus: EventBus = None
    ):
        self.browser = browser
        self.knowledge_base = knowledge_base
        self.event_bus = event_bus or EventBus()

    async def fill(self, product: Product) -> Result[bool]:
        """填写商品上架表单"""
        self._emit_progress(1, 6, "正在打开发布页面...")

        # 导航到发布页面
        result = await self.browser.goto(self.PUBLISH_URL)
        if not result.success:
            return result

        # 检查登录状态
        logged_in = await self._check_login()
        if not logged_in:
            self._emit_event(EventTypes.LOGIN_EXPIRED, session_id="main")
            return Result.fail_with(
                code="B_LOGIN_EXPIRED",
                message="请先登录淘宝账号",
                recoverable=True
            )

        self._emit_progress(2, 6, "正在填写商品标题...")

        # 填写标题
        title_result = await self._fill_title(product.title)
        if not title_result.success:
            await self._report_problem(
                ProblemType.FIELD_MISMATCH,
                "无法填写商品标题",
                {"field": "title", "value": product.title}
            )
            return title_result

        self._emit_progress(3, 6, "正在填写商品价格...")

        # 填写价格
        price_result = await self._fill_price(product.price)
        if not price_result.success:
            await self._report_problem(
                ProblemType.FIELD_MISMATCH,
                "无法填写商品价格",
                {"field": "price", "value": str(product.price)}
            )
            return price_result

        self._emit_progress(4, 6, "正在上传商品图片...")

        # 上传图片
        if product.images:
            images_result = await self._upload_images(product.images)
            if not images_result.success:
                # 图片上传失败不阻断流程
                self._emit_progress(4, 6, "图片上传失败，请手动上传")

        self._emit_progress(5, 6, "正在填写商品描述...")

        # 填写描述
        if product.description:
            await self._fill_description(product.description)

        self._emit_progress(6, 6, "表单填写完成，请检查并提交")

        return Result.ok(True)

    async def _check_login(self) -> bool:
        """检查登录状态"""
        # 检查是否有登录相关元素
        result = await self.browser.is_logged_in(".user-nick")
        return result.success and result.data

    async def _fill_title(self, title: str) -> Result[bool]:
        """填写标题"""
        selectors = [
            "input[name='title']",
            "#title",
            ".title-input input",
        ]

        for selector in selectors:
            result = await self.browser.fill(selector, title)
            if result.success:
                return result

        return Result.fail_with(
            code="F_FIELD_MISMATCH",
            message="找不到标题输入框",
            recoverable=True
        )

    async def _fill_price(self, price: float) -> Result[bool]:
        """填写价格"""
        selectors = [
            "input[name='price']",
            "#price",
            ".price-input input",
        ]

        for selector in selectors:
            result = await self.browser.fill(selector, str(price))
            if result.success:
                return result

        return Result.fail_with(
            code="F_FIELD_MISMATCH",
            message="找不到价格输入框",
            recoverable=True
        )

    async def _upload_images(self, images: list[str]) -> Result[bool]:
        """上传图片（占位实现）"""
        # TODO: 实现图片上传逻辑
        # 这需要处理文件上传或 URL 导入
        return Result.ok(True)

    async def _fill_description(self, description: str) -> Result[bool]:
        """填写描述"""
        selectors = [
            "textarea[name='description']",
            "#description",
            ".desc-editor textarea",
        ]

        for selector in selectors:
            result = await self.browser.fill(selector, description)
            if result.success:
                return result

        return Result.ok(True)  # 描述可选

    async def _report_problem(
        self,
        problem_type: ProblemType,
        message: str,
        extra_context: dict = None
    ) -> Problem:
        """上报问题"""
        # 截图
        screenshot_path = None
        if self.browser.page:
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = f"data/screenshots/problem_{timestamp}.png"
                Path(screenshot_path).parent.mkdir(parents=True, exist_ok=True)
                await self.browser.page.screenshot(path=screenshot_path)
            except Exception:
                pass

        # 获取当前页面 URL
        page_url = ""
        if self.browser.page:
            page_url = self.browser.page.url

        # 创建问题记录
        problem = Problem(
            id=self.knowledge_base.problems.generate_id(),
            type=problem_type,
            message=message,
            context=ProblemContext(
                page_url=page_url,
                screenshot=screenshot_path,
                **(extra_context or {})
            ),
            status=ProblemStatus.OPEN
        )

        # 保存问题
        self.knowledge_base.report_problem(problem)

        # 发送事件
        self._emit_event(
            EventTypes.PROBLEM,
            problem_id=problem.id,
            problem_type=problem_type.value,
            message=message
        )

        return problem

    def _emit_progress(self, step: int, total: int, message: str):
        """发送进度事件"""
        if self.event_bus:
            self.event_bus.emit(
                EventTypes.PROGRESS,
                step=step,
                total=total,
                message=message
            )

    def _emit_event(self, event_type: str, **payload):
        """发送事件"""
        if self.event_bus:
            self.event_bus.emit(event_type, **payload)
