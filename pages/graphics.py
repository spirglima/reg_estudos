import sys
import os
import sqlite3

from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import numpy as np
import mplcursors

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QCalendarWidget,
    QMessageBox,
)

from PySide6.QtCore import QDate

from pages.config import ConfigManager
from database.table import DataBaseManager

class StudyViewer(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # Figura do matplotlib
        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)

        layout.addWidget(self.canvas)

    def construir_timeline(self, sessions):

        timeline = []

        for sessao in sessions:

            logs = self.database.get_log_session(
                sessao["id"]
            )

            disciplina = sessao["disciplina"]

            inicio = None

            for log in logs:

                evento = log["evento"]

                timestamp = datetime.strptime(
                    log["timestamp"],
                    "%Y-%m-%d %H:%M:%S"
                )

                if evento == "ESTUDANDO":

                    inicio = timestamp

                elif evento in (
                    "Pausa",
                    "PAUSA",
                    "ENCERRADO_AUTO"
                ):

                    if inicio is not None:

                        timeline.append({
                            "disciplina": disciplina,
                            "inicio": inicio,
                            "fim": timestamp
                        })

                        inicio = None

        return timeline

    def generate_chart(self, data_str):

        self.database = DataBaseManager()
        self.configuracoes = ConfigManager()

        sessions = self.database.get_session_dia(data_str)

        # # dados das seções de estudo

        # print("Sessões de estudo registradas: ")

        # print(sessions)

        # disciplinas = self.configuracoes.get_disciplinas()

        # # Configurações cadastradas pelo usuário

        # print("Hora que o dia começa:")
        # print(self.configuracoes.get_hora_ini_dia())

        # print("Hora que o dia termina:")
        # print(self.configuracoes.get_hora_fim_dia())

        # print("Disciplinas: ")
        
        # print(disciplinas)

        # print("Quadro Semanal:") # A disciplina que é estudada naquele dia da semana (importante para definir no gráfico se a meta foi alcançada)

        semana = ["seg", "ter", "qua", "qui", "sex", "sab", "dom"]

        # for dia in semana:
        #     print(self.configuracoes.get_quadro_semanal(dia.lower()))

        # print("E hoje é:")

        # data = QDate.fromString(data_str, "yyyy-MM-dd")
        # dia_semana = semana[data.dayOfWeek() - 1]

        # print(dia_semana)

        # print("Informações das disciplinas:")

        # # A meta semanal é dividida igualmente entre as sessões de estudo de cada disciplina (cada seção consta no quadro semanal)

        # for disciplina in disciplinas:
        #     print(self.configuracoes.get_cor_disciplina(disciplina))
        #     print(self.configuracoes.get_meta_semanal(disciplina)) # Horas
        #     print(self.configuracoes.get_oculto_disciplina(disciplina)) # Se deve ou não estar oculta nos gráficos

        # print("Esses são os respectivos logs:") # Perceba que os logs podem ser sobrepostos, mesmo que na realidade seja impossível, o usuário pode cadasrar mais de um log no mesmo horário
        
        if not sessions:
            self.figure.clear()
            self.canvas.draw()
            
            return
        
        # =====================================
        # LIMPA FIGURA
        # =====================================
        
        self.figure.clear()
        
        # =====================================
        # EIXOS
        # =====================================

        gs = self.figure.add_gridspec(
            2,
            1,
            height_ratios=[1, 5]
        ) # Controle da proporção de preenchimento de cada gráfico

        ax_timeline = self.figure.add_subplot( gs[0] )

        ax_resumo = self.figure.add_subplot( gs[1] )

        # =====================================
        # TIMELINE
        # =====================================

        timeline = self.construir_timeline( sessions )

        for bloco in timeline:
            disciplina = bloco["disciplina"]
            cor = self.configuracoes.get_cor_disciplina( disciplina )
            inicio = mdates.date2num( bloco["inicio"] )
            fim = mdates.date2num( bloco["fim"] )
            largura = fim - inicio
            ax_timeline.barh( 0, largura, left=inicio, height=0.9, color=cor, edgecolor="none" )

        # =====================================
        # LIMITES DE HORÁRIO
        # =====================================

        hora_ini = self.configuracoes.get_hora_ini_dia()
        hora_fim = self.configuracoes.get_hora_fim_dia()

        inicio_dia = datetime.strptime( f"{data_str} {hora_ini}:00", "%Y-%m-%d %H:%M:%S" )
        fim_dia = datetime.strptime( f"{data_str} {hora_fim}:00", "%Y-%m-%d %H:%M:%S" )

        ax_timeline.set_xlim( inicio_dia, fim_dia )
        ax_timeline.set_yticks([])

        ax_timeline.xaxis.set_major_formatter( mdates.DateFormatter("%H:%M") )
        ax_timeline.xaxis.set_major_locator( mdates.HourLocator(interval=1) )

        ax_timeline.grid( axis="x", linestyle="--", alpha=0.3 )
        ax_timeline.set_title( f"Linha do Tempo" )

        # =====================================
        # RESUMO DISCIPLINAS
        # =====================================

        disciplinas = []
        estudo_horas = []
        pausa_horas = []
        cores = []

        resumo = {}

        for sessao in sessions:
            disciplina = sessao["disciplina"]

            if disciplina not in resumo:
                resumo[disciplina] = { "estudo": 0, "pausa": 0 }
            
            resumo[disciplina]["estudo"] += ( sessao["duracao_segundos"] )

            resumo[disciplina]["pausa"] += ( sessao["pausa_segundos"] )
        
        for disciplina, dados in resumo.items():
            disciplinas.append( disciplina )
            estudo_horas.append( dados["estudo"] / 3600 )
            pausa_horas.append( dados["pausa"] / 3600 )
            cores.append( self.configuracoes.get_cor_disciplina( disciplina ) )

        metas_diarias = []

        for disciplina in disciplinas:

            meta_semanal = float(
                self.configuracoes.get_meta_semanal(disciplina)
            )

            aparicoes = 0

            for dia in semana:

                aparicoes += (
                    self.configuracoes
                    .get_quadro_semanal(dia)
                    .count(disciplina)
                )

            if aparicoes > 0:
                meta_dia = meta_semanal / aparicoes
            else:
                meta_dia = 0

            metas_diarias.append(meta_dia)

        x = np.arange(len(disciplinas))
        largura = 0.35

        # Gráfico de meta
        # ax_resumo.bar( x - largura/2, metas_diarias, largura, facecolor="none", edgecolor="black", linewidth=2, label = "Meta")
        for xi, yi in zip(x, metas_diarias):
            ax_resumo.hlines(
                yi,
                xi - largura,
                xi,
                colors = "black",
                linewidth=2
            )

        # Gráfico de estudos
        ax_resumo.bar( x - largura/2, estudo_horas, largura, color=cores, label="Estudo" )
        ax_resumo.bar( x + largura/2, pausa_horas, largura, color="#cccccc", label="Pausa" )
        


        ax_resumo.set_xticks(x)

        ax_resumo.set_xticklabels( disciplinas, rotation=15 )

        ax_resumo.legend()

        ax_resumo.set_ylabel( "Horas" )

        ax_resumo.set_title( "Disciplinas estudadas hoje" )

        # =====================================
        # TOOLTIP ESTUDO
        # =====================================

        

        cursor_resumo = mplcursors.cursor(
            ax_resumo,
            hover = True
        )

        @cursor_resumo.connect("add")
        def on_add_estudo(sel):
            index = sel.index

            disciplina = disciplinas[index]
            tempo_str = self.horas_para_hms(estudo_horas[index])

            sel.annotation.set_text(
                f"{disciplina}\n"
                f"{tempo_str}"
            )

            sel.annotation.get_bbox_patch().set(
                fc="#FFFFFF",
                ec="#D0D0D0",
                lw=1,
                alpha=0.98,
                boxstyle="round,pad=0.4"
            )

            sel.annotation.set_fontsize(10)

        # @cursor_resumo.connect("add")
        # def on_add_estudo(sel):
        #     index = sel.index
        #     disciplina = disciplinas[index]

        #     tempo = estudo_horas[index]

        #     tempo_str = self.horas_para_hms(tempo)

        #     sel.annotation.set_text(
        #         f"{disciplina}\n"
        #         f"Total: "
        #         f"{tempo_str}\n"
        #     )

        #     sel.annotation.get_bbox_patch().set(
        #         fc = "white",
        #         alpha=0.95
        #     )

        # =====================================
        # AJUSTE FINAL
        # =====================================

        self.figure.tight_layout()

        self.canvas.draw()
    
    def horas_para_hms(self, horas):
        total_segundos = int(horas * 3600)

        h = total_segundos // 3600
        m = (total_segundos % 3600) // 60
        s = total_segundos % 60

        return f"{h:02d}:{m:02d}:{s:02d}"
        