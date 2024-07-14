import matplotlib
matplotlib.use('TkAgg')  # 确保在 PyCharm 中启用交互式绘图
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.lines import Line2D

# 读取带有转向信息的数据
data = pd.read_csv("D:\Desktop\SITP\车辆sitp\Xi'an\Veh_smoothed_tracks_RawId.csv", dtype=str)

# 转换列数据类型
data['Frame'] = data["frame_id"].astype(int)  # 将第2列转换为整数表示帧号
data['ID'] = data["track_id"] # 将第1列作为车辆ID
data['Type'] = data['agent_type']  # 将第4列作为车辆类型
data['X'] = data['x'].astype(float)  # 将第5列转换为浮点数表示X坐标
data['Y'] = data["y"].astype(float)  # 将第6列转换为浮点数表示Y坐标
data['Turn'] = data["trajectory"]  # 将第19列作为转向信息

# 映射类型到简化标识符
type_map = {
    "car": 'C',
    "motorcycle": 'M',
    "bicycle": 'B',
    "bus": 'BUS',
    "tricycle": 'TC',
    "truck": 'TR',
    "pedestrian": 'P',
    "others": 'O'
}
data['Type'] = data['Type'].map(type_map)  # 将车辆类型映射为简化标识符

# 映射转向信息到简化标识符
turn_map = {
    "right": 'R',
    "left": 'L',
    "straight": 'S'
}
data['Turn'] = data['Turn'].map(turn_map)  # 将转向信息映射为简化标识符

# 准备动画
fig, ax = plt.subplots()
ax.set_xlim([-30, 30])  # 设置X轴范围
ax.set_ylim([-10, 50])  # 设置Y轴范围

# 创建一个字典来保存动画线条和文本
lines = {}
for _id in data['ID'].unique():
    lines[_id] = {
        'line': None,
        'text': None,
        'turn_text': None  # 新增转向信息的文本
    }

# 定义不同类型的颜色
type_colors = {
    'C': 'r',  # 小汽车
    'M': 'b',  # 摩托车
    'B': [1, 0.84314, 0],  # 自行车
    'BUS': 'cyan',  # 公共汽车
    'TC': [0.54118, 0.16863, 0.88627],  # 三轮车
    'TR': [0.5451, 0.27059, 0.07451],  # 卡车
    'P': 'k',  # 行人
    'O': 'green'  # 其他
}

def init():
    """初始化函数，在开始动画前调用"""
    for key in lines.keys():
        if lines[key]['line'] is not None:
            lines[key]['line'].set_data([], [])  # 清空线条数据
        if lines[key]['text'] is not None:
            lines[key]['text'].set_visible(False)  # 隐藏文本
        if lines[key]['turn_text'] is not None:
            lines[key]['turn_text'].set_visible(False)  # 隐藏转向文本
    return []

def update(frame):
    """更新函数，在每一帧调用"""
    current_data = data[data['Frame'] == frame]  # 获取当前帧的数据
    ids_in_frame = set(current_data['ID'].values)  # 当前帧中的车辆ID集合

    # 清除不再活动的线条和文本
    for _id in list(lines.keys()):
        if _id not in ids_in_frame:
            if lines[_id]['line'] is not None:
                lines[_id]['line'].set_data([], [])  # 清空不活动线条的数据
            if lines[_id]['text'] is not None:
                lines[_id]['text'].set_visible(False)  # 隐藏不活动文本
            if lines[_id]['turn_text'] is not None:
                lines[_id]['turn_text'].set_visible(False)  # 隐藏不活动转向文本

    for idx, row in current_data.iterrows():
        _id = row['ID']
        if lines[_id]['line'] is None:
            lines[_id]['line'] = Line2D([], [], color=type_colors[row['Type']], linewidth=2 if row['Type'] == 'C' else 1)
            ax.add_line(lines[_id]['line'])  # 为新出现的车辆添加线条
        if lines[_id]['text'] is None:
            lines[_id]['text'] = ax.text(0, 0, f"{row['Type']}{_id}", verticalalignment='top', fontsize=5, visible=True)
        if lines[_id]['turn_text'] is None:
            lines[_id]['turn_text'] = ax.text(0, 0, row['Turn'], verticalalignment='top', fontsize=5, color='green', visible=True)
        x, y = row['X'], row['Y']
        lines[_id]['line'].set_data(list(lines[_id]['line'].get_xdata()) + [x], list(lines[_id]['line'].get_ydata()) + [y])
        lines[_id]['text'].set_position((x, y))
        lines[_id]['text'].set_visible(True)
        lines[_id]['turn_text'].set_position((x, y - 1))  # 显示在车辆下方
        lines[_id]['turn_text'].set_visible(True)
    return []

# 获取最大帧数
SOTIF_framemax = data['Frame'].max()

# 创建动画
ani = animation.FuncAnimation(fig, update, frames=range(SOTIF_framemax + 1), init_func=init, blit=False)

# 显示动画
plt.show()
