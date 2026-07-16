import json
import os
import re
from copy import deepcopy

from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import QUrl


CONFIG_FILE = "config.json"


DEFAULT_CONFIG = {
    "config_file": "config.json",
    "database_file": "estudos.db",

    "usuario": "usuário",

    "dias_estudo_semanal": [
        "dom",
        "seg",
        "ter",
        "qua",
        "qui",
        "sex",
        "sab"
    ],

    "quadro_semanal": {
        "dom": [],
        "seg": [],
        "ter": [],
        "qua": [],
        "qui": [],
        "sex": [],
        "sab": []
    },

    "hora_ini_dia": "08:00",
    "hora_fim_dia": "22:30",

    "ultimo_timer": 60,
    
    "cronometro": {
        "largura": 240,
        "altura": 420
    },

    "som": {
        "arquivo": "",
        "volume": 100
    },

    "tags": [
        "Teoria",
        "Revisão",
        "Simulados",
        "Exercícios"
    ],

    "disciplinas": {
        "Português": {
            "cor": "#FFB3BA",
            "meta_semanal": 0,
            "peso": 1,
            "oculto": 0,
            "topicos": []
        }
    },

    # Progresso para cumprir o cronograma
    "progress_levels": {
        "40": "Um jegue faz melhor",
        "42": "Chama o suporte",
        "44": "Não dê nem água",
        "46": "Catástrofe",
        "48": "Deu muito ruim",
        "50": "Deu ruim",
        "52": "Muito ruim",
        "54": "Tá osso",
        "56": "Tá complicado viu",
        "58": "Sobreviveu",
        "60": "Passou (nem perto de) raspando",
        "62": "Quase funcionando",
        "64": "Faz o básico",
        "66": "Regular",
        "68": "Tá pagando a mensalidade",
        "70": "Dá pro gasto",
        "72": "Decente",
        "74": "Entrou no jogo",
        "76": "Começando a cozinhar",
        "78": "Tá legal",
        "80": "Joio largando o centeio",
        "82": "Mandou bem",
        "84": "Ótimo",
        "86": "Tá carregando o time",
        "88": "Brabo demais",
        "90": "Excelente",
        "92": "Amassou",
        "94": "Absolute cinema",
        "96": "Mano das galáxias",
        "98": "Lendário"
    },

    # Performance nos simulados
    "performance_levels": {
        "49": "NPC perdido",
        "50": "🪵▫️▫️▫️▫️ Madeira",
        "51": "🪵🪵▫️▫️▫️ Madeira",
        "52": "🪵🪵🪵▫️▫️ Madeira",
        "53": "🪵🪵🪵🪵▫️ Madeira",
        "54": "🪵🪵🪵🪵🪵 Madeira",
        "55": "🪨▫️▫️▫️▫️ Pedra",
        "56": "🪨🪨▫️▫️▫️ Pedra",
        "57": "🪨🪨🪨▫️▫️ Pedra",
        "58": "🪨🪨🪨🪨▫️ Pedra",
        "59": "🪨🪨🪨🪨🪨 Pedra",
        "60": "⚙️▫️▫️▫️▫️ Ferro",
        "61": "⚙️⚙️▫️▫️▫️ Ferro",
        "62": "⚙️⚙️⚙️▫️▫️ Ferro",
        "63": "⚙️⚙️⚙️⚙️▫️ Ferro",
        "64": "⚙️⚙️⚙️⚙️⚙️ Ferro",
        "65": "🥉▫️▫️▫️▫️ Bronze",
        "66": "🥉🥉▫️▫️▫️ Bronze",
        "67": "🥉🥉🥉▫️▫️ Bronze",
        "68": "🥉🥉🥉🥉▫️ Bronze",
        "69": "🥉🥉🥉🥉🥉 Bronze",
        "70": "🥈▫️▫️▫️▫️ Prata",
        "71": "🥈🥈▫️▫️▫️ Prata",
        "72": "🥈🥈🥈▫️▫️ Prata",
        "73": "🥈🥈🥈🥈▫️ Prata",
        "74": "🥈🥈🥈🥈🥈 Prata",
        "75": "🥇▫️▫️▫️▫️ Ouro",
        "76": "🥇🥇▫️▫️▫️ Ouro",
        "77": "🥇🥇🥇▫️▫️ Ouro",
        "78": "🥇🥇🥇🥇▫️ Ouro",
        "79": "🥇🥇🥇🥇🥇 Ouro",
        "80": "💠▫️▫️▫️▫️ Platina",
        "81": "💠💠▫️▫️▫️ Platina",
        "82": "💠💠💠▫️▫️ Platina",
        "83": "💠💠💠💠▫️ Platina",
        "84": "💠💠💠💠💠 Platina",
        "85": "💎▫️▫️▫️▫️ Diamante",
        "86": "💎💎▫️▫️▫️ Diamante",
        "87": "💎💎💎▫️▫️ Diamante",
        "88": "💎💎💎💎▫️ Diamante",
        "89": "💎💎💎💎💎 Diamante",
        "90": "👑▫️▫️▫️▫️ Mestre",
        "91": "👑👑▫️▫️▫️ Mestre",
        "92": "👑👑👑▫️▫️ Mestre",
        "93": "👑👑👑👑▫️ Mestre",
        "94": "👑👑👑👑👑 Mestre",
        "95": "🏆▫️▫️▫️▫️ Lendário",
        "96": "🏆🏆▫️▫️▫️ Lendário",
        "97": "🏆🏆🏆▫️▫️ Lendário",
        "98": "🏆🏆🏆🏆▫️ Lendário",
        "99": "🏆🏆🏆🏆🏆 Lendário"
    }
}


