import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

# =======================
# ⚙️ 请将你的数据保存为这个文件名
INPUT_FILE = 'alcohol.txt'


# =======================

def analyze_baseline(file_path):
    data_list = []

    # 1. 读取数据
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except:
        with open(file_path, 'r', encoding='gbk') as f:
            lines = f.readlines()

    print(f"📂 正在读取文件... (共 {len(lines)} 行)")

    for line in lines:
        if '收←◆' in line:
            try:
                # 提取数据
                content = line.split(']收←◆')[1].strip()
                vals = content.split(',')
                if len(vals) >= 5:
                    data_list.append({
                        'MQ3 (Alcohol)': int(vals[1]),  # 第2列
                        'MQ135 (Air)': int(vals[3])  # 第4列
                    })
            except:
                continue

    if not data_list:
        print("❌ 错误：没有提取到数据，请检查文件格式！")
        return

    df = pd.DataFrame(data_list)

    # 2. 计算基准值 (算法：取数值最小的 10% 数据的平均值)
    # 这样可以排除掉你通气时那些几千的高数值干扰
    mq3_base = df['MQ3 (Alcohol)'].nsmallest(int(len(df) * 0.1)).mean()
    mq135_base = df['MQ135 (Air)'].nsmallest(int(len(df) * 0.1)).mean()

    print("-" * 30)
    print(f"📊 科学计算出的基准值 (Bottom 10% Mean):")
    print(f"🔹 MQ-3 (酒精): {mq3_base:.2f}")
    print(f"🔹 MQ-135   : {mq135_base:.2f}")
    print("-" * 30)

    # 3. 可视化诊断
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # --- MQ3 波形图 ---
    axes[0, 0].plot(df['MQ3 (Alcohol)'], color='blue', alpha=0.6)
    axes[0, 0].axhline(y=mq3_base, color='red', linestyle='--', label=f'Baseline: {mq3_base:.0f}')
    axes[0, 0].set_title('MQ-3 Raw Waveform')
    axes[0, 0].legend()

    # --- MQ3 直方图 (查看基准分布) ---
    axes[0, 1].hist(df['MQ3 (Alcohol)'], bins=50, color='blue', alpha=0.7)
    axes[0, 1].set_title('MQ-3 Distribution (Tallest Bar = Baseline)')
    axes[0, 1].set_xlabel('ADC Value')

    # --- MQ135 波形图 ---
    axes[1, 0].plot(df['MQ135 (Air)'], color='green', alpha=0.6)
    axes[1, 0].axhline(y=mq135_base, color='red', linestyle='--', label=f'Baseline: {mq135_base:.0f}')
    axes[1, 0].set_title('MQ-135 Raw Waveform')
    axes[1, 0].legend()

    # --- MQ135 直方图 ---
    axes[1, 1].hist(df['MQ135 (Air)'], bins=50, color='green', alpha=0.7)
    axes[1, 1].set_title('MQ-135 Distribution')
    axes[1, 1].set_xlabel('ADC Value')

    plt.tight_layout()
    plt.show()


# --- 运行 ---
if __name__ == '__main__':
    if os.path.exists(INPUT_FILE):
        analyze_baseline(INPUT_FILE)
    else:
        print(f"请先将串口数据保存为 {INPUT_FILE} 并放在代码旁边！")