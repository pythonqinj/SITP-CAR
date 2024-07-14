import pandas as pd

# 加载提供的CSV文件
file_path = "D:\\Desktop\\SITP\\车辆sitp\\Xi'an\\Veh_smoothed_tracks_RawId.csv"
data = pd.read_csv(file_path)

# 定义区域范围
regions = {
    1: {'x': (-20, 20), 'y': (-float('inf'), 10)},
    2: {'x': (-float('inf'), -20), 'y': (0, 40)},
    3: {'x': (-20, 20), 'y': (30, float('inf'))},
    4: {'x': (20, float('inf')), 'y': (0, 40)}
}

# 定义一个函数判断点属于哪个区域
def get_region(x, y):
    for region, bounds in regions.items():
        if bounds['x'][0] < x <= bounds['x'][1] and bounds['y'][0] < y <= bounds['y'][1]:
            return region
    return None

# 获取每个 track_id 的第一帧和最后一帧的坐标
grouped = data.groupby('track_id')
first_frame = grouped.first().reset_index()
last_frame = grouped.last().reset_index()

# 应用区域判断逻辑
first_frame['start_region'] = first_frame.apply(lambda row: get_region(row['x'], row['y']), axis=1)
last_frame['end_region'] = last_frame.apply(lambda row: get_region(row['x'], row['y']), axis=1)

# 判断转向
def determine_turn(start_region, end_region):
    if start_region is not None and end_region is not None:
        delta = end_region - start_region
        if abs(delta) == 2:
            return 'straight'
        elif delta == 1 or delta == -3:
            return 'left'
        elif delta == -1 or delta == 3:
            return 'right'
    return 'unknown'

# 计算转向
turns = first_frame[['track_id', 'start_region']].merge(last_frame[['track_id', 'end_region']], on='track_id')
turns['turn'] = turns.apply(lambda row: determine_turn(row['start_region'], row['end_region']), axis=1)

# 合并转向数据到原始数据
data = data.merge(turns[['track_id', 'turn']], on='track_id', how='left')

# 将标记后的数据保存到一个新的CSV文件
output_file_path = '转向2.csv'
data.to_csv(output_file_path, index=False)

print("转向判断已完成，结果已保存到", output_file_path)
