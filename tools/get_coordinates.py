import cv2
import numpy as np
import pyautogui
import time
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import sys

# 设置UTF-8编码
if sys.platform.startswith('win'):
    # Windows平台
    import ctypes
    # 设置控制台代码页为UTF-8
    ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    # 设置字体
    os.environ['PYTHONIOENCODING'] = 'utf-8'

class CoordinateGetter:
    def __init__(self):
        self.image = None
        self.image_path = None
        self.window_name = "点击获取坐标 (按ESC退出，按S保存)"
        self.coordinates = []
        
    def select_image(self):
        """
        选择图片文件或截取当前屏幕
        """
        root = tk.Tk()
        root.withdraw()
        
        # 询问用户是否要截取当前屏幕
        screen_capture = messagebox.askyesno("选择", "是否截取当前屏幕？\n选择'是'截取屏幕，选择'否'打开图片文件")
        
        if screen_capture:
            # 给用户时间切换到目标窗口
            messagebox.showinfo("提示", "将在3秒后截取屏幕，请切换到目标窗口")
            root.destroy()
            time.sleep(3)
            
            # 截取屏幕
            screenshot = pyautogui.screenshot()
            self.image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            self.image_path = "screen_capture.png"
            cv2.imwrite(self.image_path, self.image)
            print(f"已保存屏幕截图到: {os.path.abspath(self.image_path)}")
        else:
            # 打开文件选择对话框
            self.image_path = filedialog.askopenfilename(
                title="选择图片",
                filetypes=[("图片文件", "*.png;*.jpg;*.jpeg;*.bmp")]
            )
            root.destroy()
            
            if not self.image_path:
                print("未选择图片，程序退出")
                return False
                
            # 读取图片
            self.image = cv2.imread(self.image_path)
            
        if self.image is None:
            print(f"无法读取图片: {self.image_path}")
            return False
            
        return True
        
    def mouse_callback(self, event, x, y, flags, param):
        """
        鼠标事件回调函数
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            # 记录坐标
            self.coordinates.append((x, y))
            
            # 在图片上标记点击位置
            img_copy = self.image.copy()
            for i, (cx, cy) in enumerate(self.coordinates):
                # 画圆圈
                cv2.circle(img_copy, (cx, cy), 5, (0, 0, 255), -1)
                # 显示坐标和序号
                cv2.putText(img_copy, f"{i+1}: ({cx}, {cy})", (cx + 10, cy), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            
            # 更新显示
            cv2.imshow(self.window_name, img_copy)
            
            # 打印坐标
            print(f"点击位置 {len(self.coordinates)}: ({x}, {y})")
    
    def save_coordinates(self):
        """
        保存坐标到文件
        """
        if not self.coordinates:
            print("没有坐标可保存")
            return
        
        # 创建Excel示例配置
        excel_example = "coordinates\excel_example.txt"
        with open(excel_example, 'w') as f:
            f.write("# Excel配置示例\n")
            f.write("type, target, click_type, delay, shift\n")
            for i, (x, y) in enumerate(self.coordinates):
                f.write(f"fixed, {x},{y}, single, 1.0, 0\n")
                
        print(f"Excel配置示例已保存到: {os.path.abspath(excel_example)}")
    
    def run(self):
        """
        运行坐标获取器
        """
        # 选择图片
        if not self.select_image():
            return
            
        # 创建窗口并设置鼠标回调
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        
        # 显示图片
        cv2.imshow(self.window_name, self.image)
        
        # 等待按键
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC键退出
                break
            elif key == ord('s'):  # S键保存
                self.save_coordinates()
        
        # 关闭窗口
        cv2.destroyAllWindows()
        
        # 如果有坐标但未保存，询问是否保存
        if self.coordinates and key == 27:
            root = tk.Tk()
            root.withdraw()
            if messagebox.askyesno("保存", "是否保存坐标？"):
                self.save_coordinates()
            root.destroy()

if __name__ == "__main__":
    print("=== 坐标获取工具 ===")
    print("使用说明:")
    print("1. 选择是截取屏幕还是打开图片文件")
    print("2. 在图片上点击获取坐标")
    print("3. 按S键保存坐标，按ESC键退出")
    print("===================")
    
    getter = CoordinateGetter()
    getter.run()
