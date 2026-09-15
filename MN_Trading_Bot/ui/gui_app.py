# ui/gui_app.py

# ==========================================
# STYLESHEETS (PowerX Optimizer Style)
# ==========================================
DARK_THEME = """
    QMainWindow { background-color: #12151c; }
    QWidget { 
        background-color: #12151c; 
        color: #e8eaed; 
        font-family: 'Inter', 'Segoe UI', sans-serif; 
        font-size: 13px;
    }

    /* ── Eingabefelder ─────────────────────────────────────────── */
    QLineEdit, QSpinBox, QDoubleSpinBox, QTimeEdit, QComboBox { 
        background-color: #1a1e27; 
        border: 1px solid #2a2f3a; 
        border-radius: 6px; 
        padding: 5px 9px; 
        color: #e8eaed; 
        selection-background-color: #2196f3; 
        selection-color: #ffffff;
        min-height: 22px; 
    }
    QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QTimeEdit:hover, QComboBox:hover { 
        border: 1px solid #3a4150; 
    }
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTimeEdit:focus { 
        border: 1px solid #2196f3; 
    }
    QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled, QComboBox:disabled {
        color: #4d5561;
        border-color: #232833;
    }
    QComboBox::drop-down { border: none; width: 20px; }
    QComboBox::down-arrow {
        image: none;
        width: 0; height: 0;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid #9aa1ad;
        margin-right: 8px;
    }
    QComboBox::down-arrow:hover, QComboBox::down-arrow:on { border-top-color: #2196f3; }
    QComboBox QAbstractItemView { 
        background-color: #1a1e27; 
        border: 1px solid #2a2f3a;
        color: #e8eaed; 
        selection-background-color: #2196f3; 
        selection-color: #ffffff;
        outline: none;
    }

    /* ── Spin-Buttons (Spin/Double/Time-Edit teilen QAbstractSpinBox) ── */
    QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {
        background-color: #2a3140;
        border-left: 1px solid #2a2f3a;
        width: 24px;
    }
    QAbstractSpinBox::up-button {
        subcontrol-position: top right;
        border-top-right-radius: 6px;
    }
    QAbstractSpinBox::down-button {
        subcontrol-position: bottom right;
        border-bottom-right-radius: 6px;
    }
    QAbstractSpinBox::up-button:hover, QAbstractSpinBox::down-button:hover {
        background-color: #2196f3;
    }
    QAbstractSpinBox::up-button:pressed, QAbstractSpinBox::down-button:pressed {
        background-color: #1976d2;
    }
    QAbstractSpinBox::up-arrow {
        image: none; width: 0; height: 0;
        border-left: 6px solid transparent; border-right: 6px solid transparent;
        border-bottom: 9px solid #ffffff;
    }
    QAbstractSpinBox::down-arrow {
        image: none; width: 0; height: 0;
        border-left: 6px solid transparent; border-right: 6px solid transparent;
        border-top: 9px solid #ffffff;
    }
    QAbstractSpinBox::up-arrow:disabled {
        border-bottom-color: #4d5561;
    }
    QAbstractSpinBox::down-arrow:disabled {
        border-top-color: #4d5561;
    }
    /* ── Buttons ───────────────────────────────────────────────── */
    QPushButton { 
        background-color: #1a1e27; 
        border: 1px solid #2a2f3a; 
        border-radius: 3px; 
        padding: 7px 16px; 
        font-weight: 600; 
        color: #e8eaed; 
    }
    QPushButton:hover { 
        background-color: #232833; 
        border-color: #3a4150; 
    }
    QPushButton:pressed { background-color: #14171e; }
    QPushButton:checked {
        background-color: #19385c;
        border: 1px solid #2196f3;
        color: #64b5f6;
    }
    QPushButton:disabled { 
        background-color: #1a1e27; 
        color: #4d5561; 
        border-color: #232833; 
    }
    /* Blau = Primäre Aktion (PXO Place Order / Set) */
    QPushButton#btn_success { background-color: #2196f3; color: #ffffff; border: none; }
    QPushButton#btn_success:hover { background-color: #1e88e5; }
    /* Orange = Sekundärakzent (PXO High-ROI Highlight / Banner) */
    QPushButton#btn_accent { background-color: #f2994a; color: #1a1206; border: none; font-weight: 700; }
    QPushButton#btn_accent:hover { background-color: #e0822c; }
    /* Rot = Destruktive Aktion (Stop Loss / Exit) */
    QPushButton#btn_danger { background-color: #f2555c; color: #ffffff; border: none; }
    QPushButton#btn_danger:hover { background-color: #d8383f; }
    /* Platzhalter-Buttons – schmale Spalten */
    QPushButton#btn_locked:disabled {
        background-color: #1a1e27;
        color: #6b7482;
        border-color: #232833;
    }

    /* ── Tabellen & Header ─────────────────────────────────────── */
    QTableWidget { 
        background-color: #1a1e27; 
        gridline-color: #232833; 
        border: 1px solid #2a2f3a; 
        border-radius: 8px; 
        color: #e8eaed;
        outline: none;
    }
    QTableWidget::item { padding: 4px 6px; }
    QHeaderView::section { 
        background-color: #14171e; 
        color: #8993a3; 
        padding: 8px 6px; 
        font-weight: 700; 
        font-size: 11px;
        border: none; 
        border-bottom: 1px solid #2a2f3a;
    }
    QTableWidget::item:selected { 
        background-color: #19385c; 
        color: #64b5f6; 
    }
    QTableCornerButton::section { background-color: #14171e; border: none; }

    /* ── GroupBoxes & Tabs ─────────────────────────────────────── */
    QGroupBox { 
        background-color: #1a1e27;
        border: 1px solid #2a2f3a; 
        border-radius: 8px; 
        margin-top: 14px; 
        font-weight: 700; 
        color: #e8eaed; 
        padding-top: 12px;
    }
    QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }
    QGroupBox::indicator {
        width: 16px; height: 16px;
        border: 1px solid #2a2f3a;
        border-radius: 4px;
        background-color: #1a1e27;
        margin-left: 4px;
    }
    QGroupBox::indicator:hover { border: 1px solid #2196f3; }
    QGroupBox::indicator:checked { background-color: #2196f3; border: 1px solid #2196f3; }

    /* Underline-Tabs (wie PXO: "Conservative | Aggressive | Watchlist") */
    QTabWidget::pane { border: 1px solid #2a2f3a; background: #12151c; border-radius: 8px; top: -1px; }
    QTabBar::tab { 
        background: transparent; 
        color: #7c8798; 
        padding: 10px 18px; 
        border: none;
        border-bottom: 2px solid transparent;
        margin-right: 4px; 
        font-weight: 600; 
    }
    QTabBar::tab:selected { color: #2196f3; border-bottom: 2px solid #2196f3; }
    QTabBar::tab:hover:!selected { color: #e8eaed; }

    /* ── ScrollBars ────────────────────────────────────────────── */
    QScrollArea { background-color: transparent; border: none; }
    QScrollBar:vertical { background: #12151c; width: 10px; margin: 0; }
    QScrollBar::handle:vertical { background: #2a2f3a; border-radius: 5px; min-height: 24px; }
    QScrollBar::handle:vertical:hover { background: #2196f3; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
    QScrollBar:horizontal { background: #12151c; height: 10px; margin: 0; }
    QScrollBar::handle:horizontal { background: #2a2f3a; border-radius: 5px; min-width: 24px; }
    QScrollBar::handle:horizontal:hover { background: #2196f3; }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

    /* ── Sensor-Badges & Custom Switches ───────────────────────── */
    QLabel#sensorBadge {
        background-color: #1a1e27; 
        border: 1px solid #2a2f3a; 
        border-radius: 5px;
        padding: 5px 12px; 
        font-weight: 700; 
        color: #9aa1ad;
    }
    /* NEU (DARK_THEME) */
    QCheckBox#toggleSwitch::indicator {
        width: 38px; height: 20px; border-radius: 10px;
        background-color: #2a3140; border: 1px solid #3a4150;
    }
    QCheckBox#toggleSwitch::indicator:checked { background-color: #2e8b57; border: 1px solid #2e8b57; }
    QCheckBox#toggleSwitch::indicator:hover { border-color: #2196f3; }

    /* Sonderfall Broker-Modus (Live/Paper) */
    QCheckBox#toggleSwitchDanger::indicator {
        width: 38px; height: 20px; border-radius: 10px;
        background-color: #2e8b57; border: 1px solid #2e8b57;
    }
    QCheckBox#toggleSwitchDanger::indicator:checked { background-color: #b45309; border: 1px solid #b45309; }
    QCheckBox#toggleSwitchDanger::indicator:hover { border-color: #2196f3; }
    QCheckBox#toggleSwitch { font-weight: 700; padding: 2px; }

    /* ── Reguläre Checkboxes ───────────────────────────────────── */
    QCheckBox { spacing: 8px; }
    QCheckBox::indicator { 
        width: 16px; height: 16px; 
        border: 1px solid #2a2f3a; 
        border-radius: 4px; 
        background-color: #1a1e27; 
    }
    QCheckBox::indicator:hover { border: 1px solid #2196f3; }
    QCheckBox::indicator:checked { background-color: #2196f3; border: 1px solid #2196f3; }

    /* ── Tooltips ──────────────────────────────────────────────── */
    QToolTip {
        background-color: #1a1e27;
        color: #e8eaed;
        border: 1px solid #2a2f3a;
        padding: 4px 8px;
        border-radius: 4px;
    }
"""

