import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

# 1. 环境配置 (Environment Configuration)
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']  # 优先尝试微软雅黑，其次黑体
plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号


def analyze_and_plot(file_path):
    print("正在读取并分析数据...")

    try:
        df = pd.read_excel(file_path)
    except FileNotFoundError:
        print(f"错误：找不到文件 {file_path}。请确认 process.py 是否已成功运行并生成了文件。")
        return

    # 2. 数据过滤 (Data Filtering)
    df_expense = df[df['收支类型'] == '支出']

    # 3. 数据聚合 (Data Aggregation)
    expense_summary = df_expense.groupby('一级分类')['金额'].sum().sort_values(ascending=False)

    if expense_summary.empty:
        print("没有找到任何支出数据，无法生成图表。")
        return

    # 4. 数据可视化 (Data Visualization)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    # 左图：柱状图
    bars = ax1.bar(expense_summary.index, expense_summary.values, color='steelblue')
    ax1.set_title('本月 各项总支出明细')
    ax1.set_ylabel('金额 (RMB)')
    ax1.tick_params(axis='x', rotation=45)

    for bar in bars:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2, yval + 5, round(yval, 2), ha='center', va='bottom')

    # 右图：饼图
    ax2.pie(expense_summary.values, labels=expense_summary.index, autopct='%1.1f%%', startangle=140,
            colors=plt.cm.Pastel1.colors)
    ax2.set_title('本月 支出结构占比')

    plt.tight_layout()
    print("图表渲染完成，正在展示弹出窗口...")
    plt.show()


# ==========================================
# 核心执行区 (Execution Entry Point)
# ==========================================
if __name__ == '__main__':
    # 动态获取项目根目录和 output 文件夹路径
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

    # 自动获取当前运行的时间（年月），去 output 文件夹里找对应的账本
    current_time = datetime.now()
    target_filename = f"{current_time.strftime('%Y_%m')}_processed_all.xlsx"
    target_path = os.path.join(OUTPUT_DIR, target_filename)

    analyze_and_plot(target_path)