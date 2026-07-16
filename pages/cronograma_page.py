import sys
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QInputDialog,
    QFrame,
    QSizePolicy,
    QMenu,
    QMessageBox
)

from pages.config import ConfigManager


from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QDialogButtonBox
)

DIALOG_STYLE = """
QDialog {
    background-color: #eef2f7;
}

QLabel {
    color: #374151;
    font-size: 13px;
    font-weight: 600;
}

QComboBox {
    background-color: white;

    border: 1px solid #d6dee8;
    border-radius: 14px;

    padding: 10px 14px;

    color: #374151;
}

QComboBox:hover {
    border: 1px solid #bfdbfe;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox QAbstractItemView {
    background-color: white;

    border: 1px solid #d6dee8;
    border-radius: 12px;

    selection-background-color: #dbeafe;
    selection-color: #1d4ed8;

    padding: 4px;
}

QPushButton {
    background-color: white;

    border: 1px solid #d6dee8;
    border-radius: 16px;

    padding: 10px 16px;

    font-size: 15px;

    color: #374151;
}

QPushButton:hover {
    background-color: #f8fbff;
    border: 1px solid #bfdbfe;
    color: #2563eb;
}
"""

class SelecionarDisciplinaDialog(QDialog):

    def __init__(self, disciplinas, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Nova tarefa")
        self.resize(350, 140)
        self.setStyleSheet(DIALOG_STYLE)

        layout = QVBoxLayout(self)

        label = QLabel("Clique para selecionar a disciplina:")
        label.setObjectName("fieldLabel")

        self.combo = QComboBox()
        self.combo.addItems(disciplinas)

        botoes = QDialogButtonBox(
            QDialogButtonBox.Ok |
            QDialogButtonBox.Cancel
        )

        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject)

        layout.addWidget(label)
        layout.addWidget(self.combo)
        layout.addStretch()
        layout.addWidget(botoes)

    def disciplina(self):
        return self.combo.currentText()

class TaskListWidget(QListWidget):

    def __init__(self):
        super().__init__()

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

        self.setDefaultDropAction(Qt.MoveAction)

        self.setDragDropMode(
            QListWidget.InternalMove
        )

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(
            self.show_context_menu
        )

        # Parte que faz a "deseleção" do objeto selecionado
        self._ja_estava_selecionado = False
        self.itemClicked.connect(self.toggle_selection)

        self.model().rowsMoved.connect(self.on_rows_moved)

    

    def on_rows_moved(
        self,
        parent,
        start,
        end,
        destination,
        row
    ): # Salva quando a disciplina é movida na coluna
        coluna = self.parent()

        quadro = coluna.parent()

        quadro.recalcular_horas()
        quadro.salvar_quadro_semanal()

        coluna.imprimir_estado_semana(
            "mover",
            None
        )

    def show_context_menu(self, pos):

        item = self.itemAt(pos)

        if not item:
            return

        menu = QMenu(self)

        # editar = menu.addAction("Editar")

        menu.addSeparator()

        excluir = menu.addAction("Excluir")

        action = menu.exec(
            self.viewport().mapToGlobal(pos)
        )

        if action == excluir:

            disciplina = item.data(Qt.UserRole)

            self.takeItem(self.row(item))

            quadro = self.parent().parent()

            quadro.recalcular_horas()

            # for i in range(self.count()):
            #     print(
            #         i,
            #         self.item(i).data(Qt.UserRole)
            #     )

            quadro.salvar_quadro_semanal()

            self.parent().imprimir_estado_semana(
                "remover",
                disciplina
            )

        # elif action == editar:

        #     text, ok = QInputDialog.getText(
        #         self,
        #         "Editar tarefa",
        #         "Nome da tarefa:",
        #         text=item.text()
        #     )

        #     if ok and text.strip():
        #         item.setText(text.strip())

    def toggle_selection(self, item): # controla a "deseleção do card"
        if self._ja_estava_selecionado:
            self._ja_estava_selecionado = False
            item.setSelected(False)
        else:
            self._ja_estava_selecionado = True



