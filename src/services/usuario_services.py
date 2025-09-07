from ..models import usuario_model
from src import db
from ..schemas import usuario_schema

def cadastrar_usuario(usuario):
    usuario_db = usuario_model.Usuario(nome= usuario.nome, email=usuario.email, telefone = usuario.telefone, senha= usuario.senha)
    #criptografia de senha
    usuario_db.gen_senha(usuario.senha)
    db.session.add(usuario_db)
    db.session.commit()
    return usuario_db

def listar_usuario():
    return usuario_model.Usuario.query.all()
    

def listar_usuario_id(id):
    try:
        #buscar usuario
        usuario_encontrado = usuario_model.Usuario.query.get(id)
        return usuario_encontrado
    except Exception as e:
        print(f"erro ao listar usuário por id {e}")
        return None
    
def exluir_usuario(id):
    # Busca o usuário pelo id
    usuario = usuario_model.Usuario.query.get(id)
    if usuario:
        # Se encontrar, exclui o usuário do banco
        db.session.delete(usuario)
        db.session.commit()
        return True  # Retorna True se excluiu com sucesso
    else:
        return False  # Retorna False se não encontrou o usuário
    
def editar_usuario(id, novo_usuario):
    # Busca o usuário pelo id
    usuario = usuario_model.Usuario.query.get(id)
    if usuario:
        # Atualiza os dados do usuário
        usuario.nome = novo_usuario.nome
        usuario.email = novo_usuario.email
        usuario.telefone = novo_usuario.telefone

        # Se foi informada uma nova senha, atualiza e criptografa
        if novo_usuario.senha:
            usuario.gen_senha(novo_usuario.senha)
        
        db.session.commit()  # Salva as alterações no banco
        return usuario  # Retorna o usuário atualizado

def listar_usuario_email(email):
    return usuario_model.Usuario.query.filter_by(email=email).first()

