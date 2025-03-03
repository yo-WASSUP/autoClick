import os
import time
import numpy as np
import cv2
import win32gui
import win32con
import win32api
import win32process
import win32com.client
import pywinauto
import ctypes
from ctypes import wintypes
from PIL import ImageGrab

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
        """激活窗口，确保窗口可见并置于前台"""
        if not self.window_handle:
            print("错误: 未找到窗口")
            return False
            
        try:
            # 1. 首先确保窗口未最小化
            placement = win32gui.GetWindowPlacement(self.window_handle)
            if placement[1] == win32con.SW_SHOWMINIMIZED:
                print("窗口已最小化，正在恢复...")
                win32gui.ShowWindow(self.window_handle, win32con.SW_RESTORE)
            else:
                print("窗口未最小化，尝试置于最前")
                try:
                    win32gui.SetWindowPos(
                        self.window_handle, 
                        win32con.HWND_TOPMOST, 
                        0, 0, 0, 0, 
                        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
                    )
                    # 重置为非TOPMOST，避免窗口总是保持在最上面
                    win32gui.SetWindowPos(
                        self.window_handle, 
                        win32con.HWND_NOTOPMOST, 
                        0, 0, 0, 0, 
                        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
                    )
                except Exception as e:
                    print(f"SetWindowPos失败: {str(e)}")
            
            # 让操作系统有时间响应
            time.sleep(0.1)

            # 最后检查窗口状态
            foreground_hwnd = win32gui.GetForegroundWindow()
            is_visible = win32gui.IsWindowVisible(self.window_handle)
            
            if foreground_hwnd == self.window_handle:
                print("窗口成功置为前台")
                return True
            elif is_visible:
                print(f"窗口可见但非前台 (当前前台窗口句柄: {foreground_hwnd})")
                return True
            else:
                print(f"警告: 窗口不可见且未激活 (当前前台窗口句柄: {foreground_hwnd})")
                return False
                
        except Exception as e:
            print(f"激活窗口失败: {str(e)}")
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
            screenshot = ImageGrab.grab(bbox=(left, top, left + width, top + height))
            
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
            
            # 检查窗口是否为Ace云手机
            window_name = win32gui.GetWindowText(self.window_handle)
            is_ace_app = "Ace云手机" in window_name
            
            # 显示点击指示器 (如果已实现)
            self.show_click_indicator(global_x, global_y, duration=0.3)
            
            # 尝试将窗口设置为前台
            if not is_ace_app:
                # 对于普通窗口，必须置为前台后点击
                if not self.set_foreground():
                    print("警告: 无法将窗口设置为前台，点击可能会失败")
                    return False
                time.sleep(0.2)  # 等待窗口获取焦点
            else:
                # 对于Ace云手机，即使窗口不是前台也尝试点击
                foreground_result = self.set_foreground()
                is_visible = win32gui.IsWindowVisible(self.window_handle)
                if not foreground_result and not is_visible:
                    print("错误: Ace云手机窗口不可见，无法进行点击")
                    return False
                else:
                    print("Ace云手机窗口可见，继续进行点击操作")
                    time.sleep(0.1)
            
            # 使用Windows API执行点击
            return self.force_click(global_x, global_y, click_type, 0)
            
        except Exception as e:
            print(f"点击失败: {str(e)}")
            return False
    
    def force_click(self, x, y, click_type='single', move_duration=0):
        """
        强制点击指定位置，绕过一些应用的安全限制
        
        Args:
            x (int): 全局X坐标
            y (int): 全局Y坐标
            click_type (str): 'single', 'double', 或 'right'
            move_duration (float): 鼠标移动动画持续时间
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 判断软件类型，针对不同软件使用不同策略
            window_name = win32gui.GetWindowText(self.window_handle)
            using_direct_message = False
            
            # 对于特定软件使用更强力的方法
            if "Ace云手机" in window_name:
                print("检测到Ace云手机，尝试使用专用方法点击")
                # 使用专门的Ace云手机点击方法
                result = self.click_ace_cloud(x, y, click_type)
                if result:
                    return True
                else:
                    print("专用方法失败，尝试常规方法...")
            
            # 常规方法：使用SendInput模拟鼠标操作
            MOUSEEVENTF_MOVE = 0x0001
            MOUSEEVENTF_LEFTDOWN = 0x0002
            MOUSEEVENTF_LEFTUP = 0x0004
            MOUSEEVENTF_RIGHTDOWN = 0x0008
            MOUSEEVENTF_RIGHTUP = 0x0010
            MOUSEEVENTF_ABSOLUTE = 0x8000
            
            class POINT(ctypes.Structure):
                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
                
            class MOUSEINPUT(ctypes.Structure):
                _fields_ = [
                    ("dx", wintypes.LONG),
                    ("dy", wintypes.LONG),
                    ("mouseData", wintypes.DWORD),
                    ("dwFlags", wintypes.DWORD),
                    ("time", wintypes.DWORD),
                    ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))
                ]
                
            class INPUT(ctypes.Structure):
                _fields_ = [
                    ("type", wintypes.DWORD),
                    ("mi", MOUSEINPUT)
                ]
                
            # 获取鼠标当前位置
            current_position = POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(current_position))
            
            # 计算屏幕尺寸
            screen_width = ctypes.windll.user32.GetSystemMetrics(0)
            screen_height = ctypes.windll.user32.GetSystemMetrics(1)
            
            # 计算绝对坐标 (0-65535范围)
            abs_x = int(65535 * x / screen_width)
            abs_y = int(65535 * y / screen_height)
            
            # 模拟鼠标移动
            if move_duration > 0:
                # 计算步骤
                steps = int(move_duration * 60)  # 60fps
                start_x, start_y = current_position.x, current_position.y
                
                for step in range(1, steps + 1):
                    # 计算当前步骤位置
                    current_x = start_x + int((x - start_x) * step / steps)
                    current_y = start_y + int((y - start_y) * step / steps)
                    
                    # 计算绝对坐标
                    step_abs_x = int(65535 * current_x / screen_width)
                    step_abs_y = int(65535 * current_y / screen_height)
                    
                    # 创建输入事件
                    move_input = INPUT()
                    move_input.type = 0  # INPUT_MOUSE
                    move_input.mi.dx = step_abs_x
                    move_input.mi.dy = step_abs_y
                    move_input.mi.mouseData = 0
                    move_input.mi.dwFlags = MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE
                    move_input.mi.time = 0
                    move_input.mi.dwExtraInfo = ctypes.pointer(wintypes.ULONG(0))
                    
                    # 发送输入
                    ctypes.windll.user32.SendInput(1, ctypes.byref(move_input), ctypes.sizeof(INPUT))
                    
                    # 短暂延迟
                    time.sleep(1 / 60)
            else:
                # 直接移动到目标位置
                move_input = INPUT()
                move_input.type = 0  # INPUT_MOUSE
                move_input.mi.dx = abs_x
                move_input.mi.dy = abs_y
                move_input.mi.mouseData = 0
                move_input.mi.dwFlags = MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE
                move_input.mi.time = 0
                move_input.mi.dwExtraInfo = ctypes.pointer(wintypes.ULONG(0))
                
                # 发送输入
                ctypes.windll.user32.SendInput(1, ctypes.byref(move_input), ctypes.sizeof(INPUT))
            
            # 等待短暂时间，确保鼠标移动完成
            time.sleep(0.05)
            
            # 执行点击
            if click_type in ['single', 'double']:

                # 按下左键
                click_down = INPUT()
                click_down.type = 0  # INPUT_MOUSE
                click_down.mi.dx = abs_x
                click_down.mi.dy = abs_y
                click_down.mi.mouseData = 0
                click_down.mi.dwFlags = MOUSEEVENTF_LEFTDOWN
                click_down.mi.time = 0
                click_down.mi.dwExtraInfo = ctypes.pointer(wintypes.ULONG(0))
                
                # 发送按下输入
                ctypes.windll.user32.SendInput(1, ctypes.byref(click_down), ctypes.sizeof(INPUT))
                
                # 等待短暂时间
                time.sleep(0.05)
                
                # 释放左键
                click_up = INPUT()
                click_up.type = 0  # INPUT_MOUSE
                click_up.mi.dx = abs_x
                click_up.mi.dy = abs_y
                click_up.mi.mouseData = 0
                click_up.mi.dwFlags = MOUSEEVENTF_LEFTUP
                click_up.mi.time = 0
                click_up.mi.dwExtraInfo = ctypes.pointer(wintypes.ULONG(0))
                
                # 发送释放输入
                ctypes.windll.user32.SendInput(1, ctypes.byref(click_up), ctypes.sizeof(INPUT))
                
                # 如果是双击，执行第二次点击
                if click_type == 'double':
                    time.sleep(0.1)  # 双击间隔
                    
                    # 再次按下左键
                    ctypes.windll.user32.SendInput(1, ctypes.byref(click_down), ctypes.sizeof(INPUT))
                    
                    # 等待短暂时间
                    time.sleep(0.05)
                    
                    # 再次释放左键
                    ctypes.windll.user32.SendInput(1, ctypes.byref(click_up), ctypes.sizeof(INPUT))
                    
            elif click_type == 'right':
                # 右键点击
                
                # 按下右键
                click_down = INPUT()
                click_down.type = 0  # INPUT_MOUSE
                click_down.mi.dx = abs_x
                click_down.mi.dy = abs_y
                click_down.mi.mouseData = 0
                click_down.mi.dwFlags = MOUSEEVENTF_RIGHTDOWN
                click_down.mi.time = 0
                click_down.mi.dwExtraInfo = ctypes.pointer(wintypes.ULONG(0))
                
                # 发送按下输入
                ctypes.windll.user32.SendInput(1, ctypes.byref(click_down), ctypes.sizeof(INPUT))
                
                # 等待短暂时间
                time.sleep(0.05)
                
                # 释放右键
                click_up = INPUT()
                click_up.type = 0  # INPUT_MOUSE
                click_up.mi.dx = abs_x
                click_up.mi.dy = abs_y
                click_up.mi.mouseData = 0
                click_up.mi.dwFlags = MOUSEEVENTF_RIGHTUP
                click_up.mi.time = 0
                click_up.mi.dwExtraInfo = ctypes.pointer(wintypes.ULONG(0))
                
                # 发送释放输入
                ctypes.windll.user32.SendInput(1, ctypes.byref(click_up), ctypes.sizeof(INPUT))
                       
            print(f"使用Windows API强制点击位置 ({x}, {y}), 类型: {click_type}")
            return True
            
        except Exception as e:
            print(f"强制点击失败: {str(e)}")
            return False
    
    def click_ace_cloud(self, x, y, click_type='single'):
        """
        在Ace云手机窗口中使用DD键鼠驱动程序点击指定坐标
        
        参数:
            x: 屏幕x坐标
            y: 屏幕y坐标
            click_type: 点击类型，支持'single'（单击）、'double'（双击）和'right'（右键）
        
        返回:
            bool: 点击是否成功
        """
        success = False
        print(f"Ace云手机点击: ({x}, {y}), 类型: {click_type}")
        
        # 尝试激活窗口
        try:
            self.activate_window()
        except Exception as e:
            print(f"无法激活Ace云手机窗口: {str(e)}")
        
        # 使用DD驱动程序执行点击
        try:
            # 加载DD驱动DLL
            try:
                # 首先尝试通过相对路径加载
                dd_dll = ctypes.windll.LoadLibrary(r'dd43390.dll')
                print("成功加载DD驱动DLL（相对路径）")
            except:
                print(f"无法加载DD驱动DLL: {str(e)}")
                return False
            
            # 初始化DD驱动
            st = dd_dll.DD_btn(0)
            if st != 1:
                print(f"DD驱动初始化失败，状态码: {st}")
                return False
            
            print("DD驱动初始化成功")
            
            # 移动鼠标到目标位置
            print(f"移动鼠标到: ({x}, {y})")
            dd_dll.DD_mov(x, y)
            time.sleep(0.1)  # 短暂延迟确保移动完成
            
            # 根据点击类型执行点击
            if click_type == 'single':
                # 单击左键
                print("执行左键单击")
                dd_dll.DD_btn(1)  # 左键按下
                time.sleep(0.05)
                dd_dll.DD_btn(2)  # 左键释放
            elif click_type == 'double':
                # 双击左键
                print("执行左键双击")
                dd_dll.DD_btn(1)  # 左键按下
                time.sleep(0.05)
                dd_dll.DD_btn(2)  # 左键释放
                time.sleep(0.05)
                dd_dll.DD_btn(1)  # 左键按下
                time.sleep(0.05)
                dd_dll.DD_btn(2)  # 左键释放
            elif click_type == 'right':
                # 右键单击
                print("执行右键单击")
                dd_dll.DD_btn(4)  # 右键按下
                time.sleep(0.05)
                dd_dll.DD_btn(8)  # 右键释放
            
            print("DD驱动点击执行成功")
            success = True
        except Exception as e:
            print(f"使用DD驱动点击失败: {str(e)}")
        
        return success

    def show_click_indicator(self, x, y, duration=0.3, color=(255, 0, 0)):
        """
        在指定位置显示临时圆圈作为点击指示
        
        Args:
            x (int): 屏幕X坐标
            y (int): 屏幕Y坐标
            duration (float): 显示持续时间，单位秒
            color (tuple): 圆圈颜色，RGB格式
        """
        try:
            # 边界检查，确保坐标不为负
            if x < 0 or y < 0:
                print(f"坐标 ({x}, {y}) 超出屏幕范围，无法显示指示器")
                return False
                
            import threading
            import time
            import win32gui
            import win32con
            import win32api
            
            # 打印点击位置
            print(f"在位置 ({x}, {y}) 显示点击指示器")
            
            # 在单独的线程中执行，避免阻塞主线程
            def show_indicator():
                # 获取桌面DC
                hdc = win32gui.GetDC(0)
                
                # 创建画笔
                hpen = win32gui.CreatePen(win32con.PS_SOLID, 2, win32api.RGB(*color))
                old_pen = win32gui.SelectObject(hdc, hpen)
                
                # 创建空画刷 (透明填充)
                hbrush = win32gui.GetStockObject(win32con.NULL_BRUSH)
                old_brush = win32gui.SelectObject(hdc, hbrush)
                
                # 绘制圆圈
                win32gui.Ellipse(hdc, x-10, y-10, x+10, y+10)
                
                # 恢复画笔和画刷
                win32gui.SelectObject(hdc, old_pen)
                win32gui.SelectObject(hdc, old_brush)
                
                # 释放资源
                win32gui.DeleteObject(hpen)
                win32gui.ReleaseDC(0, hdc)
                
                # 等待指定时间
                time.sleep(duration)
                
                # 重绘桌面 (圆圈将会消失)
                win32gui.RedrawWindow(0, None, None, win32con.RDW_INVALIDATE | win32con.RDW_ERASE)
            
            # 启动线程
            indicator_thread = threading.Thread(target=show_indicator)
            indicator_thread.daemon = True
            indicator_thread.start()
            
            return True
            
        except Exception as e:
            print(f"显示点击指示器失败: {str(e)}")
            return False
