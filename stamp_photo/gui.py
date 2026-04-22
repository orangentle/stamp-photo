"""stamp-photo GUI 主窗口 (PySide6)。"""

import sys
from io import BytesIO
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QLineEdit, QRadioButton, QButtonGroup,
    QFileDialog, QGroupBox, QMessageBox, QSizePolicy,
)
from PySide6.QtGui import QPixmap, QImage, QIcon, QPainter, QColor
from PySide6.QtCore import Qt, QTimer

from .core import generate_stamp, save_stamp
from .styles import STYLES, list_styles
from . import __version__


def _pil_to_qpixmap(pil_image):
    """将 PIL RGBA Image 转为 QPixmap。"""
    buf = BytesIO()
    pil_image.save(buf, format="PNG")
    buf.seek(0)
    qimg = QImage()
    qimg.loadFromData(buf.read())
    return QPixmap.fromImage(qimg)


def _color_icon(rgb, size=16):
    """生成纯色方块图标。"""
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(*rgb))
    return QIcon(pixmap)


class StampApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"stamp-photo 邮票照片生成器 v{__version__}")
        self.setMinimumSize(620, 480)

        self._input_image = None
        self._current_style = "blue"
        self._current_name = ""
        self._output_format = "png"

        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(300)
        self._debounce_timer.timeout.connect(self._update_preview)

        self._init_ui()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # ===== 左侧：预览区 =====
        self._preview_label = QLabel("请选择图片")
        self._preview_label.setAlignment(Qt.AlignCenter)
        self._preview_label.setMinimumSize(280, 380)
        self._preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._preview_label.setStyleSheet(
            "QLabel { background: #f0f0f0; border: 1px dashed #ccc; "
            "border-radius: 8px; color: #999; font-size: 14px; }"
        )
        main_layout.addWidget(self._preview_label, stretch=3)

        # ===== 右侧：控制面板 =====
        panel = QVBoxLayout()
        panel.setSpacing(12)
        main_layout.addLayout(panel, stretch=2)

        # 选择图片
        btn_open = QPushButton("选择图片...")
        btn_open.setMinimumHeight(36)
        btn_open.setCursor(Qt.PointingHandCursor)
        btn_open.clicked.connect(self._on_open_image)
        panel.addWidget(btn_open)

        # 款式选择
        style_group = QGroupBox("款式")
        style_layout = QVBoxLayout(style_group)
        self._style_btn_group = QButtonGroup(self)
        self._style_btn_group.setExclusive(True)

        for key, label, label_en in list_styles():
            scheme = STYLES[key]
            rb = QRadioButton(f"{label} ({label_en})")
            rb.setIcon(_color_icon(scheme["border_fill_top"]))
            rb.setProperty("style_key", key)
            if key == "blue":
                rb.setChecked(True)
            self._style_btn_group.addButton(rb)
            style_layout.addWidget(rb)

        self._style_btn_group.buttonClicked.connect(self._on_style_changed)
        panel.addWidget(style_group)

        # 姓名输入
        name_group = QGroupBox("姓名（可选）")
        name_layout = QVBoxLayout(name_group)
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("输入要显示的名字...")
        self._name_input.textChanged.connect(self._on_name_changed)
        name_layout.addWidget(self._name_input)
        panel.addWidget(name_group)

        # 输出格式
        fmt_group = QGroupBox("输出格式")
        fmt_layout = QHBoxLayout(fmt_group)
        self._fmt_btn_group = QButtonGroup(self)
        rb_png = QRadioButton("PNG")
        rb_png.setChecked(True)
        rb_png.setProperty("fmt", "png")
        rb_pdf = QRadioButton("PDF")
        rb_pdf.setProperty("fmt", "pdf")
        self._fmt_btn_group.addButton(rb_png)
        self._fmt_btn_group.addButton(rb_pdf)
        self._fmt_btn_group.buttonClicked.connect(self._on_format_changed)
        fmt_layout.addWidget(rb_png)
        fmt_layout.addWidget(rb_pdf)
        panel.addWidget(fmt_group)

        # 导出按钮
        panel.addStretch()
        btn_export = QPushButton("导出保存")
        btn_export.setMinimumHeight(40)
        btn_export.setCursor(Qt.PointingHandCursor)
        btn_export.setStyleSheet(
            "QPushButton { background: #4a90d9; color: white; "
            "border-radius: 6px; font-size: 14px; font-weight: bold; }"
            "QPushButton:hover { background: #3a7bc8; }"
        )
        btn_export.clicked.connect(self._on_export)
        panel.addWidget(btn_export)

    # ---------- 事件处理 ----------

    def _on_open_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "",
            "图片文件 (*.jpg *.jpeg *.png *.bmp *.webp);;所有文件 (*)",
        )
        if path:
            self._input_image = path
            self._update_preview()

    def _on_style_changed(self, button):
        self._current_style = button.property("style_key")
        self._update_preview()

    def _on_name_changed(self, text):
        self._current_name = text
        self._debounce_timer.start()

    def _on_format_changed(self, button):
        self._output_format = button.property("fmt")

    def _update_preview(self):
        if not self._input_image:
            return
        try:
            stamp = generate_stamp(
                self._input_image,
                style=self._current_style,
                name=self._current_name,
            )
            pixmap = _pil_to_qpixmap(stamp)
            scaled = pixmap.scaled(
                self._preview_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self._preview_label.setPixmap(scaled)
        except Exception as e:
            self._preview_label.setText(f"预览失败:\n{e}")

    def _on_export(self):
        if not self._input_image:
            QMessageBox.warning(self, "提示", "请先选择图片")
            return

        ext = self._output_format
        filter_str = f"{'PNG 图片' if ext == 'png' else 'PDF 文档'} (*.{ext})"
        path, _ = QFileDialog.getSaveFileName(
            self, "导出保存", f"stamp_output.{ext}", filter_str,
        )
        if not path:
            return

        try:
            stamp = generate_stamp(
                self._input_image,
                style=self._current_style,
                name=self._current_name,
            )
            save_stamp(stamp, path)
            QMessageBox.information(self, "完成", f"已保存到:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "导出失败", str(e))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_preview()


def main():
    app = QApplication(sys.argv)
    window = StampApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
