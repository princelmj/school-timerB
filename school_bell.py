import tkinter as tk
from tkinter import messagebox, filedialog
import pygame
import json
import os
import time
import threading

class SchoolBellApp:
    def __init__(self, root):
        self.root = root
        self.root.title("校园上课铃")
        self.root.geometry("400x300")

        # 初始化铃声配置
        self.bell_schedule = []

        print("Creating UI...")
        # 创建界面组件
        self.create_ui()

        print("Loading config...")
        # 加载铃声配置（必须在 create_ui 之后）
        self.load_config()

        # 初始化 Pygame 音乐模块
        pygame.mixer.init()

        # 启动定时检测线程
        self.running = True
        self.thread = threading.Thread(target=self.check_time_loop)
        self.thread.daemon = True
        self.thread.start()

    def create_ui(self):
        print("正在创建 UI...")
        # 创建主框架
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 铃声列表标题
        tk.Label(main_frame, text="当前铃声配置：", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))

        # 创建带滚动条的列表框
        list_frame = tk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(list_frame, height=10, selectmode=tk.SINGLE)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        # 按钮区域
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(pady=10, fill=tk.X)

        tk.Button(btn_frame, text="添加铃声", width=12, command=self.add_bell).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="删除选中项", width=12, command=self.delete_bell).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="保存配置", width=12, command=self.save_config).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="加载配置", width=12, command=self.load_config_ui).pack(side=tk.LEFT, padx=5)

        # 状态栏
        self.status_bar = tk.Label(self.root, text="就绪", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 更新状态栏
        self.update_status_bar()

    def load_config(self, path=None):
        if not path:
            path = "bell_config.json"
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                self.bell_schedule = json.load(f)
        self.update_listbox()

    def save_config(self):
        path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[("JSON 文件", "*.json")])
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.bell_schedule, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("提示", "配置已保存")

    def load_config_ui(self):
        path = filedialog.askopenfilename(filetypes=[("JSON 文件", "*.json")])
        if path:
            self.load_config(path)
            messagebox.showinfo("提示", "配置已加载")

    def update_listbox(self):
        try:
            self.listbox.delete(0, tk.END)
        except Exception as e:
            print("Listbox 错误:", str(e))
        for item in self.bell_schedule:
            self.listbox.insert(tk.END, f"{item['time']} - {item['description']}")

    def add_bell(self):
        AddBellWindow(self)

    def delete_bell(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            del self.bell_schedule[index]
            self.update_listbox()

    def check_time_loop(self):
        while self.running:
            current_time = time.strftime("%H:%M")
            for bell in self.bell_schedule:
                if bell["time"] == current_time:
                    self.play_bell(bell)
                    time.sleep(60)  # 防止重复播放
            time.sleep(10)

    def play_bell(self, bell):
        sound_path = bell.get("sound", "bell.mp3")
        if os.path.exists(sound_path):
            pygame.mixer.music.load(sound_path)
            pygame.mixer.music.play()
        else:
            messagebox.showerror("错误", f"找不到铃声文件: {sound_path}")

    def update_status_bar(self):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.status_bar.config(text=f"当前时间: {current_time}")
        self.root.after(1000, self.update_status_bar)


class AddBellWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.title("添加铃声")
        self.geometry("300x150")

        tk.Label(self, text="时间 (HH:MM): ").pack(pady=5)
        self.time_entry = tk.Entry(self)
        self.time_entry.pack(pady=5)

        tk.Label(self, text="描述:").pack(pady=5)
        self.desc_entry = tk.Entry(self)
        self.desc_entry.pack(pady=5)

        tk.Button(self, text="选择铃声", command=self.select_sound).pack(pady=5)
        tk.Button(self, text="确认", command=self.confirm).pack(pady=5)

        self.sound_path = None

    def select_sound(self):
        path = filedialog.askopenfilename(filetypes=[("音频文件", "*.mp3 *.wav")])
        if path:
            self.sound_path = path

    def confirm(self):
        time_str = self.time_entry.get().strip()
        desc = self.desc_entry.get().strip()
        if time_str and desc:
            bell = {
                "time": time_str,
                "description": desc
            }
            if self.sound_path:
                bell["sound"] = self.sound_path
            self.parent.bell_schedule.append(bell)
            self.parent.update_listbox()
            self.destroy()
        else:
            messagebox.showwarning("警告", "请输入完整信息")

if __name__ == "__main__":
    root = tk.Tk()
    app = SchoolBellApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: os._exit(0))
    root.mainloop()