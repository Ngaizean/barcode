# 生产线工具集

> 工业界生产管理实用工具集合

## 项目简介

这是一套专为工业界生产线设计的实用工具集，包含条形码生成、送货单管理等生产环节常用功能。项目采用模块化设计，界面简洁易用，适合制造业、仓储物流、零售等场景使用。

## 🛠️ 包含工具

### 1. 条形码生成器 (Barcode Generator)

**功能特性**
- ✅ EAN-13 标准条形码生成
- ✅ 批量生成和管理
- ✅ 实时预览
- ✅ 自动计算校验位
- ✅ PDF 批量导出（A4纸张，7列×16行布局）
- ✅ 自定义款号、数量、颜色等信息
- ✅ 根据文本长度自动调整尺寸

**适用场景**
- 商品标签打印
- 库存管理标签
- 产品包装标识
- 仓储物流标签

**快速启动**
```bash
python run_barcode.py
```

### 2. 送货单管理器 (Shipment Manager)

**功能特性**
- ✅ 创建和管理多个送货单
- ✅ 表格数据编辑
- ✅ 自动计算总金额
- ✅ 折叠/展开单据视图
- ✅ 支持打印预览和打印
- ✅ 客户信息管理
- ✅ 日期自动记录

**适用场景**
- 生产订单管理
- 发货单据生成
- 物流配送管理
- 客户交付记录

**快速启动**
```bash
python run_shipment.py
```

## 📦 项目结构

```
production-tools/
├── README.md                  # 项目说明
├── LICENSE                    # BSD 许可证
├── requirements.txt           # 依赖列表
├── run_barcode.py            # 条形码生成器启动脚本
├── run_shipment.py           # 送货单管理器启动脚本
├── assets/                   # 资源文件
│   ├── app.ico              # 应用图标
│   ├── app.svg              # SVG 图标
│   └── splash.png           # 启动画面
├── src/                      # 源代码
│   ├── barcode_generator/    # 条形码生成器
│   │   ├── __init__.py
│   │   ├── main.py           # 主程序
│   │   └── BarcodeItem.py    # 条形码条目组件
│   └── shipment_manager/     # 送货单管理器
│       ├── __init__.py
│       └── main.py           # 主程序
├── Encoder/                  # EAN-13 编码器模块
│   ├── __init__.py          # EAN13Encoder 类
│   ├── encoding.py          # 编码表和函数
│   └── renderer.py          # 条形码渲染器
└── docs/                     # 文档
    └── ARCHITECTURE.md       # 架构文档
```

## 🚀 快速开始

### 环境要求

- Python 3.7+
- 操作系统：Windows / macOS / Linux

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/Ngaizean/barcode.git
cd barcode
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **运行工具**

启动条形码生成器：
```bash
python run_barcode.py
```

启动送货单管理器：
```bash
python run_shipment.py
```

## 📖 使用指南

### 条形码生成器

#### 步骤1：添加条目
- 输入款号（商品编码，12或13位数字）
- 设置生产数量
- （可选）输入颜色或规格信息
- 条形码自动生成并实时预览

#### 步骤2：批量管理
- 点击"添加条目"增加更多条目
- 点击条目进行选中（支持多选）
- 点击"删除选中"移除不需要的条目
- 点击"一键清空"清除所有条目

#### 步骤3：导出打印
- 点击"导出PDF"按钮
- 选择保存位置
- 条形码将按A4纸张格式导出（7列×16行）
- 使用 PDF 阅读器或直接打印

### 送货单管理器

#### 步骤1：创建送货单
- 点击"添加送货单"
- 填写客户信息（公司名称、地址等）
- 设置送货日期
- 添加商品明细

#### 步骤2：编辑明细
- 双击表格单元格进行编辑
- 添加/删除行
- 输入商品名称、数量、单价
- 系统自动计算总金额

#### 步骤3：打印
- 点击"打印送货单"按钮
- 预览并打印

## 🔧 技术架构

### 技术栈
- **GUI框架**: PyQt5
- **条形码生成**: Python EAN-13 Encoder
- **PDF生成**: reportlab
- **图像处理**: Pillow (PIL)

### 核心模块

#### EAN-13 编码器 (Encoder/)
- 完整的 EAN-13 编码算法实现
- 自动校验位计算（Modulo-10）
- 高质量条形码渲染
- 支持自定义尺寸和样式

#### 条形码生成器 (src/barcode_generator/)
- 批量条目管理
- PDF 批量导出
- A4 纸张自动排版
- 实时预览功能

#### 送货单管理器 (src/shipment_manager/)
- 多单据管理
- 表格数据编辑
- 自动计算功能
- 打印预览

## 📋 配置说明

### 条形码尺寸配置

在 `src/barcode_generator/main.py` 中可以修改：

```python
barcode_width = 90      # 条形码宽度（点）
barcode_height = 45     # 条形码高度（点）
barcodes_per_row = 7    # 每行条形码数量
margin_x = 10          # 左右边距
margin_y = 32          # 上下边距
```

### 送货单配置

在 `src/shipment_manager/main.py` 中可以自定义：
- 默认客户信息
- 表格列配置
- 打印样式
- 单据格式

## 🎯 适用行业

- **制造业**: 产品标签、生产订单
- **仓储物流**: 库存标签、发货单据
- **零售业**: 商品标签、配送单
- **批发贸易**: 批次管理、送货单据
- **电商**: 订单标签、物流单据

## 📚 EAN-13 条形码说明

### 编码格式
EAN-13 由 13 位数字组成：
- 前 2-3 位：国家/地区代码
- 中间 4-5 位：制造商代码
- 后 5 位：产品代码
- 最后 1 位：校验位（自动计算）

### 校验位计算
采用 Modulo-10 算法，系统自动计算并验证。

详细文档请参考：[EAN-13 技术规范](http://www.barcodeisland.com/ean13.phtml)

## 🔍 常见问题

**Q: 条形码无法扫描？**
A: 请确保输入的是 12 或 13 位纯数字，系统会自动计算校验位。

**Q: 如何调整导出的 PDF 布局？**
A: 修改 `src/barcode_generator/main.py` 中的 `barcodes_per_row` 参数。

**Q: 支持哪些条形码格式？**
A: 目前支持 EAN-13，未来计划添加 Code128、QR Code 等格式。

**Q: 送货单可以保存为模板吗？**
A: 可以在创建送货单后，使用"另存为"功能保存模板。

## 🛠️ 开发说明

### 添加新工具

在 `src/` 下创建新目录，并添加对应的启动脚本：

```bash
src/
└── your_tool/
    ├── __init__.py
    └── main.py
```

创建启动脚本 `run_your_tool.py`：

```python
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.your_tool.main import YourTool

def main():
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = YourTool()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
```

### 代码规范
- 遵循 PEP 8 规范
- 使用类型注解
- 添加文档字符串
- 保持代码简洁清晰

## 📈 更新日志

### v1.0.0 (2024)
- ✨ 初始版本发布
- ✅ 条形码生成器
- ✅ 送货单管理器
- ✅ PDF 导出功能
- ✅ EAN-13 编码器

## 📄 许可证

本项目采用 BSD 许可证。详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系方式

- **GitHub**: [@Ngaizean](https://github.com/Ngaizean)
- **Issues**: https://github.com/Ngaizean/barcode/issues

---

**提高生产效率，从使用合适工具开始！** 🏭
