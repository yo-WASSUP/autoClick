import os
import sys
import time
import cv2
import numpy as np
from paddleocr import PaddleOCR
import paddle

def check_gpu():
    """检查GPU是否可用"""
    print("=" * 50)
    print("GPU检查")
    print("=" * 50)
    
    # 检查CUDA是否可用
    print(f"CUDA是否可用: {paddle.device.is_compiled_with_cuda()}")
    
    # 检查可用的设备
    print(f"可用的设备: {paddle.device.get_device()}")
    
    # 检查CUDA版本
    if paddle.device.is_compiled_with_cuda():
        print(f"CUDA版本: {paddle.version.cuda()}")
    
    # 检查Paddle版本
    print(f"Paddle版本: {paddle.__version__}")
    
    # 检查当前使用的设备
    print(f"当前使用的设备: {paddle.device.get_device()}")
    
    print("\n")

def test_ocr_speed():
    """测试OCR速度"""
    print("=" * 50)
    print("OCR速度测试")
    print("=" * 50)
    

    # 使用CPU测试
    print("\nCPU测试:")
    ocr_cpu = PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=False, show_log=False)
    
    start_time = time.time()
    result_cpu = ocr_cpu.ocr("screenshots\screenshot.png", cls=True)
    cpu_time = time.time() - start_time
    
    print(f"CPU识别耗时: {cpu_time:.2f}秒")
    if result_cpu and result_cpu[0]:
        for line in result_cpu:
            for item in line:
                print(f"识别文字: {item[1][0]}, 置信度: {item[1][1]:.2f}")
    
    # 使用GPU测试
    print("\nGPU测试:")
    ocr_gpu = PaddleOCR(
        use_angle_cls=True, 
        lang='ch', 
        use_gpu=True,
        show_log=False,
        rec_batch_num=6,
        det_db_thresh=0.3,
        det_db_box_thresh=0.5,
        use_mp=True,
        total_process_num=4
    )
    
    start_time = time.time()
    result_gpu = ocr_gpu.ocr("screenshots\screenshot.png", cls=True)
    gpu_time = time.time() - start_time
    
    print(f"GPU识别耗时: {gpu_time:.2f}秒")
    if result_gpu and result_gpu[0]:
        for line in result_gpu:
            for item in line:
                print(f"识别文字: {item[1][0]}, 置信度: {item[1][1]:.2f}")
    
    # 比较速度
    if cpu_time > 0 and gpu_time > 0:
        speedup = cpu_time / gpu_time
        print(f"\nGPU加速比: {speedup:.2f}x")
    
    print("\n")

def main():
    """主函数"""
    print("PaddleOCR GPU检查工具")
    print("-" * 50)
    
    check_gpu()
    test_ocr_speed()
    
    print("检查完成")

if __name__ == "__main__":
    main()
