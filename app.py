import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import hashlib
import threading
from collections import defaultdict


# ══════════════════════════════════════════════════════════════
# 核心业务逻辑（与 GUI 解耦）
# ══════════════════════════════════════════════════════════════

def delete_empty_dirs(root_path, log_cb):
    """删除空目录（自底向上）"""
    if not os.path.isdir(root_path):
        raise ValueError(f"路径不存在：{root_path}")
    deleted, failed = 0, []
    for dirpath, _, _ in os.walk(root_path, topdown=False):
        if dirpath == root_path:
            continue
        try:
            if not os.listdir(dirpath):
                os.rmdir(dirpath)
                deleted += 1
                log_cb(f"✅ 已删除空目录：{dirpath}")
        except Exception as e:
            failed.append(dirpath)
            log_cb(f"❌ 失败：{dirpath}  ({e})")
    return deleted, failed


def delete_empty_files(root_path, log_cb):
    """删除大小为 0 的文件"""
    if not os.path.isdir(root_path):
        raise ValueError(f"路径不存在：{root_path}")
    deleted, failed = 0, []
    for dirpath, _, filenames in os.walk(root_path):
        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            try:
                if os.path.getsize(fpath) == 0:
                    os.remove(fpath)
                    deleted += 1
                    log_cb(f"✅ 已删除空文件：{fpath}")
            except Exception as e:
                failed.append(fpath)
                log_cb(f"❌ 失败：{fpath}  ({e})")
    return deleted, failed


def delete_duplicate_files(root_path, log_cb):
    """删除重复文件（保留每组中最先发现的一个）"""
    if not os.path.isdir(root_path):
        raise ValueError(f"路径不存在：{root_path}")

    def md5(path, chunk=65536):
        h = hashlib.md5()
        with open(path, "rb") as f:
            while chunk_data := f.read(chunk):
                h.update(chunk_data)
        return h.hexdigest()

    # 先按文件大小分组，再对同尺寸文件计算 MD5
    size_map = defaultdict(list)
    for dirpath, _, filenames in os.walk(root_path):
        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            try:
                size_map[os.path.getsize(fpath)].append(fpath)
            except Exception:
                pass

    hash_map = defaultdict(list)
    for size, paths in size_map.items():
        if len(paths) < 2:
            continue
        for p in paths:
            try:
                hash_map[md5(p)].append(p)
            except Exception as e:
                log_cb(f"⚠️ 跳过（读取失败）：{p}  ({e})")

    deleted, failed = 0, []
    for h, paths in hash_map.items():
        if len(paths) < 2:
            continue
        keep = paths[0]
        log_cb(f"📌 保留：{keep}")
        for dup in paths[1:]:
            try:
                os.remove(dup)
                deleted += 1
                log_cb(f"  ✅ 删除重复：{dup}")
            except Exception as e:
                failed.append(dup)
                log_cb(f"  ❌ 失败：{dup}  ({e})")
    return deleted, failed


def delete_by_extension(root_path, extensions, log_cb):
    """
    删除指定后缀的文件。
    extensions: list[str]，如 [".DS_Store", ".Thumbs.db"]
    """
    if not os.path.isdir(root_path):
        raise ValueError(f"路径不存在：{root_path}")
    exts = {e.lower().strip() for e in extensions if e.strip()}
    deleted, failed = 0, []
    for dirpath, _, filenames in os.walk(root_path):
        for fname in filenames:
            _, ext = os.path.splitext(fname)
            match_name = fname.lower() in exts
            match_ext  = ext.lower() in exts
            if match_name or match_ext:
                fpath = os.path.join(dirpath, fname)
                try:
                    os.remove(fpath)
                    deleted += 1
                    log_cb(f"✅ 已删除：{fpath}")
                except Exception as e:
                    failed.append(fpath)
                    log_cb(f"❌ 失败：{fpath}  ({e})")
    return deleted, failed


def calc_folder_size(root_path, log_cb):
    """统计文件夹及各子文件夹的大小"""
    if not os.path.isdir(root_path):
        raise ValueError(f"路径不存在：{root_path}")

    def fmt(n):
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if n < 1024:
                return f"{n:.1f} {unit}"
            n /= 1024
        return f"{n:.1f} PB"

    # 统计根目录总大小
    grand = 0
    for dp, _, fns in os.walk(root_path):
        for fn in fns:
            try:
                grand += os.path.getsize(os.path.join(dp, fn))
            except Exception:
                pass

    # 统计第一层子目录大小
    entries = []
    try:
        for name in os.listdir(root_path):
            sub = os.path.join(root_path, name)
            if not os.path.isdir(sub):
                continue
            sub_total = 0
            for dp2, _, fns in os.walk(sub):
                for fn in fns:
                    try:
                        sub_total += os.path.getsize(os.path.join(dp2, fn))
                    except Exception:
                        pass
            entries.append((sub_total, name))
    except Exception:
        pass

    entries.sort(reverse=True)

    log_cb(f"📦 总大小：{fmt(grand)}  （{root_path}）")
    log_cb("─" * 60)
    if entries:
        for size, name in entries:
            bar_len = int(size / grand * 30) if grand else 0
            bar = "█" * bar_len + "░" * (30 - bar_len)
            log_cb(f"  {bar}  {fmt(size):>10}  {name}")
    else:
        log_cb("  （无子目录）")
    return grand, len(entries)


