"""
VOLTIX PRO // Modern Battery Analyzer & Electrochemical Telemetry Suite
State-of-the-art Python desktop application with PySide6 and Matplotlib.
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
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QSlider, QProgressBar, QFrame, QSplitter, QMessageBox,
    QScrollArea, QLineEdit, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QFont, QColor, QPalette, QIcon, QPainter, QBrush, QPen, QLinearGradient, QPixmap

import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import AutoMinorLocator

from battery_engine import BatteryDataset, load_and_analyze, export_html_report, BatteryMetrics


# ==============================================================================
# MODERN DARK CYBER-ENGINEERING STYLESHEET
# ==============================================================================
MODERN_QSS = """
QMainWindow, QWidget#MainRoot {
    background-color: #0b0f17;
    color: #f8fafc;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
}

QFrame#HeaderCard, QFrame#KpiCard, QFrame#PanelCard, QFrame#SimCard {
    background-color: #141b2d;
    border: 1px solid #23304a;
    border-radius: 10px;
}

QFrame#KpiCard:hover {
    border: 1px solid #3b82f6;
    background-color: #182239;
}

/* Headings & Text */
QLabel {
    color: #f8fafc;
}
QLabel#MutedLabel {
    color: #94a3b8;
    font-size: 11px;
}
QLabel#KpiTitle {
    color: #94a3b8;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
QLabel#KpiValue {
    color: #f8fafc;
    font-size: 22px;
    font-weight: 700;
}
QLabel#KpiSub {
    color: #64748b;
    font-size: 11px;
}

/* Buttons */
QPushButton {
    background-color: #1e293b;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 7px 14px;
    font-weight: 600;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #2b3952;
    border: 1px solid #00e5ff;
    color: #00e5ff;
}
QPushButton:pressed {
    background-color: #0f172a;
}
QPushButton#PrimaryBtn {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #00e5ff);
    color: #ffffff;
    border: none;
    font-weight: 700;
}
QPushButton#PrimaryBtn:hover {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0369a1, stop:1 #38bdf8);
    color: #ffffff;
}
QPushButton#AccentBtn {
    background-color: #1e1b4b;
    color: #a5b4fc;
    border: 1px solid #4f46e5;
}
QPushButton#AccentBtn:hover {
    background-color: #312e81;
    color: #c7d2fe;
}
QFrame#HudFrame {
    background-color: #0d131f;
    border: 1px solid #1e293b;
    border-radius: 8px;
}
QFrame#HudFrame QLabel {
    border: none;
    background: transparent;
}

/* Inputs & Spinners */
QComboBox, QDoubleSpinBox, QLineEdit {
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 5px 10px;
    color: #f8fafc;
    font-size: 12px;
}
QComboBox:focus, QDoubleSpinBox:focus, QLineEdit:focus {
    border: 1px solid #00e5ff;
}
QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}
QComboBox QAbstractItemView {
    background-color: #141b2d;
    border: 1px solid #334155;
    color: #f8fafc;
    selection-background-color: #1e293b;
    selection-color: #00e5ff;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #23304a;
    background-color: #0e1422;
    border-radius: 8px;
    top: -1px;
}
QTabBar::tab {
    background-color: #141b2d;
    color: #94a3b8;
    border: 1px solid #23304a;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 18px;
    margin-right: 4px;
    font-weight: 600;
    font-size: 12px;
}
QTabBar::tab:selected {
    background-color: #0e1422;
    color: #00e5ff;
    border-top: 2px solid #00e5ff;
    border-bottom: 1px solid #0e1422;
}
QTabBar::tab:hover:!selected {
    background-color: #1c263e;
    color: #f8fafc;
}

/* Table Widget */
QTableWidget {
    background-color: #101626;
    border: 1px solid #23304a;
    border-radius: 8px;
    gridline-color: #1e293b;
    color: #f8fafc;
    font-size: 12px;
}
QHeaderView::section {
    background-color: #141b2d;
    color: #94a3b8;
    padding: 6px 8px;
    border: 1px solid #23304a;
    font-weight: 600;
}
QTableWidget::item:selected {
    background-color: rgba(0, 229, 255, 0.15);
    color: #00e5ff;
}

