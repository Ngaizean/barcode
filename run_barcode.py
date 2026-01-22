#!/usr/bin/env python3
"""
条形码生成器启动脚本
"""

import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from PyQt5.QtWidgets import QApplication
from src.barcode_generator.main import BarcodeGenerator

def main():
    app = QApplication(sys.argv)

    # 创建并显示主窗口
    window = BarcodeGenerator()
    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
