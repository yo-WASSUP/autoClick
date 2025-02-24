import win32gui
import win32con
import win32api
import time
import numpy as np
import cv2
from PIL import ImageGrab

class WindowController:
    def __init__(self):
        self.window_handle = None
        
    def find_window(self, window_title):
        """
        查找指定标题的窗口
        """
        self.window_handle = win32gui.FindWindow(None, window_title)
        if self.window_handle == 0:
            return False
        self.set_foreground()
        return True
        
    def get_window_rect(self):
        """
        获取窗口位置和大小
        """
        if not self.window_handle:
            return None
        return win32gui.GetWindowRect(self.window_handle)
        
    def capture_window(self):
        """
        截取窗口画面
        """
        if not self.window_handle:
            return None
            
        left, top, right, bottom = self.get_window_rect()
        screenshot = ImageGrab.grab((left, top, right, bottom))
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
    def click(self, x, y):
        """
        在指定坐标执行点击
        """
        if not self.window_handle:
            return False
            
        # 获取窗口位置
        left, top, _, _ = self.get_window_rect()
        
        # 将相对坐标转换为屏幕绝对坐标
        screen_x = left + x
        screen_y = top + y
        
        # 移动鼠标并点击
        win32api.SetCursorPos((screen_x, screen_y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
        time.sleep(0.1)
        
        return True

    def set_foreground(self):
        """
        将窗口置于最前面
        """
        if not self.window_handle:
            return False
            
        # 如果窗口被最小化，先恢复它
        if win32gui.IsIconic(self.window_handle):
            win32gui.ShowWindow(self.window_handle, win32con.SW_RESTORE)
            
        # 将窗口置于最前面
        win32gui.SetForegroundWindow(self.window_handle)
        return True
