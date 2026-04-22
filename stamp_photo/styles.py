"""邮票款式配色方案定义。"""

STYLES = {
    "blue": {
        "label": "天空蓝",
        "label_en": "Sky Blue",
        "border_fill_top": (155, 220, 255),
        "border_fill_bot": (100, 175, 240),
        "inner_line": (100, 180, 240),
        "double_border": False,
        "name_fill": (255, 255, 255, 255),
        "name_outline": (50, 120, 200, 230),
    },
    "gold": {
        "label": "尊贵金",
        "label_en": "Royal Gold",
        "border_fill_top": (28, 18, 10),
        "border_fill_bot": (28, 18, 10),
        "inner_line": (218, 165, 32),
        "inner_line2": (180, 140, 28),
        "double_border": True,
        "name_fill": (255, 223, 100, 255),
        "name_outline": (0, 0, 0, 240),
    },
    "red": {
        "label": "经典红",
        "label_en": "Classic Red",
        "border_fill_top": (255, 130, 120),
        "border_fill_bot": (200, 40, 40),
        "inner_line": (220, 60, 60),
        "double_border": False,
        "name_fill": (255, 255, 255, 255),
        "name_outline": (140, 20, 20, 230),
    },
    "green": {
        "label": "森林绿",
        "label_en": "Forest Green",
        "border_fill_top": (130, 210, 140),
        "border_fill_bot": (34, 120, 60),
        "inner_line": (50, 150, 70),
        "double_border": False,
        "name_fill": (255, 255, 255, 255),
        "name_outline": (20, 80, 30, 230),
    },
    "purple": {
        "label": "暗紫",
        "label_en": "Dark Purple",
        "border_fill_top": (180, 130, 220),
        "border_fill_bot": (80, 30, 120),
        "inner_line": (140, 80, 180),
        "double_border": False,
        "name_fill": (230, 200, 255, 255),
        "name_outline": (50, 10, 80, 230),
    },
}


def get_style(name):
    """获取指定款式配色，不存在则抛出 ValueError。"""
    if name not in STYLES:
        valid = ", ".join(STYLES.keys())
        raise ValueError(f"未知款式 '{name}'，可选: {valid}")
    return STYLES[name]


def list_styles():
    """返回所有款式列表 [(key, label, label_en), ...]。"""
    return [(k, v["label"], v["label_en"]) for k, v in STYLES.items()]
