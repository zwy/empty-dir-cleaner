#!/usr/bin/env python3
"""
png_to_icon.py — 将 PNG 图片转换为 .ico（Windows）和 .icns（macOS）

用法：
    python png_to_icon.py <图片路径>

示例：
    python png_to_icon.py ~/Desktop/my_icon.png
    python png_to_icon.py /Users/xxx/app_icon.png

输出：与输入 PNG 同目录，生成同名的 .ico 和 .icns 文件。

依赖：
    pip install pillow
"""

import sys
import os
import io
import struct

# ── 检查依赖 ────────────────────────────────────────────
try:
    from PIL import Image
except ImportError:
    print("❌ 缺少依赖，请先执行：pip install pillow")
    sys.exit(1)


# ── 生成 .ico（Windows）────────────────────────────────
def convert_to_ico(img: Image.Image, output_path: str):
    """
    内嵌 6 种标准尺寸：16 / 32 / 48 / 64 / 128 / 256
    系统会自动按场景（桌面、任务栏、文件管理器）选用对应尺寸。
    """
    sizes = [16, 32, 48, 64, 128, 256]
    images = [img.resize((s, s), Image.LANCZOS) for s in sizes]
    images[0].save(
        output_path,
        format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=images[1:],
    )


# ── 生成 .icns（macOS）────────────────────────────────
def convert_to_icns(img: Image.Image, output_path: str):
    """
    手动封装 icns 二进制格式，内嵌 7 种尺寸：
    16 / 32 / 64 / 128 / 256 / 512 / 1024（Retina）
    """
    ICNS_ENTRIES = [
        (16,   b"icp4"),
        (32,   b"icp5"),
        (64,   b"icp6"),
        (128,  b"ic07"),
        (256,  b"ic08"),
        (512,  b"ic09"),
        (1024, b"ic10"),
    ]

    chunks = []
    for size, tag in ICNS_ENTRIES:
        resized = img.resize((size, size), Image.LANCZOS)
        buf = io.BytesIO()
        resized.save(buf, format="PNG")
        data = buf.getvalue()
        # 每个 chunk = tag(4B) + 总长度(4B, 含头) + PNG 数据
        chunks.append(tag + struct.pack(">I", 8 + len(data)) + data)

    body = b"".join(chunks)
    with open(output_path, "wb") as f:
        f.write(b"icns")                      # magic
        f.write(struct.pack(">I", 8 + len(body)))  # 文件总长度
        f.write(body)


# ── 主流程 ──────────────────────────────────────────────
def main():
    # 参数检查
    if len(sys.argv) != 2:
        print("用法：python png_to_icon.py <PNG图片路径>")
        print("示例：python png_to_icon.py app_icon.png")
        sys.exit(1)

    input_path = sys.argv[1]

    if not os.path.isfile(input_path):
        print(f"❌ 文件不存在：{input_path}")
        sys.exit(1)

    if not input_path.lower().endswith(".png"):
        print("⚠️  建议输入 PNG 格式文件（其他格式可能导致透明度丢失）")

    # 确定输出路径（与输入同目录，同名不同后缀）
    base = os.path.splitext(input_path)[0]
    ico_path  = base + ".ico"
    icns_path = base + ".icns"

    # 加载图片，强制转为 RGBA（保留透明通道）
    try:
        img = Image.open(input_path).convert("RGBA")
    except Exception as e:
        print(f"❌ 无法打开图片：{e}")
        sys.exit(1)

    print(f"📂 输入：{input_path}  ({img.size[0]}×{img.size[1]} px)")

    # 转换
    try:
        convert_to_ico(img, ico_path)
        size_ico = os.path.getsize(ico_path)
        print(f"✅ Windows .ico → {ico_path}  ({size_ico // 1024} KB，含 6 种尺寸)")
    except Exception as e:
        print(f"❌ 生成 .ico 失败：{e}")

    try:
        convert_to_icns(img, icns_path)
        size_icns = os.path.getsize(icns_path)
        print(f"✅ macOS  .icns → {icns_path}  ({size_icns // 1024} KB，含 7 种尺寸)")
    except Exception as e:
        print(f"❌ 生成 .icns 失败：{e}")

    print("\n🎉 完成！")
    print(f"   打包 Windows 程序：pyinstaller --icon {ico_path}  ...")
    print(f"   打包 macOS  程序：pyinstaller --icon {icns_path} ...")


if __name__ == "__main__":
    main()
