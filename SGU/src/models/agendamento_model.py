from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from src import db


class AgendamentoModel(db.Model):

    __tablename__ = 'agendamentos'
    
    # Campos principais
    id = Column(Integer, primary_key=True, autoincrement=True)
    dt_agendamento = Column(DateTime, nullable=False, default=datetime.utcnow)
    dt_atendimento = Column(DateTime, nullable=False)
    
    # Chaves estrangeiras
    id_user = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    id_profissional = Column(Integer, ForeignKey('profissionais.id'), nullable=False)
    id_servico = Column(Integer, ForeignKey('servicos.id'), nullable=False)
    
    # Campos adicionais
    status = Column(String(20), nullable=False, default='agendado')
    observacoes = Column(Text, nullable=True)
    valor_total = Column(Numeric(10, 2), nullable=False, default=0.00)
    taxa_cancelamento = Column(Numeric(10, 2), nullable=True, default=0.00)
    
    # Relacionamentos
    usuario = relationship("UsuarioModel", backref="agendamentos")
    profissional = relationship("ProfissionalModel", backref="agendamentos")
    servico = relationship("ServicoModel", backref="agendamentos")

    # Agendamento
    
    def __init__(self, dt_atendimento, id_user, id_profissional, id_servico, 
                 observacoes=None, valor_total=0.00):

        self.dt_atendimento = dt_atendimento
        self.id_user = id_user
        self.id_profissional = id_profissional
        self.id_servico = id_servico
        self.observacoes = observacoes
        self.valor_total = valor_total
        self.dt_agendamento = datetime.utcnow()
        self.status = 'agendado'
        
    
    def to_dict(self): #TODO - Estudar o porque disso

        return {
            'id': self.id,
            'dt_agendamento': self.dt_agendamento.isoformat() if self.dt_agendamento else None,
            'dt_atendimento': self.dt_atendimento.isoformat() if self.dt_atendimento else None,
            'id_user': self.id_user,
            'id_profissional': self.id_profissional,
            'id_servico': self.id_servico,
            'status': self.status,
            'observacoes': self.observacoes,
            'valor_total': float(self.valor_total) if self.valor_total else 0.0,
            'taxa_cancelamento': float(self.taxa_cancelamento) if self.taxa_cancelamento else 0.0
        }
    
    
    #SECTION - CRUD NO BANCO
    
    def save(self): # Salvar no banco

        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Erro ao salvar agendamento: {str(e)}")
    
    def update(self, **kwargs): # Atualizar os dados no banco de dados

        try:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            db.session.commit()
            return self
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Erro ao atualizar agendamento: {str(e)}")
    
    def delete(self): # Deletar a informação do banco de dados

        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Erro ao deletar agendamento: {str(e)}")
        
        
    #SECTION Politica de cancelamento
    
    def pode_cancelar_gratuito(self): 

        agora = datetime.utcnow()
        diferenca = self.dt_atendimento - agora
        return diferenca.total_seconds() >= 7200  # 2 horas = 7200 segundos
    
    def calcular_taxa_cancelamento(self, valor_servico):

        agora = datetime.utcnow()
        diferenca = self.dt_atendimento - agora
        minutos_antecedencia = diferenca.total_seconds() / 60
        
        if minutos_antecedencia >= 120:  # 2 horas ou mais
            return 0.0
        elif minutos_antecedencia >= 90:  # 1h30min
            return valor_servico * 0.40
        elif minutos_antecedencia >= 60:  # 1h
            return valor_servico * 0.45
        elif minutos_antecedencia >= 30:  # 30min
            return valor_servico * 0.50
        else:  # Menos de 30min
            return valor_servico  # 100% do valor
        
    
    #SECTION Consultas no banco

    @staticmethod  # Consulta pelo id do agendamento
    def find_by_id(agendamento_id):

        return AgendamentoModel.query.filter_by(id=agendamento_id).first()
    
    @staticmethod # Consulta pelo id do usuario
    def find_by_user(user_id):

        return AgendamentoModel.query.filter_by(id_user=user_id).all()
    
    @staticmethod # Consulta dos horários de cada profissional
    def find_by_profissional_data(profissional_id, data): 

        inicio_dia = datetime.combine(data, datetime.min.time())
        fim_dia = datetime.combine(data, datetime.max.time())
        
        return AgendamentoModel.query.filter(
            AgendamentoModel.id_profissional == profissional_id,
            AgendamentoModel.dt_atendimento.between(inicio_dia, fim_dia),
            AgendamentoModel.status != 'cancelado'
        ).order_by(AgendamentoModel.dt_atendimento).all()
    
    @staticmethod # Consulta para evitar conflitos na agenda
    def find_conflitos_horario(profissional_id, dt_inicio, dt_fim):

        return AgendamentoModel.query.filter(
            AgendamentoModel.id_profissional == profissional_id,
            AgendamentoModel.status != 'cancelado',
            AgendamentoModel.dt_atendimento < dt_fim,
            # Assumindo que temos um campo dt_fim ou calculamos baseado na duração
        ).all()