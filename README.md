# 🗂 空目录清理工具 (Empty Directory Cleaner)

一个基于 Python + Tkinter 的桌面 GUI 工具，递归扫描指定文件夹，**一键删除所有空目录**。

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python) ![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey) ![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ 功能特性

- 📁 支持手动输入路径或点击「浏览」选择目录
- 🔄 自底向上递归扫描，正确处理多层嵌套空目录
- 🖥 实时日志滚动显示每一条删除记录
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

**第一步：安装打包工具**

```bash
pip install pyinstaller
```

**第二步：执行打包命令**

```bash
# Windows → 生成 dist/空目录清理工具.exe
pyinstaller --onefile --windowed --name "空目录清理工具" --icon app_icon.ico app.py

# macOS → 生成 dist/空目录清理工具.app
pyinstaller --onedir --windowed --name "空目录清理工具" --icon app_icon.icns app.py
```

**第三步：找到生成文件**

```
dist/
└── 空目录清理工具.exe   ← Windows 双击此文件运行
└── 空目录清理工具.app   ← macOS 双击此文件运行
```

> 打包完成后 `build/` 和 `*.spec` 为临时文件，可以删除。

---

## 🛠 打包参数说明

| 参数 | 说明 |
|---|---|
| `--onefile` / `-F` | 打包成**单个**可执行文件，便于分发 |
| `--windowed` / `-w` | 不弹出黑色命令行窗口（GUI 程序必加）|
| `--name "名称"` | 设置生成的程序文件名 |
| `--icon app_icon.ico` | Windows 程序图标（`.ico` 格式）|
| `--icon app_icon.icns` | macOS 程序图标（`.icns` 格式）|

---

## ❓ 常见问题

**Q：打包后启动很慢（要等 10 秒以上）？**

`--onefile` 模式每次启动会先解压到临时目录，属于正常现象。如希望秒开，改用 `--onedir` 模式（生成一个文件夹而非单文件）：

```bash
pyinstaller --onedir --windowed --name "空目录清理工具" --icon app_icon.ico app.py
```

**Q：Windows 提示「无法验证发布者」或被杀毒软件拦截？**

PyInstaller 打包的程序在 Windows 首次运行时可能触发 SmartScreen 警告，选择「仍要运行」即可，这是未签名程序的通用问题，与本工具本身无关。

**Q：macOS 提示「无法打开，因为无法验证开发者」？**

右键点击 `.app` → 选择「打开」→ 确认，之后就可以正常运行。

**Q：能在 Windows 上打包出 macOS 的 .app 文件吗？**

不能。PyInstaller 只能为**当前操作系统**生成对应的可执行文件，需要分别在 Windows 和 macOS 上各自打包。

---

## 🎨 图标文件说明

| 文件 | 格式 | 用途 |
|---|---|---|
| `app_icon.png` | PNG 1024×1024 | 原始图标源文件 |
| `app_icon.ico` | ICO（含 6 种尺寸）| Windows 打包用 |
| `app_icon.icns` | ICNS（含 7 种尺寸）| macOS 打包用 |

如需将其他 PNG 转换为图标格式，可使用仓库中附带的转换脚本：

```bash
pip install pillow
python png_to_icon.py your_image.png
# 在同目录生成 your_image.ico 和 your_image.icns
```

---

## 📁 项目结构

```
empty-dir-cleaner/
├── app.py            # 主程序（GUI + 核心逻辑）
├── app_icon.png      # 原始图标（PNG 1024×1024）
├── app_icon.ico      # Windows 图标
├── app_icon.icns     # macOS 图标
├── png_to_icon.py    # PNG → ICO / ICNS 转换工具
├── requirements.txt  # 依赖说明（打包时需要 pyinstaller）
└── README.md         # 使用文档
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

> ⚠️ **注意：** 删除操作不可撤销，请确认目标路径正确后再执行。根目录本身不会被删除。

---

## 📄 License

MIT License — 自由使用、修改和分发。
