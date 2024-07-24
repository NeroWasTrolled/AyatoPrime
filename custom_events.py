import random
from datetime import datetime, timedelta

class GerenciadorDeEventos:
    def __init__(self):
        self.evento_atual = None
        self.eventos_ativos = False
        self.usuarios_em_evento = {}
        self.cooldowns_de_evento = {}

    def ativar_eventos(self):
        self.eventos_ativos = True

    def desativar_eventos(self):
        self.eventos_ativos = False
        self.evento_atual = None
        self.usuarios_em_evento = {}

    def pode_ativar_evento(self, user_id):
        if user_id in self.cooldowns_de_evento:
            return datetime.utcnow() > self.cooldowns_de_evento[user_id]
        return True

    def ativar_evento_para_usuario(self, user_id):
        self.usuarios_em_evento[user_id] = {
            'evento': random.choice(['adrenaline_meter', 'rage_meter']),
            'hora_inicio': datetime.utcnow(),
            'hora_fim': datetime.utcnow() + timedelta(minutes=5)
        }

    def desativar_evento_para_usuario(self, user_id):
        self.cooldowns_de_evento[user_id] = datetime.utcnow() + timedelta(minutes=30)
        if user_id in self.usuarios_em_evento:
            del self.usuarios_em_evento[user_id]

    def obter_evento_para_usuario(self, user_id):
        return self.usuarios_em_evento.get(user_id, None)

    def obter_efeitos_do_evento(self, rolagens, tipo_dado, evento):
        if evento['evento'] == 'adrenaline_meter':
            return [random.randint(max(1, tipo_dado - 2), tipo_dado) for _ in rolagens], "# ADRENALINE!"
        elif evento['evento'] == 'rage_meter':
            extra = random.randint(1, 5)
            media = (tipo_dado + 1) // 2
            rolagens_modificadas = [random.randint(media + 1, tipo_dado) + extra for _ in rolagens]
            mensagem = f"# RAGE!\n\nAll rolls +{extra}"
            if extra >= 4:
                mensagem += "\n\n# CRITICAL DAMAGE!"
            return rolagens_modificadas, mensagem
        else:
            return rolagens, None

gerenciador_de_eventos = GerenciadorDeEventos()
