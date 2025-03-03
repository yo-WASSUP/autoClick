import win32gui
import time
import ctypes
import win32con
import sys
from ctypes import wintypes

# 定义SendInput相关的结构体和常量
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_ABSOLUTE = 0x8000

# 屏幕分辨率常量
SCREEN_WIDTH = ctypes.windll.user32.GetSystemMetrics(0)
SCREEN_HEIGHT = ctypes.windll.user32.GetSystemMetrics(1)
SCREEN_RESOLUTION = SCREEN_WIDTH * 65536 // SCREEN_WIDTH, SCREEN_HEIGHT * 65536 // SCREEN_HEIGHT

# 定义输入结构体
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
    class _INPUT(ctypes.Union):
        _fields_ = [
            ("mi", MOUSEINPUT),
            # 可以添加其他输入类型如键盘、硬件
        ]
    _anonymous_ = ("_input",)
    _fields_ = [
        ("type", wintypes.DWORD),
        ("_input", _INPUT)
    ]

def send_mouse_input(flags, x=0, y=0, data=0):
    """发送鼠标输入事件"""
    # 转换坐标到绝对坐标系
    if flags & MOUSEEVENTF_ABSOLUTE:
        x = int(x * 65536 // SCREEN_WIDTH)
        y = int(y * 65536 // SCREEN_HEIGHT)
    
    # 准备INPUT结构体
    extra = ctypes.pointer(wintypes.ULONG(0))
    ii = INPUT(
        type=1,  # INPUT_MOUSE
        mi=MOUSEINPUT(dx=x, dy=y, mouseData=data, dwFlags=flags, time=0, dwExtraInfo=extra)
    )
    
    # 发送输入
    ctypes.windll.user32.SendInput(1, ctypes.byref(ii), ctypes.sizeof(ii))

def move_mouse_driver(x, y):
    """使用驱动级API移动鼠标到绝对位置"""
    send_mouse_input(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, x, y)

def click_mouse_driver(button='left'):
    """使用驱动级API点击鼠标"""
    if button == 'left':
        send_mouse_input(MOUSEEVENTF_LEFTDOWN)
        time.sleep(0.05)
        send_mouse_input(MOUSEEVENTF_LEFTUP)
    elif button == 'right':
        send_mouse_input(MOUSEEVENTF_RIGHTDOWN)
        time.sleep(0.05)
        send_mouse_input(MOUSEEVENTF_RIGHTUP)
    elif button == 'middle':
        send_mouse_input(MOUSEEVENTF_MIDDLEDOWN)
        time.sleep(0.05)
        send_mouse_input(MOUSEEVENTF_MIDDLEUP)

def test_clicks(coordinates=None):
    """
    使用驱动级API测试鼠标点击功能，在指定坐标上进行点击
    
    参数:
        coordinates: 要点击的坐标列表，格式为[(x1, y1), (x2, y2), (x3, y3)]
    """
    print("开始驱动级鼠标点击测试...")
    
    # 默认测试坐标
    if coordinates is None:
        coordinates = [
            (500, 300),  # 点击位置1
            (800, 400),  # 点击位置2
            (1000, 500)  # 点击位置3
        ]
    
    # 逐个位置进行点击测试
    for i, (x, y) in enumerate(coordinates):
        print(f"\n测试点击位置 {i+1}: ({x}, {y})")
        
        # 慢速移动鼠标到目标位置（可视化过程）
        current_x, current_y = win32gui.GetCursorPos()
        steps = 20  # 移动步骤数
        
        for step in range(1, steps + 1):
            # 计算当前步骤的位置
            step_x = current_x + (x - current_x) * step // steps
            step_y = current_y + (y - current_y) * step // steps
            
            # 使用驱动级API移动鼠标
            move_mouse_driver(step_x, step_y)
            time.sleep(0.05)  # 短暂延迟使移动可见
        
        # 确保最终位置准确
        move_mouse_driver(x, y)
        print(f"鼠标已移动到 ({x}, {y})")
        time.sleep(0.5)
        
        # 执行点击
        print("执行驱动级点击...")
        click_mouse_driver('left')
        
        # 再尝试一种低级别点击方法（模拟硬件级别点击）
        print("尝试额外的低级点击方式...")
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.05)
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        
        # 等待观察
        print("查看是否有点击效果...")
        time.sleep(2)

    print("\n测试完成！")

if __name__ == "__main__":
    coordinates = [
        (500, 500),  # 第一个点击位置
        (500, 600),  # 第二个点击位置
        (500, 700)  # 第三个点击位置
    ]
    test_clicks(coordinates)
