import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path

class StatusWindow:
    def __init__(self):
        try:
            self.root = tk.Tk()
            self.root.title("mygo助手")
            self.root.geometry("300x350")
            self.root.resizable(False, False)
            

            self.root.configure(bg='#f0f0f0')
            style = ttk.Style()
            style.configure('Switch.TCheckbutton',
                           background='#f0f0f0',
                           font=('Microsoft YaHei UI', 10))
            

            main_frame = ttk.Frame(self.root, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            

            title_label = ttk.Label(
                main_frame,
                text="mygo助手控制面板",
                font=('Microsoft YaHei UI', 12, 'bold')
            )
            title_label.pack(pady=(0, 10))
            

            self.is_running = tk.BooleanVar(value=True)
            self.switch = ttk.Checkbutton(
                main_frame,
                text="启用mygo助手",
                variable=self.is_running,
                style='Switch.TCheckbutton',
                command=self._on_switch_change
            )
            self.switch.pack(pady=5)
            

            self.status_label = ttk.Label(
                main_frame,
                text="状态：运行中",
                font=('Microsoft YaHei UI', 10)
            )
            self.status_label.pack(pady=5)
            

            status_frame = ttk.LabelFrame(
                main_frame,
                text="环境检查",
                padding="5"
            )
            status_frame.pack(fill=tk.X, pady=5)
            

            self.dep_status = ttk.Label(
                status_frame,
                text="依赖状态: 检查中...",
                font=('Microsoft YaHei UI', 9)
            )
            self.dep_status.pack(anchor=tk.W)
            

            self.file_status = ttk.Label(
                status_frame,
                text="文件状态: 检查中...",
                font=('Microsoft YaHei UI', 9)
            )
            self.file_status.pack(anchor=tk.W)
            

            check_btn = ttk.Button(
                status_frame,
                text="重新检查",
                command=self.check_all,
                width=10
            )
            check_btn.pack(pady=(5, 0))
            

            tips_frame = ttk.LabelFrame(
                main_frame,
                text="使用说明",
                padding="5"
            )
            tips_frame.pack(fill=tk.X, pady=5)
            
            tips_text = """1. 直接输入中文关键词
2. 使用左右箭头浏览表情包
3. 点击图片或按回车发送
4. 按ESC关闭窗口
5. 按Ctrl+Q退出程序"""
            
            tips_label = ttk.Label(
                tips_frame,
                text=tips_text,
                font=('Microsoft YaHei UI', 9),
                justify=tk.LEFT
            )
            tips_label.pack(pady=2)
            
            self.on_switch_change = None
            

            self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
            

            self.root.bind_all('<Control-q>', self.quit_app)
            self.root.bind_all('<Control-Q>', self.quit_app)
            

            self.root.after(100, self.check_all)
            
        except Exception as e:
            messagebox.showerror("错误", 
                f"启动失败，请确保系统已安装 Python 环境。\n错误信息: {str(e)}")
            raise
    
    def _on_switch_change(self):
        status = "运行中" if self.is_running.get() else "已停止"
        self.status_label.config(text=f"状态：{status}")
        if self.on_switch_change:
            self.on_switch_change(self.is_running.get())
    
    def minimize_to_tray(self):
        """最小化到托盘而不是关闭"""
        self.root.iconify()  
    
    def quit_app(self, event=None):
        """退出应用程序"""
        if messagebox.askokcancel("退出", "确定要退出mygo助手吗？"):
            self.root.destroy()
            sys.exit(0)
    
    def run(self):
        self.root.mainloop()
    
    def set_callback(self, callback):
        """设置回调函数"""
        self.on_switch_change = callback 
    
    def check_all(self):
        """检查所有环境状态"""
        self.check_dependencies()
        self.check_files()
    
    def check_dependencies(self):
        """检查依赖组件"""
        missing_deps = []
        
        dependencies = {
            'opencc': 'opencc-python-reimplemented',
            'PIL.Image': 'pillow',
            'win32gui': 'pywin32',
            'keyboard': 'keyboard'
        }
        
        for module, package in dependencies.items():
            try:
                __import__(module.split('.')[0])
            except ImportError:
                missing_deps.append(package)
        
        if missing_deps:
            self.dep_status.config(
                text="依赖状态: ⚠️ 缺少依赖",
                foreground='red'
            )
            install_cmd = "pip install " + " ".join(missing_deps)
            messagebox.showerror("缺少依赖", 
                "检测到缺少以下依赖组件：\n" + 
                "\n".join(missing_deps) + 
                "\n\n请使用以下命令安装：\n" +
                install_cmd + 
                "\n\n或者直接运行安装脚本：install_dependencies.py")
        else:
            self.dep_status.config(
                text="依赖状态: ✓ 已安装",
                foreground='green'
            )
    
    def check_files(self):
        """检查必要文件和目录"""
        base_path = Path(__file__).parent.parent
        missing_files = []
        
        required_paths = [
            ('config/config.json', '配置文件'),
            ('data/image_map.json', '图片映射文件'),
            ('images', '图片目录')
        ]
        
        for path, desc in required_paths:
            full_path = base_path / path
            if not full_path.exists():
                missing_files.append(f"{desc} ({path})")
                if path in ['images', 'config', 'data']:
                    try:
                        full_path.mkdir(parents=True, exist_ok=True)
                        print(f"已创建目录: {path}")
                    except Exception as e:
                        print(f"创建目录失败 {path}: {e}")
        
        if missing_files:
            self.file_status.config(
                text="文件状态: ⚠️ 缺少文件",
                foreground='red'
            )
            messagebox.showwarning("缺少文件",
                "检测到缺少以下文件或目录：\n" + 
                "\n".join(missing_files) + 
                "\n\n请确保：\n" +
                "1. 已将表情包图片放入 images 目录\n" +
                "2. 已运行索引工具生成图片映射\n" +
                "3. 配置文件存在且格式正确")
        else:
            self.file_status.config(
                text="文件状态: ✓ 完整",
                foreground='green'
            ) 