class Coluna_dia(QFrame):
    def __init__(self, title):
        super().__init__()

        self.titulo = title

        self.configuracao = ConfigManager()

        self.setStyleSheet("""
            QFrame {
                background: #ECECEC;
                border-radius: 8px;
            }

            QLabel {
                font-size: 14px;
                font-weight: bold;
            }

            QListWidget {
                background: transparent;
                border: none;
            }

            QListWidget::item {
                background: white;
                border: 1px solid #B0B0B0;
                border-radius: 6px;
                padding: 10px;
                margin: 4px;
            }

            QListWidget::item:selected {
                background: #D7EAFF;
                color: black;
            }

            QPushButton {
                height: 30px;
                font-weight: bold;
            }
        """)

        layout = QVBoxLayout(self)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(title_label)

        self.task_list = TaskListWidget()

        layout.addWidget(self.task_list)

        add_button = QPushButton("+")
        add_button.setObjectName("kanban")
        add_button.clicked.connect(self.add_task)

        layout.addWidget(add_button)

    def add_task(self):

        disciplinas = list(
            self.configuracao.get_disciplinas()
        )

        if not disciplinas:
            QMessageBox.warning(
                self,
                "Aviso",
                "Nenhuma disciplina cadastrada."
            )
            return

        dialog = SelecionarDisciplinaDialog(
            disciplinas,
            self
        )

        if dialog.exec():

            disciplina = dialog.disciplina()

            item = self.criar_item_disciplina(
                disciplina
            )

            self.task_list.addItem(item)

            quadro = self.parent()

            quadro.recalcular_horas()
            quadro.salvar_quadro_semanal()

            meta_semanal = self.configuracao.get_meta_semanal(disciplina) # Retorna o número de horas de estudo semanal para a disciplina

            self.imprimir_estado_semana(
                "adicionar",
                disciplina
            )

        # for i in range(self.task_list.count()):
        #     item = self.task_list.item(i)
        #     print(item.text())
        #     print(item.data(Qt.UserRole))
        #     print(" ")
        #     print("-" * 20)

    def criar_item_disciplina(self, disciplina):

        item = QListWidgetItem()

        item.setData(
            Qt.UserRole,
            disciplina
        )

        item.setText(disciplina)

        return item

    def imprimir_estado_semana(self, acao, disciplina):

        pass

        # print("\n" + "=" * 60)

        # if acao == "adicionar":
        #     print(f"DISCIPLINA ADICIONADA: {disciplina}")
        #     print(f"DIA DA SEMANA: {self.titulo}")

        # elif acao == "remover":
        #     print(f"DISCIPLINA REMOVIDA: {disciplina}")
        #     print(f"DIA DA SEMANA: {self.titulo}")

        # elif acao == "mover":

        #     print("QUADRO MODIFICADO")
        #     print(
        #         f"ALTERAÇÃO OCORREU EM: {self.titulo}"
        # )

        # print("\nDISCIPLINAS DA SEMANA:")

        # quadro = self.parent()

        # for coluna in quadro.findChildren(Coluna_dia):

        #     titulo = (
        #         coluna.layout()
        #         .itemAt(0)
        #         .widget()
        #         .text()
        #     )

        #     print(f"\n[{titulo}]")

        #     if coluna.task_list.count() == 0:
        #         print("  (vazio)")
        #         continue

        #     for i in range(coluna.task_list.count()):

        #         item = coluna.task_list.item(i)

        #         print(
        #             f"{i+1}º -> {item.text()}"
        #         )

        # print("=" * 60 + "\n")

    


    # def dropEvent(self, event): # Detecta o movimento dos cards

    #     super().dropEvent(event)

    #     coluna = self.parent()

    #     quadro = coluna.parent()

    #     quadro.recalcular_horas()
    #     quadro.salvar_quadro_semanal()

    #     coluna.imprimir_estado_semana(
    #         "mover",
    #         None
    #     )


class QuadroSemanal(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Quadro Semanal")
        self.resize(1400, 700)

        self.config = ConfigManager()

        self.layout = QHBoxLayout(self)

    def refresh(self):

        self.config = ConfigManager() # precisa recriar a instância, se não ela pega dados antigos

        self.limpar_layout(self.layout)

        dias_semana = [
            "DOM",
            "SEG",
            "TER",
            "QUA",
            "QUI",
            "SEX",
            "SAB",
        ]

        dias_usuario = self.config.get_dias_estudo_semanal()

        dias_mostrados = [
            dia for dia in dias_semana
            if dia.lower() in dias_usuario
        ]

        # Guardar a referencia das conlunas
        self.colunas = {}

        for dia in dias_mostrados:

            coluna = Coluna_dia(dia)

            coluna.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Expanding
            )

            self.layout.addWidget(coluna)

            self.colunas[dia.lower()] = coluna
        
        # Carrega as disciplinas salvas no json

        for dia in dias_mostrados:

            disciplinas = self.config.get_quadro_semanal(dia.lower())

            coluna = self.colunas[dia.lower()]

            for disciplina in disciplinas:

                item = coluna.criar_item_disciplina(disciplina)

                coluna.task_list.addItem(item)
            
        self.recalcular_horas()

    def limpar_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def recalcular_horas(self):

        disciplinas = {}

        for coluna in self.colunas.values():

        # for coluna in self.findChildren(Coluna_dia):

            for i in range(coluna.task_list.count()):

                item = coluna.task_list.item(i)

                disciplina = item.data(Qt.UserRole)

                disciplinas.setdefault(
                    disciplina,
                    []
                ).append(item)

        for disciplina, itens in disciplinas.items():

            meta = self.config.get_meta_semanal(
                disciplina
            )

            try:
                meta = float(meta)
            except:
                meta = 0

            quantidade = len(itens)

            horas_por_card = (
                meta / quantidade
                if quantidade
                else 0
            )

            for item in itens:

                item.setText(
                    f"{disciplina}\n"
                    f"{horas_por_card:.1f} h"
                )

    def salvar_quadro_semanal(self):

        quadro = {}

        for dia, coluna in self.colunas.items():

            disciplinas = []

            for i in range(coluna.task_list.count()):

                item = coluna.task_list.item(i)

                disciplinas.append(
                    item.data(Qt.UserRole)
                )

            quadro[dia] = disciplinas

        self.config.set_quadro_semanal(quadro)
