import pandas as pd

# 加载上传的CSV文件
file_path = r"D:\Desktop\SITP\车辆sitp\Xi'an\tmp\data_V64-PTW10211.csv"
data = pd.read_csv(file_path)

# 计算时间差（以秒为单位）
time_diff = data['timestamp_ms'].diff() / 1000.0

# 计算yaw_rad的角速度
yaw_rate = data['yaw_rad'].diff() / time_diff

# 计算yaw_rad的角加速度
yaw_acceleration = yaw_rate.diff() / time_diff

# 将yaw_rad加速度添加到数据框中
data['yaw_accel'] = yaw_acceleration

# 保存更新后的数据框到一个新的CSV文件
output_file_path = '偏航率.csv'
data.to_csv(output_file_path, index=False)

# 显示输出文件路径
print(f'更新后的文件已保存到: {output_file_path}')
