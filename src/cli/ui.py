"""
终端 UI 组件
"""
import sys
import os
from typing import Callable

# Windows 终端 UTF-8 支持（仅在真正的 Windows 控制台中启用）
def _init_windows_console():
    """初始化 Windows 控制台"""
    if sys.platform != "win32":
        return
    # 检查是否在真正的 Windows 控制台中（而非 Git Bash/MinTTY）
    if not sys.stdout.isatty():
        return
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

_init_windows_console()


class UI:
    """终端 UI 工具类"""

    # 颜色代码
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"

    # 跨平台符号
    SYM_OK = "[OK]" if sys.platform == "win32" else "✓"
    SYM_ERR = "[X]" if sys.platform == "win32" else "✗"
    SYM_WARN = "[!]" if sys.platform == "win32" else "⚠"
    SYM_INFO = "[i]" if sys.platform == "win32" else "ℹ"

    def __init__(self, use_color: bool = True):
        self.use_color = use_color

    def _color(self, text: str, color: str) -> str:
        """添加颜色"""
        if not self.use_color:
            return text
        return f"{color}{text}{self.RESET}"

    def print(self, message: str = ""):
        """打印消息"""
        print(message)

    def print_header(self, title: str):
        """打印标题"""
        line = "=" * 50
        print(self._color(line, self.CYAN))
        print(self._color(f"  {title}", self.BOLD))
        print(self._color(line, self.CYAN))

    def print_success(self, message: str):
        """打印成功消息"""
        print(self._color(f"{self.SYM_OK} {message}", self.GREEN))

    def print_error(self, message: str):
        """打印错误消息"""
        print(self._color(f"{self.SYM_ERR} {message}", self.RED))

    def print_warning(self, message: str):
        """打印警告消息"""
        print(self._color(f"{self.SYM_WARN} {message}", self.YELLOW))

    def print_info(self, message: str):
        """打印信息"""
        print(self._color(f"{self.SYM_INFO} {message}", self.BLUE))

    def input(self, prompt: str, default: str = None) -> str:
        """获取用户输入"""
        if default:
            prompt = f"{prompt} [{default}]: "
        else:
            prompt = f"{prompt}: "

        try:
            value = input(self._color(prompt, self.CYAN)).strip()
            return value if value else (default or "")
        except (KeyboardInterrupt, EOFError):
            print()
            return default or ""

    def confirm(self, message: str, default: bool = True) -> bool:
        """确认操作"""
        suffix = "[Y/n]" if default else "[y/N]"
        prompt = f"{message} {suffix}: "

        try:
            value = input(self._color(prompt, self.CYAN)).strip().lower()
            if not value:
                return default
            return value in ("y", "yes", "是")
        except (KeyboardInterrupt, EOFError):
            print()
            return default

    def select(self, options: list[str], prompt: str = "请选择") -> int:
        """选择菜单"""
        print()
        for i, option in enumerate(options, 1):
            print(f"  {self._color(str(i), self.CYAN)}. {option}")
        print()

        while True:
            try:
                sys.stdout.write(self._color(f"{prompt} [1-{len(options)}]: ", self.CYAN))
                sys.stdout.flush()
                value = sys.stdin.readline().strip()
                if not value:
                    continue
                idx = int(value)
                if 1 <= idx <= len(options):
                    return idx - 1
                self.print_warning(f"请输入 1-{len(options)} 之间的数字")
            except ValueError:
                self.print_warning("请输入有效的数字")
            except (KeyboardInterrupt, EOFError):
                print()
                raise KeyboardInterrupt

    def progress(self, current: int, total: int, message: str = ""):
        """显示进度"""
        percent = (current / total * 100) if total > 0 else 0
        bar_len = 30
        filled = int(bar_len * current / total) if total > 0 else 0
        # Windows 兼容的进度条符号
        fill_char = "#" if sys.platform == "win32" else "█"
        empty_char = "-" if sys.platform == "win32" else "░"
        bar = fill_char * filled + empty_char * (bar_len - filled)

        line = f"\r{self._color('[', self.CYAN)}{bar}{self._color(']', self.CYAN)} {percent:5.1f}%"
        if message:
            line += f" {message}"

        # 清除行尾
        line += " " * 20

        sys.stdout.write(line)
        sys.stdout.flush()

        if current >= total:
            print()  # 完成后换行

    def table(self, headers: list[str], rows: list[list[str]]):
        """打印表格"""
        # 计算列宽
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))

        # 打印表头
        header_line = " | ".join(
            self._color(h.ljust(col_widths[i]), self.BOLD)
            for i, h in enumerate(headers)
        )
        print(header_line)
        print("-" * (sum(col_widths) + 3 * (len(headers) - 1)))

        # 打印行
        for row in rows:
            row_line = " | ".join(
                str(cell).ljust(col_widths[i]) if i < len(col_widths) else str(cell)
                for i, cell in enumerate(row)
            )
            print(row_line)

    def clear(self):
        """清屏"""
        print("\033[2J\033[H", end="")
