import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import json
import re
import traceback
from pathlib import Path
import threading
from queue import Queue
import time
import keyboard
from io import BytesIO

class MemeSelector:
    """表情包选择器类"""
    
    # 1. 配置相关方法
    def get_default_config(self):
        """获取默认配置"""
        return {
            'window': {
                'width': 400,
                'height': 500,
                'opacity': 0.95,
                'position': {'x': None, 'y': None}
            },
            'features': {
                'search': {
                    'score_threshold': 10,
                    'max_results': 20,
                    'min_length': 1
                },
                'display': {
                    'thumbnail_size': 100,
                    'max_name_length': 30
                }
            },
            'style': {
                'font_family': 'Microsoft YaHei UI',
                'font_size': 10,
                'hover_color': '#f0f0f0',
                'toast_bg': '#333333',
                'toast_fg': 'white'
            }
        }

    def merge_configs(self, default_config, user_config):
        """深度合并配置"""
        for key, value in user_config.items():
            if key in default_config:
                if isinstance(value, dict) and isinstance(default_config[key], dict):
                    self.merge_configs(default_config[key], value)
                else:
                    default_config[key] = value

    def load_config(self):
        """加载配置文件"""
        try:
            config_path = self.config_path / 'config.json'
            default_config = self.get_default_config()
            
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    self.merge_configs(default_config, user_config)
            
            return default_config
            
        except Exception as e:
            print(f"加载配置失败: {e}")
            traceback.print_exc()
            return self.get_default_config()

    def __init__(self, root=None):
        """初始化表情包选择器"""
        try:
            print("初始化表情包选择器...")
            
            # 1. 基础设置
            self.root = root or tk.Tk()
            if not root:
                self.root.withdraw()
            
            # 2. 设置路径
            self.base_path = Path(__file__).parent.parent
            self.images_path = self.base_path / 'images'
            self.config_path = self.base_path / 'config'
            self.data_path = self.base_path / 'data'
            
            # 3. 加载配置
            self.config = self.load_config()
            print("配置加载完成")
            
            # 4. 初始化转换器
            try:
                import opencc
                self.t2s = opencc.OpenCC('t2s')
                self.s2t = opencc.OpenCC('s2t')
                print("OpenCC 转换器初始化成功")
            except Exception as e:
                print(f"警告: OpenCC 初始化失败，将使用简单转换: {e}")
                self.t2s = lambda x: x
                self.s2t = lambda x: x
            
            # 5. 初始化变量
            self.current_window = None
            self.search_var = tk.StringVar(self.root)
            self.pinyin_buffer = ""
            self.photo_references = {}
            self.last_search = ""
            self.search_results = []
            
            # 6. 创建自定义样式
            self.style = ttk.Style()
            self.style.configure('Result.TFrame', padding=5)
            self.style.configure('Hover.TFrame', background='#f0f0f0')
            self.style.configure('ResultText.TLabel', 
                               font=(self.config['style']['font_family'], 
                                    self.config['style']['font_size']))
            
            # 7. 创建提示标签
            self.toast_label = ttk.Label(
                self.root,
                text="",
                style='Toast.TLabel',
                background=self.config['style']['toast_bg'],
                foreground=self.config['style']['toast_fg'],
                padding=10
            )
            
            # 8. 加载图片映射
            self.image_map = self.load_image_map()
            print(f"加载了 {len(self.image_map)} 个图片映射")
            
            # 9. 预加载图片
            self.preload_images()
            
            print("表情包选择器初始化完成")
            
        except Exception as e:
            print(f"初始化失败: {e}")
            traceback.print_exc()
            raise

    def load_image_map(self):
        """加载图片映射"""
        try:
            image_map = {}
            for image_path in self.images_path.glob('**/*'):
                if image_path.is_file() and image_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                    relative_path = image_path.relative_to(self.images_path)
                    name = relative_path.stem.lower()  # 转换为小写以便搜索
                    image_map[name] = str(image_path)
            return image_map
        except Exception as e:
            print(f"加载图片映射失败: {e}")
            traceback.print_exc()
            return {}

    def preload_images(self):
        """预加载图片缩略图"""
        try:
            total = len(self.image_map)
            success = 0
            thumbnail_size = self.config['features']['display']['thumbnail_size']
            
            for name, path in self.image_map.items():
                try:
                    image = Image.open(path)
                    image.thumbnail((thumbnail_size, thumbnail_size))
                    photo = ImageTk.PhotoImage(image)
                    self.photo_references[name] = photo
                    success += 1
                except Exception as e:
                    print(f"预加载图片失败 {path}: {e}")
                    
            print(f"预加载完成: 成功 {success}/{total} 个图片")
            
        except Exception as e:
            print(f"预加载过程失败: {e}")
            traceback.print_exc()

    def check_directories(self):
        """检查并创建必要的目录"""
        try:
            required_dirs = [self.images_path, self.config_path, self.data_path]
            for dir_path in required_dirs:
                if not dir_path.exists():
                    print(f"创建目录: {dir_path}")
                    dir_path.mkdir(parents=True)
                else:
                    print(f"目录已存在: {dir_path}")
            return True
        except Exception as e:
            print(f"检查目录失败: {e}")
            traceback.print_exc()
            return False

    def load_image_map(self):
        """加载图片映射"""
        try:
            image_map = {}
            for image_path in self.images_path.glob('**/*'):
                if image_path.is_file() and image_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                    relative_path = image_path.relative_to(self.images_path)
                    name = relative_path.stem.lower()  # 转换为小写以便搜索
                    image_map[name] = str(image_path)
            return image_map
        except Exception as e:
            print(f"加载图片映射失败: {e}")
            traceback.print_exc()
            return {}

    def preload_images(self):
        """预加载图片缩略图"""
        try:
            total = len(self.image_map)
            success = 0
            thumbnail_size = self.config['features']['display']['thumbnail_size']
            
            for name, path in self.image_map.items():
                try:
                    image = Image.open(path)
                    image.thumbnail((thumbnail_size, thumbnail_size))
                    photo = ImageTk.PhotoImage(image)
                    self.photo_references[name] = photo
                    success += 1
                except Exception as e:
                    print(f"预加载图片失败 {path}: {e}")
                    
            print(f"预加载完成: 成功 {success}/{total} 个图片")
            
        except Exception as e:
            print(f"预加载过程失败: {e}")
            traceback.print_exc()

    def send_image(self, image_path):
        """发送图片到剪贴板"""
        try:
            print(f"准备发送图片: {image_path}")
            
            # 加载图片
            image = Image.open(image_path)
            
            # 转换为BMP格式（用于剪贴板）
            output = BytesIO()
            image.convert('RGB').save(output, 'BMP')
            data = output.getvalue()[14:]  # 跳过BMP文件头
            output.close()
            
            # 复制到剪贴板
            import win32clipboard
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
            
            # 模拟粘贴操作
            keyboard.send('ctrl+v')
            
            # 显示成功提示
            self.show_toast("图片已发送", 2000)
            
            # 清空搜索
            self.pinyin_buffer = ""
            self.search_var.set("")
            
            # 隐藏窗口
            self.hide_window()
            
        except Exception as e:
            print(f"发送图片失败: {e}")
            traceback.print_exc()
            
            try:
                # 备用方案：保存为临时文件
                import tempfile
                import os
                
                temp_dir = tempfile.gettempdir()
                temp_path = os.path.join(temp_dir, f"meme_{int(time.time())}.png")
                
                image = Image.open(image_path)
                image.save(temp_path)
                
                self.show_toast(f"图片已保存到: {temp_path}", 3000)
                
            except Exception as backup_error:
                print(f"备用方案也失败了: {backup_error}")
                self.show_toast("发送失败", 2000)

    def create_thumbnail(self, image_path, size=(100, 100)):
        """创建图片缩略图"""
        try:
            image = Image.open(image_path)
            image.thumbnail(size)
            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"创建缩略图失败 {image_path}: {e}")
            return None

    def reload_images(self):
        """重新加载所有图片"""
        try:
            print("重新加载图片...")
            self.photo_references.clear()
            self.image_map = self.load_image_map()
            self.preload_images()
            print("图片重新加载完成")
            return True
        except Exception as e:
            print(f"重新加载图片失败: {e}")
            traceback.print_exc()
            return False

    def search_memes(self, search_text):
        """搜索表情包"""
        try:
            print(f"\n开始搜索: {search_text}")
            
            # 转换搜索文本
            search_text_simp = self.t2s.convert(search_text)
            search_text_trad = self.s2t.convert(search_text)
            print(f"搜索文本: 「{search_text}」简体「{search_text_simp}」繁体「{search_text_trad}」")
            
            # 初始化结果列表
            results = []
            
            # 遍历所有图片
            for name, path in self.image_map.items():
                try:
                    # 计算匹配分数
                    score = self.calculate_match_score(name, [
                        search_text,
                        search_text_simp,
                        search_text_trad
                    ])
                    
                    # 如果分数超过阈值，添加到结果
                    if score >= self.config['features']['search']['score_threshold']:
                        results.append({
                            'name': name,
                            'path': path,
                            'score': score,
                            'alt': name.replace('_', ' ').title()
                        })
                except Exception as e:
                    print(f"处理图片 {name} 失败: {e}")
                    continue
            
            # 按分数排序
            results.sort(key=lambda x: x['score'], reverse=True)
            
            # 限制结果数量
            max_results = self.config['features']['search']['max_results']
            results = results[:max_results]
            
            print(f"找到 {len(results)} 个匹配结果")
            
            # 显示排名前三的匹配
            if results:
                print("排名前三的匹配：")
                for i, result in enumerate(results[:3], 1):
                    print(f"{i}. {result['alt']} (分数: {result['score']})")
            
            # 更新窗口内容
            if self.current_window and self.current_window.winfo_exists():
                self.update_popup_content(results)
            else:
                self._create_popup(results)
                
        except Exception as e:
            print(f"搜索错误: {e}")
            traceback.print_exc()

    def calculate_match_score(self, name, search_texts):
        """计算匹配分数"""
        try:
            max_score = 0
            name_lower = name.lower()
            
            # 获取拼音
            try:
                from pypinyin import lazy_pinyin
                name_pinyin = ''.join(lazy_pinyin(name_lower))
            except:
                name_pinyin = name_lower
                
            for search_text in search_texts:
                search_lower = search_text.lower()
                
                # 1. 完全匹配
                if name_lower == search_lower:
                    return 100
                    
                # 2. 包含关系
                if search_lower in name_lower:
                    score = 90
                    max_score = max(max_score, score)
                    
                # 3. 拼音匹配
                try:
                    search_pinyin = ''.join(lazy_pinyin(search_lower))
                    if search_pinyin in name_pinyin:
                        print(f"拼音匹配成功: {search_lower} 匹配到 {name_lower}")
                        score = 80
                        max_score = max(max_score, score)
                except:
                    pass
                    
                # 4. 部分匹配
                if any(part in name_lower for part in search_lower.split()):
                    score = 70
                    max_score = max(max_score, score)
                    
                # 5. 模糊匹配
                try:
                    from fuzzywuzzy import fuzz
                    ratio = fuzz.ratio(search_lower, name_lower)
                    if ratio > 60:
                        score = ratio
                        max_score = max(max_score, score)
                except:
                    pass
                    
            return max_score
            
        except Exception as e:
            print(f"计算匹配分数失败: {e}")
            return 0

    def handle_key(self, event):
        """处理按键事件"""
        try:
            if not self.current_window or not self.current_window.winfo_exists():
                return
                
            key = event.name
            print(f"按键: {key}")
            
            # 处理回车键
            if key == 'enter':
                self.search_memes(self.pinyin_buffer)
                return
                
            # 处理退格键
            if key == 'backspace':
                if self.pinyin_buffer:
                    self.pinyin_buffer = self.pinyin_buffer[:-1]
                    print(f"当前拼音缓冲: {self.pinyin_buffer}")
                return
                
            # 处理其他按键
            if len(key) == 1:  # 单个字符
                self.pinyin_buffer += key
                print(f"当前拼音缓冲: {self.pinyin_buffer}")
                
        except Exception as e:
            print(f"按键处理失败: {e}")
            traceback.print_exc()

    def update_search(self, *args):
        """更新搜索结果"""
        try:
            search_text = self.search_var.get().strip()
            if search_text == self.last_search:
                return
                
            self.last_search = search_text
            if len(search_text) >= self.config['features']['search']['min_length']:
                self.search_memes(search_text)
                
        except Exception as e:
            print(f"更新搜索失败: {e}")
            traceback.print_exc()

    def _create_popup(self, memes):
        """创建弹出窗口"""
        try:
            # 创建窗口
            window = tk.Toplevel(self.root)
            window.title("表情包搜索")
            
            # 设置窗口大小和位置
            window_width = self.config['window']['width']
            window_height = self.config['window']['height']
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            window.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
            # 设置窗口属性
            window.attributes('-topmost', True)
            window.attributes('-alpha', self.config['window']['opacity'])
            
            # 创建搜索框
            self.search_entry = ttk.Entry(
                window,
                textvariable=self.search_var,
                font=(self.config['style']['font_family'], 12)
            )
            self.search_entry.pack(fill=tk.X, padx=5, pady=5)
            
            # 创建滚动区域
            canvas = tk.Canvas(window)
            scrollbar = ttk.Scrollbar(window, orient="vertical", command=canvas.yview)
            self.scrollable_frame = ttk.Frame(canvas)
            
            # 配置滚动
            self.scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # 布局
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # 绑定事件
            window.bind('<Escape>', lambda e: self.hide_window())
            window.bind('<Return>', lambda e: self.search_memes(self.search_var.get()))
            window.protocol("WM_DELETE_WINDOW", self.hide_window)
            
            # 保存窗口引用
            self.current_window = window
            
            # 更新内容
            self.update_popup_content(memes)
            
            # 聚焦到搜索框
            self.search_entry.focus_set()
            
        except Exception as e:
            print(f"创建弹窗失败: {e}")
            traceback.print_exc()

    def update_popup_content(self, results):
        """更新弹窗内容"""
        try:
            # 清空现有内容
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
                
            # 显示结果
            for result in results:
                try:
                    # 创建结果框架
                    result_frame = ttk.Frame(self.scrollable_frame, style='Result.TFrame')
                    result_frame.pack(fill=tk.X, padx=5, pady=2)
                    
                    # 创建图片标签
                    url = result['path']
                    if result['name'] in self.photo_references:
                        photo = self.photo_references[result['name']]
                    else:
                        photo = self.create_thumbnail(url)
                        if photo:
                            self.photo_references[result['name']] = photo
                        
                    if photo:
                        label = ttk.Label(result_frame, image=photo)
                        label.image = photo
                        label.pack(side=tk.LEFT, padx=5)
                    
                    # 创建文本标签
                    name_label = ttk.Label(
                        result_frame,
                        text=result['alt'],
                        style='ResultText.TLabel',
                        wraplength=300
                    )
                    name_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                    
                    # 绑定点击事件
                    for widget in (label, name_label, result_frame):
                        widget.bind('<Button-1>', lambda e, u=url: self.send_image(u))
                        widget.bind('<Enter>', lambda e, f=result_frame: self.on_hover(f, True))
                        widget.bind('<Leave>', lambda e, f=result_frame: self.on_hover(f, False))
                    
                except Exception as e:
                    print(f"处理搜索结果项失败: {e}")
                    traceback.print_exc()
                    continue
                    
        except Exception as e:
            print(f"更新弹窗内容失败: {e}")
            traceback.print_exc()

    def show_window(self):
        """显示搜索窗口"""
        try:
            print("呼出搜索窗口")
            if self.current_window and self.current_window.winfo_exists():
                self.current_window.deiconify()
                self.current_window.lift()
                self.search_entry.focus_set()
            else:
                self._create_popup([])
        except Exception as e:
            print(f"显示窗口失败: {e}")
            traceback.print_exc()

    def hide_window(self):
        """隐藏搜索窗口"""
        try:
            if self.current_window and self.current_window.winfo_exists():
                self.current_window.withdraw()
        except Exception as e:
            print(f"隐藏窗口失败: {e}")
            traceback.print_exc()

    def show_toast(self, message, duration=2000):
        """显示提示信息"""
        try:
            self.toast_label.configure(text=message)
            
            if not self.current_window:
                return
                
            window_width = self.current_window.winfo_width()
            window_height = self.current_window.winfo_height()
            toast_width = self.toast_label.winfo_reqwidth()
            toast_height = self.toast_label.winfo_reqheight()
            
            x = (window_width - toast_width) // 2
            y = window_height - toast_height - 20
            
            self.toast_label.place(x=x, y=y)
            
            self.current_window.after(duration, lambda: self.toast_label.place_forget())
            
        except Exception as e:
            print(f"显示提示失败: {e}")
            traceback.print_exc()

    def on_hover(self, frame, enter):
        """处理鼠标悬停效果"""
        try:
            frame.configure(style='Hover.TFrame' if enter else 'Result.TFrame')
        except Exception as e:
            print(f"处理悬停效果失败: {e}")
            traceback.print_exc()

    def register_hotkey(self):
        """注册全局热键"""
        try:
            keyboard.on_press(self.handle_key)
            keyboard.add_hotkey('tab', self.show_window)
            print("热键注册成功")
        except Exception as e:
            print(f"注册热键失败: {e}")
            traceback.print_exc()

    def unregister_hotkey(self):
        """注销全局热键"""
        try:
            keyboard.unhook_all()
            print("热键注销成功")
        except Exception as e:
            print(f"注销热键失败: {e}")
            traceback.print_exc()

    def save_config(self):
        """保存配置到文件"""
        try:
            config_path = self.config_path / 'config.json'
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            print("配置保存成功")
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            traceback.print_exc()
            return False

    def cleanup(self):
        """清理资源"""
        try:
            # 注销热键
            self.unregister_hotkey()
            
            # 保存配置
            self.save_config()
            
            # 清理图片引用
            self.photo_references.clear()
            
            # 销毁窗口
            if self.current_window and self.current_window.winfo_exists():
                self.current_window.destroy()
            
            print("资源清理完成")
            
        except Exception as e:
            print(f"清理资源失败: {e}")
            traceback.print_exc()

    def format_file_size(self, size_in_bytes):
        """格式化文件大小"""
        try:
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_in_bytes < 1024:
                    return f"{size_in_bytes:.2f} {unit}"
                size_in_bytes /= 1024
            return f"{size_in_bytes:.2f} TB"
        except Exception as e:
            print(f"格式化文件大小失败: {e}")
            return "未知大小"

    def get_image_info(self, image_path):
        """获取图片信息"""
        try:
            image = Image.open(image_path)
            info = {
                'format': image.format,
                'size': image.size,
                'mode': image.mode,
                'file_size': self.format_file_size(Path(image_path).stat().st_size)
            }
            return info
        except Exception as e:
            print(f"获取图片信息失败: {e}")
            return None

    def validate_image(self, image_path):
        """验证图片是否有效"""
        try:
            with Image.open(image_path) as img:
                img.verify()
            return True
        except Exception as e:
            print(f"图片验证失败 {image_path}: {e}")
            return False

    def create_directories(self):
        """创建必要的目录结构"""
        try:
            directories = [
                self.images_path,
                self.config_path,
                self.data_path,
                self.images_path / 'favorites',
                self.data_path / 'cache'
            ]
            
            for directory in directories:
                if not directory.exists():
                    directory.mkdir(parents=True)
                    print(f"创建目录: {directory}")
                    
            return True
            
        except Exception as e:
            print(f"创建目录失败: {e}")
            traceback.print_exc()
            return False

    def log_error(self, error_message, exception=None):
        """记录错误日志"""
        try:
            log_path = self.data_path / 'error.log'
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {error_message}\n")
                if exception:
                    f.write(f"异常详情: {str(exception)}\n")
                    f.write(f"堆栈跟踪:\n{traceback.format_exc()}\n")
                f.write("-" * 50 + "\n")
                
        except Exception as e:
            print(f"写入错误日志失败: {e}")
            traceback.print_exc()