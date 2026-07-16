import sys
import os
import sqlite3

from datetime import datetime

from PySide6.QtCore import (
    Qt,
    QTimer, QTime,
    QSize,
    QEasingCurve,
    QPropertyAnimation,
    QUrl,
    Signal,
    QDateTime
)

from PySide6.QtGui import (
    QColor,
    QPainter,
    QFont,
    QPen,
    QKeySequence,
    QShortcut
)

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGraphicsDropShadowEffect,
    QFrame,
    QFileDialog,
    QMessageBox,
    QTextEdit,
    QLineEdit,
    QDialog,
    QComboBox,
)

from PySide6.QtMultimedia import QSoundEffect
from pages.config import ConfigManager
from windows.add_estudos import RegistroEstudoWindow

# ============================================================
# CONFIG
# ============================================================

TIMER_INTERVAL_MS = 100

# ============================================================
# BOTÃO
# ============================================================

class PastelButton(QPushButton):

    def __init__(self, text, color):
        super().__init__(text)

        self.setMinimumHeight(58)
        self.setCursor(Qt.PointingHandCursor)

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: none;
                border-radius: 22px;
                color: #5f5f5f;
                font-size: 17px;
                font-weight: bold;
                padding: 14px;
            }}

            QPushButton:hover {{
                background-color: rgba(255,255,255,0.55);
            }}

            QPushButton:pressed {{
                padding-top: 16px;
            }}
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(180, 180, 180, 90))

        self.setGraphicsEffect(shadow)



# ============================================================
# GRÁFICO CIRCULAR
# ============================================================

class CircularProgress(QWidget):

    def __init__(self):
        super().__init__()

        self.progress = 1.0
        self.overtime = False

        self.saving = False
        self.spinner_angle = 0

        self.spinner_timer = QTimer(self)
        self.spinner_timer.timeout.connect(
            self.rotate_spinner
        )

        self.setMinimumSize(320, 320)

    def set_progress(self, value, overtime=False):

        self.progress = value
        self.overtime = overtime

        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(24, 24, -24, -24)

        pen_width = 28

        # ====================================================
        # FUNDO
        # ====================================================

        bg_pen = QPen(QColor(255, 255, 255, 70))

        bg_pen.setWidth(pen_width)
        bg_pen.setCapStyle(Qt.RoundCap)

        painter.setPen(bg_pen)
        painter.setBrush(Qt.NoBrush)

        painter.drawEllipse(rect)

        # ====================================================
        # COR DA BARRA
        # ====================================================

        if not self.overtime:
            color = QColor("#76e941")
        else:
            color = QColor("#ffb7b2")

        progress_pen = QPen(color)

        progress_pen.setWidth(pen_width)
        progress_pen.setCapStyle(Qt.RoundCap)

        painter.setPen(progress_pen)

        # ====================================================
        # DESENHO
        # ====================================================

        painter.drawArc(
            rect,
            90 * 16,
            int(-360 * self.progress * 16)
        )


        if self.saving:
            spinner_pen = QPen(
                QColor("#7dafff")
            )

            spinner_pen.setWidth(8)
            spinner_pen.setCapStyle(Qt.RoundCap)

            painter.setPen(spinner_pen)

            spinner_rect = rect.adjusted(
                40, 40, -40, -40
            )

            painter.drawArc(
                spinner_rect,
                -self.spinner_angle * 16,
                -90 * 16
            )
        
    def rotate_spinner(self):

        self.spinner_angle += 12

        if self.spinner_angle >= 360:
            self.spinner_angle = 0

        self.update()

    def start_saving_animation(self):

        self.saving = True
        self.spinner_timer.start(20)

    def stop_saving_animation(self):

        self.saving = False
        self.spinner_timer.stop()
        self.update()

# ============================================================
# APP
# ============================================================

