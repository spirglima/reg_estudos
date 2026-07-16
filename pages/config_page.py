import sys
import os

from PySide6.QtCore import Qt, QTime, Signal
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTimeEdit,
    QFrame,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QComboBox,
    QSlider
)

from PySide6.QtWidgets import QInputDialog

from pages.config import ConfigManager


# ============================================================
# BOTÃO DE DIA DA SEMANA
# ============================================================

class DayButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)

        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)

        self.setMinimumHeight(42)
        self.setMinimumWidth(65)

        self.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 10px;

                background: #dbeafe;
                color: #1e3a8a;

                font-weight: 600;
                padding: 8px;
            }

            QPushButton:hover {
                background: #93c5fd;
            }

            QPushButton:checked {
                background: #2563eb;
                color: white;
            }

            QPushButton:checked:hover {
                background: #1d4ed8;
            }
        """)


# ============================================================
# TAG CHIP
# ============================================================

class TagChip(QFrame):

    removed = Signal(str)
    renamed = Signal()

    def __init__(self, text):
        super().__init__()

        self.tag_text = text

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 4, 2)
        layout.setSpacing(3)

        self.label = QPushButton(text)
        self.label.setToolTip("Clique para renomear")
        self.label.setFlat(True)

        self.label.setCursor(Qt.PointingHandCursor)
        self.label.clicked.connect(self.rename_tag)

        remove_btn = QPushButton("✕")
        remove_btn.setObjectName("removeTag")

        remove_btn.setFixedSize(16, 16)
        remove_btn.clicked.connect(self.remove_self)

        layout.addWidget(self.label)
        layout.addWidget(remove_btn)

        self.setStyleSheet("""
            QFrame {
                background: #eff6ff;
                border: 1px solid #bfdbfe;
                border-radius: 10px;
            }

            QPushButton {
                border: none;
                background: transparent;
                padding: 0px;
            }

            QPushButton:hover {
                background: transparent;
            }

            QPushButton#removeTag {
                color: #94a3b8;
                font-weight: bold;
            }

            QPushButton#removeTag:hover {
                color: #dc2626;
            }
        """)

    def rename_tag(self):
        novo_nome, ok = QInputDialog.getText(
            self,
            "Renomear Tag",
            "Novo nome:"
        )
        configuracao = ConfigManager()

        if ok and novo_nome.strip():

            configuracao.rename_tag(self.tag_text, novo_nome.strip())

            self.tag_text = novo_nome.strip()

            self.label.setText(self.tag_text)

            self.renamed.emit()

    def remove_self(self):
        self.removed.emit(self.tag_text)
        self.deleteLater()


# ============================================================
# FLOW LAYOUT SIMPLES
# ============================================================

class FlowWidget(QWidget):

    changed = Signal()

    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)

        self.layout.addStretch()

    def add_chip(self, chip):

        self.layout.insertWidget(
            self.layout.count() - 1,
            chip
        )

        self.changed.emit()


# ============================================================
# CARD
# ============================================================

class SettingsCard(QFrame):
    def __init__(self, title):
        super().__init__()

        self.setObjectName("card")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(16)

        label = QLabel(title)
        label.setObjectName("cardTitle")

        layout.addWidget(label)

        self.body = QVBoxLayout()
        self.body.setSpacing(14)

        layout.addLayout(self.body)


# ============================================================
# JANELA
# ============================================================

class ConfigPage(QWidget):

    def __init__(self):
        super().__init__()

        # self.setWindowTitle("Configurações")
        # self.resize(900, 750)

        self.setStyleSheet("""
            QWidget {
                background: #ffffff;
                font-size: 14px;
            }
        
            QLabel#pageTitle {
                font-size: 28px;
                font-weight: bold;
                color: #111827;
            }
            
            QLabel#subtitle {
                color: #6b7280;
                font-size: 15px;
            }
            QFrame#card {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 16px;
            }
        
            QLabel#cardTitle {
                font-size: 16px;
                font-weight: 700;
                color: #111827;
            }
        
            QLabel {
                color: #374151;
            }

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

            QPushButton {
                min-height: 20px;
                border-radius: 8px;
            }
                           
            QPushButton#saveButton {
                background: #2563eb;
                color: white;
                font-weight: 600;
                border: none;
            }

            QPushButton#saveButton:hover:enabled {
                background: #3b82f6;
            }

            QPushButton#saveButton:pressed {
                background: #1d4ed8;
            }

            QPushButton#saveButton:disabled {
                background: #d1d5db;
                color: #6b7280;
            }

            QPushButton#cancelButton {
                background: white;
                border: 1px solid #d1d5db;
                font-weight: 600;
            }

            QPushButton#cancelButton:hover {
                background: #f3f4f6;
            }

            QPushButton#addTagButton {
                background: #2563eb;
                color: white;
                border: none;
                padding: 0 14px;
                font-weight: bold;
            }

            QPushButton#addTagButton:hover {
                background: #3b82f6;
            }
        
        """)

        self.build_ui()

    # ========================================================

    def build_ui(self):

        root = QVBoxLayout(self)

        root.setContentsMargins(40, 40, 40, 40)
        root.setSpacing(20)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        root.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        content = QVBoxLayout(container)
        content.setSpacing(8)

        self.configuracao = ConfigManager()

        # ====================================================
        # USUÁRIO
        # ====================================================

        card_about = SettingsCard("Sobre")

        card_about.body.addWidget(QLabel("<b>Software Integrado de Estudos</b>"))
        card_about.body.addWidget(QLabel("Versão 1.0"))
        card_about.body.addWidget(QLabel("Desenvolvido por Marcus Lima"))
        card_about.body.addWidget(QLabel("Ferramenta para planejamento, organização e acompanhamento do desempenho."))

        content.addWidget(card_about)

        # ====================================================
        # ARQUIVOS
        # ====================================================

        card_files = SettingsCard("Arquivos")

        card_files.body.addWidget(QLabel("Arquivo de configuração (padrão)"))

        self.txt_config = QLineEdit("config.json")
        self.txt_config.setEnabled(False)
        card_files.body.addWidget(self.txt_config)

        card_files.body.addWidget(QLabel("Banco de dados"))

        self.txt_db = QLineEdit(self.configuracao.get_database_file())
        self.txt_db.textChanged.connect(
            self.configuracao.alterar_database_file
            )

        card_files.body.addWidget(self.txt_db)

        content.addWidget(card_files)

        # ====================================================
        # USUÁRIO
        # ====================================================

        card_user = SettingsCard("Usuário")

        card_user.body.addWidget(QLabel("Nome"))

        self.txt_user = QLineEdit(self.configuracao.get_nome_usuario())
        self.txt_user.textChanged.connect(self.configuracao.alterar_usuario)

        card_user.body.addWidget(self.txt_user)

        content.addWidget(card_user)

        # ====================================================
        # AGENDA
        # ====================================================

        card_schedule = SettingsCard("Agenda")

        card_schedule.body.addWidget(QLabel("Dias de estudo"))

        days_layout = QHBoxLayout()
        days_layout.setSpacing(8)

        self.day_buttons = []

        for dia in ["dom", "seg", "ter", "qua", "qui", "sex", "sab"]:

            btn = DayButton(dia)

            if dia in self.configuracao.get_dias_estudo_semanal():
                btn.setChecked(True)

            btn.toggled.connect(
                lambda checked, dia=dia:
                    self.configuracao.alterar_dia_estudo_semanal(checked, dia)
            )

            self.day_buttons.append(btn)

            days_layout.addWidget(btn)

        days_layout.addStretch()

        card_schedule.body.addLayout(days_layout)

        card_schedule.body.addWidget(QLabel("Horário útil"))

        time_layout = QHBoxLayout()

        self.time_start = QTimeEdit()
        self.time_start.setTime(QTime.fromString(self.configuracao.get_hora_ini_dia(), "HH:mm"))
        self.time_start.setDisplayFormat("HH:mm")
        self.time_start.timeChanged.connect(self.configuracao.alterar_hora_ini_dia)

        self.time_end = QTimeEdit()
        self.time_end.setTime(QTime.fromString(self.configuracao.get_hora_fim_dia(), "HH:mm"))
        self.time_end.setDisplayFormat("HH:mm")
        self.time_end.timeChanged.connect(self.configuracao.alterar_hora_fim_dia)

        lbl_ate = QLabel("até")

        time_layout.addWidget(self.time_start)
        time_layout.addWidget(lbl_ate)
        time_layout.addWidget(self.time_end)
        time_layout.addStretch()

        card_schedule.body.addLayout(time_layout)

        content.addWidget(card_schedule)

        # ====================================================
        # TAGS
        # ====================================================

        card_tags = SettingsCard("Tags")

        self.tags_widget = FlowWidget()

        card_tags.body.addWidget(self.tags_widget)

        add_layout = QHBoxLayout()

        self.txt_new_tag = QLineEdit()
        self.txt_new_tag.setPlaceholderText("Nova tag...")

        btn_add_tag = QPushButton("+")
        btn_add_tag.setObjectName("addTagButton")
        btn_add_tag.setFixedWidth(45)

        btn_add_tag.clicked.connect(self.add_tag)

        add_layout.addWidget(self.txt_new_tag)
        add_layout.addWidget(btn_add_tag)

        card_tags.body.addLayout(add_layout)

        content.addWidget(card_tags)

        # Tags iniciais

        for tag in self.configuracao.get_tags():
            self.create_tag(tag)

        # ====================================================
        # JANELA DO CRONOMETRO
        # ====================================================
        
        card_janela_cronometro = SettingsCard(
            "Tamanho da janela do cronômetro (px)"
        )

        janela_cronometro_layout = QHBoxLayout()

        self.janela_cronometro_width = QSpinBox()
        self.janela_cronometro_width.setRange(100, 3000)
        self.janela_cronometro_width.setValue(self.configuracao.get_cronometro_width())
        self.janela_cronometro_width.valueChanged.connect(self.configuracao.alterar_cronometro_largura)

        self.janela_cronometro_height = QSpinBox()
        self.janela_cronometro_height.setRange(200, 3000)
        self.janela_cronometro_height.setValue(self.configuracao.get_cronometro_high())
        self.janela_cronometro_height.valueChanged.connect(self.configuracao.alterar_cronometro_altura)

        janela_cronometro_layout.addWidget(QLabel("Largura"))

        janela_cronometro_layout.addWidget(
            self.janela_cronometro_width
        )

        janela_cronometro_layout.addSpacing(20)

        janela_cronometro_layout.addWidget(QLabel("Altura"))

        janela_cronometro_layout.addWidget(
            self.janela_cronometro_height
        )

        janela_cronometro_layout.addStretch()

        card_janela_cronometro.body.addLayout(
            janela_cronometro_layout
        )

        content.addWidget(card_janela_cronometro)

        # ====================================================
        # SOM E ALARMES
        # ====================================================

        card_som = SettingsCard("Som do timer")

        # arquivo

        card_som.body.addWidget(QLabel("Som de término (.wav)"))

        som_layout = QHBoxLayout()

        self.som_arquivo = QComboBox()

        arquivos_wav = self.configuracao.update_audio_file()

        self.configuracao.get_som_arquivo()

        if arquivos_wav:
            self.som_arquivo.addItems(arquivos_wav)

            # Caso da primeira inicialização, arquivo_salvo == ""
            # e
            # Caso o usuário apague o arquivo que era usado antes

            # O programa muda para o primeiro que ele encontrar:

            arquivo_salvo = self.configuracao.get_som_arquivo()

            if (not arquivo_salvo or arquivo_salvo not in arquivos_wav):
                self.configuracao.alterar_som_arquivo(arquivos_wav[0])
            
            indice_musica = self.som_arquivo.findText(self.configuracao.get_som_arquivo())

            if indice_musica >= 0:
                self.som_arquivo.setCurrentIndex(indice_musica)
        else:
            self.som_arquivo.addItem(
                "Nenhum arquivo .wav encontrado"
            )

        self.som_arquivo.currentTextChanged.connect(self.configuracao.alterar_som_arquivo)

        som_layout.addWidget(self.som_arquivo)

        card_som.body.addLayout(som_layout)

        # volume

        card_som.body.addWidget(QLabel("Volume"))

        volume_layout = QHBoxLayout()

        self.som_volume = QSlider(Qt.Horizontal)
        self.som_volume.setRange(0, 200)
        self.som_volume.setValue(self.configuracao.get_som_volume())

        self.som_volume.sliderReleased.connect(
            lambda: self.configuracao.update_volume(self.som_volume.value())
        )
        self.som_volume.sliderReleased.connect(
            lambda:
            self.configuracao.alterar_som_volume(self.som_volume.value())
            )

        self.lbl_volume = QLabel()
        self.lbl_volume.setText(f"{self.configuracao.get_som_volume()}%")

        self.som_volume.sliderReleased.connect(
            lambda: self.lbl_volume.setText(f"{self.som_volume.value()}%")
        )

        self.btn_testar_som = QPushButton("▶ Testar som")
        self.btn_testar_som.clicked.connect(
            lambda: self.configuracao.testar_som(
                self.som_arquivo.currentText()
                )
            )
        
        volume_layout.addWidget(self.som_volume)
        volume_layout.addWidget(self.lbl_volume)
        volume_layout.addWidget(self.btn_testar_som)

        card_som.body.addLayout(volume_layout)

        content.addWidget(card_som)

    def create_tag(self, text):

        chip = TagChip(text)

        self.configuracao.add_tag(text)

        chip.removed.connect(self.remove_tag)

        self.tags_widget.add_chip(chip)

    # ========================================================

    def add_tag(self):

        text = self.txt_new_tag.text().strip()

        if not text:
            return

        self.create_tag(text)

        self.txt_new_tag.clear()

    # ========================================================

    def remove_tag(self, tag):

        self.configuracao.remove_tag(tag)

    # ========================================================