from flask import render_template, request, flash, session, redirect, Blueprint
from flask_login import login_required, current_user
from src.crud import CRUDSummoners
crud = CRUDSummoners()

main = Blueprint('main', __name__)

@main.route('/')
def Home():
    lista = crud.readLeague()
    lista = crud.ordenarLista(lista)
    return render_template('home.html', lista = lista)

@main.route('/updateData')
def updateData():
    crud.updateLeague()
    return redirect("/")

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/admin')
@login_required
def admin():
    lista = crud.readLeague()
    return render_template("crud.html", lista = lista)

@main.route('/addSummoner', methods=['POST'])
@login_required
def addSummoner():
    summoner = request.form.get("summonerNew")
    crud.createUser(summoner)
    return redirect("/admin")

@main.route('/addRiotApi', methods=['POST'])
@login_required
def addRiotApi():
    riotApi = request.form.get("riotApi")
    crud.updateRiotApi(riotApi)
    return redirect("/admin")
