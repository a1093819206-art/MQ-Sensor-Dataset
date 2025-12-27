import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import re
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def parse_line(line):
    """
    解析数据行
    """
    # 匹配 [时间]...数字,数字...
    match = re.search(r'\[(.*?)\][^0-9\-]*([0-9\.\,\-]+)', line)
    if match:
        timestamp = match.group(1)
        data_str = match.group(2)
        try:
            values = [float(x) for x in data_str.split(',') if x.strip()]
            if len(values) >= 8:
                return [timestamp] + values
        except ValueError:
            return None
    return None


def process_and_relabel(file_path):
    if not os.path.exists(file_path):
        print(f"错误：找不到文件 {file_path}")
        return

    # 1. 读取文件
    raw_lines = []
    encodings = ['utf-8', 'gbk', 'gb18030', 'ansi']
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                raw_lines = f.readlines()
            if len(raw_lines) > 0:
                print(f"成功读取文件 ({enc})，共 {len(raw_lines)} 行")
                break
        except UnicodeDecodeError:
            continue

    # 2. 正则解析
    parsed_data = [parse_line(line) for line in raw_lines if parse_line(line) is not None]
    print(f"正则解析成功：提取到 {len(parsed_data)} 行原始数据")

    if len(parsed_data) == 0:
        print("警告：未提取到数据，请检查txt文件内容格式是否为 [时间]...数据...")
        return

    # 3. 定义列名
    columns = [
        'Time', 'MQ4', 'MQ3', 'MQ7', 'MQ135', 'MQ136', 'Temp', 'Hum', 'PM25', 'Label_Raw'
    ]

    df = pd.DataFrame(parsed_data)
    # 截取或补齐列
    df = df.iloc[:, :len(columns)]
    df.columns = columns[:len(df.columns)]

    # 4. 时间处理 (关键修复：不再使用 mixed)
    # 先尝试精确格式，如果失败则尝试自动推断
    try:
        df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S.%f')
    except ValueError:
        try:
            df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S')
        except ValueError:
            df['Time'] = pd.to_datetime(df['Time'], errors='coerce')

    # 删除时间解析失败的行
    df = df.dropna(subset=['Time'])
    print(f"时间格式转换后有效行数: {len(df)}")

    if len(df) == 0:
        print("错误：时间格式转换失败，所有数据均无效。请检查时间列格式。")
        return

    # 5. 数据清洗 (去除接触不良)
    # 规则: 保留 MQ4 > 200 且 PM2.5 > 50 的数据
    df_clean = df[(df['MQ4'] > 200) & (df['PM25'] > 50)].copy()

    print(f"清洗接触不良后剩余: {len(df_clean)} 行")
    print(f"已剔除异常断线数据: {len(df) - len(df_clean)} 行")

    # 6. 修改标签 (Relabeling)
    # 重置标签：MQ7 > 1000 为 1，否则为 0
    df_clean['Label'] = 0
    df_clean.loc[df_clean['MQ7'] > 1000, 'Label'] = 1

    alarm_count = df_clean['Label'].sum()
    print(f"重新打标完成：标记了 {alarm_count} 个烟雾报警点 (Label=1)")

    # 7. 绘图验证
    plt.style.use('bmh')
    fig, axes = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    # 图1: MQ-7 (显示高数值)
    ax1 = axes[0]
    ax1.plot(df_clean['Time'], df_clean['MQ7'], color='#d62728', label='MQ-7 (CO/烟雾)')
    # 标记报警点
    alarms = df_clean[df_clean['Label'] == 1]
    if not alarms.empty:
        ax1.scatter(alarms['Time'], alarms['MQ7'], color='red', s=15, label='报警区域', zorder=5)

    # 标注最大值
    max_val = df_clean['MQ7'].max()
    max_time = df_clean.loc[df_clean['MQ7'].idxmax(), 'Time']
    ax1.annotate(f'峰值: {max_val}', xy=(max_time, max_val), xytext=(max_time, max_val + 500),
                 arrowprops=dict(facecolor='black', shrink=0.05), horizontalalignment='center')

    ax1.set_title('MQ-7 传感器 (主报警源)', fontsize=14)
    ax1.set_ylabel('数值')
    ax1.legend(loc='upper right')

    # 图2: PM2.5
    ax2 = axes[1]
    ax2.plot(df_clean['Time'], df_clean['PM25'], color='#1f77b4', label='PM2.5')
    ax2.set_title('PM2.5 传感器趋势', fontsize=14)
    ax2.set_ylabel('浓度')
    ax2.legend(loc='upper right')

    # 格式化时间
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.gcf().autofmt_xdate()

    plt.tight_layout()
    plt.savefig('final_verified_plot.png', dpi=300)
    print("绘图完成: final_verified_plot.png")

    # 8. 保存文件
    output_file = 'cleaned_labeled_smoke_data.csv'
    # 只保留需要的列
    final_cols = ['Time', 'MQ4', 'MQ3', 'MQ7', 'MQ135', 'MQ136', 'Temp', 'Hum', 'PM25', 'Label']
    df_clean[final_cols].to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"最终数据已保存为: {output_file}")


if __name__ == "__main__":
    process_and_relabel('somke.txt')