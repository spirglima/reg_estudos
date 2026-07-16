from PySide6.QtCore import Qt, QTime, QDate, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QButtonGroup,
    QLineEdit,
    QTimeEdit,
    QComboBox,
    QDateEdit,
    QToolButton,
    QFrame,
    QCheckBox,
    QMessageBox
)

from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression

from PySide6.QtWidgets import (
    QDialog,
    QCalendarWidget,
)

from pages.config import ConfigManager
from database.table import DataBaseManager

STYLE = """
QWidget {
    background-color: #eef2f7;
    color: #2d3748;
    font-family: "Segoe UI";
    font-size: 14px;
}

QLabel {
    font-weight: 600;
}

QPushButton {
    background-color: white;
    border: 1px solid #d6dde8;
    border-radius: 8px;
    padding: 8px 14px;
}

QPushButton:hover {
    background-color: #f8fafc;
}

QPushButton:checked {
    background-color: #3b82f6;
    color: white;
    border: none;
}

QLineEdit,
QComboBox,
QTimeEdit,
QDateEdit {
    background-color: white;
    border: 1px solid #d6dde8;
    border-radius: 8px;
    padding: 8px;
}

QToolButton {
    background-color: white;
    border: 1px solid #d6dde8;
    border-radius: 8px;
    padding: 6px;
}

QFrame {
    background-color: white;
    border-radius: 12px;
    border: 1px solid #dfe6ee;
}

QFrame#sectionCard {
    background-color: white;
    border: 1px solid #d6dde8;
    border-radius: 12px;
}

QFrame#sectionCard QLabel.tituloSecao {
    font-size: 15px;
    font-weight: 700;
}

QTimeEdit#timerGrande {
    font-size: 24px;
    font-weight: 600;
    padding: 10px;
}

QCheckBox {
    background: transparent;
    spacing: 8px;
    font-weight: 500;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #d6dde8;
    border-radius: 4px;
    background: white;
}

QCheckBox::indicator:hover {
    border: 1px solid #3b82f6;
}

QCheckBox::indicator:checked {
    background: #3b82f6;
    border: 1px solid #3b82f6;
}

QCheckBox::indicator:disabled {
    background: #e5e7eb;
}

"""


