#!/usr/bin/env python3
"""
送货单管理工具启动脚本
"""

import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from PyQt5.QtWidgets import QApplication
from src.shipment_manager.main import MainWindow as ShipmentManager

def main():
    app = QApplication(sys.argv)

    # 创建并显示主窗口
    window = ShipmentManager()
    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
