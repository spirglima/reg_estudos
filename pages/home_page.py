
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QDateEdit
)

from PySide6.QtCore import QDate

from pages.config import ConfigManager
from pages.graphics import StudyViewer
from windows.add_estudos import RegistroEstudoWindow
from windows.Cronometro import FocusTimer
from database.table import DataBaseManager


# =========================================================
# HOME
# =========================================================

class HomePage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # layout.setContentsMargins(45, 45, 45, 45)
        # layout.setSpacing(18)

        # Mensagem de início:

        self.subtitle = QLabel()

        self.subtitle.setStyleSheet("""
            color: #6b7280;
            font-size: 15px;
        """)

        layout.addWidget(self.subtitle)

        layout.addSpacing(20)

        # botões de ação

        top = QHBoxLayout()

        self.btn_add = QPushButton("Adicionar estudo")
        self.btn_add.clicked.connect(self.add_estudo)

        self.btn_timer = QPushButton("Cronômetro")
        self.btn_timer.clicked.connect(self.cronometro)

        top.addWidget(self.btn_add)
        top.addWidget(self.btn_timer)

        top.addStretch()

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.dateChanged.connect(self.refresh)

        top.addWidget(self.date_edit)

        layout.addLayout(top)

        self.chart_widget = StudyViewer()
        # Tem que ser enviada a data
        # self.chart_widget(data)

        layout.addWidget(
            self.chart_widget,
            1
        )

        layout.addStretch()

        self.refresh()

    def add_estudo(self):
        self.janela_registro = RegistroEstudoWindow()
        self.janela_registro.closed.connect(self.refresh)
        self.janela_registro.show()

    def cronometro(self):
        self.janela_cronometro = FocusTimer()
        
        self.window().hide() # esconde a janela principal

        self.janela_cronometro.closed.connect(self.window().show)

        self.janela_cronometro.study_saved.connect(self.refresh)
        
        self.janela_cronometro.show()

    def refresh(self):
        self.configuracao = ConfigManager()
        self.database = DataBaseManager()

        usuario = self.configuracao.config["usuario"]

        self.subtitle.setText(
            f"Bem-vindo {usuario}!"
        )

        selected_date = self.date_edit.date().toString("yyyy-MM-dd")

        self.chart_widget.generate_chart(selected_date)

