"""跨平台字体查找。"""

import platform
import os
import warnings
from PIL import ImageFont

# 各平台候选字体路径（优先 CJK 字体）
_FONT_CANDIDATES = {
    "Windows": [
        r"C:\Windows\Fonts\msyhbd.ttc",   # 微软雅黑 Bold
        r"C:\Windows\Fonts\msyh.ttc",     # 微软雅黑
        r"C:\Windows\Fonts\simhei.ttf",   # 黑体
        r"C:\Windows\Fonts\arial.ttf",
    ],
    "Darwin": [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/Library/Fonts/Arial.ttf",
    ],
    "Linux": [
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
}


def resolve_font(explicit_path=None, size=36):
    """
    返回一个 ImageFont 对象。

    Parameters
    ----------
    explicit_path : str, optional
        用户指定的字体文件路径，优先使用。
    size : int
        字号（像素）。
    """
    if explicit_path:
        if not os.path.isfile(explicit_path):
            raise FileNotFoundError(f"字体文件不存在: {explicit_path}")
        return ImageFont.truetype(explicit_path, size)

    system = platform.system()
    candidates = _FONT_CANDIDATES.get(system, [])

    for path in candidates:
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)

    warnings.warn(
        "未找到合适的字体文件，中文字符可能无法正确显示。"
        "可通过 font_path 参数指定字体。",
        stacklevel=2,
    )
    return ImageFont.load_default()
