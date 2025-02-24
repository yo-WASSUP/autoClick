import cv2
import numpy as np
from image_recognition import ImageRecognition

def test_recognition():
    # 创建ImageRecognition实例
    ir = ImageRecognition()
    
    # 读取要识别的图片
    image_path = r"images\warehouse-manager.png"  # 请确保此图片存在
    image = cv2.imread(image_path)
    if image is None:
        print(f"无法读取图片: {image_path}")
        return
    
    # 保存原始图片的副本用于显示
    display_image = image.copy()
    
    # 1. 测试文字识别
    target_text = "背包"  # 要查找的文字
    text_location = ir.find_text_location(image, target_text)
    
    if text_location:
        # 在找到的文字位置画一个圆圈
        cv2.circle(display_image, text_location, 20, (0, 255, 0), 2)
        # 添加文字标签
        cv2.putText(display_image, f"Text: {target_text}", 
                    (text_location[0]-50, text_location[1]-30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        print(f"找到文字 '{target_text}' 在位置: {text_location}")
    else:
        print(f"未找到文字: {target_text}")
    
    # 2. 测试图标识别
    icon_path = r"images\shield-armer.png"  # 请确保此图片存在
    template = cv2.imread(icon_path)
    if template is not None:
        icon_location = ir.template_matching(image, template)
        
        if icon_location:
            # 在找到的图标位置画一个红色圆圈
            cv2.circle(display_image, icon_location, 20, (0, 0, 255), 2)
            # 添加图标标签
            cv2.putText(display_image, "Icon", 
                        (icon_location[0]-30, icon_location[1]-30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            print(f"找到图标在位置: {icon_location}")
        else:
            print("未找到图标")
    else:
        print(f"无法读取图标文件: {icon_path}")
    
    # 显示结果
    cv2.imshow("Recognition Result", display_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_recognition()