LIGHT_THEME = """
    QMainWindow { background-color: #f4f6f9; }
    QWidget { 
        background-color: #f4f6f9; 
        color: #1f2430; 
        font-family: 'Inter', 'Segoe UI', sans-serif; 
        font-size: 13px;
    }

    /* ── Eingabefelder ─────────────────────────────────────────── */
    QLineEdit, QSpinBox, QDoubleSpinBox, QTimeEdit, QComboBox { 
        background-color: #ffffff; 
        border: 1px solid #e1e4e9; 
        border-radius: 6px; 
        padding: 5px 9px; 
        color: #1f2430; 
        selection-background-color: #2196f3; 
        selection-color: #ffffff;
        min-height: 22px; 
    }
    QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QTimeEdit:hover, QComboBox:hover { 
        border: 1px solid #c3cad3; 
    }
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTimeEdit:focus { 
        border: 1px solid #2196f3; 
    }
    QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled, QComboBox:disabled {
        color: #aab1bc;
        border-color: #eaecf0;
    }
    QComboBox::drop-down { border: none; width: 20px; }
    QComboBox::down-arrow {
        image: none;
        width: 0; height: 0;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid #7c8798;
        margin-right: 8px;
    }
    QComboBox::down-arrow:hover, QComboBox::down-arrow:on { border-top-color: #2196f3; }
    QComboBox QAbstractItemView { 
        background-color: #ffffff; 
        border: 1px solid #e1e4e9;
        color: #1f2430; 
        selection-background-color: #2196f3; 
        selection-color: #ffffff;
        outline: none;
    }

    /* ── Spin-Buttons ──────────────────────────────────────────── */
    QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {
        background-color: #e2e8f0;
        border-left: 1px solid #cbd5e1;
        width: 24px;
    }
    QAbstractSpinBox::up-button {
        subcontrol-position: top right;
        border-top-right-radius: 6px;
    }
    QAbstractSpinBox::down-button {
        subcontrol-position: bottom right;
        border-bottom-right-radius: 6px;
    }
    QAbstractSpinBox::up-button:hover, QAbstractSpinBox::down-button:hover {
        background-color: #2196f3;
    }
    QAbstractSpinBox::up-button:pressed, QAbstractSpinBox::down-button:pressed {
        background-color: #1976d2;
    }
    QAbstractSpinBox::up-arrow {
        image: none; width: 0; height: 0;
        border-left: 6px solid transparent; border-right: 6px solid transparent;
        border-bottom: 9px solid #0f172a;
    }
    QAbstractSpinBox::down-arrow {
        image: none; width: 0; height: 0;
        border-left: 6px solid transparent; border-right: 6px solid transparent;
        border-top: 9px solid #0f172a;
    }
    QAbstractSpinBox::up-arrow:hover { border-bottom-color: #ffffff; }
    QAbstractSpinBox::down-arrow:hover { border-top-color: #ffffff; }
    QAbstractSpinBox::up-arrow:disabled {
        border-bottom-color: #aab1bc;
    }
    QAbstractSpinBox::down-arrow:disabled {
        border-top-color: #aab1bc;
    }

    /* ── Buttons ───────────────────────────────────────────────── */
    QPushButton { 
        background-color: #ffffff; 
        border: 1px solid #e1e4e9; 
        border-radius: 6px; 
        padding: 7px 8px; 
        font-weight: 600; 
        color: #1f2430; 
    }
    QPushButton:hover { 
        background-color: #f8fafc; 
        border-color: #c3cad3; 
    }
    QPushButton:pressed { background-color: #eef0f3; }
    QPushButton:checked {
        background-color: #e3f2fd;
        border: 1px solid #2196f3;
        color: #1976d2;
    }
    QPushButton:disabled { 
        background-color: #eef1f5; 
        color: #aab1bc; 
        border-color: #eaecf0; 
    }
    /* Blau = Primäre Aktion (PXO Place Order / Set) */
    QPushButton#btn_success { background-color: #2196f3; color: #ffffff; border: none; }
    QPushButton#btn_success:hover { background-color: #1e88e5; }
    /* Orange = Sekundärakzent (PXO Banner Highlight) */
    QPushButton#btn_accent { background-color: #f2994a; color: #ffffff; border: none; font-weight: 700; }
    QPushButton#btn_accent:hover { background-color: #e0822c; }
    /* Rot = Destruktive Aktion (Stop Loss / Exit) */
    QPushButton#btn_danger { background-color: #e5484d; color: #ffffff; border: none; }
    QPushButton#btn_danger:hover { background-color: #cc3238; }
    /* Platzhalter-Buttons – schmale Spalten */
    QPushButton#btn_locked:disabled {
        background-color: #eef1f5;
        color: #8b95a5;
        border-color: #dde3ea;
    }

    /* ── Tabellen & Header ─────────────────────────────────────── */
    QTableWidget { 
        background-color: #ffffff; 
        gridline-color: #eaecf0; 
        border: 1px solid #e1e4e9; 
        border-radius: 8px; 
        color: #1f2430;
        outline: none;
    }
    QTableWidget::item { padding: 4px 6px; }
    QHeaderView::section { 
        background-color: #f7f8fa; 
        color: #7c8798; 
        padding: 8px 6px; 
        font-weight: 700; 
        font-size: 11px;
        border: none; 
        border-bottom: 1px solid #e1e4e9;
    }
    QTableWidget::item:selected { 
        background-color: #e3f2fd; 
        color: #1976d2; 
    }
    QTableCornerButton::section { background-color: #f7f8fa; border: none; }

    /* ── GroupBoxes & Tabs ─────────────────────────────────────── */
    QGroupBox { 
        background-color: #ffffff;
        border: 1px solid #e1e4e9; 
        border-radius: 8px; 
        margin-top: 14px; 
        font-weight: 700; 
        color: #1f2430; 
        padding-top: 12px;
    }
    QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }
    QGroupBox::indicator {
        width: 16px; height: 16px;
        border: 1px solid #e1e4e9;
        border-radius: 4px;
        background-color: #ffffff;
        margin-left: 4px;
    }
    QGroupBox::indicator:hover { border: 1px solid #2196f3; }
    QGroupBox::indicator:checked { background-color: #2196f3; border: 1px solid #2196f3; }

    /* Underline-Tabs (wie PXO: "Conservative | Aggressive | Watchlist") */
    QTabWidget::pane { border: 1px solid #e1e4e9; background: #f4f6f9; border-radius: 8px; top: -1px; }
    QTabBar::tab { 
        background: transparent; 
        color: #7c8798; 
        padding: 10px 18px; 
        border: none;
        border-bottom: 2px solid transparent;
        margin-right: 4px; 
        font-weight: 600; 
    }
    QTabBar::tab:selected { color: #2196f3; border-bottom: 2px solid #2196f3; }
    QTabBar::tab:hover:!selected { color: #1f2430; }

    /* ── ScrollBars ────────────────────────────────────────────── */
    QScrollArea { background-color: transparent; border: none; }
    QScrollBar:vertical { background: #f4f6f9; width: 10px; margin: 0; }
    QScrollBar::handle:vertical { background: #e1e4e9; border-radius: 5px; min-height: 24px; }
    QScrollBar::handle:vertical:hover { background: #2196f3; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
    QScrollBar:horizontal { background: #f4f6f9; height: 10px; margin: 0; }
    QScrollBar::handle:horizontal { background: #e1e4e9; border-radius: 5px; min-width: 24px; }
    QScrollBar::handle:horizontal:hover { background: #2196f3; }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

    /* ── Sensor-Badges & Custom Switches ───────────────────────── */
    QLabel#sensorBadge {
        background-color: #f7f8fa; 
        border: 1px solid #e1e4e9; 
        border-radius: 5px;
        padding: 5px 12px; 
        font-weight: 700; 
        color: #7c8798;
    }
    QCheckBox#toggleSwitch::indicator {
        width: 38px; height: 20px; border-radius: 10px;
        background-color: #e2e8f0; border: 1px solid #3a4150;
    }
    QCheckBox#toggleSwitch::indicator:checked { background-color: #2f9e5e; border: 1px solid #2f9e5e; }
    QCheckBox#toggleSwitch::indicator:hover { border-color: #2196f3; }

    /* Sonderfall Broker-Modus (Live/Paper) */
    QCheckBox#toggleSwitchDanger::indicator {
        width: 38px; height: 20px; border-radius: 10px;
        background-color: #2f9e5e; border: 1px solid #2f9e5e;
    }
    QCheckBox#toggleSwitchDanger::indicator:checked  { background-color: #b45309; border: 1px solid #b45309; }
    QCheckBox#toggleSwitchDanger::indicator:hover { border-color: #2196f3; }
    QCheckBox#toggleSwitch { font-weight: 700; padding: 2px; }

    /* ── Reguläre Checkboxes ───────────────────────────────────── */
    QCheckBox { spacing: 8px; }
    QCheckBox::indicator { 
        width: 16px; height: 16px; 
        border: 1px solid #e1e4e9; 
        border-radius: 4px; 
        background-color: #ffffff; 
    }
    QCheckBox::indicator:hover { border: 1px solid #2196f3; }
    QCheckBox::indicator:checked { background-color: #2196f3; border: 1px solid #2196f3; }

    /* ── Tooltips ──────────────────────────────────────────────── */
    QToolTip {
        background-color: #1f2430;
        color: #ffffff;
        border: 1px solid #e1e4e9;
        padding: 4px 8px;
        border-radius: 4px;
    }
    /* Container und Zeilen in Form layouts vollkommen transparent machen */
    QFormLayout, QGroupBox QWidget {
        background-color: transparent;
    }

    /* Transparenter Hintergrund für Labels und Checkbox-Texte */
    QLabel, QCheckBox {
        background-color: transparent;
        color: #0f172a;
    }

    /* Verhindert graue Hintergründe bei Checkbox-Indikatoren/Texten */
    QCheckBox::indicator {
        background-color: transparent;
    }

    /* NUR Eingabefelder bekommen eine explizite weiße Box mit Rand */
    QLineEdit, QSpinBox, QDoubleSpinBox, QTimeEdit, QComboBox {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 4px;
        padding: 4px 8px;
        color: #0f172a;
    }
    /* Transparenz für alle verschachtelten Sub-Widgets in Formular-Layouts */
    QFormLayout > QWidget,
    QGroupBox QWidget {
        background-color: transparent;
        background: transparent;
    }

    /* Spezifische Korrektur für benutzerdefinierte Checkbox- & Switch-Container */
    QCheckBox, QCheckBox::indicator, QCheckBox * {
        background-color: transparent;
    }

    /* Verhindert, dass Toggle-Switch-Labels einen festen Hintergrund zeichnen */
    QWidget[class*="Toggle"], QWidget[class*="Switch"] {
        background-color: transparent;
    }
   
"""

from ib_insync import IB
import sys
import ctypes
import os
import json
import socket
import struct
import random
import requests
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import pytz
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox,
    QTimeEdit, QGroupBox, QScrollArea, QMessageBox, QFrame, QSplitter, QInputDialog,
    QAbstractItemView, QListWidget, QListWidgetItem, QAbstractSpinBox, QFileDialog,
    QSizePolicy
)
from PySide6.QtCore import Qt, QTime, QTimer, QEvent, QObject
from PySide6.QtGui import QFont, QColor, QIcon

class NoWheelFilter(QObject):
    """
    Blockiert Mausrad-Events auf allen Spin-/Time-/ComboBoxen ("+/-"-Felder),
    damit Scrollen über die Seite nicht versehentlich Werte verändert.
    QAbstractSpinBox deckt QSpinBox/QDoubleSpinBox/QTimeEdit/QDateEdit ab.
    """
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Wheel and isinstance(obj, (QAbstractSpinBox, QComboBox)):
            event.ignore()
            return True
        return super().eventFilter(obj, event)

# ==========================================
# KONFIGURATIONSPFADE (%userprofile%/mn_bot/config)
# ==========================================
CONFIG_DIR = Path.home() / "mn_bot" / "config"
SCHEDULES_FILE = CONFIG_DIR / "schedules.json"
TEMPLATES_FILE = CONFIG_DIR / "trade_templates.json"
BROKER_FILE = CONFIG_DIR / "broker_settings.json"
BOT_MODE_FILE = CONFIG_DIR / "bot_mode_settings.json"
TELEGRAM_FILE = CONFIG_DIR / "telegram_settings.json"

SERVICE_NAME = "MN Trading Bot Scheduler"

DAY_ABBR_TO_FULL = {
    "MON": "MONDAY", "TUE": "TUESDAY", "WED": "WEDNESDAY",
    "THU": "THURSDAY", "FRI": "FRIDAY", "SAT": "SATURDAY", "SUN": "SUNDAY",
}


# Hilfsfunktionen zum Laden/Speichern von JSON
def load_json(filepath, default_content):
    if not filepath.exists():
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(default_content, f, indent=4)
        return default_content
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default_content

def save_json(filepath, data):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