# ══════════════════════════════════════════════════════════════
# 公共样式常量
# ══════════════════════════════════════════════════════════════

BG       = "#f5f5f0"
BG2      = "#e8e6e0"
TEAL     = "#01696f"
TEAL_HVR = "#0c4e54"
TEXT     = "#28251d"
MUTED    = "#7a7974"
DARK_BG  = "#1c1b19"
DARK_FG  = "#cdccca"


# ══════════════════════════════════════════════════════════════
# 公共 UI 组件
# ══════════════════════════════════════════════════════════════

def make_path_bar(parent, btn_text="▶  执行", btn_cmd=None):
    """顶部路径输入栏，返回 (path_var, run_btn, status_var)"""
    frame = tk.Frame(parent, bg=BG, padx=20, pady=14)
    frame.pack(fill="x")

    tk.Label(frame, text="目标文件夹路径",
             font=("Helvetica", 10, "bold"), fg=TEXT, bg=BG
             ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 6))

    path_var = tk.StringVar()
    tk.Entry(frame, textvariable=path_var,
             font=("Helvetica", 11), relief="solid", bd=1,
             bg="white", fg=TEXT, width=50
             ).grid(row=1, column=0, padx=(0, 8), ipady=5, sticky="ew")

    def browse():
        p = filedialog.askdirectory(title="选择目标文件夹")
        if p:
            path_var.set(p)

    tk.Button(frame, text="浏览…", command=browse,
              font=("Helvetica", 10), bg=BG2, fg=TEXT,
              relief="flat", padx=10, pady=4, cursor="hand2",
              activebackground="#d4d1ca"
              ).grid(row=1, column=1, padx=(0, 8))

    run_btn = tk.Button(frame, text=btn_text, command=btn_cmd,
                        font=("Helvetica", 10, "bold"),
                        bg=TEAL, fg="white", relief="flat",
                        padx=14, pady=4, cursor="hand2",
                        activebackground=TEAL_HVR)
    run_btn.grid(row=1, column=2)
    frame.columnconfigure(0, weight=1)

    status_var = tk.StringVar(value="就绪")
    tk.Label(parent, textvariable=status_var,
             font=("Helvetica", 9), fg=MUTED, bg=BG2,
             anchor="w", padx=12, pady=4).pack(fill="x")

    return path_var, run_btn, status_var


def make_log_area(parent):
    """日志区，返回 (log_box, summary_var)"""
    outer = tk.Frame(parent, bg=BG, padx=20, pady=8)
    outer.pack(fill="both", expand=True)

    hdr = tk.Frame(outer, bg=BG)
    hdr.pack(fill="x", pady=(0, 6))
    tk.Label(hdr, text="执行日志",
             font=("Helvetica", 10, "bold"), fg=TEXT, bg=BG).pack(side="left")

    log_box = scrolledtext.ScrolledText(
        outer, font=("Courier New", 10),
        bg=DARK_BG, fg=DARK_FG,
        relief="flat", bd=0, wrap="word",
        state="disabled", insertbackground="white")
    log_box.pack(fill="both", expand=True)

    def clear():
        log_box.config(state="normal")
        log_box.delete("1.0", "end")
        log_box.config(state="disabled")
        summary_var.set("")

    tk.Button(hdr, text="清除日志", command=clear,
              font=("Helvetica", 9), bg=BG2, fg=MUTED,
              relief="flat", padx=8, pady=2, cursor="hand2"
              ).pack(side="right")

    summary_var = tk.StringVar(value="")
    tk.Label(parent, textvariable=summary_var,
             font=("Helvetica", 10), fg=TEXT, bg=BG, pady=6).pack()

    return log_box, summary_var


def log_append(root_win, log_box, msg):
    """线程安全写日志"""
    def _do():
        log_box.config(state="normal")
        log_box.insert("end", msg + "\n")
        log_box.see("end")
        log_box.config(state="disabled")
    root_win.after(0, _do)


