from src.crud import CRUDUser
from flask import Flask, render_template, request, flash, session, redirect, Blueprint,url_for
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_bootstrap import Bootstrap
import hashlib

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect("/admin")
    return render_template('login.html')

@auth.route('/login', methods=['post'])
def login_post():
    user = request.form.get('user')
    password = request.form.get('password')
    Us = CRUDUser().loginUser(user)
    if Us == None:
        flash("Error en los datos introducidos") 
        return render_template("login.html")
    if Us.get_password() == hashlib.sha256(password.encode('utf-8')).hexdigest():
        login_user(Us)
        return redirect("/admin")
    return render_template("login.html")
    

@auth.route('/signup')
def signup_post():
    return redirect(url_for('auth.login'))

@auth.route('/logout')
def logout():
    logout_user()
    return redirect("/")