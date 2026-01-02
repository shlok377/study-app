import sys
import os
import random
import time
import shutil
import json

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *


# ---------- Helpers ----------
def base_dir() -> str:
    """Folder where this main.py is located (src/)."""
    return os.path.dirname(os.path.abspath(__file__))


def resource_path(filename: str) -> str:
    """Absolute path for a file placed next to this script (src/)."""
    return os.path.join(base_dir(), filename)


def list_pdfs_in_dir(folder: str) -> list[str]:
    try:
        files = os.listdir(folder)
    except FileNotFoundError:
        return []
    pdfs = [f for f in files if f.lower().endswith(".pdf")]
    pdfs.sort(key=lambda x: x.lower())
    return pdfs


def find_logo_path() -> str:
    """Looks for your logo in the SAME folder as this file (src/)."""
    candidates = [
        "LuminaraTransparentRect copy.png",
        "LuminaraTransparentRect copy.jpg",
        "LuminaraTransparentRect.png",
        "LuminaraTransparentRect.jpg",
        "LuminaraTransparentRect.jpeg",
    ]
    for name in candidates:
        p = resource_path(name)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(
        "No logo file found in src/. Put your logo next to src/main.py.\n"
        f"Tried: {candidates}"
    )


def safe_filename(name: str) -> str:
    # keep it simple for mac/windows; remove weird chars
    keep = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._- ()"
    cleaned = "".join(ch for ch in name if ch in keep).strip()
    return cleaned or f"file_{int(time.time())}"


# ---------- UI Components ----------
class LogoLabel(QLabel):
    """Auto-scale logo without stretch/elongation (KeepAspectRatio)"""
    def __init__(self, parent=None, max_w=900):
        super().__init__(parent)
        self.max_w = max_w
        self._original = None
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background: transparent;")

    def load_logo(self, image_path: str):
        pix = QPixmap(image_path)
        if pix.isNull():
            raise FileNotFoundError(f"Logo not found or unreadable: {image_path}")
        self._original = pix
        self._apply_scale()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_scale()

    def _apply_scale(self):
        if self._original is None:
            return
        w = min(self.width(), self.max_w)
        h = self.height()
        scaled = self._original.scaled(
            w, h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled)


class GlowButton(QPushButton):
    """Accent Button with Snappy Hover, Dimmed Text, and 50% Glow Opacity"""
    def __init__(self, text, accent_color, parent=None):
        super().__init__(text, parent)
        self.accent = accent_color
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._glow_opacity = 0
        
        # Fast animation (200ms) to keep the UI responsive
        self.anim = QVariantAnimation(self)
        self.anim.setDuration(200) 
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.valueChanged.connect(self.update_glow)
        
        self.setStyleSheet(self._base_stylesheet(font_px=13))

    def _base_stylesheet(self, font_px=13):
        """Helper to create the button style with dynamic font size"""
        return f"""
            QPushButton {{
                background-color: {self.accent};
                color: white;
                border-radius: 12px;
                font-weight: bold;
                font-size: {font_px}px;
                border: 1px solid rgba(255, 255, 255, 30);
                padding: 10px 14px;
            }}
            QPushButton:hover {{
                /* Dim the text slightly (80% opacity) so it stays visible */
                color: rgba(255, 255, 255, 200); 
            }}
        """

    def setFontPx(self, font_px: int):
        """Changes the font size dynamically while keeping other styles"""
        self.setStyleSheet(self._base_stylesheet(font_px=font_px))

    def update_glow(self, value):
        self._glow_opacity = value
        self.update()

    def enterEvent(self, event):
        self.anim.setDirection(QVariantAnimation.Direction.Forward)
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.anim.setDirection(QVariantAnimation.Direction.Backward)
        self.anim.start()
        super().leaveEvent(event)

    def paintEvent(self, event):
        # 1. Draw the GLOW FIRST as a background layer
        if self._glow_opacity > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            glow_color = QColor(self.accent).lighter(110)
            # Apply exactly 65% opacity at peak hover
            glow_color.setAlphaF(self._glow_opacity * 0.75)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(glow_color)
            painter.drawRoundedRect(self.rect(), 12, 12)
            painter.end()

        # 2. Draw the BUTTON TEXT SECOND so it stays on top and visible
        super().paintEvent(event)

class ClickableTimer(QLabel):
    clicked = pyqtSignal()

    def __init__(self, text, accent_color):
        super().__init__(text)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            f"color: {accent_color}; font-weight: bold; font-size: 18px; "
            f"background: rgba(255,255,255,10); padding: 10px 20px; border-radius: 12px;"
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()


