import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

# 设置字体以支持中文显示 (根据你的系统自动选择)
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


def visualize_sensor_data(file_path):
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"错误: 找不到文件 {file_path}")
            return

        # 1. 读取数据
        df = pd.read_csv(file_path)

        # 2. 处理时间列 (修正部分)
        # 方法 A: 不指定 format，让 pandas 自动解析 (兼容性最好)
        # 方法 B: 指定精确格式 '%H:%M:%S.%f'
        try:
            df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S.%f')
        except ValueError:
            # 如果上面失败（比如有的时间没有微秒），尝试自动推断
            print("尝试自动推断时间格式...")
            df['Time'] = pd.to_datetime(df['Time'])

        # 3. 设置绘图画布 (3行1列)
        plt.style.use('bmh')
        fig, axes = plt.subplots(3, 1, figsize=(12, 12), sharex=True)

        # --- 子图 1: PM2.5 浓度与报警事件 ---
        ax1 = axes[0]
        ax1.plot(df['Time'], df['PM25'], label='PM2.5 浓度', color='#1f77b4', linewidth=1.5)

        # 将 Label=1 (烟雾/异常) 的点用红色散点标记出来
        if 'Label' in df.columns:
            anomalies = df[df['Label'] == 1]
            if not anomalies.empty:
                ax1.scatter(anomalies['Time'], anomalies['PM25'], color='red', label='烟雾报警', s=25, zorder=5)

        ax1.set_title('PM2.5 浓度与报警检测', fontsize=14)
        ax1.set_ylabel('PM2.5 数值')
        ax1.legend(loc='upper right')
        ax1.grid(True, linestyle='--', alpha=0.7)

        # --- 子图 2: 气体传感器 (MQ-7 / MQ-135) ---
        ax2 = axes[1]
        ax2.plot(df['Time'], df['MQ_A'], label='MQ_A (如 MQ-7)', color='green', alpha=0.8)
        ax2.plot(df['Time'], df['MQ_B'], label='MQ_B (如 MQ-135)', color='#ff7f0e', alpha=0.8)

        ax2.set_title('气体传感器趋势', fontsize=14)
        ax2.set_ylabel('传感器读数')
        ax2.legend(loc='upper right')
        ax2.grid(True, linestyle='--', alpha=0.7)

        # --- 子图 3: 环境温湿度 (双Y轴) ---
        ax3 = axes[2]
        color_temp = 'tab:red'
        ax3.set_xlabel('时间', fontsize=12)
        ax3.set_ylabel('温度 (°C)', color=color_temp, fontsize=12)
        ax3.plot(df['Time'], df['Temp'], color=color_temp, label='温度')
        ax3.tick_params(axis='y', labelcolor=color_temp)

        # 创建共享X轴的第二个Y轴用于显示湿度
        ax4 = ax3.twinx()
        color_hum = 'tab:blue'
        ax4.set_ylabel('湿度 (%)', color=color_hum, fontsize=12)
        ax4.plot(df['Time'], df['Hum'], color=color_hum, linestyle='--', label='湿度')
        ax4.tick_params(axis='y', labelcolor=color_hum)

        ax3.set_title('环境温湿度', fontsize=14)

        # 4. 格式化 X 轴时间显示
        formatter = mdates.DateFormatter('%H:%M:%S')
        ax3.xaxis.set_major_formatter(formatter)
        plt.gcf().autofmt_xdate()

        # 5. 保存和显示
        plt.tight_layout()
        output_file = 'sensor_data_visualization.png'
        plt.savefig(output_file, dpi=300)
        print(f"绘图完成！图片已保存为 {output_file}")
        plt.show()

    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()


# --- 运行主程序 ---
if __name__ == "__main__":
    # 确保文件名和你本地生成的csv文件名一致
    csv_file = 'MQ7_PM25_data.csv'
    visualize_sensor_data(csv_file)