import tkinter as tk
from tkinter import ttk, messagebox
import random
import numpy as np
from sklearn.linear_model import LinearRegression
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta

plt.rcParams['font.family'] = 'SimHei'
plt.rcParams['axes.unicode_minus'] = False

# 用户数据库
users = {
    "admin": "admin123",
    "user": "user123"
}


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("空气质量监测系统 - 登录")
        self.root.geometry("300x200")
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.root, text="用户名:").place(x=50, y=40)
        self.username = ttk.Entry(self.root)
        self.username.place(x=120, y=40)

        ttk.Label(self.root, text="密码:").place(x=50, y=80)
        self.password = ttk.Entry(self.root, show="*")
        self.password.place(x=120, y=80)

        ttk.Button(self.root, text="登录", command=self.authenticate).place(x=120, y=120)
        self.status = ttk.Label(self.root, text="", foreground="red")
        self.status.place(x=80, y=160)

    def authenticate(self):
        username = self.username.get()
        password = self.password.get()

        if username in users and users[username] == password:
            self.root.destroy()
            main_window = tk.Tk()
            AirQualityApp(main_window)
            main_window.mainloop()
        else:
            self.status.config(text="用户名或密码错误！")


class AirQualityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("空气质量实时监测系统")
        self.root.geometry("1200x800")

        # 初始化数据
        self.history = {
            'PM2.5': [], 'PM10': [], 'CO2': [], 'SO2': [], 'timestamp': []
        }
        self.prediction_data = {
            'PM2.5': [], 'PM10': [], 'CO2': [], 'SO2': [], 'timestamp': []
        }

        # 创建界面
        self.create_menu()
        self.create_widgets()
        self.update_data()

    def create_menu(self):
        menubar = tk.Menu(self.root)

        # 系统菜单
        system_menu = tk.Menu(menubar, tearoff=0)
        system_menu.add_command(label="退出", command=self.root.quit)

        # 用户菜单
        user_menu = tk.Menu(menubar, tearoff=0)
        user_menu.add_command(label="修改密码", command=self.change_password)
        user_menu.add_separator()
        user_menu.add_command(label="注销", command=self.logout)

        # 分析菜单
        analysis_menu = tk.Menu(menubar, tearoff=0)
        analysis_menu.add_command(label="预测未来趋势", command=self.show_prediction)
        analysis_menu.add_command(label="关闭预测", command=self.hide_prediction)

        menubar.add_cascade(label="系统", menu=system_menu)
        menubar.add_cascade(label="用户", menu=user_menu)
        menubar.add_cascade(label="分析", menu=analysis_menu)

        self.root.config(menu=menubar)

    def change_password(self):
        dialog = tk.Toplevel()
        dialog.title("修改密码")
        dialog.geometry("300x200")

        ttk.Label(dialog, text="原密码:").place(x=50, y=40)
        old_pw = ttk.Entry(dialog, show="*")
        old_pw.place(x=120, y=40)

        ttk.Label(dialog, text="新密码:").place(x=50, y=80)
        new_pw = ttk.Entry(dialog, show="*")
        new_pw.place(x=120, y=80)

        ttk.Label(dialog, text="确认密码:").place(x=50, y=120)
        confirm_pw = ttk.Entry(dialog, show="*")
        confirm_pw.place(x=120, y=120)

        def save_password():
            if new_pw.get() != confirm_pw.get():
                messagebox.showerror("错误", "新密码不一致！")
                return
            messagebox.showinfo("成功", "密码修改成功！")
            dialog.destroy()

        ttk.Button(dialog, text="保存", command=save_password).place(x=120, y=160)

    def logout(self):
        self.root.destroy()
        root = tk.Tk()
        LoginWindow(root)
        root.mainloop()

    def create_widgets(self):
        # 控制面板
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=10, padx=10, fill="x")

        # 城市选择
        self.city_frame = ttk.LabelFrame(control_frame, text="城市选择")
        self.city_frame.pack(side=tk.LEFT, padx=5)

        self.cities = ttk.Combobox(self.city_frame, values=["北京", "上海", "广州", "深圳"])
        self.cities.set("北京")
        self.cities.pack(pady=5, padx=5)

        # 操作按钮
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(side=tk.LEFT, padx=10)

        ttk.Button(btn_frame, text="刷新数据", command=self.update_data).pack(pady=5)
        ttk.Button(btn_frame, text="预测趋势", command=self.show_prediction).pack(pady=5)

        # 实时数据显示
        self.data_frame = ttk.LabelFrame(self.root, text="实时数据")
        self.data_frame.pack(pady=10, padx=10, fill="x")

        self.labels = {
            'PM2.5': self.create_data_label("PM2.5 (μg/m³)", 0),
            'PM10': self.create_data_label("PM10 (μg/m³)", 1),
            'CO2': self.create_data_label("CO2 (ppm)", 2),
            'SO2': self.create_data_label("SO2 (μg/m³)", 3)
        }

        # 图表区域
        self.chart_frame = ttk.LabelFrame(self.root, text="空气质量趋势")
        self.chart_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.fig = Figure(figsize=(10, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # 预测开关
        self.show_prediction_flag = False

    def create_data_label(self, text, row):
        frame = ttk.Frame(self.data_frame)
        frame.grid(row=row, column=0, padx=10, pady=5, sticky="w")

        ttk.Label(frame, text=text, width=15).pack(side=tk.LEFT)
        value_label = ttk.Label(frame, text="--", width=10)
        value_label.pack(side=tk.LEFT)

        status_label = ttk.Label(frame, text="", width=15)
        status_label.pack(side=tk.LEFT)

        return (value_label, status_label)

    def get_air_quality(self):
        """模拟获取空气质量数据"""
        return {
            'PM2.5': random.randint(20, 200),
            'PM10': random.randint(30, 300),
            'CO2': random.randint(400, 2000),
            'SO2': random.randint(5, 150)
        }

    def predict_future(self):
        """使用线性回归预测未来3小时数据"""
        for key in ['PM2.5', 'PM10', 'CO2', 'SO2']:
            if len(self.history[key]) < 3:  # 至少需要3个数据点才能预测
                self.prediction_data[key] = []
                continue

            # 准备数据
            X = np.arange(len(self.history[key])).reshape(-1, 1)
            y = np.array(self.history[key])

            # 训练模型
            model = LinearRegression()
            model.fit(X, y)

            # 预测未来3个时间点
            future_X = np.arange(len(self.history[key]), len(self.history[key]) + 3).reshape(-1, 1)
            self.prediction_data[key] = model.predict(future_X).tolist()

        # 生成预测时间戳
        last_time = datetime.strptime(self.history['timestamp'][-1], "%H:%M:%S")
        self.prediction_data['timestamp'] = [
            (last_time + timedelta(hours=i)).strftime("%H:%M:%S") for i in range(1, 4)
        ]

    def update_data(self):
        # 获取新数据
        new_data = self.get_air_quality()
        timestamp = datetime.now().strftime("%H:%M:%S")

        # 更新历史记录
        for key in self.history:
            if key in new_data:
                self.history[key].append(new_data[key])
            else:
                self.history[key].append(timestamp)

        # 保持最多20条历史记录
        for key in self.history:
            if len(self.history[key]) > 20:
                self.history[key] = self.history[key][-20:]

        # 更新预测数据
        if self.show_prediction_flag:
            self.predict_future()

        # 更新界面
        self.update_display(new_data)
        self.update_chart()

        # 每5秒自动更新
        self.root.after(5000, self.update_data)

    def update_display(self, data):
        for key, (value_label, status_label) in self.labels.items():
            value_label.config(text=str(data[key]))

            if key == 'PM2.5':
                status, color = self.get_pm25_status(data[key])
            elif key == 'PM10':
                status, color = self.get_pm10_status(data[key])
            else:
                status, color = "", "black"

            status_label.config(text=status, foreground=color)

    def get_pm25_status(self, value):
        if value <= 35:
            return "优", "green"
        elif value <= 75:
            return "良", "blue"
        elif value <= 115:
            return "轻度污染", "orange"
        else:
            return "重度污染", "red"

    def get_pm10_status(self, value):
        if value <= 50:
            return "优", "green"
        elif value <= 150:
            return "良", "blue"
        elif value <= 250:
            return "轻度污染", "orange"
        else:
            return "重度污染", "red"

    def update_chart(self):
        self.ax.clear()

        # 绘制历史数据
        self.ax.plot(self.history['timestamp'], self.history['PM2.5'], 'b-', label='PM2.5')
        self.ax.plot(self.history['timestamp'], self.history['PM10'], 'g-', label='PM10')
        self.ax.plot(self.history['timestamp'], self.history['CO2'], 'r-', label='CO2')
        self.ax.plot(self.history['timestamp'], self.history['SO2'], 'm-', label='SO2')

        # 绘制预测数据
        if self.show_prediction_flag and len(self.prediction_data['timestamp']) > 0:
            # 连接最后一个历史数据点和第一个预测点
            for key, color in [('PM2.5', 'b'), ('PM10', 'g'), ('CO2', 'r'), ('SO2', 'm')]:
                if len(self.prediction_data[key]) > 0:
                    last_hist = self.history[key][-1]
                    first_pred = self.prediction_data[key][0]
                    self.ax.plot(
                        [self.history['timestamp'][-1], self.prediction_data['timestamp'][0]],
                        [last_hist, first_pred],
                        color=color, linestyle='--'
                    )

            # 绘制预测数据点
            self.ax.plot(self.prediction_data['timestamp'], self.prediction_data['PM2.5'], 'b--', label='PM2.5预测')
            self.ax.plot(self.prediction_data['timestamp'], self.prediction_data['PM10'], 'g--', label='PM10预测')
            self.ax.plot(self.prediction_data['timestamp'], self.prediction_data['CO2'], 'r--', label='CO2预测')
            self.ax.plot(self.prediction_data['timestamp'], self.prediction_data['SO2'], 'm--', label='SO2预测')

            # 标记预测区域
            self.ax.axvspan(
                self.history['timestamp'][-1], self.prediction_data['timestamp'][-1],
                color='gray', alpha=0.1, label='预测区域'
            )

        # 图表格式设置
        self.ax.set_title("空气质量趋势及预测")
        self.ax.set_xlabel("时间")
        self.ax.set_ylabel("浓度值")
        self.ax.legend()
        self.ax.tick_params(axis='x', rotation=45)

        # 调整x轴刻度，避免重叠
        if len(self.history['timestamp']) > 10:
            step = len(self.history['timestamp']) // 10
            self.ax.set_xticks(self.history['timestamp'][::step])

        self.fig.tight_layout()
        self.canvas.draw()

    def show_prediction(self):
        """显示预测功能"""
        self.show_prediction_flag = True
        self.predict_future()
        self.update_chart()
        messagebox.showinfo("提示", "已开启未来3小时预测功能")

    def hide_prediction(self):
        """隐藏预测功能"""
        self.show_prediction_flag = False
        self.update_chart()
        messagebox.showinfo("提示", "已关闭预测功能")


if __name__ == "__main__":
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()