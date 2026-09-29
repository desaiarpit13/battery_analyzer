"""
VOLTIX PRO // Neo-Brutalist Battery Analyzer & Electrochemical Telemetry Suite
High-Contrast Neo-Brutalist Workstation UI with Unblurred Hard Offset Drop Shadows,
Vibrant Accent Color-Blocking, Bold Outlines, Dynamic Tactile Shadows, and Physical HUD.
"""

import sys
import os
import time
import webbrowser
import numpy as np
import pandas as pd

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QDoubleSpinBox, QFileDialog,
    QStackedWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QSlider, QProgressBar, QFrame, QSplitter, QMessageBox,
    QScrollArea, QLineEdit, QSizePolicy, QButtonGroup,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot, QSize
from PySide6.QtGui import (
    QFont, QColor, QPalette, QIcon, QPainter, QBrush, QPen,
    QLinearGradient, QRadialGradient, QPixmap
)

import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from battery_engine import BatteryDataset, load_and_analyze, export_html_report, BatteryMetrics


# ==============================================================================
# HARD OFFSET SHADOW HELPERS & BRUTALIST CONTROLS
# ==============================================================================
def apply_brutalist_shadow(widget: QWidget, offset: int = 5, color: str = "#000000"):
    """Applies a razor-sharp, unblurred hard offset drop shadow (Neo-Brutalism signature)."""
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(0)
    shadow.setOffset(offset, offset)
    shadow.setColor(QColor(color))
    widget.setGraphicsEffect(shadow)
    return shadow


class BrutalistButton(QPushButton):
    """Tactile Neo-Brutalist button with an unblurred hard offset shadow that physically depresses on click."""

    def __init__(self, text: str = "", parent=None, offset: int = 4):
        super().__init__(text, parent)
        self.default_offset = offset
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(0)
        self.shadow.setOffset(offset, offset)
        self.shadow.setColor(QColor("#000000"))
        self.setGraphicsEffect(self.shadow)

    def mousePressEvent(self, event):
        self.shadow.setOffset(1, 1)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.shadow.setOffset(self.default_offset, self.default_offset)
        super().mouseReleaseEvent(event)


class BrutalistNavButton(QPushButton):
    """Sidebar navigation button with hard offset shadow and active depressed state."""

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setProperty("class", "NavButton")
        self.setCheckable(True)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(0)
        self.shadow.setOffset(4, 4)
        self.shadow.setColor(QColor("#000000"))
        self.setGraphicsEffect(self.shadow)
        self.toggled.connect(self._on_toggled)

    def _on_toggled(self, checked: bool):
        if checked:
            self.shadow.setOffset(1, 1)
        else:
            self.shadow.setOffset(4, 4)


# ==============================================================================
# NEO-BRUTALIST THEME (QSS)
# ==============================================================================
NEOBRUTALISM_QSS = """
/* Global Canvas / Window */
QMainWindow, QWidget#MainRoot {
    background-color: #f4efe6;
    color: #000000;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Inter', Roboto, sans-serif;
}

/* Sidebar Rail */
QFrame#Sidebar {
    background-color: #fffdf8;
    border-right: 3px solid #000000;
    min-width: 250px;
    max-width: 260px;
}

/* Sidebar Navigation Buttons */
QPushButton.NavButton {
    background-color: #ffffff;
    color: #000000;
    border: 2.5px solid #000000;
    border-radius: 6px;
    padding: 10px 14px;
    text-align: left;
    font-size: 13px;
    font-weight: 800;
    margin-bottom: 3px;
}
QPushButton.NavButton:hover {
    background-color: #fef08a;
    color: #000000;
}
QPushButton.NavButton:checked {
    background-color: #ffe600;
    color: #000000;
    border: 3px solid #000000;
    font-weight: 900;
}

/* Cards & Containers */
QFrame#TopNavBar, QFrame#HeroCard, QFrame#PanelCard, QFrame#SimCard, QFrame#SidebarCard {
    background-color: #ffffff;
    border: 2.5px solid #000000;
    border-radius: 8px;
}
QFrame#HeroCard {
    background-color: #ffffff;
    border: 2.5px solid #000000;
}
QFrame#HeroCard:hover {
    background-color: #ffffff;
}

/* Labels & Typography */
QLabel {
    color: #000000;
}
QLabel#BrandTitle {
    font-size: 20px;
    font-weight: 900;
    color: #000000;
    letter-spacing: 0.5px;
}
QLabel#MutedLabel {
    color: #1e293b;
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
QLabel#HeroTitle {
    color: #000000;
    font-size: 11px;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}
QLabel#HeroValue {
    color: #000000;
    font-size: 22px;
    font-weight: 900;
}
QLabel#HeroSub {
    color: #334155;
    font-size: 11px;
    font-weight: 700;
}

/* Buttons */
QPushButton {
    background-color: #ffffff;
    color: #000000;
    border: 2.5px solid #000000;
    border-radius: 6px;
    padding: 7px 14px;
    font-weight: 800;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #fef08a;
    color: #000000;
}
QPushButton:pressed {
    background-color: #e2e8f0;
}
QPushButton#PrimaryGlowBtn {
    background-color: #ffe600;
    color: #000000;
    border: 2.5px solid #000000;
    font-weight: 900;
    border-radius: 6px;
}
QPushButton#PrimaryGlowBtn:hover {
    background-color: #facc15;
    color: #000000;
}
QPushButton#AccentGlowBtn {
    background-color: #00f0ff;
    color: #000000;
    border: 2.5px solid #000000;
    border-radius: 6px;
    font-weight: 900;
}
QPushButton#AccentGlowBtn:hover {
    background-color: #38bdf8;
    color: #000000;
}

/* Inputs & Combos */
QComboBox, QDoubleSpinBox, QLineEdit {
    background-color: #ffffff;
    border: 2px solid #000000;
    border-radius: 6px;
    padding: 6px 10px;
    color: #000000;
    font-size: 12px;
    font-weight: 700;
}
QComboBox:focus, QDoubleSpinBox:focus, QLineEdit:focus {
    background-color: #fef9c3;
    border: 2.5px solid #000000;
}
QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 2.5px solid #000000;
    color: #000000;
    selection-background-color: #ffe600;
    selection-color: #000000;
    font-weight: 700;
}

/* Table Widget */
QTableWidget {
    background-color: #ffffff;
    border: 2.5px solid #000000;
    border-radius: 8px;
    gridline-color: #cbd5e1;
    color: #000000;
    font-size: 12px;
    font-weight: 600;
}
QHeaderView::section {
    background-color: #ffe600;
    color: #000000;
    padding: 8px 10px;
    border: 1px solid #000000;
    font-weight: 900;
    font-size: 12px;
}
QTableWidget::item:selected {
    background-color: #00f0ff;
    color: #000000;
}

/* ScrollBars */
QScrollBar:vertical {
    background: #f1efe9;
    border: 1.5px solid #000000;
    width: 9px;
    margin: 0px;
    border-radius: 0px;
}
QScrollBar::handle:vertical {
    background: #000000;
    min-height: 20px;
    border-radius: 0px;
}
QScrollBar::handle:vertical:hover {
    background: #ffe600;
}
QScrollBar:horizontal {
    background: #f1efe9;
    border: 1.5px solid #000000;
    height: 9px;
    margin: 0px;
    border-radius: 0px;
}
QScrollBar::handle:horizontal {
    background: #000000;
    min-width: 20px;
    border-radius: 0px;
}
QScrollBar::handle:horizontal:hover {
    background: #ffe600;
}
QScrollBar::add-line, QScrollBar::sub-line {
    background: none;
    border: none;
}

/* Slider */
QSlider::groove:horizontal {
    border: 2.5px solid #000000;
    height: 8px;
    background: #ffffff;
    border-radius: 4px;
}
QSlider::sub-page:horizontal {
    background: #ffe600;
    border: 2.5px solid #000000;
    border-radius: 4px;
}
QSlider::handle:horizontal {
    background: #000000;
    border: 2px solid #000000;
    width: 16px;
    margin-top: -6px;
    margin-bottom: -6px;
    border-radius: 8px;
}
QSlider::handle:horizontal:hover {
    background: #ffe600;
}

/* HUD Frame */
QFrame#HudFrame {
    background-color: #f8fafc;
    border: 2px solid #000000;
    border-radius: 6px;
}
QFrame#HudFrame QLabel {
    border: none;
    background: transparent;
}
"""
STUDIO_QSS = NEOBRUTALISM_QSS  # Backwards compatibility alias


