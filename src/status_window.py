import tkinter as tk
from tkinter import ttk
from pathlib import Path
import json
import traceback

class StatusWindow:
    def __init__(self, root=None):
        """初始化状态窗口"""
        try:
            print("初始化状态窗口...")
            
            # 使用传入的root或创建新的
            self.root = root or tk.Tk()
            
            # 创建主窗口
            self.window = tk.Toplevel(self.root)
            self.window.title("表情包助手")
            
            # 加载配置
            self.config = self.load_config()
            print("配置加载完成")
            
            # 设置窗口大小
            window_width = self.config.get('window', {}).get('width', 220)
            window_height = self.config.get('window', {}).get('height', 120)
            self.window.geometry(f"{window_width}x{window_height}")
            
            # 设置窗口属性
            self.window.attributes('-topmost', True)  # 保持在最上层
            self.window.attributes('-alpha', 0.95)    # 设置透明度
            self.window.overrideredirect(True)        # 无边框模式
            
            # 创建自定义样式
            self.style = ttk.Style()
            self.style.configure(
                'Status.TLabel',
                font=('Microsoft YaHei UI', 10),
                padding=10,
                background='#f0f0f0'
            )
            self.style.configure(
                'Title.TLabel',
                font=('Microsoft YaHei UI', 11, 'bold'),
                padding=(10, 5),
                background='#e0e0e0'
            )
            
            # 创建主框架
            self.main_frame = ttk.Frame(self.window, padding=2)
            self.main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 创建标题栏
            self.title_frame = ttk.Frame(self.main_frame)
            self.title_frame.pack(fill=tk.X)
            
            # 标题标签
            self.title_label = ttk.Label(
                self.title_frame,
                text="表情包助手",
                style='Title.TLabel'
            )
            self.title_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # 最小化按钮
            self.min_button = ttk.Label(
                self.title_frame,
                text="—",
                style='Title.TLabel',
                cursor='hand2'
            )
            self.min_button.pack(side=tk.RIGHT)
            self.min_button.bind('<Button-1>', lambda e: self.hide())
            
            # 关闭按钮
            self.close_button = ttk.Label(
                self.title_frame,
                text="×",
                style='Title.TLabel',
                cursor='hand2'
            )
            self.close_button.pack(side=tk.RIGHT)
            self.close_button.bind('<Button-1>', lambda e: self.close())
            
            # 状态标签
            self.status_label = ttk.Label(
                self.main_frame,
                text="按Tab键呼出搜索\n按ESC键隐藏窗口\n点击表情直接发送",
                style='Status.TLabel',
                justify=tk.CENTER
            )
            self.status_label.pack(expand=True)
            
            # 添加拖动功能
            self.title_frame.bind('<Button-1>', self.start_drag)
            self.title_frame.bind('<B1-Motion>', self.on_drag)
            self.title_label.bind('<Button-1>', self.start_drag)
            self.title_label.bind('<B1-Motion>', self.on_drag)
            
            # 初始化拖动变量
            self.drag_start_x = 0
            self.drag_start_y = 0
            
            # 将窗口放置在右下角
            self.position_window()
            
            # 保存初始位置
            self.save_position()
            
            print("状态窗口初始化完成")
            
        except Exception as e:
            print(f"状态窗口初始化失败: {e}")
            traceback.print_exc()
            raise

    def load_config(self):
        """加载配置文件"""
        try:
            config_path = Path(__file__).parent.parent / 'config' / 'config.json'
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return self.get_default_config()
        except Exception as e:
            print(f"加载配置失败: {e}")
            return self.get_default_config()

    def get_default_config(self):
        """获取默认配置"""
        return {
            'window': {
                'width': 220,
                'height': 120,
                'opacity': 0.95
            },
            'position': {
                'x': None,
                'y': None
            }
        }

    def save_config(self):
        """保存配置"""
        try:
            config_path = Path(__file__).parent.parent / 'config' / 'config.json'
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            print("配置保存成功")
        except Exception as e:
            print(f"保存配置失败: {e}")
            traceback.print_exc()

    def position_window(self):
        """将窗口定位到屏幕右下角"""
        try:
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            window_width = self.window.winfo_width()
            window_height = self.window.winfo_height()
            
            # 如果配置中有保存的位置，使用保存的位置
            if 'position' in self.config:
                x = self.config['position'].get('x')
                y = self.config['position'].get('y')
                if x is not None and y is not None:
                    self.window.geometry(f"+{x}+{y}")
                    return
            
            # 否则放置在右下角
            x = screen_width - window_width - 20
            y = screen_height - window_height - 40
            self.window.geometry(f"+{x}+{y}")
            print(f"窗口已定位到: x={x}, y={y}")
            
        except Exception as e:
            print(f"定位窗口失败: {e}")
            traceback.print_exc()

    def save_position(self):
        """保存窗口位置"""
        try:
            x = self.window.winfo_x()
            y = self.window.winfo_y()
            self.config.setdefault('position', {})
            self.config['position']['x'] = x
            self.config['position']['y'] = y
            self.save_config()
        except Exception as e:
            print(f"保存位置失败: {e}")
            traceback.print_exc()

    def start_drag(self, event):
        """开始拖动"""
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def on_drag(self, event):
        """拖动时"""
        try:
            x = self.window.winfo_x() + (event.x - self.drag_start_x)
            y = self.window.winfo_y() + (event.y - self.drag_start_y)
            self.window.geometry(f"+{x}+{y}")
            self.save_position()
        except Exception as e:
            print(f"拖动失败: {e}")
            traceback.print_exc()

    def update_status(self, text):
        """更新状态文本"""
        try:
            self.status_label.configure(text=text)
        except Exception as e:
            print(f"更新状态失败: {e}")
            traceback.print_exc()

    def show(self):
        """显示窗口"""
        try:
            self.window.deiconify()
            self.window.lift()
            self.position_window()
        except Exception as e:
            print(f"显示窗口失败: {e}")
            traceback.print_exc()

    def hide(self):
        """隐藏窗口"""
        try:
            self.window.withdraw()
        except Exception as e:
            print(f"隐藏窗口失败: {e}")
            traceback.print_exc()

    def close(self):
        """关闭窗口"""
        try:
            self.save_position()
            self.window.destroy()
        except Exception as e:
            print(f"关闭窗口失败: {e}")
            traceback.print_exc()