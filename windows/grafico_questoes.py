from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class StatisticsWindow(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent_window = parent

        self.setWindowTitle("Estatísticas")
        self.resize(550, 500)

        plt.style.use("tableau-colorblind10")

        layout = QVBoxLayout(self)

        self.figure = Figure(figsize=(8,5))
        self.canvas = FigureCanvasQTAgg(self.figure)

        layout.addWidget(self.canvas)

        self.btn_voltar = QPushButton("Voltar")

        layout.addWidget(self.btn_voltar)

        self.btn_voltar.clicked.connect(self.voltar)

    def atualizar_grafico(self, dados):

        self.figure.clear()

        ax = self.figure.add_subplot(211)

        disciplinas = [d["disciplina"] for d in dados]
        rendimento = [d["rendimento"] for d in dados]

        # Cores das barras
        # cores = [
        #     "#4E79A7", "#F28E2B", "#59A14F",
        #     "#E15759", "#76B7B2", "#EDC948",
        #     "#B07AA1", "#FF9DA7"
        # ]

        cores = [ "#A8DADC", # azul água
                 "#F4A261", # laranja pastel
                 "#8AB17D", # verde oliva suave
                 "#E5989B", # rosa queimado
                 "#84A59D", # verde acinzentado
                 "#E9C46A", # amarelo pastel
                 "#B8A1C9", # lilás "#FFCAD4", # rosa claro
                 "#CDB4DB", # lavanda
                 "#BDE0FE", # azul bebê
                 "#A2D2FF", # azul pastel
                 "#FFC8A2", # pêssego
                 "#D8E2DC", # verde muito claro
                 "#FFE5D9", # creme rosado
                 "#D0F4DE", # menta
                 "#FEC5BB", # salmão claro
                 "#FCD5CE", # rosa pálido
                 "#FAE1DD", # bege rosado
                 "#E8E8E4", # cinza claro quente
                 "#DDEDEA", # verde gelo
                 "#C3AED6", # roxo pastel
                 "#B5EAD7", # verde menta
                 "#FFDAC1", # pêssego claro
                 "#E2F0CB", # verde limão suave
                 "#C7CEEA", # azul lavanda
                 "#F6DFEB", # rosa lavanda
                 "#CDE7BE", # verde claro
                 "#F9DCC4", # areia clara
                 "#D6EADF", # verde névoa
                 "#E4C1F9" # violeta pastel
                 ]

        barras = ax.bar(
            disciplinas,
            rendimento,
            color=cores[:len(disciplinas)],
            edgecolor="black",
            linewidth=0.8
        )

        ax.set_ylim(0, 100)

        ax.set_ylabel("Rendimento (%)", fontsize=11)
        ax.set_title(
            "Rendimento por disciplina",
            fontsize=14,
            weight="bold"
        )

        # Grade
        ax.grid(axis="y", linestyle="--", alpha=0.35)

        # Remove bordas desnecessárias
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        # Valores sobre as barras
        for barra, valor in zip(barras, rendimento):
            ax.text(
                barra.get_x() + barra.get_width()/2,
                valor + 2,
                f"{valor:.1f}%",
                ha="center",
                fontsize=9
            )

        self.figure.tight_layout()

        self.canvas.draw()

    def grafico_pizza(self, dados):

        self.figure.subplots_adjust(hspace=0.45)

        ax = self.figure.add_subplot(212)

        disciplinas = [d["disciplina"] for d in dados]
        questoes = [d["total"] for d in dados]

        # cores = [
        #     "#4E79A7", "#F28E2B", "#59A14F",
        #     "#E15759", "#76B7B2", "#EDC948",
        #     "#B07AA1", "#FF9DA7"
        # ]

        cores = [ "#A8DADC", # azul água
                 "#F4A261", # laranja pastel
                 "#8AB17D", # verde oliva suave
                 "#E5989B", # rosa queimado
                 "#84A59D", # verde acinzentado
                 "#E9C46A", # amarelo pastel
                 "#B8A1C9", # lilás "#FFCAD4", # rosa claro
                 "#CDB4DB", # lavanda
                 "#BDE0FE", # azul bebê
                 "#A2D2FF", # azul pastel
                 "#FFC8A2", # pêssego
                 "#D8E2DC", # verde muito claro
                 "#FFE5D9", # creme rosado
                 "#D0F4DE", # menta
                 "#FEC5BB", # salmão claro
                 "#FCD5CE", # rosa pálido
                 "#FAE1DD", # bege rosado
                 "#E8E8E4", # cinza claro quente
                 "#DDEDEA", # verde gelo
                 "#C3AED6", # roxo pastel
                 "#B5EAD7", # verde menta
                 "#FFDAC1", # pêssego claro
                 "#E2F0CB", # verde limão suave
                 "#C7CEEA", # azul lavanda
                 "#F6DFEB", # rosa lavanda
                 "#CDE7BE", # verde claro
                 "#F9DCC4", # areia clara
                 "#D6EADF", # verde névoa
                 "#E4C1F9" # violeta pastel
                 ]

        wedges, texts, autotexts = ax.pie(
            questoes,
            labels=disciplinas,
            colors=cores[:len(disciplinas)],
            autopct="%1.1f%%",
            startangle=90,
            pctdistance=0.75,
            wedgeprops={
                "edgecolor": "white",
                "linewidth": 2
            }
        )

        # Aparência dos textos
        for t in texts:
            t.set_fontsize(10)

        for t in autotexts:
            t.set_fontsize(10)
            t.set_weight("bold")
            t.set_color("white")

        ax.set_title(
            "Distribuição das questões por disciplina",
            fontsize=14,
            weight="bold"
        )

        ax.axis("equal")

        self.figure.tight_layout()

        self.canvas.draw()

    def voltar(self):

        self.close()

    def closeEvent(self, event):

        if self.parent_window is not None:
            self.parent_window.show()

        event.accept()