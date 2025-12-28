import sys
import os
import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QTableWidget, QTableWidgetItem, 
                             QPushButton, QHeaderView, QFormLayout, QFileDialog, 
                             QMessageBox, QMenu, QInputDialog, QAction, QScrollArea,
                             QFrame, QSizePolicy, QGridLayout)
from PyQt5.QtCore import Qt, QRectF, QSizeF, QMarginsF
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtGui import QTextDocument, QPainter, QAbstractTextDocumentLayout

# --- 单个送货单控件 (容器) ---
class SingleDeliveryNote(QWidget):
    def __init__(self, parent_area, index):
        super().__init__()
        self.parent_area = parent_area # 引用主窗口以便调用删除等
        self.index = index
        self.is_collapsed = False
        
        self.init_ui()
        self.calculate_totals() # 初始计算

    def init_ui(self):
        # 外层边框布局
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self.main_layout)

        # --- 1. 容器控制栏 (修改点：按钮移到左边) ---
        control_bar = QHBoxLayout()
        
        # 1.1 标题在最左边
        self.lbl_id = QLabel(f"送货单 #{self.index}")
        self.lbl_id.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        control_bar.addWidget(self.lbl_id)

        control_bar.addSpacing(15) # 间距

        # 1.2 折叠按钮紧跟标题
        self.btn_collapse = QPushButton("🔽 折叠/展开")
        self.btn_collapse.setStyleSheet("font-size: 16px; padding: 5px 10px;")
        self.btn_collapse.clicked.connect(self.toggle_collapse)
        control_bar.addWidget(self.btn_collapse)

        # 1.3 删除按钮紧跟折叠按钮
        self.btn_remove = QPushButton("❌ 删除此单")
        self.btn_remove.setStyleSheet("font-size: 16px; padding: 5px 10px; color: red;")
        self.btn_remove.clicked.connect(lambda: self.parent_area.remove_note(self))
        control_bar.addWidget(self.btn_remove)
        
        # 1.4 弹簧在最后，把内容顶到左边
        control_bar.addStretch()
        
        self.main_layout.addLayout(control_bar)

        # --- 2. 实际内容区域 (可折叠部分) ---
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        
        # 为了美观，给内容区域加个边框
        self.content_widget.setStyleSheet(".QWidget { border: 2px solid #ccc; border-radius: 10px; background-color: white; }")
        
        self._init_content_ui() # 加载原有的单据UI逻辑
        
        self.main_layout.addWidget(self.content_widget)

    def toggle_collapse(self):
        self.is_collapsed = not self.is_collapsed
        if self.is_collapsed:
            self.content_widget.setVisible(False)
            self.btn_collapse.setText("▶️ 展开")
        else:
            self.content_widget.setVisible(True)
            self.btn_collapse.setText("🔽 折叠")

    def _init_content_ui(self):
        """此处复用原本的UI构建逻辑"""
        
        # --- 标题 ---
        self.title_edit = QLineEdit("送 货 单")
        self.title_edit.setAlignment(Qt.AlignCenter)
        self.title_edit.setStyleSheet("font-size: 48px; font-weight: bold; border: none; background: transparent; margin: 10px 0;")
        self.content_layout.addWidget(self.title_edit)

        # --- 头部信息 ---
        header_grid = QGridLayout()
        header_grid.setContentsMargins(20, 10, 20, 10)
        header_grid.setHorizontalSpacing(50) 
        
        input_style = "QLineEdit { font-size: 20px; padding: 5px; border: 1px solid #ddd; }"
        label_style = "QLabel { font-size: 20px; font-weight: bold; }"
        
        self.input_customer = QLineEdit("XX商贸有限公司")
        self.input_customer.setStyleSheet(input_style)
        self.input_address = QLineEdit("上海市浦东新区XX路XX号")
        self.input_address.setStyleSheet(input_style)
        
        self.input_date = QLineEdit(datetime.date.today().strftime("%Y-%m-%d"))
        self.input_date.setStyleSheet(input_style)
        self.input_phone = QLineEdit("13800138000")
        self.input_phone.setStyleSheet(input_style)

        header_grid.addWidget(QLabel("收货单位：", styleSheet=label_style), 0, 0, Qt.AlignRight)
        header_grid.addWidget(self.input_customer, 0, 1)
        header_grid.addWidget(QLabel("日期：", styleSheet=label_style), 0, 2, Qt.AlignRight)
        header_grid.addWidget(self.input_date, 0, 3)
        
        header_grid.addWidget(QLabel("收货地址：", styleSheet=label_style), 1, 0, Qt.AlignRight)
        header_grid.addWidget(self.input_address, 1, 1)
        header_grid.addWidget(QLabel("联系电话：", styleSheet=label_style), 1, 2, Qt.AlignRight)
        header_grid.addWidget(self.input_phone, 1, 3)

        self.content_layout.addLayout(header_grid)

        # --- 表格区域 ---
        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget { font-size: 18px; border: 1px solid #ccc; } 
            QHeaderView::section { font-size: 18px; font-weight: bold; padding: 5px; height: 40px; background-color: #f0f0f0; }
        """)
        
        self.columns = ['货号', '名称', '规格', '单位', '数量', '单价', '金额', '备注']
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)
        self.table.verticalHeader().setVisible(False)

        # 表头右键菜单
        header = self.table.horizontalHeader()
        header.setContextMenuPolicy(Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(self.show_header_menu)
        header.sectionDoubleClicked.connect(self.rename_column_at)
        
        header.setSectionResizeMode(QHeaderView.Stretch)
        # header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        
        compact_columns = [0, 3, 4, 5, 6] # 序号、单位、数量、单价、金额
        for col_idx in compact_columns:
            header.setSectionResizeMode(col_idx, QHeaderView.ResizeToContents)
        
        self.table.verticalHeader().setDefaultSectionSize(45)

        # (修改点：启用表格内容的右键菜单)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_body_menu)

        # 初始化数据
        initial_data = [
            ['A4打印纸', '70g 500张', '包', 10, 25, ''],
            ['黑色签字笔', '0.5mm', '支', 50, 2.5, ''],
            ['透明胶带', '4.5cm宽', '卷', 20, 5, '']
        ]
        for row_data in initial_data:
            self.add_row(data=row_data)

        self.add_row() # 空行
        self.table.itemChanged.connect(self.on_item_changed)
        self.content_layout.addWidget(self.table)
        
        # --- 按钮栏 ---
        btn_bar = QHBoxLayout()
        btn_add_r = QPushButton("➕ 加一行")
        btn_add_r.clicked.connect(lambda: self.add_row())
        btn_add_c = QPushButton("➕ 加一列")
        btn_add_c.clicked.connect(self.add_column)
        btn_bar.addWidget(btn_add_r)
        btn_bar.addWidget(btn_add_c)
        btn_bar.addStretch()
        self.content_layout.addLayout(btn_bar)

        # --- 合计区域 ---
        total_layout = QHBoxLayout()
        self.lbl_chinese_total = QLabel("合计(大写): 零元整")
        self.lbl_chinese_total.setStyleSheet("font-weight: bold; font-size: 22px; color: #555;")
        self.lbl_num_total = QLabel("总金额: 0.00")
        self.lbl_num_total.setStyleSheet("font-weight: bold; font-size: 28px; color: #d9534f;")

        total_layout.addWidget(self.lbl_chinese_total)
        total_layout.addStretch()
        total_layout.addWidget(self.lbl_num_total)
        self.content_layout.addLayout(total_layout)

        # --- 底部签名 ---
        footer_layout = QHBoxLayout()
        self.input_deliverer = QLineEdit("王五")
        self.input_deliverer.setStyleSheet(input_style)
        self.input_receiver = QLineEdit("")
        self.input_receiver.setStyleSheet(input_style)

        footer_label_style = "QLabel { font-size: 20px; font-weight: bold; }"
        footer_layout.addStretch(1)
        footer_layout.addWidget(QLabel("送货方(签字):", styleSheet=footer_label_style))
        footer_layout.addWidget(self.input_deliverer)
        footer_layout.addStretch(1)
        footer_layout.addWidget(QLabel("收货方(签字):", styleSheet=footer_label_style))
        footer_layout.addWidget(self.input_receiver)
        footer_layout.addStretch(1)
        self.content_layout.addLayout(footer_layout)

    # --- 逻辑方法: 右键行菜单 (新增) ---
    def show_body_menu(self, pos):
        """显示表格内容区域的右键菜单（行操作）"""
        index = self.table.indexAt(pos)
        row = index.row()
        
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { font-size: 16px; padding: 5px; }")

        # 无论是否点中行，都允许在最后添加，但这里主要处理点中行的情况
        if row >= 0:
            action_del = QAction(f"❌ 删除第 {row + 1} 行", self)
            action_del.triggered.connect(lambda: self.delete_row_at(row))
            
            action_insert_above = QAction("👆 在上方插入一行", self)
            action_insert_above.triggered.connect(lambda: self.insert_row_at(row))

            menu.addAction(action_del)
            menu.addAction(action_insert_above)
        else:
            # 如果点在空白处（非行上）
            action_add = QAction("➕ 在末尾添加一行", self)
            action_add.triggered.connect(lambda: self.add_row())
            menu.addAction(action_add)

        menu.exec_(self.table.mapToGlobal(pos))

    def delete_row_at(self, row):
        """删除指定行并重新计算"""
        self.table.removeRow(row)
        # 重新排序号
        for r in range(self.table.rowCount()):
            item = self.table.item(r, 0)
            if item:
                item.setText(str(r + 1))
        self.calculate_totals() # 重新计算总价

    def insert_row_at(self, row):
        """在指定位置插入行"""
        self.table.insertRow(row)
        # 填充序号和只读属性
        item_idx = QTableWidgetItem(str(row + 1))
        item_idx.setFlags(item_idx.flags() ^ Qt.ItemIsEditable)
        item_idx.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 0, item_idx)

        # 重新排序号 (因为插入点之后的序号变了)
        for r in range(row, self.table.rowCount()):
             item = self.table.item(r, 0)
             if not item:
                 # 防止刚插入的行还没item的情况（虽然上面set了）
                 item_idx_new = QTableWidgetItem(str(r + 1))
                 item_idx_new.setFlags(item_idx_new.flags() ^ Qt.ItemIsEditable)
                 item_idx_new.setTextAlignment(Qt.AlignCenter)
                 self.table.setItem(r, 0, item_idx_new)
             else:
                 item.setText(str(r + 1))
        
        # 确保金额列不可编辑
        headers = [self.table.horizontalHeaderItem(c).text() for c in range(self.table.columnCount())]
        if "金额" in headers:
            idx_amt = headers.index("金额")
            item_amt = QTableWidgetItem("0.00")
            item_amt.setFlags(item_amt.flags() ^ Qt.ItemIsEditable)
            self.table.setItem(row, idx_amt, item_amt)

    # --- 逻辑方法 (表头菜单 - 复用) ---
    def show_header_menu(self, pos):
        index = self.table.horizontalHeader().logicalIndexAt(pos)
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { font-size: 16px; padding: 5px; }")
        action_insert = QAction("👈 在左侧插入列", self)
        action_insert.triggered.connect(lambda: self.insert_column_at(index))
        action_rename = QAction("✏️ 修改列名", self)
        action_rename.triggered.connect(lambda: self.rename_column_at(index))
        action_delete = QAction("🗑️ 删除本列", self)
        action_delete.triggered.connect(lambda: self.delete_column_at(index))
        menu.addAction(action_insert)
        menu.addAction(action_rename)
        menu.addSeparator()
        menu.addAction(action_delete)
        menu.exec_(self.table.mapToGlobal(pos))

    def insert_column_at(self, index):
        self.table.insertColumn(index)
        self.table.setHorizontalHeaderItem(index, QTableWidgetItem("新列"))
        self.refresh_header_mode()

    def delete_column_at(self, index):
        if self.table.columnCount() <= 1: return
        self.table.removeColumn(index)

    def rename_column_at(self, index):
        old_text = self.table.horizontalHeaderItem(index).text()
        new_text, ok = QInputDialog.getText(self, "修改表头", "请输入新列名:", text=old_text)
        if ok and new_text:
            self.table.horizontalHeaderItem(index).setText(new_text)
            self.on_item_changed(None)

    def refresh_header_mode(self):
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)

    def add_column(self):
        self.insert_column_at(self.table.columnCount())

    def add_row(self, data=None):
        row = self.table.rowCount()
        self.table.insertRow(row)
        item_idx = QTableWidgetItem(str(row + 1))
        item_idx.setFlags(item_idx.flags() ^ Qt.ItemIsEditable)
        item_idx.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 0, item_idx)
        
        headers = [self.table.horizontalHeaderItem(c).text() for c in range(self.table.columnCount())]
        name = data[0] if data else ""
        spec = data[1] if data else ""
        unit = data[2] if data else ""
        qty  = str(data[3]) if data and len(data)>3 else "0"
        price = str(data[4]) if data and len(data)>4 else "0"
        remark = data[5] if data and len(data)>5 else ""

        def set_cell(col_name, val):
            if col_name in headers:
                self.table.setItem(row, headers.index(col_name), QTableWidgetItem(val))

        if "名称" in headers:
            set_cell("名称", name)
            set_cell("规格", spec)
            set_cell("单位", unit)
            set_cell("数量", qty)
            set_cell("单价", price)
            set_cell("备注", remark)
        else:
            if self.table.columnCount() > 1: self.table.setItem(row, 1, QTableWidgetItem(name))
        
        if "金额" in headers:
            idx = headers.index("金额")
            item_amt = QTableWidgetItem("0.00")
            item_amt.setFlags(item_amt.flags() ^ Qt.ItemIsEditable)
            self.table.setItem(row, idx, item_amt)
        
        self.calculate_row(row)

    def on_item_changed(self, item):
        if item is None: return
        headers = [self.table.horizontalHeaderItem(c).text() for c in range(self.table.columnCount())]
        if "数量" in headers and "单价" in headers:
            idx_qty = headers.index("数量")
            idx_price = headers.index("单价")
            if item.column() == idx_qty or item.column() == idx_price:
                self.calculate_row(item.row())
                self.calculate_totals()

    def calculate_row(self, row):
        headers = [self.table.horizontalHeaderItem(c).text() for c in range(self.table.columnCount())]
        if "数量" not in headers or "单价" not in headers or "金额" not in headers: return
        idx_qty = headers.index("数量")
        idx_price = headers.index("单价")
        idx_amt = headers.index("金额")
        try:
            self.table.blockSignals(True)
            qty_item = self.table.item(row, idx_qty)
            price_item = self.table.item(row, idx_price)
            qty = float(qty_item.text()) if qty_item and qty_item.text() else 0
            price = float(price_item.text()) if price_item and price_item.text() else 0
            amount = qty * price
            amt_item = self.table.item(row, idx_amt)
            if amt_item is None:
                amt_item = QTableWidgetItem("0.00")
                amt_item.setFlags(amt_item.flags() ^ Qt.ItemIsEditable)
                self.table.setItem(row, idx_amt, amt_item)
            amt_item.setText(f"{amount:.2f}")
        except ValueError: pass
        finally: self.table.blockSignals(False)

    def calculate_totals(self):
        headers = [self.table.horizontalHeaderItem(c).text() for c in range(self.table.columnCount())]
        if "金额" not in headers: return
        idx_amt = headers.index("金额")
        total = 0.0
        for row in range(self.table.rowCount()):
            try:
                item = self.table.item(row, idx_amt)
                if item: total += float(item.text())
            except ValueError: pass
        self.lbl_num_total.setText(f"总金额: {total:.2f}")
        self.lbl_chinese_total.setText(f"合计(大写): {self.digit_to_chinese(total)}")

    def digit_to_chinese(self, num):
        if num == 0: return "零元整"
        units = ['', '拾', '佰', '仟']
        big_units = ['', '万', '亿']
        nums = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
        str_num = f"{num:.2f}"
        integer_part, decimal_part = str_num.split('.')
        result = []
        integer_part = integer_part[::-1]
        for i, digit in enumerate(integer_part):
            n = int(digit)
            unit_idx = i % 4
            big_unit_idx = i // 4
            if i > 0 and unit_idx == 0: result.append(big_units[big_unit_idx])
            if n != 0:
                result.append(units[unit_idx])
                result.append(nums[n])
            else:
                if result and result[-1] != '零' and result[-1] not in big_units:
                    result.append('零')
        result_str = "".join(result[::-1]).replace("零万", "万").replace("零亿", "亿").strip("零")
        if not result_str: result_str = "零"
        result_str += "元"
        jiao, fen = int(decimal_part[0]), int(decimal_part[1])
        if jiao == 0 and fen == 0: result_str += "整"
        else:
            if jiao != 0: result_str += f"{nums[jiao]}角"
            if fen != 0: result_str += f"{nums[fen]}分"
        return result_str

    # --- HTML 生成逻辑 ---
    # --- HTML 生成逻辑 ---
    def generate_html(self):
        """生成本送货单的 HTML 代码片段"""
        headers = [self.table.horizontalHeaderItem(c).text() for c in range(self.table.columnCount())]
        
        # --- 1. 生成动态表头 ---
        header_html = "<tr>"
        for i, h in enumerate(headers): 
            # 默认给一个小宽度
            width_attr = 'width="8%"' 
            
            # 根据列名或者索引来分配宽度 (这里用列名判断更稳妥，防止你删减列)
            if "序号" in h:
                width_attr = 'width="5%"'
            elif "产品" in h or "名称" in h:
                width_attr = 'width="25%"'  # 给大空间
            elif "规格" in h:
                width_attr = 'width="20%"'  # 给大空间
            elif "备注" in h:
                width_attr = 'width="15%"'  # 给中等空间
            # 剩下的 单位、数量、单价、金额 默认使用 8% 左右即可
            
            header_html += f"<th {width_attr}>{h}</th>"
        header_html += "</tr>"

        # --- 2. 生成动态内容 ---
        rows_html = ""
        for r in range(self.table.rowCount()):
            rows_html += "<tr>"
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                text = item.text() if item else ""
                # 判断是否是产品名称列（通常是第2列，索引为1）
                col_name = headers[c] if c < len(headers) else ""
                if "产品名称" in col_name or "名称" in col_name:
                    align = "left"
                else:
                    align = "center"
                rows_html += f'<td style="text-align: {align};">{text}</td>'
            rows_html += "</tr>"

        total_val = self.lbl_num_total.text().split(":")[1].strip()
        chinese_val = self.lbl_chinese_total.text().split(":")[1].strip()
        
        line_style = "border-bottom: 1px solid black; min-width: 120px; display: inline-block; text-align: center; padding-bottom: 2px;"

        # --- 3. 组装 HTML ---
        # 修改点：在所有 table 标签中显式添加 width="100%" 属性
        html = f"""
        <div class="container" style="page-break-inside: avoid; padding-bottom: 20px;">
            <h1>{self.title_edit.text()}</h1>
            
            <table class="info-table" width="100%" border="0" cellspacing="0" cellpadding="0">
                <tr>
                    <td width="50%" align="left"><strong>收货单位:</strong> {self.input_customer.text()}</td>
                    <td width="50%" align="right"><strong>日期:</strong> {self.input_date.text()}</td>
                </tr>
                <tr>
                    <td align="left"><strong>收货地址:</strong> {self.input_address.text()}</td>
                    <td align="right"><strong>联系电话:</strong> {self.input_phone.text()}</td>
                </tr>
            </table>

            <table class="main-table" width="100%" border="1" cellspacing="0" cellpadding="2">
                <thead>{header_html}</thead>
                <tbody>
                    {rows_html}
                    <tr class="total-row">
                        <td colspan="2" align="center"><strong>合计 (大写)</strong></td>
                        <td colspan="{len(headers) - 4}">{chinese_val}</td>
                        <td colspan="2" align="right"><strong>¥ {total_val}</strong></td>
                    </tr>
                </tbody>
            </table>

            <table class="footer-table" width="100%" border="0">
                <tr>
                    <td width="50%" align="center">
                        <strong>送货方(签字):</strong> 
                        <span style="{line_style}">{self.input_deliverer.text()}</span>
                    </td>
                    <td width="50%" align="center">
                        <strong>收货方(签字):</strong> 
                        <span style="{line_style}">{self.input_receiver.text()}</span>
                    </td>
                </tr>
            </table>
        </div>
        """
        return html

# --- 主窗口 (管理多个送货单) ---
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.save_dir = os.getcwd() 
        self.notes = [] # 存储所有的 SingleDeliveryNote 实例
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('多功能送货单生成器 (竖向A4版)')
        
        screen = QApplication.primaryScreen().availableGeometry()
        self.resize(int(screen.width() * 0.8), int(screen.height() * 0.9)) 
        
        font = self.font()
        font.setPointSize(14) 
        self.setFont(font)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # --- 顶部工具栏 ---
        toolbar = QHBoxLayout()
        
        btn_add = QPushButton("➕ 新增送货单")
        btn_add.setStyleSheet("background-color: #5cb85c; color: white; padding: 10px 20px; font-weight: bold; border-radius: 5px;")
        btn_add.clicked.connect(self.add_new_note)
        
        btn_export = QPushButton("🖨️ 导出全部为 PDF")
        btn_export.setStyleSheet("background-color: #0275d8; color: white; padding: 10px 20px; font-weight: bold; border-radius: 5px;")
        btn_export.clicked.connect(self.export_pdf)

        btn_path = QPushButton("📂 设置保存路径")
        btn_path.clicked.connect(self.set_save_directory)

        toolbar.addWidget(btn_add)
        toolbar.addWidget(btn_path)
        toolbar.addStretch()
        toolbar.addWidget(btn_export)
        main_layout.addLayout(toolbar)

        # --- 滚动区域 (容纳多个单据) ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setAlignment(Qt.AlignTop) # 让单据从上往下排
        self.scroll_area.setWidget(self.scroll_widget)
        
        main_layout.addWidget(self.scroll_area)
        
        # 默认添加一张
        self.add_new_note()

    def add_new_note(self):
        # 自动折叠之前的单据
        if self.notes:
            for note in self.notes:
                if not note.is_collapsed:
                    note.toggle_collapse()
        
        new_note = SingleDeliveryNote(self, len(self.notes) + 1)
        self.notes.append(new_note)
        self.scroll_layout.addWidget(new_note)

    def remove_note(self, note_widget):
        if len(self.notes) <= 1:
            QMessageBox.warning(self, "提示", "至少保留一张送货单")
            return
        
        reply = QMessageBox.question(self, "确认", "确定要删除这张送货单吗？", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.scroll_layout.removeWidget(note_widget)
            note_widget.deleteLater()
            self.notes.remove(note_widget)
            # 重排序号
            for i, note in enumerate(self.notes):
                note.lbl_id.setText(f"送货单 #{i + 1}")
                note.index = i + 1

    def set_save_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择保存文件夹", self.save_dir)
        if directory:
            self.save_dir = directory

    def export_pdf(self):
        default_name = os.path.join(self.save_dir, f"送货单汇总_{datetime.date.today()}.pdf")
        filename, _ = QFileDialog.getSaveFileName(self, "导出 PDF", default_name, "PDF Files (*.pdf)")
        if not filename: return

        # 1. 拼接 HTML
        # --- 1. 拼接 HTML ---
        full_html_body = ""
        for i, note in enumerate(self.notes):
            full_html_body += note.generate_html()
            
            # 如果不是最后一张，加一个虚线分割，而不是分页
            if i < len(self.notes) - 1:
                # 使用 table width="100%" 是在 Qt 中强制占满宽度的最可靠方法
                # border-bottom 负责画那条虚线
                full_html_body += """
                <div style="height: 30px;"></div> <table width="100%" border="0" cellspacing="0" cellpadding="0">
                    <tr>
                        <td style="border-bottom: 1px dashed #999; height: 1px;"></td>
                    </tr>
                    <tr>
     
                    </tr>
                </table>
                
                <div style="height: 30px;"></div> """

        # 2. 准备打印机和尺寸
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(filename)
        printer.setOrientation(QPrinter.Portrait)
        

        # ✅ 关键 1：启用 FullPage（否则 Qt 会强制把内容限制在可打印区域内）
        printer.setFullPage(True)

        # ✅ 关键 2：把页边距设为 0（Qt 5 推荐走 pageLayout）
        try:
            layout = printer.pageLayout()
            layout.setMargins(QMarginsF(0, 0, 0, 0))
            printer.setPageLayout(layout)
        except Exception:
            # 兼容老接口
            printer.setPageMargins(0, 0, 0, 0, QPrinter.Millimeter)
        
        # 3. 构建 CSS，注入计算出的宽度
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: "Microsoft YaHei", SimHei, sans-serif; margin: 0; padding: 0; }}
                
                .container {{ 
                    width: 100%; /* 使用计算出的精确宽度 */
                    margin: 0; 
                    padding: 0;
                }}
                
                h1 {{ 
                    text-align: center; 
                    font-size: 18pt; 
                    margin: 0; /* 移除所有margin */
                    padding: 10px 0; /* 上10px 下10px */
                    letter-spacing: 3px; 
                }}
                
                .info-table {{ width: 100%; margin-bottom: 15px; font-size: 10pt; padding: 0; }} /* 减少间距 */
                
                /* 核心修改：强制表格宽度 */
                .main-table {{ 
                    width: 100%; /* 配合 HTML 里的 width="100%" */
                    border-collapse: collapse; 
                    margin: 0; /* 移除所有margin */
                    table-layout: auto; /* 改为auto布局，让浏览器根据内容自动调整列宽 */
                }}
                
                /* 序号列保持较窄 */
                .main-table th:nth-child(1) {{ width: 5%; }}  /* 序号 */
                
                .main-table th {{ 
                    background-color: #f5f5f5; 
                    font-weight: bold; 
                    border: 1px solid black; 
                    padding: 3px; /* 减少padding */
                    font-size: 9pt; 
                    white-space: nowrap; /* 表头不换行 */
                    text-align: center; /* 表头居中 */
                }}
                
                .main-table td {{ 
                    border: 1px solid black; 
                    padding: 3px; /* 减少padding */
                    font-size: 9pt; 
                    white-space: nowrap; /* 单元格内容不换行 */
                }}
                
                .total-row {{ background-color: #fdfdfd; font-weight: bold; }}
                .footer-table {{ width: 100%; margin-top: 8px; font-size: 10pt; }}
            </style>
        </head>
        <body>
            {full_html_body}
        </body>
        </html>
        """

        doc = QTextDocument()
        
        # =========== 【关键修改】设置所有边距为0 ===========
        doc.setDocumentMargin(0) # 设置文档整体边距为0
        
        doc.setDocumentMargin(0)
        doc.setHtml(html_content)

        # ✅ 关键 4：用 paperRect（整张纸）而不是 pageRect（可打印区域）
        paper_rect = printer.paperRect(QPrinter.Point)  # 单位：Point(1/72 inch)
        doc.setPageSize(paper_rect.size())
        doc.setTextWidth(paper_rect.width())
        
        # 调整 RootFrame 边距
        root_frame = doc.rootFrame()
        frame_format = root_frame.frameFormat()
        frame_format.setMargin(0)       # 边距清零
        frame_format.setTopMargin(0)    # 顶部清零
        frame_format.setBottomMargin(0) # 底部清零
        frame_format.setLeftMargin(0)   # 左侧清零
        frame_format.setRightMargin(0)  # 右侧清零
        root_frame.setFrameFormat(frame_format)
        # =========== 【关键修改结束】 ===========
        
        doc.print_(printer)

        QMessageBox.information(self, "成功", f"PDF 已保存至:\n{filename}")
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