class TradingBotUI(QMainWindow):
    def __init__(self):
            super().__init__()
            self.setWindowTitle("MN Trading Bot Manager")
            self.resize(1024, 768)

            # Pfad zu deinem Custom-Icon (PNG oder ICO)
            icon_path = Path(__file__).parent / "favicon.png"
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))

            # Aktueller Theme-Status (True = Dark, False = Light) – gepflegt von
            # toggle_theme(), genutzt für theme-abhängige Akzentfarben (z.B. in
            # refresh_today_preview()). Default passt zum direkt gesetzten LIGHT_THEME unten.
            self.is_dark_theme = False

            # Bugfix: wurde bisher nirgends initialisiert, aber in
            # check_telegram_alert_on_disconnect() gelesen -> AttributeError beim
            # ersten TWS-Disconnect (z.B. direkt beim Start ohne laufendes TWS).
            self.last_telegram_alert_time = None

            # Letzter bekannter TWS-Verbindungsstatus (None = noch nicht geprüft).
            # Wird gebraucht, um das Status-Badge nach einem Theme-Wechsel korrekt
            # neu einzufärben (siehe toggle_theme() / _style_status_badge()).
            self._tws_connected = None

            # 1. Konfigurationen laden
            self.load_all_configs()

            # 2. Standard-Style setzen (PowerX Light Mode)
            QApplication.instance().setStyleSheet(LIGHT_THEME)

            # 3. Benutzeroberfläche aufbauen
            self.init_ui()

            # 4. Background-Timer starten
            self.status_timer = QTimer(self)
            self.status_timer.timeout.connect(self.check_tws_status)
            self.status_timer.timeout.connect(self.update_service_status)
            self.status_timer.start(5000)

            # 5. Erstprüfung nach UI-Aufbau
            self.update_service_status()
            self.check_tws_status()
        
    def toggle_theme(self, is_light):
            if is_light:
                QApplication.instance().setStyleSheet(LIGHT_THEME)
                self.is_dark_theme = False
                self.btn_theme_toggle.setText("🌙 Dark Mode")
            else:
                QApplication.instance().setStyleSheet(DARK_THEME)
                self.is_dark_theme = True
                self.btn_theme_toggle.setText("☀️ Light Mode")

            # Hart codierte Akzentfarben (Expired/Pending) in der "Heute geplant"-
            # Tabelle sind theme-abhängig -> nach Theme-Wechsel neu einfärben.
            if hasattr(self, "today_table"):
                self.refresh_today_preview()

            # TWS-Status-Badge neu einfärben: die State-Farben werden inline
            # gesetzt (siehe _style_status_badge()) und überleben deshalb
            # KEINEN globalen QApplication.setStyleSheet()-Wechsel automatisch.
            if hasattr(self, "lbl_tws_status"):
                state = "checking"
                if self._tws_connected is True:
                    state = "connected"
                elif self._tws_connected is False:
                    state = "disconnected"
                self._style_status_badge(self.lbl_tws_status, state)   

    def load_all_configs(self):
        self.schedules_data = load_json(SCHEDULES_FILE, [])
        if isinstance(self.schedules_data, dict):
            self.schedules_data = self.schedules_data.get("schedules", [])

        self.templates_data = load_json(TEMPLATES_FILE, [])
        if isinstance(self.templates_data, dict):
            self.templates_data = self.templates_data.get("templates", [])

        self.broker_data = load_json(BROKER_FILE, {
            "IB_HOST": "127.0.0.1", "IB_PORT_PAPER": 7498, "IB_PORT_LIVE": 7497,
            "CLIENT_ID": 1, "USE_PAPER_TRADING": True
        })
        self.bot_mode_data = load_json(BOT_MODE_FILE, {
            "DEBUG_MODE": False, "CHECK_CONDITIONS": True, "CHECK_EXECUTION_TIME": True,
            "CHECK_MARKET_OPEN": True, "TRADE_REPORT_CSV": "reports/mn_trading_trade_report.csv"
        })
        self.telegram_data = load_json(TELEGRAM_FILE, {
            "TELEGRAM_ENABLED": True, "TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": ""
        })

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # 1. Top Bar mit Statusfeld & TWS Sensor
        main_layout.addLayout(self.create_top_service_bar())
        

        # 2. Haupt-Tabs
        self.main_tabs = QTabWidget()
        self.main_tabs.addTab(self.create_dashboard_tab(), "📊 Dashboard")
        self.main_tabs.addTab(self.create_schedule_editor_tab(), "📝 Schedule-Editor")
        self.main_tabs.addTab(self.create_templates_tab(), "📜 Trade Templates")
        self.main_tabs.addTab(self.create_system_config_tab(), "⚙️ System-Einstellungen")

        main_layout.addWidget(self.main_tabs)
        self.setCentralWidget(main_widget)
        self._apply_plus_minus_symbols()
        
    def _apply_plus_minus_symbols(self):
        """
        Entfernt die Spin-/Time-Buttons komplett (kein +/- und keine Pfeile
        mehr), da diese in diesem QSS/Fusion-Setup nicht als "+"/"-" gerendert
        werden, sondern als leere schwarze Vierecke. Die Felder werden dadurch
        zu ganz normalen Eingabefeldern, in die der Wert direkt eingetippt
        wird. Muss nach jedem Neuaufbau von Widgets (z.B. Template-Tabs)
        erneut aufgerufen werden.
        """
        for sb in self.findChildren(QAbstractSpinBox):
            sb.setButtonSymbols(QAbstractSpinBox.NoButtons)   

    # ==========================================
    # 1. TOP BAR: SERVICE CONTROL & TWS SENSOR
    # ==========================================
    def create_top_service_bar(self):
            layout = QHBoxLayout()

            # Titel
            title = QLabel("<b>MN TRADING BOT MANAGER</b>")
            title.setFont(QFont("Space Grotesk", 13, QFont.Bold))
            layout.addWidget(title)

            layout.addStretch()

            # TWS Status Sensor Anzeige
            # NEU
            self.lbl_tws_status = QLabel("TWS Status: Prüfe...")
            self.lbl_tws_status.setObjectName("sensorBadge")
            self._style_status_badge(self.lbl_tws_status, "checking")
            layout.addWidget(self.lbl_tws_status)

            # Service Status Anzeige
            self.lbl_service_status = QLabel("Dienst: 🟡 Prüfe...")
            self.lbl_service_status.setFont(QFont("Inter", 10, QFont.Bold))
            layout.addWidget(self.lbl_service_status)

            # Service Control Buttons
            btn_start = QPushButton("▶ Start")
            btn_start.setObjectName("btn_success")
            btn_start.clicked.connect(lambda: self.control_service("start"))

            btn_stop = QPushButton("⏹ Stop")
            btn_stop.setObjectName("btn_danger")
            btn_stop.clicked.connect(lambda: self.control_service("stop"))

            btn_restart = QPushButton("🔄 Restart")
            btn_restart.clicked.connect(lambda: self.control_service("restart"))

            layout.addWidget(btn_start)
            layout.addWidget(btn_stop)
            layout.addWidget(btn_restart)

            # Light/Dark Mode Toggle Switch
            #self.btn_theme_toggle = QPushButton("☀️ Light Mode")
            #self.btn_theme_toggle.setCheckable(True)
            #self.btn_theme_toggle.toggled.connect(self.toggle_theme)
            #layout.addWidget(self.btn_theme_toggle)

            return layout

    def is_tws_logged_in(self, host="127.0.0.1", port=7497, timeout=1.5):
            """
            Prüft mit ib_insync/ib_async, ob TWS/Gateway wirklich verbunden und handelsbereit ist[cite: 3].
            Erkennt zuverlässig den Sperr-/Lesemodus nach einer Zweitgeräte-Anmeldung[cite: 3].
            """
            ib = IB()
            try:
                # Reservierte Client-ID nur für Statuschecks (z.B. 998)
                ib.connect(host, int(port), clientId=998, timeout=timeout)
                is_conn = ib.isConnected()
                ib.disconnect()
                return is_conn
            except Exception:
                if ib.isConnected():
                    ib.disconnect()
                return False

    def check_tws_status(self):
        """
        Wird alle 5 Sekunden vom QTimer aufgerufen
        """
        host = self.broker_data.get("IB_HOST", "127.0.0.1")
        use_paper = self.broker_data.get("USE_PAPER_TRADING", True)
        port = self.broker_data.get("IB_PORT_PAPER", 7498) if use_paper else self.broker_data.get("IB_PORT_LIVE", 7497)
        mode_str = "Paper" if use_paper else "Live"

        connected = self.is_tws_logged_in(host=host, port=port)
        self._tws_connected = connected

        if connected:
            self.lbl_tws_status.setText(f"TWS Status: Connected ({mode_str})")
            self._style_status_badge(self.lbl_tws_status, "connected")
        else:
            self.lbl_tws_status.setText(f"TWS Status: Disconnected ({mode_str})")
            self._style_status_badge(self.lbl_tws_status, "disconnected")
            self.check_telegram_alert_on_disconnect(mode_str)


    def check_telegram_alert_on_disconnect(self, mode_str):
        now = datetime.now()
        one_hour_later = now + timedelta(hours=1)
        has_upcoming = False

        # Sicherstellen, dass wir eine Liste durchlaufen
        schedules_list = self.schedules_data if isinstance(self.schedules_data, list) else self.schedules_data.get("schedules", [])

        for sched in schedules_list:
            will_run, _ = self._compute_schedule_today_status(sched)
            if will_run:
                time_str = sched.get("EXECUTION_TIME", "00:00:00")
                try:
                    t = datetime.strptime(time_str, "%H:%M:%S").time()
                    sched_dt = datetime.combine(now.date(), t)
                    
                    # Falls die Zeit heute schon verstrichen ist, auf morgen schieben
                    if sched_dt < now - timedelta(minutes=5):
                        sched_dt += timedelta(days=1)

                    if now <= sched_dt <= one_hour_later:
                        has_upcoming = True
                        break
                except Exception:
                    pass

        if has_upcoming:
            # Re-Notification Limit: maximal alle 15 Minuten senden
            if self.last_telegram_alert_time is None or (now - self.last_telegram_alert_time) > timedelta(minutes=15):
                self.send_telegram_alert(f"⚠️ **WARNUNG:** TWS ist DISCONNECTED ({mode_str})!\nEin geplanter Schedule startet innerhalb der nächsten Stunde!")
                self.last_telegram_alert_time = now

        if has_upcoming:
            # Re-Notification Limit: maximal alle 15 Minuten senden
            if self.last_telegram_alert_time is None or (now - self.last_telegram_alert_time) > timedelta(minutes=15):
                self.send_telegram_alert(f"⚠️ **WARNUNG:** TWS ist DISCONNECTED ({mode_str})!\nEin geplanter Schedule startet innerhalb der nächsten Stunde!")
                self.last_telegram_alert_time = now
                     
    def send_telegram_alert(self, text):
        if not self.telegram_data.get("TELEGRAM_ENABLED", False):
            return

        token = self.telegram_data.get("TELEGRAM_BOT_TOKEN", "").strip()
        chat_id = self.telegram_data.get("TELEGRAM_CHAT_ID", "").strip()

        if not chat_id:
            print("Telegram enabled but chat_id missing")
            return

        if not token:
            print("Telegram notifications enabled but bot_token not configured.")
            return

        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
            }

            response = requests.post(url, data=data, timeout=5)

            if response.status_code == 200:
                print("✅ Telegram notification sent")
            else:
                print(f"Telegram API returned status {response.status_code}")

        except Exception as e:
            print(f"Fehler beim Senden der Telegram-Benachrichtigung: {e}")            

    def update_service_status(self):
        try:
            output = subprocess.check_output(f'sc query "{SERVICE_NAME}"', shell=True, text=True)
            if "RUNNING" in output:
                self.lbl_service_status.setText("Dienst: 🟢 LÄUFT")
            else:
                self.lbl_service_status.setText("Dienst: 🔴 GESTOPPT")
        except Exception:
            self.lbl_service_status.setText("Dienst: ⚠️ NICHT GEFUNDEN")

    def control_service(self, action):
        cmd = f'net {action} "{SERVICE_NAME}"' if action in ["start", "stop"] else f'net stop "{SERVICE_NAME}" & net start "{SERVICE_NAME}"'
        subprocess.run(cmd, shell=True)
        self.update_service_status()

    # ==========================================
    # 2. DASHBOARD
    # ==========================================
    def create_dashboard_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        splitter = QSplitter(Qt.Vertical)

        # OBEN: Heute geplant (nur was wirklich heute läuft)
        today_box = QGroupBox("📅 Heute geplant")
        today_layout = QVBoxLayout(today_box)

        self.today_table = QTableWidget(0, 4)
        self.today_table.setHorizontalHeaderLabels(["Name", "Ausführungszeit", "Template", "Status heute"])
        self.today_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.today_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.today_table.setCornerButtonEnabled(False)
        self.today_table.setAlternatingRowColors(True)
        self.today_table.setFocusPolicy(Qt.NoFocus)
        
        today_layout.addWidget(self.today_table)

        # UNTEN: Aktive Schedules
        top_box = QGroupBox("Definierte Schedules")
        top_layout = QVBoxLayout(top_box)

        action_bar = QHBoxLayout()
        btn_add = QPushButton("➕ Neues Schedule")
        btn_add.setObjectName("btn_accent")
        btn_add.clicked.connect(self.add_new_schedule)

        btn_edit = QPushButton("✏️ Schedule bearbeiten")
        btn_edit.clicked.connect(self.edit_selected_schedule)

        btn_del = QPushButton("🗑️ Schedule löschen")
        btn_del.setObjectName("btn_danger")
        btn_del.clicked.connect(self.delete_selected_schedule)

        btn_export = QPushButton("⬇ Export")
        btn_export.clicked.connect(self.export_schedules)

        btn_import = QPushButton("⬆ Import")
        btn_import.clicked.connect(self.import_schedules)

        action_bar.addWidget(btn_add)
        action_bar.addWidget(btn_edit)
        action_bar.addWidget(btn_del)
        action_bar.addWidget(btn_export)
        action_bar.addWidget(btn_import)
        action_bar.addStretch()

        action_bar.addWidget(btn_add)
        action_bar.addWidget(btn_edit)
        action_bar.addWidget(btn_del)
        action_bar.addStretch()

        self.sched_table = QTableWidget(0, 7)
        self.sched_table.setHorizontalHeaderLabels([
            "Name", "Template Ref", "Zeit", "Status", "Instant Trade", "Test Trade (LMT)", "Preview Trade"
        ])

        # Spalten 0-3 strecken sich mit dem Fenster, die drei Action-Button-
        # Spalten bekommen eine feste Mindestbreite – sonst werden
        # "Test Trade (LMT)" / "Preview Trade" bei kleineren Fenstern
        # abgeschnitten dargestellt (z.B. "lact", "Draviaw").
        header = self.sched_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        for col in (4, 5, 6):
            header.setSectionResizeMode(col, QHeaderView.Fixed)
            self.sched_table.setColumnWidth(col, 140)

        # Höhere Zeilen, damit die Buttons nicht vertikal abgeschnitten werden.
        self.sched_table.verticalHeader().setDefaultSectionSize(42)

        self.sched_table.setCornerButtonEnabled(False)
        self.sched_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.sched_table.setAlternatingRowColors(True)
        self.sched_table.setFocusPolicy(Qt.NoFocus)

        top_layout.addLayout(action_bar)
        top_layout.addWidget(self.sched_table)

        splitter.addWidget(today_box)
        splitter.addWidget(top_box)
        layout.addWidget(splitter)

        self.refresh_schedules_table()
        return widget

    def edit_selected_schedule(self):
        row = self.sched_table.currentRow()
        if row >= 0:
            self.on_schedule_selected(row)
            self.main_tabs.setCurrentIndex(1)
        else:
            QMessageBox.warning(self, "Hinweis", "Bitte wähle ein Schedule aus der Tabelle aus!")

    # ==========================================
    # SCHEDULE EDITOR TAB
    # ==========================================
    def create_schedule_editor_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.editor_box = QGroupBox("Schedule-Editor (Kein Schedule ausgewählt - Unter Dashboard ein definiertes Schedule auswählen und dann auf 'Schedule bearbeiten' klicken)")
        self.init_schedule_editor_form()

        layout.addWidget(self.editor_box)
        layout.addStretch()
        return widget

    def _make_toggle_switch(self, checked: bool, on_text: str = "Aktiv", off_text: str = "Inaktiv", object_name: str = "toggleSwitch") -> QCheckBox:
        cb = QCheckBox(on_text if checked else off_text)
        cb.setObjectName(object_name)
        cb.setChecked(checked)
        cb.stateChanged.connect(lambda _s, c=cb, on=on_text, off=off_text: c.setText(on if c.isChecked() else off))
        return cb
        
    def _make_password_field(self, text: str) -> QWidget:
        """
        Passwort-Eingabefeld mit Augen-Symbol zum Ein-/Ausblenden.
        Das eigentliche QLineEdit ist über container.line_edit erreichbar,
        damit bestehender Code (z.B. self.cfg_tg_token.text()) unverändert bleibt.
        """
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        line_edit = QLineEdit(text)
        line_edit.setEchoMode(QLineEdit.Password)

        btn_toggle = QPushButton("👁")
        btn_toggle.setCheckable(True)
        btn_toggle.setFixedWidth(32)
        btn_toggle.setToolTip("Bot Token anzeigen/verbergen")

        def _toggle_visibility(checked):
            line_edit.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)
            btn_toggle.setText("Show" if checked else "Hide")

        btn_toggle.toggled.connect(_toggle_visibility)

        layout.addWidget(line_edit)
        layout.addWidget(btn_toggle)

        container.line_edit = line_edit
        return container        

    def init_schedule_editor_form(self):
        main_layout = QVBoxLayout(self.editor_box)

        # ==========================================
        # 1. Schedule Details
        # ==========================================
        grp_details = QGroupBox("Schedule Details")
        f_details = QFormLayout(grp_details)
        f_details.setLabelAlignment(Qt.AlignLeft)

        self.edit_name = QLineEdit()
        self.edit_template = QComboBox()

        qty_widget = QWidget()
        qty_layout = QHBoxLayout(qty_widget)
        qty_layout.setContentsMargins(0, 0, 0, 0)

        self.edit_mode = QComboBox()
        self.edit_mode.addItems(["FixedQty"])
        self.edit_qty = QSpinBox()
        self.edit_qty.setRange(1, 1000)

        qty_layout.addWidget(self.edit_mode, 2)
        qty_layout.addWidget(QLabel("Anzahl:"), 0)
        qty_layout.addWidget(self.edit_qty, 1)

        f_details.addRow("Schedule Name:", self.edit_name)
        f_details.addRow("Trade Template:", self.edit_template)
        f_details.addRow("Quantity Selection / Qty:", qty_widget)

        # ==========================================
        # 2. Execution Timing
        # ==========================================
        grp_timing = QGroupBox("Execution Timing")
        f_timing = QFormLayout(grp_timing)
        f_timing.setLabelAlignment(Qt.AlignLeft)

        time_widget = QWidget()
        time_layout = QHBoxLayout(time_widget)
        time_layout.setContentsMargins(0, 0, 0, 0)

        self.edit_time = QTimeEdit()
        self.edit_time.setDisplayFormat("HH:mm:ss")

        # Reine Anzeige-Hilfe (AM/PM) neben der 24h-Eingabe – wird NICHT
        # mitgespeichert, EXECUTION_TIME bleibt unverändert im HH:mm:ss-Format.
        self.lbl_time_ampm = QLabel("AM")
        self.lbl_time_ampm.setStyleSheet("font-weight: 700; padding-left: 6px;")
        self.edit_time.timeChanged.connect(self._update_time_ampm_label)
        self._update_time_ampm_label(self.edit_time.time())

        time_layout.addWidget(self.edit_time)
        time_layout.addWidget(self.lbl_time_ampm)
        time_layout.addStretch()

        self.edit_expiration_minutes = QSpinBox()
        self.edit_expiration_minutes.setRange(0, 120)
        self.edit_expiration_minutes.setSuffix(" min")

        days_widget = QWidget()
        days_layout = QHBoxLayout(days_widget)
        days_layout.setContentsMargins(0, 0, 0, 0)
        days_layout.setSpacing(6)
        self.day_checkboxes = {}
        for day in ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]:
            cb = QCheckBox(day)
            self.day_checkboxes[day] = cb
            days_layout.addWidget(cb)
        days_layout.addStretch()

        self.edit_week_of_month = QComboBox()
        self.edit_week_of_month.addItems(["Jede Woche", "1. Woche", "2. Woche", "3. Woche", "4. Woche", "5. Woche"])

        f_timing.addRow("Execution Time:", time_widget)
        f_timing.addRow("Expiration Minutes:", self.edit_expiration_minutes)
        f_timing.addRow("Days to Execute:", days_widget)
        f_timing.addRow("Woche im Monat:", self.edit_week_of_month)

        # ==========================================
        # 3. Entry Conditions
        # Gleiches Muster wie "Execution / Sweep Advanced": die GroupBox selbst
        # trägt die Checkbox im Titel und schaltet ihren gesamten Inhalt frei
        # (Qt deaktiviert Kind-Widgets einer checkbaren GroupBox automatisch,
        # wenn sie unchecked ist – keine manuelle Enable/Disable-Logik nötig).
        # ==========================================
        grp_cond = QGroupBox("Entry Conditions")
        grp_cond.setCheckable(True)
        grp_cond.setChecked(False)
        f_cond = QFormLayout(grp_cond)
        f_cond.setLabelAlignment(Qt.AlignLeft)
        self.grp_entry_conditions = grp_cond

        # RSI Zeile
        rsi_widget = QWidget()
        rsi_layout = QHBoxLayout(rsi_widget)
        rsi_layout.setContentsMargins(0, 0, 0, 0)
        self.chk_rsi = self._make_toggle_switch(False)
        self.spin_rsi_period = QSpinBox()
        self.spin_rsi_period.setRange(1, 200)
        self.spin_rsi_min = QSpinBox()
        self.spin_rsi_min.setRange(0, 100)
        self.spin_rsi_max = QSpinBox()
        self.spin_rsi_max.setRange(0, 100)

        rsi_layout.addWidget(self.chk_rsi)
        rsi_layout.addWidget(QLabel("Periode:"))
        rsi_layout.addWidget(self.spin_rsi_period)
        rsi_layout.addWidget(QLabel("Min:"))
        rsi_layout.addWidget(self.spin_rsi_min)
        rsi_layout.addWidget(QLabel("Max:"))
        rsi_layout.addWidget(self.spin_rsi_max)

        # SMA Zeile
        sma_widget = QWidget()
        sma_layout = QHBoxLayout(sma_widget)
        sma_layout.setContentsMargins(0, 0, 0, 0)
        self.chk_sma = self._make_toggle_switch(False)
        self.spin_sma_period = QSpinBox()
        self.spin_sma_period.setRange(1, 200)
        sma_layout.addWidget(self.chk_sma)
        sma_layout.addWidget(QLabel("Periode:"))
        sma_layout.addWidget(self.spin_sma_period)
        sma_layout.addStretch()

        # Intraday Zeile
        intraday_widget = QWidget()
        intraday_layout = QHBoxLayout(intraday_widget)
        intraday_layout.setContentsMargins(0, 0, 0, 0)
        self.chk_intraday = self._make_toggle_switch(False)
        self.spin_intraday_pct = QDoubleSpinBox()
        self.spin_intraday_pct.setRange(-100.0, 100.0)
        self.spin_intraday_pct.setSingleStep(0.05)
        self.spin_intraday_pct.setSuffix(" %")
        intraday_layout.addWidget(self.chk_intraday)
        intraday_layout.addWidget(QLabel("Min %:"))
        intraday_layout.addWidget(self.spin_intraday_pct)
        intraday_layout.addStretch()

        # Reihenfolge (Drag & Drop) -> bestimmt ORDER für RSI/ABOVE_SMA/INTRADAY_MOVE
        # (ab 2). WEEKDAY_FILTER ist immer fest ORDER=1 und wird hier nicht gelistet.
        self.cond_order_list = QListWidget()
        self.cond_order_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.cond_order_list.setDefaultDropAction(Qt.MoveAction)
        self.cond_order_list.setFixedHeight(90)
        self.cond_order_list.setToolTip(
            "Reihenfolge per Drag & Drop ändern – bestimmt ORDER (ab 2). "
            "WEEKDAY_FILTER läuft unabhängig davon immer zuerst (ORDER 1)."
        )
        self._populate_condition_order_list({"RSI": 2, "ABOVE_SMA": 3, "INTRADAY_MOVE": 4})

        f_cond.addRow("RSI Condition:", rsi_widget)
        f_cond.addRow("Preis über SMA:", sma_widget)
        f_cond.addRow("Intraday Move:", intraday_widget)
        f_cond.addRow("Reihenfolge (Drag Drop):", self.cond_order_list)

        # ==========================================
        # 4. Execution Advanced
        # ==========================================
        grp_adv = QGroupBox("Execution Advanced")
        f_adv = QFormLayout(grp_adv)
        f_adv.setLabelAlignment(Qt.AlignLeft)

        self.edit_ramp_up = QTimeEdit()
        self.edit_ramp_up.setDisplayFormat("HH:mm:ss")

        self.edit_max_runtime = QSpinBox()
        self.edit_max_runtime.setRange(0, 1440)
        self.edit_max_runtime.setSuffix(" min")

        f_adv.addRow("Ramp Up Time:", self.edit_ramp_up)
        f_adv.addRow("Max Runtime:", self.edit_max_runtime)

        # ==========================================
        # 5. Status
        # ==========================================
        grp_status = QGroupBox("Status")
        f_status = QFormLayout(grp_status)
        f_status.setLabelAlignment(Qt.AlignLeft)
        self.edit_disabled = self._make_toggle_switch(True)
        f_status.addRow("Schedule:", self.edit_disabled)

        # Main Layout zusammenbauen
        main_layout.addWidget(grp_details)
        main_layout.addWidget(grp_timing)
        main_layout.addWidget(grp_cond)
        main_layout.addWidget(grp_adv)
        main_layout.addWidget(grp_status)

        btn_save = QPushButton("💾 Speichern")
        btn_save.setObjectName("btn_success")
        btn_save.clicked.connect(self.save_schedules)
        main_layout.addWidget(btn_save)
        
    def _update_time_ampm_label(self, qtime: QTime):
        """Aktualisiert nur die AM/PM-Anzeige neben Execution Time.
        Rein visuell – EXECUTION_TIME wird weiterhin als HH:mm:ss (24h) gespeichert."""
        if hasattr(self, "lbl_time_ampm"):
            self.lbl_time_ampm.setText("PM" if qtime.hour() >= 12 else "AM")        
        
    def _populate_condition_order_list(self, order_values: dict):
        """Füllt self.cond_order_list sortiert nach ORDER-Werten
        (nur RSI/ABOVE_SMA/INTRADAY_MOVE; WEEKDAY_FILTER läuft separat mit ORDER=1)."""
        labels = {
            "RSI": "RSI",
            "ABOVE_SMA": "Preis über SMA",
            "INTRADAY_MOVE": "Intraday Move",
        }
        ordered_keys = sorted(order_values.keys(), key=lambda k: order_values[k])

        self.cond_order_list.clear()
        for key in ordered_keys:
            item = QListWidgetItem(labels.get(key, key))
            item.setData(Qt.UserRole, key)
            self.cond_order_list.addItem(item)        
        

    def refresh_schedules_table(self):
        schedules = self.schedules_data
        self.sched_table.setRowCount(len(schedules))

        for row, s in enumerate(schedules):
            self.sched_table.setItem(row, 0, QTableWidgetItem(s.get("NAME", "")))
            self.sched_table.setItem(row, 1, QTableWidgetItem(s.get("TRADETEMPLATE", s.get("NAME", ""))))
            self.sched_table.setItem(row, 2, QTableWidgetItem(s.get("EXECUTION_TIME", "00:00:00")))

            disabled = s.get("DISABLED", False)
            status_item = QTableWidgetItem("🔴 Deaktiviert" if disabled else "🟢 Aktiv")
            self.sched_table.setItem(row, 3, status_item)

            btn_instant = QPushButton("🔒 Instant")
            btn_instant.setObjectName("btn_locked")
            btn_instant.setEnabled(False)
            btn_instant.setMinimumSize(120, 30)
            btn_instant.setToolTip("Instant Trade – kommt in einer zukünftigen Version")

            btn_test = QPushButton("🔒 Test")
            btn_test.setObjectName("btn_locked")
            btn_test.setEnabled(False)
            btn_test.setMinimumSize(120, 30)
            btn_test.setToolTip("Test Trade (LMT) – kommt in einer zukünftigen Version")

            btn_preview = QPushButton("🔒 Preview")
            btn_preview.setObjectName("btn_locked")
            btn_preview.setEnabled(False)
            btn_preview.setMinimumSize(120, 30)
            btn_preview.setToolTip("Preview Trade – kommt in einer zukünftigen Version")

            self.sched_table.setCellWidget(row, 4, btn_instant)
            self.sched_table.setCellWidget(row, 5, btn_test)
            self.sched_table.setCellWidget(row, 6, btn_preview)

        self.refresh_today_preview()

    def _compute_schedule_today_status(self, sched: dict):
        if sched.get("DISABLED", False):
            return False, "Deaktiviert"

        try:
            now_et = datetime.now(pytz.timezone("America/New_York"))
        except Exception:
            now_et = datetime.now()

        weekday_filter = sched.get("ENTRY_CONDITIONS", {}).get("WEEKDAY_FILTER", {})
        configured_days = [d.upper() for d in weekday_filter.get("DAYS", [])]
        today_full = now_et.strftime("%A").upper()

        if configured_days:
            if today_full not in configured_days:
                return False, f"Nicht {today_full.capitalize()}"
        elif now_et.weekday() >= 5:
            return False, "Wochenende"

        week_of_month = weekday_filter.get("WEEK_OF_MONTH")
        if week_of_month:
            current_week = ((now_et.day - 1) // 7) + 1
            if int(week_of_month) != current_week:
                return False, f"Nicht Woche {week_of_month}"

        return True, "Wird laufen"

    def refresh_today_preview(self):
        today_schedules = []
        try:
            now_et = datetime.now(pytz.timezone("America/New_York"))
        except Exception:
            now_et = datetime.now()

        current_time_str = now_et.strftime("%H:%M:%S")

        for s in self.schedules_data:
            will_run, reason = self._compute_schedule_today_status(s)
            if will_run:
                exec_time = s.get("EXECUTION_TIME", "00:00:00")

                # Prüfen, ob die Zeit für heute bereits verstrichen ist
                if exec_time < current_time_str:
                    status = "🔴 Schon gelaufen / Expired"
                else:
                    status = f"🟢 {reason}"

                today_schedules.append((s.get("NAME", ""), exec_time, s.get("TRADETEMPLATE", ""), status))

        today_schedules.sort(key=lambda r: r[1])

        # Theme-abhängige Akzentfarben (identisch zu DARK_THEME/LIGHT_THEME oben)
        expired_color = "#f6465d" if self.is_dark_theme else "#f04438"   # Danger-Rot
        pending_color = "#16c784" if self.is_dark_theme else "#099250"  # Erfolg-Grün

        self.today_table.setRowCount(len(today_schedules))
        for row, (name, time_str, tmpl, status) in enumerate(today_schedules):
            self.today_table.setItem(row, 0, QTableWidgetItem(name))
            self.today_table.setItem(row, 1, QTableWidgetItem(time_str))
            self.today_table.setItem(row, 2, QTableWidgetItem(tmpl))

            status_item = QTableWidgetItem(status)
            if "Expired" in status:
                status_item.setForeground(QColor(expired_color))
            else:
                status_item.setForeground(QColor(pending_color))
            self.today_table.setItem(row, 3, status_item)

    def on_schedule_selected(self, row):
        schedules = self.schedules_data
        if row < 0 or row >= len(schedules):
            return

        sched = schedules[row]
        self.editor_box.setTitle(f"Schedule-Editor: {sched.get('NAME')}")
        self.edit_name.setText(sched.get("NAME", ""))

        self.edit_template.clear()
        templates = [t.get("TEMPLATENAME", t.get("TRADE_TYPE", "")) for t in self.templates_data]
        self.edit_template.addItems(templates)
        self.edit_template.setCurrentText(sched.get("TRADETEMPLATE", ""))

        time_str = sched.get("EXECUTION_TIME", "00:00:00")
        self.edit_time.setTime(QTime.fromString(time_str, "hh:mm:ss"))
        self._update_time_ampm_label(self.edit_time.time())

        ramp_up_str = sched.get("RAMP_UP_TIME", "00:01:00")
        self.edit_ramp_up.setTime(QTime.fromString(ramp_up_str, "hh:mm:ss"))

        self.edit_max_runtime.setValue(int(sched.get("MAX_RUNTIME_MINUTES", 10)))
        self.edit_expiration_minutes.setValue(int(sched.get("EXPIRATION_MINUTES", 5)))

        self.edit_disabled.setChecked(not sched.get("DISABLED", False))

        qty_cfg = sched.get("QUANTITY", {})
        self.edit_mode.setCurrentText(qty_cfg.get("MODE", "FixedQty"))
        self.edit_qty.setValue(int(qty_cfg.get("QTY", 1)))

        entry_conditions = sched.get("ENTRY_CONDITIONS", {})
        weekday_filter = entry_conditions.get("WEEKDAY_FILTER", {})

        days_upper = [d.upper() for d in weekday_filter.get("DAYS", [])]
        for abbr, cb in self.day_checkboxes.items():
            cb.setChecked(DAY_ABBR_TO_FULL[abbr] in days_upper)

        week_of_month = weekday_filter.get("WEEK_OF_MONTH")
        self.edit_week_of_month.setCurrentIndex(int(week_of_month) if week_of_month else 0)

        has_conds = any(k in entry_conditions for k in ["RSI", "ABOVE_SMA", "INTRADAY_MOVE"])
        self.grp_entry_conditions.setChecked(has_conds)

        rsi_cfg = entry_conditions.get("RSI")
        self.chk_rsi.setChecked(rsi_cfg is not None)
        self.spin_rsi_period.setValue(int((rsi_cfg or {}).get("PERIOD", 14)))
        self.spin_rsi_min.setValue(int((rsi_cfg or {}).get("MIN", 50)))
        self.spin_rsi_max.setValue(int((rsi_cfg or {}).get("MAX", 75)))

        sma_cfg = entry_conditions.get("ABOVE_SMA")
        self.chk_sma.setChecked(sma_cfg is not None)
        self.spin_sma_period.setValue(int((sma_cfg or {}).get("PERIOD", 5)))

        intraday_cfg = entry_conditions.get("INTRADAY_MOVE")
        self.chk_intraday.setChecked(intraday_cfg is not None)
        self.spin_intraday_pct.setValue(float((intraday_cfg or {}).get("MIN_PCT", 0.3)))

        # Reihenfolge (ORDER) aus den Conditions übernehmen, Default 2/3/4 wenn
        # noch nicht gesetzt. WEEKDAY_FILTER (ORDER=1) läuft separat, nicht gelistet.
        order_defaults = {"RSI": 2, "ABOVE_SMA": 3, "INTRADAY_MOVE": 4}
        order_values = {
            key: int((entry_conditions.get(key) or {}).get("ORDER", order_defaults[key]))
            for key in order_defaults
        }
        self._populate_condition_order_list(order_values)

    def add_new_schedule(self):
        new_sched = {
            "NAME": f"NEW-SCHEDULE-{len(self.schedules_data) + 1}",
            "DISABLED": False,
            "EXECUTION_TIME": "12:00:00",
            "RAMP_UP_TIME": "00:01:00",
            "MAX_RUNTIME_MINUTES": 10,
            "EXPIRATION_MINUTES": 5,
            "TRADETEMPLATE": "",
            "QUANTITY": {"MODE": "FixedQty", "QTY": 1},
            "ENTRY_CONDITIONS": {},
        }
        self.schedules_data.append(new_sched)
        self.refresh_schedules_table()
        self.on_schedule_selected(len(self.schedules_data) - 1)
        self.main_tabs.setCurrentIndex(1)

    def delete_selected_schedule(self):
        row = self.sched_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Hinweis", "Bitte wähle ein Schedule aus der Tabelle aus!")
            return

        sched_name = self.schedules_data[row].get("NAME", f"Schedule {row + 1}")
        reply = QMessageBox.question(
            self,
            "Schedule löschen",
            f"Schedule '{sched_name}' wirklich löschen?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        del self.schedules_data[row]
        save_json(SCHEDULES_FILE, self.schedules_data)
        self.refresh_schedules_table()

    def export_schedules(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Schedules exportieren", str(SCHEDULES_FILE.name), "JSON Dateien (*.json)"
        )
        if not path:
            return
        try:
            save_json(Path(path), self.schedules_data)
            QMessageBox.information(self, "Export", f"Schedules exportiert nach:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export fehlgeschlagen", f"Fehler beim Exportieren:\n{e}")

    def import_schedules(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Schedules importieren", "", "JSON Dateien (*.json)"
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Import fehlgeschlagen", f"Datei konnte nicht gelesen werden:\n{e}")
            return

        if isinstance(data, dict):
            data = data.get("schedules", [])

        if not isinstance(data, list):
            QMessageBox.critical(self, "Import fehlgeschlagen", "Die Datei enthält keine gültige Schedule-Liste.")
            return

        reply = QMessageBox.question(
            self,
            "Schedules importieren",
            f"{len(data)} Schedule(s) in der Datei gefunden.\n"
            f"Die aktuell geladenen {len(self.schedules_data)} Schedule(s) wirklich überschreiben?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        self.schedules_data = data
        save_json(SCHEDULES_FILE, self.schedules_data)
        self.refresh_schedules_table()
        QMessageBox.information(self, "Import", f"{len(data)} Schedule(s) importiert.")

    def save_schedules(self):
        row = self.sched_table.currentRow()
        if row >= 0 and row < len(self.schedules_data):
            sched = self.schedules_data[row]
            sched["NAME"] = self.edit_name.text()
            sched["TRADETEMPLATE"] = self.edit_template.currentText()
            sched["EXECUTION_TIME"] = self.edit_time.time().toString("hh:mm:ss")
            sched["RAMP_UP_TIME"] = self.edit_ramp_up.time().toString("hh:mm:ss")
            sched["MAX_RUNTIME_MINUTES"] = self.edit_max_runtime.value()
            sched["EXPIRATION_MINUTES"] = self.edit_expiration_minutes.value()
            sched["DISABLED"] = not self.edit_disabled.isChecked()
            sched["QUANTITY"] = {
                "MODE": self.edit_mode.currentText(),
                "QTY": self.edit_qty.value()
            }

            entry_conditions = sched.get("ENTRY_CONDITIONS", {})

            selected_days = [DAY_ABBR_TO_FULL[abbr] for abbr, cb in self.day_checkboxes.items() if cb.isChecked()]
            weekday_filter = entry_conditions.get("WEEKDAY_FILTER", {})
            weekday_filter["DAYS"] = selected_days
            # WEEKDAY_FILTER läuft immer zuerst, nicht über die UI-Reihenfolge editierbar
            weekday_filter["ORDER"] = 1

            week_idx = self.edit_week_of_month.currentIndex()
            if week_idx > 0:
                weekday_filter["WEEK_OF_MONTH"] = week_idx
            else:
                weekday_filter.pop("WEEK_OF_MONTH", None)
            entry_conditions["WEEKDAY_FILTER"] = weekday_filter

            if self.grp_entry_conditions.isChecked():
                if self.chk_rsi.isChecked():
                    entry_conditions["RSI"] = {
                        "PERIOD": self.spin_rsi_period.value(),
                        "MIN": self.spin_rsi_min.value(),
                        "MAX": self.spin_rsi_max.value()
                    }
                else:
                    entry_conditions.pop("RSI", None)

                if self.chk_sma.isChecked():
                    entry_conditions["ABOVE_SMA"] = {"PERIOD": self.spin_sma_period.value()}
                else:
                    entry_conditions.pop("ABOVE_SMA", None)

                if self.chk_intraday.isChecked():
                    entry_conditions["INTRADAY_MOVE"] = {"MIN_PCT": self.spin_intraday_pct.value()}
                else:
                    entry_conditions.pop("INTRADAY_MOVE", None)
            else:
                entry_conditions.pop("RSI", None)
                entry_conditions.pop("ABOVE_SMA", None)
                entry_conditions.pop("INTRADAY_MOVE", None)

            # Reihenfolge (ORDER) aus der Drag&Drop-Liste übernehmen (ab 2).
            # Nur für Conditions, die tatsächlich aktiv/vorhanden sind.
            for pos in range(self.cond_order_list.count()):
                key = self.cond_order_list.item(pos).data(Qt.UserRole)
                if key in entry_conditions:
                    entry_conditions[key]["ORDER"] = pos + 2

            sched["ENTRY_CONDITIONS"] = entry_conditions

        save_json(SCHEDULES_FILE, self.schedules_data)
        self.refresh_schedules_table()
        QMessageBox.information(self, "Speichern", "Schedule wurde erfolgreich gespeichert!")

    # ==========================================
    # 3. TRADE TEMPLATES
    # ==========================================
    def create_templates_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        tmpl_bar = QHBoxLayout()
        btn_add_tmpl = QPushButton("➕ Neues Template")
        btn_add_tmpl.setObjectName("btn_accent")
        btn_add_tmpl.clicked.connect(self.add_new_template)

        btn_del_tmpl = QPushButton("🗑️ Template löschen")
        btn_del_tmpl.setObjectName("btn_danger")
        btn_del_tmpl.clicked.connect(self.delete_current_template)

        btn_export_tmpl = QPushButton("⬇ Export")
        btn_export_tmpl.clicked.connect(self.export_templates)

        btn_import_tmpl = QPushButton("⬆ Import")
        btn_import_tmpl.clicked.connect(self.import_templates)

        btn_save = QPushButton("💾 Speichern")
        btn_save.setObjectName("btn_success")
        btn_save.clicked.connect(self.save_templates)

        tmpl_bar.addWidget(btn_add_tmpl)
        tmpl_bar.addWidget(btn_del_tmpl)
        tmpl_bar.addWidget(btn_export_tmpl)
        tmpl_bar.addWidget(btn_import_tmpl)
        tmpl_bar.addStretch()
        tmpl_bar.addWidget(btn_save)

        self.template_tabs = QTabWidget()
        self.build_template_tabs()

        layout.addLayout(tmpl_bar)
        layout.addWidget(self.template_tabs)
        return widget

    def build_template_tabs(self):
        self.template_tabs.clear()
        self.template_matrix_tables = {}
        self.template_iv_override_checks = {}
        templates = self.templates_data

        for idx, tmpl in enumerate(templates):
            name = tmpl.get("TEMPLATENAME", tmpl.get("TRADE_TYPE", f"Template {idx+1}"))
            tab_widget = QScrollArea()
            tab_widget.setWidgetResizable(True)

            content = QWidget()
            form = QFormLayout(content)

            t_name = QLineEdit(name)
            t_name.textChanged.connect(lambda text, i=idx: self.update_template_name(i, text))

            t_type = QComboBox()
            t_type.setEditable(True)
            t_type.addItems(["BULL_PUT", "PBW", "IRON_CONDOR"])
            current_type = tmpl.get("TRADE_TYPE", "")
            if current_type and t_type.findText(current_type) == -1:
                # Bestehende/legacy Werte (z.B. "PUT_BROKEN_WING", "RUT_IRON_CONDOR")
                # nicht stillschweigend überschreiben, sondern als Option ergänzen.
                t_type.addItem(current_type)
            t_type.setCurrentText(current_type)
            t_type.currentTextChanged.connect(lambda text, i=idx: self.update_template_val(i, "TRADE_TYPE", text))
            # Nur bei expliziter Auswahl/Bestätigung (nicht bei jedem Tastendruck
            # im editierbaren Feld) neu aufbauen, damit Leg3/Leg4 sofort korrekt
            # erscheinen/verschwinden.
            t_type.activated.connect(lambda _idx: self._rebuild_template_tabs_keep_index())

            symbol = QComboBox()
            symbol.setEditable(True)
            symbol.addItems(["SPX", "RUT", "NDX"])
            current_symbol = tmpl.get("SYMBOL", "")
            if current_symbol and symbol.findText(current_symbol) == -1:
                symbol.addItem(current_symbol)
            symbol.setCurrentText(current_symbol)
            symbol.currentTextChanged.connect(lambda text, i=idx: self.update_template_val(i, "SYMBOL", text))

            commission = QDoubleSpinBox()
            commission.setRange(0, 50)
            commission.setValue(float(tmpl.get("COMMISSION_PER_CONTRACT", 1.50)))
            commission.valueChanged.connect(lambda val, i=idx: self.update_template_val(i, "COMMISSION_PER_CONTRACT", val))

            form.addRow("Template Name:", t_name)
            form.addRow("Trade Type:", t_type)
            form.addRow("Underlying Symbol:", symbol)
            form.addRow("Commission / Contract ($):", commission)

            # __SECTION__LEG_DEFINITION – direkt nach Commission, gilt für alle
            # TradeTypes (Bull Put nutzt genau Leg1/Leg2, PBW/Iron Condor bauen
            # mit LEG3/LEG4 – aktuell nicht im GUI editierbar – darauf auf).
            form.addRow(self._build_leg_definition_box(idx, tmpl))

            advanced_box = QGroupBox("Execution / Sweep Advanced")
            advanced_box.setCheckable(True)
            advanced_box.setChecked(False)
            advanced_form = QFormLayout(advanced_box)

            min_sweep = QDoubleSpinBox()
            min_sweep.setRange(-1000, 1000)
            min_sweep.setValue(float(tmpl.get("MIN_SWEEP_PRICE", -5.0)))
            min_sweep.valueChanged.connect(lambda val, i=idx: self.update_template_val(i, "MIN_SWEEP_PRICE", val))

            max_sweep = QDoubleSpinBox()
            max_sweep.setRange(-1000, 1000)
            max_sweep.setValue(float(tmpl.get("MAX_SWEEP_PRICE", -1.0)))
            max_sweep.valueChanged.connect(lambda val, i=idx: self.update_template_val(i, "MAX_SWEEP_PRICE", val))

            max_attempts = QSpinBox()
            max_attempts.setRange(1, 500)
            max_attempts.setValue(int(tmpl.get("MAX_SWEEP_ATTEMPTS", 40)))
            max_attempts.valueChanged.connect(lambda val, i=idx: self.update_template_val(i, "MAX_SWEEP_ATTEMPTS", val))

            wait_seconds = QSpinBox()
            wait_seconds.setRange(1, 120)
            wait_seconds.setSuffix(" s")
            wait_seconds.setValue(int(tmpl.get("SWEEP_WAIT_SECONDS", 5)))
            wait_seconds.valueChanged.connect(lambda val, i=idx: self.update_template_val(i, "SWEEP_WAIT_SECONDS", val))

            sweep_step = QDoubleSpinBox()
            sweep_step.setRange(0.01, 5.0)
            sweep_step.setSingleStep(0.01)
            sweep_step.setDecimals(2)
            sweep_step.setValue(float(tmpl.get("SWEEP_STEP", 0.05)))
            sweep_step.valueChanged.connect(lambda val, i=idx: self.update_template_val(i, "SWEEP_STEP", val))

            start_quantile = QDoubleSpinBox()
            start_quantile.setRange(0.0, 1.0)
            start_quantile.setSingleStep(0.05)
            start_quantile.setDecimals(2)
            start_quantile.setValue(float(tmpl.get("START_SWEEP_QUANTILE", 0.25)))
            start_quantile.valueChanged.connect(lambda val, i=idx: self.update_template_val(i, "START_SWEEP_QUANTILE", val))

            advanced_form.addRow("Min Sweep Price ($):", min_sweep)
            advanced_form.addRow("Max Sweep Price ($):", max_sweep)
            advanced_form.addRow("Max Sweep Attempts:", max_attempts)
            advanced_form.addRow("Sweep Wait Seconds:", wait_seconds)
            advanced_form.addRow("Sweep Step ($):", sweep_step)
            advanced_form.addRow("Start Sweep Quantile:", start_quantile)

            form.addRow(advanced_box)

            # __SECTION__RESCAN_CONTROL – eigene Section (statt Teil von
            # Execution/Sweep Advanced), da MAX_RESCAN_ATTEMPTS von jeder
            # Strategie mit Rescan-Loop genutzt wird, nicht IC-spezifisch.
            form.addRow(self._build_rescan_control_box(idx, tmpl))

            # ==========================================================
            # NUR für Iron-Condor-Templates (z.B. RUT-IC-DELTA-SYM):
            # __SECTION__IV_RANK_STEERING + __SECTION__SPREAD_WIDTH
            # ==========================================================
            if self._is_iron_condor_template(tmpl):
                form.addRow(self._build_iv_rank_steering_box(idx, tmpl))
                form.addRow(self._build_spread_width_box(idx, tmpl))

            tab_widget.setWidget(content)
            self.template_tabs.addTab(tab_widget, name)
            
        self._apply_plus_minus_symbols()    

    def _normalize_trade_type(self, tmpl: dict) -> str:
        """Analog zu bot.py._create_trade_type: normalisiert TRADE_TYPE-Varianten
        auf 'BULL_PUT' / 'PBW' / 'IRON_CONDOR', sonst 'OTHER' (unbekannt/legacy)."""
        tt = (tmpl.get("TRADE_TYPE") or "").strip().upper()
        if tt in ("BULL_PUT", "PUT_SPREAD", "BPS"):
            return "BULL_PUT"
        if tt in ("PBW", "PUT_BROKEN_WING"):
            return "PBW"
        if tt in ("IRON_CONDOR", "RUT_IRON_CONDOR"):
            return "IRON_CONDOR"
        return "OTHER"

    def _rebuild_template_tabs_keep_index(self):
        """Baut die Template-Tabs neu auf (z.B. nach TRADE_TYPE-Wechsel) und
        springt danach zurück auf den zuvor aktiven Tab."""
        current_tab = self.template_tabs.currentIndex()
        self.build_template_tabs()
        if 0 <= current_tab < self.template_tabs.count():
            self.template_tabs.setCurrentIndex(current_tab)

    def _build_leg_row(
        self,
        idx: int,
        tmpl: dict,
        leg_num: int,
        leg_label: str,
        fixed,
        show_target: bool,
        target_default: int = 0,
        target_type_options=None,
        target_type_default: str = "",
        dte_default: int = 4,
    ) -> QWidget:
        """Baut eine komplette, kompakte Ein-Zeilen-Darstellung für ein Leg –
        INKLUSIVE des "Leg1:"-Labels in derselben QHBoxLayout-Zeile.
        Bewusst NICHT über QFormLayout(label, field), weil QFormLayout Label-
        und Feld-Spalte bei unterschiedlich hohen Widgets nicht zuverlässig
        vertikal synchronisiert (führt zu "Leg1:" vs. Inhalt versetzt). Da
        hier alles in EINER Zeile/EINEM Layout liegt und jedes Element
        explizit Qt.AlignVCenter bekommt, sind Label und Felder garantiert
        auf einer Linie.
        fixed: (ACTION, PUT_CALL, QTY) wenn durch die Trade-Type-Struktur
        vorgegeben (wird angezeigt + ins Template geschrieben, aber nicht
        editierbar) – oder None für frei editierbar (Fallback bei unbekanntem
        TRADE_TYPE). show_target steuert, ob Target/Target-Type/DTE zusätzlich
        in derselben Zeile angezeigt werden (bei Iron Condor Leg1-4 nicht
        nötig, da die Steuerung über IV-Rank/Spread-Width läuft)."""
        row_widget = QWidget()
        row_widget.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(8)

        # Feste Breite, damit die Felder aller Legs untereinander sauber
        # anfangen, egal ob "Leg1:" oder "Leg2 (Lower Wing):" davor steht.
        label_widget = QLabel(leg_label)
        label_widget.setFixedWidth(150)
        row_layout.addWidget(label_widget, 0, Qt.AlignVCenter)

        prefix = f"LEG{leg_num}_"

        if fixed is not None:
            action_val, put_call_val, qty_val = fixed
            # Feste Werte erzwingen & ins Template schreiben, unabhängig vom
            # bisherigen Inhalt – sichtbar, aber nicht veränderbar.
            self.update_template_val(idx, prefix + "ACTION", action_val)
            self.update_template_val(idx, prefix + "PUT_CALL", put_call_val)
            self.update_template_val(idx, prefix + "QTY", qty_val)

            fixed_lbl = QLabel(f"<b>{action_val} {put_call_val}</b> \u00d7 {qty_val}  <i>(fest)</i>")
            fixed_lbl.setMinimumWidth(120)
            row_layout.addWidget(fixed_lbl, 0, Qt.AlignVCenter)
        else:
            action_combo = QComboBox()
            action_combo.setMinimumWidth(90)
            action_combo.addItems(["SELL", "BUY"])
            current = tmpl.get(prefix + "ACTION", "SELL")
            if current and action_combo.findText(current) == -1:
                action_combo.addItem(current)
            action_combo.setCurrentText(current)
            self.update_template_val(idx, prefix + "ACTION", current)
            action_combo.currentTextChanged.connect(
                lambda text, i=idx, k=prefix + "ACTION": self.update_template_val(i, k, text)
            )

            put_call_combo = QComboBox()
            put_call_combo.setMinimumWidth(60)
            put_call_combo.addItems(["P", "C"])
            current = tmpl.get(prefix + "PUT_CALL", "P")
            if current and put_call_combo.findText(current) == -1:
                put_call_combo.addItem(current)
            put_call_combo.setCurrentText(current)
            self.update_template_val(idx, prefix + "PUT_CALL", current)
            put_call_combo.currentTextChanged.connect(
                lambda text, i=idx, k=prefix + "PUT_CALL": self.update_template_val(i, k, text)
            )

            qty_val = int(tmpl.get(prefix + "QTY", 1))
            qty_spin = QSpinBox()
            qty_spin.setMinimumWidth(55)
            qty_spin.setRange(1, 50)
            qty_spin.setValue(qty_val)
            self.update_template_val(idx, prefix + "QTY", qty_val)
            qty_spin.valueChanged.connect(
                lambda val, i=idx, k=prefix + "QTY": self.update_template_val(i, k, val)
            )

            row_layout.addWidget(action_combo, 0, Qt.AlignVCenter)
            row_layout.addWidget(put_call_combo, 0, Qt.AlignVCenter)
            row_layout.addWidget(QLabel("Qty:"), 0, Qt.AlignVCenter)
            row_layout.addWidget(qty_spin, 0, Qt.AlignVCenter)

        if show_target:
            target_key = prefix + "TARGET"
            target_val = int(float(tmpl.get(target_key, target_default)))
            target_spin = QSpinBox()
            target_spin.setMinimumWidth(70)
            target_spin.setRange(-1000, 1000)
            target_spin.setValue(target_val)
            self.update_template_val(idx, target_key, target_val)
            target_spin.valueChanged.connect(
                lambda val, i=idx, k=target_key: self.update_template_val(i, k, val)
            )

            type_key = prefix + "TARGET_TYPE"
            type_combo = QComboBox()
            type_combo.setEditable(True)
            type_combo.setMinimumWidth(150)
            type_combo.addItems(target_type_options or [])
            current_type = tmpl.get(type_key, target_type_default)
            if current_type and type_combo.findText(current_type) == -1:
                type_combo.addItem(current_type)
            type_combo.setCurrentText(current_type)
            self.update_template_val(idx, type_key, current_type)
            type_combo.currentTextChanged.connect(
                lambda text, i=idx, k=type_key: self.update_template_val(i, k, text)
            )

            dte_key = prefix + "DTE"
            dte_val = int(tmpl.get(dte_key, dte_default))
            dte_spin = QSpinBox()
            dte_spin.setMinimumWidth(55)
            dte_spin.setRange(0, 80)
            dte_spin.setValue(dte_val)
            self.update_template_val(idx, dte_key, dte_val)
            dte_spin.valueChanged.connect(
                lambda val, i=idx, k=dte_key: self.update_template_val(i, k, val)
            )

            row_layout.addWidget(QLabel("Target:"), 0, Qt.AlignVCenter)
            row_layout.addWidget(target_spin, 0, Qt.AlignVCenter)
            row_layout.addWidget(QLabel("Type:"), 0, Qt.AlignVCenter)
            row_layout.addWidget(type_combo, 0, Qt.AlignVCenter)
            row_layout.addWidget(QLabel("DTE:"), 0, Qt.AlignVCenter)
            row_layout.addWidget(dte_spin, 0, Qt.AlignVCenter)

        return row_widget
        
    def _leg_row_label(self, text: str) -> QLabel:
        """Zeilen-Label für die Leg-Definition-Sektion, vertikal zentriert.
        Wichtig: QFormLayout.setLabelAlignment() steuert NUR die horizontale
        Ausrichtung der Zeilenlabel – die vertikale Zentrierung gegenüber
        einer (höheren) Feld-Zeile muss am QLabel selbst gesetzt werden,
        sonst klebt das Label oben an der Zeile statt mittig zu sitzen."""
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        return lbl        

    def _build_leg_definition_box(self, idx: int, tmpl: dict) -> QGroupBox:
        """__SECTION__LEG_DEFINITION – kompakt (1 Zeile pro Leg).
        Bewusst NICHT checkable (anders als "Execution / Sweep Advanced"):
        eine checkable GroupBox graut ihren Inhalt im unchecked-Zustand aus,
        was hier – da die Werte ja immer sichtbar/gültig sein sollen – nur
        unsauber aussieht. Jede Zeile wird über form.addRow(EIN Widget) statt
        form.addRow(label, feld) eingehängt, weil QFormLayout Label- und
        Feld-Spalte bei unterschiedlich hohen Widgets nicht zuverlässig
        vertikal synchronisiert ("Leg1:" saß sonst versetzt zum Inhalt) – das
        "Leg1:"-Label ist stattdessen Teil derselben Zeile in _build_leg_row().
        Action/Put-Call/Qty sind für bekannte TradeTypes (Bull Put, PBW, Iron
        Condor) durch die jeweilige Struktur vorgegeben und daher fest (nicht
        editierbar), werden aber weiterhin ins Template geschrieben. Bei einem
        unbekannten/legacy TRADE_TYPE bleibt Leg1/Leg2 komplett editierbar
        (Fallback, wie zuvor)."""
        box = QGroupBox("Leg Definition")
        form = QFormLayout(box)

        trade_type = self._normalize_trade_type(tmpl)

        if trade_type == "BULL_PUT":
            form.addRow(self._build_leg_row(
                idx, tmpl, 1, "Leg1 (Short Put):", fixed=("SELL", "P", 1), show_target=True,
                target_default=45, target_type_options=["Delta"],
                target_type_default="Delta", dte_default=4,
            ))
            form.addRow(self._build_leg_row(
                idx, tmpl, 2, "Leg2 (Long Put):", fixed=("BUY", "P", 1), show_target=True,
                target_default=-10, target_type_options=["StrikeOffset_Leg1"],
                target_type_default="StrikeOffset_Leg1", dte_default=4,
            ))

        elif trade_type == "PBW":
            form.addRow(self._build_leg_row(
                idx, tmpl, 1, "Leg1 (Body):", fixed=("SELL", "P", 2), show_target=True,
                target_default=0, target_type_options=["NearestATM", "PercentageOTM"],
                target_type_default="NearestATM", dte_default=4,
            ))
            form.addRow(self._build_leg_row(
                idx, tmpl, 2, "Leg2 (Lower Wing):", fixed=("BUY", "P", 1), show_target=True,
                target_default=-30, target_type_options=["StrikeOffset_Leg1"],
                target_type_default="StrikeOffset_Leg1", dte_default=4,
            ))
            form.addRow(self._build_leg_row(
                idx, tmpl, 3, "Leg3 (Upper Wing):", fixed=("BUY", "P", 1), show_target=True,
                target_default=30, target_type_options=["StrikeOffset_Leg1"],
                target_type_default="StrikeOffset_Leg1", dte_default=4,
            ))

        elif trade_type == "IRON_CONDOR":
            # Steuerung läuft komplett über IV-Rank Steering + Spread Width
            # (siehe _build_iv_rank_steering_box / _build_spread_width_box) –
            # Target/Type/DTE je Leg sind hier funktionslos und werden daher
            # bewusst ausgeblendet, um die Sektion kompakt zu halten.
            form.addRow(self._build_leg_row(
                idx, tmpl, 1, "Leg1 (Short Put):", fixed=("SELL", "P", 1), show_target=False,
            ))
            form.addRow(self._build_leg_row(
                idx, tmpl, 2, "Leg2 (Long Put):", fixed=("BUY", "P", 1), show_target=False,
            ))
            form.addRow(self._build_leg_row(
                idx, tmpl, 3, "Leg3 (Short Call):", fixed=("SELL", "C", 1), show_target=False,
            ))
            form.addRow(self._build_leg_row(
                idx, tmpl, 4, "Leg4 (Long Call):", fixed=("BUY", "C", 1), show_target=False,
            ))

        else:
            # Unbekannter/legacy TRADE_TYPE -> Fallback: Leg1/Leg2 frei editierbar.
            form.addRow(self._build_leg_row(
                idx, tmpl, 1, "Leg1:", fixed=None, show_target=True,
                target_default=45, target_type_options=["Delta", "PercentageOTM", "NearestATM"],
                target_type_default="Delta", dte_default=4,
            ))
            form.addRow(self._build_leg_row(
                idx, tmpl, 2, "Leg2:", fixed=None, show_target=True,
                target_default=-10, target_type_options=["StrikeOffset_Leg1"],
                target_type_default="StrikeOffset_Leg1", dte_default=4,
            ))

        return box
        
    def _build_rescan_control_box(self, idx: int, tmpl: dict) -> QGroupBox:
        """__SECTION__RESCAN_CONTROL – eigene Section (früher Teil von
        Execution/Sweep Advanced). MAX_RESCAN_ATTEMPTS wird von jeder Strategie
        mit Rescan-Loop genutzt, ist also nicht IC- oder Sweep-spezifisch."""
        box = QGroupBox("Rescan Control")
        form = QFormLayout(box)

        max_rescans = QSpinBox()
        max_rescans.setRange(1, 50)
        max_rescans.setValue(int(tmpl.get("MAX_RESCAN_ATTEMPTS", 4)))
        max_rescans.valueChanged.connect(lambda val, i=idx: self.update_template_val(i, "MAX_RESCAN_ATTEMPTS", val))

        form.addRow("Max Rescan Attempts:", max_rescans)

        return box

    def _is_iron_condor_template(self, tmpl: dict) -> bool:
        """True für Templates mit TRADE_TYPE IRON_CONDOR/RUT_IRON_CONDOR
        (z.B. RUT-IC-DELTA-SYM). Analog zur Normalisierung in bot.py._create_trade_type."""
        return (tmpl.get("TRADE_TYPE") or "").strip().upper() in ("IRON_CONDOR", "RUT_IRON_CONDOR")
            
    def _append_matrix_row(self, table: QTableWidget, min_iv_rank, max_dte, delta_limit):
        row = table.rowCount()
        table.insertRow(row)
        table.setItem(row, 0, QTableWidgetItem(str(min_iv_rank)))
        table.setItem(row, 1, QTableWidgetItem(str(max_dte)))
        table.setItem(row, 2, QTableWidgetItem(str(delta_limit)))

    def _build_iv_rank_steering_box(self, idx: int, tmpl: dict) -> QGroupBox:
        """__SECTION__IV_RANK_STEERING – nur für Iron-Condor-Templates."""
        box = QGroupBox("IV-Rank Steering (Iron Condor)")
        form = QFormLayout(box)

        # --- IV_RANK_OVERRIDE (optional, None = Live-Berechnung via bot.get_iv_rank()) ---
        override_widget = QWidget()
        override_layout = QHBoxLayout(override_widget)
        override_layout.setContentsMargins(0, 0, 0, 0)

        override_value = tmpl.get("IV_RANK_OVERRIDE")
        chk_override = QCheckBox("Aktiv (überschreibt Live-Berechnung)")
        chk_override.setChecked(override_value is not None)

        spin_override = QSpinBox()
        spin_override.setRange(0, 100)
        spin_override.setValue(int(override_value) if override_value is not None else 20)
        spin_override.setEnabled(override_value is not None)

        chk_override.toggled.connect(spin_override.setEnabled)
        chk_override.toggled.connect(
            lambda checked, i=idx, s=spin_override: self.update_template_val(
                i, "IV_RANK_OVERRIDE", s.value() if checked else None
            )
        )
        spin_override.valueChanged.connect(
            lambda val, i=idx, c=chk_override: self.update_template_val(
                i, "IV_RANK_OVERRIDE", val if c.isChecked() else None
            )
        )

        override_layout.addWidget(chk_override)
        override_layout.addWidget(spin_override)
        self.template_iv_override_checks[idx] = (chk_override, spin_override)

        # --- IV_RANK_LOOKBACK_DAYS ---
        lookback = QSpinBox()
        lookback.setRange(30, 3650)
        lookback.setSuffix(" Tage")
        lookback.setValue(int(tmpl.get("IV_RANK_LOOKBACK_DAYS", 365)))
        lookback.valueChanged.connect(lambda val, i=idx: self.update_template_val(i, "IV_RANK_LOOKBACK_DAYS", val))

        # --- LATE_ENTRY_CUTOFF_ET ---
        cutoff = QTimeEdit()
        cutoff.setDisplayFormat("HH:mm:ss")
        cutoff_str = tmpl.get("LATE_ENTRY_CUTOFF_ET", "12:00:00")
        cutoff.setTime(QTime.fromString(cutoff_str, "hh:mm:ss"))
        cutoff.timeChanged.connect(
            lambda t, i=idx: self.update_template_val(i, "LATE_ENTRY_CUTOFF_ET", t.toString("hh:mm:ss"))
        )

        form.addRow("IV-Rank Override:", override_widget)
        form.addRow("IV-Rank Lookback:", lookback)
        form.addRow("Late-Entry Cutoff (ET):", cutoff)

        # --- IV_RANK_MATRIX (Tabelle: MIN_IV_RANK / MAX_DTE / DELTA_LIMIT) ---
        matrix_table = QTableWidget(0, 3)
        matrix_table.setHorizontalHeaderLabels(["Min IV-Rank", "Max DTE", "Delta-Limit"])
        matrix_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        matrix_table.setFixedHeight(140)

        for row in tmpl.get("IV_RANK_MATRIX", []) or []:
            self._append_matrix_row(
                matrix_table,
                row.get("MIN_IV_RANK", 0),
                row.get("MAX_DTE", 0),
                row.get("DELTA_LIMIT", 0),
            )

        self.template_matrix_tables[idx] = matrix_table

        btn_row = QHBoxLayout()
        btn_add_row = QPushButton("➕ Zeile")
        btn_add_row.clicked.connect(lambda: self._append_matrix_row(matrix_table, 0, 0, 0))
        btn_del_row = QPushButton("🗑️ Zeile")
        btn_del_row.clicked.connect(
            lambda: matrix_table.removeRow(matrix_table.currentRow()) if matrix_table.currentRow() >= 0 else None
        )
        btn_row.addWidget(btn_add_row)
        btn_row.addWidget(btn_del_row)
        btn_row.addStretch()

        matrix_container = QWidget()
        matrix_layout = QVBoxLayout(matrix_container)
        matrix_layout.setContentsMargins(0, 0, 0, 0)
        matrix_layout.addLayout(btn_row)
        matrix_layout.addWidget(matrix_table)

        form.addRow("IV-Rank -> DTE/Delta Matrix:", matrix_container)

        return box

    def _build_spread_width_box(self, idx: int, tmpl: dict) -> QGroupBox:
        """__SECTION__SPREAD_WIDTH – nur für Iron-Condor-Templates."""
        box = QGroupBox("Spread Width (Iron Condor)")
        form = QFormLayout(box)

        strike_step = QSpinBox()
        strike_step.setRange(1, 100)
        strike_step.setValue(int(tmpl.get("STRIKE_STEP", 5)))
        strike_step.valueChanged.connect(lambda val, i=idx: self.update_template_val(i, "STRIKE_STEP", val))

        min_width = QSpinBox()
        min_width.setRange(1, 1000)
        min_width.setSuffix(" Punkte")
        min_width.setValue(int(tmpl.get("MIN_SPREAD_WIDTH", 50)))
        min_width.valueChanged.connect(lambda val, i=idx: self.update_template_val(i, "MIN_SPREAD_WIDTH", val))

        max_width = QSpinBox()
        max_width.setRange(1, 1000)
        max_width.setSuffix(" Punkte")
        max_width.setValue(int(tmpl.get("MAX_SPREAD_WIDTH", 100)))
        max_width.valueChanged.connect(lambda val, i=idx: self.update_template_val(i, "MAX_SPREAD_WIDTH", val))

        put_window = QSpinBox()
        put_window.setRange(1, 2000)
        put_window.setValue(int(tmpl.get("PUT_DELTA_WINDOW", 300)))
        put_window.valueChanged.connect(lambda val, i=idx: self.update_template_val(i, "PUT_DELTA_WINDOW", val))

        call_window = QSpinBox()
        call_window.setRange(1, 2000)
        call_window.setValue(int(tmpl.get("CALL_DELTA_WINDOW", 300)))
        call_window.valueChanged.connect(lambda val, i=idx: self.update_template_val(i, "CALL_DELTA_WINDOW", val))

        form.addRow("Strike Step:", strike_step)
        form.addRow("Min Spread Width:", min_width)
        form.addRow("Max Spread Width:", max_width)
        form.addRow("Put Delta Window:", put_window)
        form.addRow("Call Delta Window:", call_window)

        hint = QLabel(
            "Hinweis: Punkte pro Seite – manuell an Kontogröße anpassen "
            "(< 50k: 20/20, 50–150k: 30–50, > 150k: 50–100)"
        )
        hint.setWordWrap(True)
        form.addRow(hint)

        return box            

    def update_template_val(self, index, key, val):
        if index < len(self.templates_data):
            self.templates_data[index][key] = val

    def update_template_name(self, index, new_name):
        if index < len(self.templates_data):
            self.templates_data[index]["TEMPLATENAME"] = new_name
            self.template_tabs.setTabText(index, new_name)

    def add_new_template(self):
        text, ok = QInputDialog.getText(self, "Neues Template", "Name des neuen Templates:")
        if ok and text:
            new_tmpl = {
                "TEMPLATENAME": text,
                "TRADE_TYPE": "BULL_PUT",
                "SYMBOL": "SPX",
                "COMMISSION_PER_CONTRACT": 1.64,
                "MIN_SWEEP_PRICE": -5.0,
                "MAX_SWEEP_PRICE": -1.0,
                "MAX_SWEEP_ATTEMPTS": 40,
                "SWEEP_WAIT_SECONDS": 5,
                "SWEEP_STEP": 0.05,
                "START_SWEEP_QUANTILE": 0.25,
            }
            self.templates_data.append(new_tmpl)
            self.build_template_tabs()
            self.template_tabs.setCurrentIndex(len(self.templates_data) - 1)

    def delete_current_template(self):
        curr_idx = self.template_tabs.currentIndex()
        templates = self.templates_data
        if curr_idx < 0 or curr_idx >= len(templates):
            return

        tmpl_name = templates[curr_idx].get("TEMPLATENAME", f"Template {curr_idx+1}")
        reply = QMessageBox.question(self, "Template Löschen", f"Template '{tmpl_name}' wirklich löschen?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            del self.templates_data[curr_idx]
            save_json(TEMPLATES_FILE, self.templates_data)
            self.build_template_tabs()
            
    def export_templates(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Trade Templates exportieren", str(TEMPLATES_FILE.name), "JSON Dateien (*.json)"
        )
        if not path:
            return
        try:
            save_json(Path(path), self.templates_data)
            QMessageBox.information(self, "Export", f"Templates exportiert nach:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export fehlgeschlagen", f"Fehler beim Exportieren:\n{e}")

    def import_templates(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Trade Templates importieren", "", "JSON Dateien (*.json)"
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Import fehlgeschlagen", f"Datei konnte nicht gelesen werden:\n{e}")
            return

        if isinstance(data, dict):
            data = data.get("templates", [])

        if not isinstance(data, list):
            QMessageBox.critical(self, "Import fehlgeschlagen", "Die Datei enthält keine gültige Template-Liste.")
            return

        reply = QMessageBox.question(
            self,
            "Trade Templates importieren",
            f"{len(data)} Template(s) in der Datei gefunden.\n"
            f"Die aktuell geladenen {len(self.templates_data)} Template(s) wirklich überschreiben?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        self.templates_data = data
        save_json(TEMPLATES_FILE, self.templates_data)
        self.build_template_tabs()
        QMessageBox.information(self, "Import", f"{len(data)} Template(s) importiert.")            

    def save_templates(self):
        # IV_RANK_MATRIX-Tabellen (nur bei Iron-Condor-Templates vorhanden) zurückschreiben
        for idx, table in self.template_matrix_tables.items():
            if idx >= len(self.templates_data):
                continue
            matrix = []
            for row in range(table.rowCount()):
                item0 = table.item(row, 0)
                item1 = table.item(row, 1)
                item2 = table.item(row, 2)
                if item0 is None or item1 is None or item2 is None:
                    continue
                try:
                    min_iv_rank = float(item0.text())
                    max_dte = int(float(item1.text()))
                    delta_limit = float(item2.text())
                except ValueError:
                    continue
                matrix.append({
                    "MIN_IV_RANK": int(min_iv_rank) if min_iv_rank.is_integer() else min_iv_rank,
                    "MAX_DTE": max_dte,
                    "DELTA_LIMIT": int(delta_limit) if delta_limit.is_integer() else delta_limit,
                })
            self.templates_data[idx]["IV_RANK_MATRIX"] = matrix

        save_json(TEMPLATES_FILE, self.templates_data)
        QMessageBox.information(self, "Erfolg", "Templates wurden erfolgreich gespeichert!")

    # ==========================================
    # 4. SYSTEM CONFIGURATIONS
    # ==========================================
    def create_system_config_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Broker Config
        broker_box = QGroupBox("⚙️ Broker")
        b_form = QFormLayout(broker_box)

        self.cfg_ib_host = QLineEdit(self.broker_data.get("IB_HOST", "127.0.0.1"))
        self.cfg_port_paper = QSpinBox()
        self.cfg_port_paper.setRange(1000, 9999)
        self.cfg_port_paper.setValue(self.broker_data.get("IB_PORT_PAPER", 7498))
        self.cfg_port_live = QSpinBox()
        self.cfg_port_live.setRange(1000, 9999)
        self.cfg_port_live.setValue(self.broker_data.get("IB_PORT_LIVE", 7497))

        self.cfg_client_id = QSpinBox()
        self.cfg_client_id.setRange(0, 999)
        self.cfg_client_id.setValue(self.broker_data.get("CLIENT_ID", 1))

        # Umschalter: Live / Paper - eigener object_name ("toggleSwitchDanger"),
        # damit Live-Trading weiterhin farblich auffällt, aber gedeckter als die
        # übrigen (neutralen) Toggle-Switches in der App.
        self.cfg_use_paper = self._make_toggle_switch(
            self.broker_data.get("USE_PAPER_TRADING", True),
            on_text="Paper",
            off_text="Live",
            object_name="toggleSwitchDanger",
        )

        b_form.addRow("IB Host:", self.cfg_ib_host)
        b_form.addRow("Port (Paper):", self.cfg_port_paper)
        b_form.addRow("Port (Live):", self.cfg_port_live)
        b_form.addRow("Client ID:", self.cfg_client_id)
        b_form.addRow("Modus:", self.cfg_use_paper)

        # Bot Mode Config
        bot_box = QGroupBox("🤖 Bot-Modus")
        bot_form = QFormLayout(bot_box)

        self.cfg_debug = self._make_toggle_switch(self.bot_mode_data.get("DEBUG_MODE", False))
        self.cfg_chk_cond = self._make_toggle_switch(self.bot_mode_data.get("CHECK_CONDITIONS", True))
        self.cfg_chk_exec_time = self._make_toggle_switch(self.bot_mode_data.get("CHECK_EXECUTION_TIME", True))
        self.cfg_chk_market_open = self._make_toggle_switch(self.bot_mode_data.get("CHECK_MARKET_OPEN", True))

        bot_form.addRow("Debug:", self.cfg_debug)
        bot_form.addRow("Checks:", self.cfg_chk_cond)
        bot_form.addRow("Zeitprüfung:", self.cfg_chk_exec_time)
        bot_form.addRow("Marktprüfung:", self.cfg_chk_market_open)

        # Telegram
        tg_box = QGroupBox("💬 Telegram-Benachrichtigungen")
        tg_form = QFormLayout(tg_box)

        self.cfg_tg_enable = self._make_toggle_switch(self.telegram_data.get("TELEGRAM_ENABLED", True))

        tg_token_widget = self._make_password_field(self.telegram_data.get("TELEGRAM_BOT_TOKEN", ""))
        self.cfg_tg_token = tg_token_widget.line_edit

        self.cfg_tg_chat = QLineEdit(self.telegram_data.get("TELEGRAM_CHAT_ID", ""))

        tg_form.addRow("Aktiv:", self.cfg_tg_enable)
        tg_form.addRow("Bot Token:", tg_token_widget)
        tg_form.addRow("Chat ID:", self.cfg_tg_chat)

        self.btn_save_sys = QPushButton("💾 Speichern")
        self.btn_save_sys.setObjectName("btn_success")
        self.btn_save_sys.clicked.connect(self.save_system_configs)

        layout.addWidget(broker_box)
        layout.addWidget(bot_box)
        layout.addWidget(tg_box)
        layout.addWidget(self.btn_save_sys)
        layout.addStretch()

        return widget
        
    def _style_status_badge(self, label: QLabel, state: str):
        """
        Färbt ein Status-Badge (z.B. TWS-Sensor) deutlich sichtbar je nach
        state ("connected" | "disconnected" | "checking") ein. Das statische
        #sensorBadge-Grau aus dem Stylesheet bot keinen Kontrast zwischen
        "Connected" und "Disconnected" - daher hier ein expliziter Inline-Style
        je Zustand und Theme.
        """
        palettes = {
            "connected": {
                True:  ("rgba(34, 197, 94, 0.18)", "rgba(34, 197, 94, 0.55)", "#4ade80"),
                False: ("rgba(34, 197, 94, 0.14)", "rgba(34, 197, 94, 0.45)", "#15803d"),
            },
            "disconnected": {
                True:  ("rgba(239, 68, 68, 0.18)", "rgba(239, 68, 68, 0.55)", "#f87171"),
                False: ("rgba(239, 68, 68, 0.14)", "rgba(239, 68, 68, 0.45)", "#b91c1c"),
            },
            "checking": {
                True:  ("#1a1e27", "#2a2f3a", "#9aa1ad"),
                False: ("#f7f8fa", "#e1e4e9", "#7c8798"),
            },
        }
        bg, border, fg = palettes.get(state, palettes["checking"])[self.is_dark_theme]
        label.setStyleSheet(
            f"background-color: {bg}; border: 1px solid {border}; color: {fg}; "
            f"border-radius: 5px; padding: 5px 12px; font-weight: 700;"
        )        

    def save_system_configs(self):
        # Broker
        self.broker_data["IB_HOST"] = self.cfg_ib_host.text()
        self.broker_data["IB_PORT_PAPER"] = self.cfg_port_paper.value()
        self.broker_data["IB_PORT_LIVE"] = self.cfg_port_live.value()
        self.broker_data["CLIENT_ID"] = self.cfg_client_id.value()
        self.broker_data["USE_PAPER_TRADING"] = self.cfg_use_paper.isChecked()
        save_json(BROKER_FILE, self.broker_data)

        # Bot Mode
        self.bot_mode_data["DEBUG_MODE"] = self.cfg_debug.isChecked()
        self.bot_mode_data["CHECK_CONDITIONS"] = self.cfg_chk_cond.isChecked()
        self.bot_mode_data["CHECK_EXECUTION_TIME"] = self.cfg_chk_exec_time.isChecked()
        self.bot_mode_data["CHECK_MARKET_OPEN"] = self.cfg_chk_market_open.isChecked()
        save_json(BOT_MODE_FILE, self.bot_mode_data)

        # Telegram
        self.telegram_data["TELEGRAM_ENABLED"] = self.cfg_tg_enable.isChecked()
        self.telegram_data["TELEGRAM_BOT_TOKEN"] = self.cfg_tg_token.text()
        self.telegram_data["TELEGRAM_CHAT_ID"] = self.cfg_tg_chat.text()
        save_json(TELEGRAM_FILE, self.telegram_data)

        QMessageBox.information(self, "Erfolg", "Alle System-Einstellungen wurden gespeichert!")


if __name__ == "__main__":
    # 1. Windows AppUserModelID festlegen (Erzwingt das eigene Taskleisten-Icon)
    if sys.platform == "win32":
        myappid = "mntradingbot.manager.ui.1.0"  # Beliebige eindeutige ID
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)    
    
    app = QApplication(sys.argv)
    
    # 2. Anwendungsweites Icon laden
    icon_path = Path(__file__).parent / "assets" / "favicon.png"
    if not icon_path.exists():
        icon_path = Path(__file__).parent / "favicon.png"
        
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))    

    # Fusion sorgt dafür, dass die Stylesheet-Regeln für die Spinbox-Pfeile
    # (::up-arrow / ::down-arrow) konsequent angewendet werden – der native
    # Windows-Style rendert eigene, kaum sichtbare Pfeile darüber/darunter.
    app.setStyle("Fusion")

    no_wheel_filter = NoWheelFilter(app)
    app.installEventFilter(no_wheel_filter)

    window = TradingBotUI()
    window.show()
    sys.exit(app.exec())