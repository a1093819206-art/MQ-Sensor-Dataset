import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# 设置中文字体
import platform

if platform.system() == "Windows":
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
else:
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def show_training_process():
    # 1. 准备数据 (合并所有 CSV)
    files = {
        "Alcohol": "alcohol_data.csv",
        "MQ4": "MQ4_data.csv",
        "MQ7": "MQ7_MQ135_PM25.csv",
        "MQ136": "MQ136_data.csv",
        "Normal": "normaml_data.csv",
        "Env": "TepHum_data.csv"
    }

    dfs = []
    print("🚀 正在加载所有数据集...")

    for name, filepath in files.items():
        try:
            df = pd.read_csv(filepath)
            # 标准化列名
            cols_map = {}
            for col in df.columns:
                if col in ['PM', 'PM25', 'PM2.5']: cols_map[col] = 'PM2.5'
                if col in ['Time', 'Timestamp']: cols_map[col] = 'DROP'
            df = df.rename(columns=cols_map)
            if 'DROP' in df.columns: df = df.drop(columns=['DROP'])

            # 统一列
            df = df[['MQ4', 'MQ3', 'MQ7', 'MQ135', 'MQ136', 'Temp', 'Hum', 'PM2.5', 'Label']]

            # 打标签 (0=正常, 1=烟, 2=气, 3=酒, 4=硫)
            if name == "MQ7":
                df.loc[df['Label'] == 1, 'Label'] = 1
            elif name == "MQ4":
                df.loc[df['Label'] == 1, 'Label'] = 2
            elif name == "Alcohol":
                df.loc[df['Label'] == 1, 'Label'] = 3
            elif name == "MQ136":
                df.loc[df['Label'] == 1, 'Label'] = 4
            else:
                df['Label'] = 0

            dfs.append(df)
        except:
            pass

    # 合并
    df_final = pd.concat(dfs, ignore_index=True).dropna()

    # 2. 划分 训练集 vs 考试集
    X = df_final.drop(columns=['Label'])
    y = df_final['Label']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print(f"📊 数据准备完毕: {len(df_final)} 条样本")
    print("🔄 开始迭代训练 (模拟 AI 学习过程)...")
    print("-" * 50)
    print(f"{'轮次':<6} | {'树的数量':<8} | {'训练集准确率':<12} | {'测试集准确率':<12}")
    print("-" * 50)

    # 3. 迭代训练 (warm_start=True 允许增量训练)
    rf = RandomForestClassifier(n_estimators=1, warm_start=True, random_state=42, n_jobs=-1)

    history = {'train': [], 'test': [], 'trees': []}

    # 模拟 50 轮训练
    for i in range(1, 51):
        rf.n_estimators = i  # 每次增加一棵树
        rf.fit(X_train, y_train)

        # 记录成绩
        train_acc = rf.score(X_train, y_train)
        test_acc = rf.score(X_test, y_test)

        history['train'].append(train_acc)
        history['test'].append(test_acc)
        history['trees'].append(i)

        if i % 5 == 0 or i == 1:
            print(f"Epoch {i:<2} | {i:<10} | {train_acc:.4f}       | {test_acc:.4f}")

    # 4. 绘制训练过程图
    plt.figure(figsize=(10, 6))
    plt.plot(history['trees'], history['train'], label='学习成绩 (训练集)', linestyle='--', color='blue', alpha=0.6)
    plt.plot(history['trees'], history['test'], label='考试成绩 (测试集)', linewidth=3, color='red')

    plt.xlabel('模型复杂度 (决策树数量)')
    plt.ylabel('准确率 (Accuracy)')
    plt.title('AI 模型训练过程监控曲线')
    plt.legend(loc='lower right')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('training_process.png')

    print("-" * 50)
    print("✅ 训练演示完成！")
    print("📈 过程图表已保存为: training_process.png")
    # plt.show()


if __name__ == "__main__":
    show_training_process()