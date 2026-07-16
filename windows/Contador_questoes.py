import sys
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QPushButton,
    QLabel,
    QLineEdit,
    QSpinBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea
)


from windows.grafico_questoes import StatisticsWindow
from pages.config import ConfigManager

class GridGroup(QFrame):
    clicked = Signal(object)

    def __init__(self, titulo):
        super().__init__()

        self.titulo = QLabel(f"<b>{titulo}</b>")
        self.titulo.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: 600;
                color: #4A4A4A;
                padding: 2px;
            }
        """)

        self.grid = QGridLayout()

        layout = QVBoxLayout(self)
        layout.addWidget(self.titulo)
        layout.addLayout(self.grid)

        self.max_col = 5

        self.set_selected(False)

    def mousePressEvent(self, event):
        self.clicked.emit(self)
        super().mousePressEvent(event)

    def set_selected(self, value):
        if value:
            self.setStyleSheet("""
                QFrame{
                    background:#dce7ef;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame{
                    background:white;
                }
            """)

    def add_widget(self, widget):
        count = self.grid.count()

        row = count // self.max_col
        col = count % self.max_col

        self.grid.addWidget(widget, row, col)

class QuestionButton(QPushButton):

    changed = Signal()

    def __init__(self, numero, correta=True):
        super().__init__(str(numero))

        self.setFixedSize(45, 45)

        self.correta = correta
        self.atualizar_estilo()

        self.clicked.connect(self.alternar)

    def alternar(self):
        self.correta = not self.correta
        self.atualizar_estilo()
        self.changed.emit()

    def atualizar_estilo(self):
        cor = "#6FCF97" if self.correta else "#FF8B94"

        self.setStyleSheet(f"""
            QPushButton {{
                background: {cor};
                border:none;
                border-radius:8px;
                font-weight:bold;
            }}

            QPushButton:hover {{
                border:2px solid black;
            }}
        """)

class Contador_de_questoes(QWidget):

    closed = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Contador de questões")
        self.resize(850, 450)

        self.selected_group = None
        self.group_count = 1

        main_layout = QHBoxLayout(self)

        self.statistics_window = StatisticsWindow()

        self.altura_btn = 40
        self.largura_btn = 400

        self.configuracao = ConfigManager()

        ##################################################
        # Painel esquerdo
        ##################################################

        left = QVBoxLayout()

        # ===== Labels =====
        self.label_add_disciplina = QLabel("Adicionar disciplina:")

        self.label_certas = QLabel("Certas")
        self.label_erradas = QLabel("Erradas")

        for label in (self.label_certas, self.label_erradas, self.label_add_disciplina):
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-size: 16px; color:#555;")

        # ===== Combo e btn add disciplina =====

        self.combo_disciplina = QComboBox()
        itens_str = self.configuracao.get_disciplinas()
        itens_str.sort()
        self.combo_disciplina.addItems(itens_str)

        self.btn_new_group = QPushButton("⮞")
        self.btn_new_group.setFixedWidth(50)
        self.btn_new_group.setStyleSheet("font-size:14px; font-weight: bold;")

        self.btn_new_group.clicked.connect(lambda: self.new_group(self.combo_disciplina.currentText()))

        layout_add_disciplina = QHBoxLayout()
        layout_add_disciplina.addWidget(self.combo_disciplina)
        layout_add_disciplina.addWidget(self.btn_new_group)

        # ===== SpinBoxes (somente leitura) =====

        self.spin_certas = QSpinBox()
        self.spin_erradas = QSpinBox()

        for spin in (self.spin_certas, self.spin_erradas):
            spin.setRange(0, 100000)
            spin.setAlignment(Qt.AlignCenter)
            spin.setButtonSymbols(QSpinBox.NoButtons)
            spin.setReadOnly(True)
            spin.setFixedHeight(55)
            spin.setStyleSheet("""
                QSpinBox {
                    font-size: 22px;
                    border-radius: 10px;
                    padding: 8px;
                    background-color: #f5f5f5;
                    border: 2px solid #ddd;
                }
            """)

        # ===== Botões principais =====

        self.btn_certas = QPushButton("+1 Certa (C)")
        self.btn_erradas = QPushButton("+1 Errada (V)")

        self.btn_certas.setShortcut("c")
        self.btn_erradas.setShortcut("v")

        self.btn_certas.clicked.connect(lambda: self.add_question(True))
        self.btn_erradas.clicked.connect(lambda: self.add_question(False))

        self.btn_certas.setStyleSheet(self.estilo_botao("#a8e6cf", "#6fcf97"))
        self.btn_erradas.setStyleSheet(self.estilo_botao("#ffaaa5", "#ff8b94"))

        

        for btn in (self.btn_certas, self.btn_erradas):
            btn.setMinimumHeight(60)
            btn.setCursor(Qt.PointingHandCursor)

        # ===== Botão Remover =====

        self.btn_remove_disciplina = QPushButton("Remover disciplina")
        self.btn_remove_disciplina.clicked.connect(self.remove_selected_group)

        self.btn_remove_question = QPushButton("Remover questão")
        self.btn_remove_question.clicked.connect(self.remove_last_question)

        for btn in (self.btn_remove_question, self.btn_remove_disciplina):
            btn.setFixedHeight(self.altura_btn)
            btn.setFixedWidth(self.largura_btn/2)
            btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                border-radius: 8px;
                background-color: #eeeeee;
                color: #555;
            }
            QPushButton:hover {
                background-color: #dddddd;
            }
        """)

        # ===== Botão YAML =====

        self.btn_yaml = QPushButton("Copiar YAML")
        self.btn_yaml.clicked.connect(self.gerar_yaml)
        # self.btn_yaml.setFixedHeight(35)
        self.btn_yaml.setFixedSize( self.largura_btn, self.altura_btn)
        self.btn_yaml.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                border-radius: 8px;
                background-color: #d0e6ff;
                color: #333;
            }
            QPushButton:hover {
                background-color: #bcdcff;
            }
        """)

        # ===== Métricas =====

        self.label_total = QLabel("Questões total: 0")
        self.label_rendimento = QLabel("Rendimento total: 0%")

        self.label_total.setAlignment(Qt.AlignCenter)
        self.label_rendimento.setAlignment(Qt.AlignCenter)

        self.label_total.setStyleSheet("font-size: 16px; color: #666;")
        self.label_rendimento.setStyleSheet("font-size: 20px; font-weight: bold;")

        # ===== Gráfico =====

        self.btn_grafico = QPushButton("Gráfico")
        self.btn_grafico.clicked.connect(self.abrir_estatisticas)
        self.btn_grafico.setFixedSize(self.largura_btn, self.altura_btn)
        self.btn_grafico.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                border-radius: 8px;
                background-color: #d0e6ff;
                color: #333;
            }
            QPushButton:hover {
                background-color: #bcdcff;
            }
        """)

        # ===== Salvar =====

        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.clicked.connect(self.salvar_simulado)
        self.btn_salvar.setFixedSize(self.largura_btn, self.altura_btn)
        self.btn_salvar.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                border-radius: 8px;
                background-color: #dee6ff;
                color: #333;
            }
            QPushButton:hover {
                background-color: #bcdcff;
            }
        """)

        # ===== Layouts =====

        layout_certas = QVBoxLayout()
        layout_certas.addWidget(self.label_certas)
        layout_certas.addWidget(self.spin_certas)
        layout_certas.addWidget(self.btn_certas)

        layout_erradas = QVBoxLayout()
        layout_erradas.addWidget(self.label_erradas)
        layout_erradas.addWidget(self.spin_erradas)
        layout_erradas.addWidget(self.btn_erradas)

        layout_linha = QHBoxLayout()
        layout_linha.addLayout(layout_certas)
        layout_linha.addLayout(layout_erradas)

        # -----------------------

        layout_remove = QHBoxLayout()
        layout_remove.addWidget(self.btn_remove_disciplina)
        layout_remove.addWidget(self.btn_remove_question)

        # -----------------------

        left.addWidget(self.label_add_disciplina)
        left.addLayout(layout_add_disciplina)
        left.addSpacing(15)
        left.addLayout(layout_linha)
        left.addSpacing(15)
        left.addWidget(self.label_total)
        left.addSpacing(15)
        left.addWidget(self.label_rendimento)
        left.addStretch(15)
        left.addWidget(self.btn_grafico)
        left.addWidget(self.btn_yaml)
        left.addLayout(layout_remove)
        left.addWidget(self.btn_salvar)
        

        ##################################################
        # Área de trabalho
        ##################################################

        self.container = QWidget()
        self.groups_layout = QVBoxLayout(self.container)
        self.groups_layout.setAlignment(Qt.AlignTop)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.container)

        ##################################################

        main_layout.addLayout(left, 1)
        main_layout.addWidget(scroll, 1)

        ##################################################


    def new_group(self, disciplina):

        group = GridGroup(f"{disciplina}")
        self.group_count += 1

        group.clicked.connect(self.select_group)

        self.groups_layout.addWidget(group)

        self.select_group(group)


    def select_group(self, group):

        if self.selected_group:
            self.selected_group.set_selected(False)

        self.selected_group = group
        self.selected_group.set_selected(True)

    def remove_selected_group(self):

        if self.selected_group is None:
            return

        group = self.selected_group

        self.groups_layout.removeWidget(group)

        group.deleteLater()

        self.selected_group = None

        # Seleciona o primeiro grupo restante
        if self.groups_layout.count():
            novo = self.groups_layout.itemAt(0).widget()
            self.select_group(novo)
        
        self.atualizar_estatisticas()


    def add_question(self, correta):

        if not self.selected_group:
            return

        count = self.selected_group.grid.count() + 1

        button = QuestionButton(count, correta)
        button.changed.connect(self.atualizar_estatisticas)
        button.setFixedSize(50, 50)

        self.selected_group.add_widget(button)

        self.atualizar_estatisticas()


    def remove_last_question(self):
        if not self.selected_group:
            return

        grid = self.selected_group.grid

        if grid.count() == 0:
            return

        # Último item do grid
        item = grid.takeAt(grid.count() - 1)

        if item.widget():
            item.widget().deleteLater()

        self.atualizar_estatisticas()

    def estilo_botao(self, cor_base, cor_hover):
        return f"""
            QPushButton {{
                font-size: 16px;
                border-radius: 12px;
                background-color: {cor_base};
                color: #333;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {cor_hover};
            }}
        """
    
    def atualizar_estatisticas(self):

        certas = 0
        erradas = 0

        for i in range(self.groups_layout.count()):

            group = self.groups_layout.itemAt(i).widget()

            for j in range(group.grid.count()):

                item = group.grid.itemAt(j)
                button = item.widget()

                if button.correta:
                    certas += 1
                else:
                    erradas += 1

        self.spin_certas.setValue(certas)
        self.spin_erradas.setValue(erradas)

        total = certas + erradas

        self.label_total.setText(f"Questões total: {total}")

        if total:
            rendimento = 100 * certas / total
        else:
            rendimento = 0

        self.label_rendimento.setText(f"Rendimento total: {rendimento:.1f}%")
        cor = self.cor_gradiente(rendimento)
        self.label_rendimento.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {cor};"
        )

        self.atualizar_janela_graficos()

    def obter_estatisticas(self):
        dados = []

        for i in range(self.groups_layout.count()):

            group = self.groups_layout.itemAt(i).widget()

            certas = 0
            erradas = 0

            for j in range(group.grid.count()):

                botao = group.grid.itemAt(j).widget()

                if botao.correta:
                    certas += 1
                else:
                    erradas += 1

            total = certas + erradas

            rendimento = 0

            if total:
                rendimento = 100 * certas / total

            dados.append({
                "disciplina": group.titulo.text().replace("<b>", "").replace("</b>", ""),
                "certas": certas,
                "erradas": erradas,
                "total": total,
                "rendimento": rendimento
            })

        return dados
    
    def atualizar_janela_graficos(self):

        # Atualiza a janela de gráficos quando ela está aberta

        if self.statistics_window is not None and self.statistics_window.isVisible():
            
            dados = self.obter_estatisticas()
            self.statistics_window.atualizar_grafico(dados)
            self.statistics_window.grafico_pizza(dados)
    
    def abrir_estatisticas(self):
        dados = self.obter_estatisticas()

        self.statistics_window.atualizar_grafico(dados)
        self.statistics_window.grafico_pizza(dados)

        # self.hide()

        self.statistics_window.show()


    def cor_gradiente(self, p):
        pontos = [
            (0,   (255, 99, 132)),
            (60,  (255, 159, 64)),
            (70,  (255, 205, 86)),
            (80,  (75, 192, 192)),
            (90,  (54, 162, 235)),
            (100, (54, 162, 235)),
        ]

        for i in range(len(pontos) - 1):
            p1, c1 = pontos[i]
            p2, c2 = pontos[i + 1]

            if p1 <= p <= p2:
                t = (p - p1) / (p2 - p1) if p2 != p1 else 0
                r = int(c1[0] + (c2[0] - c1[0]) * t)
                g = int(c1[1] + (c2[1] - c1[1]) * t)
                b = int(c1[2] + (c2[2] - c1[2]) * t)
                return f"rgb({r}, {g}, {b})"

        return "rgb(54,162,235)"
    
    def gerar_yaml(self):

        array_certas = []
        array_erradas = []
        count_certas = 0
        count_erradas = 0

        for i in range(self.groups_layout.count()):

            group = self.groups_layout.itemAt(i).widget()

            for j in range(group.grid.count()):

                item = group.grid.itemAt(j)
                button = item.widget()

                if button.correta:
                    count_certas += 1
                    array_certas.append(-1)
                    array_erradas.append(0)
                else:
                    count_erradas += 1
                    array_certas.append(0)
                    array_erradas.append(1)

        labels = list(range(1, count_certas + count_erradas + 1))

        yaml_text = f"""type: bar
labels: {labels}
series:
- title: Erradas
    data: {array_certas}
- title: Corretas
    data: {array_erradas}
"""

        QApplication.clipboard().setText(yaml_text)

    def salvar_simulado(self):
        pass

    def alterar_simulado(self):
        pass

    def closeEvent(self, event):
        
        # Fecha a janela de estatísticas se estiver aberta
        if self.statistics_window is not None:
            self.statistics_window.close()
        
        self.closed.emit()
        super().closeEvent(event)