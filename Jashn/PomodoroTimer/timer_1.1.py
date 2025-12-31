import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTabWidget, QTimeEdit, QListWidget,
    QMessageBox, QSpinBox, QScrollArea, QFrame, QDialog,
    QDialogButtonBox, QAbstractItemView, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import (
    Qt, QTimer, QTime, QSize, QRect, QRectF, QPropertyAnimation, 
    QEasingCurve, pyqtProperty, QPoint, QPointF
)
from PyQt6.QtGui import (
    QFont, QColor, QPainter, QPainterPath, QPen, QBrush
)
import math

# --- UI COLOR PALETTE ---
BG_MAIN = QColor("#0A0914")       
BG_GRADIENT = QColor("#16162E")   
BG_WIDGET = QColor("#1A1A2E")     
BG_INPUT = QColor("#1A1D2E")      

TEXT_PRIMARY = QColor("#E2E8F0")  
TEXT_WHITE = QColor("#FFFFFF")    
TEXT_SECONDARY = QColor("#A78BFA") 

ACCENT_MAIN = QColor("#8B5CF6")   
ACCENT_SECONDARY = QColor("#A78BFA") 
ALERT_RED = QColor("#FF4444")     

class StyledButton(QPushButton):
    """
    A modern button with advanced animations.
    """
    def __init__(self, text, color=ACCENT_MAIN, parent=None):
        super().__init__(text, parent)
        self._color = color # Internal color variable
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(40)
        self.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        
        # --- RIPPLE STATE ---
        self._ripple_radius = 0.0 # Explicit float
        self._ripple_center = QPoint()
        
        # --- GLOW EFFECT (HOVER) ---
        self.glow_effect = QGraphicsDropShadowEffect(self)
        self.glow_effect.setBlurRadius(0) 
        self.glow_effect.setColor(color)
        self.glow_effect.setOffset(0, 0)
        self.setGraphicsEffect(self.glow_effect)
        
        # --- ANIMATIONS ---
        self.glow_anim = QPropertyAnimation(self.glow_effect, b"blurRadius")
        self.glow_anim.setDuration(200)
        self.glow_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        self.ripple_anim = QPropertyAnimation(self, b"rippleRadius")
        self.ripple_anim.setDuration(450)
        self.ripple_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.ripple_anim.finished.connect(self.reset_ripple)

    # Setter to safely change color and trigger update
    def setColor(self, color):
        self._color = color
        self.glow_effect.setColor(color)
        self.update()

    @pyqtProperty(float)
    def rippleRadius(self):
        return float(self._ripple_radius)

    @rippleRadius.setter
    def rippleRadius(self, radius):
        self._ripple_radius = float(radius)
        self.update() 

    def reset_ripple(self):
        self._ripple_radius = 0.0
        self.update()

    def enterEvent(self, event):
        if self.isEnabled():
            self.glow_anim.stop()
            self.glow_anim.setStartValue(self.glow_effect.blurRadius())
            self.glow_anim.setEndValue(25)
            self.glow_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.isEnabled():
            self.glow_anim.stop()
            self.glow_anim.setStartValue(self.glow_effect.blurRadius())
            self.glow_anim.setEndValue(0)
            self.glow_anim.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if self.isEnabled():
            self._ripple_center = event.pos()
            self._ripple_radius = 0.0
            
            max_dim = max(self.width(), self.height())
            end_radius = max_dim * 1.5
            
            self.ripple_anim.stop()
            self.ripple_anim.setStartValue(0.0)
            self.ripple_anim.setEndValue(float(end_radius))
            self.ripple_anim.start()
            
        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self.isEnabled():
            bg_color = self._color
            text_color = TEXT_WHITE
        else:
            bg_color = QColor(255, 255, 255, 10)
            text_color = QColor(255, 255, 255, 100)

        path = QPainterPath()
        # Use explicit floats for addRoundedRect to avoid potential binding ambiguity
        path.addRoundedRect(0.0, 0.0, float(self.width()), float(self.height()), 8.0, 8.0)
        
        painter.fillPath(path, bg_color)
        
        if self._ripple_radius > 0:
            painter.save()
            painter.setClipPath(path)
            
            max_radius = self.ripple_anim.endValue()
            progress = self._ripple_radius / max_radius if max_radius > 0 else 0
            opacity = 0.4 * (1.0 - progress)
            
            ripple_color = QColor(255, 255, 255)
            ripple_color.setAlphaF(max(0.0, opacity))
            
            painter.setBrush(QBrush(ripple_color))
            painter.setPen(Qt.PenStyle.NoPen)
            
            # Cast QPoint to QPointF to match float radius
            painter.drawEllipse(QPointF(self._ripple_center), self._ripple_radius, self._ripple_radius)
            
            painter.restore()

        painter.setPen(text_color)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())

