# Personal Finance Data Pipeline (个人财务数据流水线)

基于 Python 开发的个人账单自动化处理与分析工具。支持一键提取、清洗并合并支付宝与微信支付导出的账单明细，最终输出标准化的数据透视表和可视化分析图表。

## 🌟 核心功能 (Features)

- **双引擎解析**: 自动识别 `.csv` (纯文本) 与 `.xlsx` (Excel 二进制) 格式的账单。
- **智能去噪**: 自动跳过微信/支付宝官方账单头部的非结构化统计说明文字。
- **自动清洗**: 过滤“已退款”、“已关闭”以及“内部转账”等干扰数据，还原真实消费流水。
- **动态可视化**: 结合 `matplotlib` 一键生成月度支出结构饼图与柱状图。
- **隐私隔离**: 采用 `.gitignore` 严格屏蔽真实交易数据上传，保障个人隐私安全。

## 📁 目录结构 (Directory Structure)

```text
Bill_Processing/
├── data/               # 存放原始账单 (alipay.csv / wechat.xlsx) - 被 Git 忽略
├── output/             # 存放自动清洗后的标准化账单及可视化结果 - 被 Git 忽略
├── src/
│   ├── process.py      # 数据 ETL 清洗脚本
│   └── analyze.py      # 数据可视化分析脚本
├── requirements.txt    # Python 依赖清单
└── .gitignore          # 隐私保护配置