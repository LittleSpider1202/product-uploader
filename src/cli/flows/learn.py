"""
学习流程 - 字段绑定模式
"""
import asyncio
from datetime import datetime

from src.cli.ui import UI
from src.core import EventBus
from src.infra import BrowserManager, KnowledgeBase
from src.models import FieldType, FieldBinding, BindingConfig, Result
from src.infra.logger import logger, trace
from .base import BaseFlow, FlowResult

log = logger.get("learn_flow")

# 千牛后台 URL
QIANNIU_LOGIN_URL = "https://myseller.taobao.com/"
QIANNIU_PUBLISH_URL = "https://item.publish.taobao.com/sell/v2/publish.htm"


class LearnFlow(BaseFlow):
    """学习流程：字段绑定"""

    FIELD_TYPES = [
        (FieldType.TEXT, "text", "单行文本"),
        (FieldType.NUMBER, "number", "数字"),
        (FieldType.TEXTAREA, "textarea", "多行文本"),
        (FieldType.IMAGE, "image", "单张图片"),
        (FieldType.IMAGES, "images", "多张图片"),
        (FieldType.SELECT, "select", "下拉选择"),
        (FieldType.RICHTEXT, "richtext", "富文本"),
    ]

    def __init__(
        self,
        ui: UI,
        knowledge_base: KnowledgeBase,
        event_bus: EventBus = None
    ):
        super().__init__(ui)
        self.knowledge_base = knowledge_base
        self.event_bus = event_bus or EventBus()
        self.browser: BrowserManager | None = None
        self.config: BindingConfig | None = None

    async def run(self) -> FlowResult:
        """执行学习流程"""
        with trace("学习流程"):
            self.ui.print_header("学习模式 - 字段绑定")
            self.ui.print()
            self.ui.print_info("本模式用于配置千牛字段与淘宝元素的映射关系")
            self.ui.print()

            options = [
                "创建新配置",
                "查看已有配置",
                "返回"
            ]

            idx = self.select(options)

            if idx == 0:
                return await self._create_config()
            elif idx == 1:
                return await self._view_configs()
            else:
                return FlowResult.cancelled("用户返回")

    async def _create_config(self) -> FlowResult:
        """创建新配置"""
        self.ui.print()

        # 输入配置名称
        config_name = self.input("请输入配置名称（如：女装类目）")
        if not config_name:
            return FlowResult.cancelled("未输入配置名称")

        # 创建配置对象
        config_id = f"cfg_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.config = BindingConfig(
            id=config_id,
            name=config_name
        )

        # 启动浏览器
        self.ui.print()
        self.ui.print_info("正在启动浏览器...")
        self.browser = BrowserManager()
        result = await self.browser.start()
        if not result.success:
            self.ui.print_error(f"启动浏览器失败: {result.error.message}")
            return FlowResult.failed(result.error.message)

        try:
            # 阶段1: 登录千牛
            login_result = await self._phase_login()
            if not login_result.success:
                return FlowResult.failed(login_result.error.message)

            # 阶段2: 绑定千牛字段
            bind_target_result = await self._phase_bind_target()
            if not bind_target_result.success:
                return FlowResult.failed(bind_target_result.error.message)

            # 阶段3: 绑定淘宝元素
            bind_source_result = await self._phase_bind_source()
            if not bind_source_result.success:
                return FlowResult.failed(bind_source_result.error.message)

            # 阶段4: 保存配置
            return await self._phase_save()

        except KeyboardInterrupt:
            self.ui.print()
            self.ui.print_info("用户取消操作")
            return FlowResult.cancelled("用户取消")

        finally:
            # 清理浏览器
            await self._cleanup_browser()

    async def _cleanup_browser(self):
        """安全清理浏览器"""
        if self.browser:
            try:
                await self.browser.disable_element_capture()
            except Exception:
                pass
            try:
                await self.browser.stop()
            except Exception:
                pass
            # 给 Playwright 一点时间完成内部清理
            try:
                await asyncio.sleep(0.1)
            except Exception:
                pass
            self.browser = None

    async def _phase_login(self) -> Result[bool]:
        """阶段1: 登录千牛"""
        self.ui.print()
        self.ui.print_header("阶段 1/4: 登录千牛")
        self.ui.print()

        # 检查是否有已保存的 cookies
        from pathlib import Path
        cookie_file = Path("cookies.json")

        login_options = ["手动扫码登录"]
        if cookie_file.exists():
            login_options.insert(0, "使用已保存的 Cookies (推荐)")
        login_options.append("从文件导入 Cookies")

        login_idx = self.select(login_options, "选择登录方式")

        # 导航到千牛后台
        self.ui.print()
        self.ui.print_info("正在打开千牛后台...")
        result = await self.browser.goto(QIANNIU_LOGIN_URL)
        if not result.success:
            return result

        if cookie_file.exists() and login_idx == 0:
            # 使用已保存的 cookies
            self.ui.print_info("正在加载 Cookies...")
            load_result = await self.browser.load_cookies("cookies.json")
            if load_result.success:
                self.ui.print_success("Cookies 加载成功")
                # 刷新页面使 cookies 生效
                await self.browser.page.reload()
                await asyncio.sleep(2)  # 等待页面加载
                self.ui.print()
                self.ui.print_info("如果没有自动登录，请选择手动登录")
                self.ui.input("按回车继续")
            else:
                self.ui.print_warning(f"Cookies 加载失败: {load_result.error.message}")
                self.ui.print_warning("请手动登录")
                self.ui.input("登录完成后按回车继续")

        elif (cookie_file.exists() and login_idx == 2) or (not cookie_file.exists() and login_idx == 1):
            # 从文件导入 cookies
            self.ui.print()
            self.ui.print_info("请将 cookies.json 文件放到项目根目录")
            self.ui.print()
            self.ui.print("获取 Cookies 方法:")
            self.ui.print("  1. 用你的浏览器登录千牛 (https://myseller.taobao.com/)")
            self.ui.print("  2. 按 F12 打开开发者工具")
            self.ui.print("  3. 切换到 Application/应用程序 标签")
            self.ui.print("  4. 左侧 Cookies -> 选择 taobao.com 域名")
            self.ui.print("  5. 右键 -> 导出全部 或 使用扩展导出")
            self.ui.print()
            self.ui.print("或安装浏览器扩展 'EditThisCookie' 导出为 JSON")
            self.ui.print()

            self.ui.input("导入 cookies.json 后按回车继续")

            if cookie_file.exists():
                load_result = await self.browser.load_cookies("cookies.json")
                if load_result.success:
                    self.ui.print_success("Cookies 加载成功")
                    await self.browser.page.reload()
                    await asyncio.sleep(2)
                else:
                    self.ui.print_warning("Cookies 加载失败，请手动登录")
                    self.ui.input("登录完成后按回车继续")
            else:
                self.ui.print_warning("未找到 cookies.json，请手动登录")
                self.ui.input("登录完成后按回车继续")

        else:
            # 手动登录
            self.ui.print()
            self.ui.print_warning("请在浏览器中完成登录")
            self.ui.input("登录完成后按回车继续")

            # 登录成功后保存 cookies
            self.ui.print_info("正在保存 Cookies...")
            save_result = await self.browser.save_cookies("cookies.json")
            if save_result.success:
                self.ui.print_success("Cookies 已保存，下次可直接使用")

        return Result.ok(True)

    async def _phase_bind_target(self) -> Result[bool]:
        """阶段2: 绑定千牛字段"""
        self.ui.print()
        self.ui.print_header("阶段 2/4: 绑定千牛字段")
        self.ui.print()

        self.ui.print_info("请手动进入商品编辑页面")
        self.ui.input("进入编辑页后按回车继续")

        # 记录目标页面 URL
        if self.browser.page:
            self.config.target_url_pattern = self.browser.page.url

        # 启用元素捕获
        await self.browser.enable_element_capture()

        self.ui.print()
        self.ui.print_info("进入字段绑定模式")
        self.ui.print("  - Ctrl + 点击 页面元素自动捕获 XPath")
        self.ui.print("  - 或手动输入 XPath 表达式")
        self.ui.print()

        field_count = 0
        while True:
            self.ui.print(f"--- 字段 #{field_count + 1} ---")

            # 选择绑定方式
            bind_options = [
                "Ctrl+点击 捕获元素",
                "手动输入 XPath",
                "查看已绑定字段",
                "完成绑定 (done)"
            ]
            bind_idx = self.select(bind_options, "选择绑定方式")

            if bind_idx == 2:  # 查看已绑定
                self._print_bound_fields()
                continue

            if bind_idx == 3:  # done
                if field_count == 0:
                    self.ui.print_warning("至少需要绑定一个字段")
                    continue
                break

            xpath = None
            element_text = None

            if bind_idx == 0:  # Ctrl+点击捕获
                self.ui.print()
                # 每次捕获前重新注入脚本（页面导航后脚本会失效）
                await self.browser.enable_element_capture()
                self.ui.print_info("请在页面上 Ctrl+点击 要绑定的元素...")
                self.ui.print_info("（按住 Ctrl 移动鼠标可看到高亮效果）")

                result = await self._wait_for_capture_or_timeout()
                if result is None:
                    self.ui.print_warning("捕获超时，请重试")
                    continue

                xpath = result['selector']
                element_text = result.get('text')

                self.ui.print()
                self.ui.print_success(f"捕获到: {xpath}")
                if element_text:
                    self.ui.print(f"  内容预览: {element_text[:30]}...")

            else:  # 手动输入
                self.ui.print()
                xpath = self.input("请输入 XPath 表达式")
                if not xpath:
                    self.ui.print_warning("已取消")
                    continue

            # 添加 xpath= 前缀（如果没有）
            if not xpath.startswith("xpath="):
                xpath = f"xpath={xpath}"

            # 输入字段信息
            field_name = self.input("字段名称")
            if not field_name:
                self.ui.print_warning("已跳过此元素")
                continue

            # 选择字段类型
            self.ui.print("字段类型:")
            type_options = [f"{ft[1]} - {ft[2]}" for ft in self.FIELD_TYPES]
            type_idx = self.select(type_options)
            field_type = self.FIELD_TYPES[type_idx][0]

            # 是否必填
            required = self.ui.confirm("是否必填", default=True)

            # 创建字段绑定
            binding = FieldBinding(
                name=field_name,
                field_type=field_type,
                required=required,
                target_selector=xpath,
                source_selector=None
            )
            self.config.add_field(binding)
            field_count += 1

            self.ui.print()
            self.ui.print_success(
                f"[OK] 已添加: {field_name} ({field_type.value}, "
                f"{'必填' if required else '选填'})"
            )
            self.ui.print()

        self.ui.print()
        self.ui.print_success(f"千牛字段绑定完成，共 {field_count} 个字段")
        return Result.ok(True)

    async def _phase_bind_source(self) -> Result[bool]:
        """阶段3: 绑定淘宝元素"""
        self.ui.print()
        self.ui.print_header("阶段 3/4: 绑定淘宝元素")
        self.ui.print()

        # 输入淘宝商品链接
        taobao_url = self.input("请输入淘宝商品链接")
        if not taobao_url:
            self.ui.print_warning("跳过淘宝元素绑定")
            return Result.ok(True)

        # 打开新标签页
        self.ui.print_info("正在打开淘宝页面...")
        new_page_result = await self.browser.new_page()
        if not new_page_result.success:
            self.ui.print_error("打开新标签页失败")
            return Result.ok(True)  # 不阻断流程

        new_page = new_page_result.data
        try:
            await new_page.goto(taobao_url, wait_until="domcontentloaded")
        except Exception as e:
            self.ui.print_error(f"打开淘宝页面失败: {e}")
            return Result.ok(True)

        # 切换到新页面进行元素捕获
        # 保存原页面引用
        original_page = self.browser._page
        self.browser._page = new_page

        # 重新启用元素捕获
        await self.browser.enable_element_capture()

        self.config.source_url_pattern = taobao_url

        self.ui.print()
        self.ui.print_info("请在淘宝页面上绑定对应元素")
        self.ui.print("  - Ctrl + 点击 捕获元素")
        self.ui.print("  - 或手动输入 XPath")
        self.ui.print()

        # 逐个字段绑定
        for binding in self.config.fields:
            self.ui.print(f"绑定【{binding.name}】:")

            bind_options = [
                "Ctrl+点击 捕获元素",
                "手动输入 XPath",
                "跳过此字段"
            ]
            bind_idx = self.select(bind_options)

            if bind_idx == 2:  # 跳过
                self.ui.print_warning(f"  跳过: {binding.name}")
                self.ui.print()
                continue

            xpath = None

            if bind_idx == 0:  # Ctrl+点击
                # 重新注入脚本
                await self.browser.enable_element_capture()
                self.ui.print_info("请在页面上 Ctrl+点击 对应元素...")
                result = await self._wait_for_capture_or_timeout(timeout=60)

                if result is None:
                    self.ui.print_warning(f"  超时跳过: {binding.name}")
                    self.ui.print()
                    continue

                xpath = result['selector']
            else:  # 手动输入
                xpath = self.input("请输入 XPath 表达式")
                if not xpath:
                    self.ui.print_warning(f"  跳过: {binding.name}")
                    self.ui.print()
                    continue

            # 添加 xpath= 前缀
            if not xpath.startswith("xpath="):
                xpath = f"xpath={xpath}"

            binding.source_selector = xpath
            self.ui.print_success(f"  [OK] {binding.name} -> {xpath}")

            self.ui.print()

        # 恢复原页面
        self.browser._page = original_page

        return Result.ok(True)

    async def _phase_save(self) -> FlowResult:
        """阶段4: 保存配置"""
        self.ui.print()
        self.ui.print_header("阶段 4/4: 保存配置")
        self.ui.print()

        # 显示绑定结果
        self.ui.print("绑定结果预览:")
        self.ui.print()
        self._print_config_table()

        self.ui.print()
        if not self.ui.confirm("保存此配置", default=True):
            return FlowResult.cancelled("用户取消保存")

        # 保存配置
        save_result = self._save_config()
        if save_result.success:
            self.ui.print()
            self.ui.print_success(f"配置已保存: {self.config.name}")
            return FlowResult.success("配置创建成功", {"config_id": self.config.id})
        else:
            self.ui.print_error(f"保存失败: {save_result.error.message}")
            return FlowResult.failed(save_result.error.message)

    def _print_bound_fields(self):
        """打印已绑定的字段（简洁版）"""
        if not self.config.fields:
            self.ui.print()
            self.ui.print_warning("暂无已绑定字段")
            self.ui.print()
            return

        self.ui.print()
        self.ui.print(f"已绑定 {len(self.config.fields)} 个字段:")
        self.ui.print()
        self.ui.print(f"  {'#':<3} | {'字段名':<12} | {'类型':<10} | {'必填':<4} | {'XPath'}")
        self.ui.print("  " + "-" * 70)

        for i, f in enumerate(self.config.fields, 1):
            xpath = f.target_selector.replace("xpath=", "")
            if len(xpath) > 35:
                xpath = xpath[:32] + "..."
            required = "Y" if f.required else "N"
            self.ui.print(f"  {i:<3} | {f.name:<12} | {f.field_type.value:<10} | {required:<4} | {xpath}")

        self.ui.print()

    def _print_config_table(self):
        """打印配置表格"""
        # 表头
        self.ui.print(
            f"  {'字段名':<10} | {'类型':<10} | {'必填':<4} | "
            f"{'千牛选择器':<25} | {'淘宝选择器':<25}"
        )
        self.ui.print("  " + "-" * 90)

        # 数据行
        for f in self.config.fields:
            target = f.target_selector[:22] + "..." if len(f.target_selector) > 25 else f.target_selector
            source = (f.source_selector[:22] + "..." if f.source_selector and len(f.source_selector) > 25
                      else f.source_selector or "-")
            required = "Y" if f.required else "N"

            self.ui.print(
                f"  {f.name:<10} | {f.field_type.value:<10} | {required:<4} | "
                f"{target:<25} | {source:<25}"
            )

    def _save_config(self) -> Result[bool]:
        """保存配置到文件"""
        import json
        from pathlib import Path

        try:
            # 创建目录
            config_dir = Path("data/bindings")
            config_dir.mkdir(parents=True, exist_ok=True)

            # 保存文件
            config_file = config_dir / f"{self.config.id}.json"
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(self.config.to_dict(), f, ensure_ascii=False, indent=2)

            log.info("配置已保存", config_id=self.config.id, path=str(config_file))
            return Result.ok(True)
        except Exception as e:
            log.error("保存配置失败", error=str(e))
            return Result.fail_with(
                code="S_WRITE_FAILED",
                message=f"保存失败: {e}",
                recoverable=False
            )

    async def _view_configs(self) -> FlowResult:
        """查看已有配置"""
        import json
        from pathlib import Path

        config_dir = Path("data/bindings")
        if not config_dir.exists():
            self.ui.print_warning("暂无配置")
            return FlowResult.cancelled("无配置")

        config_files = list(config_dir.glob("*.json"))
        if not config_files:
            self.ui.print_warning("暂无配置")
            return FlowResult.cancelled("无配置")

        self.ui.print()
        self.ui.print("已有配置:")
        self.ui.print()

        for cf in config_files:
            try:
                with open(cf, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    config = BindingConfig.from_dict(data)
                    self.ui.print(
                        f"  - {config.name} ({len(config.fields)} 个字段) "
                        f"[{config.created_at.strftime('%Y-%m-%d')}]"
                    )
            except Exception:
                continue

        self.ui.print()
        return FlowResult.success("查看完成")

    async def _wait_for_capture_or_timeout(self, timeout: int = 60) -> dict | None:
        """等待元素捕获或超时"""
        start_time = asyncio.get_event_loop().time()

        while True:
            # 检查是否有捕获的元素
            result = await self.browser.get_captured_element()
            if result.success and result.data:
                return result.data

            # 检查超时
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= timeout:
                return None

            await asyncio.sleep(0.2)