class ModernSpinBox(QSpinBox):
    def __init__(self):
        super().__init__()
        self.setButtonSymbols(QSpinBox.ButtonSymbols.UpDownArrows)
        self.setStyleSheet(f"""
            QSpinBox {{
                background: {BG_INPUT.name()};
                color: {TEXT_PRIMARY.name()};
                border: 1px solid #333;
                border-radius: 5px;
                padding: 5px;
                font-size: 16px;
                font-family: 'Segoe UI';
                font-weight: bold;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 20px;
                background: {BG_INPUT.name()};
                border: none;
                border-left: 1px solid #333;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background: {ACCENT_MAIN.name()};
            }}
            QSpinBox::up-arrow {{ width: 10px; height: 10px; }} 
            QSpinBox::down-arrow {{ width: 10px; height: 10px; }}
        """)

class CircularTimer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(320, 320)
        self.time_str = "00:00:00"
        self.progress = 1.0

    def update_progress(self, time_text, progress):
        self.time_str = time_text
        self.progress = max(0.0, min(1.0, progress))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        padding = 15
        rect = QRect(padding, padding, w - 2*padding, h - 2*padding)
        
        pen_bg = QPen(QColor(226, 232, 240, 20), 8) 
        painter.setPen(pen_bg)
        painter.drawEllipse(rect)
        
        if self.progress > 0:
            pen_prog = QPen(ACCENT_MAIN, 8)
            pen_prog.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen_prog)
            
            span_angle = int(-self.progress * 360 * 16)
            painter.drawArc(rect, 90 * 16, span_angle)
        
        painter.setPen(TEXT_WHITE)
        painter.setFont(QFont("Consolas", 42, QFont.Weight.Bold))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.time_str)

class AlarmRollerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Alarm")
        self.setFixedSize(350, 300)
        self.setStyleSheet(f"background: {BG_WIDGET.name()}; color: {TEXT_PRIMARY.name()};")
        
        main_layout = QVBoxLayout(self)
        
        lbl = QLabel("Pick Time")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        main_layout.addWidget(lbl)

        roller_layout = QHBoxLayout()
        roller_layout.setSpacing(5)

        self.list_hours = self.create_list([str(i) for i in range(1, 13)])
        self.list_mins = self.create_list([f"{i:02d}" for i in range(60)])
        self.list_ampm = self.create_list(["AM", "PM"])

        now = QTime.currentTime()
        h = now.hour()
        ampm_index = 1 if h >= 12 else 0
        h_12 = h if 1 <= h <= 12 else (h % 12 if h % 12 != 0 else 12)
        
        self.list_hours.setCurrentRow(h_12 - 1)
        self.list_mins.setCurrentRow(now.minute())
        self.list_ampm.setCurrentRow(ampm_index)

        roller_layout.addWidget(self.list_hours)
        roller_layout.addWidget(QLabel(":"))
        roller_layout.addWidget(self.list_mins)
        roller_layout.addWidget(self.list_ampm)
        
        main_layout.addLayout(roller_layout)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        ok_btn = btns.button(QDialogButtonBox.StandardButton.Ok)
        ok_btn.setText("Set")
        ok_btn.setStyleSheet(f"background: {ACCENT_MAIN.name()}; color: white; border: none; padding: 6px 15px; border-radius: 4px; font-weight: bold;")
        
        cancel_btn = btns.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_btn.setStyleSheet(f"background: {BG_INPUT.name()}; color: {TEXT_PRIMARY.name()}; border: none; padding: 6px 15px; border-radius: 4px;")
        
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        main_layout.addWidget(btns)

    def create_list(self, items):
        lst = QListWidget()
        lst.addItems(items)
        lst.setStyleSheet(f"""
            QListWidget {{
                background: {BG_INPUT.name()};
                border: 1px solid #333;
                border-radius: 5px;
                font-size: 20px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 10px;
                color: {TEXT_SECONDARY.name()};
            }}
            QListWidget::item:selected {{
                background: rgba(139, 92, 246, 0.2); 
                color: {ACCENT_MAIN.name()};
                font-weight: bold;
            }}
        """)
        lst.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        return lst

    def get_time(self):
        h_str = self.list_hours.currentItem().text()
        m_str = self.list_mins.currentItem().text()
        ampm = self.list_ampm.currentItem().text()
        
        h = int(h_str)
        m = int(m_str)
        
        if ampm == "PM" and h != 12:
            h += 12
        elif ampm == "AM" and h == 12:
            h = 0
            
        return QTime(h, m)

