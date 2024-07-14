import pandas as pd
import numpy as np

# 加载上传的CSV文件
file_path = "data_V64-PTW10211.csv"
data = pd.read_csv(file_path)

# 假设 l 的值（前后轴之间的距离）
l = 2.741  # 假设为 2.741 米


# 定义函数来计算所需的各列
def calculate_yaw_rate(group):
    group = group.copy()  # 避免修改原始组
    group['time_diff'] = group['timestamp_ms'].diff() / 1000.0  # 将毫秒转换为秒
    group['yaw_diff'] = group['yaw_rad'].diff()
    group['yaw_rate'] = group['yaw_diff'] / group['time_diff']
    group['rM'] = np.abs(group['v_lon'] / group['yaw_rate'])
    group['tan_A'] = l / group['rM']
    group['A'] = np.arctan(group['tan_A'])
    group['A_diff'] = group['A'].diff()
    group['A rate'] = group['A_diff'] / group['time_diff']

    # 计算角速度的变化率，即角加速度
    group['A_velocity'] = group['A_diff'] / group['time_diff']
    group['A_velocity_diff'] = group['A_velocity'].diff()
    group['A_acceleration'] = group['A_velocity_diff'] / group['time_diff']

    return group


# 按照车辆ID分组并应用计算函数
grouped_data = data.groupby('track_id', group_keys=False).apply(lambda x: calculate_yaw_rate(x)).reset_index(drop=True)

# 删除临时计算列以获得干净的数据
cleaned_data = grouped_data.drop(
    columns=['time_diff', 'yaw_diff', 'yaw_rate', 'A_diff', 'rM', 'A', 'tan_A', 'A_velocity_diff'])

# 保留车辆轨迹的id在表格中
output_file_path = "A角加速度.csv"
cleaned_data.to_csv(output_file_path, index=False)

# 检查清理后的数据
print(cleaned_data.head())

# 确认文件保存成功
print(f"文件已保存到 {output_file_path}")
