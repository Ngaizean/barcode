import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QMessageBox, QFileDialog, QSpinBox, QScrollArea,
                            QFrame, QGridLayout, QSplashScreen)  # 添加QSplashScreen
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QTimer  # 添加QTimer
from PyQt5.QtSvg import QSvgRenderer
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from BarcodeItem import BarcodeItem
from PyQt5.QtGui import QPainter

width, height = A4  # A4: 595 x 842 points

# 设置条形码尺寸参数
barcode_width = 90   # 单个条形码宽度（点）
barcode_height = 45   # 单个条形码高度（点）
barcodes_per_row = 7  # 每行放置的条形码数量

# 设置页面边距
margin_x = 10  # 左右边距（点）
margin_y = 32  # 上下边距（点）

# 计算行距和列距
row_spacing = barcode_height + 5  # 行距：条码高 + 文本间隔
col_spacing = (width - 2 * margin_x) / barcodes_per_row
max_items_per_page = barcodes_per_row * 16  # 每页最多 16 行



class BarcodeGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.barcode_items = {}  # 用于存储所有条目
        self.selected_items = []  # 用于追踪当前选中的多个条目
        self.barcode_data_dict = {}  # 用于存储条形码数据
        self.itemIdentifier = 0
        self.set_application_icon()
        self.initUI()
        
    def initUI(self):
        # 获取屏幕尺寸
        screen = QApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()
        
        # 将窗口大小设置为屏幕的一定比例
        width = int(screen_width * 0.4)  # 屏幕宽度的40%
        height = int(screen_height * 0.8)  # 屏幕高度的80%
        
        # 窗口居中显示
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.setWindowTitle('汇庆EAN-13条形码生成器')
        self.setGeometry(x, y, width, height)
        
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建滚动区域用于容纳多个条目
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)
        
        # 创建容器窗口部件
        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)
        
        # 创建布局以保存多个条目
        self.items_layout = QVBoxLayout(scroll_content)
        
        # 添加一个初始条目
        self.add_barcode_item()
        
        # 创建底部按钮布局（分为两层）
        buttons_container = QVBoxLayout()
        
        # 上层按钮布局
        top_button_layout = QHBoxLayout()
        
        # 添加新条目按钮
        self.add_item_button = QPushButton('添加条目')
        self.add_item_button.clicked.connect(self.add_barcode_item)
        
        # 删除选中条目按钮
        self.delete_items_button = QPushButton('删除选中')
        self.delete_items_button.clicked.connect(self.delete_selected_items)
        
        # 清空所有按钮
        self.clear_all_button = QPushButton('一键清空')
        self.clear_all_button.clicked.connect(self.clear_all_items)
        
        # 添加按钮到上层布局
        top_button_layout.addWidget(self.add_item_button)
        top_button_layout.addWidget(self.delete_items_button)
        top_button_layout.addWidget(self.clear_all_button)
        
        # 下层按钮布局
        bottom_button_layout = QHBoxLayout()
        
        # 合并保存为PDF按钮
        self.merge_pdf_button = QPushButton('合并保存PDF')
        self.merge_pdf_button.clicked.connect(lambda: self.save_pdf(type='merge'))
        
        # 分开保存PDF按钮
        self.separate_pdf_button = QPushButton('分开保存PDF')
        self.separate_pdf_button.clicked.connect(lambda: self.save_pdf(type='separate'))
        
        # 添加按钮到下层布局
        bottom_button_layout.addWidget(self.merge_pdf_button)
        bottom_button_layout.addWidget(self.separate_pdf_button)
        
        # 将上下两层布局添加到容器中
        buttons_container.addLayout(top_button_layout)
        buttons_container.addLayout(bottom_button_layout)
        
        # 将按钮容器添加到主布局
        main_layout.addLayout(buttons_container)
        
    def add_barcode_item(self):
        item = BarcodeItem(self, self.itemIdentifier)
        self.barcode_items[self.itemIdentifier] = item
        self.items_layout.addWidget(item)
        self.itemIdentifier += 1

    def clear_all_items(self):
        reply = QMessageBox.question(self, '确认', '确定要清空所有条目吗？',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 移除所有条目
            for item_id, item_widget in list(self.barcode_items.items()):  # 使用list()创建副本进行迭代
                self.items_layout.removeWidget(item_widget)
                item_widget.deleteLater()
        
            # 清空列表
            self.barcode_items.clear()
            self.selected_items.clear()  # 同时清空选中列表
            self.itemIdentifier = 0
            self.barcode_data_dict.clear()  # 清空条形码数据字典
            # 添加一个新的空条目
            self.add_barcode_item()


    def select_item(self, item):
        # 如果项目已经在选中列表中，则取消选中
        if item in self.selected_items:
            self.selected_items.remove(item)
            item.set_selected(False)
        else:
            # 否则添加到选中列表
            self.selected_items.append(item)
            item.set_selected(True)

    def refreshData(self,itemID=None):
        """刷新条形码数据"""
        if itemID is not None:
            self.barcode_data_dict[itemID] = self.barcode_items[itemID].get_barcode_data()
            

    def save_pdf(self,itemID=None,type=None):
        
        def generate_pdf(self,barcode_data_list):

            # 打开文件对话框
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存PDF", "", "PDF文件 (*.pdf);;所有文件 (*.*)")

            if not file_path:
                return False
            
            
            try:
                # 确保文件有正确的扩展名
                if not file_path.endswith('.pdf'):
                    file_path += '.pdf'
                # 创建合并的PDF
                self.generate_merged_pdf(file_path, barcode_data_list)
                QMessageBox.information(self, "成功", f"条形码已保存！")
                return True
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存PDF时出错: {str(e)}")
                return False
    
        for v in self.barcode_items.values():
            if not v.generate_barcode():
                QMessageBox.warning(self, "错误", "出现错误！")
                return
                
            
        for item in self.barcode_items.values():
            item.generate_barcode()
        if type == 'merge':
            generate_pdf(self, self.barcode_data_dict)
        elif type == 'separate':
            # 选择保存目录
            dir_path = QFileDialog.getExistingDirectory(self, "选择保存目录")
            if not dir_path:
                return
            
            try:
                success_count = 0
                for k,v in self.barcode_data_dict.items():
                    # 创建文件名
                    file_name = f"{v['style_code']}_{v['barcode_code']}" if v['style_code'] else f"{v['barcode_code']}"
                    file_path = os.path.join(dir_path, f"{file_name}.pdf")
                    
                    # 生成单个PDF
                    self.generate_merged_pdf(file_path, {k:v})
                    success_count += 1

                QMessageBox.information(self, "成功", f"已成功保存 {success_count} 个PDF文件！")

            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存分开PDF时出错: {str(e)}")
        elif type == 'single':
            for k,v in self.barcode_data_dict.items():
                if k == itemID:
                    generate_pdf(self,{k:v})

    
    

    def generate_merged_pdf(self, file_path, barcode_data_dict):
        # 创建一个PDF画布，使用A4纸张大小
        c = canvas.Canvas(file_path, pagesize=A4)
        

        # 追踪当前位置
        current_row = 0
        current_col = 0
        items_on_page = 0


        for entry in barcode_data_dict:
            pil_img = barcode_data_dict[entry]['barcode_image']  # PIL.Image 对象
            quantity = barcode_data_dict[entry]['quantity']
            style_code = barcode_data_dict[entry].get('style_code', '')

            # 一张图片画多次
            for i in range(quantity):
                # 新页
                if items_on_page >= max_items_per_page:
                    c.showPage()
                    current_row = current_col = items_on_page = 0

                # 计算左下角坐标
                x = margin_x + current_col * col_spacing
                y = height - margin_y - (current_row+1) * row_spacing + 20

                # 转成 ReportLab ImageReader
                img_reader = ImageReader(pil_img)

                # 绘制图像
                c.drawImage(img_reader,
                            x, y,
                            width=barcode_width,
                            height=barcode_height,
                            preserveAspectRatio=True,
                            mask='auto')

                # 更新位置
                current_col += 1
                if current_col >= barcodes_per_row:
                    current_col = 0
                    current_row += 1
                items_on_page += 1

        c.save()

    def get_selected_items(self):
        """返回当前选中的所有条目"""
        return self.selected_items
    
    def clear_selection(self):
        """清除所有选中状态"""
        for item in self.selected_items:
            item.set_selected(False)
        self.selected_items.clear()
    
    def delete_selected_items(self):
        """删除当前选中的所有条目"""
        if not self.selected_items:
            QMessageBox.information(self, "提示", "请先选择要删除的条目")
            return
            
        reply = QMessageBox.question(
            self, 
            '确认', 
            f'确定要删除选中的 {len(self.selected_items)} 个条目吗？',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 从布局和列表中移除选中的条目
            for item in self.selected_items[:]:  # 使用副本进行迭代，因为我们会修改原始列表
                self.items_layout.removeWidget(item)
                
                del self.barcode_items[item.get_barcode_data()['itemID']]
                item.deleteLater()
            
            # 清空选中列表
            self.selected_items.clear()
            
            # 如果删除后没有条目了，添加一个空条目
            if not self.barcode_items:
                self.add_barcode_item()

    def set_application_icon(self):
        try:
            # 使用SVG图标
            svg_path = resource_path("app.svg")
            renderer = QSvgRenderer(svg_path)
            pixmap = QPixmap(128, 128)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            self.setWindowIcon(QIcon(pixmap))
        except Exception as e:
            print(f"无法加载应用图标: {e}")


# 获取应用程序根目录的路径函数
def resource_path(relative_path):
    """获取资源的绝对路径，兼容开发环境和PyInstaller打包后的环境"""
    try:
        # PyInstaller创建临时文件夹并将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# 在主函数中
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 设置字体大小
    screen = app.primaryScreen().geometry()
    font = app.font()
    base_size = 15
    screen_factor = min(screen.width(), screen.height()) / 1080
    font_size = max(base_size, int(15 * screen_factor))
    font.setPointSize(font_size)
    app.setFont(font)
    
    # 使用resource_path来获取打包后的资源路径
    try:
        # 创建启动画面，并调整大小
        original_pixmap = QPixmap(resource_path("splash.png"))
        # 缩放到原来的50%大小（或根据需要调整）
        scaled_pixmap = original_pixmap.scaled(
            original_pixmap.width() // 2, 
            original_pixmap.height() // 2,
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        splash = QSplashScreen(scaled_pixmap, Qt.WindowStaysOnTopHint)
        
        # 可以在启动画面上添加一些消息
        splash.showMessage("正在加载...", Qt.AlignBottom | Qt.AlignCenter, Qt.white)
        splash.show()
        
        # 让应用程序处理事件，确保启动画面显示
        app.processEvents()
    except Exception as e:
        print(f"启动画面加载失败: {e}")
    
    # 创建主窗口
    window = BarcodeGenerator()
    
    # 如果启动画面创建成功，则设置延迟显示主窗口
    if 'splash' in locals():
        QTimer.singleShot(1500, lambda: (window.show(), splash.finish(window)))
    else:
        window.show()
    
    sys.exit(app.exec_())