import sys
import traceback
from src.meme_selector import MemeSelector
from src.status_window import StatusWindow
import threading
import keyboard

def main():
    try:
        # 创建选择器
        selector = MemeSelector()
        
        # 创建状态窗口
        status_window = StatusWindow()
        
        # 设置状态窗口的回调
        def on_switch_change(state):
            selector.set_running_state(state)
        status_window.set_callback(on_switch_change)
        
        # 创建主窗口
        selector.root = status_window.root
        
        # 启动检查弹窗队列的定时器
        selector.root.after(100, selector.check_popup_queue)
        
        # 启动键盘监听线程
        keyboard_thread = threading.Thread(
            target=lambda: keyboard.on_press(selector.on_key),
            daemon=True
        )
        keyboard_thread.start()
        
        # 运行主循环（在主线程中）
        status_window.run()
        
    except Exception as e:
        print(f"发生错误: {e}")
        traceback.print_exc()
        try:
            input("按回车键退出...")
        except:
            pass
        finally:
            sys.exit(1)

if __name__ == "__main__":
    main() 