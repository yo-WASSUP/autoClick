import cv2
import time
import json
from image_recognition import ImageRecognition
from window_controller import WindowController

class AutoClicker:
    def __init__(self, config_file='config.json'):
        self.image_recognition = ImageRecognition()
        self.window_controller = WindowController()
        self.config = self.load_config(config_file)
        
    def load_config(self, config_file):
        """
        加载配置文件
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "window_title": "游戏窗口标题",
                "click_sequence": [
                    {
                        "type": "text",  # 可以是 "text" 或 "template"
                        "target": "按钮文字",  # 文字内容或模板图片路径
                        "delay": 1.0  # 点击后等待时间
                    }
                ]
            }
            
    def run(self):
        """
        运行自动点击流程
        """
        # 查找窗口
        if not self.window_controller.find_window(self.config["window_title"]):
            print(f"未找到窗口：{self.config['window_title']}")
            return False
            
        # 执行点击序列
        for action in self.config["click_sequence"]:
            # 捕获当前窗口画面
            screenshot = self.window_controller.capture_window()
            if screenshot is None:
                continue
                
            # 根据类型进行识别
            target_pos = None
            if action["type"] == "text":
                target_pos = self.image_recognition.find_text_location(
                    screenshot, action["target"])
            elif action["type"] == "template":
                template = cv2.imread(action["target"])
                if template is not None:
                    target_pos = self.image_recognition.template_matching(
                        screenshot, template)
                        
            # 执行点击
            if target_pos:
                self.window_controller.click(*target_pos)
                time.sleep(action["delay"])
            else:
                print(f"未找到目标：{action['target']}")
                
        return True

if __name__ == "__main__":
    auto_clicker = AutoClicker()
    auto_clicker.run()
