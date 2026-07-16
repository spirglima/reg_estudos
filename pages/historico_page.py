import sqlite3
from pathlib import Path
from datetime import timedelta, datetime

from PySide6.QtCore import Qt, Signal, QDate, QDateTime, QTime
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QScrollArea,
    QSizePolicy,
    QDateEdit,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem
)

from pages.config import ConfigManager
from database.table import DataBaseManager
from windows.add_estudos import RegistroEstudoWindow

class JanelaLogs(QWidget):
    def __init__(self, logs):
        super().__init__()

        self.setWindowTitle("Histórico de Eventos")
        self.resize(340, 300)

        layout = QVBoxLayout(self)

        tabela = QTableWidget()
        tabela.setColumnCount(3)
        tabela.setHorizontalHeaderLabels(["Data", "Hora", "Evento"])
        tabela.setRowCount(len(logs))

        for linha, log in enumerate(logs):
            dt = datetime.strptime(
                log["timestamp"],
                "%Y-%m-%d %H:%M:%S"
            )

            tabela.setItem(
                linha, 0,
                QTableWidgetItem(dt.strftime("%d/%m/%Y"))
            )

            tabela.setItem(
                linha, 1,
                QTableWidgetItem(dt.strftime("%H:%M:%S"))
            )

            tabela.setItem(
                linha, 2,
                QTableWidgetItem(log["evento"])
            )

        tabela.resizeColumnsToContents()
        layout.addWidget(tabela)

# =========================================================
# CARD DE SESSÃO
# =========================================================

class SessionCard(QFrame):

    open_log_requested = Signal(int)
    edit_requested = Signal(int)
    delete_requested = Signal(int)

    def __init__(self, session_data):
        super().__init__()

        self.setStyleSheet("background-color: #ffffff;")

        self.session_data = session_data
        self.session_id = session_data["id"]

        self.setObjectName("sessionCard")

        layout = QVBoxLayout(self)

        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # -------------------------------------------------
        # Informações
        # -------------------------------------------------

        disciplina = QLabel(
            f"{session_data['disciplina']} - "
            f"{session_data['topico']}"
        )

        disciplina.setStyleSheet("""
            font-size:16px;
            font-weight:600;
        """)

        categoria = QLabel(
            f"Categoria: {session_data['categoria']}"
        )

        data_fim = QLabel(
            f"Data: {session_data['data_fim']}"
        )

        temp_int = int(session_data['duracao_segundos'])
        temp_str = self.duracao_formatada(temp_int)

        duracao = QLabel(
            f"Duração: {temp_str}"
        )

        layout.addWidget(disciplina)
        layout.addWidget(categoria)
        layout.addWidget(data_fim)
        layout.addWidget(duracao)

        # -------------------------------------------------
        # Botões
        # -------------------------------------------------

        button_layout = QHBoxLayout()

        btn_log = QPushButton("📂 log")
        btn_edit = QPushButton("✏️ editar")
        btn_delete = QPushButton("🗑️ excluir")

        btn_log.clicked.connect(
            lambda: self.open_log_requested.emit(
                self.session_id
            )
        )

        btn_edit.clicked.connect(
            lambda: self.edit_requested.emit(
                self.session_id
            )
        )

        btn_delete.clicked.connect(
            lambda: self.delete_requested.emit(
                self.session_id
            )
        )

        button_layout.addWidget(btn_log)
        button_layout.addWidget(btn_edit)
        button_layout.addWidget(btn_delete)

        button_layout.addStretch()

        layout.addLayout(button_layout)

    def duracao_formatada(self, temp_segundos):
        horas = temp_segundos // 3600
        minutos = (temp_segundos % 3600) // 60
        segundos = temp_segundos % 60

        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

# =========================================================
# HISTÓRICO
# =========================================================

