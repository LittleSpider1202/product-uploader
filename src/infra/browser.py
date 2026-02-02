"""
Playwright 浏览器封装
"""
import asyncio
import json
from pathlib import Path
from typing import Callable
from dataclasses import dataclass, field
from datetime import datetime

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright

from src.models import Result
from src.infra.logger import logger

log = logger.get("browser")


@dataclass
class RetryPolicy:
    """重试策略"""
    max_attempts: int = 3
    base_delay: float = 1.0
    exponential: bool = True
    max_delay: float = 30.0
    retryable_codes: list[str] = field(default_factory=lambda: [
        "B_TIMEOUT",
        "B_NETWORK_ERROR",
    ])

    def get_delay(self, attempt: int) -> float:
        if self.exponential:
            delay = self.base_delay * (2 ** attempt)
        else:
            delay = self.base_delay
        return min(delay, self.max_delay)


def _get_default_user_data_dir() -> str:
    """获取默认用户数据目录（项目根目录下）"""
    # 使用项目根目录下的 user_data，确保路径一致
    project_root = Path(__file__).parent.parent.parent
    return str(project_root / "user_data")


@dataclass
class BrowserConfig:
    """浏览器配置"""
    headless: bool = False
    slow_mo: int = 0
    timeout: int = 30000
    user_data_dir: str = None  # None 时使用默认路径
    viewport_width: int = 1280
    viewport_height: int = 800

    def __post_init__(self):
        if self.user_data_dir is None:
            self.user_data_dir = _get_default_user_data_dir()


