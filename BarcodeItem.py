from PyQt5.QtWidgets import QFrame, QGridLayout, QLabel, QLineEdit, QPushButton, QSpinBox, QHBoxLayout, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from io import BytesIO
import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont
from reportlab.graphics.barcode import eanbc
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics import renderPM
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black
from pdf2image import convert_from_bytes
from pystrich.ean13 import EAN13Encoder


def calculate_barcode_width(style_code):
    """根据文本实际渲染宽度设置条形码宽度"""
    picWidth = 2
    frontSize = 22.5
    numberFontSize = 20
    spacing = 1.0
    if not style_code:
        return {
            'picWidth': picWidth,
            'frontSize': frontSize,
            'numberFontSize': numberFontSize,
            'spacing': spacing
        }  # 默认宽度

    length = len(style_code)
    if length >= 14 and length < 16:
        picWidth = 3
        frontSize = 29
        numberFontSize = 30
        spacing = 1.1
    elif length >= 16 and length <= 20:
        picWidth = 4
        frontSize = 35
        numberFontSize = 40
        spacing = 1.2

    return {
        'picWidth': picWidth,
        'frontSize': frontSize,
        'numberFontSize': numberFontSize,
        'spacing': spacing
    }

# 添加自定义QSpinBox类来禁用鼠标滚轮事件
class NoWheelSpinBox(QSpinBox):
    def wheelEvent(self, event):
        event.ignore()

