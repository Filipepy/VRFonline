from HRrequest import database, login_manager

from flask_login import UserMixin

@login_manager.user_loader
def load_usuario(id_usuario):
    return Usuario.query.get(int(id_usuario))
class Usuario(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String, nullable=False)
    email = database.Column(database.String, nullable=False, unique=True)
    senha = database.Column(database.String, nullable=False)
    perfil = database.Column(database.String, default='Padrao')
    createdate = database.Column(database.DateTime, nullable=False)
    foto_perfil = database.Column(database.String, default='default.jpg')


class Employees(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    id_employee = database.Column(database.Integer)
    name = database.Column(database.String, nullable=False)
    position = database.Column(database.String, nullable=False)
    costcenter = database.Column(database.String, nullable=False)
    limitedate = database.Column(database.Date, nullable=False)
    acperiod = database.Column(database.String, nullable=False)
    balance = database.Column(database.Integer, nullable=False)
    createdate = database.Column(database.DateTime, default='01/01/2024 00:00:00')


class RequestVacation(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    id_employee = database.Column(database.Integer)
    name = database.Column(database.String, nullable=False)
    position = database.Column(database.String, nullable=False)
    costcenter = database.Column(database.String, nullable=False)
    typecoverage = database.Column(database.String, nullable=False)
    namecoverage = database.Column(database.String, nullable=False)
    positioncoverage = database.Column(database.String, nullable=False)
    dtlimite = database.Column(database.String, nullable=False)
    dtstart = database.Column(database.Date, nullable=False)
    dtend = database.Column(database.Date, nullable=False)
    dtreturn = database.Column(database.String, nullable=False)
    dtemb = database.Column(database.Date, nullable=False)
    qtdday = database.Column(database.Integer, nullable=False)
    qtdsell = database.Column(database.Integer, nullable=False)
    advancesalary = database.Column(database.String, nullable=False)
    createby = database.Column(database.String, nullable=False)
    status = database.Column(database.String, nullable=False)
    createdate = database.Column(database.DateTime, nullable=False)
