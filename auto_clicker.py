import time
import cv2
import pandas as pd
import json
import sys
import os
from image_recognition import ImageRecognition
from window_controller import WindowController
import win32gui

class AutoClicker:
    def __init__(self, config_file='click-test1.xlsx'):
        self.image_recognition = ImageRecognition()
        self.window_controller = WindowController()
        self.config = self.load_config(config_file)
            
    def get_icon_path(self, icon_name):
        return f"images/icons/{icon_name}.png"
        
    def load_config(self, config_file):
        """
        从Excel文件加载配置
        """
        try:
            # 读取Excel文件
            df = pd.read_excel(config_file)
            
            # 验证必要的列是否存在
            required_columns = ['type', 'target', 'click_type', 'delay', 'shift']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Excel文件缺少必要的列: {', '.join(missing_columns)}")
                
            # 构建点击序列
            click_sequence = []
            for _, row in df.iterrows():
                if pd.isna(row['target']):  # 跳过空行
                    continue
                click_sequence.append({
                    'type': row['type'],
                    'target': row['target'],
                    'click_type': row['click_type'],
                    'delay': float(row['delay']),
                    'shift': str(row['shift']) if not pd.isna(row['shift']) else '0'
                })
            
            return {
                'window_title': 'click-test1.xlsx - WPS Office',
                # 'window_title': 'Ace云手机',
                # 'window_title': '新VIP-0R4O',
                'click_sequence': click_sequence
            }
        except FileNotFoundError:
            print(f"未找到配置文件: {config_file}")
            return {}
        except Exception as e:
            print(f"加载配置文件时出错: {str(e)}")
            return {}
            
    def parse_shift(self, shift_str):
        """
        解析偏移值，返回x和y的偏移量
        例如：'L50' -> (-50, 0)  # 左移50像素
             'R30' -> (30, 0)   # 右移30像素
             'U20' -> (0, -20)  # 上移20像素
             'D40' -> (0, 40)   # 下移40像素
        """
        if not shift_str or shift_str == '0':
            return (0, 0)
            
        try:
            # 如果是纯数字，直接返回(0, 0)
            if isinstance(shift_str, (int, float)) or shift_str.isdigit():
                return (0, 0)
                
            direction = shift_str[0].upper()
            pixels = int(shift_str[1:])
            
            if direction == 'L':
                return (-pixels, 0)
            elif direction == 'R':
                return (pixels, 0)
            elif direction == 'U':
                return (0, -pixels)
            elif direction == 'D':
                return (0, pixels)
        except (IndexError, ValueError, TypeError) as e:
            print(f"无效的偏移值: {shift_str}, 错误: {str(e)}")
        return (0, 0)

    def run(self):
        """
        运行自动点击流程
        """
        if not self.config:
            print("配置无效，请检查配置文件")
            return False
            
        # 查找窗口
        if not self.window_controller.find_window(self.config["window_title"]):
            print(f"未找到窗口：{self.config['window_title']}")
            return False
            
        print(f"开始执行点击序列，共 {len(self.config['click_sequence'])} 步")
        
        # 执行点击序列
        step_index = 0
        retry_count = 0
        while step_index < len(self.config["click_sequence"]):
            # 在每个步骤执行前检查窗口是否存在
            if not win32gui.IsWindow(self.window_controller.window_handle):
                print(f"窗口已关闭或不存在，尝试重新查找窗口: {self.config['window_title']}")
                if not self.window_controller.find_window(self.config["window_title"]):
                    print(f"无法重新找到窗口，停止执行")
                    return False
                print("已重新找到窗口，继续执行")
            
            action = self.config["click_sequence"][step_index]
            print(f"执行步骤 {step_index + 1}/{len(self.config['click_sequence'])}: {action['type']} - {action['target']}")
            
            # 捕获当前窗口画面
            screenshot_data = self.window_controller.capture_window()
            if screenshot_data is None:
                print("截图失败，重试...")
                time.sleep(1)
                retry_count += 1
                continue
                
            screenshot, window_pos = screenshot_data
            
            # 获取截图尺寸作为窗口尺寸
            window_height, window_width = screenshot.shape[:2]
            
            # 根据步骤类型执行不同操作
            success = False
            try:
                step_type = action["type"]
                target = action["target"]
                shift = action.get("shift", "0")
                click_type = action.get("click_type", "single")
                delay = float(action.get("delay", 1.0))
                
                # 解析偏移
                shift_x, shift_y = self.parse_shift(shift)
                
                # 根据类型执行操作
                if step_type == "fixed":
                    # 解析固定坐标
                    try:
                        x, y = map(int, target.split(":"))
                            
                        # 计算偏移后的坐标
                        click_x = x + shift_x
                        click_y = y + shift_y
                        
                        # 检查坐标是否在窗口范围内
                        if x < 0 or y < 0 or (window_width > 0 and x >= window_width) or (window_height > 0 and y >= window_height):
                            print(f"警告: 坐标 ({x}, {y}) 可能超出窗口范围 ({window_width}x{window_height})，但仍将尝试点击")
                        
                        # 计算全局坐标
                        global_x = window_pos[0] + click_x
                        global_y = window_pos[1] + click_y
                            
                        success = self.window_controller.force_click(global_x, global_y, click_type, move_duration=0.3)
                        if not success:
                            print(f"点击固定位置 ({x}, {y}) 失败")
                            continue
                    except Exception as e:
                        print(f"解析固定坐标时出错: {str(e)}")
                        continue
                elif action["type"] == "text":
                    target_pos = self.image_recognition.find_text_location(
                        screenshot, action["target"]
                    )
                    if target_pos:
                        # 计算偏移后的坐标
                        click_x = target_pos[0] + shift_x
                        click_y = target_pos[1] + shift_y
                        
                        # 检查坐标是否在窗口范围内
                        if target_pos[0] < 0 or target_pos[1] < 0 or (window_width > 0 and target_pos[0] >= window_width) or (window_height > 0 and target_pos[1] >= window_height):
                            print(f"警告: 文字位置 ({target_pos[0]}, {target_pos[1]}) 可能超出窗口范围 ({window_width}x{window_height})，但仍将尝试点击")
                        
                        # 计算全局坐标
                        global_x = window_pos[0] + click_x
                        global_y = window_pos[1] + click_y
                        
                        success = self.window_controller.force_click(global_x, global_y, click_type, move_duration=0.3)
                        if not success:
                            print(f"点击文字 '{action['target']}' 失败")
                            continue
                    else:
                        print(f"未找到文字: '{action['target']}'")
                        continue
                elif action["type"] == "template":
                    # 获取图标路径
                    icon_path = self.get_icon_path(action["target"])
                    if icon_path is not None:
                        target_pos = self.image_recognition.find_icon(
                            screenshot, icon_path, threshold=0.7
                        )
                        if target_pos:
                            # 计算偏移后的坐标
                            click_x = target_pos[0] + shift_x
                            click_y = target_pos[1] + shift_y
                            
                            # 检查坐标是否在窗口范围内
                            if target_pos[0] < 0 or target_pos[1] < 0 or (window_width > 0 and target_pos[0] >= window_width) or (window_height > 0 and target_pos[1] >= window_height):
                                print(f"警告: 图标位置 ({target_pos[0]}, {target_pos[1]}) 可能超出窗口范围 ({window_width}x{window_height})，但仍将尝试点击")
                            
                            # 计算全局坐标
                            global_x = window_pos[0] + click_x
                            global_y = window_pos[1] + click_y
                            
                            success = self.window_controller.force_click(global_x, global_y, click_type, move_duration=0.3)
                            if not success:
                                print(f"点击图标 '{action['target']}' 失败")
                                continue
                        else:
                            print(f"未找到图标: '{action['target']}'")
                            continue
                    else:
                        print(f"无法加载图标: {action['target']}")
                        continue
                else:
                    print(f"未知的步骤类型: {step_type}")
                    continue
            except Exception as e:
                print(f"执行步骤 {step_index + 1} 时出错: {str(e)}")
                success = False
                
            if not success:
                print(f"步骤 {step_index + 1} 失败，等待重试...")
                time.sleep(1)  # 失败后等待1秒再重试
                continue
                
            print(f"步骤 {step_index + 1} 完成")
            # 等待指定时间
            time.sleep(delay)
            # 成功后移动到下一步
            step_index += 1
                
        print("所有步骤执行完毕")
        return True
        
if __name__ == "__main__":
    auto_clicker = AutoClicker()
    auto_clicker.run()