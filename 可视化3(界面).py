import matplotlib
matplotlib.use('TkAgg')  # 确保在 PyCharm 中启用交互式绘图
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.lines import Line2D
import glob
import os
from tkinter import Tk, filedialog, Button, Label, Frame, StringVar, OptionMenu

# 定义读取CSV文件的函数
def read_csv_file(file_path):
    data = pd.read_csv(file_path, dtype=str)  # 读取CSV文件并将所有列类型设置为字符串
    data['frame_id'] = data['frame_id'].astype(int)  # 将frame_id列转换为整数类型
    min_frame_id = data['frame_id'].min()  # 获取最小的frame_id值
    data['Frame'] = data['frame_id'] - min_frame_id  # 创建一个新的Frame列，从0开始编号

    data['ID'] = data.iloc[:, 0]  # 获取ID列
    data['Type'] = data.iloc[:, 3]  # 获取Type列
    data['X'] = data.iloc[:, 4].astype(float)  # 获取X列并转换为浮点数
    data['Y'] = data.iloc[:, 5].astype(float)  # 获取Y列并转换为浮点数
    data['Turn'] = data.iloc[:, 18]  # 获取Turn列

    type_map = {  # 定义类型映射
        "car": 'C',
        "motorcycle": 'M',
        "bicycle": 'B',
        "bus": 'BUS',
        "tricycle": 'TC',
        "truck": 'TR',
        "pedestrian": 'P',
        "others": 'O'
    }
    data['Type'] = data['Type'].map(type_map)  # 映射Type列

    turn_map = {  # 定义转向映射
        "right": 'R',
        "left": 'L',
        "straight": 'S'
    }
    data['Turn'] = data['Turn'].map(turn_map)  # 映射Turn列
    return data

# 初始化动画
def init_animation():
    global fig, ax, lines, type_colors
    fig, ax = plt.subplots()  # 创建一个子图
    ax.set_xlim([-30, 30])  # 设置X轴范围
    ax.set_ylim([-10, 50])  # 设置Y轴范围
    lines = {}  # 初始化存储线条和文本的字典
    type_colors = {  # 定义每种类型的颜色
        'C': 'r',
        'M': 'b',
        'B': [1, 0.84314, 0],
        'BUS': 'cyan',
        'TC': [0.54118, 0.16863, 0.88627],
        'TR': [0.5451, 0.27059, 0.07451],
        'P': 'k',
        'O': 'green'
    }

# 初始化函数，在开始动画前调用
def init():
    for key in lines.keys():  # 遍历所有的线条
        if lines[key]['line'] is not None:
            lines[key]['line'].set_data([], [])  # 清空线条数据
        if lines[key]['text'] is not None:
            lines[key]['text'].set_visible(False)  # 隐藏文本
        if lines[key]['turn_text'] is not None:
            lines[key]['turn_text'].set_visible(False)  # 隐藏转向文本
    return []

# 更新函数，在每一帧调用
def update(frame, data):
    current_data = data[data['Frame'] == frame]  # 获取当前帧的数据
    ids_in_frame = set(current_data['ID'].values)  # 获取当前帧的所有ID

    # 初始化ID
    for _id in ids_in_frame:
        if _id not in lines:
            lines[_id] = {
                'line': None,
                'text': None,
                'turn_text': None
            }

    for _id in list(lines.keys()):
        if _id not in ids_in_frame:
            if lines[_id]['line'] is not None:
                lines[_id]['line'].set_data([], [])  # 清空不在当前帧的线条数据
            if lines[_id]['text'] is not None:
                lines[_id]['text'].set_visible(False)  # 隐藏不在当前帧的文本
            if lines[_id]['turn_text'] is not None:
                lines[_id]['turn_text'].set_visible(False)  # 隐藏不在当前帧的转向文本

    for idx, row in current_data.iterrows():
        _id = row['ID']
        if lines[_id]['line'] is None:
            lines[_id]['line'] = Line2D([], [], color=type_colors[row['Type']], linewidth=2 if row['Type'] == 'C' else 1)  # 创建新线条
            ax.add_line(lines[_id]['line'])
        if lines[_id]['text'] is None:
            lines[_id]['text'] = ax.text(0, 0, f"{row['Type']}{_id}", verticalalignment='top', fontsize=8, visible=True)  # 创建新文本，设置字体大小
        if lines[_id]['turn_text'] is None:
            lines[_id]['turn_text'] = ax.text(0, 0, row['Turn'], verticalalignment='top', fontsize=8, color='green', visible=True)  # 创建新转向文本，设置字体大小
        x, y = row['X'], row['Y']
        lines[_id]['line'].set_data(list(lines[_id]['line'].get_xdata()) + [x], list(lines[_id]['line'].get_ydata()) + [y])  # 更新线条数据
        lines[_id]['text'].set_position((x, y))  # 更新文本位置
        lines[_id]['text'].set_visible(True)  # 显示文本
        lines[_id]['turn_text'].set_position((x, y - 1))  # 更新转向文本位置
        lines[_id]['turn_text'].set_visible(True)  # 显示转向文本
    return []

# 可视化CSV文件
def visualize_csv():
    global data, ani, SOTIF_framemax
    selected_file_path = csv_files_dict.get(selected_file.get())
    if selected_file_path:
        data = read_csv_file(selected_file_path)  # 读取CSV文件
        SOTIF_framemax = data['Frame'].max()  # 获取最大帧数
        init_animation()  # 初始化动画
        ani = animation.FuncAnimation(fig, update, frames=range(SOTIF_framemax + 1), fargs=(data,), init_func=init, blit=False)  # 创建动画
        plt.show()
        # 记录已经播放过的文件
        played_files.add(selected_file.get())
        update_option_menu()

# 更新OptionMenu
def update_option_menu():
    option_menu['menu'].delete(0, 'end')  # 清空OptionMenu
    for file_name in csv_files_dict.keys():
        color = "green" if file_name in played_files else "black"  # 设置已经播放过的文件为绿色
        option_menu['menu'].add_command(label=file_name, command=lambda name=file_name: selected_file.set(name), foreground=color)  # 添加新的文件选项

# 加载文件夹
def load_folder():
    global csv_files_dict
    folder_path = filedialog.askdirectory()  # 打开文件夹选择对话框
    if folder_path:
        csv_files = glob.glob(os.path.join(folder_path, "*.csv"))  # 获取所有CSV文件
        csv_files_dict = {os.path.basename(f): f for f in csv_files}  # 创建文件名和路径的字典
        if csv_files_dict:
            selected_file.set('选择CSV文件')
            update_option_menu()  # 更新OptionMenu
        else:
            selected_file.set('文件夹中没有CSV文件')

# 创建Tkinter界面
root = Tk()
root.title("CSV文件可视化")

played_files = set()  # 初始化已经播放过的文件集合

frame = Frame(root)
frame.pack(padx=10, pady=10)

label = Label(frame, text="选择包含CSV文件的文件夹:")  # 创建标签
label.pack(pady=5)

btn_load = Button(frame, text="选择文件夹", command=load_folder)  # 创建选择文件夹按钮
btn_load.pack(pady=5)

select_file = StringVar(root)  # 初始化选择文件的StringVar
selected_file = StringVar(root)  # 初始化当前选择文件的StringVar

option_menu = OptionMenu(frame, selected_file, ())  # 创建文件选择的OptionMenu
option_menu.pack(pady=5)

btn_play = Button(frame, text="播放动画", command=visualize_csv)  # 创建播放动画按钮
btn_play.pack(pady=5)

root.mainloop()
