import os
import sys
import cv2
import numpy as np
import argparse
from paddleocr import PaddleOCR
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.font_manager import FontProperties
import matplotlib
from cv_utils import put_chinese_text, draw_box_with_text, draw_text_with_box, imread_cn

class OCRDetector:
    def __init__(self, use_gpu=True, lang='ch'):
        """
        初始化OCR检测器
        
        Args:
            use_gpu: 是否使用GPU加速
            lang: 语言，默认为中文
        """
        self.ocr = PaddleOCR(
            use_angle_cls=True,  # 使用方向分类器
            lang=lang,           # 语言
            use_gpu=use_gpu,     # 使用GPU
            show_log=False       # 不显示日志
        )
        print(f"OCR初始化完成，使用GPU: {use_gpu}, 语言: {lang}")
        
    def detect(self, image_path):
        """
        检测图片中的文字
        
        Args:
            image_path: 图片路径
            
        Returns:
            检测结果列表，每项包含位置和文本信息
        """
        if not os.path.exists(image_path):
            print(f"图片不存在: {image_path}")
            return None
            
        print(f"正在处理图片: {image_path}")
        result = self.ocr.ocr(image_path, cls=True)
        
        if not result or len(result) == 0:
            print("未检测到文字")
            return []
            
        # 处理结果
        detected_texts = []
        for line in result:
            for item in line:
                box = item[0]  # 文本框坐标 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                text = item[1][0]  # 文本内容
                confidence = item[1][1]  # 置信度
                
                # 计算中心点
                center_x = int(sum(point[0] for point in box) / 4)
                center_y = int(sum(point[1] for point in box) / 4)
                
                detected_texts.append({
                    'box': box,
                    'text': text,
                    'confidence': confidence,
                    'center': (center_x, center_y)
                })
                
        print(f"检测到 {len(detected_texts)} 个文本区域")
        return detected_texts
        
    def visualize(self, image_path, detected_texts, output_path=None):
        """
        可视化检测结果
        
        Args:
            image_path: 原始图片路径
            detected_texts: 检测结果
            output_path: 输出图片路径，如果为None则显示图片
        """
        if not detected_texts:
            print("没有检测结果可视化")
            return
            
        # 读取图片
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 创建图形
        plt.figure(figsize=(20, 20))
        ax = plt.gca()
        ax.imshow(image)
        
        # 设置中文字体
        try:
            font = FontProperties(fname=r"C:\Windows\Fonts\simhei.ttf", size=14)
        except:
            font = FontProperties(size=14)
        
        # 绘制检测框和文本
        for i, item in enumerate(detected_texts):
            box = item['box']
            text = item['text']
            confidence = item['confidence']
            center = item['center']
            
            # 创建多边形
            polygon = patches.Polygon(box, closed=True, fill=False, edgecolor='red', linewidth=2)
            ax.add_patch(polygon)
            
            # 添加文本标签
            label = f"{i+1}: {text} ({confidence:.2f})"
            ax.text(center[0], center[1], label, color='blue', fontproperties=font,
                   bbox=dict(facecolor='white', alpha=0.7))
            
            # 标记中心点
            ax.plot(center[0], center[1], 'ro', markersize=5)
            
        plt.title(f"OCR Detection Results - {len(detected_texts)} texts", fontproperties=font)
        plt.axis('off')
        
        # 保存或显示
        if output_path:
            plt.savefig(output_path, bbox_inches='tight', dpi=100)
            print(f"可视化结果已保存到: {output_path}")
        else:
            plt.show()
            
    def visualize_opencv(self, image_path, detected_texts, output_path=None):
        """
        使用OpenCV可视化检测结果
        
        Args:
            image_path: 原始图片路径
            detected_texts: 检测结果
            output_path: 输出图片路径，如果为None则显示图片
        """
        if not detected_texts:
            print("没有检测结果可视化")
            return
            
        # 读取图片 - 使用支持中文路径的函数
        image = imread_cn(image_path)
        if image is None:
            print(f"无法读取图片: {image_path}")
            return
            
        # 在图片上绘制检测结果
        for i, item in enumerate(detected_texts):
            box = item['box']
            text = item['text']
            confidence = item['confidence']
            center = item['center']
            
            # 转换坐标为整数
            box = [[int(p[0]), int(p[1])] for p in box]
            
            # 绘制多边形框
            pts = np.array(box, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(image, [pts], True, (0, 0, 255), 2)
            
            # 绘制中心点
            cv2.circle(image, center, 5, (255, 0, 0), -1)
            
            # 添加文字标签
            label = f"{i+1}: {text} ({confidence:.2f})"
            image = draw_text_with_box(
                image, 
                label, 
                (center[0] + 10, center[1]), 
                text_color=(0, 0, 255),
                bg_color=(255, 255, 255),
                text_size=20,
                alpha=0.7
            )
        
        # 添加标题
        image = put_chinese_text(
            image,
            f"OCR Detection Results - {len(detected_texts)} texts",
            (20, 30),
            text_color=(255, 0, 0),
            text_size=30
        )
        
        # 保存或显示
        if output_path:
            cv2.imwrite(output_path, image)
            print(f"可视化结果已保存到: {output_path}")
        else:
            cv2.imshow("OCR Detection Results", image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
        return image
        
def main():
    # 参数解析
    parser = argparse.ArgumentParser(description='OCR检测工具')
    parser.add_argument('--image_path', type=str, default='screenshot.png', help='要检测的图像路径')
    parser.add_argument('--output_dir', type=str, default='ocr_results', help='结果输出目录')
    parser.add_argument('--no_gpu', action='store_true', help='不使用GPU')
    parser.add_argument('--lang', type=str, default='ch', help='语言: ch(中文)或en(英文)')
    parser.add_argument('--no_visual', action='store_true', help='不显示可视化结果')
    
    args = parser.parse_args()
    
    # 创建OCR检测器
    use_gpu = not args.no_gpu
    detector = OCRDetector(use_gpu=use_gpu, lang=args.lang)
    
    # 检测图像
    image_path = args.image_path
    print(f"正在处理图像: {image_path}")
    
    if not os.path.exists(image_path):
        print(f"错误: 图像文件 '{image_path}' 不存在")
        return
    
    # 执行OCR检测
    detected_texts = detector.detect(image_path)
    
    # 创建输出目录
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # 获取文件名（不含扩展名）
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    
    if detected_texts:
        # 可视化
        if not args.no_visual:
            visual_path = os.path.join(args.output_dir, f"{base_name}_visual.png")
            detector.visualize(image_path, detected_texts, visual_path)
            detector.visualize_opencv(image_path, detected_texts, os.path.join(args.output_dir, f"{base_name}_visual_opencv.png"))
            
        print(f"处理完成: {image_path}")
    else:
        print(f"处理失败: {image_path}")

if __name__ == "__main__":
    main()
