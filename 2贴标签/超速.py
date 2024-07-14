import pandas as pd
import numpy as np

# 加载数据
file_path = "D:\\Desktop\\SITP\\车辆sitp\\Xi'an\\Veh_smoothed_tracks_RawId.csv"
data = pd.read_csv(file_path)

# 使用速度分量计算速度
data['speed'] = np.sqrt(data['vx']**2 + data['vy']**2)

# 设置限速
speed_limit = 6.94

# 添加一列新列指示车辆是否超速，超速为"S"，未超速为"N"
data['overspeed'] = np.where(data['speed'] > speed_limit, 'S', 'N')

# 保存更新后的数据框到新的CSV文件
output_file_path = "D:\\Desktop\\SITP\\车辆sitp\\Xi'an\\超速.csv"
data.to_csv(output_file_path, index=False)

print(f"更新后的CSV文件已保存至: {output_file_path}")
