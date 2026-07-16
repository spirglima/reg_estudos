import sys

from PySide6.QtCore import Qt
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
)

from pages.home_page import HomePage
from pages.disciplinas_page import GerenciadorDisciplinas
from pages.cronograma_page import QuadroSemanal
from pages.historico_page import HistoryPage
from pages.config_page import ConfigPage
from pages.simulados_page import SimuladoPage

from pages.global_style import STYLE

# python3 -m pip list
# python3 -m pip freeze > requirements.txt
# python3 -m pip install -r requirements.txt


# =========================================================
# PÁGINAS GENÉRICAS
# =========================================================

class SimplePage(QWidget):
    def __init__(self, title):
        super().__init__()

        layout = QVBoxLayout(self)

        layout.setContentsMargins(45, 45, 45, 45)
        layout.setSpacing(20)

        label = QLabel(title)
        label.setObjectName("pageTitle")

        subtitle = QLabel("Área em desenvolvimento")

        subtitle.setStyleSheet("""
            color: #6b7280;
            font-size: 15px;
        """)

        layout.addWidget(label)
        layout.addWidget(subtitle)
        layout.addStretch()

# =========================================================
# JANELA PRINCIPAL
# =========================================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Crontrole de Estudos")

        self.resize(1250, 720)

        # tamanho mínimo
        self.setMinimumSize(800, 500)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)

        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # =================================================
        # SIDEBAR
        # =================================================

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")

        sidebar.setFixedWidth(250)

        sidebar_layout = QVBoxLayout(sidebar)

        sidebar_layout.setContentsMargins(14, 22, 14, 22)
        sidebar_layout.setSpacing(16)

        # título
        title = QLabel("Estudos")
        title.setObjectName("title")

        # menu
        self.menu = QListWidget()

        # remove scrollbars
        self.menu.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.menu.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        # menu ocupa todo o espaço vertical
        self.menu.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        menu_items = [
            "Home",
            "Disciplinas",
            "Cronograma",
            "Histórico",
            "Simulados",
            "Estatísticas",
            "Configurações",
        ]

        for item in menu_items:
            QListWidgetItem(item, self.menu)

        self.menu.setCurrentRow(0)

        sidebar_layout.addWidget(title)

        sidebar_layout.addSpacing(8)

        sidebar_layout.addWidget(self.menu)

        # menu cresce verticalmente
        sidebar_layout.setStretchFactor(self.menu, 1)

        # =================================================
        # ÁREA CENTRAL
        # =================================================

        self.pages = QStackedWidget()

        self.pages.addWidget(HomePage())
        self.pages.addWidget(GerenciadorDisciplinas())
        self.pages.addWidget(QuadroSemanal())
        self.pages.addWidget(HistoryPage())
        self.pages.addWidget(SimuladoPage())
        self.pages.addWidget(SimplePage("Estatísticas"))
        self.pages.addWidget(ConfigPage())

        self.menu.currentRowChanged.connect(
            self.pages.setCurrentIndex
        )

        self.menu.currentRowChanged.connect(
            self.change_page
        )

        # =================================================
        # LAYOUT FINAL
        # =================================================

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.pages)

    def change_page(self, index): # ATUALIZAÇÃO DA PAGINA SEMPRE QUE O USUÁRIO ALTERANA # FACILITA QUANDO OCULTAR DISCIPLINAS OU MODIFICAR CONFIGURAÇÕES
        self.pages.setCurrentIndex(index)

        page = self.pages.currentWidget()

        if hasattr(page, "refresh"):
            page.refresh()

# =========================================================
# EXECUÇÃO
# =========================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyleSheet(STYLE)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())