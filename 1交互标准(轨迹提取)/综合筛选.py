import pandas as pd
import numpy as np
from tqdm import tqdm
import os

# 网格搜索的初始阈值
YAW_ACCELERATE_THRESHOLDS = [0.1, 0.3, 0.5]  # Yaw加速度阈值
PET_THRESHOLDS = [4, 6, 8]  # PET阈值
MIN_DISTANCE_THRESHOLDS = [0.5, 1, 1.5,2]  # 最小距离阈值

def calculate_distances(group1, group2):
    """
    计算两组轨迹点之间的距离矩阵和相同时间的最小距离。
    :param group1: DataFrame, 第一组车辆轨迹数据
    :param group2: DataFrame, 第二组车辆轨迹数据
    :return: tuple, (np.array, float), 距离矩阵和相同时间的最小距离
    """
    distances = np.linalg.norm(group1[['x', 'y']].values[:, None, :] - group2[['x', 'y']].values[None, :, :], axis=2)
    merged = pd.merge(group1, group2, on='timestamp_ms', suffixes=('_1', '_2'))
    merged['distance'] = np.linalg.norm(merged[['x_1', 'y_1']].values - merged[['x_2', 'y_2']].values, axis=1)
    same_time_min_distance = merged['distance'].min()
    return distances, same_time_min_distance

def PET_Calculate(group1, group2):
    """
    计算两组轨迹之间的潜在交通冲突时间（PET）。
    :param group1: DataFrame, 第一组车辆轨迹数据
    :param group2: DataFrame, 第二组车辆轨迹数据
    :return: tuple, (float, float), PET时间和相同时间的最小距离，-1代表没有任何冲突
    """
    distances, same_time_min_distance = calculate_distances(group1, group2)
    min_distance = np.min(distances)

    if min_distance > 0.5:
        return -1, np.nan

    min_idx = np.unravel_index(np.argmin(distances, axis=None), distances.shape)
    PET = abs(group2.iloc[min_idx[1]]['timestamp_ms'] - group1.iloc[min_idx[0]]['timestamp_ms']) / 1000

    return PET, same_time_min_distance

def calculate_yaw_accelerate(data, yaw_accelerate_threshold):
    """
    计算yaw加速度并根据阈值过滤数据。
    :param data: DataFrame, 包含轨迹数据
    :param yaw_accelerate_threshold: float, yaw加速度的阈值
    :return: DataFrame, 过滤后的数据
    """
    time_diff = data['timestamp_ms'].diff() / 1000.0
    yaw_rate = data['yaw_rad'].diff() / time_diff
    yaw_accelerate = yaw_rate.diff() / time_diff
    data['yaw_accel'] = yaw_accelerate
    filtered_data = data[abs(yaw_accelerate) > yaw_accelerate_threshold]
    return filtered_data

def write2csv(group1, group2, output_dir):
    """
    将结果写入CSV文件。
    :param group1: DataFrame, 第一组车辆轨迹数据
    :param group2: DataFrame, 第二组车辆轨迹数据
    :param output_dir: str, 输出文件夹名
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_filename = os.path.join(output_dir, 'trajectory_data.csv')
    with open(output_filename, 'a', newline="", encoding='utf-8') as f:
        group1.to_csv(f, index=False, header=False)
        group2.to_csv(f, index=False, header=False)

def process_trajectories(df, yaw_accelerate_threshold, pet_threshold, min_distance_threshold):
    """
    处理轨迹数据并应用网格搜索的阈值。
    :param df: DataFrame, 包含所有轨迹数据
    :param yaw_accelerate_threshold: float, yaw加速度的阈值
    :param pet_threshold: float, PET的阈值
    :param min_distance_threshold: float, 最小距离的阈值
    """
    grouped = df.groupby('track_id')
    trajectories = {name: group for name, group in grouped}

    ptw_ids = [id for id in trajectories if trajectories[id]['agent_type'].iloc[0] in ['motorcycle', 'bicycle']]
    for id_ptw in tqdm(ptw_ids, desc="Processing PTWs"):
        group_ptw = trajectories[id_ptw]
        for id_veh in trajectories:
            if id_ptw != id_veh and trajectories[id_veh]['agent_type'].iloc[0] not in ['motorcycle', 'bicycle']:
                group_veh = trajectories[id_veh]
                if group_veh['frame_id'].max() >= group_ptw['frame_id'].min() and group_veh['frame_id'].min() <= group_ptw['frame_id'].max():
                    PET, same_time_min_distance = PET_Calculate(group_veh, group_ptw)
                    if 0 <= PET <= pet_threshold and same_time_min_distance <= min_distance_threshold:
                        filtered_group_veh = calculate_yaw_accelerate(group_veh, yaw_accelerate_threshold)
                        filtered_group_ptw = calculate_yaw_accelerate(group_ptw, yaw_accelerate_threshold)
                        if not filtered_group_veh.empty and not filtered_group_ptw.empty:
                            output_dir = f'./tmp/{pet_threshold}_{yaw_accelerate_threshold}_{min_distance_threshold}_tmp'
                            write2csv(filtered_group_veh, filtered_group_ptw, output_dir)

# 示例使用
file_path = r"D:\Desktop\SITP\车辆sitp\Xi'an\Veh_smoothed_tracks_RawId.csv"
df = pd.read_csv(file_path)

# 对每个阈值组合进行网格搜索
for yaw_accelerate_threshold in YAW_ACCELERATE_THRESHOLDS:
    for pet_threshold in PET_THRESHOLDS:
        for min_distance_threshold in MIN_DISTANCE_THRESHOLDS:
            process_trajectories(df, yaw_accelerate_threshold, pet_threshold, min_distance_threshold)