# ==============================================================================
# HIGH-DEFINITION NEO-BRUTALIST MATPLOTLIB CANVAS
# ==============================================================================
class StudioMplCanvas(FigureCanvas):
    """Reusable high-resolution Matplotlib canvas with custom Neo-Brutalist aesthetic."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor="#ffffff")
        super().__init__(self.fig)
        self.setParent(parent)
        self.setStyleSheet("background-color: #ffffff; border: 2.5px solid #000000; border-radius: 8px;")

    def apply_studio_theme(self, ax):
        """Applies a crisp high-contrast Neo-Brutalist engineering theme to an axis."""
        ax.set_facecolor("#fafaf9")
        ax.tick_params(colors="#000000", labelsize=9, which="both")
        ax.xaxis.label.set_color("#000000")
        ax.xaxis.label.set_fontweight("bold")
        ax.yaxis.label.set_color("#000000")
        ax.yaxis.label.set_fontweight("bold")
        ax.title.set_color("#000000")
        ax.title.set_fontsize(11)
        ax.title.set_fontweight("bold")
        for spine in ax.spines.values():
            spine.set_color("#000000")
            spine.set_linewidth(2.0)
        ax.grid(True, linestyle="--", alpha=0.5, color="#cbd5e1")


# ==============================================================================
# PHYSICAL CELL VISUAL GAUGE (NEO-BRUTALIST HARD SHADOW GRAPHIC)
# ==============================================================================
class BatteryCell3DWidget(QWidget):
    """Neo-Brutalist high-contrast cross-section battery cell with fluid level depletion and hard offset shadows."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.soc_pct = 100.0
        self.voltage = 4.20
        self.setFixedSize(164, 164)

    def set_values(self, soc_pct: float, voltage: float):
        self.soc_pct = max(0.0, min(100.0, soc_pct))
        self.voltage = voltage
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # Terminal cap at top
        cap_w = 36
        cap_h = 8
        cap_x = (w - cap_w) // 2
        cap_y = 6

        # Terminal cap hard offset shadow (4px offset)
        painter.fillRect(cap_x + 4, cap_y + 4, cap_w, cap_h, QColor("#000000"))
        # Terminal cap body
        painter.setBrush(QBrush(QColor("#ffe600")))
        painter.setPen(QPen(QColor("#000000"), 2.5))
        painter.drawRoundedRect(cap_x, cap_y, cap_w, cap_h, 3, 3)

        # Outer battery cylinder
        body_x = 24
        body_y = 15
        body_w = w - 48
        body_h = h - 48

        # Hard offset unblurred shadow (6px down, 6px right)
        painter.fillRect(body_x + 6, body_y + 6, body_w, body_h, QColor("#000000"))

        # Cylinder white background
        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.setPen(QPen(QColor("#000000"), 3.0))
        painter.drawRoundedRect(body_x, body_y, body_w, body_h, 8, 8)

        # Fluid Level
        fill_margin = 5
        max_fill_h = body_h - (fill_margin * 2)
        fill_h = int(max_fill_h * (self.soc_pct / 100.0))
        fill_y = body_y + body_h - fill_margin - fill_h
        fill_x = body_x + fill_margin
        fill_w = body_w - (fill_margin * 2)

        if fill_h > 2:
            if self.soc_pct > 50:
                col = QColor("#00f076")  # Vivid Lime
            elif self.soc_pct > 20:
                col = QColor("#ffe600")  # Electric Yellow
            else:
                col = QColor("#ff3366")  # Neon Red/Pink

            painter.setBrush(QBrush(col))
            painter.setPen(QPen(QColor("#000000"), 2.0))
            painter.drawRoundedRect(fill_x, fill_y, fill_w, fill_h, 5, 5)

        # Text inside battery: Black text on white/yellow pill with hard shadow
        text_bg_w = body_w - 16
        text_bg_h = 38
        text_bg_x = body_x + 8
        text_bg_y = body_y + (body_h // 2) - 19

        # Text badge hard offset shadow (3px)
        painter.fillRect(text_bg_x + 3, text_bg_y + 3, text_bg_w, text_bg_h, QColor("#000000"))
        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.setPen(QPen(QColor("#000000"), 2.0))
        painter.drawRoundedRect(text_bg_x, text_bg_y, text_bg_w, text_bg_h, 6, 6)

        painter.setPen(QColor("#000000"))
        font_pct = QFont("Segoe UI", 13, QFont.Black)
        painter.setFont(font_pct)
        painter.drawText(text_bg_x, text_bg_y + 2, text_bg_w, 18, Qt.AlignCenter, f"{self.soc_pct:.1f}%")

        font_v = QFont("Segoe UI", 10, QFont.Bold)
        painter.setFont(font_v)
        painter.drawText(text_bg_x, text_bg_y + 20, text_bg_w, 16, Qt.AlignCenter, f"{self.voltage:.2f} V")

        # Bottom label pill with hard offset shadow
        sub_w = 114
        sub_h = 20
        sub_x = (w - sub_w) // 2
        sub_y = h - 24

        painter.fillRect(sub_x + 3, sub_y + 3, sub_w, sub_h, QColor("#000000"))
        painter.setBrush(QBrush(QColor("#ffe600")))
        painter.setPen(QPen(QColor("#000000"), 2.0))
        painter.drawRoundedRect(sub_x, sub_y, sub_w, sub_h, 4, 4)

        font_sub = QFont("Segoe UI", 8, QFont.Black)
        painter.setFont(font_sub)
        painter.setPen(QColor("#000000"))
        painter.drawText(sub_x, sub_y, sub_w, sub_h, Qt.AlignCenter, "ESTIMATED SOC")


# ==============================================================================
# MAIN APPLICATION WINDOW (NEO-BRUTALIST WORKSTATION)
# ==============================================================================
class ModernBatteryAnalyzer(QMainWindow):
    """Voltix Pro // Neo-Brutalist Battery Analyzer & Electrochemical Telemetry Suite."""

    def __init__(self, initial_csv: str = "Battery_data.csv"):
        super().__init__()
        self.setWindowTitle("VOLTIX PRO // Neo-Brutalist Battery Telemetry Suite")
        self.resize(1360, 900)
        self.setMinimumSize(1100, 740)

        self.initial_csv = initial_csv
        self.dataset = None

        # Playback timer
        self.play_timer = QTimer(self)
        self.play_timer.timeout.connect(self._on_playback_tick)
        self.play_idx = 0
        self.playback_speed = 1

        self._init_ui()

        # Load initial data if exists
        if os.path.exists(self.initial_csv):
            self.load_dataset(self.initial_csv)
        else:
            alt = self.initial_csv.lower()
            if os.path.exists(alt):
                self.load_dataset(alt)

    def _init_ui(self):
        """Constructs the Neo-Brutalist Workspace layout with Sidebar Rail and Main Canvas."""
        root = QWidget()
        root.setObjectName("MainRoot")
        self.setCentralWidget(root)

        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Left Sidebar
        sidebar = self._build_sidebar()
        root_layout.addWidget(sidebar)

        # 2. Right Main Canvas Container
        canvas_container = QWidget()
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(18, 14, 18, 14)
        canvas_layout.setSpacing(14)

        # Top Bar
        top_bar = self._build_top_bar()
        canvas_layout.addWidget(top_bar)

        # Hero KPI Row
        hero_row = self._build_hero_kpis()
        canvas_layout.addWidget(hero_row)

        # Main Stacked Views (Studio Pages)
        self.pages = QStackedWidget()
        self.pages.addWidget(self._build_page_cockpit())          # Index 0: Overview Cockpit
        self.pages.addWidget(self._build_page_electrochemistry()) # Index 1: Electrochemical Lab
        self.pages.addWidget(self._build_page_simulation())       # Index 2: Cell Simulator
        self.pages.addWidget(self._build_page_matrix())           # Index 3: Telemetry Matrix
        self.pages.addWidget(self._build_page_report())           # Index 4: Diagnostic Certificate
        self.pages.currentChanged.connect(self._on_page_changed)
        canvas_layout.addWidget(self.pages, stretch=1)

        # Footer Status
        self.status_bar_label = QLabel("● Ready • Neo-Brutalist Telemetry Workstation Initialized")
        self.status_bar_label.setStyleSheet("color: #000000; font-size: 11px; font-weight: 800; padding: 2px 4px;")
        canvas_layout.addWidget(self.status_bar_label)

        root_layout.addWidget(canvas_container, stretch=1)

    def _on_page_changed(self, idx: int):
        btn = self.nav_group.button(idx)
        if btn and not btn.isChecked():
            btn.setChecked(True)

    # --------------------------------------------------------------------------
    # LEFT SIDEBAR
    # --------------------------------------------------------------------------
    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(14, 18, 14, 18)
        layout.setSpacing(14)

        # Brand header
        brand_box = QVBoxLayout()
        brand_box.setSpacing(4)
        brand_lbl = QLabel("⚡ VOLTIX PRO")
        brand_lbl.setObjectName("BrandTitle")

        ver_row = QHBoxLayout()
        badge_ver = QLabel("NEO-BRUTALIST")
        badge_ver.setStyleSheet("background: #ffe600; color: #000000; border: 1.5px solid #000000; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 900;")
        apply_brutalist_shadow(badge_ver, offset=2)

        status_dot = QLabel("● ACTIVE")
        status_dot.setStyleSheet("background: #00f076; color: #000000; border: 1.5px solid #000000; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 900;")
        apply_brutalist_shadow(status_dot, offset=2)

        ver_row.addWidget(badge_ver)
        ver_row.addWidget(status_dot)
        ver_row.addStretch(1)

        brand_box.addWidget(brand_lbl)
        brand_box.addLayout(ver_row)
        layout.addLayout(brand_box)

        # Section Label
        sec_nav = QLabel("WORKSPACES")
        sec_nav.setObjectName("MutedLabel")
        layout.addWidget(sec_nav)

        # Navigation Buttons (Radio group with dynamic hard offset shadows)
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        nav_items = [
            ("📊  Overview Cockpit", 0),
            ("⚡  Electrochemical Lab", 1),
            ("🕹️  Cell Simulator", 2),
            ("📋  Telemetry Matrix", 3),
            ("📑  Diagnostic Report", 4)
        ]

        for text, idx in nav_items:
            btn = BrutalistNavButton(text)
            if idx == 0:
                btn.setChecked(True)
            btn.clicked.connect(lambda checked, i=idx: self.pages.setCurrentIndex(i))
            self.nav_group.addButton(btn, idx)
            layout.addWidget(btn)

        layout.addSpacing(6)

        # Section Label: Parameters
        sec_cfg = QLabel("CELL PARAMETERS")
        sec_cfg.setObjectName("MutedLabel")
        layout.addWidget(sec_cfg)

        # Card for Chemistry & Specs (Hard offset shadow 5px)
        cfg_card = QFrame()
        cfg_card.setObjectName("SidebarCard")
        apply_brutalist_shadow(cfg_card, offset=5)
        cfg_lay = QVBoxLayout(cfg_card)
        cfg_lay.setContentsMargins(12, 12, 12, 12)
        cfg_lay.setSpacing(10)

        # Chemistry combo
        lbl_chem = QLabel("Chemistry Preset:")
        lbl_chem.setObjectName("MutedLabel")
        self.combo_chem = QComboBox()
        self.combo_chem.addItems([
            "Li-ion NMC (4.2V)",
            "LiFePO4 / LFP (3.65V)",
            "LTO / Titanate (2.8V)",
            "NiMH (1.45V)",
            "Custom"
        ])
        apply_brutalist_shadow(self.combo_chem, offset=3)
        self.combo_chem.currentIndexChanged.connect(self._on_chem_changed)
        cfg_lay.addWidget(lbl_chem)
        cfg_lay.addWidget(self.combo_chem)

        # Rated Capacity
        lbl_cap = QLabel("Nominal Rating (Ah):")
        lbl_cap.setObjectName("MutedLabel")
        self.spin_capacity = QDoubleSpinBox()
        self.spin_capacity.setRange(0.05, 500.0)
        self.spin_capacity.setValue(2.00)
        self.spin_capacity.setSingleStep(0.1)
        self.spin_capacity.setSuffix(" Ah")
        apply_brutalist_shadow(self.spin_capacity, offset=3)
        self.spin_capacity.valueChanged.connect(self._recalc_with_params)
        cfg_lay.addWidget(lbl_cap)
        cfg_lay.addWidget(self.spin_capacity)

        # Cutoff Voltage
        lbl_cut = QLabel("Cutoff Voltage (V):")
        lbl_cut.setObjectName("MutedLabel")
        self.spin_cutoff = QDoubleSpinBox()
        self.spin_cutoff.setRange(0.5, 100.0)
        self.spin_cutoff.setValue(3.20)
        self.spin_cutoff.setSingleStep(0.05)
        self.spin_cutoff.setSuffix(" V")
        apply_brutalist_shadow(self.spin_cutoff, offset=3)
        self.spin_cutoff.valueChanged.connect(self._recalc_with_params)
        cfg_lay.addWidget(lbl_cut)
        cfg_lay.addWidget(self.spin_cutoff)

        layout.addWidget(cfg_card)

        layout.addStretch(1)

        # Bottom load button in sidebar (Tactile Brutalist Button)
        self.btn_load_side = BrutalistButton("📂 Open CSV File", offset=4)
        self.btn_load_side.setObjectName("PrimaryGlowBtn")
        self.btn_load_side.setFixedHeight(38)
        self.btn_load_side.clicked.connect(self.on_open_file_dialog)
        layout.addWidget(self.btn_load_side)

        return sidebar

    # --------------------------------------------------------------------------
    # TOP CANVAS BAR
    # --------------------------------------------------------------------------
    def _build_top_bar(self) -> QWidget:
        top_bar = QFrame()
        top_bar.setObjectName("TopNavBar")
        apply_brutalist_shadow(top_bar, offset=5)
        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(14)

        # Breadcrumb / Dataset indicator
        self.lbl_dataset = QLabel("📁 Battery_data.csv")
        self.lbl_dataset.setStyleSheet("background: #ffe600; border: 2px solid #000000; padding: 6px 14px; border-radius: 6px; font-weight: 900; color: #000000; font-size: 12px;")
        apply_brutalist_shadow(self.lbl_dataset, offset=3)
        layout.addWidget(self.lbl_dataset)

        self.lbl_points_badge = QLabel("80 points • 10.0s rate")
        self.lbl_points_badge.setStyleSheet("background: #ffffff; border: 1.5px solid #000000; padding: 5px 12px; border-radius: 6px; color: #000000; font-size: 11px; font-weight: 800;")
        apply_brutalist_shadow(self.lbl_points_badge, offset=3)
        layout.addWidget(self.lbl_points_badge)

        layout.addStretch(1)

        # Actions (Tactile Buttons with Hard Offset Shadows)
        btn_html = BrutalistButton("🌐 Web Dashboard", offset=4)
        btn_html.setObjectName("AccentGlowBtn")
        btn_html.clicked.connect(self.on_export_html)
        layout.addWidget(btn_html)

        btn_snap = BrutalistButton("📸 Snap Charts", offset=4)
        btn_snap.clicked.connect(self.on_save_charts)
        layout.addWidget(btn_snap)

        return top_bar

    # --------------------------------------------------------------------------
    # HERO KPI CARDS (PROMINENT 5PX HARD SHADOWS)
    # --------------------------------------------------------------------------
    def _build_hero_kpis(self) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 8, 8)
        layout.setSpacing(14)

        kpi_configs = [
            ("Terminal Voltage", "kpi_v_val", "kpi_v_sub", "#0284c7", "#e0f2fe"),
            ("Delivered Capacity", "kpi_cap_val", "kpi_cap_sub", "#16a34a", "#dcfce7"),
            ("Delivered Energy", "kpi_wh_val", "kpi_wh_sub", "#eab308", "#fef9c3"),
            ("Current & Power", "kpi_ip_val", "kpi_ip_sub", "#ea580c", "#ffedd5"),
            ("Cell Health Grade", "kpi_health_val", "kpi_health_sub", "#db2777", "#fce7f3"),
        ]

        def make_kpi(title: str, val_attr: str, sub_attr: str, accent: str, bg_color: str):
            card = QFrame()
            card.setObjectName("HeroCard")
            card.setStyleSheet(f"background-color: {bg_color}; border: 2.5px solid #000000; border-radius: 8px;")
            apply_brutalist_shadow(card, offset=5)
            c_lay = QVBoxLayout(card)
            c_lay.setContentsMargins(14, 12, 14, 12)
            c_lay.setSpacing(4)

            stripe = QFrame()
            stripe.setFixedHeight(4)
            stripe.setStyleSheet(f"background-color: {accent}; border-radius: 2px;")
            c_lay.addWidget(stripe)

            t = QLabel(title)
            t.setObjectName("HeroTitle")
            c_lay.addWidget(t)

            v = QLabel("--")
            v.setObjectName("HeroValue")
            setattr(self, val_attr, v)
            c_lay.addWidget(v)

            s = QLabel("--")
            s.setObjectName("HeroSub")
            setattr(self, sub_attr, s)
            c_lay.addWidget(s)

            return card

        for title, val_attr, sub_attr, accent, bg_color in kpi_configs:
            layout.addWidget(make_kpi(title, val_attr, sub_attr, accent, bg_color))

        return container

    # --------------------------------------------------------------------------
    # PAGE 0: OVERVIEW COCKPIT (6PX HARD SHADOW CANVAS)
    # --------------------------------------------------------------------------
    def _build_page_cockpit(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(4, 4, 10, 10)

        self.canvas_cockpit = StudioMplCanvas(page, width=10, height=6)
        apply_brutalist_shadow(self.canvas_cockpit, offset=6)
        layout.addWidget(self.canvas_cockpit)
        return page

    def _render_page_cockpit(self):
        if not self.dataset:
            return

        df = self.dataset.df
        m = self.dataset.metrics
        fig = self.canvas_cockpit.fig
        fig.clear()

        gs = fig.add_gridspec(2, 2, hspace=0.46, wspace=0.30, top=0.92, bottom=0.10, left=0.07, right=0.93)
        ax1 = fig.add_subplot(gs[0, 0])
        ax2 = fig.add_subplot(gs[0, 1])
        ax3 = fig.add_subplot(gs[1, 0])
        ax4 = fig.add_subplot(gs[1, 1])

        for ax in [ax1, ax2, ax3, ax4]:
            self.canvas_cockpit.apply_studio_theme(ax)

        # 1. Voltage vs Time
        ax1.plot(df["Time"], df["Voltage"], color="#0284c7", linewidth=2.8, label="Voltage (V)")
        ax1.axhline(m.v_cutoff, color="#dc2626", linestyle="--", linewidth=2.0, alpha=0.9, label=f"Cutoff ({m.v_cutoff:.2f}V)")
        ax1.axhline(m.plateau_v_mean, color="#16a34a", linestyle=":", linewidth=2.0, alpha=0.9, label=f"Plateau ({m.plateau_v_mean:.2f}V)")
        ax1.fill_between(df["Time"], df["Voltage"], m.v_cutoff, color="#0284c7", alpha=0.15)
        ax1.set_title("Voltage vs Time (Discharge Profile)")
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Voltage (V)")
        ax1.legend(loc="upper right", facecolor="#ffffff", edgecolor="#000000", labelcolor="#000000", fontsize=8)

        # 2. Dynamic Load Drain (Current & Power)
        ax2.plot(df["Time"], df["Current"], color="#ea580c", linewidth=2.4, label="Current (A)")
        ax2.set_title("Current & Power Drain vs Time")
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel("Current (A)", color="#ea580c")
        ax2.tick_params(axis="y", labelcolor="#ea580c")

        ax2_p = ax2.twinx()
        ax2_p.plot(df["Time"], df["Power"], color="#7c3aed", linewidth=2.2, linestyle="-.", label="Power (W)")
        ax2_p.set_ylabel("Power (W)", color="#7c3aed")
        ax2_p.tick_params(axis="y", labelcolor="#7c3aed")
        for spine in ax2_p.spines.values():
            spine.set_color("#000000")
            spine.set_linewidth(2.0)

        # 3. Capacity & Energy Accumulation
        ax3.plot(df["Time"], df["Capacity_mAh"], color="#16a34a", linewidth=2.4, label="Capacity (mAh)")
        ax3.set_title("Delivered Capacity & Energy Accumulation")
        ax3.set_xlabel("Time (s)")
        ax3.set_ylabel("Capacity (mAh)", color="#16a34a")
        ax3.tick_params(axis="y", labelcolor="#16a34a")

        ax3_e = ax3.twinx()
        ax3_e.plot(df["Time"], df["Energy_Wh"], color="#d97706", linewidth=2.4, linestyle="--", label="Energy (Wh)")
        ax3_e.set_ylabel("Energy (Wh)", color="#d97706")
        ax3_e.tick_params(axis="y", labelcolor="#d97706")
        for spine in ax3_e.spines.values():
            spine.set_color("#000000")
            spine.set_linewidth(2.0)

        # 4. Definitive V vs Capacity
        ax4.plot(df["Capacity_Ah"], df["Voltage"], color="#0284c7", linewidth=2.8)
        ax4.set_title("V vs Delivered Capacity (Definitive Curve)")
        ax4.set_xlabel("Delivered Capacity (Ah)")
        ax4.set_ylabel("Voltage (V)")
        ax4.scatter([df["Capacity_Ah"].iloc[0], df["Capacity_Ah"].iloc[-1]],
                    [df["Voltage"].iloc[0], df["Voltage"].iloc[-1]],
                    color="#ffe600", edgecolors="#000000", linewidths=2.0, s=65, zorder=5)

        self.canvas_cockpit.draw()

    # --------------------------------------------------------------------------
    # PAGE 1: ELECTROCHEMICAL LAB (6PX HARD SHADOW CANVAS)
    # --------------------------------------------------------------------------
    def _build_page_electrochemistry(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(4, 4, 10, 10)

        self.canvas_electro = StudioMplCanvas(page, width=10, height=6)
        apply_brutalist_shadow(self.canvas_electro, offset=6)
        layout.addWidget(self.canvas_electro)
        return page

    def _render_page_electrochemistry(self):
        if not self.dataset:
            return

        df = self.dataset.df
        fig = self.canvas_electro.fig
        fig.clear()

        gs = fig.add_gridspec(2, 2, hspace=0.46, wspace=0.30, top=0.92, bottom=0.10, left=0.07, right=0.93)
        ax1 = fig.add_subplot(gs[0, 0])
        ax2 = fig.add_subplot(gs[0, 1])
        ax3 = fig.add_subplot(gs[1, 0])
        ax4 = fig.add_subplot(gs[1, 1])

        for ax in [ax1, ax2, ax3, ax4]:
            self.canvas_electro.apply_studio_theme(ax)

        # 1. Discharge Stage Decomposition (V vs Ah)
        ax1.plot(df["Capacity_Ah"], df["Voltage"], color="#0284c7", linewidth=2.8, label="Discharge Curve")
        ohmic_cap = df["Capacity_Ah"].iloc[min(2, len(df)-1)]
        knee_indices = np.where(df["Voltage"] <= 3.5)[0]
        knee_cap = df["Capacity_Ah"].iloc[knee_indices[0]] if len(knee_indices) > 0 else df["Capacity_Ah"].iloc[-1]

        ax1.axvspan(0, ohmic_cap, color="#bae6fd", alpha=0.45, label="1. Ohmic Drop")
        ax1.axvspan(ohmic_cap, knee_cap, color="#bbf7d0", alpha=0.45, label="2. Working Plateau")
        ax1.axvspan(knee_cap, df["Capacity_Ah"].iloc[-1], color="#fecdd3", alpha=0.45, label="3. Knee / Depletion")
        ax1.set_title("Discharge Stage Decomposition (V vs Ah)")
        ax1.set_xlabel("Delivered Capacity (Ah)")
        ax1.set_ylabel("Voltage (V)")
        ax1.legend(loc="upper right", facecolor="#ffffff", edgecolor="#000000", labelcolor="#000000", fontsize=8)

        # 2. State of Charge (SoC %) vs Voltage (OCV-SoC curve)
        ax2.plot(df["Voltage"], df["SoC_pct"], color="#7c3aed", linewidth=2.6)
        ax2.set_title("State of Charge (SoC %) vs Voltage")
        ax2.set_xlabel("Terminal Voltage (V)")
        ax2.set_ylabel("Estimated SoC (%)")

        # 3. Voltage Sag Rate (dV/dt) vs Time
        ax3.plot(df["Time"], np.abs(df["dV_dt_mV_s"]), color="#e11d48", linewidth=2.4, label="|dV/dt|")
        ax3.set_title("Voltage Decay Velocity |dV/dt| (mV/s)")
        ax3.set_xlabel("Time (s)")
        ax3.set_ylabel("Sag Rate (mV/s)")
        ax3.legend(loc="upper right", facecolor="#ffffff", edgecolor="#000000", labelcolor="#000000", fontsize=8)

        # 4. Instantaneous Power vs Voltage
        ax4.plot(df["Voltage"], df["Power"], color="#d97706", linewidth=2.4)
        ax4.set_title("Power vs Terminal Voltage Profile")
        ax4.set_xlabel("Terminal Voltage (V)")
        ax4.set_ylabel("Power Output (W)")

        self.canvas_electro.draw()

    # --------------------------------------------------------------------------
    # PAGE 2: CELL SIMULATOR & PLAYBACK
    # --------------------------------------------------------------------------
    def _build_page_simulation(self) -> QWidget:
        page = QWidget()
        h_layout = QHBoxLayout(page)
        h_layout.setContentsMargins(4, 4, 10, 10)
        h_layout.setSpacing(16)

        # Left panel: Visual Battery Widget & Dynamic Gauge Box
        left_panel = QFrame()
        left_panel.setObjectName("SimCard")
        apply_brutalist_shadow(left_panel, offset=6)
        left_panel.setFixedWidth(310)
        lp_lay = QVBoxLayout(left_panel)
        lp_lay.setContentsMargins(14, 14, 14, 14)
        lp_lay.setSpacing(10)

        lp_title = QLabel("PHYSICAL CELL TELEMETRY")
        lp_title.setObjectName("HeroTitle")
        lp_lay.addWidget(lp_title)

        # The Battery Graphic
        self.battery_widget = BatteryCell3DWidget()
        lp_lay.addWidget(self.battery_widget, alignment=Qt.AlignCenter)

        # Live HUD Metric Grid (Hard shadow 4px)
        grid_frame = QFrame()
        grid_frame.setObjectName("HudFrame")
        apply_brutalist_shadow(grid_frame, offset=4)
        grid_lay = QVBoxLayout(grid_frame)
        grid_lay.setContentsMargins(12, 10, 12, 10)
        grid_lay.setSpacing(7)

        def make_hud_row(label: str, attr_name: str):
            row = QHBoxLayout()
            l = QLabel(label)
            l.setStyleSheet("color: #000000; font-size: 11px; font-weight: 800;")
            v = QLabel("--")
            v.setStyleSheet("color: #000000; font-weight: 900; font-size: 13px; background: #ffe600; border: 1.5px solid #000000; padding: 2px 6px; border-radius: 4px;")
            setattr(self, attr_name, v)
            row.addWidget(l)
            row.addStretch(1)
            row.addWidget(v)
            return row

        grid_lay.addLayout(make_hud_row("Timestamp:", "hud_time"))
        grid_lay.addLayout(make_hud_row("Terminal Voltage:", "hud_volt"))
        grid_lay.addLayout(make_hud_row("Discharge Current:", "hud_curr"))
        grid_lay.addLayout(make_hud_row("Output Power:", "hud_pow"))
        grid_lay.addLayout(make_hud_row("Capacity Delivered:", "hud_cap"))
        grid_lay.addLayout(make_hud_row("Energy Delivered:", "hud_energy"))
        grid_lay.addLayout(make_hud_row("Dynamic Sag Rate:", "hud_sag"))

        lp_lay.addWidget(grid_frame)
        lp_lay.addStretch(1)
        h_layout.addWidget(left_panel)

        # Right panel: Dynamic Chart + Scrub/Play controls
        right_panel = QFrame()
        right_panel.setObjectName("PanelCard")
        apply_brutalist_shadow(right_panel, offset=6)
        rp_lay = QVBoxLayout(right_panel)
        rp_lay.setContentsMargins(12, 12, 12, 12)
        rp_lay.setSpacing(10)

        self.canvas_sim = StudioMplCanvas(right_panel, width=7, height=4)
        apply_brutalist_shadow(self.canvas_sim, offset=5)
        rp_lay.addWidget(self.canvas_sim, stretch=1)

        # Control Bar
        ctrl_box = QFrame()
        ctrl_box.setObjectName("HudFrame")
        apply_brutalist_shadow(ctrl_box, offset=4)
        ctrl_lay = QVBoxLayout(ctrl_box)
        ctrl_lay.setContentsMargins(12, 10, 12, 10)
        ctrl_lay.setSpacing(8)

        # Slider row
        slider_row = QHBoxLayout()
        self.lbl_sim_time_now = QLabel("0.0 s")
        self.lbl_sim_time_now.setStyleSheet("color: #000000; background: #ffe600; border: 1.5px solid #000000; padding: 2px 8px; border-radius: 4px; font-weight: 900; font-size: 12px; min-width: 60px;")
        apply_brutalist_shadow(self.lbl_sim_time_now, offset=2)
        self.sim_slider = QSlider(Qt.Horizontal)
        self.sim_slider.setRange(0, 100)
        self.sim_slider.sliderMoved.connect(self._on_slider_moved)
        self.lbl_sim_time_end = QLabel("0.0 s")
        self.lbl_sim_time_end.setStyleSheet("color: #000000; font-size: 12px; font-weight: 800; min-width: 60px; text-align: right;")

        slider_row.addWidget(self.lbl_sim_time_now)
        slider_row.addWidget(self.sim_slider, stretch=1)
        slider_row.addWidget(self.lbl_sim_time_end)
        ctrl_lay.addLayout(slider_row)

        # Buttons row (Tactile Brutalist Buttons)
        btn_row = QHBoxLayout()
        self.btn_play = BrutalistButton("▶ Play", offset=4)
        self.btn_play.setFixedSize(95, 36)
        self.btn_play.setStyleSheet("background-color: #00f076; color: #000000; border: 2.5px solid #000000; font-weight: 900; border-radius: 6px; font-size: 13px;")
        self.btn_play.clicked.connect(self._toggle_playback)

        self.btn_rewind = BrutalistButton("⏮ Reset", offset=4)
        self.btn_rewind.setFixedSize(85, 36)
        self.btn_rewind.setStyleSheet("background-color: #ffffff; color: #000000; border: 2.5px solid #000000; border-radius: 6px; font-weight: 800; font-size: 12px;")
        self.btn_rewind.clicked.connect(self._rewind_playback)

        btn_row.addWidget(self.btn_play)
        btn_row.addWidget(self.btn_rewind)
        btn_row.addSpacing(16)

        lbl_spd = QLabel("Speed:")
        lbl_spd.setStyleSheet("color: #000000; font-weight: 800;")
        btn_row.addWidget(lbl_spd)
        self.combo_speed = QComboBox()
        self.combo_speed.addItems(["1x Real-Time", "2x Faster", "5x High Speed", "10x Ultra Speed"])
        apply_brutalist_shadow(self.combo_speed, offset=3)
        self.combo_speed.currentIndexChanged.connect(self._on_speed_changed)
        btn_row.addWidget(self.combo_speed)
        btn_row.addStretch(1)

        ctrl_lay.addLayout(btn_row)
        rp_lay.addWidget(ctrl_box)

        h_layout.addWidget(right_panel, stretch=1)
        return page

    def _render_page_simulation_static(self):
        if not self.dataset:
            return

        df = self.dataset.df
        fig = self.canvas_sim.fig
        fig.clear()

        self.sim_ax = fig.add_subplot(1, 1, 1)
        self.canvas_sim.apply_studio_theme(self.sim_ax)

        self.sim_ax.plot(df["Time"], df["Voltage"], color="#cbd5e1", linewidth=2.0, label="Discharge Path")
        self.sim_line_active, = self.sim_ax.plot([], [], color="#0284c7", linewidth=3.0, label="Elapsed")
        self.sim_marker, = self.sim_ax.plot([], [], marker="o", markersize=10, color="#ffe600",
                                            markeredgecolor="#000000", markeredgewidth=2.5)

        self.sim_ax.set_title("Interactive Dynamic Discharge Tracker")
        self.sim_ax.set_xlabel("Time (s)")
        self.sim_ax.set_ylabel("Voltage (V)")
        self.sim_ax.set_xlim(df["Time"].min() - 10, df["Time"].max() + 10)
        self.sim_ax.set_ylim(df["Voltage"].min() - 0.1, df["Voltage"].max() + 0.1)

        self.canvas_sim.draw()

    def _update_simulation_point(self, idx: int):
        if not self.dataset:
            return

        df = self.dataset.df
        n = len(df)
        idx = max(0, min(n - 1, idx))
        self.play_idx = idx

        row = df.iloc[idx]
        t = float(row["Time"])
        v = float(row["Voltage"])
        i = float(row["Current"])
        p = float(row["Power"])
        cap_mah = float(row["Capacity_mAh"])
        energy_wh = float(row["Energy_Wh"])
        soc = float(row["SoC_pct"])
        sag = abs(float(row["dV_dt_mV_s"]))

        # Update HUD labels
        self.hud_time.setText(f"{t:.1f} s")
        self.hud_volt.setText(f"{v:.3f} V")
        self.hud_curr.setText(f"{i:.3f} A")
        self.hud_pow.setText(f"{p:.3f} W")
        self.hud_cap.setText(f"{cap_mah:.1f} mAh")
        self.hud_energy.setText(f"{energy_wh:.3f} Wh")
        self.hud_sag.setText(f"{sag:.1f} mV/s")

        self.lbl_sim_time_now.setText(f"{t:.1f} s")
        self.sim_slider.blockSignals(True)
        self.sim_slider.setValue(idx)
        self.sim_slider.blockSignals(False)

        # Update Battery Cell
        self.battery_widget.set_values(soc, v)

        # Update Marker & Elapsed Line
        if hasattr(self, "sim_line_active"):
            times_elapsed = df["Time"].iloc[:idx + 1]
            volts_elapsed = df["Voltage"].iloc[:idx + 1]
            self.sim_line_active.set_data(times_elapsed, volts_elapsed)
            self.sim_marker.set_data([t], [v])
            self.canvas_sim.draw_idle()

    def _toggle_playback(self):
        if self.play_timer.isActive():
            self.play_timer.stop()
            self.btn_play.setText("▶ Play")
            self.btn_play.setStyleSheet("background-color: #00f076; color: #000000; border: 2.5px solid #000000; font-weight: 900; border-radius: 6px; font-size: 13px;")
        else:
            self.play_timer.start(100 // self.playback_speed)
            self.btn_play.setText("⏸ Pause")
            self.btn_play.setStyleSheet("background-color: #ff3366; color: #ffffff; border: 2.5px solid #000000; font-weight: 900; border-radius: 6px; font-size: 13px;")

    def _on_playback_tick(self):
        if not self.dataset:
            return
        n = len(self.dataset.df)
        if self.play_idx >= n - 1:
            self.play_timer.stop()
            self.btn_play.setText("▶ Play")
            self.btn_play.setStyleSheet("background-color: #00f076; color: #000000; border: 2.5px solid #000000; font-weight: 900; border-radius: 6px; font-size: 13px;")
            return
        self.play_idx += 1
        self._update_simulation_point(self.play_idx)

    def _rewind_playback(self):
        self.play_timer.stop()
        self.btn_play.setText("▶ Play")
        self.btn_play.setStyleSheet("background-color: #00f076; color: #000000; border: 2.5px solid #000000; font-weight: 900; border-radius: 6px; font-size: 13px;")
        self.play_idx = 0
        self._update_simulation_point(0)

    def _on_slider_moved(self, val: int):
        self._update_simulation_point(val)

    def _on_speed_changed(self, idx: int):
        speeds = [1, 2, 5, 10]
        self.playback_speed = speeds[idx] if idx < len(speeds) else 1
        if self.play_timer.isActive():
            self.play_timer.setInterval(max(10, 100 // self.playback_speed))

    # --------------------------------------------------------------------------
    # PAGE 3: TELEMETRY MATRIX (TABLE WITH 6PX HARD SHADOW)
    # --------------------------------------------------------------------------
    def _build_page_matrix(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(4, 4, 10, 10)
        layout.setSpacing(10)

        # Search Bar
        top_bar = QHBoxLayout()
        search_lbl = QLabel("Search Matrix:")
        search_lbl.setStyleSheet("color: #000000; font-size: 12px; font-weight: 900;")
        top_bar.addWidget(search_lbl)

        self.edit_filter = QLineEdit()
        self.edit_filter.setPlaceholderText("Filter points by typing value (e.g. 4.1 or 3.2)...")
        apply_brutalist_shadow(self.edit_filter, offset=3)
        self.edit_filter.textChanged.connect(self._filter_table)
        top_bar.addWidget(self.edit_filter, stretch=1)

        self.btn_export_csv = BrutalistButton("💾 Export Filtered CSV", offset=4)
        self.btn_export_csv.setStyleSheet("background-color: #a78bfa; color: #000000; border: 2.5px solid #000000; font-weight: 900; border-radius: 6px; padding: 7px 14px;")
        self.btn_export_csv.clicked.connect(self.on_export_table_csv)
        top_bar.addWidget(self.btn_export_csv)

        layout.addLayout(top_bar)

        self.table_widget = QTableWidget()
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.verticalHeader().setVisible(False)
        apply_brutalist_shadow(self.table_widget, offset=6)
        layout.addWidget(self.table_widget, stretch=1)

        self.lbl_stats = QLabel("Points: 0")
        self.lbl_stats.setStyleSheet("color: #000000; font-size: 11px; font-weight: 800; background: #ffffff; border: 1.5px solid #000000; padding: 4px 10px; border-radius: 4px;")
        apply_brutalist_shadow(self.lbl_stats, offset=3)
        layout.addWidget(self.lbl_stats)

        return page

    def _populate_table(self):
        if not self.dataset:
            return

        df = self.dataset.df
        cols = [
            ("Time", "Time (s)", "{:.0f}"),
            ("Voltage", "Voltage (V)", "{:.3f}"),
            ("Current", "Current (A)", "{:.3f}"),
            ("Power", "Power (W)", "{:.3f}"),
            ("Capacity_Ah", "Capacity (Ah)", "{:.4f}"),
            ("Capacity_mAh", "Capacity (mAh)", "{:.1f}"),
            ("Energy_Wh", "Energy (Wh)", "{:.4f}"),
            ("SoC_pct", "SoC (%)", "{:.1f}%"),
            ("dV_dt_mV_s", "Sag (mV/s)", "{:.2f}"),
            ("R_dc_mOhm", "R_dc (mΩ)", "{:.1f}")
        ]

        self.table_widget.setColumnCount(len(cols))
        self.table_widget.setHorizontalHeaderLabels([c[1] for c in cols])
        self.table_widget.setRowCount(len(df))

        for row_idx, row in df.iterrows():
            for col_idx, (key, _, fmt) in enumerate(cols):
                val = row[key]
                item = QTableWidgetItem(fmt.format(val))
                item.setTextAlignment(Qt.AlignCenter)
                self.table_widget.setItem(row_idx, col_idx, item)

        m = self.dataset.metrics
        self.lbl_stats.setText(
            f"Total Matrix Points: {m.data_points}  |  Sample Rate: {m.sample_rate_s:.1f}s  |  "
            f"Voltage: [{m.v_min:.2f}V - {m.v_max:.2f}V]  |  Current Mean: {m.i_mean:.2f}A  |  Power Mean: {m.p_mean:.2f}W"
        )

    def _filter_table(self, query: str):
        query = query.strip().lower()
        rows = self.table_widget.rowCount()
        cols = self.table_widget.columnCount()
        for r in range(rows):
            match = False
            if not query:
                match = True
            else:
                for c in range(cols):
                    item = self.table_widget.item(r, c)
                    if item and query in item.text().lower():
                        match = True
                        break
            self.table_widget.setRowHidden(r, not match)

    # --------------------------------------------------------------------------
    # PAGE 4: DIAGNOSTIC CERTIFICATE
    # --------------------------------------------------------------------------
    def _build_page_report(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(4, 4, 10, 10)
        layout.setSpacing(12)

        top_strip = QHBoxLayout()
        title_rep = QLabel("BATTERY PERFORMANCE AUDIT & HEALTH CERTIFICATE")
        title_rep.setStyleSheet("font-size: 13px; font-weight: 900; color: #000000; background: #ffe600; border: 2px solid #000000; padding: 5px 12px; border-radius: 6px;")
        apply_brutalist_shadow(title_rep, offset=3)
        top_strip.addWidget(title_rep)
        top_strip.addStretch(1)

        btn_copy = BrutalistButton("📋 Copy Certificate", offset=4)
        btn_copy.clicked.connect(self._copy_report_to_clipboard)
        top_strip.addWidget(btn_copy)

        btn_save_txt = BrutalistButton("📄 Save as TXT", offset=4)
        btn_save_txt.clicked.connect(self._save_report_txt)
        top_strip.addWidget(btn_save_txt)

        btn_open_html = BrutalistButton("🌐 View in Browser (HTML)", offset=4)
        btn_open_html.setObjectName("PrimaryGlowBtn")
        btn_open_html.clicked.connect(self.on_export_html)
        top_strip.addWidget(btn_open_html)

        layout.addLayout(top_strip)

        self.report_text = QLabel()
        self.report_text.setTextFormat(Qt.MarkdownText)
        self.report_text.setStyleSheet("""
            background-color: #ffffff;
            border: 2.5px solid #000000;
            border-radius: 8px;
            padding: 22px;
            color: #000000;
            font-size: 13px;
            line-height: 1.6;
        """)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        scroll.setWidget(self.report_text)
        apply_brutalist_shadow(scroll, offset=6)

        layout.addWidget(scroll, stretch=1)
        return page

    def _render_page_report(self):
        if not self.dataset:
            return

        m = self.dataset.metrics
        name = self.dataset.source_name

        report_md = f"""# 🔋 VOLTIX PRO Performance Audit
**Dataset Source:** `{name}`  
**Audit Timestamp:** `{time.strftime('%Y-%m-%d %H:%M:%S')}`  
**Diagnostic Grade:** **<span style="color: #000000; background: #ffe600; border: 1.5px solid #000000; padding: 2px 8px; border-radius: 4px;">{m.cell_grade}</span>**  
**Executive Summary:** {m.cell_status_summary}

---

### ⚡ 1. Primary Electrical & Energy Telemetry
| Parameter | Value | Standard Unit | Notes |
| :--- | :--- | :--- | :--- |
| **Initial Voltage (V_init)** | `{m.v_initial:.3f}` | V | Initial resting / start voltage |
| **Final / Cutoff Voltage (V_final)** | `{m.v_final:.3f}` | V | Safe limit cutoff: `{m.v_cutoff:.2f}V` |
| **Total Voltage Sag (&Delta;V)** | `{m.v_drop:.3f}` | V | Overall voltage potential decrease |
| **Thermodynamic Mean Voltage (V_avg)** | `{m.v_avg_discharge:.3f}` | V | Calculated via `Energy / Capacity` |
| **Delivered Capacity (High-Precision)** | `{m.capacity_ah:.4f}` | Ah | **`{m.capacity_mah:.1f} mAh`** |
| **Delivered Energy (High-Precision)** | `{m.energy_wh:.4f}` | Wh | **`{m.energy_mwh:.1f} mWh`** |
| **Delivered Capacity (Rectangular)** | `{m.capacity_rect_ah:.4f}` | Ah | Baseline comparison |
| **Delivered Energy (Rectangular)** | `{m.energy_rect_wh:.4f}` | Wh | Baseline comparison |

---

### 📈 2. Current, Power & Dynamic Load Analysis
| Metric | Continuous Mean | Transient Peak | Unit |
| :--- | :--- | :--- | :--- |
| **Discharge Current** | `{m.i_mean:.3f} A` | `{m.i_max:.3f} A` | Peak C-rate: `{m.c_rate_max:.2f}C` |
| **Output Electrical Power** | `{m.p_mean:.3f} W` | `{m.p_max:.3f} W` | Peak dissipation load |
| **RMS Equivalent Current** | `{m.i_rms:.3f} A` | - | Thermal stress indicator |

---

### 🔬 3. Electrochemical Health & Diagnostics
* **State of Health (SoH %):** **`{m.soh_pct:.2f}%`** (measured relative to rated `{m.nominal_capacity_ah:.2f} Ah`).
* **Estimated DC Internal Resistance (R_dc):**
  * Median Impedance: **`{m.rdc_median_mohm:.1f} m&Omega;`**
  * End-of-Discharge Impedance: **`{m.rdc_final_mohm:.1f} m&Omega;`**
* **Discharge Phase Breakdown:**
  * **Initial Ohmic Drop:** `~{m.ohmic_drop_v:.3f} V`
  * **Stable Working Plateau:** Mean `{m.plateau_v_mean:.3f} V` over `{m.plateau_duration_s:.0f} seconds`
  * **Knee Depletion Point:** `{m.knee_voltage:.2f} V` at `{m.knee_time_s:.0f} seconds`
  * **Peak Voltage Sag Rate:** `{m.max_sag_rate_mv_s:.2f} mV/s`

---

### ⚠️ 4. Safety & Compliance Assessment
{"* **Alarms / Flags:**" if m.warnings else "* **All safety metrics passed without anomalies.**"}
{"".join([f"  * ⚠️ {w}\\n" for w in m.warnings])}
"""
        self.report_text.setText(report_md)

    def _copy_report_to_clipboard(self):
        text = self.report_text.text()
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Copied", "Audit report copied to clipboard!")

    def _save_report_txt(self):
        if not self.dataset:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Audit Report", "battery_audit_report.txt", "Text Files (*.txt)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.report_text.text())
            QMessageBox.information(self, "Saved", f"Report saved successfully to {os.path.basename(path)}")

    # --------------------------------------------------------------------------
    # DATASET LOADING & RECALCULATION
    # --------------------------------------------------------------------------
    def load_dataset(self, file_path: str):
        try:
            nom_cap = self.spin_capacity.value()
            cutoff = self.spin_cutoff.value()
            self.dataset = load_and_analyze(file_path, nominal_capacity_ah=nom_cap, cutoff_voltage=cutoff)
            self._update_all_views()
            self.lbl_dataset.setText(f"📁 {os.path.basename(file_path)}")
            self.lbl_points_badge.setText(f"{self.dataset.metrics.data_points} points • {self.dataset.metrics.sample_rate_s:.1f}s rate")
            self.status_bar_label.setText(f"● Loaded '{os.path.basename(file_path)}' • {self.dataset.metrics.data_points} points analyzed.")
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load dataset:\n{str(e)}")

    def _recalc_with_params(self):
        if not self.dataset:
            return
        self.dataset.nominal_capacity_ah = self.spin_capacity.value()
        self.dataset.cutoff_voltage = self.spin_cutoff.value()
        self.dataset.process_data()
        self._update_all_views()

    def _on_chem_changed(self, idx: int):
        presets = [
            (2.0, 3.20),  # Li-ion NMC
            (2.0, 2.50),  # LFP
            (1.5, 1.80),  # LTO
            (1.9, 1.00),  # NiMH
            (self.spin_capacity.value(), self.spin_cutoff.value())  # Custom
        ]
        cap, cut = presets[idx]
        self.spin_capacity.blockSignals(True)
        self.spin_cutoff.blockSignals(True)
        self.spin_capacity.setValue(cap)
        self.spin_cutoff.setValue(cut)
        self.spin_capacity.blockSignals(False)
        self.spin_cutoff.blockSignals(False)
        self._recalc_with_params()

    def _update_all_views(self):
        if not self.dataset:
            return

        m = self.dataset.metrics

        # 1. Update Hero Cards
        self.kpi_v_val.setText(f"{m.v_initial:.2f}V → {m.v_final:.2f}V")
        self.kpi_v_sub.setText(f"Drop: Δ{m.v_drop:.2f}V  |  Avg: {m.v_avg_discharge:.3f}V")

        self.kpi_cap_val.setText(f"{m.capacity_ah:.4f} Ah")
        self.kpi_cap_sub.setText(f"{m.capacity_mah:.1f} mAh  |  {m.soh_pct:.1f}% of {m.nominal_capacity_ah:.1f}Ah")

        self.kpi_wh_val.setText(f"{m.energy_wh:.4f} Wh")
        self.kpi_wh_sub.setText(f"{m.energy_mwh:.1f} mWh  |  Plateau: {m.plateau_duration_s:.0f}s")

        self.kpi_ip_val.setText(f"{m.i_mean:.2f}A / {m.p_mean:.2f}W")
        self.kpi_ip_sub.setText(f"Peak I: {m.i_max:.2f}A ({m.c_rate_max:.2f}C) | Peak P: {m.p_max:.2f}W")

        self.kpi_health_val.setText(f"{m.cell_grade}")
        self.kpi_health_sub.setText(f"Median IR: {m.rdc_median_mohm:.0f} mΩ | Final: {m.rdc_final_mohm:.0f} mΩ")

        # 2. Render Plots
        self._render_page_cockpit()
        self._render_page_electrochemistry()

        # 3. Setup Simulation Slider & Canvas
        n = len(self.dataset.df)
        self.sim_slider.setRange(0, n - 1)
        self.lbl_sim_time_end.setText(f"{m.duration_s:.1f} s")
        self._render_page_simulation_static()
        self._update_simulation_point(0)

        # 4. Populate Matrix Table
        self._populate_table()

        # 5. Render Report
        self._render_page_report()

    # --------------------------------------------------------------------------
    # ACTIONS: OPEN FILE, EXPORT HTML, SAVE SNAPSHOTS
    # --------------------------------------------------------------------------
    def on_open_file_dialog(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Battery CSV Data", "", "CSV Files (*.csv);;All Files (*)")
        if path:
            self.load_dataset(path)

    def on_export_html(self):
        if not self.dataset:
            QMessageBox.warning(self, "No Data", "Please load a battery dataset first.")
            return

        out_path = os.path.abspath("battery_report.html")
        export_html_report(self.dataset, out_path)

        res = QMessageBox.question(
            self, "Report Exported",
            f"Interactive HTML Report generated successfully at:\n{out_path}\n\nWould you like to open it in your web browser now?",
            QMessageBox.Yes | QMessageBox.No
        )
        if res == QMessageBox.Yes:
            webbrowser.open(f"file:///{out_path.replace(os.sep, '/')}")

    def on_save_charts(self):
        if not self.dataset:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Dashboard Snapshot", "battery_cockpit.png", "PNG Image (*.png);;PDF (*.pdf)")
        if path:
            self.canvas_cockpit.fig.savefig(path, dpi=300, facecolor=self.canvas_cockpit.fig.get_facecolor(), bbox_inches="tight")
            QMessageBox.information(self, "Saved", f"Cockpit snapshot saved to:\n{path}")

    def on_export_table_csv(self):
        if not self.dataset:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Computed Telemetry", "battery_telemetry_matrix.csv", "CSV Files (*.csv)")
        if path:
            self.dataset.df.to_csv(path, index=False)
            QMessageBox.information(self, "Saved", f"Full telemetry matrix exported to:\n{path}")


# ==============================================================================
# MAIN LAUNCHER
# ==============================================================================
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Voltix Pro Neo-Brutalist Battery Analyzer")
    parser.add_argument("file", nargs="?", default="Battery_data.csv", help="CSV dataset file path")
    parser.add_argument("--cli", action="store_true", help="Run in terminal CLI mode without GUI")
    parser.add_argument("--html", action="store_true", help="Generate interactive HTML report directly")
    parser.add_argument("--capacity", type=float, default=2.0, help="Rated nominal capacity in Ah (default: 2.0)")
    parser.add_argument("--cutoff", type=float, default=3.2, help="Cutoff voltage in V (default: 3.2)")

    args, _ = parser.parse_known_args()

    if args.html:
        battery = load_and_analyze(args.file, nominal_capacity_ah=args.capacity, cutoff_voltage=args.cutoff)
        out = export_html_report(battery, "battery_report.html")
        print(f"Generated interactive HTML report at: {os.path.abspath(out)}")
        return

    if args.cli:
        if sys.platform == "win32":
            try:
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass
        battery = load_and_analyze(args.file, nominal_capacity_ah=args.capacity, cutoff_voltage=args.cutoff)
        m = battery.metrics
        print("=" * 60)
        print("      [VOLTIX PRO] - BATTERY PERFORMANCE AUDIT")
        print("=" * 60)
        print(f"File: {args.file} | Grade: {m.cell_grade}")
        print(f"Voltage: {m.v_initial:.3f}V -> {m.v_final:.3f}V (Drop: {m.v_drop:.3f}V)")
        print(f"Delivered Capacity: {m.capacity_ah:.4f} Ah ({m.capacity_mah:.1f} mAh)")
        print(f"Delivered Energy: {m.energy_wh:.4f} Wh ({m.energy_mwh:.1f} mWh)")
        print(f"Average Current: {m.i_mean:.3f} A | Peak Current: {m.i_max:.3f} A")
        print(f"Average Power: {m.p_mean:.3f} W | Peak Power: {m.p_max:.3f} W")
        print(f"Thermodynamic Mean V: {m.v_avg_discharge:.3f} V")
        print(f"Median DC IR: {m.rdc_median_mohm:.1f} mOhm")
        print("=" * 60)
        return

    # Enable High DPI scaling and launch Neo-Brutalist GUI
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setStyleSheet(NEOBRUTALISM_QSS)

    csv_to_open = args.file if os.path.exists(args.file) else ("battery_data.csv" if os.path.exists("battery_data.csv") else args.file)
    win = ModernBatteryAnalyzer(initial_csv=csv_to_open)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
