# EAN-13 条形码生成器

> 基于 PyQt5 的 EAN-13 条形码生成与批量打印工具

## 项目简介

这是一个功能完善的 EAN-13 条形码生成器桌面应用程序，支持批量生成、预览和导出条形码到 PDF 文件。项目采用 Python + PyQt5 开发，界面简洁友好，适合商品标签、库存管理等场景使用。

## 主要功能

### 条形码生成
- ✅ 支持 EAN-13 标准条形码生成
- ✅ 实时预览条形码效果
- ✅ 自动计算校验位
- ✅ 支持款号/数量/颜色等自定义信息
- ✅ 根据文本长度自动调整条形码尺寸

### 批量管理
- ✅ 支持添加多个条目
- ✅ 批量删除和清空功能
- ✅ 多选条目操作
- ✅ 自动编号管理

### 导出功能
- ✅ 导出为 PDF 文件（A4纸张）
- ✅ 自动排版布局（每行7个，共16行）
- ✅ 支持打印预览

### 送货单功能
- ✅ 创建和管理多个送货单
- ✅ 表格数据编辑
- ✅ 自动计算总金额
- ✅ 折叠/展开单据视图
- ✅ 打印功能

## 技术栈

- **GUI框架**: PyQt5
- **条形码生成**: barcode, reportlab
- **图像处理**: Pillow (PIL)
- **PDF处理**: reportlab, pdf2image
- **编码器**: 自研 EAN-13 编码器

## 项目结构

```
barcode/
├── main.py                 # 主程序入口（条形码生成器）
├── BarcodeItem.py          # 条形码条目组件
├── Shipment.py             # 送货单功能模块
├── Encoder/                # EAN-13 编码器模块
│   ├── __init__.py        # 模块初始化和EAN13Encoder类
│   ├── encoding.py        # 编码表和函数
│   └── renderer.py        # 条形码渲染器
├── app.ico                # 应用图标
├── app.svg                # SVG图标
├── splash.png             # 启动画面
├── requirements.txt       # 依赖列表
└── README.md             # 项目说明
```

## 安装部署

### 环境要求

- Python 3.7+
- 操作系统：Windows / macOS / Linux

### 安装步骤

1. 克隆项目
```bash
git clone https://github.com/Ngaizean/barcode.git
cd barcode
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行程序
```bash
python main.py
```

## 使用说明

### 条形码生成器

1. **添加条目**
   - 输入款号（商品编码）
   - 设置数量
   - （可选）输入颜色信息
   - 条形码会自动生成并预览

2. **批量操作**
   - 点击"添加条目"增加更多条目
   - 点击条目进行选中（可多选）
   - 点击"删除选中"移除不需要的条目
   - 点击"一键清空"清除所有条目

3. **导出PDF**
   - 点击"导出PDF"按钮
   - 选择保存位置
   - 条形码将按A4纸张格式导出（7列×16行）

### 送货单功能

1. **创建送货单**
   - 点击"添加送货单"
   - 填写客户信息、地址、日期等
   - 添加商品明细

2. **编辑表格**
   - 双击表格单元格进行编辑
   - 添加/删除行
   - 系统自动计算总金额

3. **打印**
   - 点击"打印送货单"按钮
   - 预览并打印

## EAN-13 编码说明

### 编码格式

EAN-13 条形码由13位数字组成：
- 前2-3位：国家/地区代码
- 中间4-5位：制造商代码
- 后5位：产品代码
- 最后1位：校验位（自动计算）

### 编码原理

项目实现了完整的 EAN-13 编码算法：
1. **校验位计算**：使用 Modulo-10 算法
2. **奇偶校验**：根据首位数字确定后续数字的编码方式
3. **二进制编码**：将数字转换为7位二进制条形码
4. **保护条**：添加起始、中间和结束保护模式

详细文档请参考：[EAN-13 技术规范](http://www.barcodeisland.com/ean13.phtml)

## 开发说明

### 核心类说明

#### `EAN13Encoder` (Encoder/__init__.py)
EAN-13编码器核心类，负责：
- 验证输入码（12或13位数字）
- 计算校验位
- 生成左右两侧编码
- 输出条形码图像

#### `BarcodeItem` (BarcodeItem.py)
条形码条目组件，实现：
- 用户界面布局
- 输入字段管理
- 实时条形码预览
- 选中状态处理

#### `BarcodeGenerator` (main.py)
主窗口类，管理：
- 多个条目的添加/删除
- PDF导出功能
- 启动画面

#### `SingleDeliveryNote` (Shipment.py)
送货单组件，包含：
- 表格数据管理
- 自动计算功能
- 打印功能

### 自定义配置

在 `main.py` 中可以修改以下参数：

```python
# 条形码尺寸
barcode_width = 90      # 宽度（点）
barcode_height = 45     # 高度（点）

# 页面布局
barcodes_per_row = 7    # 每行条形码数量
max_items_per_page = 112  # 每页最大条目数（7×16）

# 边距设置
margin_x = 10          # 左右边距
margin_y = 32          # 上下边距
```

## 常见问题

**Q: 生成的条形码无法扫描？**
A: 请确保输入的是12位或13位纯数字。系统会自动计算并添加校验位。

**Q: 如何调整条形码大小？**
A: 可以修改 `main.py` 中的 `barcode_width` 和 `barcode_height` 参数。

**Q: 导出的PDF排版不合适？**
A: 调整 `barcodes_per_row` 参数可以改变每行的条形码数量。

**Q: 支持哪些条形码格式？**
A: 目前仅支持 EAN-13 格式。未来计划添加 Code128、QR Code 等格式。

## 依赖说明

主要依赖库：
- `PyQt5` - GUI框架
- `reportlab` - PDF生成
- `Pillow` - 图像处理
- `barcode` - 条形码生成
- `pdf2image` - PDF转换

完整列表见 `requirements.txt`。

## 更新日志

### v1.0.0 (2024)
- ✨ 初始版本发布
- ✅ EAN-13 条形码生成
- ✅ PDF批量导出
- ✅ 送货单功能
- ✅ 多选和批量操作

## 许可证

本项目采用 BSD 许可证。详见 LICENSE 文件。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请通过以下方式联系：
- GitHub Issues: https://github.com/Ngaizean/barcode/issues

---

**Happy Coding!** 🚀
