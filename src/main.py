"""
Product Uploader - 淘宝商品一键上架工具

主入口文件
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.cli.shell import main


if __name__ == "__main__":
    main()
