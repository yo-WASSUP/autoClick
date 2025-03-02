import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

def imread_cn(file_path):
    """
    读取中文路径的图片
    
    Args:
        file_path: 图片路径，可以包含中文
        
    Returns:
        读取的图片，如果读取失败则返回None
    """
    try:
        # 使用PIL读取图片，它支持中文路径
        img_pil = Image.open(file_path)
        # 转换为OpenCV格式
        img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        return img_cv
    except Exception as e:
        print(f"读取图片失败: {file_path}, 错误: {str(e)}")
        return None

def put_chinese_text(img, text, position, text_color=(0, 0, 255), text_size=30):
    """
    在图片上添加中文文字
    
    Args:
        img: OpenCV格式的图片(numpy.ndarray)
        text: 要添加的文字
        position: 文字位置 (x, y)
        text_color: 文字颜色，默认红色
        text_size: 文字大小
        
    Returns:
        添加文字后的图片
    """
    # 判断图片是否为OpenCV格式
    if isinstance(img, np.ndarray):
        # 转换OpenCV图片为PIL格式
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    else:
        img_pil = img
        
    # 创建一个可以在给定图像上绘图的对象
    draw = ImageDraw.Draw(img_pil)
    
    # 加载中文字体
    fontpath = os.path.join(os.environ.get('WINDIR', 'C:/Windows'), 'Fonts/simhei.ttf')
    
    # 如果找不到系统字体，使用备选路径
    if not os.path.exists(fontpath):
        # 尝试其他常见字体路径
        common_fonts = [
            'C:/Windows/Fonts/simhei.ttf',
            'C:/Windows/Fonts/simsun.ttc',
            'C:/Windows/Fonts/msyh.ttc',
            'C:/Windows/Fonts/simkai.ttf'
        ]
        
        for font in common_fonts:
            if os.path.exists(font):
                fontpath = font
                break
    
    # 创建字体对象
    try:
        font = ImageFont.truetype(fontpath, text_size)
    except IOError:
        # 如果找不到任何中文字体，使用默认字体
        font = ImageFont.load_default()
        print("警告: 找不到中文字体，使用默认字体")
    
    # 在图片上绘制文字
    draw.text(position, text, font=font, fill=text_color)
    
    # 将PIL图片转换回OpenCV格式
    if isinstance(img, np.ndarray):
        img_opencv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        return img_opencv
    else:
        return img_pil

def draw_text_with_box(img, text, position, text_color=(0, 0, 255), bg_color=(255, 255, 255), 
                      text_size=30, padding=5, alpha=0.7):
    """
    在图片上添加带背景框的中文文字
    
    Args:
        img: OpenCV格式的图片
        text: 要添加的文字
        position: 文字位置 (x, y)
        text_color: 文字颜色，默认红色
        bg_color: 背景颜色，默认白色
        text_size: 文字大小
        padding: 文字与边框的间距
        alpha: 背景透明度 (0-1)
        
    Returns:
        添加文字后的图片
    """
    # 转换为PIL图像
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    
    # 加载中文字体
    fontpath = os.path.join(os.environ.get('WINDIR', 'C:/Windows'), 'Fonts/simhei.ttf')
    
    # 如果找不到系统字体，使用备选路径
    if not os.path.exists(fontpath):
        # 尝试其他常见字体路径
        common_fonts = [
            'C:/Windows/Fonts/simhei.ttf',
            'C:/Windows/Fonts/simsun.ttc',
            'C:/Windows/Fonts/msyh.ttc',
            'C:/Windows/Fonts/simkai.ttf'
        ]
        
        for font in common_fonts:
            if os.path.exists(font):
                fontpath = font
                break
    
    # 创建字体对象
    try:
        font = ImageFont.truetype(fontpath, text_size)
    except IOError:
        font = ImageFont.load_default()
        print("警告: 找不到中文字体，使用默认字体")
    
    # 计算文本大小
    try:
        # 新版PIL使用font.getbbox或font.getsize
        if hasattr(font, 'getbbox'):
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        elif hasattr(font, 'getsize'):
            text_width, text_height = font.getsize(text)
        else:
            # 旧版PIL使用draw.textsize
            text_width, text_height = draw.textsize(text, font=font)
    except Exception as e:
        # 如果计算失败，使用估计值
        print(f"警告: 无法计算文本大小: {str(e)}")
        text_width = len(text) * text_size * 0.6
        text_height = text_size * 1.2
    
    # 计算背景框位置
    x, y = position
    box_position = [
        x - padding, 
        y - padding, 
        x + text_width + padding, 
        y + text_height + padding
    ]
    
    # 创建一个透明层用于绘制背景框
    overlay = Image.new('RGBA', img_pil.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    # 绘制背景框
    overlay_draw.rectangle(box_position, fill=(*bg_color, int(255 * alpha)))
    
    # 将透明层合并到原图
    img_pil = Image.alpha_composite(img_pil.convert('RGBA'), overlay)
    
    # 绘制文字
    draw = ImageDraw.Draw(img_pil)
    draw.text(position, text, font=font, fill=(*text_color, 255))
    
    # 转换回OpenCV格式
    img_opencv = cv2.cvtColor(np.array(img_pil.convert('RGB')), cv2.COLOR_RGB2BGR)
    return img_opencv

def draw_box_with_text(img, text, box, text_color=(0, 0, 255), box_color=(0, 255, 0), 
                      text_size=20, thickness=2):
    """
    在图片上绘制带文字标注的矩形框
    
    Args:
        img: OpenCV格式的图片
        text: 要添加的文字
        box: 矩形框坐标 [x1, y1, x2, y2]
        text_color: 文字颜色
        box_color: 矩形框颜色
        text_size: 文字大小
        thickness: 矩形框线条粗细
        
    Returns:
        处理后的图片
    """
    # 绘制矩形框
    x1, y1, x2, y2 = box
    cv2.rectangle(img, (x1, y1), (x2, y2), box_color, thickness)
    
    # 添加文字（在矩形框上方）
    return put_chinese_text(img, text, (x1, y1 - text_size - 5), text_color, text_size)

def show_image_with_text(img, window_name="Image Preview", wait_key=0, text=None, position=None):
    """
    显示带有中文标题和可选文字的图片
    
    Args:
        img: 要显示的图片
        window_name: 窗口标题（注意：OpenCV不支持中文窗口标题，只能使用英文）
        wait_key: cv2.waitKey的参数，0表示等待按键
        text: 要在图片上显示的文字
        position: 文字位置
    """
    # 复制图片以避免修改原图
    display_img = img.copy()
    
    # 如果有文字要显示
    if text and position:
        display_img = put_chinese_text(display_img, text, position)
    
    # 显示图片
    cv2.imshow(window_name, display_img)
    cv2.waitKey(wait_key)
    
    return display_img

# 测试代码
if __name__ == "__main__":
    # 创建一个空白图片
    img = np.zeros((400, 600, 3), dtype=np.uint8)
    img.fill(255)  # 白色背景
    
    # 测试在图片上添加中文
    img = put_chinese_text(img, "这是中文测试", (50, 50), (255, 0, 0), 30)
    
    # 测试带背景框的文字
    img = draw_text_with_box(img, "带背景框的中文", (50, 100), (0, 0, 255), (200, 200, 200), 30)
    
    # 测试带文字的矩形框
    img = draw_box_with_text(img, "目标检测框", [100, 150, 300, 250])
    
    # 显示结果 - 注意窗口标题只能使用英文
    show_image_with_text(img, "Chinese Text Demo", text="按任意键关闭", position=(50, 300))
