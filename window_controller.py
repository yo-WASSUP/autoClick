import time
import numpy as np
import cv2
import win32gui
import win32con
import win32com.client
import os
import ctypes
from ctypes import wintypes

class WindowController:
    def __init__(self):
        self.window_handle = None
        self.window_title = None
        
    def find_window(self, window_title):
        """
        查找指定标题的窗口
        """
        try:
            # 使用win32gui查找窗口
            def callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd) and window_title.lower() in win32gui.GetWindowText(hwnd).lower():
                    windows.append(hwnd)
                return True
            
            windows = []
            win32gui.EnumWindows(callback, windows)
            
            if not windows:
                print(f"未找到标题为 '{window_title}' 的窗口")
                return False
                
            self.window_handle = windows[0]
            self.window_title = window_title
            
            # 激活窗口
            self.set_foreground()
            return True
        except Exception as e:
            print(f"查找窗口时出错: {str(e)}")
            return False
    
    def set_foreground(self):
        """将窗口设置为前台窗口"""
        if not self.window_handle:
            print("错误: 未找到窗口")
            return False
        try:
            win32gui.SetForegroundWindow(self.window_handle)
            print("使用SetForegroundWindow成功激活窗口")
            return True
        except Exception as e:
            print(f"SetForegroundWindow失败: {str(e)}")
            return False
    
    def get_window_rect(self):
        """
        获取窗口的位置和大小
        """
        if not self.window_handle:
            return None
            
        try:
            # 使用win32gui直接获取窗口位置
            hwnd = self.window_handle
            
            try:
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                width = right - left
                height = bottom - top
                
                # 检查窗口是否在屏幕外或尺寸是否为0
                if left < -10000 or top < -10000 or width <= 0 or height <= 0:
                    print("警告: 窗口可能不可见或被最小化")
                    self.set_foreground()  # 尝试再次激活窗口
                    time.sleep(0.5)
                    
                    # 再次尝试获取窗口位置
                    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                    width = right - left
                    height = bottom - top
                    
                    # 再次检查窗口尺寸
                    if width <= 0 or height <= 0:
                        print("错误: 无法获取有效的窗口尺寸")
                        return None
                
                return (left, top, width, height)
                
            except Exception as e:
                print(f"GetWindowRect失败: {str(e)}")
                return None
                
        except Exception as e:
            print(f"获取窗口位置时出错: {str(e)}")
            return None
    
    def capture_window(self):
        """
        捕获窗口截图
        
        返回:
            tuple: (截图, 窗口左上角坐标) 或 None (如果失败)
        """
        if not self.window_handle:
            print("错误: 未找到窗口")
            return None
        
        try:
            # 获取窗口位置
            rect = self.get_window_rect()
            if not rect:
                print("错误: 无法获取窗口位置")
                return None
                
            left, top, width, height = rect
            
            # 使用PIL截取屏幕
            import PIL.ImageGrab
            screenshot = PIL.ImageGrab.grab(bbox=(left, top, left + width, top + height))
            
            # 转换为OpenCV格式
            screenshot_np = np.array(screenshot)
            screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            
            # 保存截图
            screenshot_dir = "screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)
            screenshot_path = os.path.join(screenshot_dir, f"screenshot.png")
            cv2.imwrite(screenshot_path, screenshot_cv)
            
            return (screenshot_cv, (left, top))
            
        except Exception as e:
            print(f"捕获窗口截图失败: {str(e)}")
            return None
    
    def click(self, x, y, click_type='single'):
        """
        点击窗口内的指定位置
        
        参数:
            x (int): 窗口内的X坐标
            y (int): 窗口内的Y坐标
            click_type (str): 点击类型，'single'表示单击，'double'表示双击，'right'表示右键单击
            
        返回:
            bool: 点击操作是否成功
        """
        if not self.window_handle:
            print("错误: 未找到窗口")
            return False
            
        try:
            # 获取窗口位置
            rect = self.get_window_rect()
            if not rect:
                print("错误: 无法获取窗口位置，点击失败")
                return False
                
            left, top, width, height = rect
            
            # 计算全局坐标
            global_x = left + x
            global_y = top + y
            
            # 可选：截图并可视化点击位置
            screenshot = self.capture_window()
            if screenshot is not None:
                # 创建可视化图像
                visual_img = screenshot[0].copy()
                
                # 在点击位置绘制圆圈
                cv2.circle(visual_img, (x, y), 20, (0, 255, 0), 2)  # 绿色圆圈
                cv2.circle(visual_img, (x, y), 5, (0, 0, 255), -1)  # 红色圆点
                
                # 保存可视化图像
                cv2.imwrite("click_target.png", visual_img)
                print("点击目标可视化图像保存到: click_target.png")
            
            # 始终将窗口设置为前台，无论force_focus参数如何设置
            self.set_foreground()
            time.sleep(0.2)  # 等待窗口获取焦点
            
            # 使用Windows API执行点击
            return self.force_click(global_x, global_y, click_type, 0)
            
        except Exception as e:
            print(f"点击失败: {str(e)}")
            return False
    
    def force_click(self, x, y, click_type='single', move_duration=0.3):
        """
        使用Windows API强制点击指定位置，无视窗口焦点
        
        参数:
            x (int): 全局X坐标
            y (int): 全局Y坐标
            click_type (str): 点击类型，'single'表示单击，'double'表示双击，'right'表示右键单击
            move_duration (float): 鼠标移动动画的持续时间，设为0则立即移动
            
        返回:
            bool: 点击操作是否成功
        """
        try:
            # 确保窗口置顶
            if self.window_handle:
                self.set_foreground()
                time.sleep(0.2)  # 等待窗口获取焦点
            
            user32 = ctypes.WinDLL('user32', use_last_error=True)
            
            # 定义必要的结构和常量
            INPUT_MOUSE = 0
            MOUSEEVENTF_MOVE = 0x0001
            MOUSEEVENTF_LEFTDOWN = 0x0002
            MOUSEEVENTF_LEFTUP = 0x0004
            MOUSEEVENTF_RIGHTDOWN = 0x0008
            MOUSEEVENTF_RIGHTUP = 0x0010
            MOUSEEVENTF_ABSOLUTE = 0x8000
            MOUSEEVENTF_MOVE_ABSOLUTE = MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE
            
            # 获取屏幕分辨率
            SCREEN_WIDTH = ctypes.windll.user32.GetSystemMetrics(0)
            SCREEN_HEIGHT = ctypes.windll.user32.GetSystemMetrics(1)
            
            class MOUSEINPUT(ctypes.Structure):
                _fields_ = [("dx", wintypes.LONG),
                           ("dy", wintypes.LONG),
                           ("mouseData", wintypes.DWORD),
                           ("dwFlags", wintypes.DWORD),
                           ("time", wintypes.DWORD),
                           ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))]
            
            class INPUT(ctypes.Structure):
                _fields_ = [("type", wintypes.DWORD),
                           ("mi", MOUSEINPUT)]
            
            # 获取当前鼠标位置
            class POINT(ctypes.Structure):
                _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]
                
            pt = POINT()
            user32.GetCursorPos(ctypes.byref(pt))
            start_x, start_y = pt.x, pt.y
            
            print(f"当前鼠标位置: ({start_x}, {start_y})")
            print(f"目标点击位置: ({x}, {y})")
            
            # 确保坐标在屏幕范围内
            x = max(0, min(x, SCREEN_WIDTH - 1))
            y = max(0, min(y, SCREEN_HEIGHT - 1))
            
            # 如果需要移动动画，则分步移动鼠标
            if move_duration > 0:
                # 计算需要移动的步数
                steps = int(move_duration * 60)  # 60fps
                steps = max(10, min(100, steps))  # 确保步数在合理范围内
                
                # 计算每一步的移动距离
                dx = (x - start_x) / steps
                dy = (y - start_y) / steps
                
                # 分步移动鼠标
                for i in range(steps):
                    # 计算当前步骤的位置
                    current_x = int(start_x + dx * (i + 1))
                    current_y = int(start_y + dy * (i + 1))
                    
                    # 将坐标转换为Windows API所需的格式 (0-65535范围)
                    normalized_x = int(65535 * current_x / SCREEN_WIDTH)
                    normalized_y = int(65535 * current_y / SCREEN_HEIGHT)
                    
                    # 创建鼠标移动输入
                    move_input = INPUT(type=INPUT_MOUSE,
                                      mi=MOUSEINPUT(dx=normalized_x, dy=normalized_y,
                                                   mouseData=0,
                                                   dwFlags=MOUSEEVENTF_MOVE_ABSOLUTE,
                                                   time=0,
                                                   dwExtraInfo=None))
                    
                    # 发送移动事件
                    user32.SendInput(1, ctypes.byref(move_input), ctypes.sizeof(INPUT))
                    
                    # 短暂延迟，创建平滑的动画效果
                    time.sleep(move_duration / steps)
            else:
                # 直接移动到目标位置
                # 将坐标转换为Windows API所需的格式 (0-65535范围)
                normalized_x = int(65535 * x / SCREEN_WIDTH)
                normalized_y = int(65535 * y / SCREEN_HEIGHT)
                
                # 创建鼠标移动输入
                move_input = INPUT(type=INPUT_MOUSE,
                                  mi=MOUSEINPUT(dx=normalized_x, dy=normalized_y,
                                               mouseData=0,
                                               dwFlags=MOUSEEVENTF_MOVE_ABSOLUTE,
                                               time=0,
                                               dwExtraInfo=None))
                
                # 发送移动事件
                user32.SendInput(1, ctypes.byref(move_input), ctypes.sizeof(INPUT))
                time.sleep(0.05)  # 短暂延迟确保鼠标已移动到位
            
            # 根据点击类型执行不同的点击操作
            if click_type == 'single':
                # 左键按下
                down_input = INPUT(type=INPUT_MOUSE,
                                  mi=MOUSEINPUT(dx=0, dy=0,
                                               mouseData=0,
                                               dwFlags=MOUSEEVENTF_LEFTDOWN,
                                               time=0,
                                               dwExtraInfo=None))
                
                # 左键释放
                up_input = INPUT(type=INPUT_MOUSE,
                                mi=MOUSEINPUT(dx=0, dy=0,
                                             mouseData=0,
                                             dwFlags=MOUSEEVENTF_LEFTUP,
                                             time=0,
                                             dwExtraInfo=None))
                
                # 发送点击事件
                user32.SendInput(1, ctypes.byref(down_input), ctypes.sizeof(INPUT))
                time.sleep(0.05)  # 短暂延迟模拟真实点击
                user32.SendInput(1, ctypes.byref(up_input), ctypes.sizeof(INPUT))
                
            elif click_type == 'double':
                for _ in range(2):
                    # 左键按下
                    down_input = INPUT(type=INPUT_MOUSE,
                                      mi=MOUSEINPUT(dx=0, dy=0,
                                                   mouseData=0,
                                                   dwFlags=MOUSEEVENTF_LEFTDOWN,
                                                   time=0,
                                                   dwExtraInfo=None))
                    
                    # 左键释放
                    up_input = INPUT(type=INPUT_MOUSE,
                                    mi=MOUSEINPUT(dx=0, dy=0,
                                                 mouseData=0,
                                                 dwFlags=MOUSEEVENTF_LEFTUP,
                                                 time=0,
                                                 dwExtraInfo=None))
                    
                    # 发送点击事件
                    user32.SendInput(1, ctypes.byref(down_input), ctypes.sizeof(INPUT))
                    time.sleep(0.05)  # 短暂延迟模拟真实点击
                    user32.SendInput(1, ctypes.byref(up_input), ctypes.sizeof(INPUT))
                    time.sleep(0.1)  # 两次点击之间的延迟
                    
            elif click_type == 'right':
                # 右键按下
                down_input = INPUT(type=INPUT_MOUSE,
                                  mi=MOUSEINPUT(dx=0, dy=0,
                                               mouseData=0,
                                               dwFlags=MOUSEEVENTF_RIGHTDOWN,
                                               time=0,
                                               dwExtraInfo=None))
                
                # 右键释放
                up_input = INPUT(type=INPUT_MOUSE,
                                mi=MOUSEINPUT(dx=0, dy=0,
                                             mouseData=0,
                                             dwFlags=MOUSEEVENTF_RIGHTUP,
                                             time=0,
                                             dwExtraInfo=None))
                
                # 发送点击事件
                user32.SendInput(1, ctypes.byref(down_input), ctypes.sizeof(INPUT))
                time.sleep(0.05)  # 短暂延迟模拟真实点击
                user32.SendInput(1, ctypes.byref(up_input), ctypes.sizeof(INPUT))
                       
            print(f"使用Windows API强制点击位置 ({x}, {y}), 类型: {click_type}")
            return True
            
        except Exception as e:
            print(f"强制点击失败: {e}")
            return False
