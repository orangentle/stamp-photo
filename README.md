# stamp-photo

> Postage stamp style photo generator / 邮票风格照片生成器

把任意照片变成带齿孔花边的邮票风格图片，支持 5 种预设配色，可导出 PNG 或 PDF。

Turn any photo into a postage stamp style image with perforated edges. 5 preset color themes, export to PNG or PDF.

## Styles / 款式预览

| 天空蓝 | 尊贵金 | 经典红 | 森林绿 | 暗紫 |
|:---:|:---:|:---:|:---:|:---:|
| ![blue](samples/blue.png) | ![gold](samples/gold.png) | ![red](samples/red.png) | ![green](samples/green.png) | ![purple](samples/purple.png) |

## Features / 功能

- 5 种邮票款式：天空蓝、尊贵金、经典红、森林绿、暗紫
- GUI 图形界面，选图 → 选款式 → 导出，简单三步
- 实时预览效果
- 支持输入姓名显示在邮票底部
- 导出 PNG（透明背景）或 PDF（打印用）
- 300 DPI 高清输出，3.0cm × 4.0cm 含模切白边

## Installation / 安装

### 直接下载 exe（推荐）

前往 [Releases](https://github.com/orangentle/stamp-photo/releases) 下载最新版 `stamp-photo.exe`，双击运行即可。

### 从源码运行

```bash
git clone https://github.com/orangentle/stamp-photo.git
cd stamp-photo
pip install -r requirements.txt
python -m stamp_photo.gui
```

## Usage / 使用方法

1. 点击「选择图片」打开一张照片
2. 选择喜欢的款式（蓝/金/红/绿/紫）
3. 可选输入姓名，会显示在邮票底部
4. 选择输出格式 PNG 或 PDF
5. 点击「导出保存」

## Build exe / 打包

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name stamp-photo --clean -y \
  --hidden-import=stamp_photo \
  --hidden-import=stamp_photo.core \
  --hidden-import=stamp_photo.styles \
  --hidden-import=stamp_photo.fonts \
  --hidden-import=stamp_photo.gui \
  run.py
```

生成的 `dist/stamp-photo.exe` 即可独立运行。

## License / 许可证

[MIT](LICENSE)
