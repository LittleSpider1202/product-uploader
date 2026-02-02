"""
交互式 Shell - 主入口
"""
import asyncio
from pathlib import Path

from src.cli.ui import UI
from src.cli.flows import CollectFlow, UploadFlow, LearnFlow, KnowledgeFlow
from src.core import EventBus
from src.infra import BrowserManager, BrowserConfig, ProductStorage, KnowledgeBase, ConfigManager
from src.infra import logger, trace, get_run_id

log = logger.get("shell")


class InteractiveShell:
    """交互式 Shell"""

    VERSION = "0.1.0"

    def __init__(self):
        self.ui = UI()
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load()

        # 初始化组件
        data_dir = Path(self.config.data_dir)
        self.storage = ProductStorage(data_dir / "products")
        self.knowledge_base = KnowledgeBase(data_dir)
        self.event_bus = EventBus()

        # 浏览器管理器（延迟初始化）
        self.browser: BrowserManager | None = None

    async def start(self):
        """启动 Shell"""
        self._print_welcome()

        while True:
            try:
                choice = self._show_main_menu()

                if choice == 0:  # 学习模式
                    with trace("学习模式"):
                        # codegen 会自己打开浏览器，不需要预先启动
                        flow = LearnFlow(
                            self.ui, self.knowledge_base, self.event_bus
                        )
                        await flow.run()

                elif choice == 1:  # 采集商品
                    with trace("采集商品"):
                        await self._ensure_browser()
                        flow = CollectFlow(
                            self.ui, self.browser, self.storage, self.event_bus
                        )
                        await flow.run()

                elif choice == 2:  # 上架商品
                    with trace("上架商品"):
                        await self._ensure_browser()
                        flow = UploadFlow(
                            self.ui, self.browser, self.storage,
                            self.knowledge_base, self.event_bus
                        )
                        await flow.run()

                elif choice == 3:  # 知识库
                    with trace("知识库管理"):
                        flow = KnowledgeFlow(self.ui, self.knowledge_base)
                        await flow.run()

                elif choice == 4:  # 设置
                    self._show_settings()

                elif choice == 5:  # 退出
                    log.info("用户退出")
                    break

            except KeyboardInterrupt:
                self.ui.print()
                self.ui.print_info("收到退出信号...")
                log.info("用户按 Ctrl+C 退出")
                break

        await self._cleanup()
        self.ui.print()
        self.ui.print_info("再见！")

    def _print_welcome(self):
        """打印欢迎信息"""
        self.ui.clear()
        self.ui.print()
        self.ui.print_header("淘宝商品一键上架工具")
        self.ui.print()
        self.ui.print(f"  版本: {self.VERSION}")
        self.ui.print(f"  运行ID: {get_run_id()}")
        self.ui.print()

        # 显示知识库状态
        stats = self.knowledge_base.get_stats()
        if stats["total_solutions"] > 0:
            self.ui.print_success(
                f"知识库已加载: {stats['total_solutions']} 个方案"
            )
            self.ui.print()
        else:
            self._print_guide()

    def _print_guide(self):
        """打印新手引导"""
        self.ui.print_warning("知识库为空，请先完成初始化")
        self.ui.print()
        self.ui.print("  使用流程：")
        self.ui.print("  ─────────────────────────────────────")
        self.ui.print("  1. 学习模式  录制你在天猫后台的操作")
        self.ui.print("  2. 采集商品  从淘宝复制商品信息")
        self.ui.print("  3. 上架商品  自动填充并发布到店铺")
        self.ui.print("  ─────────────────────────────────────")
        self.ui.print()
        self.ui.print_info("首次使用请选择「学习模式」录制操作")
        self.ui.print()

    def _show_main_menu(self) -> int:
        """显示主菜单"""
        options = [
            "学习模式 - 录制操作方案（首次使用请先选这个）",
            "采集商品 - 从淘宝复制商品信息",
            "上架商品 - 将商品发布到店铺",
            "知识库   - 管理已录制的方案",
            "设置",
            "退出"
        ]
        return self.ui.select(options, "请选择操作")

    async def _ensure_browser(self):
        """确保浏览器已启动"""
        if self.browser is None:
            self.ui.print_info("正在启动浏览器...")
            log.info("启动浏览器")

            browser_config = BrowserConfig(
                headless=self.config.browser_headless,
                slow_mo=self.config.browser_slow_mo,
                timeout=self.config.browser_timeout,
                user_data_dir=self.config.user_data_dir
            )
            self.browser = BrowserManager(browser_config)

            result = await self.browser.start()
            if result.success:
                self.ui.print_success("浏览器已启动")
                log.info("浏览器启动成功")
            else:
                self.ui.print_error(f"浏览器启动失败: {result.error.message}")
                log.error("浏览器启动失败", error=result.error.message)
                self.browser = None

    def _show_settings(self):
        """显示设置"""
        self.ui.print_header("设置")
        self.ui.print()

        options = [
            f"无头模式: {'开启' if self.config.browser_headless else '关闭'}",
            f"操作延迟: {self.config.browser_slow_mo}ms",
            f"超时时间: {self.config.browser_timeout}ms",
            "保存设置",
            "返回"
        ]

        while True:
            idx = self.ui.select(options, "选择要修改的设置")

            if idx == 0:
                self.config.browser_headless = not self.config.browser_headless
                options[0] = f"无头模式: {'开启' if self.config.browser_headless else '关闭'}"
            elif idx == 1:
                value = self.ui.input("输入操作延迟 (ms)", str(self.config.browser_slow_mo))
                try:
                    self.config.browser_slow_mo = int(value)
                    options[1] = f"操作延迟: {self.config.browser_slow_mo}ms"
                except ValueError:
                    self.ui.print_warning("请输入有效数字")
            elif idx == 2:
                value = self.ui.input("输入超时时间 (ms)", str(self.config.browser_timeout))
                try:
                    self.config.browser_timeout = int(value)
                    options[2] = f"超时时间: {self.config.browser_timeout}ms"
                except ValueError:
                    self.ui.print_warning("请输入有效数字")
            elif idx == 3:
                self.config_manager.save(self.config)
                self.ui.print_success("设置已保存")
            else:
                break

    async def _cleanup(self):
        """清理资源"""
        if self.browser:
            self.ui.print_info("正在关闭浏览器...")
            try:
                await self.browser.stop()
            except Exception as e:
                log.warning("关闭浏览器时出错", error=str(e))


