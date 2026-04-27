# 🗂 空目录清理工具 (Empty Directory Cleaner)

一个基于 Python + Tkinter 的桌面 GUI 工具，递归扫描指定文件夹，**一键删除所有空目录**。

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python) ![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey) ![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ 功能特性

- 📁 支持手动输入路径或点击「浏览」选择目录
- 🔁 自底向上递归扫描，正确处理多层嵌套空目录
- 🖥 实时日志滚动展示每一条删除记录
- 🧵 子线程执行，界面不卡死
- ✅ / ❌ 区分成功与失败，底部汇总统计

---

## 🖼 界面预览

```
┌─────────────────────────────────────────┐
│  🗂  空目录清理工具                      │  ← 标题栏
├─────────────────────────────────────────┤
│  目标文件夹路径                          │
│  [/path/to/folder    ] [浏览…] [▶ 执行] │  ← 输入区
├─────────────────────────────────────────┤
│  正在扫描：/path/to/folder               │  ← 状态栏
├─────────────────────────────────────────┤
│  执行日志                    [清除日志]  │
│  🚀 开始扫描：/path/to/folder            │
│  ✅ 已删除：/path/to/folder/empty_sub   │  ← 日志区
│  ✨ 完成！共删除 3 个空目录，失败 0 个   │
├─────────────────────────────────────────┤
│  ✅ 已删除 3 个空目录  |  ❌ 失败 0 个   │  ← 统计栏
└─────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 方式一：直接运行源码（需要 Python）

**环境要求：** Python 3.8+（Tkinter 为标准库，无需额外安装）

```bash
# 克隆仓库
git clone https://github.com/zwy/empty-dir-cleaner.git
cd empty-dir-cleaner

# 直接运行
python app.py
```

### 方式二：打包成可执行文件（双击运行，无需 Python）

```bash
# 安装打包工具
pip install pyinstaller

# Windows → 生成 dist/空目录清理工具.exe
pyinstaller --onefile --windowed --name "空目录清理工具" app.py

# macOS → 生成 dist/空目录清理工具.app
pyinstaller --onefile --windowed --name "空目录清理工具" app.py
```

打包完成后，在 `dist/` 目录找到生成的文件，双击即可运行。

> **说明：** `--onefile` 将所有依赖打包进单个文件；`--windowed` 避免弹出黑色命令行窗口。

---

## 📖 使用说明

1. **输入路径** — 在输入框中粘贴目标文件夹的完整路径，或点击「浏览…」通过文件选择器选择。
2. **点击执行** — 点击「▶ 执行清理」按钮，程序开始递归扫描。
3. **查看日志** — 日志区实时滚动显示每一条删除记录：
   - `✅ 已删除：路径` — 删除成功
   - `❌ 失败：路径 (原因)` — 删除失败（权限不足等）
4. **查看结果** — 底部统计栏显示总删除数和失败数。
5. **清除日志** — 点击右上角「清除日志」可清空日志区。

> ⚠️ **注意：** 删除操作不可撤销，请确认目标路径正确后再执行。根目录本身不会被删除。

---

## 🛠 打包参数说明

| 参数 | 说明 |
|---|---|
| `--onefile` / `-F` | 打包成单个可执行文件 |
| `--windowed` / `-w` | 不弹出黑色命令行窗口（GUI 程序必加）|
| `--name "名称"` | 设置输出文件名称 |
| `--icon app.ico` | 自定义程序图标（Windows 用 `.ico`）|

---

## 📁 项目结构

```
empty-dir-cleaner/
├── app.py           # 主程序（GUI + 核心逻辑）
├── requirements.txt # 依赖说明（仅打包时需要）
└── README.md        # 使用文档
```

---

## 🔧 核心逻辑说明

程序使用 `os.walk(topdown=False)` **自底向上**遍历目录树，确保先处理最深层的空目录，再向上判断父目录是否因此变空，从而正确处理多层嵌套的空目录结构。

```python
for dirpath, dirnames, filenames in os.walk(root_path, topdown=False):
    if not os.listdir(dirpath):  # 目录为空
        os.rmdir(dirpath)        # 删除
```

GUI 使用 `threading.Thread` + `self.after()` 回调机制，在子线程中执行文件操作，在主线程中更新界面，避免界面冻结。

---

## 📄 License

MIT License — 自由使用、修改和分发。
