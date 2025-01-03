import tkinter as tk
import keyboard
import sys
import traceback
from pathlib import Path
from src.meme_selector import MemeSelector

class Application:
    """应用主类"""
    
    def __init__(self):
        """初始化应用"""
        try:
            print("初始化应用...")
            
            # 创建主窗口
            self.root = tk.Tk()
            self.root.withdraw()  # 隐藏主窗口但保持运行
            
            # 设置主窗口属性
            self.root.attributes('-alpha', 0)  # 完全透明
            self.root.attributes('-topmost', True)  # 保持在最上层
            self.root.overrideredirect(True)  # 无边框
            
            # 初始化表情包选择器
            self.selector = MemeSelector(self.root)
            
            # 注册热键
            self.register_hotkeys()
            
            # 设置定期更新
            self.setup_update_loop()
            
            print("应用初始化完成")
            
        except Exception as e:
            print(f"应用初始化失败: {e}")
            traceback.print_exc()
            sys.exit(1)

    def register_hotkeys(self):
        """注册热键"""
        try:
            # Tab 键呼出搜索窗口
            keyboard.add_hotkey('tab', self.selector.show_window)
            # Esc 键隐藏窗口
            keyboard.add_hotkey('esc', self.selector.hide_window)
            print("热键注册成功")
        except Exception as e:
            print(f"注册热键失败: {e}")
            traceback.print_exc()

    def setup_update_loop(self):
        """设置更新循环"""
        def update():
            try:
                self.root.update()
                self.root.after(10, update)  # 每10ms更新一次
            except Exception as e:
                print(f"更新循环错误: {e}")
                traceback.print_exc()
                self.cleanup()
                sys.exit(1)
        update()

    def run(self):
        """运行应用"""
        try:
            print("\n=== 表情包助手已启动 ===")
            print("按Tab键呼出搜索窗口")
            print("按ESC键隐藏窗口")
            print("按Ctrl+C退出程序\n")
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n接收到退出信号")
        except Exception as e:
            print(f"应用运行失败: {e}")
            traceback.print_exc()
        finally:
            self.cleanup()

    def cleanup(self):
        """清理资源"""
        try:
            print("\n开始清理资源...")
            
            # 清理选择器资源
            if hasattr(self, 'selector'):
                self.selector.cleanup()
            
            # 注销热键
            keyboard.unhook_all()
            
            # 销毁主窗口
            if hasattr(self, 'root'):
                self.root.destroy()
                
            print("资源清理完成")
            
        except Exception as e:
            print(f"清理资源失败: {e}")
            traceback.print_exc()

def check_environment():
    """检查运行环境"""
    try:
        # 检查Python版本
        if sys.version_info < (3, 7):
            print("错误: 需要 Python 3.7 或更高版本")
            return False
            
        # 检查必要的目录
        base_path = Path(__file__).parent
        required_dirs = [
            base_path / 'images',
            base_path / 'config',
            base_path / 'data'
        ]
        
        for dir_path in required_dirs:
            if not dir_path.exists():
                print(f"创建目录: {dir_path}")
                dir_path.mkdir(parents=True, exist_ok=True)
                
        return True
        
    except Exception as e:
        print(f"环境检查失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主函数"""
    try:
        # 检查环境
        if not check_environment():
            return 1
            
        # 创建并运行应用
        app = Application()
        app.run()
        
        return 0
        
    except Exception as e:
        print(f"程序运行失败: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())