class _OutputFilter:
    """过滤 stdout/stderr 中的 Playwright/asyncio 清理错误"""
    FILTER_PATTERNS = [
        "TargetClosedError",
        "I/O operation on closed pipe",
        "Exception ignored",
        "Future exception was never retrieved",
        "unclosed transport",
        "_ProactorBasePipeTransport",
        "ResourceWarning",
    ]

    def __init__(self, original):
        self.original = original

    def write(self, msg):
        # 过滤 Playwright 和 asyncio 的清理错误
        if any(x in msg for x in self.FILTER_PATTERNS):
            return
        self.original.write(msg)

    def flush(self):
        self.original.flush()

    def fileno(self):
        return self.original.fileno()

    def __getattr__(self, name):
        return getattr(self.original, name)


def main():
    """程序入口"""
    import warnings
    import sys

    # 抑制各类清理警告
    warnings.filterwarnings("ignore", category=ResourceWarning)
    warnings.filterwarnings("ignore", message=".*unclosed.*")

    # 设置 stderr 过滤（不在退出时恢复，确保能过滤退出时的错误）
    sys.stderr = _OutputFilter(sys.__stderr__)

    try:
        shell = InteractiveShell()
        asyncio.run(shell.start())
    except KeyboardInterrupt:
        # 静默处理 Ctrl+C，不显示 traceback
        print()
    except Exception as e:
        log.error("程序异常退出", error=str(e))
        raise


if __name__ == "__main__":
    main()
