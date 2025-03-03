import time
import win32gui
import win32con
from window_controller import WindowController

def main():
    """
    测试窗口激活函数，尤其是对最小化窗口的处理
    """
    print("窗口激活功能测试")
    print("=" * 50)
    
    # 创建WindowController实例
    controller = WindowController()
    
    # 查找窗口
    def enum_windows_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            if window_text:
                windows.append((hwnd, window_text))
        return True
    
    # 列出所有可见窗口
    all_windows = []
    win32gui.EnumWindows(enum_windows_callback, all_windows)
    
    print("可见窗口列表:")
    for i, (hwnd, title) in enumerate(all_windows):
        # 只显示有标题的窗口
        if title.strip():
            print(f"{i+1}. [{hwnd}] {title}")
    
    # 用户选择窗口
    try:
        choice = int(input("\n请选择要测试的窗口编号 (1-N): "))
        if choice < 1 or choice > len(all_windows):
            print("无效的选择")
            return
            
        selected_hwnd, selected_title = all_windows[choice-1]
        print(f"\n已选择窗口: {selected_title} (句柄: {selected_hwnd})")
        
        controller.window_handle = selected_hwnd
        
        # 显示当前窗口状态
        placement = win32gui.GetWindowPlacement(selected_hwnd)
        state = "最小化" if placement[1] == win32con.SW_SHOWMINIMIZED else "正常"
        print(f"窗口当前状态: {state}")
        
        # 进行激活测试
        input("按Enter键测试窗口激活...")
        print("正在激活窗口...")
        result = controller.set_foreground()
        print(f"激活结果: {'成功' if result else '失败'}")
           
    except Exception as e:
        print(f"测试过程中出错: {str(e)}")

if __name__ == "__main__":
    main()
