import sys
import random
import time
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class GlowButton(QPushButton):
    """Accent Button (10%) with High-Intensity 5-Second Glow"""
    def __init__(self, text, accent_color, parent=None):
        super().__init__(text, parent)
        self.accent = accent_color
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._glow_opacity = 0
        self.anim = QVariantAnimation(self)
        self.anim.setDuration(5000) 
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.valueChanged.connect(self.update_glow)
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.accent};
                color: white;
                border-radius: 12px;
                font-weight: bold;
                font-size: 13px;
                border: 1px solid rgba(255, 255, 255, 30);
            }}
        """)

    def update_glow(self, value):
        self._glow_opacity = value
        self.update()

    def enterEvent(self, event):
        self.anim.setDirection(QVariantAnimation.Direction.Forward)
        self.anim.start()

    def leaveEvent(self, event):
        self.anim.setDirection(QVariantAnimation.Direction.Backward)
        self.anim.start()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._glow_opacity > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            glow_rect = self.rect().toRectF()
            glow_color = QColor(self.accent)
            glow_color.setAlphaF(self._glow_opacity * 0.95) 
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(glow_color)
            painter.drawRoundedRect(glow_rect, 12, 12)

class ClickableTimer(QLabel):
    """Mini-Timer that switches to the Focus Tab when clicked"""
    clicked = pyqtSignal()
    def __init__(self, text, accent_color):
        super().__init__(text)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"color: {accent_color}; font-weight: bold; font-size: 18px; background: rgba(255,255,255,10); padding: 10px 20px; border-radius: 12px;")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton: self.clicked.emit()

class GlassCard(QFrame):
    """Secondary Component (30%): Premium Glassmorphism"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(50)
        self.shadow.setColor(QColor(0, 0, 0, 220))
        self.setGraphicsEffect(self.shadow)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().toRectF()
        path = QPainterPath()
        path.addRoundedRect(rect, 25, 25)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(255, 255, 255, 22)) 
        gradient.setColorAt(1, QColor(255, 255, 255, 6))  
        painter.fillPath(path, QBrush(gradient))
        painter.setPen(QPen(QColor(255, 255, 255, 30), 1.5))
        painter.drawPath(path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.color_60_primary = "#0A0914" 
        self.color_30_secondary = "#1A1A2E"
        self.color_10_accent = "#8B5CF6"
        self.color_text_dim = "#A78BFA"

        self.resize(1280, 850)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.quotes = ["Success is the sum of small efforts repeated daily.", "Your only limit is your mind.", "Deep work is the superpower of the 21st century."]
        self.timer_seconds = 25 * 60
        self.timer_running = False
        self.pom_timer = QTimer()
        self.pom_timer.timeout.connect(self.update_pomodoro)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1) Sidebar with Icon Labels
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(110)
        self.sidebar.setStyleSheet(f"background: {self.color_30_secondary}; border-right: 1px solid rgba(255,255,255,10);")
        self.side_lay = QVBoxLayout(self.sidebar)
        self.side_lay.setContentsMargins(5, 40, 5, 20)
        
        self.stack = QStackedWidget()
        self.buttons = []
        nav_items = [("🏠", "Home"), ("📑", "Notes"), ("📝", "Quiz"), ("⏳", "Focus"), ("📅", "Plan")]
        
        for i, (icon, name) in enumerate(nav_items):
            container = QWidget(); lay = QVBoxLayout(container); lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(4)
            btn = QPushButton(icon); btn.setFixedSize(55, 55); btn.setCheckable(True)
            btn.setStyleSheet(f"QPushButton {{ font-size: 24px; background: transparent; border-radius: 15px; color: white; }}"
                              f"QPushButton:checked {{ background: white; color: {self.color_10_accent}; }}")
            
            lbl = QLabel(name); lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("color: white; font-size: 9px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;")
            
            btn.clicked.connect(lambda checked, idx=i: self.change_page(idx))
            lay.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter); lay.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)
            self.side_lay.addWidget(container); self.buttons.append(btn)

        self.side_lay.addStretch()
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.stack)

        self.setup_home()
        self.setup_notes()
        self.setup_quiz()
        self.setup_pomodoro()
        self.setup_calendar()
        self.change_page(0)

    def change_page(self, index):
        for i, btn in enumerate(self.buttons): btn.setChecked(i == index)
        self.stack.setCurrentIndex(index)
        if index == 0: self.refresh_quote()

    def setup_home(self):
        page = QWidget(); lay = QVBoxLayout(page); lay.setContentsMargins(50, 50, 50, 50); lay.setSpacing(20)
        logo_card = GlassCard(); logo_card.setFixedHeight(120); l_lay = QVBoxLayout(logo_card)
        logo = QLabel("ACADEMIA"); logo.setFont(QFont("Inter", 50, QFont.Weight.Bold))
        logo.setStyleSheet("color: white; letter-spacing: 15px;"); l_lay.addWidget(logo, alignment=Qt.AlignmentFlag.AlignCenter)
        upload_card = GlassCard(); u_lay = QVBoxLayout(upload_card)
        up_btn = GlowButton("Import Study PDF(s)", self.color_10_accent); up_btn.setFixedSize(280, 65)
        up_btn.clicked.connect(self.select_pdfs); u_lay.addStretch(); u_lay.addWidget(up_btn, alignment=Qt.AlignmentFlag.AlignCenter); u_lay.addStretch()
        quote_card = GlassCard(); quote_card.setFixedHeight(180); q_lay = QVBoxLayout(quote_card)
        self.quote_label = QLabel(); self.quote_label.setWordWrap(True); self.quote_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.quote_label.setStyleSheet("color: white; font-size: 19px; font-style: italic;"); q_lay.addWidget(self.quote_label)
        lay.addWidget(logo_card); lay.addWidget(upload_card); lay.addWidget(quote_card); self.stack.addWidget(page)

    def select_pdfs(self): QFileDialog.getOpenFileNames(self, "Select PDF(s)", "", "PDF Files (*.pdf)")
    def refresh_quote(self): self.quote_label.setText(f"“ {random.choice(self.quotes)} ”")

    def setup_notes(self):
        page = QWidget(); main_lay = QVBoxLayout(page); main_lay.setContentsMargins(30, 30, 30, 30)
        top_bar = QHBoxLayout(); self.mini_timer = ClickableTimer("25:00", self.color_10_accent); self.mini_timer.clicked.connect(lambda: self.change_page(3))
        top_bar.addWidget(self.mini_timer); top_bar.addStretch(); main_lay.addLayout(top_bar)
        
        content_lay = QHBoxLayout(); content_lay.setSpacing(25)
        hist = GlassCard(); hist.setFixedWidth(220); h_lay = QVBoxLayout(hist)
        h_lay.addWidget(QLabel("📜 HISTORY", styleSheet="color: white; font-weight: bold;"))
        self.hist_list = QListWidget(); self.hist_list.setStyleSheet("background: transparent; color: #A78BFA; border: none;")
        h_lay.addWidget(self.hist_list)
        
        self.notes_editor = QTextEdit(); self.notes_editor.setPlaceholderText("Notes content...")
        self.notes_editor.setStyleSheet("background: rgba(10, 10, 25, 150); color: white; border-radius: 20px; padding: 20px; border: 1px solid rgba(255,255,255,10);")
        
        toolbox = GlassCard(); toolbox.setFixedWidth(280); t_lay = QVBoxLayout(toolbox)
        t_lay.setContentsMargins(15, 25, 15, 25)
        t_lay.addWidget(QLabel("AI TOOLBOX", styleSheet=f"color: {self.color_10_accent}; font-weight: bold;"))
        t_lay.addSpacing(20); t_lay.addWidget(QLabel("SUMMARY TONE", styleSheet="color: white; font-size: 10px;"))
        
        # 2) Opaque Dropdown
        tone = QComboBox(); tone.addItems(["Technical", "ELI5", "Bullet Points", "Narrative"])
        tone.setStyleSheet("QComboBox { background-color: #1A1D2E; color: white; border-radius: 8px; padding: 10px; border: 1px solid rgba(255,255,255,10); } QComboBox QAbstractItemView { background: #1A1D2E; color: white; selection-background-color: #8B5CF6; }")
        t_lay.addWidget(tone)
        
        t_lay.addStretch(); gen_btn = GlowButton("✨ GENERATE", self.color_10_accent); gen_btn.setMinimumHeight(55); t_lay.addWidget(gen_btn)
        
        content_lay.addWidget(hist, 2); content_lay.addWidget(self.notes_editor, 6); content_lay.addWidget(toolbox, 2)
        main_lay.addLayout(content_lay); self.stack.addWidget(page)

    def setup_quiz(self):
        page = QWidget(); lay = QHBoxLayout(page); lay.setContentsMargins(30, 30, 30, 30); lay.setSpacing(25)
        display = GlassCard(); d_lay = QVBoxLayout(display)
        self.quiz_area = QTextEdit(); self.quiz_area.setPlaceholderText("Quiz content..."); self.quiz_area.setStyleSheet("background: transparent; color: white; border: none;")
        d_lay.addWidget(self.quiz_area)
        
        ctrls = GlassCard(); ctrls.setFixedWidth(310); c_lay = QVBoxLayout(ctrls)
        c_lay.setContentsMargins(15, 25, 15, 25)
        c_lay.addWidget(QLabel("QUIZ CONFIG", styleSheet=f"color: {self.color_10_accent}; font-weight: bold; font-size: 12px;"))
        
        # 3) Adjusted Questions Count Styling
        c_lay.addSpacing(20)
        q_count_lbl = QLabel("QUESTIONS COUNT")
        q_count_lbl.setStyleSheet(f"color: {self.color_text_dim}; font-size: 10px; font-weight: bold; letter-spacing: 1px;")
        c_lay.addWidget(q_count_lbl)
        
        spin = QSpinBox(); spin.setRange(5, 50); spin.setValue(10)
        spin.setStyleSheet("QSpinBox { background-color: #1A1D2E; color: white; border-radius: 8px; padding: 10px; border: 1px solid rgba(255,255,255,10); }")
        c_lay.addWidget(spin)
        
        c_lay.addSpacing(20)
        for opt in ["Multiple Choice", "True/False", "Key Concepts"]:
            chk = QCheckBox(opt); chk.setStyleSheet("color: #A78BFA; font-size: 11px;"); c_lay.addWidget(chk)
            
        c_lay.addStretch(); quiz_gen_btn = GlowButton("🚀 GENERATE QUIZ", self.color_10_accent); quiz_gen_btn.setMinimumHeight(55); c_lay.addWidget(quiz_gen_btn)
        lay.addWidget(display, 7); lay.addWidget(ctrls, 3); self.stack.addWidget(page)

    def setup_pomodoro(self):
        page = QWidget(); lay = QVBoxLayout(page); lay.setContentsMargins(50, 50, 50, 50)
        timer_card = GlassCard(); cl = QVBoxLayout(timer_card)
        self.timer_label = QLabel("25:00"); self.timer_label.setFont(QFont("Inter", 120, QFont.Weight.Bold)); self.timer_label.setStyleSheet("color: white;")
        cl.addWidget(self.timer_label, alignment=Qt.AlignmentFlag.AlignCenter)
        btn_lay = QHBoxLayout(); btn_lay.setSpacing(20)
        self.start_btn = GlowButton("START", self.color_10_accent); self.start_btn.setFixedSize(140, 55); self.start_btn.clicked.connect(self.toggle_timer)
        self.stop_btn = GlowButton("STOP", self.color_10_accent); self.stop_btn.setFixedSize(140, 55); self.stop_btn.clicked.connect(self.reset_timer)
        self.lap_btn = QPushButton("LAP"); self.lap_btn.setFixedSize(140, 55); self.lap_btn.clicked.connect(self.capture_lap)
        self.lap_btn.setStyleSheet("background: transparent; border: 2px solid white; color: white; border-radius: 15px; font-weight: bold;")
        btn_lay.addStretch(); btn_lay.addWidget(self.start_btn); btn_lay.addWidget(self.stop_btn); btn_lay.addWidget(self.lap_btn); btn_lay.addStretch()
        cl.addLayout(btn_lay); lay.addWidget(timer_card); self.stack.addWidget(page)

    def toggle_timer(self):
        if not self.timer_running: self.pom_timer.start(1000); self.start_btn.setText("PAUSE")
        else: self.pom_timer.stop(); self.start_btn.setText("START")
        self.timer_running = not self.timer_running

    def reset_timer(self):
        self.pom_timer.stop(); self.timer_running = False; self.timer_seconds = 25 * 60
        self.timer_label.setText("25:00"); self.mini_timer.setText("25:00"); self.start_btn.setText("START")

    def capture_lap(self):
        self.hist_list.addItem(f"⏱️ Focus Lap: {self.timer_label.text()} (at {time.strftime('%H:%M:%S')})")

    def update_pomodoro(self):
        if self.timer_seconds > 0:
            self.timer_seconds -= 1
            mins, secs = divmod(self.timer_seconds, 60)
            formatted_time = f"{mins:02d}:{secs:02d}"
            self.timer_label.setText(formatted_time); self.mini_timer.setText(formatted_time)
        else: self.reset_timer()

    def setup_calendar(self):
        page = QWidget(); lay = QVBoxLayout(page); lay.setContentsMargins(40, 40, 40, 40)
        cal_card = GlassCard(); cv = QVBoxLayout(cal_card)
        cal = QCalendarWidget()
        
        # 4) Fix Overlap & 5) Rounded Boxes
        cal.setStyleSheet(f"""
            QCalendarWidget QWidget {{ color: white; font-family: 'Inter'; }}
            QCalendarWidget QAbstractItemView {{ background-color: #111122; border-radius: 15px; selection-background-color: {self.color_10_accent}; }}
            
            /* Rounded Date Boxes */
            QCalendarWidget QAbstractItemView:item {{ border-radius: 8px; margin: 2px; border: 1px solid rgba(255,255,255,5); }}

            /* Fixed Header Overlap */
            QCalendarWidget QWidget#qt_calendar_navigationbar {{ 
                background-color: #1A1A2E; 
                min-height: 85px; padding: 5px 20px; border-bottom: 1px solid rgba(139, 92, 246, 0.2);
            }}
            QCalendarWidget QToolButton {{ 
                color: white; font-weight: bold; background: transparent; 
                height: 40px; width: 140px; /* Increased width to prevent text overlap */
                border-radius: 8px; margin: 0 5px;
            }}
            QCalendarWidget QToolButton:hover {{ background: rgba(139, 92, 246, 0.3); }}
            
            /* Opaque Year/Month Spinners */
            QCalendarWidget QSpinBox {{ background-color: #1A1D2E; color: white; width: 65px; border-radius: 5px; }}
        """)
        cv.addWidget(cal); lay.addWidget(cal_card); self.stack.addWidget(page)

    def paintEvent(self, event):
        p = QPainter(self); g = QLinearGradient(0, 0, self.width(), self.height())
        g.setColorAt(0, QColor(self.color_60_primary)); g.setColorAt(1, QColor("#16162E")) 
        p.fillRect(self.rect(), g)

    def mousePressEvent(self, event): self.old_pos = event.globalPosition().toPoint()
    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
        self.move(self.x() + delta.x(), self.y() + delta.y()); self.old_pos = event.globalPosition().toPoint()

if __name__ == "__main__":
    app = QApplication(sys.argv); w = MainWindow(); w.show(); sys.exit(app.exec())