class ConfigManager:

    def __init__(self):

        self.config = self.load_config()
        self.player = QSoundEffect()

    def _nova_disciplina(
            self,
            cor="#A0C4FF",
            meta_semanal=0,
            peso=1.0,
            oculto=0
        ):
            return {
                "cor": cor,
                "meta_semanal": meta_semanal,
                "peso": peso,
                "oculto": oculto,
                "topicos": []
            }

    # =====================================================
    # CONFIGURAÇÃO
    # =====================================================

    def load_config(self):

        if not os.path.exists(CONFIG_FILE):

            with open(CONFIG_FILE, "w", encoding="utf-8") as file:
                json.dump(
                    DEFAULT_CONFIG,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            return deepcopy(DEFAULT_CONFIG)

        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            config = json.load(file)

        atualizado = self._merge_missing_keys(
            config,
            DEFAULT_CONFIG
        )

        if atualizado:
            self.save_config(config)
        
        if self._migrar_disciplinas_antigas(config):
            self.save_config(config)

        return config
    
    def reload(self): # Precisa desse método pq o bendito guarda uma cópia do json na memória. Ai é preciso resetar sempre que fizer uma nova alteração. É uma gambiarra

        with open(
            CONFIG_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            self.config = json.load(file)

    def save_config(self, config_data=None):

        if config_data is None:
            config_data = self.config

        with open(
            CONFIG_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                config_data,
                file,
                indent=4,
                ensure_ascii=False
            )

    def _merge_missing_keys(self, current, default):

        modified = False

        for key, value in default.items():

            if key not in current:

                current[key] = deepcopy(value)
                modified = True

            elif (
                isinstance(value, dict)
                and isinstance(current[key], dict)
            ):

                if self._merge_missing_keys(
                    current[key],
                    value
                ):
                    modified = True

        return modified
    
    def _migrar_disciplinas_antigas(self, config):

        modificou = False

        disciplinas = config["disciplinas"]

        for nome, valor in list(disciplinas.items()):

            if isinstance(valor, list):

                disciplinas[nome] = {
                    "cor": "#A0C4FF",
                    "meta_semanal": 0,
                    "peso": 1.0,
                    "oculto": 0,
                    "topicos": valor
                }

                modificou = True

        return modificou

    # =====================================================
    # GETTERS
    # =====================================================

    def get_database_file(self):
        return self.config["database_file"]
    
    def get_disciplinas(self): # Retorna o nome das disciplinas
        return list(
            self.config.get("disciplinas", {}).keys()
        )
    
    def get_info_disciplina(self, disciplina): # Retorna informações sobre uma disciplina específica
        return self.config["disciplinas"].get(
            disciplina
        )
    
    def get_nome_usuario(self):
        return self.config["usuario"]
    
    def get_ultimo_timer(self):
        return self.config["ultimo_timer"]
    
    def get_dias_estudo_semanal(self):
        return self.config["dias_estudo_semanal"]
    
    def get_quadro_semanal(self, dia):
        
        if dia not in self.config["quadro_semanal"]:
            return []
        
        return self.config["quadro_semanal"][dia]
    
    def get_hora_ini_dia(self):
        return self.config["hora_ini_dia"]

    def get_hora_fim_dia(self):
        return self.config["hora_fim_dia"]
    
    def get_cronometro_width(self):
        return self.config["cronometro"]["largura"]
    
    def get_cronometro_high(self):
        return self.config["cronometro"]["altura"]
    
    def get_som_arquivo(self):
        return self.config["som"]["arquivo"]
    
    def get_som_volume(self):
        return self.config["som"]["volume"]
    
    def get_cor_disciplina(self, disciplina):

        if disciplina not in self.config["disciplinas"]:
            return None

        return self.config["disciplinas"][disciplina]["cor"]
    
    def get_cores_disciplinas(self): # útil para os gráficos

        return {
            nome: dados["cor"]
            for nome, dados
            in self.config["disciplinas"].items()
        }

    def get_topicos(self, disciplina):

        if disciplina not in self.config["disciplinas"]:
            return []

        return self.config["disciplinas"][disciplina][
            "topicos"
        ]
    
    def get_meta_semanal(self, disciplina):

        if disciplina not in self.config["disciplinas"]:
            return None

        return self.config["disciplinas"][disciplina][
            "meta_semanal"
        ]
    
    def get_peso_disciplina(self, disciplina):

        if disciplina not in self.config["disciplinas"]:
            return None

        return self.config["disciplinas"][disciplina][
            "peso"
        ]
    
    def get_oculto_disciplina(self, disciplina):

        if disciplina not in self.config["disciplinas"]:
            return None

        return self.config["disciplinas"][disciplina][
            "oculto"
        ]

    def get_tags(self):
        return self.config["tags"]
    
    # =====================================================
    #  CAMPOS ÚNICOS
    # =====================================================

    def alterar_database_file(self, nome_do_arquivo):
        self.reload()
        self.config["database_file"] = nome_do_arquivo
        self.save_config()

    def alterar_usuario(self, user_name):
        self.reload()
        self.config["usuario"] = user_name
        self.save_config()

    def alterar_hora_ini_dia(self, hora):
        self.reload()
        self.config["hora_ini_dia"] = hora.toString("HH:mm")
        self.save_config()

    def alterar_hora_fim_dia(self, hora):
        self.reload()
        self.config["hora_fim_dia"] = hora.toString("HH:mm")
        self.save_config()

    def alterar_ultimo_timer(self, minutos):
        self.reload()
        self.config["ultimo_timer"] = minutos
        self.save_config()

    def alterar_cronometro_largura(self, largura):
        self.reload()
        self.config["cronometro"]["largura"] = largura
        self.save_config()

    def alterar_cronometro_altura(self, altura):
        self.reload()
        self.config["cronometro"]["altura"] = altura
        self.save_config()

    # =====================================================
    #  DIAS ESTUDO SEMANAL
    # =====================================================

    def alterar_dia_estudo_semanal(self, checked, dia):
        self.reload()
        if checked:
            if dia not in self.config["dias_estudo_semanal"]:
                self.config["dias_estudo_semanal"].append(dia)
                self.save_config()
        else:
            if dia in self.config["dias_estudo_semanal"]:
                self.config["dias_estudo_semanal"].remove(dia)
                self.save_config()
    # =====================================================
    # QUADRO SEMANAL
    # =====================================================

    def set_quadro_semanal(self, quadro):

        self.reload()

        self.config["quadro_semanal"] = quadro
        self.save_config()

    # =====================================================
    # DISCIPLINAS
    # =====================================================

    def add_disciplina(
        self,
        disciplina,
        cor="#A0C4FF",
        meta_semanal=0,
        peso=1.0,
        oculto=0
    ):
        self.reload()

        disciplina = disciplina.strip()

        if not disciplina:
            return False

        if disciplina in self.config["disciplinas"]:
            return False

        self.config["disciplinas"][disciplina] = (
            self._nova_disciplina(
                cor,
                meta_semanal,
                peso,
                oculto
            )
        )

        self.save_config()

        return True
    
    def rename_disciplina(self, disciplina_antiga, disciplina_nova):
        self.reload()

        disciplina_nova = disciplina_nova.strip()
        if not disciplina_nova: # Para o caso de o usuário tentar por um campo vazio
            return False

        disciplinas = self.config["disciplinas"]

        if disciplina_antiga not in disciplinas:
            return False

        if disciplina_nova in disciplinas:
            return False

        disciplinas[disciplina_nova] = disciplinas.pop(
            disciplina_antiga
        )

        self.save_config()

        return True


    def remove_disciplina(self, disciplina):
        self.reload()

        if disciplina not in self.config["disciplinas"]:
            return False

        del self.config["disciplinas"][disciplina]

        self.save_config()

        return True
    
    # =====================================================
    # COR
    # =====================================================

    def validar_cor(self, cor):
        return bool(
            re.match(
                r"^#[0-9A-Fa-f]{6}$",
                cor
            )
        )

    def set_cor_disciplina(
        self,
        disciplina,
        cor
    ):
        self.reload()
        if not self.validar_cor(cor):
            return False

        if disciplina not in self.config["disciplinas"]:
            return False

        self.config["disciplinas"][disciplina]["cor"] = cor

        self.save_config()

        return True
    
    # =====================================================
    # META SEMANAL
    # =====================================================

    def set_meta_semanal(
        self,
        disciplina,
        meta
    ):
        self.reload()

        try:
            meta = int(meta)
        except:
            return False

        if disciplina not in self.config["disciplinas"]:
            return False

        self.config["disciplinas"][disciplina][
            "meta_semanal"
        ] = meta

        self.save_config()

        return True
    
    # =====================================================
    # METODO DE PESO
    # =====================================================
    def set_peso_disciplina(
        self,
        disciplina,
        peso
    ):
        self.reload()
        try:
            peso = float(peso)
        except:
            return False

        if disciplina not in self.config["disciplinas"]:
            return False

        self.config["disciplinas"][disciplina][
            "peso"
        ] = peso

        self.save_config()

        return True
    
    # =====================================================
    # METODO OCULTO
    # =====================================================
    
    def set_oculto_disciplina(
        self,
        disciplina,
        oculto
    ):
        self.reload()

        oculto = int(bool(oculto))

        if disciplina not in self.config["disciplinas"]:
            return False

        self.config["disciplinas"][disciplina][
            "oculto"
        ] = oculto

        self.save_config()

        return True
    # =====================================================
    # TÓPICOS
    # =====================================================

    def add_topico(
        self,
        disciplina,
        topico
    ):
        self.reload()

        if disciplina not in self.config["disciplinas"]:
            return False

        topicos = self.config["disciplinas"][disciplina][
            "topicos"
        ]

        if topico in topicos:
            return False

        topicos.append(topico)

        self.save_config()

        return True

    

    def rename_topico(
        self,
        disciplina,
        topico_antigo,
        topico_novo
    ):
        self.reload()

        topico_novo = topico_novo.strip() # Verifica se o conteúdo de topico_novo está vazio
        if not topico_novo:
            return False

        if disciplina not in self.config["disciplinas"]:
            return False

        topicos = self.config["disciplinas"][disciplina][
            "topicos"
        ]

        if topico_antigo not in topicos:
            return False
        
        if topico_novo in topicos: # Verifica se o tópico já não está na lista de tópicos. Elimina tópicos repetidos (Erro que ainda tem no estudei)
            return False

        indice = topicos.index(topico_antigo)

        topicos[indice] = topico_novo

        self.save_config()

        return True
    
    
    def remove_topico(
        self,
        disciplina,
        topico
    ):
        self.reload()

        if disciplina not in self.config["disciplinas"]:
            return False

        topicos = self.config["disciplinas"][disciplina][
            "topicos"
        ]

        if topico not in topicos:
            return False

        topicos.remove(topico)

        self.save_config()

        return True

    # =====================================================
    # TAGS
    # =====================================================

    def add_tag(self, tag):
        self.reload()

        tag = tag.strip()

        if not tag:
            return False

        if tag not in self.config["tags"]:

            self.config["tags"].append(tag)

            self.save_config()

            return True

        return False

    def remove_tag(self, tag):
        self.reload()

        if tag in self.config["tags"]:

            self.config["tags"].remove(tag)

            self.save_config()

            return True

        return False

    def rename_tag(
        self,
        tag_antiga,
        tag_nova
    ):
        self.reload()
        tag_nova = tag_nova.strip() # verifica se tag_nova está vazia
        if not tag_nova:
            return False

        tags = self.config["tags"]

        if tag_antiga not in tags:
            return False

        if tag_nova in tags:
            return False

        indice = tags.index(tag_antiga)

        tags[indice] = tag_nova

        self.save_config()

        return True
    
    # =====================================================
    # SOM
    # =====================================================

    def alterar_som_arquivo(self, arquivo):

        self.reload()
        
        self.config["som"]["arquivo"] = arquivo
        
        self.save_config()

    def update_audio_file(self):

        self.reload()

        sons_dir = self.get_sons_dir()

        if not os.path.exists(sons_dir):
            return []

        arquivos_wav = sorted([
            f for f in os.listdir(sons_dir)
            if f.lower().endswith(".wav")
        ])

        return arquivos_wav
    
    def get_sons_dir(self):

        return os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            ),
            "sons"
        )
    
    def update_volume(self, volume):
        volume = volume / 100
        self.player.setVolume(volume)

    def alterar_som_volume(self, volume):
        self.reload()
        self.config["som"]["volume"] = volume
        self.save_config()
    
    def testar_som(self, arquivo):

        if not arquivo:
            return

        audio_path = os.path.join(
            self.get_sons_dir(),
            arquivo
        )

        if not os.path.exists(audio_path):
            return

        self.player.setSource(
            QUrl.fromLocalFile(audio_path)
        )

        self.player.play()


