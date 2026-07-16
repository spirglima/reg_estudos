import sys

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QMessageBox,
    QInputDialog,
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QDoubleSpinBox,
    QSpinBox,
    QPushButton,
    QColorDialog,
    QHBoxLayout
)

from PySide6.QtGui import QColor, QBrush
from pages.config import ConfigManager

class DisciplinaDialog(QDialog):
    def __init__(
        self,
        nome="",
        cor="#87CEEB",
        meta=1.0,
        peso=5,
        parent=None
    ):
        super().__init__(parent)

        self.setWindowTitle("Disciplina")
        self.setMinimumSize(500, 300)

        self.cor = cor

        layout = QVBoxLayout(self)
        form = QVBoxLayout()

        self.label_nome = QLabel("Nome:")
        self.label_nome.setObjectName("fieldLabel")
        self.label_meta_semanal = QLabel("Meta semanal (horas):")
        self.label_meta_semanal.setObjectName("fieldLabel")
        self.label_peso = QLabel("Peso (1 - 5):")
        self.label_peso.setObjectName("fieldLabel")

        self.nome_edit = QLineEdit(nome)
        self.nome_edit.setStyleSheet("""
            QLineEdit,
            QTimeEdit {
                min-height: 20px;
                padding: 6px 10px;

                border: 1px solid #d1d5db;
                border-radius: 8px;

                background: white;
            }
                           
            QLineEdit:focus,
            QTimeEdit:focus {
                border: 2px solid #60a5fa;
            }
        """)

        self.meta_spin = QDoubleSpinBox()
        self.meta_spin.setRange(0, 1000)
        self.meta_spin.setDecimals(1)
        self.meta_spin.setValue(meta)
        self.meta_spin.setStyleSheet("""
            QSpinBox,
            QDoubleSpinBox {
                min-height: 20px;
                padding: 6px 10px;

                border: 1px solid #d1d5db;
                border-radius: 8px;

                background: white;
            }

            QSpinBox:focus,
            QDoubleSpinBox:focus {
                border: 2px solid #60a5fa;
            }

            QSpinBox::up-button,
            QDoubleSpinBox::up-button,
            QSpinBox::down-button,
            QDoubleSpinBox::down-button {
                width: 18px;
                border: none;
                background: transparent;
            }

            QSpinBox::up-button:hover,
            QDoubleSpinBox::up-button:hover,
            QSpinBox::down-button:hover,
            QDoubleSpinBox::down-button:hover {
                background: #f3f4f6;
            }
        """)

        self.peso_spin = QSpinBox()
        self.peso_spin.setRange(1, 5)
        self.peso_spin.setValue(peso)
        self.peso_spin.setStyleSheet("""
            QSpinBox,
            QDoubleSpinBox {
                min-height: 20px;
                padding: 6px 10px;

                border: 1px solid #d1d5db;
                border-radius: 8px;

                background: white;
            }

            QSpinBox:focus,
            QDoubleSpinBox:focus {
                border: 2px solid #60a5fa;
            }

            QSpinBox::up-button,
            QDoubleSpinBox::up-button,
            QSpinBox::down-button,
            QDoubleSpinBox::down-button {
                width: 18px;
                border: none;
                background: transparent;
            }

            QSpinBox::up-button:hover,
            QDoubleSpinBox::up-button:hover,
            QSpinBox::down-button:hover,
            QDoubleSpinBox::down-button:hover {
                background: #f3f4f6;
            }
        """)

        self.btn_cor = QPushButton("Escolher cor")
        self.btn_cor.setStyleSheet(None)
        self.btn_cor.clicked.connect(self.escolher_cor)

        form.addWidget(self.label_nome)
        form.addWidget(self.nome_edit)
        form.addWidget(self.btn_cor)
        form.addWidget(self.label_meta_semanal)
        form.addWidget(self.meta_spin)
        form.addWidget(self.label_peso)
        form.addWidget(self.peso_spin)

        layout.addLayout(form)

        botoes = QHBoxLayout()

        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Cancelar")

        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        botoes.addWidget(btn_cancel)
        botoes.addWidget(btn_ok)

        layout.addLayout(botoes)

    def escolher_cor(self):
        cor = QColorDialog.getColor(QColor(self.cor), self)

        if cor.isValid():
            self.cor = cor.name()

    def dados(self):
        return {
            "nome": self.nome_edit.text().strip(),
            "cor": self.cor,
            "meta_semanal": self.meta_spin.value(),
            "peso": self.peso_spin.value(),
        }