class HistoryPage(QWidget):

    def __init__(self):
        super().__init__()

        self.database = DataBaseManager()

        layout = QVBoxLayout(self)

        layout.setContentsMargins(45, 45, 45, 45)
        layout.setSpacing(20)

        # =================================================
        # CABEÇALHO
        # =================================================

        header = QHBoxLayout()

        title = QLabel("Histórico")
        title.setObjectName("pageTitle")

        header.addWidget(title)
        header.addStretch()

        self.date_edit = QDateEdit()
        # self.date_edit.dateChanged.connect(self.refresh)

        self.date_edit.setCalendarPopup(True)

        self.date_edit.setDate(
            QDate.currentDate()
        )

        # self.date_edit.dateChanged.connect(
        #     self.refresh
        # )

        header.addWidget(self.date_edit)

        layout.addLayout(header)

        # =================================================
        # CONTADOR
        # =================================================

        self.info_label = QLabel(
            "Sessões encontradas: 0"
        )

        layout.addWidget(self.info_label)

        # =================================================
        # ÁREA ROLÁVEL
        # =================================================

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        self.container = QWidget()

        self.sessions_layout = QVBoxLayout(
            self.container
        )

        self.sessions_layout.setSpacing(15)

        self.sessions_layout.addStretch()

        scroll.setWidget(self.container)

        layout.addWidget(scroll)

        self.date_edit.dateChanged.connect(self.refresh) # Não tente mudar a posição dessa instrução. Ela chama funções onde pode ter elementos ainda não criados

        self.refresh()


    def clear_cards(self):

        if not hasattr(self, "sessions_layout"):
            return

        while self.sessions_layout.count() > 1:

            item = self.sessions_layout.takeAt(0)

            widget = item.widget()

            if widget:
                widget.deleteLater()

    def open_log(self, session_id):

        logs = self.database.get_log_session(session_id)

        self.janela_logs_ = JanelaLogs(logs)

        self.janela_logs_.show()

        # QMessageBox.information(
        #     self,
        #     "Log",
        #     f"Abrir logs da sessão {session_id}"
        # )

    def format_time(self, total_seconds):

        h = total_seconds // 3600
        m = (total_seconds % 3600) // 60
        s = total_seconds % 60

        return f"{h:02}:{m:02}:{s:02}"

    def edit_session(self, session_id):

        self.janela_edicao = RegistroEstudoWindow()
        self.janela_edicao.closed.connect(self.refresh)
        self.janela_edicao.session_id = session_id
        self.janela_edicao.modo_edicao()

        session = self.database.get_session_session(session_id)

        fim = QDateTime.fromString(session[0]["data_fim"], "yyyy-MM-dd HH:mm:ss")

        if QDate.currentDate() == fim.date():
            self.janela_edicao.btn_hoje.setChecked(True)
        elif QDate.currentDate().addDays(-1) == fim.date():
            self.janela_edicao.btn_ontem.setChecked(True)
        else:
            self.janela_edicao.btn_outro.setChecked(True)
            fim_formatado = fim.toString("dd/MM/yyyy")
            self.janela_edicao.edit_data.setText(fim_formatado)

        self.janela_edicao.momento.setTime(fim.time())

        duracao_str = self.format_time(int(session[0]["duracao_segundos"]))
        duracao_qtime = QTime.fromString(duracao_str)

        self.janela_edicao.timer_edit.setTime(duracao_qtime)

        id_categoria = self.janela_edicao.combo_categoria.findText(session[0]["categoria"])
        id_disciplina = self.janela_edicao.combo_disciplina.findText(session[0]["disciplina"])
        

        if id_categoria >= 0:
            self.janela_edicao.combo_categoria.setCurrentIndex(id_categoria)
        else:
            self.janela_edicao.combo_categoria.setCurrentIndex(-1)

        if id_disciplina >= 0:
            self.janela_edicao.combo_disciplina.setCurrentIndex(id_disciplina)
            self.janela_edicao.atualizar_combo_topico()
        else:
            self.janela_edicao.combo_disciplina.setCurrentIndex(-1)

        
        id_topico = self.janela_edicao.combo_topico.findText(session[0]["topico"])

        if id_topico >= 0:
            self.janela_edicao.combo_topico.setCurrentIndex(id_topico)
        else:
            self.janela_edicao.combo_topico.setCurrentIndex(-1)

        self.janela_edicao.show()
        self.janela_edicao.raise_()
        self.janela_edicao.activateWindow()





    def delete_session(self, session_id):

        resposta = QMessageBox.question(
            self,
            "Confirmar",
            "Deseja apagar esta sessão?"
        )

        if resposta != QMessageBox.Yes:
            return
        
        remocao_completa = self.database.remove_session_completa(session_id)

        if remocao_completa:
            QMessageBox.information(
                self,
                "Removido",
                f"Sessão removida."
            )
        else:
            QMessageBox.warning(
                self,
                "Erro",
                f"Sessão não encontrada."
            )

        self.refresh()


    def refresh(self):

        self.clear_cards()

        selected_date = (
            self.date_edit.date()
            .toString("yyyy-MM-dd")
        )

        sessions = self.database.get_session_dia(selected_date)

        if self.date_edit.date() == QDate.currentDate():

            self.info_label.setText(
                f"Sessões de HOJE: {len(sessions)}"
            )
        else:
            self.info_label.setText(
                f"Sessões: {len(sessions)}"
            )

        for session in sessions:

            card = SessionCard(session)

            card.open_log_requested.connect(
                self.open_log
            )

            card.edit_requested.connect(
                self.edit_session
            )

            card.delete_requested.connect(
                self.delete_session
            )

            self.sessions_layout.insertWidget(
                self.sessions_layout.count() - 1,
                card
            )