/* ScrollBars */
QScrollBar:vertical {
    background: #0b0f17;
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #334155;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #475569;
}
QScrollBar:horizontal {
    background: #0b0f17;
    height: 8px;
    margin: 0px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #334155;
    min-width: 20px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal:hover {
    background: #475569;
}
QScrollBar::add-line, QScrollBar::sub-line {
    background: none;
    border: none;
}

/* Slider */
QSlider::groove:horizontal {
    border: 1px solid #334155;
    height: 6px;
    background: #141b2d;
    border-radius: 3px;
}
QSlider::sub-page:horizontal {
    background: #00e5ff;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #f8fafc;
    border: 1px solid #00e5ff;
    width: 14px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 7px;
}
QSlider::handle:horizontal:hover {
    background: #00e5ff;
}

/* Progress Bar */
QProgressBar {
    border: 1px solid #334155;
    border-radius: 6px;
    text-align: center;
    background-color: #0f172a;
    color: #f8fafc;
    font-weight: 600;
}
QProgressBar::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #00e5ff);
    border-radius: 5px;
}
"""


# ==============================================================================
# CUSTOM MATPLOTLIB CANVAS WITH HIGH-TECH DARK THEME
# ==============================================================================
class DarkMplCanvas(FigureCanvas):
    """Reusable Matplotlib canvas with cyber dark engineering styling."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor="#0e1422")
        super().__init__(self.fig)
        self.setParent(parent)
        self.setStyleSheet("background-color: #0e1422; border-radius: 8px;")

    def apply_dark_theme(self, ax):
        """Applies consistent dark theme to an axis."""
        ax.set_facecolor("#121929")
        ax.tick_params(colors="#94a3b8", labelsize=9, which="both")
        ax.xaxis.label.set_color("#cbd5e1")
        ax.yaxis.label.set_color("#cbd5e1")
        ax.title.set_color("#f8fafc")
        ax.title.set_fontsize(11)
        ax.title.set_fontweight("bold")
        for spine in ax.spines.values():
            spine.set_color("#23304a")
            spine.set_linewidth(1.0)
        ax.grid(True, linestyle="--", alpha=0.3, color="#334155")


