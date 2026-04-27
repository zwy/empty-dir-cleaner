import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import threading


# ──────────────────────────────────────────────
# 核心功能：递归删除空目录
# ──────────────────────────────────────────────
def delete_empty_dirs(root_path, log_callback):
    """
    自底向上扫描并删除所有空目录。
    使用 os.walk(topdown=False) 从叶子目录向上遍历，
    保证子目录清空后父目录才被判断是否为空。
    返回 (deleted_count, failed_list)
    """
    if not os.path.isdir(root_path):
        raise ValueError(f"路径不存在或不是目录：{root_path}")

    deleted = 0
    failed = []

    for dirpath, dirnames, filenames in os.walk(root_path, topdown=False):
        if dirpath == root_path:
            continue  # 不删根目录本身
        try:
            if not os.listdir(dirpath):  # 目录为空
                os.rmdir(dirpath)
                deleted += 1
                log_callback(f"✅ 已删除：{dirpath}")
        except Exception as e:
            failed.append(dirpath)
            log_callback(f"❌ 失败：{dirpath}  ({e})")

    return deleted, failed


# ──────────────────────────────────────────────
# GUI 主程序
# ──────────────────────────────────────────────
class FolderCleanerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("空目录清理工具")
        self.geometry("720x520")
        self.resizable(True, True)
        self.configure(bg="#f5f5f0")
        self._build_ui()

    # ── 构建界面 ────────────────────────────────
    def _build_ui(self):
        # ── 顶部标题栏 ──
        title_frame = tk.Frame(self, bg="#1a6e74", pady=14)
        title_frame.pack(fill="x")
        tk.Label(
            title_frame,
            text="🗂  空目录清理工具",
            font=("Helvetica", 16, "bold"),
            fg="white", bg="#1a6e74"
        ).pack()

        # ── 路径输入区 ──
        input_frame = tk.Frame(self, bg="#f5f5f0", padx=20, pady=16)
        input_frame.pack(fill="x")

        tk.Label(
            input_frame, text="目标文件夹路径",
            font=("Helvetica", 10, "bold"),
            fg="#28251d", bg="#f5f5f0"
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 6))

        self.path_var = tk.StringVar()
        self.path_entry = tk.Entry(
            input_frame, textvariable=self.path_var,
            font=("Helvetica", 11),
            relief="solid", bd=1,
            bg="white", fg="#28251d",
            width=55
        )
        self.path_entry.grid(row=1, column=0, padx=(0, 8), ipady=5, sticky="ew")

        browse_btn = tk.Button(
            input_frame, text="浏览…",
            command=self._browse,
            font=("Helvetica", 10),
            bg="#e8e6e0", fg="#28251d",
            relief="flat", padx=12, pady=4,
            cursor="hand2",
            activebackground="#d4d1ca"
        )
        browse_btn.grid(row=1, column=1, padx=(0, 8))

        self.run_btn = tk.Button(
            input_frame, text="▶  执行清理",
            command=self._run,
            font=("Helvetica", 10, "bold"),
            bg="#01696f", fg="white",
            relief="flat", padx=14, pady=4,
            cursor="hand2",
            activebackground="#0c4e54"
        )
        self.run_btn.grid(row=1, column=2)

        input_frame.columnconfigure(0, weight=1)

        # ── 状态栏 ──
        self.status_var = tk.StringVar(value="就绪，请输入目录路径后点击执行")
        tk.Label(
            self, textvariable=self.status_var,
            font=("Helvetica", 9), fg="#7a7974", bg="#e8e6e0",
            anchor="w", padx=12, pady=4
        ).pack(fill="x")

        # ── 日志区 ──
        log_frame = tk.Frame(self, bg="#f5f5f0", padx=20, pady=8)
        log_frame.pack(fill="both", expand=True)

        header = tk.Frame(log_frame, bg="#f5f5f0")
        header.pack(fill="x", pady=(0, 6))
        tk.Label(
            header, text="执行日志",
            font=("Helvetica", 10, "bold"),
            fg="#28251d", bg="#f5f5f0"
        ).pack(side="left")
        tk.Button(
            header, text="清除日志",
            command=self._clear_log,
            font=("Helvetica", 9),
            bg="#e8e6e0", fg="#7a7974",
            relief="flat", padx=8, pady=2,
            cursor="hand2"
        ).pack(side="right")

        self.log_box = scrolledtext.ScrolledText(
            log_frame,
            font=("Courier New", 10),
            bg="#1c1b19", fg="#cdccca",
            relief="flat", bd=0,
            wrap="word", state="disabled",
            insertbackground="white"
        )
        self.log_box.pack(fill="both", expand=True)

        # ── 底部统计 ──
        self.summary_var = tk.StringVar(value="")
        tk.Label(
            self, textvariable=self.summary_var,
            font=("Helvetica", 10),
            fg="#28251d", bg="#f5f5f0",
            pady=8
        ).pack()

    # ── 事件处理 ────────────────────────────────
    def _browse(self):
        path = filedialog.askdirectory(title="选择目标文件夹")
        if path:
            self.path_var.set(path)

    def _run(self):
        path = self.path_var.get().strip()
        if not path:
            messagebox.showwarning("提示", "请先输入或选择目录路径")
            return
        if not os.path.isdir(path):
            messagebox.showerror("错误", f"路径不存在或不是有效目录：\n{path}")
            return

        self.run_btn.config(state="disabled", text="运行中…")
        self.status_var.set(f"正在扫描：{path}")
        self.summary_var.set("")
        self._log(f"🚀 开始扫描：{path}\n{'─'*60}")

        threading.Thread(target=self._worker, args=(path,), daemon=True).start()

    def _worker(self, path):
        try:
            deleted, failed = delete_empty_dirs(path, self._log)
            self.after(0, self._on_done, deleted, failed)
        except Exception as e:
            self.after(0, self._on_error, str(e))

    def _on_done(self, deleted, failed):
        self._log(f"{'─'*60}\n✨ 完成！共删除 {deleted} 个空目录，失败 {len(failed)} 个")
        self.summary_var.set(f"✅ 已删除 {deleted} 个空目录  |  ❌ 失败 {len(failed)} 个")
        self.status_var.set("执行完毕")
        self.run_btn.config(state="normal", text="▶  执行清理")

    def _on_error(self, msg):
        self._log(f"❌ 错误：{msg}")
        self.status_var.set("执行出错")
        messagebox.showerror("错误", msg)
        self.run_btn.config(state="normal", text="▶  执行清理")

    def _log(self, msg):
        """线程安全地向日志框追加文本"""
        def _append():
            self.log_box.config(state="normal")
            self.log_box.insert("end", msg + "\n")
            self.log_box.see("end")
            self.log_box.config(state="disabled")
        self.after(0, _append)

    def _clear_log(self):
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.config(state="disabled")
        self.summary_var.set("")


# ──────────────────────────────────────────────
if __name__ == "__main__":
    app = FolderCleanerApp()
    app.mainloop()
