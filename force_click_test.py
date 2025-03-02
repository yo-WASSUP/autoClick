import time
import tkinter as tk
from tkinter import Button, Label
from window_controller import WindowController

class ForceClickTest:
    def __init__(self, root):
        self.root = root
        self.root.title("强制点击测试")
        self.root.geometry("600x400")
        self.root.configure(bg="black")
        
        # 创建窗口控制器
        self.controller = WindowController()
        
        # 点击计数器
        self.click_counts = [0, 0]
        
        # 添加标题
        title_label = Label(root, text="强制点击测试 - 即使点击其他窗口也能继续控制", 
                           font=("Arial", 16), fg="white", bg="black")
        title_label.pack(pady=20)
        
        # 创建按钮框架
        button_frame = tk.Frame(root, bg="black")
        button_frame.pack(pady=20)
        
        # 创建按钮
        self.buttons = []
        colors = ["red", "blue"]
        
        for i, color in enumerate(colors):
            btn = Button(button_frame, text=f"按钮{i+1} (点击次数: 0)", bg=color, fg="white", 
                        width=15, height=3, font=("Arial", 12))
            # 添加点击事件监听器
            btn.config(command=lambda idx=i: self.on_button_click(idx))
            btn.pack(side=tk.LEFT, padx=20)
            self.buttons.append(btn)
        
        # 添加说明
        instruction_label = Label(root, text="请尝试点击其他窗口，然后观察脚本是否仍能控制鼠标", 
                                font=("Arial", 12), fg="white", bg="black")
        instruction_label.pack(pady=20)
        
        # 添加状态标签
        self.status_label = Label(root, text="准备开始点击测试...", 
                                font=("Arial", 12), fg="white", bg="black")
        self.status_label.pack(pady=10)
        
        # 添加退出按钮
        exit_btn = Button(root, text="退出测试", command=self.root.destroy, 
                         bg="gray", fg="white", font=("Arial", 12))
        exit_btn.pack(pady=20)
        
        # 设置窗口置顶，确保它始终可见
        self.root.attributes('-topmost', True)
        
        # 延迟启动测试
        self.root.after(3000, self.start_click_test)
    
    def on_button_click(self, button_index):
        """按钮点击事件处理函数"""
        self.click_counts[button_index] += 1
        self.buttons[button_index].config(
            text=f"按钮{button_index+1} (点击次数: {self.click_counts[button_index]})",
            bg="gray" if self.click_counts[button_index] > 0 else self.buttons[button_index]["bg"]
        )
        print(f"按钮 {button_index+1} 被真实点击了 {self.click_counts[button_index]} 次")
    
    def start_click_test(self):
        """开始点击测试"""
        self.status_label.config(text="开始点击测试...")
        
        # 查找窗口句柄
        self.controller.find_window("强制点击测试")
        
        if not self.controller.window_handle:
            self.status_label.config(text="错误: 无法找到窗口")
            return
        
        self.status_label.config(text="找到窗口，准备点击")
        
        # 循环点击按钮
        for _ in range(10):  # 点击10次
            for i, button in enumerate(self.buttons):
                # 更新状态
                self.status_label.config(text=f"点击按钮 {i+1}/{len(self.buttons)}")
                self.root.update()
                
                # 获取按钮在屏幕上的位置
                x = button.winfo_rootx() + button.winfo_width() // 2
                y = button.winfo_rooty() + button.winfo_height() // 2
                
                # 记录点击前的计数
                before_clicks = self.click_counts[i]
                
                # 使用强制点击方法
                print(f"\n开始点击按钮 {i+1}, 位置: ({x}, {y})")
                self.controller.force_click(x, y, click_type='single')
                
                # 更新UI并等待一小段时间，让事件有机会处理
                self.root.update()
                time.sleep(1.0)
                
                # 检查点击后的计数
                after_clicks = self.click_counts[i]
                
                if after_clicks > before_clicks:
                    print(f"成功点击按钮: 点击前计数={before_clicks}, 点击后计数={after_clicks}")
                    self.status_label.config(text=f"成功点击按钮 {i+1}")
                else:
                    print(f"点击按钮失败: 点击前后计数都是 {before_clicks}")
                    self.status_label.config(text=f"点击按钮 {i+1} 失败")
                
                # 更新UI
                self.root.update()
                time.sleep(1.0)
            
            # 每轮点击后等待一段时间
            self.status_label.config(text="等待下一轮点击...")
            self.root.update()
            time.sleep(2.0)
        
        self.status_label.config(text="点击测试完成!")

def main():
    # 创建Tkinter窗口
    root = tk.Tk()
    app = ForceClickTest(root)
    root.mainloop()

if __name__ == "__main__":
    main()
