import pandas as pd
import numpy as np

# 加载提供的CSV文件
file_path = "D:\\Desktop\\SITP\\车辆sitp\\Xi'an\\Veh_smoothed_tracks_RawId.csv"
data = pd.read_csv(file_path)

# 获取每个 track_id 的前五帧和最后一帧
grouped = data.groupby('track_id')
first_five_frames = grouped.head(5).copy()  # 前五帧
last_frame = grouped.tail(1).copy()  # 最后一帧

# 计算前五帧中每两帧之间的方向向量 l
first_five_frames['dx'] = first_five_frames.groupby('track_id')['x'].diff().fillna(0)
first_five_frames['dy'] = first_five_frames.groupby('track_id')['y'].diff().fillna(0)

# 计算每个 track_id 的平均方向向量
mean_direction = first_five_frames.groupby('track_id').agg({'dx': 'mean', 'dy': 'mean'}).reset_index()
mean_direction.rename(columns={'dx': 'dx_l', 'dy': 'dy_l'}, inplace=True)

# 获取第一帧和最后一帧的坐标
first_frame = grouped.head(1).copy()  # 第一帧
last_frame = grouped.tail(1).copy()  # 最后一帧

# 计算第一帧与最后一帧之间的向量 v
merged_frames = first_frame.merge(last_frame, on='track_id', suffixes=('_first', '_last'))
merged_frames['dx_v'] = merged_frames['x_last'] - merged_frames['x_first']
merged_frames['dy_v'] = merged_frames['y_last'] - merged_frames['y_first']

# 合并前五帧计算的方向向量 l
merged_frames = merged_frames.merge(mean_direction, on='track_id')

# 计算向量 l 和 v 之间的夹角
def calculate_angle(dx1, dy1, dx2, dy2):
    dot_product = dx1 * dx2 + dy1 * dy2  # 点积
    magnitude1 = np.sqrt(dx1**2 + dy1**2)  # 向量1的模
    magnitude2 = np.sqrt(dx2**2 + dy2**2)  # 向量2的模
    cos_angle = dot_product / (magnitude1 * magnitude2)  # 余弦值
    angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))  # 使用 np.clip 确保值在 [-1, 1] 之间，计算弧度
    return np.degrees(angle)  # 返回角度值

# 计算每个轨迹的夹角
merged_frames['angle'] = merged_frames.apply(lambda row: calculate_angle(row['dx_l'], row['dy_l'], row['dx_v'], row['dy_v']), axis=1)

# 定义一个函数来标记总体方向
def label_overall_direction(angle):
    if  90 > angle > 30:
        return 'left'  # 左转
    elif - 90 < angle < -30:
        return 'right'  # 右转
    else:
        return 'straight'  # 直行

# 根据夹角标记每个轨迹
merged_frames['trajectory'] = merged_frames['angle'].apply(label_overall_direction)

# 将标签合并回原始数据
data = data.merge(merged_frames[['track_id', 'trajectory']], on='track_id', how='left')

# 将标记后的数据保存到一个新的CSV文件
output_file_path = '转向1.csv'
data.to_csv(output_file_path, index=False)
