import sys
import os
import sqlite3

from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QDateTime

from pages.config import ConfigManager

from datetime import datetime

class DataBaseManager():
    def __init__(self):
        super().__init__()

        self.configuracoes = ConfigManager()

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(self.base_dir, self.configuracoes.get_database_file())

        self.conn = sqlite3.connect(self.db_path)

        self.cursor = self.conn.cursor()

        self.create_tables()

    def create_tables(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessoes (

            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            
            categoria TEXT NOT NULL,

            disciplina TEXT NOT NULL,
                            
            topico TEXT NOT NULL,

            data_fim TEXT NOT NULL,
            
            pausa_segundos INTEGER NOT NULL,

            duracao_segundos INTEGER NOT NULL
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            
            sessao_id INTEGER NOT NULL,

            timestamp TEXT NOT NULL,

            evento TEXT NOT NULL,
                            
            FOREIGN KEY (sessao_id) REFERENCES sessoes(id)
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS simulados (

            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            
            data TEXT NOT NULL,
                            
            categoria TEXT NOT NULL
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS simulados_disciplina (

            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            
            simulado_id INTEGER NOT NULL,
                            
            disciplina TEXT NOT NULL,

            FOREIGN KEY (simulado_id) REFERENCES simulados(id)
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS simulados_questoes (

            id INTEGER PRIMARY KEY AUTOINCREMENT,
            
            simulado_id INTEGER NOT NULL,
                            
            disciplina TEXT NOT NULL,
                            
            questao INTEGER NOT NULL,
            
            acertou INTEGER NOT NULL,
            
            FOREIGN KEY (simulado_id) REFERENCES simulados(id),
            
            FOREIGN KEY (disciplina) REFERENCES simulados_disciplina(disciplina)
        )
        """)

        self.conn.commit()


    #############################################
    # GETTERS
    #############################################

    def get_session_dia(self, dia_str): # Formato string do dia: "yyyy-MM-dd"

        self.cursor.execute("""
            SELECT
                id,
                categoria,
                disciplina,
                topico,
                data_fim,
                pausa_segundos,
                duracao_segundos
            FROM sessoes
            WHERE date(data_fim) = ?
            ORDER BY data_fim
        """, (dia_str,))

        rows = self.cursor.fetchall()

        sessions = []

        for row in rows:

            (
                sessao_id,
                categoria,
                disciplina,
                topico,
                data_fim,
                pausa_segundos,
                duracao_segundos
            ) = row

            sessions.append({
                "id": sessao_id,
                "categoria": categoria,
                "disciplina": disciplina,
                "topico": topico,
                "data_fim": data_fim,
                "pausa_segundos": pausa_segundos,
                "duracao_segundos": duracao_segundos,
            })

        return sessions
    
    def get_session_session(self, session_id):

        self.cursor.execute("""
            SELECT
                id,
                categoria,
                disciplina,
                topico,
                data_fim,
                pausa_segundos,
                duracao_segundos
            FROM sessoes
            WHERE id = ?
        """, (session_id,))

        rows = self.cursor.fetchall()

        session = []

        for row in rows:
            (
                sessao_id,
                categoria,
                disciplina,
                topico,
                data_fim,
                pausa_segundos,
                duracao_segundos
            ) = row

        session.append({
            "id": sessao_id,
            "categoria": categoria,
            "disciplina": disciplina,
            "topico": topico,
            "data_fim": data_fim,
            "pausa_segundos": pausa_segundos,
            "duracao_segundos": duracao_segundos,
        })

        return session
    
    def get_log_session(self, session_id):
        
        self.cursor.execute("""
            SELECT
                id,
                sessao_id,
                timestamp,
                evento
            FROM logs
            WHERE sessao_id = ?
            ORDER BY timestamp
        """, (session_id,))

        rows = self.cursor.fetchall()

        logs = []

        for row in rows:

            (
                id,
                sessao_id,
                timestamp,
                evento
            ) = row

            logs.append({
                "id": id,
                "sessao_id": sessao_id,
                "timestamp": timestamp,
                "evento": evento
            })

        return logs

    def get_session_semana(self, semana):
        pass

    def get_simulados(self, dia):
        pass

    def get_resultado_questoes(self, simulado_id):
        pass

    #############################################
    # ADICIONAR DADOS
    #############################################

    # adiciona a session e o log correspondente

    def add_session(self,
                    categoria,
                    disciplina,
                    topico,
                    data_fim,
                    pausa,
                    duracao,
                    session_logs
                    ):
        
        if categoria == None:
            categoria = "Geral"
        if disciplina == None:
            disciplina = "Geral"
        if topico == None:
            topico = "Geral"
        if pausa == None:
            pausa = 0

        if session_logs == None:
            session_logs = []
            fim = QDateTime.fromString(data_fim, "yyyy-MM-dd HH:mm:ss")
            inicio = fim.addSecs(-1 * duracao)

            session_logs.append({
                "timestamp": inicio.toString("yyyy-MM-dd HH:mm:ss"),
                "evento": "ESTUDANDO"
            })

            session_logs.append({
                "timestamp": fim.toString("yyyy-MM-dd HH:mm:ss"),
                "evento": "ENCERRADO_AUTO"
            })
        
        # evita salvar sessões vazias
        if duracao <= 0:

            QMessageBox.warning(
                None,
                "Erro",
                "Nenhum tempo de estudo para salvar."
            )

            return

        try:
            # SESSION

            self.cursor.execute(
                """
                INSERT INTO sessoes (
                    categoria,
                    disciplina,
                    topico,
                    data_fim,
                    pausa_segundos,
                    duracao_segundos
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    categoria,
                    disciplina,
                    topico,
                    data_fim,
                    pausa,
                    duracao
                )
            )

            sessao_id = self.cursor.lastrowid

            # LOGS

            for log in session_logs:

                self.cursor.execute(
                    """
                    INSERT INTO logs (
                        sessao_id,
                        timestamp,
                        evento
                    )
                    VALUES (?, ?, ?)
                    """,
                    (
                        sessao_id,
                        log["timestamp"],
                        log["evento"]
                    )
                )

            self.conn.commit()

            # return sessao_id

            QMessageBox.information(
                None,
                "Sessão salva",
                (
                    f"Disciplina: {disciplina}\n"
                    f"Duração: {self.format_time(duracao)}"
                )
            )

        except Exception as e:
            QMessageBox.critical(
                None,
                "Erro ao salvar",
                str(e)
            )

            # print("ERRO REAL:", repr(e))

            self.conn.rollback()
            raise
    
    # adiciona o simulado e resultado_questoes correspondente

    def add_simulado(self):
        pass 

    #############################################
    # FUNÇÕES DE HISTÓRICO
    #############################################

    def modify_session(self,
                    session_id,
                    categoria,
                    disciplina,
                    topico,
                    data_fim,
                    duracao
                    ):
        
        if categoria == None:
            categoria = "Geral"
        if disciplina == None:
            disciplina = "Geral"
        if topico == None:
            topico = "Geral"
        
        # evita salvar sessões vazias
        if duracao <= 0:

            QMessageBox.warning(
                None,
                "Erro",
                "Nenhum tempo de estudo para salvar."
            )

            return

        try:
            # SESSION

            self.cursor.execute(
                """
                UPDATE sessoes
                SET
                    categoria = ?,
                    disciplina = ?,
                    topico = ?,
                    data_fim = ?,
                    duracao_segundos = ?
                WHERE id = ?
                """,
                (
                    categoria,
                    disciplina,
                    topico,
                    data_fim,
                    duracao,
                    session_id
                )
            )

            self.conn.commit()

            # return sessao_id

            QMessageBox.information(
                None,
                "Sessão salva",
                (
                    f"Disciplina: {disciplina}\n"
                    f"Duração: {self.format_time(duracao)}"
                )
            )

        except Exception as e:
            QMessageBox.critical(
                None,
                "Erro ao salvar",
                str(e)
            )

            # print("ERRO REAL:", repr(e))

            self.conn.rollback()
            raise

    def modify_log(self, session_id):
        pass

    def modify_simulado(self, simulado_id):
        pass

    def modify_resultado_questoes(self, simulado_id):
        pass

    def remove_session_completa(self, session_id):

        self.cursor.execute("""
            DELETE FROM sessoes
            WHERE id = ?
        """, (session_id,))

        self.cursor.execute("""
            DELETE FROM logs
            WHERE sessao_id = ?
        """, (session_id,))

        self.conn.commit()

        return self.cursor.rowcount > 0

    def remove_simulado(self, simulado_id):
        pass

    def remove_resultado_questoes(self, simulado_id):
        pass

    def format_time(self, ms):

        total_seconds = int(ms)

        h = total_seconds // 3600
        m = (total_seconds % 3600) // 60
        s = total_seconds % 60

        return f"{h:02}:{m:02}:{s:02}"