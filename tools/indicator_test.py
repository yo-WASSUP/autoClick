import time
import win32gui
from window_controller import WindowController

def main():
    """测试点击指示器功能"""
    print("点击指示器测试")
    print("=" * 50)
    
    # 创建WindowController实例
    controller = WindowController()
    
    # 查找Ace云手机窗口
    def enum_windows_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            if window_text and "Ace云手机" in window_text:
                windows.append((hwnd, window_text))
        return True
    
    target_windows = []
    win32gui.EnumWindows(enum_windows_callback, target_windows)
    
    if target_windows:
        hwnd, title = target_windows[0]
        print(f"找到目标窗口: {title}, 句柄: {hwnd}")
        controller.window_handle = hwnd
        
        # 获取窗口位置
        rect = win32gui.GetWindowRect(hwnd)
        print(f"窗口位置: {rect}")
        
        # 计算测试点击位置 (窗口中心)
        center_x = (rect[0] + rect[2]) // 2
        center_y = (rect[1] + rect[3]) // 2
    else:
        print("未找到Ace云手机窗口，将在屏幕上测试点击指示器")
        # 获取屏幕分辨率
        import ctypes
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        
        # 使用屏幕中心
        center_x = screen_width // 2
        center_y = screen_height // 2
        
        print(f"屏幕尺寸: {screen_width}x{screen_height}")
        print(f"屏幕中心点: ({center_x}, {center_y})")
    
    print(f"将在5秒后开始测试点击指示器...")
    time.sleep(5)
    
    # 在中心点点击
    print(f"测试点1 - 中心: ({center_x}, {center_y})")
    # 先显示指示器
    controller.show_click_indicator(center_x, center_y, duration=1.0)
    # 然后执行实际点击
    controller.force_click(center_x, center_y)
    time.sleep(1.5)
    
    # 在左上角点击
    left_x = 360
    left_y = 220
    print(f"测试点2 - 左上: ({left_x}, {left_y})")
    controller.show_click_indicator(left_x, left_y, duration=1.0, color=(0, 255, 0))
    controller.force_click(left_x, left_y)
    time.sleep(1.5)
    
    # 在右下角点击
    right_x = center_x + 200
    right_y = center_y + 200
    print(f"测试点3 - 右下: ({right_x}, {right_y})")
    controller.show_click_indicator(right_x, right_y, duration=1.0, color=(0, 0, 255))
    controller.force_click(right_x, right_y)
    
    print("测试完成")

if __name__ == "__main__":
    main()
