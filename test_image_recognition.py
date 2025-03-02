import cv2
import numpy as np
from image_recognition import ImageRecognition
import os
import sys
from cv_utils import put_chinese_text, draw_box_with_text, show_image_with_text, imread_cn

def test_recognition(image_path, target_text):
    """
    测试图像识别功能
    """
    # 初始化图像识别
    ir = ImageRecognition()
    
    # 读取测试图片 - 使用支持中文路径的函数
    image = imread_cn(image_path)
    if image is None:
        print(f"无法读取图片: {image_path}")
        return
    
    # 创建一个用于显示的图像副本
    display_img = image.copy()
    
    # 1. 测试文字识别
    text_location = ir.find_text_location(image, target_text)
    if text_location:
        x, y = text_location
        print(f"找到文字 '{target_text}' 在位置: ({x}, {y})")
        
        # 在图片上标记文字位置
        cv2.circle(display_img, (x, y), 10, (0, 0, 255), -1)  # 红色圆点
        display_img = put_chinese_text(display_img, f"文字: {target_text}", (x + 15, y), (0, 0, 255), 30)
    else:
        print(f"未找到文字: {target_text}")
    
    # 2. 测试图标识别
    icon_path = r"images\icons\shield-armer.png"  # 请确保此图片存在
    template = imread_cn(icon_path)  # 使用支持中文路径的函数
    if template is not None:
        icon_location = ir.template_matching(image, template)
        if icon_location:
            x, y = icon_location
            print(f"找到图标在位置: ({x}, {y})")
            
            # 获取模板图片的尺寸
            h, w = template.shape[:2]
            
            # 在图片上标记图标位置
            display_img = draw_box_with_text(
                display_img, 
                "找到图标", 
                [x - w//2, y - h//2, x + w//2, y + h//2]
            )
    else:
        print(f"无法加载图标: {icon_path}")
    
    # 显示结果
    show_image_with_text(
        display_img, 
        "Image Recognition Test Results", 
        text="按任意键关闭窗口", 
        position=(20, 30)
    )
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # 测试图片路径和目标文字
    # image_path = "images\warehouse-manager.png"  # 请确保此图片存在
    image_path = r"images\仓库.png"  # 请确保此图片存在
    target_text = "背包"  # 要查找的文字
    
    # 如果命令行提供了参数，使用命令行参数
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    if len(sys.argv) > 2:
        target_text = sys.argv[2]
    
    test_recognition(image_path, target_text)
