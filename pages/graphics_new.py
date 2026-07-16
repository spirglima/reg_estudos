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

from PySide6.QtWebEngineWidgets import QWebEngineView

import plotly.graph_objects as go
import plotly.express as px
from plotly.offline import plot
from plotly.subplots import make_subplots

from PySide6.QtCore import QDate

from pages.config import ConfigManager
from database.table import DataBaseManager

class StudyViewer(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # Figura do matplotlib
        self.web_view = QWebEngineView()

        layout.addWidget(self.web_view)

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

        if not sessions:
            self.web_view.setHtml("<h3>Nenhum dado encontrado</h3>")
            return

        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        semana = ["seg", "ter", "qua", "qui", "sex", "sab", "dom"]

        # =====================================
        # RESUMO (DISCIPLINAS)
        # =====================================

        disciplinas = []
        estudo_horas = []
        pausa_horas = []
        cores = []

        resumo = {}

        for sessao in sessions:

            disciplina = sessao["disciplina"]

            if disciplina not in resumo:
                resumo[disciplina] = {
                    "estudo": 0,
                    "pausa": 0
                }

            resumo[disciplina]["estudo"] += sessao["duracao_segundos"]
            resumo[disciplina]["pausa"] += sessao["pausa_segundos"]

        for disciplina, dados in resumo.items():

            disciplinas.append(disciplina)

            estudo_horas.append(dados["estudo"] / 3600)
            pausa_horas.append(dados["pausa"] / 3600)

            cores.append(
                self.configuracoes.get_cor_disciplina(disciplina)
            )

        # =====================================
        # METAS
        # =====================================

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

            meta_dia = meta_semanal / aparicoes if aparicoes > 0 else 0

            metas_diarias.append(meta_dia)

        # =====================================
        # TIMELINE
        # =====================================

        timeline = self.construir_timeline(sessions)

        dados_timeline = []

        for bloco in timeline:

            dados_timeline.append({

                "Disciplina": bloco["disciplina"],

                "Inicio": bloco["inicio"],

                "Fim": bloco["fim"]

            })

        if dados_timeline:

            fig_timeline = px.timeline(

                dados_timeline,

                x_start="Inicio",

                x_end="Fim",

                y="Disciplina",

                color="Disciplina"
            )
        else:
            fig_timeline = go.Figure()


        hora_ini = self.configuracoes.get_hora_ini_dia()

        hora_fim = self.configuracoes.get_hora_fim_dia()

        inicio_dia = datetime.strptime(

            f"{data_str} {hora_ini}:00",

            "%Y-%m-%d %H:%M:%S"
        )

        fim_dia = datetime.strptime(

            f"{data_str} {hora_fim}:00",

            "%Y-%m-%d %H:%M:%S"
        )

        fig_timeline.update_xaxes(

            range=[inicio_dia, fim_dia],

            tickformat="%H:%M"
        )

        # =====================================
        # FIGURA (SUBPLOTS)
        # =====================================

        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=False
        )

        for trace in fig_timeline.data:

            fig.add_trace(
                trace,
                row=1,
                col=1
            )

        # =====================================
        # TIMELINE (ROW 1)
        # =====================================

        for bloco in timeline:

            disciplina = bloco["disciplina"]

            cor = self.configuracoes.get_cor_disciplina(disciplina)

            inicio = bloco["inicio"]
            fim = bloco["fim"]

            duracao_horas = (fim - inicio).total_seconds() / 3600

            fig.add_trace(

                go.Bar(

                    x=[duracao_horas],
                    y=[""],
                    base=inicio,

                    orientation="h",

                    marker_color=cor,

                    showlegend=False,

                    hovertemplate=
                        f"<b>{disciplina}</b><br>"
                        "Início: %{base|%H:%M}<br>"
                        "Duração: %{x:.2f} h"
                        "<extra></extra>"
                ),

                row=1,
                col=1
            )

        # =====================================
        # RESUMO (ROW 2)
        # =====================================

        fig.add_bar(

            x=disciplinas,
            y=estudo_horas,
            name="Estudo",
            marker_color=cores,

            customdata=metas_diarias,

            hovertemplate=
                "<b>%{x}</b><br>"
                "Estudo: %{y:.2f} h<br>"
                "Meta: %{customdata:.2f} h"
                "<extra></extra>",

            row=2,
            col=1
        )

        fig.add_bar(

            x=disciplinas,
            y=pausa_horas,
            name="Pausa",
            marker_color="#cccccc",

            hovertemplate=
                "<b>%{x}</b><br>"
                "Pausa: %{y:.2f} h"
                "<extra></extra>",

            row=2,
            col=1
        )

        fig.add_scatter(

            x=disciplinas,
            y=metas_diarias,

            mode="lines+markers",
            name="Meta",

            line=dict(color="black", width=3),

            row=2,
            col=1
        )

        # =====================================
        # LAYOUT FINAL
        # =====================================

        fig.update_layout(

            title="Disciplinas estudadas hoje",
            template="plotly_white",

            barmode="group",
            hovermode="closest",

            height=750
        )

        # esconder eixo Y da timeline
        fig.update_yaxes(visible=False, row=1, col=1)

        html = fig.to_html(include_plotlyjs="cdn")

        self.web_view.setHtml(html)