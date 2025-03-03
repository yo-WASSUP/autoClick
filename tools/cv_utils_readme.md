# OpenCV 中文支持工具

这个模块提供了在 OpenCV 图像上显示中文文字的功能，解决了 OpenCV 在 Windows 上不支持中文的问题。

## 主要功能

1. **imread_cn(file_path)** - 读取中文路径的图片
   - 使用 PIL 库读取图片，支持中文路径
   - 将 PIL 图像转换为 OpenCV 格式

2. **put_chinese_text(img, text, position, text_color, text_size)** - 在图像上添加中文文字
   - 使用 PIL 绘制中文文字
   - 自动查找系统中的中文字体

3. **draw_text_with_box(img, text, position, text_color, bg_color, text_size, padding, alpha)** - 在图像上添加带背景框的中文文字
   - 带有半透明背景
   - 可自定义颜色和大小

4. **draw_box_with_text(img, text, box, text_color, box_color, text_size, thickness)** - 在图像上绘制带文字标注的矩形框
   - 用于目标检测结果可视化
   - 支持中文标签

5. **show_image_with_text(img, window_name, wait_key, text, position)** - 显示带有中文文字的图片
   - 注意：窗口标题只能使用英文（OpenCV 限制）
   - 图像上的文字可以是中文

## 使用示例

```python
from cv_utils import imread_cn, put_chinese_text, draw_box_with_text

# 读取中文路径的图片
img = imread_cn("图片/测试.png")

# 在图片上添加中文
img = put_chinese_text(img, "这是中文测试", (50, 50), (255, 0, 0), 30)

# 绘制带中文标注的矩形框
img = draw_box_with_text(img, "检测到的物体", [100, 100, 300, 200])

# 显示结果 - 注意窗口标题只能使用英文
cv2.imshow("Test Image", img)
cv2.waitKey(0)
```

## 注意事项

1. OpenCV 的 `cv2.imshow()` 函数的窗口标题不支持中文，只能使用英文或 ASCII 字符
2. 图像上的文字可以是中文，使用 `put_chinese_text()` 函数
3. 如果找不到中文字体，会使用默认字体，可能导致中文显示为方块
4. 常见中文字体包括：SimHei (黑体)、SimSun (宋体)、Microsoft YaHei (微软雅黑)