def validate_path(path):
    if not path:
        messagebox.showwarning("提示", "请先选择目录路径")
        return False
    if not os.path.isdir(path):
        messagebox.showerror("错误", f"路径无效：\n{path}")
        return False
    return True


# ══════════════════════════════════════════════════════════════
# Tab 基类（减少每个 Tab 的重复代码）
# ══════════════════════════════════════════════════════════════

class BaseTab(tk.Frame):
    btn_label  = "▶  执行"
    btn_label2 = "▶  执行"  # 执行中还原用

    def __init__(self, parent, root_win):
        super().__init__(parent, bg=BG)
        self.root_win = root_win
        self.path_var, self.run_btn, self.status_var = make_path_bar(
            self, btn_text=self.btn_label, btn_cmd=self._on_run)
        self._extra_ui()
        self.log_box, self.summary_var = make_log_area(self)

    def _extra_ui(self):
        """子类可覆盖，在日志区之前插入额外控件"""
        pass

    def _on_run(self):
        path = self.path_var.get().strip()
        if not validate_path(path):
            return
        if not self._confirm(path):
            return
        self.run_btn.config(state="disabled", text="运行中…")
        self.status_var.set(f"正在处理：{path}")
        self.summary_var.set("")
        log_append(self.root_win, self.log_box,
                   f"🚀 开始：{path}\n{'─'*60}")
        threading.Thread(target=self._worker, args=(path,), daemon=True).start()

    def _confirm(self, path):
        return True

    def _worker(self, path):
        raise NotImplementedError

    def _finish(self, summary):
        log_append(self.root_win, self.log_box,
                   f"{'─'*60}\n✨ 完成！{summary}")
        self.summary_var.set(summary)
        self.status_var.set("执行完毕")
        self.run_btn.config(state="normal", text=self.btn_label)

    def _cb(self, msg):
        log_append(self.root_win, self.log_box, msg)


# ══════════════════════════════════════════════════════════════
# Tab 1 — 删除空目录
# ══════════════════════════════════════════════════════════════

class TabEmptyDir(BaseTab):
    btn_label = "▶  执行清理"

    def _worker(self, path):
        try:
            deleted, failed = delete_empty_dirs(path, self._cb)
            s = f"✅ 已删除 {deleted} 个空目录  |  ❌ 失败 {len(failed)} 个"
            self.root_win.after(0, self._finish, s)
        except Exception as e:
            self.root_win.after(0, self._err, str(e))

    def _err(self, msg):
        messagebox.showerror("错误", msg)
        self.run_btn.config(state="normal", text=self.btn_label)


# ══════════════════════════════════════════════════════════════
# Tab 2 — 删除空文件
# ══════════════════════════════════════════════════════════════

class TabEmptyFile(BaseTab):
    btn_label = "▶  执行清理"

    def _worker(self, path):
        try:
            deleted, failed = delete_empty_files(path, self._cb)
            s = f"✅ 已删除 {deleted} 个空文件  |  ❌ 失败 {len(failed)} 个"
            self.root_win.after(0, self._finish, s)
        except Exception as e:
            self.root_win.after(0, lambda: messagebox.showerror("错误", str(e)))
            self.root_win.after(0, lambda: self.run_btn.config(state="normal", text=self.btn_label))


# ══════════════════════════════════════════════════════════════
# Tab 3 — 删除重复文件
# ══════════════════════════════════════════════════════════════

class TabDuplicates(BaseTab):
    btn_label = "▶  扫描并删除"

    def _extra_ui(self):
        tk.Label(self,
                 text="⚠️  每组重复文件保留最先发现的一个，其余全部删除，操作不可撤销",
                 font=("Helvetica", 9), fg="#964219", bg=BG
                 ).pack(anchor="w", padx=20, pady=(0, 4))

    def _confirm(self, path):
        return messagebox.askyesno(
            "确认操作",
            f"将扫描并删除以下目录中的重复文件：\n{path}\n\n每组保留第一个，其余删除，操作不可撤销。\n\n确定继续？")

    def _worker(self, path):
        try:
            deleted, failed = delete_duplicate_files(path, self._cb)
            s = f"✅ 已删除 {deleted} 个重复文件  |  ❌ 失败 {len(failed)} 个"
            self.root_win.after(0, self._finish, s)
        except Exception as e:
            self.root_win.after(0, lambda: messagebox.showerror("错误", str(e)))
            self.root_win.after(0, lambda: self.run_btn.config(state="normal", text=self.btn_label))


# ══════════════════════════════════════════════════════════════
# Tab 4 — 按后缀删除
# ══════════════════════════════════════════════════════════════

