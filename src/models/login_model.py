from src import db

class Login(db.Model):
    __tablename__ = 'tb_login'

    id = db.Collumn(db.Integer, primary_key=True, autoincrement=True)
    email = db.Collumn(db.String(120), nullable=False)
    senha = db.Collumn(db.String(120), nullable=False)