# ==============================================================================
# BATTERY VISUAL GAUGE (CUSTOM WIDGET)
# ==============================================================================
class BatteryLevelWidget(QWidget):
    """Modern graphic showing a physical battery cell draining dynamically."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.soc_pct = 100.0
        self.voltage = 4.20
        self.setFixedSize(150, 160)

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
        cap_w = 32
        cap_h = 7
        cap_x = (w - cap_w) // 2
        cap_y = 6
        painter.setBrush(QBrush(QColor("#64748b")))
        painter.setPen(QPen(QColor("#94a3b8"), 1))
        painter.drawRoundedRect(cap_x, cap_y, cap_w, cap_h, 3, 3)

        # Outer battery cylinder
        body_x = 24
        body_y = 14
        body_w = w - 48
        body_h = h - 42
        painter.setBrush(QBrush(QColor("#0b0f19")))
        painter.setPen(QPen(QColor("#334155"), 2))
        painter.drawRoundedRect(body_x, body_y, body_w, body_h, 10, 10)

        # Fluid Level
        fill_margin = 5
        max_fill_h = body_h - (fill_margin * 2)
        fill_h = int(max_fill_h * (self.soc_pct / 100.0))
        fill_y = body_y + body_h - fill_margin - fill_h
        fill_x = body_x + fill_margin
        fill_w = body_w - (fill_margin * 2)

        if fill_h > 2:
            if self.soc_pct > 50:
                col_top = QColor("#00e5ff")
                col_bot = QColor("#10b981")
            elif self.soc_pct > 20:
                col_top = QColor("#fbbf24")
                col_bot = QColor("#f59e0b")
            else:
                col_top = QColor("#f87171")
                col_bot = QColor("#ef4444")

            grad = QLinearGradient(fill_x, fill_y, fill_x, fill_y + fill_h)
            grad.setColorAt(0.0, col_top)
            grad.setColorAt(1.0, col_bot)

            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(fill_x, fill_y, fill_w, fill_h, 6, 6)

        # Text inside battery
        painter.setPen(QColor("#f8fafc"))
        font_pct = QFont("Segoe UI", 14, QFont.Bold)
        painter.setFont(font_pct)
        painter.drawText(body_x, body_y + (body_h // 2) - 12, body_w, 24, Qt.AlignCenter, f"{self.soc_pct:.1f}%")

        font_v = QFont("Segoe UI", 10, QFont.Normal)
        painter.setFont(font_v)
        painter.setPen(QColor("#94a3b8"))
        painter.drawText(body_x, body_y + (body_h // 2) + 10, body_w, 18, Qt.AlignCenter, f"{self.voltage:.2f} V")

        font_sub = QFont("Segoe UI", 9, QFont.Bold)
        painter.setFont(font_sub)
        painter.setPen(QColor("#38bdf8"))
        painter.drawText(0, h - 20, w, 18, Qt.AlignCenter, "ESTIMATED SOC")


# ==============================================================================
# MAIN APPLICATION WINDOW
# ==============================================================================
class ModernBatteryAnalyzer(QMainWindow):
    """Flagship modern battery analyzer application with multi-tab telemetry analysis."""

    def __init__(self, initial_csv: str = "Battery_data.csv"):
        super().__init__()
        self.setWindowTitle("VOLTIX PRO // Modern Battery Analyzer & Electrochemical Telemetry Suite")
        self.resize(1340, 890)
        self.setMinimumSize(1080, 720)

        self.initial_csv = initial_csv
        self.dataset: Optional[BatteryDataset] = None

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
            # Check lowercase
            alt = self.initial_csv.lower()
            if os.path.exists(alt):
                self.load_dataset(alt)

    def _init_ui(self):
        """Construct the UI hierarchy."""
        root = QWidget()
        root.setObjectName("MainRoot")
        self.setCentralWidget(root)

        main_layout = QVBoxLayout(root)
        main_layout.setContentsMargins(16, 14, 16, 14)
        main_layout.setSpacing(12)

        # 1. Top Header Bar
        header = self._build_header()
        main_layout.addWidget(header)

        # 2. KPI Cards Row
        kpi_row = self._build_kpi_row()
        main_layout.addWidget(kpi_row)

        # 3. Main Work Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_tab_dashboard(), "📊 Telemetry Dashboard")
        self.tabs.addTab(self._build_tab_electrochemistry(), "⚡ Electrochemical Curves")
        self.tabs.addTab(self._build_tab_simulation(), "🕹️ Dynamic Simulation")
        self.tabs.addTab(self._build_tab_inspector(), "📋 Data Inspector & Table")
        self.tabs.addTab(self._build_tab_report(), "📑 Diagnostic Report")
        main_layout.addWidget(self.tabs, stretch=1)

        # 4. Status Bar
        self.status_bar_label = QLabel("Ready • No active alarms")
        self.status_bar_label.setStyleSheet("color: #64748b; font-size: 11px; padding: 2px 4px;")
        main_layout.addWidget(self.status_bar_label)

    # --------------------------------------------------------------------------
    # HEADER SECTION
    # --------------------------------------------------------------------------
    def _build_header(self) -> QWidget:
        card = QFrame()
        card.setObjectName("HeaderCard")
        h_layout = QHBoxLayout(card)
        h_layout.setContentsMargins(16, 10, 16, 10)
        h_layout.setSpacing(16)

        # Title block
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title_lbl = QLabel("⚡ VOLTIX PRO")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: 800; color: #00e5ff; letter-spacing: 0.5px;")
        sub_lbl = QLabel("High-Precision Battery Performance & Electrochemical Diagnostic Suite")
        sub_lbl.setStyleSheet("font-size: 11px; color: #94a3b8;")
        sub_lbl.setMinimumWidth(440)
        title_box.addWidget(title_lbl)
        title_box.addWidget(sub_lbl)
        h_layout.addLayout(title_box)

        h_layout.addStretch(1)

        # Controls: Dataset pill
        self.lbl_dataset = QLabel("📁 No CSV Loaded")
        self.lbl_dataset.setStyleSheet("background: #0f172a; border: 1px solid #334155; padding: 6px 12px; border-radius: 6px; font-weight: 600; color: #38bdf8; font-size: 12px;")
        h_layout.addWidget(self.lbl_dataset)

        # Chemistry selector
        chem_box = QVBoxLayout()
        chem_box.setSpacing(1)
        chem_lbl = QLabel("Chemistry:")
        chem_lbl.setObjectName("MutedLabel")
        self.combo_chem = QComboBox()
        self.combo_chem.addItems([
            "Li-ion NMC/LCO (4.2V)",
            "LiFePO4 / LFP (3.65V)",
            "LTO / Titanate (2.8V)",
            "NiMH (1.45V)",
            "Custom"
        ])
        self.combo_chem.currentIndexChanged.connect(self._on_chem_changed)
        chem_box.addWidget(chem_lbl)
        chem_box.addWidget(self.combo_chem)
        h_layout.addLayout(chem_box)

        # Rated Capacity
        cap_box = QVBoxLayout()
        cap_box.setSpacing(1)
        cap_lbl = QLabel("Nominal Rating:")
        cap_lbl.setObjectName("MutedLabel")
        self.spin_capacity = QDoubleSpinBox()
        self.spin_capacity.setRange(0.05, 500.0)
        self.spin_capacity.setValue(2.00)
        self.spin_capacity.setSingleStep(0.1)
        self.spin_capacity.setSuffix(" Ah")
        self.spin_capacity.valueChanged.connect(self._recalc_with_params)
        cap_box.addWidget(cap_lbl)
        cap_box.addWidget(self.spin_capacity)
        h_layout.addLayout(cap_box)

        # Cutoff Voltage
        cut_box = QVBoxLayout()
        cut_box.setSpacing(1)
        cut_lbl = QLabel("Cutoff V:")
        cut_lbl.setObjectName("MutedLabel")
        self.spin_cutoff = QDoubleSpinBox()
        self.spin_cutoff.setRange(0.5, 100.0)
        self.spin_cutoff.setValue(3.20)
        self.spin_cutoff.setSingleStep(0.05)
        self.spin_cutoff.setSuffix(" V")
        self.spin_cutoff.valueChanged.connect(self._recalc_with_params)
        cut_box.addWidget(cut_lbl)
        cut_box.addWidget(self.spin_cutoff)
        h_layout.addLayout(cut_box)

        # Action Buttons
        self.btn_load = QPushButton("📂 Load CSV")
        self.btn_load.setObjectName("PrimaryBtn")
        self.btn_load.clicked.connect(self.on_open_file_dialog)
        h_layout.addWidget(self.btn_load)

        self.btn_html = QPushButton("🌐 HTML Report")
        self.btn_html.setObjectName("AccentBtn")
        self.btn_html.clicked.connect(self.on_export_html)
        h_layout.addWidget(self.btn_html)

        self.btn_snapshot = QPushButton("📸 Snap Charts")
        self.btn_snapshot.clicked.connect(self.on_save_charts)
        h_layout.addWidget(self.btn_snapshot)

        return card

    # --------------------------------------------------------------------------
    # KPI METRIC CARDS ROW
    # --------------------------------------------------------------------------
    def _build_kpi_row(self) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Helper to create styled card
        def make_card(title: str, val_id: str, sub_id: str, accent_color: str):
            c = QFrame()
            c.setObjectName("KpiCard")
            c_lay = QVBoxLayout(c)
            c_lay.setContentsMargins(14, 12, 14, 12)
            c_lay.setSpacing(4)

            top_bar = QFrame()
            top_bar.setFixedHeight(3)
            top_bar.setStyleSheet(f"background-color: {accent_color}; border-radius: 1px;")
            c_lay.addWidget(top_bar)

            lbl_title = QLabel(title)
            lbl_title.setObjectName("KpiTitle")
            c_lay.addWidget(lbl_title)

            lbl_val = QLabel("--")
            lbl_val.setObjectName("KpiValue")
            setattr(self, val_id, lbl_val)
            c_lay.addWidget(lbl_val)

            lbl_sub = QLabel("--")
            lbl_sub.setObjectName("KpiSub")
            setattr(self, sub_id, lbl_sub)
            c_lay.addWidget(lbl_sub)

            return c

        layout.addWidget(make_card("Terminal Voltage", "kpi_v_val", "kpi_v_sub", "#00e5ff"))
        layout.addWidget(make_card("Delivered Capacity", "kpi_cap_val", "kpi_cap_sub", "#10b981"))
        layout.addWidget(make_card("Delivered Energy", "kpi_wh_val", "kpi_wh_sub", "#facc15"))
        layout.addWidget(make_card("Current & Power", "kpi_ip_val", "kpi_ip_sub", "#fb923c"))
        layout.addWidget(make_card("Cell Health & Grade", "kpi_health_val", "kpi_health_sub", "#a855f7"))

        return container

    # --------------------------------------------------------------------------
    # TAB 1: TELEMETRY DASHBOARD (4 Synchronized Visualizations)
    # --------------------------------------------------------------------------
    def _build_tab_dashboard(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)

        self.canvas_dash = DarkMplCanvas(widget, width=10, height=6)
        layout.addWidget(self.canvas_dash)
        return widget

    def _render_tab_dashboard(self):
        if not self.dataset:
            return

        df = self.dataset.df
        m = self.dataset.metrics
        fig = self.canvas_dash.fig
        fig.clear()

        # 2x2 Grid of subplots
        gs = fig.add_gridspec(2, 2, hspace=0.46, wspace=0.30, top=0.92, bottom=0.10, left=0.07, right=0.93)
        ax1 = fig.add_subplot(gs[0, 0])
        ax2 = fig.add_subplot(gs[0, 1])
        ax3 = fig.add_subplot(gs[1, 0])
        ax4 = fig.add_subplot(gs[1, 1])

        for ax in [ax1, ax2, ax3, ax4]:
            self.canvas_dash.apply_dark_theme(ax)

        # 1. Voltage vs Time
        ax1.plot(df["Time"], df["Voltage"], color="#00e5ff", linewidth=2.2, label="Voltage (V)")
        ax1.axhline(m.v_cutoff, color="#ef4444", linestyle="--", alpha=0.8, label=f"Cutoff ({m.v_cutoff:.2f}V)")
        ax1.axhline(m.plateau_v_mean, color="#10b981", linestyle=":", alpha=0.6, label=f"Plateau Mean ({m.plateau_v_mean:.2f}V)")
        ax1.fill_between(df["Time"], df["Voltage"], m.v_cutoff, color="#00e5ff", alpha=0.08)
        ax1.set_title("Voltage vs Time (Discharge Profile)")
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Voltage (V)")
        ax1.legend(loc="upper right", facecolor="#141b2d", edgecolor="#23304a", labelcolor="#cbd5e1", fontsize=8)

        # 2. Current & Power vs Time (Twin axes)
        ax2.plot(df["Time"], df["Current"], color="#fb923c", linewidth=2.0, label="Current (A)")
        ax2.set_title("Current & Power Drain vs Time")
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel("Current (A)", color="#fb923c")
        ax2.tick_params(axis="y", labelcolor="#fb923c")

        ax2_p = ax2.twinx()
        ax2_p.plot(df["Time"], df["Power"], color="#c084fc", linewidth=1.8, linestyle="-.", label="Power (W)")
        ax2_p.set_ylabel("Power (W)", color="#c084fc")
        ax2_p.tick_params(axis="y", labelcolor="#c084fc")
        ax2_p.spines["right"].set_color("#23304a")
        ax2_p.spines["left"].set_color("#23304a")
        ax2_p.spines["top"].set_color("#23304a")
        ax2_p.spines["bottom"].set_color("#23304a")

        # 3. Capacity & Energy Accumulation
        ax3.plot(df["Time"], df["Capacity_mAh"], color="#10b981", linewidth=2.0, label="Capacity (mAh)")
        ax3.set_title("Delivered Capacity & Energy Accumulation")
        ax3.set_xlabel("Time (s)")
        ax3.set_ylabel("Capacity (mAh)", color="#10b981")
        ax3.tick_params(axis="y", labelcolor="#10b981")

        ax3_e = ax3.twinx()
        ax3_e.plot(df["Time"], df["Energy_Wh"], color="#facc15", linewidth=2.0, linestyle="--", label="Energy (Wh)")
        ax3_e.set_ylabel("Energy (Wh)", color="#facc15")
        ax3_e.tick_params(axis="y", labelcolor="#facc15")
        ax3_e.spines["right"].set_color("#23304a")
        ax3_e.spines["left"].set_color("#23304a")
        ax3_e.spines["top"].set_color("#23304a")
        ax3_e.spines["bottom"].set_color("#23304a")

        # 4. Voltage vs Delivered Capacity (V vs Ah)
        ax4.plot(df["Capacity_Ah"], df["Voltage"], color="#38bdf8", linewidth=2.4)
        ax4.set_title("V vs Delivered Capacity (Definitive Curve)")
        ax4.set_xlabel("Delivered Capacity (Ah)")
        ax4.set_ylabel("Voltage (V)")
        ax4.scatter([df["Capacity_Ah"].iloc[0], df["Capacity_Ah"].iloc[-1]],
                    [df["Voltage"].iloc[0], df["Voltage"].iloc[-1]],
                    color="#00e5ff", s=35, zorder=5)

        self.canvas_dash.draw()

    # --------------------------------------------------------------------------
    # TAB 2: ELECTROCHEMICAL CURVES
    # --------------------------------------------------------------------------
    def _build_tab_electrochemistry(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)

        self.canvas_electro = DarkMplCanvas(widget, width=10, height=6)
        layout.addWidget(self.canvas_electro)
        return widget

    def _render_tab_electrochemistry(self):
        if not self.dataset:
            return

        df = self.dataset.df
        m = self.dataset.metrics
        fig = self.canvas_electro.fig
        fig.clear()

        gs = fig.add_gridspec(2, 2, hspace=0.46, wspace=0.30, top=0.92, bottom=0.10, left=0.07, right=0.93)
        ax1 = fig.add_subplot(gs[0, 0])
        ax2 = fig.add_subplot(gs[0, 1])
        ax3 = fig.add_subplot(gs[1, 0])
        ax4 = fig.add_subplot(gs[1, 1])

        for ax in [ax1, ax2, ax3, ax4]:
            self.canvas_electro.apply_dark_theme(ax)

        # 1. Discharge Stage Decomposition (V vs Ah)
        ax1.plot(df["Capacity_Ah"], df["Voltage"], color="#38bdf8", linewidth=2.5, label="Discharge Curve")
        # Shaded regions
        ohmic_cap = df["Capacity_Ah"].iloc[min(2, len(df)-1)]
        knee_indices = np.where(df["Voltage"] <= 3.5)[0]
        knee_cap = df["Capacity_Ah"].iloc[knee_indices[0]] if len(knee_indices) > 0 else df["Capacity_Ah"].iloc[-1]

        ax1.axvspan(0, ohmic_cap, color="#3b82f6", alpha=0.15, label="1. Ohmic Drop")
        ax1.axvspan(ohmic_cap, knee_cap, color="#10b981", alpha=0.12, label="2. Working Plateau")
        ax1.axvspan(knee_cap, df["Capacity_Ah"].iloc[-1], color="#ef4444", alpha=0.15, label="3. Knee / Depletion")
        ax1.set_title("Discharge Stage Decomposition (V vs Ah)")
        ax1.set_xlabel("Delivered Capacity (Ah)")
        ax1.set_ylabel("Voltage (V)")
        ax1.legend(loc="upper right", facecolor="#141b2d", edgecolor="#23304a", labelcolor="#cbd5e1", fontsize=8)

        # 2. State of Charge (SoC %) vs Voltage (OCV-SoC curve)
        ax2.plot(df["Voltage"], df["SoC_pct"], color="#818cf8", linewidth=2.2)
        ax2.set_title("State of Charge (SoC %) vs Voltage")
        ax2.set_xlabel("Terminal Voltage (V)")
        ax2.set_ylabel("Estimated SoC (%)")
        ax2.grid(True)

        # 3. Voltage Sag Rate (dV/dt) vs Time
        ax3.plot(df["Time"], np.abs(df["dV_dt_mV_s"]), color="#f43f5e", linewidth=1.8, label="|dV/dt|")
        ax3.set_title("Voltage Decay Velocity |dV/dt| (mV/s)")
        ax3.set_xlabel("Time (s)")
        ax3.set_ylabel("Sag Rate (mV/s)")
        ax3.legend(loc="upper right", facecolor="#141b2d", edgecolor="#23304a", labelcolor="#cbd5e1", fontsize=8)

        # 4. Instantaneous Power vs Voltage
        ax4.plot(df["Voltage"], df["Power"], color="#f59e0b", linewidth=2.0)
        ax4.set_title("Power vs Terminal Voltage Profile")
        ax4.set_xlabel("Terminal Voltage (V)")
        ax4.set_ylabel("Power Output (W)")

        self.canvas_electro.draw()

    # --------------------------------------------------------------------------
    # TAB 3: DYNAMIC SIMULATION & PLAYBACK
    # --------------------------------------------------------------------------
    def _build_tab_simulation(self) -> QWidget:
        widget = QWidget()
        h_layout = QHBoxLayout(widget)
        h_layout.setContentsMargins(12, 12, 12, 12)
        h_layout.setSpacing(14)

        # Left panel: Visual Battery Widget & Dynamic Gauge Box
        left_panel = QFrame()
        left_panel.setObjectName("SimCard")
        left_panel.setFixedWidth(310)
        lp_lay = QVBoxLayout(left_panel)
        lp_lay.setContentsMargins(14, 14, 14, 14)
        lp_lay.setSpacing(10)

        lp_title = QLabel("PHYSICAL CELL TELEMETRY")
        lp_title.setObjectName("KpiTitle")
        lp_lay.addWidget(lp_title)

        # The Battery Graphic
        self.battery_widget = BatteryLevelWidget()
        lp_lay.addWidget(self.battery_widget, alignment=Qt.AlignCenter)

        # Live HUD Metric Grid
        grid_frame = QFrame()
        grid_frame.setObjectName("HudFrame")
        grid_lay = QVBoxLayout(grid_frame)
        grid_lay.setContentsMargins(12, 10, 12, 10)
        grid_lay.setSpacing(7)

        def make_hud_row(label: str, attr_name: str, unit: str):
            row = QHBoxLayout()
            l = QLabel(label)
            l.setStyleSheet("color: #94a3b8; font-size: 11px;")
            v = QLabel("--")
            v.setStyleSheet("color: #00e5ff; font-weight: 700; font-size: 13px;")
            setattr(self, attr_name, v)
            row.addWidget(l)
            row.addStretch(1)
            row.addWidget(v)
            return row

        grid_lay.addLayout(make_hud_row("Timestamp:", "hud_time", "s"))
        grid_lay.addLayout(make_hud_row("Terminal Voltage:", "hud_volt", "V"))
        grid_lay.addLayout(make_hud_row("Discharge Current:", "hud_curr", "A"))
        grid_lay.addLayout(make_hud_row("Output Power:", "hud_pow", "W"))
        grid_lay.addLayout(make_hud_row("Capacity Delivered:", "hud_cap", "mAh"))
        grid_lay.addLayout(make_hud_row("Energy Delivered:", "hud_energy", "Wh"))
        grid_lay.addLayout(make_hud_row("Dynamic Sag Rate:", "hud_sag", "mV/s"))

        lp_lay.addWidget(grid_frame)
        lp_lay.addStretch(1)
        h_layout.addWidget(left_panel)

        # Right panel: Dynamic Chart + Scrub/Play controls
        right_panel = QFrame()
        right_panel.setObjectName("PanelCard")
        rp_lay = QVBoxLayout(right_panel)
        rp_lay.setContentsMargins(12, 12, 12, 12)
        rp_lay.setSpacing(10)

        # Canvas for tracking marker
        self.canvas_sim = DarkMplCanvas(right_panel, width=7, height=4)
        rp_lay.addWidget(self.canvas_sim, stretch=1)

        # Control Bar
        ctrl_box = QFrame()
        ctrl_box.setStyleSheet("background: #0f172a; border-radius: 8px; padding: 10px;")
        ctrl_lay = QVBoxLayout(ctrl_box)
        ctrl_lay.setSpacing(8)

        # Slider row
        slider_row = QHBoxLayout()
        self.lbl_sim_time_now = QLabel("0.0 s")
        self.lbl_sim_time_now.setStyleSheet("color: #00e5ff; font-weight: 700; font-size: 12px; min-width: 60px;")
        self.sim_slider = QSlider(Qt.Horizontal)
        self.sim_slider.setRange(0, 100)
        self.sim_slider.sliderMoved.connect(self._on_slider_moved)
        self.lbl_sim_time_end = QLabel("0.0 s")
        self.lbl_sim_time_end.setStyleSheet("color: #94a3b8; font-size: 12px; min-width: 60px; text-align: right;")

        slider_row.addWidget(self.lbl_sim_time_now)
        slider_row.addWidget(self.sim_slider, stretch=1)
        slider_row.addWidget(self.lbl_sim_time_end)
        ctrl_lay.addLayout(slider_row)

        # Buttons row
        btn_row = QHBoxLayout()
        self.btn_play = QPushButton("▶ Play")
        self.btn_play.setFixedSize(95, 34)
        self.btn_play.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00c6ff, stop:1 #0072ff); color: #ffffff; font-weight: 800; border-radius: 6px; font-size: 13px;")
        self.btn_play.clicked.connect(self._toggle_playback)

        self.btn_rewind = QPushButton("⏮ Reset")
        self.btn_rewind.setFixedSize(85, 34)
        self.btn_rewind.setStyleSheet("background: #1e293b; color: #f8fafc; border: 1px solid #334155; border-radius: 6px; font-weight: 600; font-size: 12px;")
        self.btn_rewind.clicked.connect(self._rewind_playback)

        btn_row.addWidget(self.btn_play)
        btn_row.addWidget(self.btn_rewind)
        btn_row.addSpacing(16)

        # Speed selector
        btn_row.addWidget(QLabel("Speed:"))
        self.combo_speed = QComboBox()
        self.combo_speed.addItems(["1x Real-Time", "2x Faster", "5x High Speed", "10x Ultra Speed"])
        self.combo_speed.currentIndexChanged.connect(self._on_speed_changed)
        btn_row.addWidget(self.combo_speed)
        btn_row.addStretch(1)

        ctrl_lay.addLayout(btn_row)
        rp_lay.addWidget(ctrl_box)

        h_layout.addWidget(right_panel, stretch=1)
        return widget

    def _render_tab_simulation_static(self):
        """Pre-draws the base curve on the simulation plot."""
        if not self.dataset:
            return

        df = self.dataset.df
        fig = self.canvas_sim.fig
        fig.clear()

        self.sim_ax = fig.add_subplot(1, 1, 1)
        self.canvas_sim.apply_dark_theme(self.sim_ax)

        self.sim_ax.plot(df["Time"], df["Voltage"], color="#334155", linewidth=2.0, label="Discharge Path")
        self.sim_line_active, = self.sim_ax.plot([], [], color="#00e5ff", linewidth=2.5, label="Elapsed")
        self.sim_marker, = self.sim_ax.plot([], [], marker="o", markersize=9, color="#00e5ff",
                                            markeredgecolor="#ffffff", markeredgewidth=2)

        self.sim_ax.set_title("Interactive Dynamic Discharge Tracker")
        self.sim_ax.set_xlabel("Time (s)")
        self.sim_ax.set_ylabel("Voltage (V)")
        self.sim_ax.set_xlim(df["Time"].min() - 10, df["Time"].max() + 10)
        self.sim_ax.set_ylim(df["Voltage"].min() - 0.1, df["Voltage"].max() + 0.1)

        self.canvas_sim.draw()

    def _update_simulation_point(self, idx: int):
        """Updates the interactive gauges and cursor to point idx."""
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

        # Update Battery Widget
        self.battery_widget.set_values(soc, v)

        # Update Plot Marker
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
        else:
            self.play_timer.start(100 // self.playback_speed)
            self.btn_play.setText("⏸ Pause")

    def _on_playback_tick(self):
        if not self.dataset:
            return
        n = len(self.dataset.df)
        if self.play_idx >= n - 1:
            self.play_timer.stop()
            self.btn_play.setText("▶ Play")
            return
        self.play_idx += 1
        self._update_simulation_point(self.play_idx)

    def _rewind_playback(self):
        self.play_timer.stop()
        self.btn_play.setText("▶ Play")
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
    # TAB 4: DATA INSPECTOR & TABLE
    # --------------------------------------------------------------------------
    def _build_tab_inspector(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Filter bar
        top_bar = QHBoxLayout()
        search_lbl = QLabel("Search / Filter Data:")
        search_lbl.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: 600;")
        top_bar.addWidget(search_lbl)

        self.edit_filter = QLineEdit()
        self.edit_filter.setPlaceholderText("Filter rows by typing (e.g. 4.1 or 3.2)...")
        self.edit_filter.textChanged.connect(self._filter_table)
        top_bar.addWidget(self.edit_filter, stretch=1)

        self.btn_export_csv = QPushButton("💾 Export Table to CSV")
        self.btn_export_csv.clicked.connect(self.on_export_table_csv)
        top_bar.addWidget(self.btn_export_csv)

        layout.addLayout(top_bar)

        # Table
        self.table_widget = QTableWidget()
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.verticalHeader().setVisible(False)
        layout.addWidget(self.table_widget, stretch=1)

        # Summary Statistics Bar
        self.lbl_stats = QLabel("Points: 0 • Min Voltage: -- • Max Voltage: --")
        self.lbl_stats.setStyleSheet("color: #94a3b8; font-size: 11px;")
        layout.addWidget(self.lbl_stats)

        return widget

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
            f"Total Points: {m.data_points}  |  Sample Rate: {m.sample_rate_s:.1f}s  |  "
            f"V range: [{m.v_min:.2f}V - {m.v_max:.2f}V]  |  I mean: {m.i_mean:.2f}A  |  P mean: {m.p_mean:.2f}W"
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
    # TAB 5: DIAGNOSTIC REPORT
    # --------------------------------------------------------------------------
    def _build_tab_report(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        # Top action strip
        top_strip = QHBoxLayout()
        title_rep = QLabel("BATTERY TEST CERTIFICATION & ENGINEERING AUDIT")
        title_rep.setStyleSheet("font-size: 13px; font-weight: 700; color: #38bdf8;")
        top_strip.addWidget(title_rep)
        top_strip.addStretch(1)

        btn_copy = QPushButton("📋 Copy Report")
        btn_copy.clicked.connect(self._copy_report_to_clipboard)
        top_strip.addWidget(btn_copy)

        btn_save_txt = QPushButton("📄 Save as TXT")
        btn_save_txt.clicked.connect(self._save_report_txt)
        top_strip.addWidget(btn_save_txt)

        btn_open_html = QPushButton("🌐 View in Browser (HTML)")
        btn_open_html.setObjectName("PrimaryBtn")
        btn_open_html.clicked.connect(self.on_export_html)
        top_strip.addWidget(btn_open_html)

        layout.addLayout(top_strip)

        # Formatted report view
        self.report_text = QLabel()
        self.report_text.setTextFormat(Qt.MarkdownText)
        self.report_text.setStyleSheet("""
            background-color: #101626;
            border: 1px solid #23304a;
            border-radius: 8px;
            padding: 20px;
            color: #f8fafc;
            font-size: 13px;
            line-height: 1.6;
        """)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        scroll.setWidget(self.report_text)

        layout.addWidget(scroll, stretch=1)
        return widget

    def _render_tab_report(self):
        if not self.dataset:
            return

        m = self.dataset.metrics
        name = self.dataset.source_name

        report_md = f"""# 🔋 VOLTIX PRO Electrochemical Test Report