class RegistroEstudoWindow(QWidget):

    closed = Signal()

    # Definição se é uma nova entrada, ou estou apenas editando
    # O padrão é uma nova entrada

    session_id = None # Modificar esse valor apenas se for uma edição de entrada

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Registro de estudo")
        self.resize(600, 420)

        self.setup_ui()

        self.setStyleSheet(STYLE)

    def setup_ui(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)

        frame = QFrame()
        layout_principal.addWidget(frame)

        layout = QVBoxLayout(frame)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # =====================================================
        # VARIÁVEIS
        # =====================================================

        self.configuracao = ConfigManager()

        self.DATA_categoria = None
        self.DATA_disciplina = None
        self.DATA_topico = None
        self.DATA_data_fim = None
        self.DATA_pausa = None
        self.DATA_duracao = None
        self.DATA_session_logs = None

        self.string_categoria = "Selecione uma tag"
        self.string_disciplina = "Selecione a disciplina"
        self.string_topico = "Selecione o tópico"

        # =====================================================
        # DATA
        # =====================================================

        card_data = QFrame()
        card_data.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border: 1px solid #d6dde8;
                border-radius: 10px;
            }
        """)

        layout_data = QVBoxLayout(card_data)
        layout_data.setContentsMargins(15, 15, 15, 15)

        lbl_data = QLabel("Data")
        lbl_data.setStyleSheet("""
            font-size:15px;
            font-weight:700;
            border:none;
            background:transparent;
        """)
        layout_data.addWidget(lbl_data)

        linha_data = QHBoxLayout()

        self.btn_hoje = QPushButton("Hoje")
        self.btn_hoje.setCheckable(True)

        self.btn_ontem = QPushButton("Ontem")
        self.btn_ontem.setCheckable(True)

        self.btn_outro = QPushButton("Outro dia")
        self.btn_outro.setCheckable(True)

        grupo = QButtonGroup(self)
        grupo.setExclusive(True)

        grupo.addButton(self.btn_hoje)
        grupo.addButton(self.btn_ontem)
        grupo.addButton(self.btn_outro)

        self.btn_hoje.setChecked(True)

        linha_data.addWidget(self.btn_hoje)
        linha_data.addWidget(self.btn_ontem)
        linha_data.addWidget(self.btn_outro)

        layout_data.addLayout(linha_data)

        self.widget_data_personalizada = QWidget()

        linha_personalizada = QHBoxLayout(
            self.widget_data_personalizada
        )
        linha_personalizada.setContentsMargins(0, 0, 0, 0)

        self.edit_data = QLineEdit()
        self.edit_data.setPlaceholderText("dd/mm/aaaa")
        self.edit_data.setMaximumWidth(120)

        regex = QRegularExpression(
            r"(0[1-9]|[12][0-9]|3[01])/"
            r"(0[1-9]|1[0-2])/"
            r"\d{4}"
        )

        validator = QRegularExpressionValidator(regex)
        self.edit_data.setValidator(validator)

        self.btn_calendario = QToolButton()
        self.btn_calendario.setText("📅")
        self.btn_calendario.clicked.connect(
            self.abrir_calendario
        )

        linha_personalizada.addWidget(self.edit_data)
        linha_personalizada.addWidget(self.btn_calendario)
        linha_personalizada.addStretch()

        layout_data.addWidget(
            self.widget_data_personalizada,
            alignment=Qt.AlignRight
        )

        self.widget_data_personalizada.hide()

        self.btn_outro.toggled.connect(
            self.widget_data_personalizada.setVisible
        )

        lbl_momento = QLabel("Momento que finalizei o estudo:")
        lbl_momento.setStyleSheet("""
            font-size:12px;
            font-weight:400;
            border:none;
            background:transparent;
        """)

        layout_data.addWidget(lbl_momento)

        self.momento = QTimeEdit()
        self.momento.setDisplayFormat("HH:mm:ss")
        self.momento.setTime(QTime.currentTime())

        self.momento.setAlignment(Qt.AlignCenter)

        layout_data.addWidget(self.momento)

        layout.addWidget(card_data)

        # =====================================================
        # TIMER
        # =====================================================

        card_timer = QFrame()
        card_timer.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border: 1px solid #d6dde8;
                border-radius: 10px;
            }
        """)

        layout_timer = QVBoxLayout(card_timer)
        layout_timer.setContentsMargins(15, 15, 15, 15)

        lbl_timer = QLabel("Tempo estudado")
        lbl_timer.setStyleSheet("""
            font-size:15px;
            font-weight:700;
            border:none;
            background:transparent;
        """)

        layout_timer.addWidget(lbl_timer)

        self.timer_edit = QTimeEdit()
        self.timer_edit.setDisplayFormat("HH:mm:ss")
        self.timer_edit.setMinimumHeight(55)
        self.timer_edit.setAlignment(Qt.AlignCenter)

        self.timer_edit.setStyleSheet("""
            QTimeEdit {
                font-size:24px;
                font-weight:600;
                padding:10px;
            }
        """)

        layout_timer.addWidget(self.timer_edit)

        layout.addWidget(card_timer)

        # =====================================================
        # CONTEÚDO
        # =====================================================

        card_conteudo = QFrame()
        card_conteudo.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border: 1px solid #d6dde8;
                border-radius: 10px;
            }
        """)

        layout_conteudo = QVBoxLayout(card_conteudo)
        layout_conteudo.setContentsMargins(
            15, 15, 15, 15
        )

        lbl_conteudo = QLabel("Conteúdo")
        lbl_conteudo.setStyleSheet("""
            font-size:15px;
            font-weight:700;
            border:none;
            background:transparent;
        """)

        layout_conteudo.addWidget(lbl_conteudo)

        linha_combos = QHBoxLayout()

        self.combo_categoria = QComboBox()
        self.combo_categoria.setMaximumWidth(180)
        self.combo_categoria.addItem(
            self.string_categoria
        )
        self.combo_categoria.addItems(self.configuracao.get_tags())

        self.combo_disciplina = QComboBox()
        self.combo_disciplina.addItem(
            self.string_disciplina
        )
        itens_str = self.configuracao.get_disciplinas()
        itens_str.sort()
        self.combo_disciplina.addItems(itens_str)
        self.combo_disciplina.currentTextChanged.connect(self.atualizar_combo_topico)

        linha_combos.addWidget(
            self.combo_categoria
        )
        linha_combos.addWidget(
            self.combo_disciplina
        )

        layout_conteudo.addLayout(
            linha_combos
        )

        self.combo_topico = QComboBox()
        self.combo_topico.addItem(
            self.string_topico
        )

        layout_conteudo.addWidget(
            self.combo_topico
        )

        # self.check_finalizado = QCheckBox("Finalizado")

        # layout_conteudo.addWidget(self.check_finalizado)

        layout.addWidget(card_conteudo)

        # =====================================================
        # ESPAÇO
        # =====================================================

        layout.addStretch()

        # =====================================================
        # BOTÕES
        # =====================================================

        linha_botoes = QHBoxLayout()
        linha_botoes.addStretch()

        self.btn_cancelar = QPushButton(
            "Cancelar"
        )
        self.btn_cancelar.clicked.connect(self.cancelar)

        self.btn_salvar = QPushButton(
            "Salvar"
        )
        
        self.btn_salvar.clicked.connect(self.salvar_sessao)
        
        linha_botoes.addWidget(
            self.btn_cancelar
        )

        linha_botoes.addWidget(
            self.btn_salvar
        )

        layout.addLayout(linha_botoes)

    def modo_edicao(self):
        self.btn_salvar.clicked.disconnect()
        self.btn_salvar.clicked.connect(lambda: self.editar_sessao(self.session_id))

    def abrir_calendario(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Escolher data")
        dialog.resize(300, 250)

        layout = QVBoxLayout(dialog)

        calendario = QCalendarWidget()
        layout.addWidget(calendario)

        calendario.clicked.connect(
            lambda data: self.selecionar_data(
                data,
                dialog
            )
        )

        dialog.exec()


    def selecionar_data(self, data, dialog):
        self.edit_data.setText(
            data.toString("dd/MM/yyyy")
        )

        dialog.accept()

    def atualizar_combo_topico(self):
        self.combo_topico.clear()
        self.combo_topico.addItem("Selecione o tópico")
        itens = self.configuracao.get_topicos(self.combo_disciplina.currentText())
        itens.sort()
        self.combo_topico.addItems(itens)


    def salvar_sessao(self):

        if self.combo_categoria.currentText() != self.string_categoria:
            self.DATA_categoria = self.combo_categoria.currentText()

        if self.combo_disciplina.currentText() != self.string_disciplina:
            self.DATA_disciplina = self.combo_disciplina.currentText()

        if self.combo_topico.currentText() != self.string_topico:
            self.DATA_topico = self.combo_topico.currentText()

        if self.btn_hoje.isChecked():
            hoje = QDate.currentDate()
            self.DATA_data_fim = hoje.toString("yyyy-MM-dd")
        elif self.btn_ontem.isChecked():
            hoje = QDate.currentDate()
            ontem = hoje.addDays(-1)
            self.DATA_data_fim = ontem.toString("yyyy-MM-dd")
        else:
            outro_dia = QDate.fromString(self.edit_data.text(), "dd/MM/yyyy")
            if not outro_dia.isValid():
                QMessageBox.warning(
                    self,
                    "Erro",
                    "Data inválida."
                )
                return
            self.DATA_data_fim = outro_dia.toString("yyyy-MM-dd")

        self.DATA_data_fim = self.DATA_data_fim + " " + self.momento.text()

        self.DATA_duracao = QTime(0, 0, 0).secsTo(self.timer_edit.time())

        db = DataBaseManager()

        db.add_session(
            self.DATA_categoria,
            self.DATA_disciplina,
            self.DATA_topico,
            self.DATA_data_fim,
            self.DATA_pausa,
            self.DATA_duracao,
            self.DATA_session_logs
        )

        # print(self.DATA_categoria)
        # print(self.DATA_disciplina)
        # print(self.DATA_topico)
        # print(self.DATA_data_fim)
        # print(self.DATA_pausa)
        # print(self.DATA_duracao)
        # print(self.DATA_session_logs)

        self.close()

    def editar_sessao(self, session_id):

        if self.combo_categoria.currentText() != self.string_categoria:
            self.DATA_categoria = self.combo_categoria.currentText()

        if self.combo_disciplina.currentText() != self.string_disciplina:
            self.DATA_disciplina = self.combo_disciplina.currentText()

        if self.combo_topico.currentText() != self.string_topico:
            self.DATA_topico = self.combo_topico.currentText()

        if self.btn_hoje.isChecked():
            hoje = QDate.currentDate()
            self.DATA_data_fim = hoje.toString("yyyy-MM-dd")

        elif self.btn_ontem.isChecked():
            hoje = QDate.currentDate()
            ontem = hoje.addDays(-1)
            self.DATA_data_fim = ontem.toString("yyyy-MM-dd")
        else:
            outro_dia = QDate.fromString(self.edit_data.text(), "dd/MM/yyyy")
            if not outro_dia.isValid():
                QMessageBox.warning(
                    self,
                    "Erro",
                    "Data inválida."
                )
                return
            self.DATA_data_fim = outro_dia.toString("yyyy-MM-dd")

        self.DATA_data_fim = self.DATA_data_fim + " " + self.momento.text()

        self.DATA_duracao = QTime(0, 0, 0).secsTo(self.timer_edit.time())

        db = DataBaseManager()

        db.modify_session(
            session_id,
            self.DATA_categoria,
            self.DATA_disciplina,
            self.DATA_topico,
            self.DATA_data_fim,
            self.DATA_duracao
        )

        # print(self.DATA_categoria)
        # print(self.DATA_disciplina)
        # print(self.DATA_topico)
        # print(self.DATA_data_fim)
        # print(self.DATA_pausa)
        # print(self.DATA_duracao)
        # print(self.DATA_session_logs)

        self.close()

    def cancelar(self):
        self.close()

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)