class BarcodeItem(QFrame):
    def __init__(self, parent=None, index=0):
        super().__init__(parent)
        self.parent = parent
        self.itemID = index
        self.barcode_image = None
        self.barcode_code = None
        self.style_code = ""
        self.selected = False
        self.initUI()
        self.connectEvents()  # 添加事件连接
        
    def mousePressEvent(self, event):
        # 选中当前条目并通知父窗口
        self.parent.select_item(self)
        super().mousePressEvent(event)
        
    def set_selected(self, selected):
        self.selected = selected
        # 根据选中状态更改样式
        if selected:
            self.setStyleSheet("background-color: #e0f0ff; border: 2px solid #3080e0;")
        else:
            self.setStyleSheet("")
            
    def clearSelection(self):
        """取消自身的选中状态"""
        if self.selected:
            if self.parent:
                # 通知父窗口移除选中状态
                self.parent.selected_items.remove(self)
            self.set_selected(False)
            
    def initUI(self):
        self.setFrameShape(QFrame.Box)
        self.setLineWidth(1)
        
        layout = QGridLayout(self)
        
        # 第一行：款号输入
        self.style_label = QLabel('款号:')
        self.style_input = QLineEdit()
        layout.addWidget(self.style_label, 0, 0)
        layout.addWidget(self.style_input, 0, 1, 1, 2)
        
        # 第二行：条形码输入
        self.code_label = QLabel('条形码编号:')
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText('12位或13位数字')
        layout.addWidget(self.code_label, 1, 0)
        layout.addWidget(self.code_input, 1, 1, 1, 2)
        
        # 第三行：数量输入和生成按钮 - 使用自定义NoWheelSpinBox替代QSpinBox
        self.quantity_label = QLabel('数量:')
        self.quantity_input = NoWheelSpinBox()  # 使用禁用滚轮的SpinBox
        self.quantity_input.setMinimum(1)
        self.quantity_input.setMaximum(9999)
        self.quantity_input.setValue(1)
        self.generate_button = QPushButton('预览条形码')
        self.generate_button.clicked.connect(self.generate_barcode)
        
        layout.addWidget(self.quantity_label, 2, 0)
        layout.addWidget(self.quantity_input, 2, 1)
        layout.addWidget(self.generate_button, 2, 2)
        
        # 第四行：条形码显示区域
        self.barcode_label = QLabel()
        self.barcode_label.setAlignment(Qt.AlignCenter)
        self.barcode_label.setMinimumHeight(200)
        self.barcode_label.setText("(未生成条形码)")
        layout.addWidget(self.barcode_label, 3, 0, 1, 3)
        
        # 第五行：单项操作按钮
        self.save_button = QPushButton('保存此条形码')
        self.save_button.clicked.connect(self.save_barcode)
        self.save_button.setEnabled(False)
        
        self.save_pdf_button = QPushButton('保存此条为PDF')
        self.save_pdf_button.clicked.connect(self.save_to_pdf)
        self.save_pdf_button.setEnabled(False)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.save_pdf_button)
        layout.addLayout(button_layout, 4, 0, 1, 3)
    def generate_barcode(self):
        # 先取消选中状态
        self.clearSelection()
        
        # 获取输入文本
        code_text = self.code_input.text().strip()
        self.style_code = self.style_input.text().strip()
        
        # 验证输入是否符合 EAN-13 格式
        if not code_text.isdigit():
            QMessageBox.warning(self, "输入错误", "请输入有效的条形码编号!")
            return False
            
        # EAN-13 应该是 12 位数字，第 13 位是校验位，会自动计算
        if len(code_text) < 12 or len(code_text) > 13:
            QMessageBox.warning(self, "输入错误", "EAN-13 条形码需要 12 位数字（第 13 位会自动计算）!")
            return False
        barcode_params = calculate_barcode_width(self.style_code)
        try:
            # 保存条形码值以便后续PDF生成
            self.barcode_code = code_text
            
            # 创建内存缓冲区来存储条形码图像
            buffer = BytesIO()
            
            # 使用pystrich生成EAN13条形码到内存缓冲区
            encoder = EAN13Encoder(self.barcode_code)
            image_data = encoder.get_imagedata(bar_width=barcode_params['picWidth'],
                                               fontSize=barcode_params['numberFontSize'],
                                               spacing=barcode_params['spacing'])  # 获取图像数据

            # 将图像数据加载到PIL Image对象
            barcode_image = Image.open(BytesIO(image_data))
            
            # 如果有款号，添加到条形码上方
            if self.style_code:
                im = barcode_image.convert("RGB")
                # 尝试加载系统字体，否则用默认
                try:
                    font = ImageFont.truetype("arial.ttf", barcode_params['frontSize'])
                except IOError:
                    font = ImageFont.load_default()
                
                text = f"NO: {self.style_code}"
                draw_temp = ImageDraw.Draw(im)
                
                # 使用 font.getbbox 来测量文本尺寸
                bbox = font.getbbox(text)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
                
                # 新建一个高出文字高度的白色画布
                print(f"文字宽度: {text_w}, 文字高度: {text_h}")
                print(f"条形码宽度: {im.width}, 条形码高度: {im.height}")
                canvas_img = Image.new("RGB", (im.width, im.height + text_h + 8), "white")
                draw = ImageDraw.Draw(canvas_img)
                
                canvas_img.paste(im, (0, text_h + 10))
                draw.text(((im.width - text_w)//2, 5), text, font=font, fill="black")
                # 把原条码图粘贴到下面
                
                # 保存最终图像
                self.barcode_image = canvas_img
            else:
                # 如果没有款号，直接使用原始条形码
                self.barcode_image = barcode_image
            
            # 将图像保存到缓冲区
            self.barcode_image.save(buffer, format='PNG')
            
            # 重置缓冲区指针位置并创建QPixmap
            buffer.seek(0)
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.read())
            
            # 调整大小并显示
            pixmap = pixmap.scaled(500, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.barcode_label.setPixmap(pixmap)
            
            # 启用保存按钮
            self.save_button.setEnabled(True)
            self.save_pdf_button.setEnabled(True)

            self.parent.refreshData(self.itemID)

            return True


        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成条形码时出错: {str(e)}")
        


    def save_barcode(self):
        self.generate_barcode()
        if self.barcode_image:
            # 打开文件对话框
            file_name = f"{self.style_code}_{self.barcode_code}" if self.style_code else f"{self.barcode_code}"
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存条形码", file_name, "PNG 图片 (*.png);;JPEG 图片 (*.jpg);;所有文件 (*.*)")
            
            if file_path:
                try:
                    # 确保文件有正确的扩展名
                    if not (file_path.endswith('.png') or file_path.endswith('.jpg') or 
                           file_path.endswith('.jpeg')):
                        file_path += '.png'
                    
                    # 保存图像
                    self.barcode_image.save(file_path)
                    QMessageBox.information(self, "成功", f"条形码已保存到 {file_path}")
                    
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"保存条形码时出错: {str(e)}")

    def save_to_pdf(self):
        self.generate_barcode()
        self.parent.save_pdf(type='single', itemID=self.itemID)

    def connectEvents(self):
        """为所有输入框和按钮连接事件，使它们在被操作时取消选中状态"""
        # 为输入框添加点击事件
        self.style_input.mousePressEvent = lambda event: self.handleWidgetClick(event, self.style_input)
        self.code_input.mousePressEvent = lambda event: self.handleWidgetClick(event, self.code_input)
        
        # 为SpinBox添加点击事件
        self.quantity_input.mousePressEvent = lambda event: self.handleWidgetClick(event, self.quantity_input)
        
        # 为按钮添加点击事件处理
        self.generate_button.mousePressEvent = lambda event: self.handleWidgetClick(event, self.generate_button)
        self.save_button.mousePressEvent = lambda event: self.handleWidgetClick(event, self.save_button)
        self.save_pdf_button.mousePressEvent = lambda event: self.handleWidgetClick(event, self.save_pdf_button)
    
    def handleWidgetClick(self, event, widget):
        """处理控件点击事件，取消选中状态"""
        self.clearSelection()
        # 调用原始的mousePressEvent以保持正常功能
        widget.__class__.mousePressEvent(widget, event)
    
    def get_barcode_data(self):
        return {
                'style_code': self.style_code,
                'barcode_code': self.barcode_code,
                'quantity': self.quantity_input.value(),
                'barcode_image': self.barcode_image,
                'itemID': self.itemID
            }