class BrowserManager:
    """浏览器管理器"""

    def __init__(self, config: BrowserConfig = None):
        self.config = config or BrowserConfig()
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None
        self._retry_policy = RetryPolicy()

    async def start(self) -> Result[Page]:
        """启动浏览器"""
        try:
            self._playwright = await async_playwright().start()

            # 使用持久化上下文保存登录态
            user_data_path = Path(self.config.user_data_dir)
            user_data_path.mkdir(parents=True, exist_ok=True)

            self._context = await self._playwright.chromium.launch_persistent_context(
                user_data_dir=str(user_data_path),
                headless=self.config.headless,
                slow_mo=self.config.slow_mo,
                args=[
                    "--start-maximized",
                    "--disable-blink-features=AutomationControlled",
                    "--no-proxy-server",
                ],
                ignore_https_errors=True,
                no_viewport=True,
            )

            # 设置默认超时
            self._context.set_default_timeout(self.config.timeout)

            # 获取或创建页面
            pages = self._context.pages
            if pages:
                self._page = pages[0]
            else:
                self._page = await self._context.new_page()

            return Result.ok(self._page)
        except Exception as e:
            return Result.fail_with(
                code="B_LAUNCH_FAILED",
                message=f"启动浏览器失败: {e}",
                recoverable=False
            )

    async def stop(self):
        """关闭浏览器"""
        if self._context:
            await self._context.close()
        if self._playwright:
            await self._playwright.stop()
        self._page = None
        self._context = None
        self._playwright = None

    @property
    def page(self) -> Page | None:
        return self._page

    @property
    def context(self) -> BrowserContext | None:
        return self._context

    async def goto(self, url: str) -> Result[Page]:
        """导航到指定 URL"""
        if not self._page:
            return Result.fail_with(
                code="B_NOT_STARTED",
                message="浏览器未启动",
                recoverable=False
            )

        try:
            await self._page.goto(url, wait_until="domcontentloaded")
            return Result.ok(self._page)
        except Exception as e:
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                return Result.fail_with(
                    code="B_TIMEOUT",
                    message=f"页面加载超时: {url}",
                    recoverable=True,
                    context={"url": url}
                )
            return Result.fail_with(
                code="B_NETWORK_ERROR",
                message=f"网络错误: {e}",
                recoverable=True,
                context={"url": url}
            )

    async def wait_for_selector(
        self,
        selector: str,
        timeout: int = None
    ) -> Result[bool]:
        """等待元素出现"""
        if not self._page:
            return Result.fail_with(
                code="B_NOT_STARTED",
                message="浏览器未启动",
                recoverable=False
            )

        try:
            await self._page.wait_for_selector(
                selector,
                timeout=timeout or self.config.timeout
            )
            return Result.ok(True)
        except Exception as e:
            if "timeout" in str(e).lower():
                return Result.fail_with(
                    code="B_TIMEOUT",
                    message=f"等待元素超时: {selector}",
                    recoverable=True,
                    context={"selector": selector}
                )
            return Result.fail_with(
                code="C_ELEMENT_NOT_FOUND",
                message=f"元素未找到: {selector}",
                recoverable=True,
                context={"selector": selector}
            )

    async def click(self, selector: str) -> Result[bool]:
        """点击元素"""
        if not self._page:
            return Result.fail_with(
                code="B_NOT_STARTED",
                message="浏览器未启动",
                recoverable=False
            )

        try:
            await self._page.click(selector)
            return Result.ok(True)
        except Exception as e:
            return Result.fail_with(
                code="C_ELEMENT_NOT_FOUND",
                message=f"点击失败: {selector} - {e}",
                recoverable=True,
                context={"selector": selector}
            )

    async def fill(self, selector: str, value: str) -> Result[bool]:
        """填写输入框"""
        if not self._page:
            return Result.fail_with(
                code="B_NOT_STARTED",
                message="浏览器未启动",
                recoverable=False
            )

        try:
            await self._page.fill(selector, value)
            return Result.ok(True)
        except Exception as e:
            return Result.fail_with(
                code="C_ELEMENT_NOT_FOUND",
                message=f"填写失败: {selector} - {e}",
                recoverable=True,
                context={"selector": selector, "value": value}
            )

    async def screenshot(self, path: str = None) -> Result[bytes]:
        """截图"""
        if not self._page:
            return Result.fail_with(
                code="B_NOT_STARTED",
                message="浏览器未启动",
                recoverable=False
            )

        try:
            screenshot = await self._page.screenshot(path=path)
            return Result.ok(screenshot)
        except Exception as e:
            return Result.fail_with(
                code="B_SCREENSHOT_FAILED",
                message=f"截图失败: {e}",
                recoverable=True
            )

    async def get_content(self, selector: str) -> Result[str]:
        """获取元素内容"""
        if not self._page:
            return Result.fail_with(
                code="B_NOT_STARTED",
                message="浏览器未启动",
                recoverable=False
            )

        try:
            element = await self._page.query_selector(selector)
            if element:
                content = await element.text_content()
                return Result.ok(content or "")
            return Result.fail_with(
                code="C_ELEMENT_NOT_FOUND",
                message=f"元素未找到: {selector}",
                recoverable=True,
                context={"selector": selector}
            )
        except Exception as e:
            return Result.fail_with(
                code="C_PARSE_FAILED",
                message=f"获取内容失败: {e}",
                recoverable=True,
                context={"selector": selector}
            )

    async def get_attribute(self, selector: str, attribute: str) -> Result[str | None]:
        """获取元素属性"""
        if not self._page:
            return Result.fail_with(
                code="B_NOT_STARTED",
                message="浏览器未启动",
                recoverable=False
            )

        try:
            element = await self._page.query_selector(selector)
            if element:
                value = await element.get_attribute(attribute)
                return Result.ok(value)
            return Result.fail_with(
                code="C_ELEMENT_NOT_FOUND",
                message=f"元素未找到: {selector}",
                recoverable=True,
                context={"selector": selector}
            )
        except Exception as e:
            return Result.fail_with(
                code="C_PARSE_FAILED",
                message=f"获取属性失败: {e}",
                recoverable=True,
                context={"selector": selector, "attribute": attribute}
            )

    async def is_logged_in(self, check_selector: str) -> Result[bool]:
        """检查是否已登录"""
        if not self._page:
            return Result.fail_with(
                code="B_NOT_STARTED",
                message="浏览器未启动",
                recoverable=False
            )

        try:
            element = await self._page.query_selector(check_selector)
            return Result.ok(element is not None)
        except Exception:
            return Result.ok(False)

    async def with_retry(
        self,
        action: Callable,
        *args,
        **kwargs
    ) -> Result:
        """带重试的执行"""
        last_result = None
        for attempt in range(self._retry_policy.max_attempts):
            result = await action(*args, **kwargs)
            if result.success:
                return result

            last_result = result
            # 检查是否可重试
            if result.error and result.error.code in self._retry_policy.retryable_codes:
                delay = self._retry_policy.get_delay(attempt)
                await asyncio.sleep(delay)
            else:
                break

        return last_result or Result.fail_with(
            code="B_RETRY_EXHAUSTED",
            message="重试次数已用尽",
            recoverable=False
        )

    # ==================== 元素捕获模式 ====================

    async def enable_element_capture(self) -> Result[bool]:
        """启用元素捕获模式（Ctrl+点击捕获元素）"""
        if not self._page:
            return Result.fail_with(
                code="B_NOT_STARTED",
                message="浏览器未启动",
                recoverable=False
            )

        js_code = """
        (() => {
            // 清理已有元素（支持重复注入）
            const existingOverlay = document.getElementById('__capture_overlay');
            const existingLabel = document.getElementById('__capture_label');
            if (existingOverlay) existingOverlay.remove();
            if (existingLabel) existingLabel.remove();

            window.__elementCaptureEnabled = true;
            window.__capturedElement = null;

            // 创建高亮覆盖层
            const overlay = document.createElement('div');
            overlay.id = '__capture_overlay';
            overlay.style.cssText = `
                position: fixed;
                pointer-events: none;
                border: 2px solid #1890ff;
                background: rgba(24, 144, 255, 0.1);
                z-index: 999999;
                display: none;
                transition: all 0.1s ease;
            `;
            document.body.appendChild(overlay);

            // 创建标签提示
            const label = document.createElement('div');
            label.id = '__capture_label';
            label.style.cssText = `
                position: fixed;
                background: #1890ff;
                color: white;
                padding: 2px 8px;
                font-size: 12px;
                font-family: monospace;
                z-index: 999999;
                display: none;
                border-radius: 2px;
            `;
            document.body.appendChild(label);

            // 创建状态提示（右下角）
            const status = document.createElement('div');
            status.id = '__capture_status';
            status.innerHTML = '捕获模式已激活<br><small>按住 Ctrl 移动鼠标</small>';
            status.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: #1890ff;
                color: white;
                padding: 12px 16px;
                font-size: 14px;
                font-family: system-ui, sans-serif;
                z-index: 999999;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            `;
            document.body.appendChild(status);

            // 3秒后淡出状态提示
            setTimeout(() => {
                status.style.transition = 'opacity 0.5s';
                status.style.opacity = '0';
                setTimeout(() => status.remove(), 500);
            }, 3000);

            // 生成 XPath 选择器
            function getXPath(el) {
                // 优先使用 id
                if (el.id) {
                    return '//' + el.tagName.toLowerCase() + '[@id="' + el.id + '"]';
                }

                // 尝试用属性生成唯一 XPath
                const attrs = ['name', 'data-testid', 'data-id', 'placeholder', 'type'];
                for (const attr of attrs) {
                    const value = el.getAttribute(attr);
                    if (value) {
                        const xpath = '//' + el.tagName.toLowerCase() + '[@' + attr + '="' + value + '"]';
                        try {
                            const result = document.evaluate(xpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                            if (result.snapshotLength === 1) {
                                return xpath;
                            }
                        } catch (e) {}
                    }
                }

                // 尝试用 class
                const className = el.getAttribute('class');
                if (className) {
                    const classes = className.split(' ').filter(c => c && !c.includes(':') && c.length < 30);
                    for (const cls of classes.slice(0, 3)) {
                        const xpath = '//' + el.tagName.toLowerCase() + '[contains(@class, "' + cls + '")]';
                        try {
                            const result = document.evaluate(xpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                            if (result.snapshotLength === 1) {
                                return xpath;
                            }
                        } catch (e) {}
                    }
                }

                // 使用完整路径
                const path = [];
                let current = el;
                while (current && current.nodeType === Node.ELEMENT_NODE) {
                    let index = 1;
                    let sibling = current.previousElementSibling;
                    while (sibling) {
                        if (sibling.tagName === current.tagName) {
                            index++;
                        }
                        sibling = sibling.previousElementSibling;
                    }

                    const tagName = current.tagName.toLowerCase();
                    // 检查是否有同名兄弟节点
                    let hasMultiple = false;
                    sibling = current.parentElement ? current.parentElement.firstElementChild : null;
                    while (sibling) {
                        if (sibling !== current && sibling.tagName === current.tagName) {
                            hasMultiple = true;
                            break;
                        }
                        sibling = sibling.nextElementSibling;
                    }

                    if (hasMultiple) {
                        path.unshift(tagName + '[' + index + ']');
                    } else {
                        path.unshift(tagName);
                    }

                    current = current.parentElement;
                }
                return '/' + path.join('/');
            }

            // 鼠标移动高亮
            document.addEventListener('mousemove', (e) => {
                if (!e.ctrlKey) {
                    overlay.style.display = 'none';
                    label.style.display = 'none';
                    return;
                }

                const el = document.elementFromPoint(e.clientX, e.clientY);
                if (!el || el === overlay || el === label) return;

                const rect = el.getBoundingClientRect();
                overlay.style.left = rect.left + 'px';
                overlay.style.top = rect.top + 'px';
                overlay.style.width = rect.width + 'px';
                overlay.style.height = rect.height + 'px';
                overlay.style.display = 'block';

                label.textContent = el.tagName.toLowerCase() + (el.id ? '#' + el.id : '');
                label.style.left = rect.left + 'px';
                label.style.top = (rect.top - 24) + 'px';
                label.style.display = 'block';
            });

            // Ctrl+点击捕获
            document.addEventListener('click', (e) => {
                if (!e.ctrlKey) return;

                e.preventDefault();
                e.stopPropagation();

                const el = document.elementFromPoint(e.clientX, e.clientY);
                if (!el || el === overlay || el === label) return;

                const xpath = getXPath(el);
                window.__capturedElement = {
                    selector: xpath,
                    tagName: el.tagName.toLowerCase(),
                    id: el.id || null,
                    className: el.className || null,
                    text: el.innerText ? el.innerText.slice(0, 50) : null
                };

                // 闪烁确认效果
                overlay.style.background = 'rgba(82, 196, 26, 0.3)';
                overlay.style.borderColor = '#52c41a';
                setTimeout(() => {
                    overlay.style.background = 'rgba(24, 144, 255, 0.1)';
                    overlay.style.borderColor = '#1890ff';
                }, 300);
            }, true);
        })();
        """

        try:
            await self._page.evaluate(js_code)
            log.info("元素捕获模式已启用")
            return Result.ok(True)
        except Exception as e:
            return Result.fail_with(
                code="B_INJECT_FAILED",
                message=f"注入捕获脚本失败: {e}",
                recoverable=False
            )

    async def get_captured_element(self) -> Result[dict | None]:
        """获取捕获的元素信息"""
        if not self._page:
            return Result.fail_with(
                code="B_NOT_STARTED",
                message="浏览器未启动",
                recoverable=False
            )

        try:
            result = await self._page.evaluate("window.__capturedElement")
            if result:
                # 清除已捕获的元素
                await self._page.evaluate("window.__capturedElement = null")
            return Result.ok(result)
        except Exception as e:
            return Result.fail_with(
                code="B_EVALUATE_FAILED",
                message=f"获取捕获元素失败: {e}",
                recoverable=True
            )

    async def disable_element_capture(self) -> Result[bool]:
        """禁用元素捕获模式"""
        if not self._page:
            return Result.ok(True)

        js_code = """
        (() => {
            window.__elementCaptureEnabled = false;
            window.__capturedElement = null;
            const overlay = document.getElementById('__capture_overlay');
            const label = document.getElementById('__capture_label');
            const status = document.getElementById('__capture_status');
            if (overlay) overlay.remove();
            if (label) label.remove();
            if (status) status.remove();
        })();
        """

        try:
            await self._page.evaluate(js_code)
            log.info("元素捕获模式已禁用")
            return Result.ok(True)
        except Exception:
            return Result.ok(True)

    async def wait_for_element_capture(self, timeout: int = 60000) -> Result[dict]:
        """等待用户捕获元素"""
        if not self._page:
            return Result.fail_with(
                code="B_NOT_STARTED",
                message="浏览器未启动",
                recoverable=False
            )

        start_time = asyncio.get_event_loop().time()
        while True:
            result = await self.get_captured_element()
            if result.success and result.data:
                return Result.ok(result.data)

            elapsed = (asyncio.get_event_loop().time() - start_time) * 1000
            if elapsed >= timeout:
                return Result.fail_with(
                    code="B_TIMEOUT",
                    message="等待元素捕获超时",
                    recoverable=True
                )

            await asyncio.sleep(0.2)

    async def new_page(self) -> Result[Page]:
        """创建新标签页"""
        if not self._context:
            return Result.fail_with(
                code="B_NOT_STARTED",
                message="浏览器未启动",
                recoverable=False
            )

        try:
            page = await self._context.new_page()
            return Result.ok(page)
        except Exception as e:
            return Result.fail_with(
                code="B_NEW_PAGE_FAILED",
                message=f"创建新标签页失败: {e}",
                recoverable=False
            )

    # ==================== Cookie 管理 ====================

    async def load_cookies(self, cookie_file: str = "cookies.json") -> Result[bool]:
        """从文件加载 cookies"""
        if not self._context:
            return Result.fail_with(
                code="B_NOT_STARTED",
                message="浏览器未启动",
                recoverable=False
            )

        cookie_path = Path(cookie_file)
        if not cookie_path.exists():
            return Result.fail_with(
                code="B_COOKIE_NOT_FOUND",
                message=f"Cookie 文件不存在: {cookie_file}",
                recoverable=True
            )

        try:
            with open(cookie_path, "r", encoding="utf-8") as f:
                cookies = json.load(f)

            # 转换格式（如果需要）
            formatted_cookies = []
            for cookie in cookies:
                formatted = {
                    "name": cookie.get("name"),
                    "value": cookie.get("value"),
                    "domain": cookie.get("domain"),
                    "path": cookie.get("path", "/"),
                }
                # 可选字段
                if cookie.get("expires"):
                    formatted["expires"] = cookie["expires"]
                if cookie.get("httpOnly") is not None:
                    formatted["httpOnly"] = cookie["httpOnly"]
                if cookie.get("secure") is not None:
                    formatted["secure"] = cookie["secure"]
                if cookie.get("sameSite"):
                    formatted["sameSite"] = cookie["sameSite"]
                formatted_cookies.append(formatted)

            await self._context.add_cookies(formatted_cookies)
            log.info(f"已加载 {len(formatted_cookies)} 个 cookies")
            return Result.ok(True)
        except Exception as e:
            return Result.fail_with(
                code="B_COOKIE_LOAD_FAILED",
                message=f"加载 cookies 失败: {e}",
                recoverable=True
            )

    async def save_cookies(self, cookie_file: str = "cookies.json") -> Result[bool]:
        """保存 cookies 到文件"""
        if not self._context:
            return Result.fail_with(
                code="B_NOT_STARTED",
                message="浏览器未启动",
                recoverable=False
            )

        try:
            cookies = await self._context.cookies()
            with open(cookie_file, "w", encoding="utf-8") as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            log.info(f"已保存 {len(cookies)} 个 cookies 到 {cookie_file}")
            return Result.ok(True)
        except Exception as e:
            return Result.fail_with(
                code="B_COOKIE_SAVE_FAILED",
                message=f"保存 cookies 失败: {e}",
                recoverable=True
            )
