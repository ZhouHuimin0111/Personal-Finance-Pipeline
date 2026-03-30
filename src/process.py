import pandas as pd
import os
from datetime import datetime

# ==========================================
# 动态路径与时间配置 (Dynamic Configuration)
# ==========================================
# 自动获取 src 文件夹的上一级目录作为项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

# 获取当前年月，用于动态命名 (例如：2026_03)
current_time = datetime.now()
output_filename = f"{current_time.strftime('%Y_%m')}_processed_all.xlsx"
output_path = os.path.join(OUTPUT_DIR, output_filename)


def process_bill(file_name, platform):
    file_path = os.path.join(DATA_DIR, file_name)
    if not os.path.exists(file_path):
        print(f"未找到文件: {file_path}，跳过该平台。")
        return None

    df = None

    # 根据文件后缀自动切换解析引擎
    if file_name.endswith('.xlsx'):
        try:
            temp_df = pd.read_excel(file_path, header=None)
            skip_rows = 0
            for i in range(len(temp_df)):
                if any('交易时间' in str(cell) for cell in temp_df.iloc[i]):
                    skip_rows = i
                    break

            df = pd.read_excel(file_path, skiprows=skip_rows)
            df.columns = df.columns.astype(str).str.strip()
            print(f"[{platform}] 成功调用 Excel 引擎读取，自动跳过 {skip_rows} 行废话。")
        except Exception as e:
            print(f"[{platform}] Excel 读取失败: {e}")
            return None

    elif file_name.endswith('.csv'):
        encodings_to_try = ['gbk', 'utf-8', 'utf-8-sig', 'gb18030']
        for enc in encodings_to_try:
            try:
                skip_rows = 0
                with open(file_path, 'r', encoding=enc, errors='ignore') as f:
                    for i, line in enumerate(f):
                        if '交易时间' in line:
                            skip_rows = i
                            break

                df = pd.read_csv(file_path, encoding=enc, skiprows=skip_rows, engine='python', on_bad_lines='skip')
                df.columns = df.columns.astype(str).str.strip()
                if '交易时间' in df.columns:
                    print(f"[{platform}] 成功调用 CSV 引擎解析！使用 {enc} 编码，跳过 {skip_rows} 行废话。")
                    break
                else:
                    df = None
            except Exception:
                continue

    if df is None or df.empty:
        print(f"[{platform}] 读取彻底失败，未能提取到有效数据。")
        return None

    # 统一的数据清洗与字段映射逻辑
    new_columns = ['日期', '收支类型', '一级分类', '二级分类', '金额', '备注']
    df_new = pd.DataFrame(columns=new_columns)

    if platform == 'alipay':
        if '交易状态' in df.columns:
            df = df[~df['交易状态'].str.contains('退款|关闭', na=False)]
        if '收/支' in df.columns:
            df = df[~df['收/支'].str.contains('不计收支', na=False)]

        df_new['日期'] = pd.to_datetime(df['交易时间']).dt.strftime('%Y/%m/%d')
        df_new['收支类型'] = df['收/支']
        df_new['金额'] = df['金额']
        df_new['备注'] = df['交易对方'].astype(str) + " - " + df['商品说明'].astype(str)

    elif platform == 'wechat':
        if '当前状态' in df.columns:
            df = df[~df['当前状态'].str.contains('退款', na=False)]
        if '收/支' in df.columns:
            df = df[~df['收/支'].str.contains('/', na=False)]

        df_new['日期'] = pd.to_datetime(df['交易时间']).dt.strftime('%Y/%m/%d')
        df_new['收支类型'] = df['收/支']

        amount_col = '金额(元)' if '金额(元)' in df.columns else '金额'
        df_new['金额'] = df[amount_col].astype(str).str.replace('¥', '').str.strip().astype(float)

        note_col = '商品' if '商品' in df.columns else '商品说明'
        df_new['备注'] = df['交易对方'].astype(str) + " - " + df[note_col].astype(str)

    df_new['一级分类'] = '待分类'
    df_new['二级分类'] = '待分类'

    return df_new


# ==========================================
# 核心执行区
# ==========================================
if __name__ == '__main__':
    df_list = []
    print("开始处理账单...")

    # 注意这里只传文件名，程序会自动去 data 文件夹找
    alipay_df = process_bill('alipay.csv', 'alipay')
    if alipay_df is not None:
        df_list.append(alipay_df)

    wechat_df = process_bill('wechat.xlsx', 'wechat')
    if wechat_df is not None:
        df_list.append(wechat_df)

    if df_list:
        final_df = pd.concat(df_list, ignore_index=True)
        final_df = final_df.sort_values(by='日期')

        try:
            final_df.to_excel(output_path, index=False)
            print(f"\n✅ 双平台账单处理并合并完成！已导出至: {output_path}")
        except PermissionError:
            print(f"\n❌ 导出失败：请检查 '{output_filename}' 是否正被 Excel 占用打开，关闭后重试！")
    else:
        print("\n⚠️ 没有成功处理任何账单数据。")