# =========================================================
# EXEMPLO DE USO
# =========================================================

# if __name__ == "__main__":

#     config_estudo = ConfigManager()

#     # COM FUNÇÃO DEDICADA

#     config_estudo.add_disciplina(
#         "Matemática",
#         cor="#A0C4FF",
#         meta_semanal=12,
#         peso=2.0
#     )

#     config_estudo.add_topico(
#         "Matemática",
#         "Funções"
#     )

#     print(
#         config_estudo.get_cor_disciplina(
#             "Matemática"
#         )
#     )

#     print(
#         config_estudo.get_meta_semanal(
#             "Matemática"
#         )
#     )

#     print(
#         config_estudo.get_peso_disciplina(
#             "Matemática"
#         )
#     )

#     print(
#         config_estudo.get_topicos(
#             "Matemática"
#         )
#     )
    
    # print(config.get_topicos("Matemática"))

    # # SEM FUNÇÃO DEDICADA

    # config.config["hora_ini_dia"] = "9:00"

    # print(config.config["hora_ini_dia"])



    # # IMPORTANTE !!!
    # # O ARQUIVO SOMENTE É SALVO DEPOIS QUE CHAMA ESSE MÉTODO:

    # confiG.save_config() 






    # print(config.config["tags"])

    # # Adicionar nova disciplina
    # config.config["disciplinas"]["Biologia"] = [
    #     "Citologia",
    #     "Genética"
    # ]

    # print(config.config["disciplinas"])