class TabByExtension(BaseTab):
    btn_label = "▶  执行删除"

    def _extra_ui(self):
        ext_frame = tk.Frame(self, bg=BG, padx=20, pady=6)
        ext_frame.pack(fill="x")
        tk.Label(ext_frame, text="指定文件名或后缀（逗号分隔）：",
                 font=("Helvetica", 10, "bold"), fg=TEXT, bg=BG).pack(side="left")
        self.ext_var = tk.StringVar(value=".DS_Store, Thumbs.db, .log, .tmp")
        tk.Entry(ext_frame, textvariable=self.ext_var,
                 font=("Helvetica", 11), relief="solid", bd=1,
                 bg="white", fg=TEXT, width=40
                 ).pack(side="left", padx=(8, 0), ipady=4)
        tk.Label(self,
                 text="💡 直接写文件名（如 .DS_Store）或以 . 开头的后缀（如 .log）",
                 font=("Helvetica", 9), fg=MUTED, bg=BG
                 ).pack(anchor="w", padx=20, pady=(0, 2))

    def _confirm(self, path):
        raw = self.ext_var.get().strip()
        if not raw:
            messagebox.showwarning("提示", "请输入要删除的文件名或后缀")
            return False
        self._exts = [e.strip() for e in raw.split(",") if e.strip()]
        return messagebox.askyesno(
            "确认操作",
            f"将删除以下类型文件：\n{', '.join(self._exts)}\n\n目录：{path}\n\n确定继续？")

    def _worker(self, path):
        try:
            deleted, failed = delete_by_extension(path, self._exts, self._cb)
            s = f"✅ 已删除 {deleted} 个文件  |  ❌ 失败 {len(failed)} 个"
            self.root_win.after(0, self._finish, s)
        except Exception as e:
            self.root_win.after(0, lambda: messagebox.showerror("错误", str(e)))
            self.root_win.after(0, lambda: self.run_btn.config(state="normal", text=self.btn_label))


# ══════════════════════════════════════════════════════════════
# Tab 5 — 文件夹大小统计
# ══════════════════════════════════════════════════════════════

class TabFolderSize(BaseTab):
    btn_label = "📊  统计大小"

    def _on_run(self):
        path = self.path_var.get().strip()
        if not validate_path(path):
            return
        self.run_btn.config(state="disabled", text="统计中…")
        self.status_var.set(f"正在统计：{path}")
        self.summary_var.set("")
        log_append(self.root_win, self.log_box,
                   f"📊 开始统计：{path}\n{'─'*60}")
        threading.Thread(target=self._worker, args=(path,), daemon=True).start()

    def _worker(self, path):
        def fmt(n):
            for unit in ("B", "KB", "MB", "GB", "TB"):
                if n < 1024:
                    return f"{n:.1f} {unit}"
                n /= 1024
            return f"{n:.1f} PB"
        try:
            grand, count = calc_folder_size(path, self._cb)
            s = f"📦 总大小：{fmt(grand)}  |  子目录数：{count}"
            self.root_win.after(0, self._finish, s)
        except Exception as e:
            self.root_win.after(0, lambda: messagebox.showerror("错误", str(e)))
            self.root_win.after(0, lambda: self.run_btn.config(state="normal", text=self.btn_label))

    def _finish(self, summary):
        log_append(self.root_win, self.log_box, f"{'─'*60}\n✨ 统计完成")
        self.summary_var.set(summary)
        self.status_var.set("统计完毕")
        self.run_btn.config(state="normal", text=self.btn_label)


# ══════════════════════════════════════════════════════════════
# 主窗口
# ══════════════════════════════════════════════════════════════

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("文件清理工具箱")
        self.geometry("780x580")
        self.minsize(680, 500)
        self.resizable(True, True)
        self.configure(bg=BG)
        self._build()

    def _build(self):
        # 顶部标题栏
        hdr = tk.Frame(self, bg=TEAL, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🧰  文件清理工具箱",
                 font=("Helvetica", 16, "bold"),
                 fg="white", bg=TEAL).pack()

        # Tab 样式
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab",
                        font=("Helvetica", 10),
                        padding=[14, 6],
                        background=BG2, foreground=MUTED)
        style.map("TNotebook.Tab",
                  background=[("selected", "white")],
                  foreground=[("selected", TEAL)])

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        for label, cls in [
            ("  🗂 空目录  ",   TabEmptyDir),
            ("  📄 空文件  ",   TabEmptyFile),
            ("  ♻️ 重复文件 ",  TabDuplicates),
            ("  🗑 按后缀  ",   TabByExtension),
            ("  📊 大小统计 ",  TabFolderSize),
        ]:
            frame = cls(nb, self)
            nb.add(frame, text=label)


if __name__ == "__main__":
    app = App()
    app.mainloop()