class GerenciadorDisciplinas(QWidget):
    def __init__(self):
        super().__init__()

        # self.setWindowTitle("Disciplinas e Tópicos")
        # self.resize(700, 500)

        self.configuracao = ConfigManager()

        self.tree = QTreeWidget()
        self.tree.setSortingEnabled(True)
        self.tree.setHeaderLabels([
            "Nome",
            "Meta (h)",
            "Peso (1 - 5)",
            "Cor",
            "Ocultar nas análises?"
        ])
        self.tree.setColumnWidth(0, 450)
        self.tree.setColumnWidth(1, 80)
        self.tree.setColumnWidth(2, 100)
        self.tree.setColumnWidth(3, 120)
        self.tree.setColumnWidth(4, 70)

        # Botões
        self.btn_add_disciplina = QPushButton("Nova disciplina")
        self.btn_add_topico = QPushButton("Novo tópico")
        self.btn_renomear = QPushButton("Modificar")
        self.btn_remover = QPushButton("Remover")
        self.btn_ocultar = QPushButton("Ocultar / Mostrar")

        self.btn_renomear.setEnabled(False)
        self.btn_remover.setEnabled(False)
        self.btn_ocultar.setEnabled(False)

        botoes = QHBoxLayout()
        botoes.addWidget(self.btn_add_disciplina)
        botoes.addWidget(self.btn_add_topico)
        botoes.addWidget(self.btn_renomear)
        botoes.addWidget(self.btn_remover)
        botoes.addWidget(self.btn_ocultar)

        layout = QVBoxLayout(self)
        layout.addWidget(self.tree)
        layout.addLayout(botoes)

        self.btn_add_disciplina.clicked.connect(self.adicionar_disciplina)
        self.btn_add_topico.clicked.connect(self.adicionar_topico)
        self.btn_renomear.clicked.connect(self.renomear_item)
        self.btn_remover.clicked.connect(self.remover_item)
        self.btn_ocultar.clicked.connect(self.alternar_oculto)

        self.tree.itemSelectionChanged.connect(
            self.atualizar_estado_botoes
        )

    # ------------------------------------------------------------------

    def adicionar_disciplina(self):

        dialog = DisciplinaDialog(parent=self)

        if dialog.exec() != QDialog.Accepted:
            return

        dados = dialog.dados()

        if not dados["nome"]:
            return

        item = QTreeWidgetItem([
            dados["nome"],
            str(dados["meta_semanal"]),
            str(dados["peso"]),
            "■"  * dados["peso"],
            "Não"
        ])

        fonte = item.font(3)  # coluna Cor
        fonte.setPointSize(16)
        item.setFont(3, fonte)

        item.setForeground(
            3,
            QBrush(QColor(dados["cor"]))
        )

        item.setData(0, 1, False)

        item.setData(0, 32, {
            "cor": dados["cor"],
            "meta_semanal": dados["meta_semanal"],
            "peso": dados["peso"]
        })

        self.configuracao.add_disciplina(dados["nome"], dados["cor"], dados["meta_semanal"], dados["peso"], 0)

        self.tree.addTopLevelItem(item)

    # ------------------------------------------------------------------

    def adicionar_topico(self):
        item = self.tree.currentItem()

        # if item is None:
        #     return

        if item is None:
            QMessageBox.warning(
                self,
                "Aviso",
                "Selecione uma disciplina."
            )
            return
        
        disciplina = item.text(0)

        # Se estiver em um tópico, pega a disciplina pai
        if item.parent():
            item = item.parent()

        nome, ok = QInputDialog.getText(
            self,
            "Novo tópico",
            "Nome do tópico:"
        )

        if not ok or not nome.strip():
            return
        
        self.configuracao.add_topico(disciplina, nome)

        topico = QTreeWidgetItem([nome.strip(), "", "", "", ""])
        topico.setData(0, 1, False)

        item.addChild(topico)
        item.setExpanded(True)

    # ------------------------------------------------------------------

    def renomear_item(self):
        item = self.tree.currentItem()

        if item is None:
            return

        if item.parent() is None:

            disciplina_antiga = item.text(0)

            info = item.data(0, 32) or {}

            dialog = DisciplinaDialog(
                nome=item.text(0),
                cor=info.get("cor", "#87CEEB"),
                meta=info.get("meta_semanal", 10),
                peso=info.get("peso", 1),
                parent=self
            )

            if dialog.exec() != QDialog.Accepted:
                return

            dados = dialog.dados()

            if not dados["nome"]:
                return
            
            self.configuracao.rename_disciplina(disciplina_antiga, dados["nome"])
            item.setText(0, dados["nome"])

            self.configuracao.set_meta_semanal(dados["nome"], dados["meta_semanal"])
            item.setText(1, str(dados["meta_semanal"]))

            self.configuracao.set_peso_disciplina(dados["nome"], dados["peso"])
            item.setText(2, str(dados["peso"]))

            self.configuracao.set_cor_disciplina(dados["nome"], dados["cor"])

            item.setData(0, 32, {
                "cor": dados["cor"],
                "meta_semanal": dados["meta_semanal"],
                "peso": dados["peso"]
            })
            item.setForeground(
                3,
                QBrush(QColor(dados["cor"]))
            )
            item.setText(
                3,
                "■" * dados["peso"]
            )
            fonte = item.font(3) # coluna cor
            fonte.setPointSize(16)
            item.setFont(3, fonte)
        else:
            disciplina = item.parent().text(0)
            topico_antigo = item.text(0)
            
            topico_novo, ok = QInputDialog.getText(
                self,
                "Renomear tópico",
                "Novo nome:",
                text=item.text(0)
            )

            self.configuracao.rename_topico(disciplina, topico_antigo, topico_novo)

            if ok and topico_novo.strip():
                item.setText(0, topico_novo.strip())

    # ------------------------------------------------------------------

    def remover_item(self):
        item = self.tree.currentItem()

        if item is None:
            return

        resposta = QMessageBox.question(
            self,
            "Confirmação",
            f"Remover '{item.text(0)}'?"
        )

        if resposta != QMessageBox.Yes:
            return

        pai = item.parent()

        if pai:
            # Remove o tópico
            self.configuracao.remove_topico(pai.text(0), item.text(0))
            pai.removeChild(item)
            
        else:
            # Remove a disciplina
            self.configuracao.remove_disciplina(item.text(0))
            indice = self.tree.indexOfTopLevelItem(item)
            self.tree.takeTopLevelItem(indice)


    # ------------------------------------------------------------------

    def alternar_oculto(self):
        item = self.tree.currentItem()

        if item is None:
            return

        # ------------------------------------------------------------------
        # DISCIPLINA
        # ------------------------------------------------------------------
        if item.parent() is None:

            novo_estado = not item.data(0, 1)

            self.configuracao.set_oculto_disciplina(item.text(0), novo_estado)

            item.setData(0, 1, novo_estado)
            item.setText(4, "Sim" if novo_estado else "Não")

            if novo_estado:
                item.setForeground(0, self.palette().mid())
            else:
                item.setForeground(0, self.palette().text())

        # ------------------------------------------------------------------
        # TÓPICO
        # ------------------------------------------------------------------
        else:
            pass

            # QMessageBox.information(
            #     self,
            #     "Aviso",
            #     "O atributo 'Oculto' só pode ser aplicado às disciplinas."
            # )

    # ------------------------------------------------------------------

    def atualizar_estado_botoes(self): # Habilita/Desabilita os botões: Modificar, Remover e Ocultar
        item = self.tree.currentItem()

        habilitado = item is not None

        self.btn_renomear.setEnabled(habilitado)
        self.btn_remover.setEnabled(habilitado)
        self.btn_ocultar.setEnabled(habilitado)

    def refresh(self): # Atualiza os dados da aba sempre que o usuário abrir ela novamente
        self.tree.clear()

        config = ConfigManager().config

        disciplinas = config.get("disciplinas", {})

        for nome_disciplina, dados in disciplinas.items():

            # Cria a disciplina
            item = QTreeWidgetItem([
                nome_disciplina,
                str(dados.get("meta_semanal", 0)),
                str(dados.get("peso", 1)),
                "■" * int(dados.get("peso", 1)),
                "Sim" if dados.get("oculto", 0) else "Não"
            ])

            fonte = item.font(3)
            fonte.setPointSize(16)
            item.setFont(3, fonte)

            item.setForeground(
                3,
                QBrush(QColor(dados.get("cor", "#FFFFFF")))
            )

            item.setData(
                0,
                1,
                bool(dados.get("oculto", 0))
            )

            item.setData(
                0,
                32,
                {
                    "cor": dados.get("cor", "#FFFFFF"),
                    "meta_semanal": dados.get("meta_semanal", 0),
                    "peso": dados.get("peso", 1)
                }
            )

            self.tree.addTopLevelItem(item)

            # Cria os tópicos da disciplina
            for nome_topico in dados.get("topicos", []):

                topico = QTreeWidgetItem([
                    nome_topico,
                    "",
                    "",
                    "",
                    ""
                ])

                topico.setData(0, 1, False)

                item.addChild(topico)

            item.setExpanded(False)