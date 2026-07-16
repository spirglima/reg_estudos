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

from windows.Contador_questoes import Contador_de_questoes

# =========================================================
# HOME
# =========================================================

class SimuladoPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # botões de ação

        top = QHBoxLayout()

        self.btn_addSimulado = QPushButton("Adicionar simulado")
        self.btn_addSimulado.clicked.connect(self.add_simulado)

        # self.btn_timer = QPushButton("Cronômetro")
        # self.btn_timer.clicked.connect(self.cronometro)

        top.addWidget(self.btn_addSimulado)
        # top.addWidget(self.btn_timer)

        top.addStretch()

        # self.date_edit = QDateEdit()
        # self.date_edit.setCalendarPopup(True)
        # self.date_edit.setDate(QDate.currentDate())
        # self.date_edit.dateChanged.connect(self.refresh)

        # top.addWidget(self.date_edit)

        layout.addLayout(top)

        # self.chart_widget = StudyViewer()

        # layout.addWidget(
        #     self.chart_widget,
        #     1
        # )

        layout.addStretch()

    def add_simulado(self):
        self.janela_simulado = Contador_de_questoes()
        
        self.window().hide() # esconde a janela principal

        self.janela_simulado.closed.connect(self.window().show)
        
        self.janela_simulado.show()