class GlassCard(QFrame):
    """Premium Glassmorphism"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(50)
        self.shadow.setColor(QColor(0, 0, 0, 220))
        self.shadow.setOffset(0, 10)
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


class AcademiaCalendar(QCalendarWidget):
    def __init__(self, accent_color, parent=None):
        super().__init__(parent)
        self.accent_color = accent_color
        self.events = {}

    def paintCell(self, painter, rect, date):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        font = painter.font()
        font.setPointSize(10)
        painter.setFont(font)

        super().paintCell(painter, rect, date)

        if date in self.events:
            y_pos = rect.bottom() - 22

            for event_text in self.events[date][:2]:
                bar_rect = QRect(rect.left() + 6, int(y_pos), rect.width() - 12, 16)

                painter.setBrush(QColor("#6D28D9"))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(bar_rect, 4, 4)

                painter.setPen(QColor("white"))
                font.setPointSize(7)
                font.setBold(True)
                painter.setFont(font)

                display_text = f"★ {event_text}"
                metrics = QFontMetrics(font)
                elided_text = metrics.elidedText(
                    display_text,
                    Qt.TextElideMode.ElideRight,
                    bar_rect.width() - 6
                )

                painter.drawText(
                    bar_rect.adjusted(5, 0, 0, 0),
                    Qt.AlignmentFlag.AlignVCenter,
                    elided_text
                )
                y_pos -= 18

        painter.restore()


# ---------- JSON parsing (Notes + QnA) ----------
def _coerce_str(x) -> str:
    if x is None:
        return ""
    if isinstance(x, (dict, list)):
        return json.dumps(x, ensure_ascii=False, indent=2)
    return str(x)


def parse_export_json(data) -> tuple[list[dict], list[dict]]:
    """
    Returns (notes, qna) where:
      notes = [{"title":..., "content":...}, ...]
      qna   = [{"question":..., "answer":...}, ...]
    Accepts many structures:
      - {"notes":[...], "qna":[...]}
      - {"items":[{"type":"note"...}, {"type":"qna"...}]}
      - [{"title":..., "content":...}, {"question":..., "answer":...}]
      - {"exportedNotes":..., "exportedQnA":...} etc.
    """
    notes: list[dict] = []
    qna: list[dict] = []

    def push_note(title, content):
        c = _coerce_str(content).strip()
        if not c:
            return
        t = _coerce_str(title).strip() or (c.splitlines()[0][:40] if c else "Untitled")
        notes.append({"title": t, "content": c})

    def push_qna(q, a):
        q = _coerce_str(q).strip()
        a = _coerce_str(a).strip()
        if not q and not a:
            return
        qna.append({"question": q or "Question", "answer": a or ""})

    def walk(obj):
        if isinstance(obj, list):
            for it in obj:
                walk(it)
            return

        if isinstance(obj, dict):
            # direct keys
            if "notes" in obj and isinstance(obj["notes"], list):
                for n in obj["notes"]:
                    if isinstance(n, dict):
                        push_note(n.get("title") or n.get("name"), n.get("content") or n.get("text") or n.get("note"))
                    else:
                        push_note("Note", n)
            if "qna" in obj and isinstance(obj["qna"], list):
                for qa in obj["qna"]:
                    if isinstance(qa, dict):
                        push_qna(qa.get("question") or qa.get("q"), qa.get("answer") or qa.get("a"))
                    else:
                        push_qna("Question", qa)

            # alternative common names
            for k in ["exportedNotes", "exported_notes", "noteExports", "notes_export"]:
                if k in obj and isinstance(obj[k], list):
                    for n in obj[k]:
                        if isinstance(n, dict):
                            push_note(n.get("title") or n.get("name"), n.get("content") or n.get("text") or n.get("note"))
                        else:
                            push_note("Note", n)

            for k in ["exportedQnA", "exported_qna", "qa", "qas", "questions"]:
                if k in obj:
                    val = obj[k]
                    if isinstance(val, list):
                        for qa in val:
                            if isinstance(qa, dict):
                                push_qna(qa.get("question") or qa.get("q"), qa.get("answer") or qa.get("a"))
                            else:
                                push_qna("Question", qa)

            # items typed
            if "items" in obj and isinstance(obj["items"], list):
                for it in obj["items"]:
                    if isinstance(it, dict):
                        typ = (it.get("type") or it.get("kind") or "").lower()
                        if "note" in typ:
                            push_note(it.get("title") or it.get("name"), it.get("content") or it.get("text") or it.get("note"))
                        elif typ in ["qna", "qa", "question", "flashcard"]:
                            push_qna(it.get("question") or it.get("q"), it.get("answer") or it.get("a"))
                        else:
                            # heuristic
                            if ("question" in it) or ("answer" in it) or ("q" in it and "a" in it):
                                push_qna(it.get("question") or it.get("q"), it.get("answer") or it.get("a"))
                            elif ("content" in it) or ("text" in it) or ("note" in it):
                                push_note(it.get("title") or it.get("name"), it.get("content") or it.get("text") or it.get("note"))

            # heuristic dict item itself
            if ("question" in obj or "q" in obj) and ("answer" in obj or "a" in obj):
                push_qna(obj.get("question") or obj.get("q"), obj.get("answer") or obj.get("a"))
            if ("content" in obj or "text" in obj or "note" in obj):
                # avoid double adding when it was clearly a QnA dict
                if not (("question" in obj or "q" in obj) and ("answer" in obj or "a" in obj)):
                    push_note(obj.get("title") or obj.get("name"), obj.get("content") or obj.get("text") or obj.get("note"))

            return

        # primitive
        push_note("Note", obj)

    walk(data)
    return notes, qna


# ---------- Main Window ----------
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

        self._note_counter = 0

        self.quotes = [
            "Success is the sum of small efforts repeated daily.",
            "Your only limit is your mind.",
            "Deep work is the superpower of the 21st century.",
            "Don't watch the clock; do what it does. Keep going.",
            "The future belongs to those who prepare for it today.",
            "Focus on being productive instead of busy.",
            "Discipline is the bridge between goals and accomplishment.",
            "The secret of getting ahead is getting started.",
            "It's not about having time, it's about making time.",
            "Great things are done by a series of small things brought together."
        ]

        self.timer_seconds = 25 * 60
        self.timer_running = False
        self.pom_timer = QTimer()
        self.pom_timer.timeout.connect(self.update_pomodoro)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(110)
        self.sidebar.setStyleSheet(
            f"background: {self.color_30_secondary}; "
            f"border-right: 1px solid rgba(255,255,255,10);"
        )
        self.side_lay = QVBoxLayout(self.sidebar)
        self.side_lay.setContentsMargins(5, 40, 5, 20)

        self.stack = QStackedWidget()
        self.buttons = []
        nav_items = [("🏠", "Home"), ("📑", "Notes"), ("📝", "Quiz"), ("⏳", "Focus"), ("📅", "Plan")]

        for i, (icon, name) in enumerate(nav_items):
            container = QWidget()
            lay = QVBoxLayout(container)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.setSpacing(4)

            btn = QPushButton(icon)
            btn.setFixedSize(55, 55)
            btn.setCheckable(True)
            btn.setStyleSheet(
                f"QPushButton {{ font-size: 24px; background: transparent; border-radius: 15px; color: white; }}"
                f"QPushButton:checked {{ background: white; color: {self.color_10_accent}; }}"
            )

            lbl = QLabel(name)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("color: white; font-size: 9px; font-weight: bold; text-transform: uppercase;")

            btn.clicked.connect(lambda checked, idx=i: self.change_page(idx))

            lay.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
            lay.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)

            self.side_lay.addWidget(container)
            self.buttons.append(btn)

        self.side_lay.addStretch()
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.stack)

        # Directory watcher for PDFs
        self.pdf_watcher = QFileSystemWatcher(self)
        self.pdf_watcher.addPath(base_dir())
        self.pdf_watcher.directoryChanged.connect(self.refresh_pdf_list)
        self.pdf_watcher.fileChanged.connect(self.refresh_pdf_list)

        # Pages
        self.setup_home()
        self.setup_notes()
        self.setup_quiz()
        self.setup_pomodoro()
        self.setup_calendar()
        self.change_page(0)

        # First refresh PDF list after UI created
        QTimer.singleShot(50, self.refresh_pdf_list)
    

    def change_page(self, index):
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == index)
        self.stack.setCurrentIndex(index)
        if index == 0:
            self.refresh_quote()
            

    # -------- Home Page (logo no card + PDF auto list) --------
    def setup_home(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(50, 50, 50, 50)
        lay.setSpacing(18)

        # Logo area (no glass card)
        logo_wrap = QWidget()
        logo_wrap.setFixedHeight(220)
        logo_wrap.setStyleSheet("background: transparent;")
        l_lay = QVBoxLayout(logo_wrap)
        l_lay.setContentsMargins(0, 0, 0, 0)

        logo = LogoLabel(max_w=980)
        logo.setMinimumHeight(170)
        logo.setStyleSheet("background: transparent;")
        logo.setGraphicsEffect(None)

        try:
            logo_path = find_logo_path()
            logo.load_logo(logo_path)
            l_lay.addWidget(logo, alignment=Qt.AlignmentFlag.AlignCenter)
        except Exception:
            fallback = QLabel("Logo file not found")
            fallback.setAlignment(Qt.AlignmentFlag.AlignCenter)
            fallback.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
            l_lay.addWidget(fallback, alignment=Qt.AlignmentFlag.AlignCenter)

        # Middle row: Upload card + PDFs list card
        mid_row = QHBoxLayout()
        mid_row.setSpacing(18)

        # Upload card
        upload_card = GlassCard()
        u_lay = QVBoxLayout(upload_card)
        u_lay.setContentsMargins(20, 20, 20, 20)

        self.up_btn = GlowButton("Import Study PDF(s)", self.color_10_accent)
        self.up_btn.setFixedSize(330, 72)
        self.up_btn.setFontPx(15)
        self.up_btn.clicked.connect(self.select_and_copy_pdfs)

        u_lay.addStretch()
        u_lay.addWidget(self.up_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        u_lay.addStretch()

        # PDFs list card (auto)
        pdf_card = GlassCard()
        pdf_card.setMinimumWidth(420)
        p_lay = QVBoxLayout(pdf_card)
        p_lay.setContentsMargins(18, 18, 18, 18)
        p_lay.setSpacing(10)

        title = QLabel("PDFs in folder")
        title.setStyleSheet("color: white; font-weight: 900; font-size: 12px; letter-spacing: 1px;")
        p_lay.addWidget(title)

        self.pdf_search = QLineEdit()
        self.pdf_search.setPlaceholderText("Search PDFs...")
        self.pdf_search.textChanged.connect(self.filter_pdf_list)
        self.pdf_search.setStyleSheet("""
            QLineEdit{
                background: rgba(255,255,255,8);
                border: 1px solid rgba(255,255,255,14);
                color: white;
                padding: 10px 12px;
                border-radius: 12px;
                font-size: 12px;
            }
        """)
        p_lay.addWidget(self.pdf_search)

        self.pdf_list = QListWidget()
        self.pdf_list.setStyleSheet("""
            QListWidget{
                background: transparent;
                border: none;
                color: #E9E7FF;
                font-size: 12px;
            }
            QListWidget::item{
                padding: 10px 10px;
                margin: 6px 0px;
                border-radius: 12px;
                background: rgba(255,255,255,7);
                border: 1px solid rgba(255,255,255,10);
            }
            QListWidget::item:selected{
                background: rgba(139,92,246,28);
                border: 1px solid rgba(139,92,246,60);
            }
        """)
        p_lay.addWidget(self.pdf_list, 1)

        open_btn = QPushButton("Open selected PDF")
        open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        open_btn.clicked.connect(self.open_selected_pdf)
        open_btn.setStyleSheet(f"""
            QPushButton{{
                background: rgba(255,255,255,10);
                border: 1px solid rgba(255,255,255,16);
                color: white;
                font-size: 12px;
                font-weight: 800;
                border-radius: 14px;
                padding: 10px 12px;
            }}
            QPushButton:hover{{ background: rgba(255,255,255,14); }}
        """)
        p_lay.addWidget(open_btn)

        mid_row.addWidget(upload_card, 1)
        mid_row.addWidget(pdf_card, 1)

        # Quote card
        quote_card = GlassCard()
        quote_card.setFixedHeight(95)
        q_lay = QVBoxLayout(quote_card)
        q_lay.setContentsMargins(20, 8, 20, 8)

        self.quote_label = QLabel()
        self.quote_label.setWordWrap(True)
        self.quote_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.quote_label.setStyleSheet("color: white; font-size: 15px; font-style: italic;")
        q_lay.addWidget(self.quote_label)

        lay.addWidget(logo_wrap)
        lay.addLayout(mid_row, 1)
        lay.addWidget(quote_card)

        self.stack.addWidget(page)

    def refresh_quote(self):
        self.quote_label.setText(f"“ {random.choice(self.quotes)} ”")

    def refresh_pdf_list(self):
        # ensure watcher tracks new files too (optional)
        folder = base_dir()
        pdfs = list_pdfs_in_dir(folder)
        current = {self.pdf_list.item(i).text() for i in range(self.pdf_list.count())}

        # rebuild clean (simpler, consistent with filtering)
        self.pdf_list.clear()
        for f in pdfs:
            self.pdf_list.addItem(f)

        # apply filter
        if hasattr(self, "pdf_search"):
            self.filter_pdf_list(self.pdf_search.text())

    def filter_pdf_list(self, text: str):
        q = (text or "").strip().lower()
        for i in range(self.pdf_list.count()):
            item = self.pdf_list.item(i)
            item.setHidden(q not in item.text().lower())

    def select_and_copy_pdfs(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDF(s)", "", "PDF Files (*.pdf)")
        if not files:
            return

        dest_dir = base_dir()
        copied = 0
        for src in files:
            try:
                name = safe_filename(os.path.basename(src))
                if not name.lower().endswith(".pdf"):
                    name += ".pdf"
                dst = os.path.join(dest_dir, name)

                # avoid overwrite: add (1), (2)...
                if os.path.exists(dst):
                    root, ext = os.path.splitext(name)
                    k = 1
                    while True:
                        dst = os.path.join(dest_dir, f"{root} ({k}){ext}")
                        if not os.path.exists(dst):
                            break
                        k += 1

                shutil.copy2(src, dst)
                copied += 1
            except Exception as e:
                QMessageBox.warning(self, "Copy failed", f"Could not copy:\n{src}\n\n{e}")

        self.refresh_pdf_list()
        if copied:
            QMessageBox.information(self, "Imported", f"Imported {copied} PDF(s) into:\n{dest_dir}")

    def open_selected_pdf(self):
        item = self.pdf_list.currentItem()
        if not item:
            QMessageBox.information(self, "Select", "Select a PDF from the list first.")
            return
        path = resource_path(item.text())
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    # -------- Notes Page (History drawer LEFT + toolbox RIGHT) --------
    def setup_notes(self):
        page = QWidget()
        main_lay = QVBoxLayout(page)
        main_lay.setContentsMargins(30, 30, 30, 30)
        main_lay.setSpacing(18)

        # Top bar: HISTORY button on LEFT + timer
        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)

        self.history_toggle_btn = QPushButton("HISTORY")
        self.history_toggle_btn.setFixedHeight(46)
        self.history_toggle_btn.setMinimumWidth(120)
        self.history_toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.history_toggle_btn.setStyleSheet(f"""
            QPushButton{{
                background: rgba(255,255,255,10);
                border: 1px solid rgba(255,255,255,18);
                color: white;
                font-size: 12px;
                font-weight: 900;
                letter-spacing: 1px;
                border-radius: 14px;
                padding: 0px 14px;
            }}
            QPushButton:hover{{ background: rgba(255,255,255,16); }}
        """)
        self.history_toggle_btn.clicked.connect(self.toggle_history_drawer)

        self.mini_timer = ClickableTimer("25:00", self.color_10_accent)
        self.mini_timer.clicked.connect(lambda: self.change_page(3))

        top_bar.addWidget(self.history_toggle_btn)
        top_bar.addWidget(self.mini_timer)
        top_bar.addStretch()
        main_lay.addLayout(top_bar)

        # Main content row: HISTORY (LEFT) | EDITOR (CENTER) | TOOLBOX (RIGHT)
        row = QHBoxLayout()
        row.setSpacing(18)

        # History drawer (LEFT) collapsed
        self.hist_drawer = GlassCard()
        self.hist_drawer.setMaximumWidth(0)
        self.hist_drawer.setMinimumWidth(0)

        h_lay = QVBoxLayout(self.hist_drawer)
        h_lay.setContentsMargins(16, 18, 16, 18)
        h_lay.setSpacing(10)

        title = QLabel("RECENT")
        title.setStyleSheet("color: white; font-weight: 900; font-size: 12px; letter-spacing: 1px;")
        h_lay.addWidget(title)

        self.hist_search = QLineEdit()
        self.hist_search.setPlaceholderText("Search history...")
        self.hist_search.textChanged.connect(self.filter_history)
        self.hist_search.setStyleSheet("""
            QLineEdit{
                background: rgba(255,255,255,8);
                border: 1px solid rgba(255,255,255,14);
                color: white;
                padding: 10px 12px;
                border-radius: 12px;
                font-size: 12px;
            }
            QLineEdit:focus{
                border: 1px solid rgba(139,92,246,70);
                background: rgba(255,255,255,10);
            }
        """)
        h_lay.addWidget(self.hist_search)

        self.hist_list = QListWidget()
        self.hist_list.setStyleSheet("""
            QListWidget{
                background: transparent;
                border: none;
                color: #E9E7FF;
                font-size: 12px;
            }
            QListWidget::item{
                padding: 10px 10px;
                margin: 6px 0px;
                border-radius: 12px;
                background: rgba(255,255,255,7);
                border: 1px solid rgba(255,255,255,10);
            }
            QListWidget::item:selected{
                background: rgba(139,92,246,28);
                border: 1px solid rgba(139,92,246,60);
            }
        """)
        self.hist_list.itemClicked.connect(self.open_note_from_history)
        h_lay.addWidget(self.hist_list, 1)

        # Drawer animation
        self._drawer_open = False
        self.hist_anim = QPropertyAnimation(self.hist_drawer, b"maximumWidth")
        self.hist_anim.setDuration(260)
        self.hist_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        # Editor (center)
        self.notes_editor = QTextEdit()
        self.notes_editor.setPlaceholderText("Write or paste notes here...")
        self.notes_editor.setStyleSheet(
            "background: rgba(10, 10, 25, 150); color: white; border-radius: 20px;font-family: 'Inter'; font-size: 16.5px;"
            "padding: 20px; border: 1px solid rgba(255,255,255,10);"
        )

        # Toolbox (RIGHT)
        toolbox = GlassCard()
        toolbox.setFixedWidth(320)
        t_lay = QVBoxLayout(toolbox)
        t_lay.setContentsMargins(15, 25, 15, 25)
        t_lay.setSpacing(14)

        t_lay.addWidget(QLabel("AI TOOLBOX", styleSheet=f"color: {self.color_10_accent}; font-weight: bold; font-size: 15px; letter-spacing: 1px;"))

        self.tone = QComboBox()
        self.tone.addItems(["Technical", "ELI5", "Bullet Points", "Narrative"])
        self.tone.setStyleSheet(
            "QComboBox { background-color: #1A1D2E; color: white; border-radius: 8px; padding: 10px; "
            "border: 1px solid rgba(255,255,255,10); } "
            "QComboBox QAbstractItemView { background: #1A1D2E; color: white; selection-background-color: #8B5CF6; }"
        )
        t_lay.addWidget(QLabel("SUMMARY TONE", styleSheet="color: white; font-size: 12px;"))
        t_lay.addWidget(self.tone)

        t_lay.addSpacing(6)

        self.gen_btn = GlowButton("✨ GENERATE", self.color_10_accent)
        self.gen_btn.setMinimumHeight(55)
        self.gen_btn.clicked.connect(self.save_note_to_history)
        t_lay.addWidget(self.gen_btn)


        # ✅ Import exported JSON (Notes + QnA display)
        import_json_btn = QPushButton("Import Exported JSON")
        import_json_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        import_json_btn.clicked.connect(self.import_exported_json)
        import_json_btn.setStyleSheet(f"""
            QPushButton{{
                background: rgba(255,255,255,10);
                border: 1px solid rgba(255,255,255,16);
                color: white;
                font-size: 12px;
                font-weight: 800;
                border-radius: 14px;
                padding: 12px 12px;
            }}
            QPushButton:hover{{ background: rgba(255,255,255,14); }}
        """)
        t_lay.addWidget(import_json_btn)

        t_lay.addStretch()

        # add all to row
        row.addWidget(self.hist_drawer)
        row.addWidget(self.notes_editor, 1)
        row.addWidget(toolbox)
        main_lay.addLayout(row)

        self.stack.addWidget(page)

    def toggle_history_drawer(self):
        target = 360 if not self._drawer_open else 0
        self.hist_anim.stop()
        self.hist_anim.setStartValue(self.hist_drawer.maximumWidth())
        self.hist_anim.setEndValue(target)
        self.hist_anim.start()
        self._drawer_open = not self._drawer_open
        if self._drawer_open:
            self.hist_search.setFocus()

    def _make_note_title(self, text: str) -> str:
        first_line = (text.strip().splitlines()[0] if text.strip() else "").strip()
        if not first_line:
            self._note_counter += 1
            return f"Note {self._note_counter} • {time.strftime('%H:%M')}"
        if len(first_line) > 28:
            first_line = first_line[:28].rstrip() + "…"
        return f"{first_line} • {time.strftime('%H:%M')}"

    def save_note_to_history(self):
        content = self.notes_editor.toPlainText()
        

        title = self._make_note_title(content)
        item = QListWidgetItem(title)
        item.setData(Qt.ItemDataRole.UserRole, content)
        self.hist_list.insertItem(0, item)
        self.hist_list.setCurrentRow(0)

        if not self._drawer_open:
            self.toggle_history_drawer()
        self.filter_history(self.hist_search.text())

    def open_note_from_history(self, item: QListWidgetItem):
        content = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(content, str):
            self.notes_editor.setPlainText(content)

    def filter_history(self, text: str):
        q = (text or "").strip().lower()
        for i in range(self.hist_list.count()):
            item = self.hist_list.item(i)
            title = (item.text() or "").lower()
            body = (item.data(Qt.ItemDataRole.UserRole) or "").lower()
            match = (q in title) or (q in body)
            item.setHidden(not match)

    def import_exported_json(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select exported JSON", "", "JSON Files (*.json)")
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.warning(self, "Invalid JSON", f"Could not read JSON:\n{e}")
            return

        notes, qna = parse_export_json(data)

        # Notes → history list
        added_notes = 0
        for n in notes:
            title = _coerce_str(n.get("title")).strip() or "Imported Note"
            content = _coerce_str(n.get("content")).strip()
            if not content:
                continue
            item = QListWidgetItem(f"{title} • imported")
            item.setData(Qt.ItemDataRole.UserRole, content)
            self.hist_list.insertItem(0, item)
            added_notes += 1

        # QnA → quiz tab area
        added_qna = 0
        if qna and hasattr(self, "quiz_area"):
            blocks = []
            for i, qa in enumerate(qna, start=1):
                q = qa.get("question", "")
                a = qa.get("answer", "")
                blocks.append(f"Q{i}. {q}\nA{i}. {a}\n")
                added_qna += 1
            # append to current quiz area (don’t overwrite if already)
            existing = self.quiz_area.toPlainText().strip()
            join_text = "\n".join(blocks).strip()
            self.quiz_area.setPlainText((existing + "\n\n" + join_text).strip() if existing else join_text)

        if added_notes and not self._drawer_open:
            self.toggle_history_drawer()

        QMessageBox.information(
            self,
            "Imported",
            f"Imported:\n• Notes: {added_notes}\n• QnA: {added_qna}\n\n(Notes appear in HISTORY, QnA appears in QUIZ tab.)"
        )

    # -------- Quiz Page --------
    # -------- Quiz Page (Modified) --------
    def setup_quiz(self):
        page = QWidget()
        lay = QHBoxLayout(page)
        lay.setContentsMargins(30, 30, 30, 30)
        lay.setSpacing(25)

        # 1. Main Display Area
        display = GlassCard()
        d_lay = QVBoxLayout(display)

        self.quiz_area = QTextEdit()
        self.quiz_area.setPlaceholderText("Quiz / QnA content will appear here...")
        self.quiz_area.setStyleSheet("background: transparent; color: white; border: none; font-size: 16.5px;")
        d_lay.addWidget(self.quiz_area)

        # 2. Control Sidebar
        ctrls = GlassCard()
        ctrls.setFixedWidth(310)
        c_lay = QVBoxLayout(ctrls)
        c_lay.setContentsMargins(18, 25, 18, 25)
        c_lay.setSpacing(15)

        c_lay.addWidget(QLabel(
            "QUIZ CONFIGURATION",
            styleSheet=f"color: {self.color_10_accent}; font-weight: bold; font-size: 15px; letter-spacing: 1px;"
        ))

        # --- Question Type Selection ---
        c_lay.addWidget(QLabel(
            "QUESTION TYPE",
            styleSheet=f"color: {self.color_text_dim}; font-size: 12px; font-weight: bold;"
        ))
        
        self.quiz_type_combo = QComboBox()
        self.quiz_type_combo.addItems(["Brief Q/Ans", "True/False", "MCQs"])
        # Set Default to Brief Q/Ans
        self.quiz_type_combo.setCurrentText("Brief Q/Ans")
        self.quiz_type_combo.setStyleSheet(
            "QComboBox { background-color: #1A1D2E; color: white; border-radius: 8px; padding: 10px; "
            "border: 1px solid rgba(255,255,255,10); } "
            "QComboBox QAbstractItemView { background: #1A1D2E; color: white; selection-background-color: #8B5CF6; }"
        )
        c_lay.addWidget(self.quiz_type_combo)

        # --- Question Count ---
        c_lay.addWidget(QLabel(
            "QUESTIONS COUNT",
            styleSheet=f"color: {self.color_text_dim}; font-size: 12px; font-weight: bold;"
        ))
        self.quiz_count_spin = QSpinBox()
        self.quiz_count_spin.setRange(5, 50)
        self.quiz_count_spin.setValue(10)
        self.quiz_count_spin.setStyleSheet(
            "QSpinBox { background-color: #1A1D2E; color: white; border-radius: 8px; padding: 10px; "
            "border: 1px solid rgba(255,255,255,10); }"
        )
        c_lay.addWidget(self.quiz_count_spin)

        # --- Character Length Slider ---
        len_header = QHBoxLayout()
        len_header.addWidget(QLabel(
            "CHARACTER LENGTH",
            styleSheet=f"color: {self.color_text_dim}; font-size: 12px; font-weight: bold;"
        ))
        self.char_len_val_label = QLabel("350") # Default Label
        self.char_len_val_label.setStyleSheet(f"color: {self.color_10_accent}; font-weight: bold; font-size: 10px;")
        len_header.addStretch()
        len_header.addWidget(self.char_len_val_label)
        c_lay.addLayout(len_header)

        self.char_len_slider = QSlider(Qt.Orientation.Horizontal)
        self.char_len_slider.setRange(100, 500)
        self.char_len_slider.setValue(350) # Default Value
        self.char_len_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid #333;
                height: 4px;
                background: #1A1D2E;
                margin: 2px 0;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {self.color_10_accent};
                border: 1px solid {self.color_10_accent};
                width: 14px;
                height: 14px;
                margin: -6px 0;
                border-radius: 7px;
            }}
        """)
        self.char_len_slider.valueChanged.connect(
            lambda v: self.char_len_val_label.setText(str(v))
        )
        c_lay.addWidget(self.char_len_slider)

        # --- Summary of Types (Info Text) ---
        c_lay.addSpacing(10)
        

        c_lay.addStretch()
        
        # --- Generate Button ---
        quiz_gen_btn = GlowButton("🚀 GENERATE QUIZ", self.color_10_accent)
        quiz_gen_btn.setMinimumHeight(55)
        c_lay.addWidget(quiz_gen_btn)

        lay.addWidget(display, 7)
        lay.addWidget(ctrls, 3)
        self.stack.addWidget(page)

    # -------- Pomodoro Page --------
    def setup_pomodoro(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(50, 50, 50, 50)

        timer_card = GlassCard()
        cl = QVBoxLayout(timer_card)

        self.timer_label = QLabel("25:00")
        self.timer_label.setFont(QFont("Inter", 120, QFont.Weight.Bold))
        self.timer_label.setStyleSheet("color: white;")
        cl.addWidget(self.timer_label, alignment=Qt.AlignmentFlag.AlignCenter)

        btn_lay = QHBoxLayout()
        btn_lay.setSpacing(20)

        self.start_btn = GlowButton("START", self.color_10_accent)
        self.start_btn.setFixedSize(140, 55)
        self.start_btn.clicked.connect(self.toggle_timer)

        self.stop_btn = GlowButton("STOP", self.color_10_accent)
        self.stop_btn.setFixedSize(140, 55)
        self.stop_btn.clicked.connect(self.reset_timer)

        self.lap_btn = QPushButton("LAP")
        self.lap_btn.setFixedSize(140, 55)
        self.lap_btn.clicked.connect(self.capture_lap)
        self.lap_btn.setStyleSheet(
            "background: transparent; border: 2px solid white; color: white; "
            "border-radius: 15px; font-weight: bold;"
        )

        btn_lay.addStretch()
        btn_lay.addWidget(self.start_btn)
        btn_lay.addWidget(self.stop_btn)
        btn_lay.addWidget(self.lap_btn)
        btn_lay.addStretch()

        cl.addLayout(btn_lay)
        lay.addWidget(timer_card)
        self.stack.addWidget(page)

    def toggle_timer(self):
        if not self.timer_running:
            self.pom_timer.start(1000)
            self.start_btn.setText("PAUSE")
        else:
            self.pom_timer.stop()
            self.start_btn.setText("START")
        self.timer_running = not self.timer_running

    def reset_timer(self):
        self.pom_timer.stop()
        self.timer_running = False
        self.timer_seconds = 25 * 60
        self.timer_label.setText("25:00")
        if hasattr(self, "mini_timer"):
            self.mini_timer.setText("25:00")
        self.start_btn.setText("START")

    def capture_lap(self):
        if hasattr(self, "hist_list"):
            self.hist_list.addItem(f"⏱️ Focus Lap: {self.timer_label.text()} (at {time.strftime('%H:%M:%S')})")

    def update_pomodoro(self):
        if self.timer_seconds > 0:
            self.timer_seconds -= 1
            mins, secs = divmod(self.timer_seconds, 60)
            formatted_time = f"{mins:02d}:{secs:02d}"
            self.timer_label.setText(formatted_time)
            if hasattr(self, "mini_timer"):
                self.mini_timer.setText(formatted_time)
        else:
            self.reset_timer()

    # -------- Calendar Page --------
    def setup_calendar(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(40, 40, 40, 40)

        cal_card = GlassCard()
        cv = QVBoxLayout(cal_card)

        self.calendar = AcademiaCalendar(self.color_10_accent)
        self.calendar.activated.connect(self.add_calendar_event)

        self.calendar.setStyleSheet(f"""
            QCalendarWidget QWidget {{ color: white; font-family: 'Inter'; }}
            QCalendarWidget QAbstractItemView {{
                background-color: #111122;
                border-radius: 15px;
                selection-background-color: {self.color_10_accent};
            }}
            QCalendarWidget QAbstractItemView:item {{
                border-radius: 8px;
                margin: 3px;
            }}
            QCalendarWidget QWidget#qt_calendar_navigationbar {{
                background-color: #1A1A2E;
                min-height: 85px;
                padding: 5px 20px;
                border-bottom: 1px solid rgba(139, 92, 246, 0.2);
            }}
            QCalendarWidget QToolButton {{
                color: white;
                font-weight: bold;
                background: transparent;
                height: 40px;
                width: 140px;
                border-radius: 8px;
            }}
            QCalendarWidget QToolButton:hover {{
                background: rgba(139, 92, 246, 0.3);
            }}
            QCalendarWidget QSpinBox {{
                background-color: #1A1D2E;
                color: white;
                width: 65px;
                border-radius: 5px;
            }}
        """)

        cv.addWidget(self.calendar)
        lay.addWidget(cal_card)
        self.stack.addWidget(page)

    def add_calendar_event(self, qdate):
        text, ok = QInputDialog.getText(
            self, "Add Event", f"Enter Exam/Event for {qdate.toString('MMM d')}:"
        )
        if ok and text:
            if qdate not in self.calendar.events:
                self.calendar.events[qdate] = []
            self.calendar.events[qdate].append(text)
            self.calendar.update()

    # -------- Window Background / Drag --------
    def paintEvent(self, event):
        p = QPainter(self)
        g = QLinearGradient(0, 0, self.width(), self.height())
        g.setColorAt(0, QColor(self.color_60_primary))
        g.setColorAt(1, QColor("#16162E"))
        p.fillRect(self.rect(), g)

    def mousePressEvent(self, event):
        self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_pos = event.globalPosition().toPoint()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