# --- MAIN MODULES ---

class ProductivityTimer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget()
        
        # UPDATED STYLESHEET: Fully Rounded Pills for ALL Tabs
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ 
                border: none; 
                background: {BG_MAIN.name()}; 
            }}
            QTabWidget::tab-bar {{
                alignment: center;
            }}
            QTabBar::tab {{
                background: {BG_WIDGET.name()};
                color: {TEXT_SECONDARY.name()};
                
                /* PILL SHAPE FOR ALL STATES */
                border-radius: 20px; 
                padding: 10px 25px;
                min-width: 140px;
                
                margin-left: 5px;
                margin-right: 5px;
                margin-bottom: 5px;
                
                font-weight: bold;
                font-family: 'Segoe UI';
                border: 1px solid #333;
            }}
            
            QTabBar::tab:hover {{
                background: {BG_INPUT.name()};
                border-color: {ACCENT_SECONDARY.name()};
            }}
            
            QTabBar::tab:selected {{
                background: {BG_MAIN.name()};
                color: {ACCENT_MAIN.name()};
                
                /* Highlight Active Tab */
                border: 2px solid {ACCENT_MAIN.name()};
                
                /* Keep it rounded, do NOT square off the bottom */
                border-radius: 20px;
            }}
        """)

        self.timer_tab = TimerMode()
        self.stopwatch_tab = StopwatchMode()
        self.alarm_tab = AlarmMode()

        self.tabs.addTab(self.timer_tab, "⏳ Timer")
        self.tabs.addTab(self.stopwatch_tab, "⏱️ Stopwatch")
        self.tabs.addTab(self.alarm_tab, "⏰ Alarm")

        self.layout.addWidget(self.tabs)

class TimerMode(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Display
        self.timer_display = CircularTimer()
        self.timer_display.update_progress("00:25:00", 1.0)
        
        # Controls
        btn_layout = QHBoxLayout()
        self.btn_start = StyledButton("Start", ACCENT_MAIN)
        self.btn_reset = StyledButton("Reset", BG_INPUT)
        self.btn_reset.setStyleSheet(f"color: {TEXT_SECONDARY.name()};")
        
        self.btn_start.clicked.connect(self.toggle_timer)
        self.btn_reset.clicked.connect(self.reset_timer)
        
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_reset)

        # Quick Select Buttons
        quick_layout = QHBoxLayout()
        for mins in [25, 30, 55, 60]:
            btn = QPushButton(f"{mins}m")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {BG_WIDGET.name()}; 
                    color: {TEXT_PRIMARY.name()}; 
                    border: 1px solid #333; 
                    padding: 8px; 
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    background: {BG_INPUT.name()};
                    border-color: {ACCENT_MAIN.name()};
                }}
            """)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, m=mins: self.set_preset_time(m))
            quick_layout.addWidget(btn)

        # Custom Input
        input_container = QFrame()
        input_container.setStyleSheet(f"background: {BG_WIDGET.name()}; border-radius: 10px; padding: 10px;")
        custom_layout = QHBoxLayout(input_container)
        
        self.spin_h = ModernSpinBox()
        self.spin_h.setRange(0, 99)
        self.spin_h.setSuffix(" h")
        
        self.spin_m = ModernSpinBox()
        self.spin_m.setRange(0, 59)
        self.spin_m.setSuffix(" m")
        
        self.spin_s = ModernSpinBox()
        self.spin_s.setRange(0, 59)
        self.spin_s.setSuffix(" s")
        
        btn_set_custom = QPushButton("Set")
        btn_set_custom.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_set_custom.setStyleSheet(f"""
            background: {ACCENT_MAIN.name()}; 
            color: white; 
            border-radius: 5px; 
            font-weight: bold; 
            padding: 5px 15px;
        """)
        btn_set_custom.clicked.connect(self.set_custom_time)

        custom_layout.addWidget(self.spin_h)
        custom_layout.addWidget(self.spin_m)
        custom_layout.addWidget(self.spin_s)
        custom_layout.addWidget(btn_set_custom)

        lbl_presets = QLabel("Presets:")
        lbl_presets.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-weight: bold;")
        lbl_manual = QLabel("Manual Input:")
        lbl_manual.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-weight: bold;")

        layout.addWidget(self.timer_display, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(btn_layout)
        layout.addSpacing(15)
        layout.addWidget(lbl_presets)
        layout.addLayout(quick_layout)
        layout.addSpacing(10)
        layout.addWidget(lbl_manual)
        layout.addWidget(input_container)
        layout.addStretch()
        
        # Logic
        self.total_ms = 25 * 60 * 1000
        self.current_ms = self.total_ms
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.is_running = False
        self.update_interval = 20 

    def set_preset_time(self, mins):
        self.spin_h.setValue(0)
        self.spin_m.setValue(mins)
        self.spin_s.setValue(0)
        self.set_custom_time()

    def set_custom_time(self):
        h = self.spin_h.value()
        m = self.spin_m.value()
        s = self.spin_s.value()
        
        total_seconds = (h * 3600) + (m * 60) + s
        if total_seconds == 0: return
        
        self.stop_timer_logic_only()
        self.btn_start.setText("Start")
        self.btn_start.setColor(ACCENT_MAIN)
        
        self.total_ms = total_seconds * 1000
        self.current_ms = self.total_ms
        self.update_display()

    def toggle_timer(self):
        if self.is_running:
            self.stop_timer_logic_only()
            self.btn_start.setText("Resume")
            self.btn_start.setColor(ACCENT_MAIN)
        else:
            self.start_timer()

    def start_timer(self):
        self.is_running = True
        self.btn_start.setText("Pause")
        self.btn_start.setColor(BG_INPUT) # Dim button to show it's active/busy
        self.timer.start(self.update_interval)

    def stop_timer_logic_only(self):
        self.is_running = False
        self.timer.stop()

    def reset_timer(self):
        self.stop_timer_logic_only()
        self.btn_start.setText("Start")
        self.btn_start.setColor(ACCENT_MAIN) # Safe restore
        self.current_ms = self.total_ms
        self.update_display()

    def update_timer(self):
        if self.current_ms > 0:
            self.current_ms -= self.update_interval
            self.update_display()
        else:
            self.stop_timer_logic_only()
            self.btn_start.setText("Start")
            self.btn_start.setColor(ACCENT_MAIN)
            self.timer_display.update_progress("DONE!", 0.0)

    def update_display(self):
        seconds_remaining = int(math.ceil(self.current_ms / 1000.0))
        m, s = divmod(seconds_remaining, 60)
        h, m = divmod(m, 60)
        text = f"{h:02d}:{m:02d}:{s:02d}"
        
        if self.total_ms > 0:
            progress = self.current_ms / self.total_ms
        else:
            progress = 0
        self.timer_display.update_progress(text, progress)

class StopwatchMode(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        self.lbl_display = QLabel("00:00.00")
        self.lbl_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_display.setFont(QFont("Consolas", 40, QFont.Weight.Bold))
        self.lbl_display.setStyleSheet(f"color: {ACCENT_MAIN.name()};")

        btn_layout = QHBoxLayout()
        self.btn_start = StyledButton("Start", ACCENT_MAIN)
        self.btn_lap = StyledButton("Lap", ACCENT_SECONDARY) 
        self.btn_reset = StyledButton("Reset", BG_INPUT)
        self.btn_reset.setStyleSheet(f"color: {TEXT_SECONDARY.name()};")

        self.btn_start.clicked.connect(self.toggle_stopwatch)
        self.btn_lap.clicked.connect(self.record_lap)
        self.btn_reset.clicked.connect(self.reset_stopwatch)

        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_lap)
        btn_layout.addWidget(self.btn_reset)

        self.laps_list = QListWidget()
        self.laps_list.setStyleSheet(f"""
            QListWidget {{
                background: transparent; 
                border: none; 
                outline: none;
            }}
            QListWidget::item {{
                color: {TEXT_SECONDARY.name()};
                padding: 10px;
                border-bottom: 1px solid rgba(255,255,255,0.05);
                font-family: 'Segoe UI';
                font-size: 16px;
            }}
            QListWidget::item:selected {{
                background: {BG_WIDGET.name()};
                color: {TEXT_WHITE.name()};
            }}
        """)
        
        layout.addWidget(self.lbl_display)
        layout.addLayout(btn_layout)
        layout.addWidget(self.laps_list)

        self.timer = QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update_stopwatch)
        self.time_elapsed_ms = 0
        self.is_running = False

    def toggle_stopwatch(self):
        if self.is_running:
            self.timer.stop()
            self.btn_start.setText("Resume")
            self.btn_start.setColor(ACCENT_MAIN)
            self.is_running = False
        else:
            self.timer.start()
            self.btn_start.setText("Pause")
            self.btn_start.setColor(BG_INPUT)
            self.is_running = True

    def update_stopwatch(self):
        self.time_elapsed_ms += 10
        self.update_display()

    def update_display(self):
        seconds = (self.time_elapsed_ms // 1000) % 60
        minutes = (self.time_elapsed_ms // 60000)
        milliseconds = (self.time_elapsed_ms % 1000) // 10
        self.lbl_display.setText(f"{minutes:02d}:{seconds:02d}.{milliseconds:02d}")

    def record_lap(self):
        if self.is_running or self.time_elapsed_ms > 0:
            lap_time = self.lbl_display.text()
            item_text = f"Lap {self.laps_list.count() + 1}   —   {lap_time}"
            self.laps_list.insertItem(0, item_text)

    def reset_stopwatch(self):
        self.timer.stop()
        self.is_running = False
        self.time_elapsed_ms = 0
        self.btn_start.setText("Start")
        self.btn_start.setColor(ACCENT_MAIN)
        self.update_display()
        self.laps_list.clear()

class AlarmMode(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        
        self.alarms_container = QWidget()
        self.alarms_layout = QVBoxLayout(self.alarms_container)
        self.alarms_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll_area.setWidget(self.alarms_container)
        self.layout.addWidget(self.scroll_area)

        self.empty_msg = QLabel("No alarms set.\nClick + to add one.")
        self.empty_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_msg.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 14px;")
        self.alarms_layout.addWidget(self.empty_msg)

        self.btn_add = QPushButton("+")
        self.btn_add.setFixedSize(50, 50)
        self.btn_add.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_MAIN.name()};
                color: white;
                font-size: 30px;
                border-radius: 25px;
                padding-bottom: 5px;
                border: 2px solid {BG_MAIN.name()};
            }}
            QPushButton:hover {{
                background-color: {ACCENT_SECONDARY.name()};
            }}
        """)
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.clicked.connect(self.open_add_alarm_dialog)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_add)
        self.layout.addLayout(btn_layout)

        self.alarms = [] 
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_alarms)
        self.check_timer.start(1000)

    def open_add_alarm_dialog(self):
        dialog = AlarmRollerDialog(self)
        if dialog.exec():
            self.add_alarm(dialog.get_time())

    def add_alarm(self, time_obj):
        self.alarms.append(time_obj)
        self.refresh_alarm_list()

    def remove_alarm(self, time_obj):
        if time_obj in self.alarms:
            self.alarms.remove(time_obj)
            self.refresh_alarm_list()

    def refresh_alarm_list(self):
        while self.alarms_layout.count() > 1:
            item = self.alarms_layout.takeAt(self.alarms_layout.count() - 1)
            if item.widget():
                item.widget().deleteLater()

        if not self.alarms:
            self.empty_msg.setVisible(True)
            return
        
        self.empty_msg.setVisible(False)
        self.alarms.sort(key=lambda t: (t.hour(), t.minute()))

        for alarm_time in self.alarms:
            row_widget = QFrame()
            row_widget.setStyleSheet(f"background: {BG_WIDGET.name()}; border-radius: 10px; border: 1px solid {BG_INPUT.name()};")
            row_layout = QHBoxLayout(row_widget)
            
            lbl_time = QLabel(alarm_time.toString("h:mm AP"))
            lbl_time.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
            lbl_time.setStyleSheet(f"color: {TEXT_PRIMARY.name()};")
            
            btn_del = QPushButton("✕")
            btn_del.setFixedSize(30, 30)
            btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_del.setStyleSheet(f"background: transparent; color: {TEXT_SECONDARY.name()}; border: 1px solid {BG_INPUT.name()}; border-radius: 15px;")
            btn_del.clicked.connect(lambda checked, t=alarm_time: self.remove_alarm(t))
            
            row_layout.addWidget(lbl_time)
            row_layout.addStretch()
            row_layout.addWidget(btn_del)
            
            self.alarms_layout.addWidget(row_widget)

    def check_alarms(self):
        now = QTime.currentTime()
        for alarm in self.alarms:
            if now.hour() == alarm.hour() and now.minute() == alarm.minute() and now.second() == 0:
                QMessageBox.warning(self, "Alarm", f"⏰ It is {alarm.toString('h:mm AP')}!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProductivityTimer()
    window.setWindowTitle("Clock")
    window.resize(700, 600) # Increased width
    window.setStyleSheet(f"background-color: {BG_MAIN.name()}; color: {TEXT_PRIMARY.name()};")
    window.show()
    sys.exit(app.exec())