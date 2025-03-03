import os
import sys
import urllib.request
import zipfile
import shutil

def download_zlib():
    """下载并安装zlibwapi.dll"""
    print("正在下载zlib...")
    
    # 下载地址
    url = "https://www.winimage.com/zLibDll/zlib123dllx64.zip"
    zip_path = "zlib123dllx64.zip"
    
    # 下载文件
    urllib.request.urlretrieve(url, zip_path)
    print(f"已下载到: {zip_path}")
    
    # 解压文件
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall("zlib")
    print("已解压文件")
    
    # 复制DLL到系统目录
    dll_path = os.path.join("zlib", "dll_x64", "zlibwapi.dll")
    
    # 复制到当前目录
    shutil.copy(dll_path, "zlibwapi.dll")
    print(f"已复制 zlibwapi.dll 到当前目录")
    
    # 清理临时文件
    os.remove(zip_path)
    shutil.rmtree("zlib")
    print("已清理临时文件")
    
    print("\n请将 zlibwapi.dll 复制到以下位置之一:")
    print("1. 当前工作目录 (已完成)")
    print("2. Python安装目录")
    print("3. Windows系统目录 (C:\\Windows\\System32)")
    print("\n完成后，重新运行您的程序")

if __name__ == "__main__":
    download_zlib()
