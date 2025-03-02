import cv2
import numpy as np
from paddleocr import PaddleOCR
from cv_utils import imread_cn
import time

class ImageRecognition:
    def __init__(self):
        # 使用GPU加速，并使用轻量级模型
        self.ocr = PaddleOCR(
            use_angle_cls=True, 
            lang='ch', 
            use_gpu=True,  # 启用GPU
            show_log=False,
            # 使用轻量级模型提高速度
            det_db_thresh=0.3,
            det_db_box_thresh=0.5
        )
        
    def find_text_location(self, image, target_text):
        """
        在图像中查找指定文字的位置
        
        Args:
            image: 图像数据
            target_text: 要查找的文字
            
        Returns:
            文字的中心位置坐标 (x, y)，如果未找到则返回 None
        """
        start_time = time.time()
        
        # 使用OCR识别图像中的所有文字
        result = self.ocr.ocr(image, cls=True)
        
        # 如果没有识别结果，返回None
        if not result or not result[0]:
            end_time = time.time()
            print(f"文字识别耗时: {end_time - start_time:.2f}秒，未找到任何文字")
            return None
            
        # 遍历识别结果，查找匹配的文字
        for line in result:
            for item in line:
                box = item[0]  # 文字框坐标
                text = item[1][0]  # 识别的文字
                confidence = item[1][1]  # 置信度
                
                # 如果文字包含目标文字，返回文字框的中心位置
                if target_text in text:
                    # 计算文字框的中心位置
                    center_x = int(sum(point[0] for point in box) / 4)
                    center_y = int(sum(point[1] for point in box) / 4)
                    
                    end_time = time.time()
                    print(f"文字识别耗时: {end_time - start_time:.2f}秒，找到文字: '{text}' (置信度: {confidence:.2f})")
                    return (center_x, center_y)
        
        # 如果未找到匹配的文字，返回None
        end_time = time.time()
        print(f"文字识别耗时: {end_time - start_time:.2f}秒，未找到目标文字: '{target_text}'")
        return None
        
    def template_matching(self, image, template, threshold=0.7):
        """
        模板匹配查找图像
        
        Args:
            image: 大图
            template: 要查找的小图模板
            threshold: 匹配阈值，越高要求越严格
            
        Returns:
            模板在图像中的中心位置 (x, y)，如果未找到则返回 None
        """
        # 进行模板匹配
        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        
        # 找到匹配度最高的位置
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # 如果最高匹配度低于阈值，认为未找到
        if max_val < threshold:
            return None
            
        # 计算模板中心在原图中的位置
        h, w = template.shape[:2]
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        
        return (center_x, center_y)
        
    def find_icon(self, image, icon_path, threshold=0.7):
        """
        在图像中查找图标
        
        Args:
            image: 图像数据
            icon_path: 图标文件路径
            threshold: 匹配阈值，越高要求越严格
            
        Returns:
            图标在图像中的中心位置 (x, y)，如果未找到则返回 None
        """
        # 读取图标图片
        icon = imread_cn(icon_path)
        if icon is None:
            print(f"无法读取图标: {icon_path}")
            return None
            
        # 获取当前图像的宽度
        screenshot_width = image.shape[1]
            
        # 计算缩放比例 (假设图标是在1920宽的屏幕上截取的)
        original_width = 1920
        scale_ratio = screenshot_width / original_width
        
        if scale_ratio != 1.0:
            # 调整图标大小
            new_width = int(icon.shape[1] * scale_ratio)
            new_height = int(icon.shape[0] * scale_ratio)
            
            # 确保尺寸至少为1x1
            new_width = max(1, new_width)
            new_height = max(1, new_height)
            
            print(f"调整图标大小: 原始 {icon.shape[1]}x{icon.shape[0]} -> 新 {new_width}x{new_height} (比例: {scale_ratio:.2f})")
            icon = cv2.resize(icon, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        # 使用模板匹配查找图标
        return self.template_matching(image, icon, threshold)
