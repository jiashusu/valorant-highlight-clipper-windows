from __future__ import annotations

import ctypes
import hashlib
import os
import subprocess
import sys
import tempfile
import threading
import webbrowser
from pathlib import Path

from PySide6.QtCore import QObject, QPoint, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QIcon, QImage, QPainter, QPainterPath, QPixmap, QTextCursor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .core import (
    ClipSegment,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SOURCE_DIR,
    VIDEO_EXTENSIONS,
    discover_videos,
    hidden_subprocess_kwargs,
    process_video,
    resolve_tool,
)
from .build_info import BUILD_SHA
from .paths import resource_root
from .update_checker import UpdateResult, check_for_update


APP_TITLE = "Valorant 高光剪辑 Windows 版"
APP_VERSION = "Windows v1.4.2"
AUTHOR_URL = "https://github.com/jiashusu/valorant-highlight-clipper-windows"
THUMBNAIL_WIDTH = 384
THUMBNAIL_HEIGHT = 216
CARD_PREVIEW_FPS = 30
CLIP_CARD_COLUMNS = 3
UPDATE_CHECK_INTERVAL_MS = 30 * 60 * 1000

COLORS = {
    "bg_top": "#050506",
    "bg_bottom": "#0B0B0D",
    "panel": "rgba(24, 24, 27, 0.62)",
    "panel_strong": "rgba(24, 24, 27, 0.82)",
    "card": "rgba(29, 29, 34, 0.76)",
    "card_hover": "rgba(38, 38, 43, 0.86)",
    "field": "rgba(13, 13, 16, 0.80)",
    "field_soft": "rgba(21, 21, 25, 0.66)",
    "border": "rgba(255, 255, 255, 0.075)",
    "border_hot": "rgba(255, 255, 255, 0.18)",
    "text": "#F6F8FC",
    "muted": "#A8ABB2",
    "subtle": "#737780",
    "accent": "#64D2FF",
    "accent_2": "#87DEFF",
    "accent_text": "#071018",
    "danger": "#FF6B7A",
    "danger_soft": "rgba(255, 107, 122, 0.22)",
    "warning": "#FFD84D",
    "warning_bg": "rgba(36, 31, 16, 0.58)",
}

TEXTS = {
    "zh": {
        "app_title": APP_TITLE,
        "author": "原作者: shu",
        "language_toggle": "EN",
        "check_update": "检查更新",
        "paths": "路径",
        "source": "素材文件夹或视频文件",
        "choose_folder": "选择文件夹",
        "choose_video": "选择视频",
        "recursive": "递归扫描",
        "output_dir": "输出目录",
        "choose_output": "选择输出目录",
        "open_output": "打开输出目录",
        "settings": "参数（建议不要动，除非你懂什么意思）",
        "confidence": "置信度",
        "framerate": "识别帧率",
        "seconds_before": "提前秒数",
        "seconds_after": "延后秒数",
        "merge_gap": "合并间隔",
        "min_event": "最短事件秒",
        "max_seconds": "最多分析秒数",
        "strict": "严格过滤队友击杀（推荐）",
        "copy_streams": "快速无损截取",
        "scan_videos": "扫描视频",
        "clear_log": "清空日志",
        "video": "视频",
        "duration": "时长",
        "size": "大小",
        "path": "路径",
        "process_log": "处理日志",
        "highlights": "Highlights",
        "preview_mode": "低清预览 / 高清播放",
        "warning": "提示：当前版本仍可能输出队友击杀片段，可先手动删除；后续会继续更新识别逻辑。",
        "empty_clips": "剪辑完成后会在这里显示低清预览和操作按钮",
        "no_clips": "没有导出片段",
        "loading_preview": "生成低清预览中",
        "loading_card_preview": "载入预览中",
        "play_high": "高清播放",
        "stop_play": "停止播放",
        "reveal_video": "定位此视频",
        "delete": "删除",
        "start": "开始剪辑",
        "start_busy": "剪辑中",
        "ready": "准备就绪",
        "scanning": "扫描中",
        "checking_update": "检查更新中",
        "trimming": "剪辑中",
        "error": "出错",
        "done": "完成",
        "latest": "已是最新版本",
        "update_failed": "检查更新失败",
        "scan_done": "扫描完成: {count} 个视频",
        "new_version": "有新版本: {version}",
        "prepare_preview": "准备卡片预览: Highlight #{index:03d}",
        "preview_inside": "卡片内预览: Highlight #{index:03d}",
        "preview_failed": "卡片预览失败",
        "low_preview": "低清预览",
        "high_preview": "高清播放",
        "missing_video": "视频不存在：{path}",
        "missing_export": "找不到导出视频：\n{path}",
        "missing_ffplay": "没有找到内建播放器 ffplay，请重新打包 App。",
        "player_failed": "播放器启动失败: {error}",
        "card_preview_failed": "卡片预览生成失败: {error}",
        "delete_confirm": "确定删除这个片段吗？\n\n{summary}",
        "delete_failed": "删除失败: {error}",
        "clip_summary": "约 {kills} 杀 · {start:.2f}s-{end:.2f}s · {duration:.2f}s",
        "clip_info": "约 {kills} 杀  ·  {duration:.2f}s\n{start:.2f}s - {end:.2f}s",
        "deleted_log": "已删除片段: {name}\n",
        "finished_log": "完成，导出 {count} 个片段\n",
        "estimate_under_minute": "约 1 分钟内",
        "estimate_minutes": "约 {low}-{high} 分钟",
        "estimate_log": "预计可能需要：{estimate}。导出时间取决于视频长度、电脑性能、识别帧率和导出设置。处理时可以去喝杯茶，放松一下。",
        "busy": "当前还有任务在运行。",
        "select_video_first": "请先扫描并选择一个视频。",
        "update_open": "{message}\n\n是否打开 GitHub Release 下载新版 Windows exe？",
        "update_error_open": "{message}\n\n是否打开 GitHub Release 页面手动查看新版？",
    },
    "en": {
        "app_title": "Valorant Highlight Clipper Windows",
        "author": "Author: shu",
        "language_toggle": "中文",
        "check_update": "Check Updates",
        "paths": "Paths",
        "source": "Source folder or video file",
        "choose_folder": "Folder",
        "choose_video": "Video",
        "recursive": "Recursive",
        "output_dir": "Output folder",
        "choose_output": "Choose output",
        "open_output": "Open output",
        "settings": "Settings (do not change unless you know what they mean)",
        "confidence": "Confidence",
        "framerate": "Scan FPS",
        "seconds_before": "Before seconds",
        "seconds_after": "After seconds",
        "merge_gap": "Merge gap",
        "min_event": "Min event sec",
        "max_seconds": "Max scan sec",
        "strict": "Strict own-kill filter",
        "copy_streams": "Fast stream copy",
        "scan_videos": "Scan Videos",
        "clear_log": "Clear Log",
        "video": "Videos",
        "duration": "Duration",
        "size": "Size",
        "path": "Path",
        "process_log": "Process Log",
        "highlights": "Highlights",
        "preview_mode": "Low preview / HD playback",
        "warning": "Note: this version may still export teammate kills. Delete them manually for now; detection will keep improving.",
        "empty_clips": "Exported highlights will appear here with previews and actions.",
        "no_clips": "No exported clips",
        "loading_preview": "Generating preview",
        "loading_card_preview": "Loading preview",
        "play_high": "HD Play",
        "stop_play": "Stop",
        "reveal_video": "Reveal File",
        "delete": "Delete",
        "start": "Start Clipping",
        "start_busy": "Clipping...",
        "ready": "Ready",
        "scanning": "Scanning",
        "checking_update": "Checking updates",
        "trimming": "Clipping",
        "error": "Error",
        "done": "Done",
        "latest": "Up to date",
        "update_failed": "Update check failed",
        "scan_done": "Scan complete: {count} videos",
        "new_version": "New version: {version}",
        "prepare_preview": "Preparing card preview: Highlight #{index:03d}",
        "preview_inside": "Card preview: Highlight #{index:03d}",
        "preview_failed": "Card preview failed",
        "low_preview": "Low preview",
        "high_preview": "HD playback",
        "missing_video": "Video does not exist: {path}",
        "missing_export": "Cannot find exported video:\n{path}",
        "missing_ffplay": "Bundled ffplay was not found. Please rebuild the app.",
        "player_failed": "Player failed to start: {error}",
        "card_preview_failed": "Card preview failed: {error}",
        "delete_confirm": "Delete this clip?\n\n{summary}",
        "delete_failed": "Delete failed: {error}",
        "clip_summary": "~{kills} kills · {start:.2f}s-{end:.2f}s · {duration:.2f}s",
        "clip_info": "~{kills} kills  ·  {duration:.2f}s\n{start:.2f}s - {end:.2f}s",
        "deleted_log": "Deleted clip: {name}\n",
        "finished_log": "Done, exported {count} clips\n",
        "estimate_under_minute": "about under 1 minute",
        "estimate_minutes": "about {low}-{high} minutes",
        "estimate_log": "Estimated time: {estimate}. Export time depends on video length, PC performance, scan FPS, and export settings. You can grab a drink and relax while it runs.",
        "busy": "Another task is still running.",
        "select_video_first": "Scan and select a video first.",
        "update_open": "{message}\n\nOpen GitHub Release to download the new Windows exe?",
        "update_error_open": "{message}\n\nOpen GitHub Release manually?",
    },
}


