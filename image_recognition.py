import cv2
import numpy as np
from paddleocr import PaddleOCR

class ImageRecognition:
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)
        
    def find_text_location(self, image, target_text):
        """
        使用PaddleOCR在图像中查找指定文字的位置
        """
        result = self.ocr.ocr(image, cls=True)
        if result is None:
            return None
            
        for line in result:
            for item in line:
                text = item[1][0]
                if target_text in text:
                    # 返回文字框的中心点坐标
                    box = item[0]
                    center_x = int((box[0][0] + box[2][0]) / 2)
                    center_y = int((box[0][1] + box[2][1]) / 2)
                    return (center_x, center_y)
        return None

    def template_matching(self, image, template, threshold=0.8):
        """
        使用模板匹配在图像中查找图标
        """
        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)
        
        if len(locations[0]) > 0:
            # 返回第一个匹配位置的中心点
            max_loc = (locations[1][0], locations[0][0])
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            return (center_x, center_y)
        return None