class FocusTimer(QWidget):

    closed = Signal()
    study_saved = Signal()

    def __init__(self):
        super().__init__()
        
        # ====================================================
        # JANELA
        # ====================================================

        self.setWindowTitle("Cronometro")

        self.setFixedSize(560, 820)

        self.setWindowFlags(
            Qt.Window |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )
        self.configuracao = ConfigManager()

        self.setAttribute(Qt.WA_TranslucentBackground)

        # ====================================================
        # ESTADO
        # ====================================================

        self.running = False

        self.view_mode = "normal"

        self.NORMAL_SIZE = QSize(560, 820)
        self.COMPACT_SIZE = QSize(300, 250)

        # tempo principal
        self.total_time_ms = self.configuracao.get_ultimo_timer() * 60 * 1000
        self.remaining_time_ms = self.total_time_ms

        # overtime
        self.overtime = False
        self.overtime_ms = 0

        # acumuladores
        self.pause_time_ms = 0
        self.study_time_ms = 0

        # som
        self.played_end_sound = False

        # historico de logs

        self.session_logs = []

        # ====================================================
        # TIMER
        # ====================================================

        self.timer = QTimer()

        self.timer.timeout.connect(self.update_timer)

        # ====================================================
        # UI
        # ====================================================

        self.build_ui()

    # ========================================================
    # UI
    # ========================================================

    def build_ui(self):

        root = QVBoxLayout(self)

        root.setContentsMargins(18, 18, 18, 18)

        self.card = QFrame()

        self.card.setStyleSheet("""
            QFrame {
                background-color: rgba(245,240,255,185);
                border-radius: 38px;
                border: 1px solid rgba(255,255,255,0.5);
            }
        """)

        root.addWidget(self.card)

        self.main_layout = QVBoxLayout(self.card)

        layout = self.main_layout

        layout.setContentsMargins(35, 30, 35, 30)
        layout.setSpacing(18)

        # ====================================================
        # TITULO
        # ====================================================

        self.title_label = QLabel("TEMPO (min)")
        title = self.title_label

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            color: #7d7d7d;
            font-size: 18px;
            font-weight: bold;
            letter-spacing: 5px;
        """)

        layout.addWidget(title)

        # ====================================================
        # INPUT
        # ====================================================

        self.input_minutes = QLineEdit(str(self.configuracao.get_ultimo_timer()))

        self.input_minutes.textChanged.connect(self.update_input_minutes)

        self.input_minutes.setAlignment(Qt.AlignCenter)

        self.input_minutes.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255,255,255,0.5);
                border-radius: 18px;
                border: none;
                padding: 16px;
                color: #777;
                font-size: 24px;
                font-weight: bold;
            }
        """)

        layout.addWidget(self.input_minutes)

        # ====================================================
        # GRÁFICO
        # ====================================================

        self.progress = CircularProgress()

        layout.addWidget(
            self.progress,
            alignment=Qt.AlignCenter
        )

        # ====================================================
        # TIMER
        # ====================================================

        horas = self.configuracao.get_ultimo_timer() // 60
        min_restantes = self.configuracao.get_ultimo_timer() % 60
        segundos = 0
        tempo_formatado = f"{horas:02d}:{min_restantes:02d}:{segundos:02d}"

        self.time_label = QLabel(tempo_formatado)
        self.time_label.setObjectName("displayCronometro")

        self.time_label.setAlignment(Qt.AlignCenter)

        font = QFont("Arial", 40, QFont.Bold)
        self.time_label.setFont(font)

        self.time_label.setStyleSheet("""
            color: #5f5f5f;
            background-color: rgba(255,255,255,0.35);
            border-radius: 24px;
            padding: 18px;
        """)

        layout.addWidget(self.time_label)

        # ====================================================
        # STATUS
        # ====================================================

        self.status_label = QLabel("PRONTO")

        self.status_label.setAlignment(Qt.AlignCenter)

        self.status_label.setStyleSheet("""
            color: #888;
            font-size: 16px;
            font-weight: bold;
            letter-spacing: 3px;
        """)

        layout.addWidget(self.status_label)

        # ====================================================
        # ESTATÍSTICAS
        # ====================================================

        self.study_label = QLabel(
            "Estudo acumulado: 00:00:00"
        )

        self.pause_label = QLabel(
            "Pausa acumulada: 00:00:00"
        )

        for lbl in [self.study_label, self.pause_label]:

            lbl.setAlignment(Qt.AlignCenter)

            lbl.setStyleSheet("""
                color: #707070;
                font-size: 16px;
                background-color: rgba(255,255,255,0.3);
                border-radius: 16px;
                padding: 12px;
            """)

            layout.addWidget(lbl)

        # ====================================================
        # BOTÕES
        # ====================================================

        buttons = QHBoxLayout()

        self.start_button = PastelButton(
            "COMEÇAR",
            "rgba(200,230,201,0.75)"
        )
        atalho = QShortcut(QKeySequence("Space"), self)
        atalho.activated.connect(self.start_button.click)

        self.save_button = PastelButton(
            "SALVAR",
            "rgba(187,222,251,0.75)"
        )

        buttons.addWidget(self.start_button)
        buttons.addWidget(self.save_button)

        layout.addLayout(buttons)

        # ====================================================
        # LOG
        # ====================================================

        self.log_box = QTextEdit()

        self.log_box.setReadOnly(True)

        self.log_box.setFixedHeight(130)

        self.log_box.setStyleSheet("""
            QTextEdit {
                background-color: rgba(255,255,255,0.3);
                border-radius: 22px;
                border: none;
                padding: 16px;
                color: #666;
                font-size: 14px;
            }
        """)

        layout.addWidget(self.log_box)

        # ====================================================
        # CONTROLES
        # ====================================================

        self.mode_btn = QPushButton("◱")

        self.mode_btn.setFixedSize(34, 34)

        self.mode_btn.setCursor(
            Qt.PointingHandCursor
        )

        self.mode_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255,255,255,0.45);
                border-radius: 17px;
                border: none;
                color: #888;
                font-size: 15px;
                                    
                padding-top: 0px;
                padding-right: 0px;
                padding-bottom: 0px;
                padding-left: 0px;
            }

            QPushButton:hover {
                background-color: rgba(220,220,255,0.8);
            }
        """)

        self.mode_btn.clicked.connect(
            self.change_view_mode
        )

        close_btn = QPushButton("✕")

        close_btn.setFixedSize(34, 34)

        close_btn.setCursor(
            Qt.PointingHandCursor
        )

        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255,255,255,0.45);
                border-radius: 17px;
                border: none;
                color: #888;
                font-size: 15px;
                                
                padding-top: 0px;
                padding-right: 0px;
                padding-bottom: 0px;
                padding-left: 0px;
            }

            QPushButton:hover {
                background-color: rgba(255,180,180,0.7);
            }
        """)

        close_btn.clicked.connect(
            self.close
        )

        controls = QHBoxLayout()

        controls.addStretch()
        controls.addWidget(self.mode_btn)
        controls.addWidget(close_btn)

        layout.addLayout(controls)

        # ====================================================
        # AUDIO
        # ====================================================

        


        self.player_end = QSoundEffect()

        self.base_dir = self.configuracao.get_sons_dir()

        audio_path = os.path.join(
            self.base_dir,
            self.configuracao.get_som_arquivo()
        )

        self.player_end.setSource(
            QUrl.fromLocalFile(audio_path)
        )

        self.player_end.setVolume(self.configuracao.get_som_volume() / 100)

        # ====================================================
        # CONEXÕES
        # ====================================================

        self.start_button.clicked.connect(
            self.toggle_timer
        )

        self.save_button.clicked.connect(
            self.save_log
        )

        self.update_display()

        self.input_minutes.clearFocus()
        self.start_button.setFocus()

    # ========================================================
    # DETECTA QUANDO O CRONOMETRO FECHA PARA ABRIR A JANELA MAIN
    # ========================================================

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)

    def update_input_minutes(self):
        try:
            tempo_minutos = int(self.input_minutes.text())
            self.configuracao.alterar_ultimo_timer(tempo_minutos)
            tempo_ms = tempo_minutos * 60 * 1000
            self.time_label.setText(self.format_time(tempo_ms))
        except:
            pass

    # ========================================================
    # FORMATAÇÃO
    # ========================================================

    def format_time(self, ms):

        total_seconds = int(ms // 1000)

        h = total_seconds // 3600
        m = (total_seconds % 3600) // 60
        s = total_seconds % 60

        return f"{h:02}:{m:02}:{s:02}"
    
    # ========================================================
    # TIMER
    # ========================================================

    def update_timer(self):

        step = TIMER_INTERVAL_MS

        # ====================================================
        # ESTUDANDO
        # ====================================================

        if self.running:

            self.study_time_ms += step

            # ------------------------------------------------
            # CONTAGEM NORMAL
            # ------------------------------------------------

            if not self.overtime:

                self.remaining_time_ms -= step

                # entrou no overtime
                if self.remaining_time_ms <= 0:

                    self.remaining_time_ms = 0

                    # toca som uma única vez
                    if not self.played_end_sound:

                        self.played_end_sound = True

                        self.player_end.play()

                    self.overtime = True

                    self.status_label.setText(
                        "OVERTIME"
                    )

            # ------------------------------------------------
            # OVERTIME
            # ------------------------------------------------

            else:

                self.overtime_ms += step

        # ====================================================
        # PAUSADO
        # ====================================================

        else:

            self.pause_time_ms += step

        self.update_display()

    # ========================================================
    # DISPLAY
    # ========================================================

    def update_display(self):

        # ====================================================
        # TIMER PRINCIPAL
        # ====================================================

        if not self.overtime:

            self.time_label.setText(
                self.format_time(
                    self.remaining_time_ms
                )
            )

            progress = (
                self.remaining_time_ms /
                self.total_time_ms
            )

            progress = max(
                0.0,
                min(progress, 1.0)
            )

            self.progress.set_progress(progress)

        else:

            self.time_label.setText(
                "+" + self.format_time(
                    self.overtime_ms
                )
            )

            self.progress.set_progress(
                1.0,
                overtime=True
            )

        # ====================================================
        # LABELS
        # ====================================================

        self.study_label.setText(
            f"Estudo acumulado: "
            f"{self.format_time(self.study_time_ms)}"
        )

        self.pause_label.setText(
            f"Pausa acumulada: "
            f"{self.format_time(self.pause_time_ms)}"
        )

    # ========================================================
    # ESTILO BOTÃO
    # ========================================================

    def estilizar_botao(
        self,
        botao,
        texto,
        cor
    ):

        botao.setText(texto)

        botao.setStyleSheet(f"""
            QPushButton {{
                background-color: {cor};
                border: none;
                border-radius: 22px;
                color: #5f5f5f;
                font-size: 17px;
                font-weight: bold;
                padding: 14px;
            }}

            QPushButton:hover {{
                background-color: rgba(255,255,255,0.55);
            }}

            QPushButton:pressed {{
                padding-top: 16px;
            }}
        """)
    
    # ========================================================
    # START / PAUSE
    # ========================================================

    def toggle_timer(self):

        # ====================================================
        # PRIMEIRA EXECUÇÃO
        # ====================================================

        if (
            self.study_time_ms == 0 and
            self.pause_time_ms == 0 and
            self.remaining_time_ms == self.total_time_ms
        ):

            try:

                minutes = int(
                    self.input_minutes.text()
                )

                if minutes <= 0:
                    raise ValueError

            except:

                QMessageBox.warning(
                    self,
                    "Erro",
                    "Digite um tempo válido."
                )

                return

            self.total_time_ms = (
                minutes * 60 * 1000
            )

            self.remaining_time_ms = (
                self.total_time_ms
            )

        # ====================================================
        # ALTERNA
        # ====================================================

        self.running = not self.running

        # ====================================================
        # TIMER
        # ====================================================

        if not self.timer.isActive():

            self.timer.start(
                TIMER_INTERVAL_MS
            )

        # ====================================================
        # BOTÃO
        # ====================================================

        if self.running:

            self.estilizar_botao(
                self.start_button,
                "PAUSAR",
                "#abc1ffc7"
            )

            self.status_label.setText("FOCO!")

            self.log("ESTUDANDO")

        else:

            self.estilizar_botao(
                self.start_button,
                "RETOMAR",
                "#ffebab"
            )

            self.status_label.setText("PAUSADO")

            self.log("Pausa")

        self.animate_button(self.start_button)

    # ========================================================
    # ANIMAÇÃO
    # ========================================================

    def animate_button(self, button):

        self.anim = QPropertyAnimation(
            button,
            b"minimumSize"
        )

        self.anim.setDuration(180)

        self.anim.setStartValue(
            QSize(0, 58)
        )

        self.anim.setEndValue(
            QSize(0, 64)
        )

        self.anim.setEasingCurve(
            QEasingCurve.OutBack
        )

        self.anim.start()

    # ========================================================
    # lOG
    # ========================================================

    def log(self, text):

        timestamp = datetime.now()

        timestamp_str = timestamp.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        linha = f"{timestamp_str} | {text}"

        self.log_box.append(linha)

        # salva temporariamente na memória
        self.session_logs.append({
            "timestamp": timestamp_str,
            "evento": text
        })

    # ========================================================
    # MODOS DO CRONOMETRO
    # ========================================================

    def change_view_mode(self):

        if self.view_mode == "normal":
            self.set_compact_mode()

        elif self.view_mode == "compact":
            self.set_normal_mode()
            

    def get_hideable_widgets(self):

        return [

            self.title_label,

            self.input_minutes,

            self.progress,

            self.status_label,

            self.study_label,

            self.pause_label,

            self.save_button,

            self.log_box
        ]
    
    def set_normal_mode(self):

        self.view_mode = "normal"

        for w in self.get_hideable_widgets():
            w.show()

        self.setFixedSize(
            self.NORMAL_SIZE
        )

        self.main_layout.setContentsMargins(
            35, 30, 35, 30
        )

        self.time_label.setStyleSheet("""
            color: #5f5f5f;
            background-color: rgba(255,255,255,0.35);
            border-radius: 24px;
            padding: 18px;
        """)

        font = QFont("Arial", 40, QFont.Bold)
        self.time_label.setFont(font)

        self.time_label.setMaximumHeight(
            9999
        )

        self.card.setStyleSheet("""
            QFrame {
                background-color: rgba(245,240,255,185);
                border-radius: 38px;
                border: 1px solid rgba(255,255,255,0.5);
            }
        """)

        self.setWindowOpacity(1.0)

        self.mode_btn.setText("◱")

        # self.start_button.show()

    def set_compact_mode(self):

        self.view_mode = "compact"

        for w in self.get_hideable_widgets():
            w.hide()

        self.setFixedSize(
            self.COMPACT_SIZE
        )

        # margens mínimas
        self.main_layout.setContentsMargins(10, 20, 10, 0) # esquerda topo direita baixo

        self.card.setStyleSheet("""
            QFrame {
                background-color: rgba(245,240,255,185);
                border-radius: 18px;
                border: 1px solid rgba(255,255,255,0.5);
            }
        """)

        self.time_label.setStyleSheet("""
            QLabel {
                color: #5f5f5f;
                background: transparent;
                padding: 0px;
            }
        """)

        font = QFont("Arial", 40, QFont.Bold)
        self.time_label.setFont(font)

        self.setWindowOpacity(0.8)

        self.mode_btn.setText("▣")

    # ========================================================
    # DRAG
    # ========================================================

    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:

            self.drag_pos = (
                event.globalPosition().toPoint()
            )

    def mouseMoveEvent(self, event):

        if event.buttons() == Qt.LeftButton:

            delta = (
                event.globalPosition().toPoint()
                - self.drag_pos
            )

            self.move(
                self.x() + delta.x(),
                self.y() + delta.y()
            )

            self.drag_pos = (
                event.globalPosition().toPoint()
            )

    # ========================================================
    # FUNDO
    # ========================================================

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        painter.setBrush(
            QColor(255, 255, 255, 18)
        )

        painter.setPen(Qt.NoPen)

        painter.drawRoundedRect(
            self.rect(),
            40,
            40
        )

    # ========================================================
    # SALVAR SESSÃO
    # ========================================================

    def save_log(self):

        # CONCLUI O LOG

        if not self.session_logs:
            QMessageBox.warning(
                self,
                "Erro",
                "Nenhuma sessão foi registrada."
            )
            return

        ultimo_evento = self.session_logs[-1]["evento"]
        
        if ultimo_evento == "ESTUDANDO":
            timestamp_str = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            self.session_logs.append({
                "timestamp": timestamp_str,
                "evento": "ENCERRADO_AUTO"
            })

        self.janela_registro = RegistroEstudoWindow()

        # Momento fim da sessão

        dataHora_fim = self.session_logs[-1]["timestamp"]

        hora_fim = QDateTime.fromString(dataHora_fim, "yyyy-MM-dd HH:mm:ss")

        self.janela_registro.momento.setTime(hora_fim.time())

        # Duração

        duracao_str = self.format_time(self.study_time_ms)

        duracao = QTime.fromString(duracao_str)

        self.janela_registro.timer_edit.setTime(duracao)

        # Pausa

        self.janela_registro.DATA_pausa = int(self.pause_time_ms / 1000)

        # Logs

        self.janela_registro.DATA_session_logs = self.session_logs

        # Janela

        self.janela_registro.closed.connect(self.study_saved.emit)

        self.janela_registro.show()

        self.janela_registro.raise_()

        self.janela_registro.activateWindow()


        self.close()