class Bridge(QObject):
    event = Signal(str, object)


class ClickLabel(QLabel):
    clicked = Signal()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


def reveal_in_explorer(path: Path) -> None:
    path = path.expanduser().resolve(strict=True)
    if not path.is_file() or path.suffix.lower() != ".mp4":
        raise FileNotFoundError(path)
    if os.name == "nt":
        params = f'/select,"{path}"'
        result = ctypes.windll.shell32.ShellExecuteW(None, "open", "explorer.exe", params, None, 1)
        if result <= 32:
            subprocess.Popen(f'explorer.exe {params}', **hidden_subprocess_kwargs())
    elif sys.platform == "darwin":
        subprocess.Popen(["open", "-R", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path.parent)])


def open_path(path: Path) -> None:
    path = path.expanduser().resolve(strict=False)
    if os.name == "nt":
        if path.is_file():
            reveal_in_explorer(path)
        elif path.exists():
            os.startfile(str(path))  # type: ignore[attr-defined]
        else:
            raise FileNotFoundError(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", "-R" if path.is_file() else str(path), str(path)] if path.is_file() else ["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path.parent if path.is_file() else path)])


def apply_windows_mica(window: QMainWindow) -> None:
    if os.name != "nt":
        return
    try:
        hwnd = int(window.winId())
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int))
        # DWMWA_SYSTEMBACKDROP_TYPE: 2=Mica, 3=Acrylic, 4=Tabbed. Use Mica as base layer.
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 38, ctypes.byref(ctypes.c_int(2)), ctypes.sizeof(ctypes.c_int))
    except Exception:
        return


