from src import db
from passlib.hash import pbkdf2_sha256 as sha256

class Usuario(db.Model):
    __tablename__='tb_usuario'

    id = db.Collumn(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Collumn(db.String(120), nullable=False)
    email = db.Collumn(db.String(120), nullable=False, unique=True)
    telefone = db.Collumn(db.String(50), nullable=False)
    senha = db.Collumn(db.String(255), nullable=False)
    
    #construtor da classe
    def __int__(self, nome, email, telefone, senha):
        self.nome = nome
        self.email = email
        self.telefone = telefone
        self.senha = senha

    def gen_senha(self, senha):
        self.senha = sha256.hash(senha)

    def verificar_senha(self, senha):
        return sha256.verify(senha, self.senha)
    
