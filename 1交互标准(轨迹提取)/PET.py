import pandas as pd
import numpy as np
from tqdm import tqdm
import os

def PET_Calculate(group1, group2):
    """
    计算两组轨迹之间的潜在交通冲突时间（PET）。
    :param group1: DataFrame, 第一组车辆轨迹数据
    :param group2: DataFrame, 第二组车辆轨迹数据
    :return: float, PET时间，-1代表没有任何冲突
    """
    # 计算两组轨迹之间的所有可能组合的欧几里得距离
    distances = np.linalg.norm(group1[['x', 'y']].values[:, None, :] - group2[['x', 'y']].values[None, :, :], axis=2)
    min_distance = np.min(distances)

    if min_distance > 0.5:
        return -1

    # 找到最小距离对应的索引
    min_idx = np.unravel_index(np.argmin(distances, axis=None), distances.shape)
    # 计算对应的时间差
    PET = abs(group2.iloc[min_idx[1]]['timestamp_ms'] - group1.iloc[min_idx[0]]['timestamp_ms']) / 1000
    return PET

def write2csv(group1, group2, PET, vehicle_id, ptw_id):
    """
    将结果写入CSV文件。
    """
    output_dir = './tmp'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_filename = f'{output_dir}/data_V{vehicle_id}-PTW{ptw_id}.csv'
    with open(output_filename, 'w', newline="", encoding='utf-8') as f:
        group1.to_csv(f, index=False)
        group2.to_csv(f, index=False, header=False)




def process_trajectories(df):
    # 按track_id进行分组
    grouped = df.groupby('track_id')
    trajectories = {name: group for name, group in grouped}

    # 使用 tqdm 来添加进度条
    ptw_ids = [id for id in trajectories if trajectories[id]['agent_type'].iloc[0] in ['motorcycle', 'bicycle']]
    for id_ptw in tqdm(ptw_ids, desc="Processing PTWs"):
        group_ptw = trajectories[id_ptw]
        for id_veh in trajectories:
            if id_ptw != id_veh and trajectories[id_veh]['agent_type'].iloc[0] not in ['motorcycle', 'bicycle']:
                group_veh = trajectories[id_veh]
                if group_veh['frame_id'].max() >= group_ptw['frame_id'].min() and group_veh['frame_id'].min() <= group_ptw['frame_id'].max():
                    PET = PET_Calculate(group_veh, group_ptw)
                    if 0 <= PET <= 6:
                        write2csv(group_veh, group_ptw, PET, id_veh, id_ptw)

# 读取数据
df = pd.read_csv("D:\Desktop\SITP\车辆sitp\Xi'an\转向.csv")
process_trajectories(df)