def format_seconds(value: float) -> str:
    minutes = int(value // 60)
    seconds = int(round(value % 60))
    return f"{minutes}:{seconds:02d}"


def format_size(value: int) -> str:
    gb = value / 1024 / 1024 / 1024
    if gb >= 1:
        return f"{gb:.2f} GB"
    return f"{value / 1024 / 1024:.1f} MB"


def estimate_minutes_range(
    video_duration: float,
    max_seconds: float | None,
    framerate: int,
    copy_streams: bool,
) -> tuple[int, int]:
    analysis_seconds = max(0.0, video_duration)
    if max_seconds is not None:
        analysis_seconds = min(analysis_seconds, max(0.0, max_seconds))
    low_seconds = analysis_seconds * 0.20
    high_seconds = analysis_seconds * 0.45
    if copy_streams:
        low_seconds *= 0.75
        high_seconds *= 0.75
    if framerate > 12:
        low_seconds *= 1.25
        high_seconds *= 1.25
    low_minutes = max(1, int((low_seconds + 59) // 60))
    high_minutes = max(low_minutes, int((high_seconds + 59) // 60))
    return low_minutes, high_minutes


def app_icon_path() -> Path:
    return resource_root() / "assets" / "app_icon" / "ValorantHighlightClipper.ico"


def short_build() -> str:
    value = (BUILD_SHA or "").strip()
    if value.startswith("v") and value.endswith("-windows"):
        return value[1:-8]
    if value.startswith("v"):
        return value
    return value[:7] if value else "unknown"


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.language = "zh"
        self.text_widgets: list[tuple[object, str, str]] = []
        self.status_key = "ready"
        self.status_kwargs: dict[str, object] = {}
        self.videos: list[dict[str, object]] = []
        self.clips: list[ClipSegment] = []
        self.selected_video: Path | None = None
        self.selected_clip_index: int | None = None
        self.worker_thread: threading.Thread | None = None
        self.last_update_prompt_sha: str | None = None
        self.player_process: subprocess.Popen[str] | None = None
        self.playing_clip_index: int | None = None
        self.playing_mode: str | None = None
        self.preview_token = 0
        self.card_preview_pixmaps: list[QPixmap] = []
        self.card_preview_frame_index = 0
        self.thumbnail_cache_dir = Path(tempfile.gettempdir()) / "valorant_clipper_qt_thumbnails"
        self.card_preview_cache_dir = Path(tempfile.gettempdir()) / "valorant_clipper_qt_card_previews"
        self.thumbnail_generation = 0
        self.thumbnail_labels: dict[int, QLabel] = {}
        self.thumbnail_pixmaps: dict[int, QPixmap] = {}
        self.play_buttons: dict[int, QPushButton] = {}
        self.card_widgets: dict[int, QFrame] = {}
        self.drag_position: QPoint | None = None

        self.bridge = Bridge()
        self.bridge.event.connect(self.handle_event)
        self.preview_timer = QTimer(self)
        self.preview_timer.timeout.connect(self.advance_card_preview)
        self.player_timer = QTimer(self)
        self.player_timer.timeout.connect(self.watch_player)
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(lambda: self.check_for_updates(manual=False))

        self.setWindowTitle(self.text("app_title"))
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        icon_path = app_icon_path()
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        self.resize(1720, 980)
        self.setMinimumSize(1360, 840)
        self.build_ui()
        self.apply_language()
        apply_windows_mica(self)
        QTimer.singleShot(1500, lambda: self.check_for_updates(manual=False))

    def text(self, key: str, **kwargs: object) -> str:
        table = TEXTS.get(self.language, TEXTS["zh"])
        return table.get(key, TEXTS["zh"].get(key, key)).format(**kwargs)

    def bind_text(self, widget, key: str, attr: str = "text"):
        self.text_widgets.append((widget, key, attr))
        if attr == "title":
            widget.setTitle(self.text(key))
        else:
            widget.setText(self.text(key))
        return widget

    def set_status(self, key: str, **kwargs: object) -> None:
        self.status_key = key
        self.status_kwargs = dict(kwargs)
        self.status_label.setText(self.text(key, **kwargs))

    def toggle_language(self) -> None:
        self.language = "en" if self.language == "zh" else "zh"
        self.apply_language()

    def apply_language(self) -> None:
        self.setWindowTitle(self.text("app_title"))
        alive_widgets = []
        for widget, key, attr in list(self.text_widgets):
            try:
                if attr == "title":
                    widget.setTitle(self.text(key))
                else:
                    widget.setText(self.text(key))
            except RuntimeError:
                continue
            alive_widgets.append((widget, key, attr))
        self.text_widgets = alive_widgets
        self.video_table.setHorizontalHeaderLabels([self.text("duration"), self.text("size"), self.text("path")])
        self.set_status(self.status_key, **self.status_kwargs)
        if self.worker_thread and self.worker_thread.is_alive():
            self.start_button.setText(self.text("start_busy"))
        if self.clips:
            selected = self.selected_clip_index
            self.refresh_clip_cards()
            if selected is not None and selected < len(self.clips):
                self.select_clip(selected)

    def build_ui(self) -> None:
        self.setStyleSheet(self.stylesheet())
        outer = QFrame(self)
        outer.setObjectName("outer")
        self.setCentralWidget(outer)
        root = QVBoxLayout(outer)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        self.titlebar = self.build_titlebar()
        root.addWidget(self.titlebar)

        body = QHBoxLayout()
        body.setSpacing(14)
        root.addLayout(body, 1)

        left = QFrame()
        left.setObjectName("glassPanel")
        self.add_shadow(left)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(16, 16, 16, 16)
        left_layout.setSpacing(12)
        self.build_left_panel(left_layout)
        body.addWidget(left, 2)

        right = QFrame()
        right.setObjectName("glassPanel")
        self.add_shadow(right)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(16, 16, 16, 16)
        right_layout.setSpacing(10)
        self.build_right_panel(right_layout)
        body.addWidget(right, 5)

        footer = QHBoxLayout()
        footer.setSpacing(10)
        root.addLayout(footer)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        footer.addWidget(self.progress, 1)
        self.start_button = self.bind_text(QPushButton(), "start")
        self.start_button.setObjectName("primaryButton")
        self.start_button.clicked.connect(self.start_job)
        footer.addWidget(self.start_button)

    def add_shadow(self, widget: QWidget, blur: int = 34, alpha: int = 110) -> None:
        shadow = QGraphicsDropShadowEffect(widget)
        shadow.setBlurRadius(blur)
        shadow.setColor(QColor(0, 0, 0, alpha))
        shadow.setOffset(0, 10)
        widget.setGraphicsEffect(shadow)

    def build_titlebar(self) -> QFrame:
        titlebar = QFrame()
        titlebar.setObjectName("titlebar")
        layout = QHBoxLayout(titlebar)
        layout.setContentsMargins(14, 6, 8, 6)
        layout.setSpacing(10)
        icon_path = app_icon_path()
        if icon_path.exists():
            logo = QLabel()
            logo.setObjectName("titleLogo")
            logo.setFixedSize(22, 22)
            logo.setPixmap(QIcon(str(icon_path)).pixmap(QSize(22, 22)))
            layout.addWidget(logo)
        title = self.bind_text(QLabel(), "app_title")
        title.setObjectName("titleText")
        layout.addWidget(title)
        version = QLabel(f"{APP_VERSION} · {short_build()}")
        version.setObjectName("versionText")
        layout.addWidget(version)
        layout.addStretch(1)
        author = self.bind_text(QLabel(), "author")
        author.setObjectName("linkText")
        author.setCursor(Qt.CursorShape.PointingHandCursor)
        author.mousePressEvent = lambda _event: webbrowser.open(AUTHOR_URL)
        layout.addWidget(author)
        self.language_button = self.bind_text(QPushButton(), "language_toggle")
        self.language_button.setObjectName("titleButton")
        self.language_button.clicked.connect(self.toggle_language)
        layout.addWidget(self.language_button)
        self.status_label = QLabel()
        self.status_label.setObjectName("statusText")
        layout.addWidget(self.status_label)
        self.update_button = self.bind_text(QPushButton(), "check_update")
        self.update_button.setObjectName("titleButton")
        self.update_button.clicked.connect(lambda: self.check_for_updates(manual=True))
        layout.addWidget(self.update_button)
        for text, handler, name in (
            ("—", self.showMinimized, "windowButton"),
            ("□", self.toggle_maximize, "windowButton"),
            ("×", self.close, "closeButton"),
        ):
            button = QPushButton(text)
            button.setObjectName(name)
            button.setFixedSize(34, 30)
            button.clicked.connect(handler)
            layout.addWidget(button)
            if text == "□":
                self.maximize_button = button
        return titlebar

    def build_left_panel(self, layout: QVBoxLayout) -> None:
        paths = self.bind_text(QGroupBox(), "paths", "title")
        paths_layout = QVBoxLayout(paths)
        paths_layout.setSpacing(8)
        self.bind_text(QLabel(), "source").setParent(paths)
        paths_layout.addWidget(self.text_widgets[-1][0])
        self.source_path = QLineEdit(str(DEFAULT_SOURCE_DIR))
        paths_layout.addWidget(self.source_path)
        source_buttons = QHBoxLayout()
        self.choose_folder_button = self.bind_text(QPushButton(), "choose_folder")
        self.choose_folder_button.clicked.connect(self.choose_source_folder)
        source_buttons.addWidget(self.choose_folder_button)
        self.choose_video_button = self.bind_text(QPushButton(), "choose_video")
        self.choose_video_button.clicked.connect(self.choose_source_file)
        source_buttons.addWidget(self.choose_video_button)
        self.recursive = self.bind_text(QCheckBox(), "recursive")
        source_buttons.addWidget(self.recursive)
        paths_layout.addLayout(source_buttons)
        self.bind_text(QLabel(), "output_dir").setParent(paths)
        paths_layout.addWidget(self.text_widgets[-1][0])
        self.output_dir = QLineEdit(str(DEFAULT_OUTPUT_DIR))
        paths_layout.addWidget(self.output_dir)
        output_buttons = QHBoxLayout()
        choose_output = self.bind_text(QPushButton(), "choose_output")
        choose_output.clicked.connect(self.choose_output_dir)
        output_buttons.addWidget(choose_output)
        open_output = self.bind_text(QPushButton(), "open_output")
        open_output.clicked.connect(self.open_output_dir)
        output_buttons.addWidget(open_output)
        paths_layout.addLayout(output_buttons)
        layout.addWidget(paths)

        settings = self.bind_text(QGroupBox(), "settings", "title")
        form = QGridLayout(settings)
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        self.confidence = self.double_spin(0.93, 0, 1, 2)
        self.framerate = self.int_spin(8, 1, 60)
        self.seconds_before = self.double_spin(4.0, 0, 30, 1)
        self.seconds_after = self.double_spin(0.5, 0, 30, 1)
        self.merge_gap = self.double_spin(3.0, 0, 30, 1)
        self.min_event_seconds = self.double_spin(0.75, 0, 5, 2)
        pairs = [
            ("confidence", self.confidence, 0, 0),
            ("framerate", self.framerate, 0, 2),
            ("seconds_before", self.seconds_before, 1, 0),
            ("seconds_after", self.seconds_after, 1, 2),
            ("merge_gap", self.merge_gap, 2, 0),
            ("min_event", self.min_event_seconds, 2, 2),
        ]
        for key, widget, row, col in pairs:
            form.addWidget(self.bind_text(QLabel(), key), row, col)
            form.addWidget(widget, row, col + 1)
        form.addWidget(self.bind_text(QLabel(), "max_seconds"), 3, 0)
        self.max_seconds = QLineEdit()
        form.addWidget(self.max_seconds, 3, 1)
        self.strict_own_kills = self.bind_text(QCheckBox(), "strict")
        self.strict_own_kills.setChecked(True)
        form.addWidget(self.strict_own_kills, 4, 0, 1, 2)
        self.copy_streams = self.bind_text(QCheckBox(), "copy_streams")
        form.addWidget(self.copy_streams, 4, 2, 1, 2)
        layout.addWidget(settings)

        actions = QHBoxLayout()
        scan = self.bind_text(QPushButton(), "scan_videos")
        scan.clicked.connect(self.scan_videos)
        actions.addWidget(scan)
        clear = self.bind_text(QPushButton(), "clear_log")
        clear.clicked.connect(self.clear_log)
        actions.addWidget(clear)
        actions.addStretch(1)
        layout.addLayout(actions)

        video_group = self.bind_text(QGroupBox(), "video", "title")
        video_layout = QVBoxLayout(video_group)
        self.video_table = QTableWidget(0, 3)
        self.video_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.video_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.video_table.setTextElideMode(Qt.TextElideMode.ElideNone)
        self.video_table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.video_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.video_table.verticalHeader().setVisible(False)
        self.video_table.horizontalHeader().setStretchLastSection(False)
        self.video_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.video_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.video_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.video_table.setColumnWidth(0, 82)
        self.video_table.setColumnWidth(1, 104)
        self.video_table.setColumnWidth(2, 760)
        self.video_table.itemSelectionChanged.connect(self.select_video_from_table)
        video_layout.addWidget(self.video_table)
        layout.addWidget(video_group, 1)

    def build_right_panel(self, layout: QVBoxLayout) -> None:
        self.bind_text(QLabel(), "process_log").setObjectName("sectionTitle")
        layout.addWidget(self.text_widgets[-1][0])
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setFixedHeight(210)
        layout.addWidget(self.log_box)
        header = QHBoxLayout()
        highlights = self.bind_text(QLabel(), "highlights")
        highlights.setObjectName("sectionTitle")
        header.addWidget(highlights)
        header.addStretch(1)
        header.addWidget(self.bind_text(QLabel(), "preview_mode"))
        layout.addLayout(header)
        warning = self.bind_text(QLabel(), "warning")
        warning.setObjectName("warning")
        warning.setWordWrap(True)
        layout.addWidget(warning)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.cards_host = QWidget()
        self.cards_grid = QGridLayout(self.cards_host)
        self.cards_grid.setContentsMargins(0, 0, 0, 0)
        self.cards_grid.setSpacing(12)
        self.scroll_area.setWidget(self.cards_host)
        layout.addWidget(self.scroll_area, 1)
        self.empty_label = self.bind_text(QLabel(), "empty_clips")
        self.empty_label.setObjectName("mutedCenter")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cards_grid.addWidget(self.empty_label, 0, 0)

    def int_spin(self, value: int, minimum: int, maximum: int) -> QSpinBox:
        spin = QSpinBox()
        spin.setRange(minimum, maximum)
        spin.setValue(value)
        return spin

    def double_spin(self, value: float, minimum: float, maximum: float, decimals: int) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(minimum, maximum)
        spin.setDecimals(decimals)
        spin.setSingleStep(0.1)
        spin.setValue(value)
        return spin

    def stylesheet(self) -> str:
        return f"""
        QWidget {{
            color: {COLORS['text']};
            font-family: "Segoe UI";
            font-size: 10pt;
        }}
        #outer {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 {COLORS['bg_top']}, stop:1 {COLORS['bg_bottom']});
            border: 1px solid rgba(255, 255, 255, 0.16);
            border-radius: 18px;
        }}
        #titlebar {{
            background: rgba(8, 8, 10, 0.54);
            border: 1px solid rgba(255, 255, 255, 0.11);
            border-radius: 14px;
        }}
        #titleLogo {{
            background: transparent;
        }}
        #titleText, #sectionTitle {{
            font-weight: 700;
            color: {COLORS['text']};
        }}
        #versionText {{
            color: {COLORS['accent']};
            font-weight: 700;
        }}
        #linkText {{
            color: {COLORS['accent']};
            font-weight: 700;
        }}
        #statusText {{
            color: {COLORS['muted']};
            font-size: 9pt;
        }}
        #glassPanel, QGroupBox, #card {{
            background: {COLORS['panel']};
            border: 1px solid {COLORS['border']};
            border-radius: 22px;
        }}
        QGroupBox {{
            margin-top: 14px;
            padding: 16px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 14px;
            padding: 0 8px;
            color: {COLORS['text']};
            font-weight: 700;
        }}
        QLineEdit, QSpinBox, QDoubleSpinBox, QTextEdit, QTableWidget {{
            background: {COLORS['field']};
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            padding: 8px;
            selection-background-color: rgba(100, 210, 255, 0.30);
        }}
        QHeaderView::section {{
            background: {COLORS['field_soft']};
            color: {COLORS['text']};
            border: 0;
            border-right: 1px solid rgba(255, 255, 255, 0.11);
            padding: 8px;
            font-weight: 700;
        }}
        QTableWidget::item {{
            padding: 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.055);
        }}
        QTableWidget::item:selected {{
            background: rgba(100, 210, 255, 0.24);
        }}
        QPushButton {{
            background: rgba(255, 255, 255, 0.09);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 18px;
            padding: 9px 16px;
            color: {COLORS['text']};
            font-weight: 650;
        }}
        QPushButton:hover {{
            background: rgba(255, 255, 255, 0.15);
            border-color: {COLORS['border_hot']};
        }}
        QPushButton:pressed {{
            background: rgba(100, 210, 255, 0.18);
        }}
        #primaryButton, #accentButton {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 {COLORS['accent']}, stop:1 {COLORS['accent_2']});
            color: {COLORS['accent_text']};
            border: 1px solid rgba(255, 255, 255, 0.44);
            font-weight: 800;
        }}
        #dangerButton {{
            background: {COLORS['danger_soft']};
            border: 1px solid rgba(255, 107, 122, 0.34);
            color: #FFD8DD;
        }}
        #titleButton, #windowButton, #closeButton {{
            background: rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 6px 10px;
        }}
        #closeButton:hover {{
            background: rgba(239, 68, 68, 0.85);
        }}
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border-radius: 5px;
            border: 1px solid rgba(226, 232, 240, 0.36);
            background: rgba(255, 255, 255, 0.08);
        }}
        QCheckBox::indicator:checked {{
            background: {COLORS['accent']};
            border-color: rgba(255, 255, 255, 0.44);
        }}
        QProgressBar {{
            background: rgba(255, 255, 255, 0.09);
            border: 1px solid rgba(255, 255, 255, 0.10);
            border-radius: 10px;
            height: 18px;
            text-align: center;
        }}
        QProgressBar::chunk {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #2DD4BF, stop:1 {COLORS['accent']});
            border-radius: 9px;
        }}
        #warning {{
            background: {COLORS['warning_bg']};
            border: 1px solid rgba(255, 216, 77, 0.20);
            border-radius: 14px;
            color: {COLORS['warning']};
            padding: 10px 12px;
        }}
        #mutedCenter {{
            color: {COLORS['muted']};
            padding: 34px;
            background: rgba(29, 29, 34, 0.58);
            border: 1px solid rgba(255, 255, 255, 0.09);
            border-radius: 18px;
        }}
        QScrollBar:vertical {{
            background: rgba(255, 255, 255, 0.03);
            width: 12px;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical {{
            background: rgba(168, 171, 178, 0.30);
            min-height: 36px;
            border-radius: 6px;
        }}
        QScrollBar:horizontal {{
            background: rgba(255, 255, 255, 0.03);
            height: 12px;
            border-radius: 6px;
        }}
        QScrollBar::handle:horizontal {{
            background: rgba(168, 171, 178, 0.30);
            min-width: 36px;
            border-radius: 6px;
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        """

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self.titlebar.geometry().contains(event.position().toPoint()):
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event) -> None:
        if self.drag_position and event.buttons() & Qt.MouseButton.LeftButton and not self.isMaximized():
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event) -> None:
        self.drag_position = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:
        if self.titlebar.geometry().contains(event.position().toPoint()):
            self.toggle_maximize()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def toggle_maximize(self) -> None:
        if self.isMaximized():
            self.showNormal()
            self.maximize_button.setText("□")
        else:
            self.showMaximized()
            self.maximize_button.setText("❐")

    def choose_source_folder(self) -> None:
        path = QFileDialog.getExistingDirectory(self, self.text("choose_folder"), self.source_path.text())
        if path:
            self.source_path.setText(path)
            self.scan_videos()

    def choose_source_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.text("choose_video"),
            str(Path.home()),
            "Video files (*.mp4 *.mov *.mkv *.avi *.m4v *.flv);;All files (*.*)",
        )
        if path:
            self.source_path.setText(path)
            self.scan_videos()

    def choose_output_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(self, self.text("choose_output"), self.output_dir.text())
        if path:
            self.output_dir.setText(path)

    def open_output_dir(self) -> None:
        output_dir = Path(self.output_dir.text()).expanduser()
        output_dir.mkdir(parents=True, exist_ok=True)
        open_path(output_dir)

    def scan_videos(self) -> None:
        self.set_status("scanning")
        self.run_thread(self.scan_worker)

    def scan_worker(self) -> None:
        try:
            videos = discover_videos(Path(self.source_path.text()), recursive=self.recursive.isChecked())
            self.bridge.event.emit("videos", videos)
        except Exception as exc:
            self.bridge.event.emit("error", f"扫描失败: {exc}")

    def check_for_updates(self, manual: bool = True) -> None:
        if manual:
            self.set_status("checking_update")
        threading.Thread(target=self.update_worker, args=(manual,), daemon=True).start()

    def update_worker(self, manual: bool) -> None:
        try:
            self.bridge.event.emit("update", (manual, check_for_update()))
        except Exception as exc:
            self.bridge.event.emit("update_error", (manual, str(exc)))

    def run_thread(self, target) -> bool:
        if self.worker_thread and self.worker_thread.is_alive():
            QMessageBox.warning(self, self.text("app_title"), self.text("busy"))
            return False
        self.worker_thread = threading.Thread(target=target, daemon=True)
        self.worker_thread.start()
        return True

    def select_video_from_table(self) -> None:
        rows = sorted({item.row() for item in self.video_table.selectedItems()})
        if not rows:
            self.selected_video = None
            return
        path_item = self.video_table.item(rows[0], 2)
        self.selected_video = Path(path_item.data(Qt.ItemDataRole.UserRole) or path_item.text()) if path_item else None

    def select_first_video(self) -> None:
        if self.video_table.rowCount() == 0:
            self.selected_video = None
            return
        self.video_table.selectRow(0)
        self.select_video_from_table()

    def start_job(self) -> None:
        if self.selected_video is None:
            self.select_first_video()
        if self.selected_video is None:
            QMessageBox.warning(self, self.text("app_title"), self.text("select_video_first"))
            return
        self.stop_preview()
        self.clips = []
        self.selected_clip_index = None
        self.clear_clip_cards()
        self.start_button.setEnabled(False)
        self.start_button.setText(self.text("start_busy"))
        self.progress.setValue(0)
        self.set_status("trimming")
        self.append_log(self.estimate_log_message() + "\n")
        self.run_thread(self.job_worker)

    def selected_video_duration(self) -> float:
        if self.selected_video is None:
            return 0.0
        selected = str(self.selected_video)
        for video in self.videos:
            if str(video.get("path", "")) == selected:
                return float(video.get("duration", 0.0) or 0.0)
        return 0.0

    def current_max_seconds(self) -> float | None:
        max_text = self.max_seconds.text().strip()
        if not max_text:
            return None
        try:
            return float(max_text)
        except ValueError:
            return None

    def estimate_label(self) -> str:
        low, high = estimate_minutes_range(
            self.selected_video_duration(),
            self.current_max_seconds(),
            int(self.framerate.value()),
            self.copy_streams.isChecked(),
        )
        if high <= 1:
            return self.text("estimate_under_minute")
        return self.text("estimate_minutes", low=low, high=high)

    def estimate_log_message(self) -> str:
        return self.text("estimate_log", estimate=self.estimate_label())

    def job_worker(self) -> None:
        assert self.selected_video is not None
        try:
            max_text = self.max_seconds.text().strip()
            max_seconds = float(max_text) if max_text else None

            def progress(message: str, value: float | None = None) -> None:
                self.bridge.event.emit("log", message)
                if value is not None:
                    self.bridge.event.emit("progress", value)

            clips = process_video(
                video_path=self.selected_video,
                output_dir=Path(self.output_dir.text()),
                confidence=float(self.confidence.value()),
                framerate=int(self.framerate.value()),
                seconds_before=float(self.seconds_before.value()),
                seconds_after=float(self.seconds_after.value()),
                merge_gap_seconds=float(self.merge_gap.value()),
                max_seconds=max_seconds,
                strict_own_kills=self.strict_own_kills.isChecked(),
                min_event_seconds=float(self.min_event_seconds.value()),
                copy_streams=self.copy_streams.isChecked(),
                progress=progress,
            )
            self.bridge.event.emit("clips", clips)
        except Exception as exc:
            self.bridge.event.emit("error", f"剪辑失败: {exc}")
        finally:
            self.bridge.event.emit("done", None)

    def handle_event(self, kind: str, payload: object) -> None:
        if kind == "videos":
            self.render_videos(payload)  # type: ignore[arg-type]
        elif kind == "log":
            self.append_log(f"{payload}\n")
        elif kind == "progress":
            self.progress.setValue(int(float(payload) * 100))
        elif kind == "clips":
            self.render_clips(payload)  # type: ignore[arg-type]
        elif kind == "error":
            self.set_status("error")
            self.append_log(f"{payload}\n")
            QMessageBox.critical(self, self.text("app_title"), str(payload))
        elif kind == "done":
            self.start_button.setEnabled(True)
            self.start_button.setText(self.text("start"))
            if self.status_key != "error":
                self.set_status("done")
        elif kind == "update":
            manual, result = payload  # type: ignore[misc]
            self.handle_update_result(bool(manual), result)  # type: ignore[arg-type]
        elif kind == "update_error":
            manual, message = payload  # type: ignore[misc]
            self.handle_update_error(bool(manual), str(message))
        elif kind == "thumbnail_ready":
            generation, index, path = payload  # type: ignore[misc]
            self.handle_thumbnail_ready(int(generation), int(index), Path(str(path)))
        elif kind == "thumbnail_error":
            generation, index = payload  # type: ignore[misc]
            self.handle_thumbnail_error(int(generation), int(index))
        elif kind == "card_preview_ready":
            token, index, frames = payload  # type: ignore[misc]
            self.handle_card_preview_ready(int(token), int(index), frames)  # type: ignore[arg-type]
        elif kind == "card_preview_error":
            token, message = payload  # type: ignore[misc]
            self.handle_card_preview_error(int(token), str(message))

    def handle_update_result(self, manual: bool, result: UpdateResult) -> None:
        if result.update_available:
            if not manual and result.remote_sha == self.last_update_prompt_sha:
                self.update_timer.start(UPDATE_CHECK_INTERVAL_MS)
                return
            self.last_update_prompt_sha = result.remote_sha
            self.set_status("new_version", version=result.remote_short)
            if QMessageBox.question(self, self.text("app_title"), self.text("update_open", message=result.message)) == QMessageBox.StandardButton.Yes:
                webbrowser.open(result.download_url)
        elif manual:
            self.set_status("latest")
            QMessageBox.information(self, self.text("app_title"), result.message)
        elif self.status_key == "checking_update":
            self.set_status("ready")
        if not manual:
            self.update_timer.start(UPDATE_CHECK_INTERVAL_MS)

    def handle_update_error(self, manual: bool, message: str) -> None:
        if manual:
            self.set_status("update_failed")
            if QMessageBox.question(self, self.text("app_title"), self.text("update_error_open", message=message)) == QMessageBox.StandardButton.Yes:
                webbrowser.open(AUTHOR_URL + "/releases/latest")
        elif self.status_key == "checking_update":
            self.set_status("ready")
        if not manual:
            self.update_timer.start(UPDATE_CHECK_INTERVAL_MS)

    def append_log(self, message: str) -> None:
        cursor = self.log_box.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_box.setTextCursor(cursor)
        self.log_box.insertPlainText(message)
        self.log_box.ensureCursorVisible()

    def clear_log(self) -> None:
        self.log_box.clear()

    def render_videos(self, videos) -> None:
        self.videos = [video.__dict__ for video in videos]
        self.video_table.setRowCount(len(self.videos))
        for row, video in enumerate(self.videos):
            values = [format_seconds(float(video["duration"])), format_size(int(video["size_bytes"])), str(video["path"])]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                item.setToolTip(value)
                if col == 2:
                    item.setData(Qt.ItemDataRole.UserRole, value)
                self.video_table.setItem(row, col, item)
        self.update_video_path_column_width()
        self.select_first_video()
        self.set_status("scan_done", count=len(self.videos))

    def update_video_path_column_width(self) -> None:
        longest = self.text("path")
        for video in self.videos:
            path = str(video.get("path", ""))
            if len(path) > len(longest):
                longest = path
        width = self.video_table.fontMetrics().horizontalAdvance(longest) + 42
        self.video_table.setColumnWidth(2, max(760, min(width, 2200)))

    def render_clips(self, clips) -> None:
        self.clips = list(clips)
        self.refresh_clip_cards()
        self.append_log(self.text("finished_log", count=len(self.clips)))
        if self.clips:
            self.select_clip(0)

    def clear_clip_cards(self) -> None:
        self.thumbnail_generation += 1
        self.thumbnail_labels = {}
        self.thumbnail_pixmaps = {}
        self.play_buttons = {}
        self.card_widgets = {}
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.empty_label = self.bind_text(QLabel(), "empty_clips")
        self.empty_label.setObjectName("mutedCenter")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cards_grid.addWidget(self.empty_label, 0, 0)

    def refresh_clip_cards(self) -> None:
        self.thumbnail_generation += 1
        generation = self.thumbnail_generation
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.thumbnail_labels = {}
        self.thumbnail_pixmaps = {}
        self.play_buttons = {}
        self.card_widgets = {}
        self.selected_clip_index = None
        if not self.clips:
            empty = self.bind_text(QLabel(), "no_clips")
            empty.setObjectName("mutedCenter")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cards_grid.addWidget(empty, 0, 0)
            return
        for index, clip in enumerate(self.clips):
            self.render_clip_card(index, clip)
            threading.Thread(
                target=self.thumbnail_worker,
                args=(generation, index, clip, self.thumbnail_seek_seconds(clip)),
                daemon=True,
            ).start()

    def render_clip_card(self, index: int, clip: ClipSegment) -> None:
        card = QFrame()
        card.setObjectName("card")
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        preview = ClickLabel(self.text("loading_preview"))
        preview.setObjectName("preview")
        preview.setFixedHeight(216)
        preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview.clicked.connect(lambda i=index: self.play_low_quality_preview(i))
        layout.addWidget(preview)
        title = QLabel(f"Highlight #{index + 1:03d}")
        title.setObjectName("cardTitle")
        layout.addWidget(title)
        info = QLabel(self.text("clip_info", kills=clip.kills, duration=clip.duration, start=clip.start, end=clip.end))
        info.setObjectName("cardMuted")
        layout.addWidget(info)
        actions = QHBoxLayout()
        play = self.bind_text(QPushButton(), "play_high")
        play.setObjectName("accentButton")
        play.clicked.connect(lambda _checked=False, i=index: self.play_high_quality(i))
        actions.addWidget(play)
        reveal = self.bind_text(QPushButton(), "reveal_video")
        reveal.clicked.connect(lambda _checked=False, i=index: self.open_selected_clip(i))
        actions.addWidget(reveal)
        delete = self.bind_text(QPushButton(), "delete")
        delete.setObjectName("dangerButton")
        delete.clicked.connect(lambda _checked=False, i=index: self.delete_selected_clip(i))
        actions.addWidget(delete)
        layout.addLayout(actions)
        row = index // CLIP_CARD_COLUMNS
        col = index % CLIP_CARD_COLUMNS
        self.cards_grid.addWidget(card, row, col)
        self.thumbnail_labels[index] = preview
        self.play_buttons[index] = play
        self.card_widgets[index] = card

    def current_clip(self, index: int | None = None) -> ClipSegment | None:
        if index is None:
            index = self.selected_clip_index
        if index is None or index < 0 or index >= len(self.clips):
            return None
        return self.clips[index]

    def select_clip(self, index: int | None = None) -> None:
        clip = self.current_clip(index)
        if clip is None:
            self.selected_clip_index = None
            return
        self.selected_clip_index = index

    def open_selected_clip(self, index: int | None = None) -> None:
        clip = self.current_clip(index)
        if clip is None:
            return
        clip_path = Path(clip.path).expanduser().resolve(strict=False)
        if not clip_path.exists():
            self.append_log(self.text("missing_export", path=clip_path) + "\n")
            QMessageBox.critical(self, self.text("app_title"), self.text("missing_export", path=clip_path))
            return
        try:
            reveal_in_explorer(clip_path)
        except Exception as exc:
            self.append_log(self.text("missing_export", path=clip_path) + f"\n{exc}\n")
            QMessageBox.critical(self, self.text("app_title"), self.text("missing_export", path=clip_path))

    def play_low_quality_preview(self, index: int | None = None) -> None:
        if index is None:
            index = self.selected_clip_index
        clip = self.current_clip(index)
        if clip is None or index is None:
            return
        if self.playing_clip_index == index and self.playing_mode == "card":
            self.stop_preview()
            return
        if self.player_process and self.player_process.poll() is None:
            self.stop_preview()
        self.stop_card_preview(reset_image=True)
        self.select_clip(index)
        self.preview_token += 1
        token = self.preview_token
        self.playing_clip_index = index
        self.playing_mode = "card"
        self.set_status("prepare_preview", index=index + 1)
        label = self.thumbnail_labels.get(index)
        if label:
            label.setText(self.text("loading_card_preview"))
        threading.Thread(target=self.card_preview_worker, args=(token, index, clip), daemon=True).start()

    def play_high_quality(self, index: int | None = None) -> None:
        if index is None:
            index = self.selected_clip_index
        clip = self.current_clip(index)
        if clip is None or index is None:
            return
        self.preview_token += 1
        if self.playing_mode == "card":
            self.stop_card_preview(reset_image=True)
        if self.player_process and self.player_process.poll() is None:
            if self.playing_clip_index == index and self.playing_mode == "high":
                self.stop_preview()
                return
            self.stop_preview()
        self.select_clip(index)
        self.start_player(index, Path(clip.path).expanduser().resolve(), "high")

    def start_player(self, index: int, video_path: Path, mode: str) -> None:
        if not video_path.exists():
            QMessageBox.warning(self, self.text("app_title"), self.text("missing_video", path=video_path))
            return
        ffplay = resolve_tool("ffplay")
        if not ffplay:
            QMessageBox.critical(self, self.text("app_title"), self.text("missing_ffplay"))
            return
        title = self.text("low_preview") if mode == "preview" else self.text("high_preview")
        command = [
            ffplay,
            "-hide_banner",
            "-loglevel",
            "error",
            "-autoexit",
            "-window_title",
            f"{self.text('app_title')} - {title} - Highlight #{index + 1:03d}",
            str(video_path),
        ]
        try:
            self.player_process = subprocess.Popen(
                command,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
                **hidden_subprocess_kwargs(),
            )
        except Exception as exc:
            QMessageBox.critical(self, self.text("app_title"), self.text("player_failed", error=exc))
            return
        self.playing_clip_index = index
        self.playing_mode = mode
        if mode == "high":
            self.set_play_button_text(index, self.text("stop_play"))
        self.status_label.setText(f"{title}: Highlight #{index + 1:03d}")
        self.player_timer.start(500)

    def watch_player(self) -> None:
        if self.player_process is None:
            self.player_timer.stop()
            return
        if self.player_process.poll() is None:
            return
        self.player_timer.stop()
        self.player_process = None
        if self.playing_clip_index is not None and self.playing_mode == "high":
            self.set_play_button_text(self.playing_clip_index, self.text("play_high"))
        self.playing_clip_index = None
        self.playing_mode = None
        self.set_status("done")

    def stop_preview(self) -> None:
        self.preview_token += 1
        self.stop_card_preview(reset_image=True)
        if self.playing_clip_index is not None and self.playing_mode == "high":
            self.set_play_button_text(self.playing_clip_index, self.text("play_high"))
        if self.player_process and self.player_process.poll() is None:
            self.player_process.terminate()
        self.player_process = None
        self.playing_clip_index = None
        self.playing_mode = None

    def set_play_button_text(self, index: int, text: str) -> None:
        button = self.play_buttons.get(index)
        if button:
            button.setText(text)

    def delete_selected_clip(self, index: int | None = None) -> None:
        clip = self.current_clip(index)
        if clip is None:
            return
        clip_path = Path(clip.path)
        summary = self.text("clip_summary", kills=clip.kills, start=clip.start, end=clip.end, duration=clip.duration)
        if QMessageBox.question(self, self.text("app_title"), self.text("delete_confirm", summary=summary)) != QMessageBox.StandardButton.Yes:
            return
        self.stop_preview()
        try:
            if clip_path.exists():
                clip_path.unlink()
        except Exception as exc:
            QMessageBox.critical(self, self.text("app_title"), self.text("delete_failed", error=exc))
            return
        self.append_log(self.text("deleted_log", name=clip_path.name))
        resolved = clip_path.expanduser().resolve(strict=False)
        self.clips = [item for item in self.clips if Path(item.path).expanduser().resolve(strict=False) != resolved]
        self.refresh_clip_cards()
        if self.clips:
            self.select_clip(0)

    def thumbnail_worker(self, generation: int, index: int, clip: ClipSegment, seek_seconds: float) -> None:
        try:
            self.bridge.event.emit("thumbnail_ready", (generation, index, self.thumbnail_for(clip, seek_seconds)))
        except Exception:
            self.bridge.event.emit("thumbnail_error", (generation, index))

    def thumbnail_for(self, clip: ClipSegment, seek_seconds: float) -> Path:
        clip_path = Path(clip.path).expanduser().resolve()
        if not clip_path.exists():
            raise FileNotFoundError(clip_path)
        cache_dir = self.thumbnail_cache_dir / self.thumbnail_cache_key(clip, seek_seconds)
        cache_dir.mkdir(parents=True, exist_ok=True)
        thumbnail_path = cache_dir / "thumbnail.jpg"
        if thumbnail_path.exists():
            return thumbnail_path
        ffmpeg = resolve_tool("ffmpeg")
        if not ffmpeg:
            raise RuntimeError("ffmpeg unavailable")
        command = [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-ss",
            f"{seek_seconds:.3f}",
            "-i",
            str(clip_path),
            "-frames:v",
            "1",
            "-vf",
            f"scale={THUMBNAIL_WIDTH}:-2:flags=lanczos",
            "-q:v",
            "3",
            str(thumbnail_path),
        ]
        result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **hidden_subprocess_kwargs())
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "thumbnail failed")
        return thumbnail_path

    def thumbnail_cache_key(self, clip: ClipSegment, seek_seconds: float) -> str:
        clip_path = Path(clip.path).expanduser().resolve()
        stat = clip_path.stat()
        source = f"{clip_path}:{stat.st_size}:{stat.st_mtime_ns}:{THUMBNAIL_WIDTH}x{THUMBNAIL_HEIGHT}:{seek_seconds:.3f}"
        return hashlib.sha1(source.encode("utf-8")).hexdigest()

    def thumbnail_seek_seconds(self, clip: ClipSegment) -> float:
        if clip.duration <= 0.3:
            return 0.0
        return min(max(0.1, float(self.seconds_before.value())), max(0.0, clip.duration - 0.2))

    def handle_thumbnail_ready(self, generation: int, index: int, image_path: Path) -> None:
        if generation != self.thumbnail_generation or index not in self.thumbnail_labels:
            return
        pixmap = self.fit_thumbnail(QPixmap(str(image_path)))
        self.thumbnail_pixmaps[index] = pixmap
        if self.playing_mode == "card" and self.playing_clip_index == index:
            return
        self.thumbnail_labels[index].setPixmap(pixmap)

    def handle_thumbnail_error(self, generation: int, index: int) -> None:
        if generation != self.thumbnail_generation or index not in self.thumbnail_labels:
            return
        self.thumbnail_labels[index].setText(self.text("preview_failed"))

    def fit_thumbnail(self, source: QPixmap) -> QPixmap:
        if source.isNull():
            return QPixmap()
        scaled = source.scaled(
            THUMBNAIL_WIDTH,
            THUMBNAIL_HEIGHT,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        result = QPixmap(THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT)
        result.fill(QColor(8, 13, 24))
        painter = QPainter(result)
        x = (THUMBNAIL_WIDTH - scaled.width()) // 2
        y = (THUMBNAIL_HEIGHT - scaled.height()) // 2
        painter.drawPixmap(x, y, scaled)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(0, 0, 0, 118))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(THUMBNAIL_WIDTH // 2 - 24, THUMBNAIL_HEIGHT // 2 - 24, 48, 48)
        path = QPainterPath()
        path.moveTo(THUMBNAIL_WIDTH // 2 - 7, THUMBNAIL_HEIGHT // 2 - 14)
        path.lineTo(THUMBNAIL_WIDTH // 2 - 7, THUMBNAIL_HEIGHT // 2 + 14)
        path.lineTo(THUMBNAIL_WIDTH // 2 + 16, THUMBNAIL_HEIGHT // 2)
        path.closeSubpath()
        painter.setBrush(QColor(255, 255, 255, 225))
        painter.drawPath(path)
        painter.end()
        return result

    def card_preview_worker(self, token: int, index: int, clip: ClipSegment) -> None:
        try:
            self.bridge.event.emit("card_preview_ready", (token, index, self.card_preview_frames_for(clip)))
        except Exception as exc:
            self.bridge.event.emit("card_preview_error", (token, str(exc)))

    def card_preview_frames_for(self, clip: ClipSegment) -> list[Path]:
        clip_path = Path(clip.path).expanduser().resolve()
        if not clip_path.exists():
            raise FileNotFoundError(clip_path)
        cache_dir = self.card_preview_cache_dir / self.card_preview_cache_key(clip)
        cache_dir.mkdir(parents=True, exist_ok=True)
        frames = sorted(cache_dir.glob("frame_*.jpg"))
        if frames:
            return frames
        ffmpeg = resolve_tool("ffmpeg")
        if not ffmpeg:
            raise RuntimeError("ffmpeg unavailable")
        temporary_dir = cache_dir / "tmp"
        if temporary_dir.exists():
            for old in temporary_dir.glob("*.jpg"):
                old.unlink()
        temporary_dir.mkdir(parents=True, exist_ok=True)
        command = [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(clip_path),
            "-vf",
            f"fps={CARD_PREVIEW_FPS},scale={THUMBNAIL_WIDTH}:{THUMBNAIL_HEIGHT}:force_original_aspect_ratio=decrease:flags=lanczos,"
            f"pad={THUMBNAIL_WIDTH}:{THUMBNAIL_HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=black",
            "-q:v",
            "3",
            str(temporary_dir / "frame_%05d.jpg"),
        ]
        result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **hidden_subprocess_kwargs())
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "card preview failed")
        frames = sorted(temporary_dir.glob("frame_*.jpg"))
        if not frames:
            raise RuntimeError("no preview frames generated")
        for frame in frames:
            frame.replace(cache_dir / frame.name)
        temporary_dir.rmdir()
        return sorted(cache_dir.glob("frame_*.jpg"))

    def card_preview_cache_key(self, clip: ClipSegment) -> str:
        clip_path = Path(clip.path).expanduser().resolve()
        stat = clip_path.stat()
        source = f"{clip_path}:{stat.st_size}:{stat.st_mtime_ns}:card_preview={THUMBNAIL_WIDTH}x{THUMBNAIL_HEIGHT}:fps={CARD_PREVIEW_FPS}:q=3"
        return hashlib.sha1(source.encode("utf-8")).hexdigest()

    def handle_card_preview_ready(self, token: int, index: int, frames: list[Path]) -> None:
        if token != self.preview_token or self.playing_clip_index != index or self.playing_mode != "card":
            return
        self.card_preview_pixmaps = [QPixmap(str(frame)) for frame in frames]
        self.card_preview_frame_index = 0
        self.set_status("preview_inside", index=index + 1)
        self.preview_timer.start(int(1000 / CARD_PREVIEW_FPS))

    def handle_card_preview_error(self, token: int, message: str) -> None:
        if token != self.preview_token:
            return
        self.stop_card_preview()
        self.set_status("preview_failed")
        QMessageBox.critical(self, self.text("app_title"), self.text("card_preview_failed", error=message))

    def advance_card_preview(self) -> None:
        index = self.playing_clip_index
        if index is None or self.playing_mode != "card" or not self.card_preview_pixmaps:
            return
        label = self.thumbnail_labels.get(index)
        if label is None:
            self.stop_card_preview(reset_image=False)
            return
        if self.card_preview_frame_index >= len(self.card_preview_pixmaps):
            self.stop_card_preview()
            if self.status_key == "preview_inside":
                self.set_status("done")
            return
        label.setPixmap(self.card_preview_pixmaps[self.card_preview_frame_index])
        self.card_preview_frame_index += 1

    def stop_card_preview(self, reset_image: bool = True) -> None:
        self.preview_timer.stop()
        if reset_image and self.playing_clip_index is not None and self.playing_mode == "card":
            label = self.thumbnail_labels.get(self.playing_clip_index)
            pixmap = self.thumbnail_pixmaps.get(self.playing_clip_index)
            if label:
                if pixmap:
                    label.setPixmap(pixmap)
                else:
                    label.setPixmap(QPixmap())
                    label.setText(self.text("loading_preview"))
        self.card_preview_pixmaps = []
        self.card_preview_frame_index = 0
        if self.playing_mode == "card":
            self.playing_clip_index = None
            self.playing_mode = None

    def closeEvent(self, event) -> None:
        self.stop_preview()
        event.accept()


def main() -> None:
    if hasattr(Qt, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