**Dataset File:** `{name}`  
**Test Date:** `{time.strftime('%Y-%m-%d %H:%M:%S')}`  
**Evaluation Rating:** **<span style="color: #00e5ff;">{m.cell_grade}</span>**  
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
        QMessageBox.information(self, "Copied", "Engineering report copied to system clipboard!")

    def _save_report_txt(self):
        if not self.dataset:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Test Report", "battery_report.txt", "Text Files (*.txt)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.report_text.text())
            QMessageBox.information(self, "Saved", f"Report saved successfully to {os.path.basename(path)}")

    # --------------------------------------------------------------------------
    # DATASET LOADING & RECALCULATION
    # --------------------------------------------------------------------------
    def load_dataset(self, file_path: str):
        """Loads and processes a new battery dataset."""
        try:
            nom_cap = self.spin_capacity.value()
            cutoff = self.spin_cutoff.value()
            self.dataset = load_and_analyze(file_path, nominal_capacity_ah=nom_cap, cutoff_voltage=cutoff)
            self._update_all_views()
            self.lbl_dataset.setText(f"📁 {os.path.basename(file_path)}")
            self.status_bar_label.setText(f"Dataset '{os.path.basename(file_path)}' loaded • {self.dataset.metrics.data_points} points analyzed.")
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load dataset:\n{str(e)}")

    def _recalc_with_params(self):
        """Recomputes with updated spinbox parameters."""
        if not self.dataset:
            return
        self.dataset.nominal_capacity_ah = self.spin_capacity.value()
        self.dataset.cutoff_voltage = self.spin_cutoff.value()
        self.dataset.process_data()
        self._update_all_views()

    def _on_chem_changed(self, idx: int):
        """Presets nominal values based on selected battery chemistry."""
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
        """Refreshes all cards, plots, and tables."""
        if not self.dataset:
            return

        m = self.dataset.metrics

        # 1. Update KPI Cards
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
        self._render_tab_dashboard()
        self._render_tab_electrochemistry()

        # 3. Setup Simulation Slider & Canvas
        n = len(self.dataset.df)
        self.sim_slider.setRange(0, n - 1)
        self.lbl_sim_time_end.setText(f"{m.duration_s:.1f} s")
        self._render_tab_simulation_static()
        self._update_simulation_point(0)

        # 4. Populate Inspector Table
        self._populate_table()

        # 5. Render Report
        self._render_tab_report()

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
        path, _ = QFileDialog.getSaveFileName(self, "Save Dashboard Snapshot", "battery_dashboard.png", "PNG Image (*.png);;PDF (*.pdf)")
        if path:
            self.canvas_dash.fig.savefig(path, dpi=300, facecolor=self.canvas_dash.fig.get_facecolor(), bbox_inches="tight")
            QMessageBox.information(self, "Saved", f"Dashboard snapshot saved to:\n{path}")

    def on_export_table_csv(self):
        if not self.dataset:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Computed Telemetry", "battery_telemetry_analyzed.csv", "CSV Files (*.csv)")
        if path:
            self.dataset.df.to_csv(path, index=False)
            QMessageBox.information(self, "Saved", f"Full telemetry table exported to:\n{path}")


# ==============================================================================
# MAIN LAUNCHER
# ==============================================================================
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Voltix Pro Modern Battery Analyzer")
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

    # Enable High DPI scaling and launch GUI
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setStyleSheet(MODERN_QSS)

    csv_to_open = args.file if os.path.exists(args.file) else ("battery_data.csv" if os.path.exists("battery_data.csv") else args.file)
    win = ModernBatteryAnalyzer(initial_csv=csv_to_open)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
