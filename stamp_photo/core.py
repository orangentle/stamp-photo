"""邮票照片生成引擎。"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from .styles import get_style
from .fonts import resolve_font

# 邮票尺寸参数 (300 DPI)
DPI = 300
TARGET_W = round(2.6 / 2.54 * DPI)   # ~307px
TARGET_H = round(3.6 / 2.54 * DPI)   # ~425px
BLEED_MARGIN = round(0.2 / 2.54 * DPI)  # 2mm ~24px

# 齿孔与装饰参数
BORDER_WIDTH = 28
SCALLOP_RADIUS = 8
SCALLOP_SPACING = 4
INNER_LINE_WIDTH = 2
NAME_FONT_SIZE = 36


def crop_center_13_18(img):
    """居中裁剪为 13:18 比例（对应 26mm x 36mm）。"""
    w, h = img.size
    target_ratio = 13 / 18
    current_ratio = w / h

    if current_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    elif current_ratio < target_ratio:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))
    return img


def generate_stamp(input_image, style="blue", name="",
                   font_path=None, font_size=NAME_FONT_SIZE, dpi=DPI):
    """
    生成邮票风格照片。

    Parameters
    ----------
    input_image : str, Path, or PIL.Image.Image
        输入图片。
    style : str
        款式名称（blue/gold/red/green/purple）。
    name : str
        底部显示的姓名文字。
    font_path : str, optional
        自定义字体路径。
    font_size : int
        姓名字号。
    dpi : int
        输出 DPI。

    Returns
    -------
    PIL.Image.Image
        RGBA 模式的邮票图片（含模切白边）。
    """
    scheme = get_style(style)
    fill_top = scheme["border_fill_top"]
    fill_bot = scheme["border_fill_bot"]
    inner_line_color = scheme["inner_line"]

    # 读取图片
    if isinstance(input_image, (str, Path)):
        img = Image.open(input_image).convert("RGB")
    else:
        img = input_image.convert("RGB")

    # 裁切 13:18 并缩放
    img = crop_center_13_18(img)
    inner_w = TARGET_W - BORDER_WIDTH * 2
    inner_h = TARGET_H - BORDER_WIDTH * 2
    img = img.resize((inner_w, inner_h), Image.LANCZOS)

    # 渐变底色画布
    canvas = Image.new("RGB", (TARGET_W, TARGET_H))
    canvas_draw = ImageDraw.Draw(canvas)
    for y in range(TARGET_H):
        t = y / max(TARGET_H - 1, 1)
        r = int(fill_top[0] + (fill_bot[0] - fill_top[0]) * t)
        g = int(fill_top[1] + (fill_bot[1] - fill_top[1]) * t)
        b = int(fill_top[2] + (fill_bot[2] - fill_top[2]) * t)
        canvas_draw.line([(0, y), (TARGET_W, y)], fill=(r, g, b))
    canvas.paste(img, (BORDER_WIDTH, BORDER_WIDTH))

    # 内框装饰线
    draw = ImageDraw.Draw(canvas)
    x0 = BORDER_WIDTH - INNER_LINE_WIDTH - 2
    y0 = BORDER_WIDTH - INNER_LINE_WIDTH - 2
    x1 = TARGET_W - BORDER_WIDTH + INNER_LINE_WIDTH + 1
    y1 = TARGET_H - BORDER_WIDTH + INNER_LINE_WIDTH + 1
    for i in range(INNER_LINE_WIDTH):
        draw.rectangle([x0 - i, y0 - i, x1 + i, y1 + i], outline=inner_line_color)

    # 双金线（金色款式）
    if scheme.get("double_border"):
        inner_line2 = scheme["inner_line2"]
        gap = 4
        draw.rectangle(
            [x0 - INNER_LINE_WIDTH - gap, y0 - INNER_LINE_WIDTH - gap,
             x1 + INNER_LINE_WIDTH + gap, y1 + INNER_LINE_WIDTH + gap],
            outline=inner_line2,
        )

    # 姓名文字
    name_font = resolve_font(font_path, font_size)
    name_fill = scheme["name_fill"]
    name_outline = scheme["name_outline"]

    txt_layer = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
    txt_draw = ImageDraw.Draw(txt_layer)

    if name:
        max_name_w = inner_w - 16
        name_bbox = txt_draw.textbbox((0, 0), name, font=name_font)
        name_w = name_bbox[2] - name_bbox[0]

        if name_w > max_name_w and len(name) > 1:
            mid = len(name) // 2
            best = None
            for sep in ["/", " ", "_"]:
                for offset in range(len(name)):
                    for pos in [mid + offset, mid - offset]:
                        if 0 < pos < len(name) and name[pos] == sep:
                            best = pos
                            break
                    if best is not None:
                        break
                if best is not None:
                    break
            if best is None:
                best = mid
            line1 = name[:best].rstrip("/ _")
            line2 = name[best:].lstrip("/ _")
            name_text = f"{line1}\n{line2}"
        else:
            name_text = name

        name_bbox = txt_draw.textbbox((0, 0), name_text, font=name_font, align="center")
        name_w = name_bbox[2] - name_bbox[0]
        name_h = name_bbox[3] - name_bbox[1]
        name_x = (TARGET_W - name_w) // 2
        name_y = TARGET_H - BORDER_WIDTH - name_h - 12

        # 描边
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx or dy:
                    txt_draw.text(
                        (name_x + dx, name_y + dy), name_text,
                        font=name_font, fill=name_outline, align="center",
                    )
        txt_draw.text(
            (name_x, name_y), name_text,
            font=name_font, fill=name_fill, align="center",
        )

    canvas = Image.alpha_composite(canvas.convert("RGBA"), txt_layer).convert("RGB")

    # 齿孔蒙版
    cw, ch = TARGET_W, TARGET_H
    mask = Image.new("L", (cw, ch), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rectangle([0, 0, cw - 1, ch - 1], fill=255)

    step = SCALLOP_RADIUS * 2 + SCALLOP_SPACING
    sr = SCALLOP_RADIUS

    for x in range(BORDER_WIDTH, cw - BORDER_WIDTH, step):
        cx = x + sr
        mask_draw.ellipse([cx - sr, -sr, cx + sr, sr], fill=0)
        mask_draw.ellipse([cx - sr, ch - sr, cx + sr, ch + sr], fill=0)
    for y in range(BORDER_WIDTH, ch - BORDER_WIDTH, step):
        cy = y + sr
        mask_draw.ellipse([-sr, cy - sr, sr, cy + sr], fill=0)
        mask_draw.ellipse([cw - sr, cy - sr, cw + sr, cy + sr], fill=0)
    for cx, cy in [(0, 0), (cw, 0), (0, ch), (cw, ch)]:
        mask_draw.ellipse([cx - sr, cy - sr, cx + sr, cy + sr], fill=0)

    # 齿孔光晕
    edge_layer = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    edge_draw = ImageDraw.Draw(edge_layer)
    glow_r = sr + 3
    glow_color = (255, 255, 255, 60)

    for x in range(BORDER_WIDTH, cw - BORDER_WIDTH, step):
        cx = x + sr
        edge_draw.ellipse([cx - glow_r, -glow_r, cx + glow_r, glow_r], fill=glow_color)
        edge_draw.ellipse([cx - glow_r, ch - glow_r, cx + glow_r, ch + glow_r], fill=glow_color)
    for y in range(BORDER_WIDTH, ch - BORDER_WIDTH, step):
        cy = y + sr
        edge_draw.ellipse([-glow_r, cy - glow_r, glow_r, cy + glow_r], fill=glow_color)
        edge_draw.ellipse([cw - glow_r, cy - glow_r, cw + glow_r, cy + glow_r], fill=glow_color)
    for cx, cy in [(0, 0), (cw, 0), (0, ch), (cw, ch)]:
        edge_draw.ellipse([cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r], fill=glow_color)

    canvas_rgba = Image.alpha_composite(canvas.convert("RGBA"), edge_layer)
    canvas_rgba.putalpha(mask)

    # 模切白边
    final_w = TARGET_W + BLEED_MARGIN * 2
    final_h = TARGET_H + BLEED_MARGIN * 2
    final_canvas = Image.new("RGBA", (final_w, final_h), (255, 255, 255, 255))
    final_canvas.paste(canvas_rgba, (BLEED_MARGIN, BLEED_MARGIN), mask=canvas_rgba.split()[3])

    return final_canvas


def save_stamp(image, output_path, dpi=DPI):
    """
    保存邮票图片。根据扩展名自动选择 PNG 或 PDF 格式。

    Returns
    -------
    Path
        保存的文件路径。
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    ext = output_path.suffix.lower()
    if ext == ".pdf":
        white_bg = Image.new("RGB", image.size, (255, 255, 255))
        white_bg.paste(image, mask=image.split()[3])
        white_bg.save(str(output_path), "PDF", resolution=dpi, quality=100)
    else:
        image.save(str(output_path), dpi=(dpi, dpi))

    return output_path
