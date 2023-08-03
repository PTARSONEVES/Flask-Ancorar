import functools
from sqlalchemy import text
from datetime import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from ...config import BaseConfig
from ...database.db import get_db
from ...mail.token import generate_confirmation_token, confirm_token
from ...mail.email import sendmail
from ...forms.auth.authform import FormRegister, FormLogin, FormLostInfoemail, FormLostChangepass

bp = Blueprint('auth', __name__, url_prefix='/auth')

# REGISTRO DE USUARIO

@bp.route('/register', methods=['GET','POST'])
def register():
    form = FormRegister()
    if form.validate_on_submit():
        username = form.usuario.data
        email = form.email.data
        password = form.senha.data
        db = get_db()
        criacao=datetime.now()
        try:
            query = text(
                f"INSERT INTO user (username, class_id, email, password, created_at, updated_at) VALUES (:username, :class_id, :email, :senha, :dado1, :dado2)"
            )
            db.execute(
                query,[{
                    'username' : username,
                    'class_id' : 3,
                    'email' : email,
                    'senha' : generate_password_hash(password),
                    'dado1' : criacao,
                    'dado2' : criacao
                }]
            )
            db.commit()
            token = generate_confirmation_token(email)
            confirm_url = url_for('auth.confirm_email',token=token,_external=True)
            html=render_template('auth/message_activate.html',confirm_url=confirm_url)
            subject="Por favor, confirme seu e-mail"
            sendmail(email,subject,html)
            flash('Um link de confirmação foi enviado para o e-mail cadastrado.','success')
            return redirect(url_for('auth.login'))
        except db.IntegrityError:
            error = f"Usuário {username} já está registrado. Faça o login."
            return render_template('auth/login.html', form=form)
    if form.errors != {}:
        for err in form.errors.values():
            flash(f"Erro ao cadastrar usuário {err}", category="danger")
    return render_template('auth/register.html', form=form)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    form=FormLogin()
    error = None
    if form.validate_on_submit():
        if request.method == 'POST':
            username=form.usuario.data
            password=form.senha.data
            if request.method == 'POST':
                db = get_db()
                query = text(
                    f"SELECT * FROM user WHERE username= :usuario;"
                )
                user = db.execute(query,{'usuario' : username}).fetchone()
                if user is None:
                    error = 1
                elif not check_password_hash(user.password, password):
                    error = 2
                if user.email_confirmed == '0':
                    error = 3 
                if error is None:
                    session.clear()
                    session['user_id'] = user.id
                    return redirect(url_for('home'))
    if form.errors != {}:
        for err in form.errors.values():
            flash(f"Erro ao efetuar login do usuário {err}", category="danger")
    if error != None:
        if error == 3:
            flash(f"Conta ainda não confirmada> Verifique seu e-mail", category="danger")
        else:
            flash(f"Erro ao efetuar login. Verificar senha e/ou usuário", category="danger")
    return render_template("auth/login.html", form=form)


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        db = get_db()
        query = text(
            f"SELECT * FROM user WHERE id = :usuario"
        )
        g.user = db.execute(query,{'usuario' : user_id}).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))
#    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('home'))
        return view(**kwargs)

    return wrapped_view

@bp.route('confirm/<token>')
#@login_required
def confirm_email(token):
    error = None
    try:
        email = confirm_token(token)
        if email != False:
            db = get_db()
            query = text(
                f"SELECT * FROM user WHERE email=  :mail"
            )
            usuario = db.execute(query,{'mail' : email}).fetchone()
            if email == usuario.email:
                if usuario.email_confirmed != '0':
                    flash('Esta conta já está confirmada. Por favor, faça seu login.','success')
                else:
                    try:
                        query = text(
                            f"UPDATE user SET email_verified_at= :dado1, email_confirmed= :emailconf, updated_at= :dado2 WHERE email= :mail"
                        )
                        db.execute(
                            query,[{
                                'dado1' : datetime.now(),
                                'emailconf' : '1',
                                'dado2' : datetime.now(),
                                'mail' : email
                            }]
                        )
                        db.commit()
                        flash('Sua conta está confirmada. Obrigado!','success')
                    except db.IntegrityError:
                        error = f"Erro na conexão com o banco de dados"
            return redirect(url_for('home'))
        else:
            error = 'O link de confirmação é inválido ou expirou.'
        return redirect(url_for('auth.login'))
    except:
        print('ERRO DESCONHECIDO')
        if error != None:
            flash({error},category='danger')
    return redirect(url_for('auth.login'))

# RECUPERAÇÃO DE SENHA

@bp.route('/lostinfoemail', methods=['GET', 'POST'])
def lostinfoemail():
    form=FormLostInfoemail()
    email = form.email.data
    if form.validate_on_submit():
        token = generate_confirmation_token(email)
        confirm_url = url_for('auth.confirm_lost',token=token,_external=True)
        html=render_template('auth/message_lostpass.html',confirm_url=confirm_url)
        subject="Por favor, confirme seu e-mail ("+str(datetime.now())+")"
        try:
            sendmail(email,subject,html)
            flash(f"Um link foi enviado ao email informado.", category="success")
            return redirect(url_for('auth.login'))
        except:
            print('NÂO ENVIOU...')
            return render_template('auth/login.html', form=form)
    else:
        if form.errors != {}:
            for err in form.errors.values():
                flash(f"{err}", category="danger")
        return render_template('auth/lost_infoemail.html', form=form)

@bp.route('/confirmlost/<token>', methods=['GET','POST'])
def confirm_lost(token):
    db = get_db()
    usuario=None
    try:
        email = confirm_token(token)
        query = text(
            f"SELECT * FROM user WHERE email = :email;"
        )
        user = db.execute(query, {'email' : email}).fetchone()
        usuario=user.id
        return redirect(url_for('auth.changepass', usuario=usuario))
    except:
#        flash('O link de confirmação é inválido ou expirouuuu.','danger')
        return render_template('auth/link_expirado.html', usuario=usuario)
#        return redirect(url_for('auth.login'))

@bp.route('/changepass/<usuario>', methods=['GET','POST'])
def changepass(usuario):
    form = FormLostChangepass()
    db = get_db()
    if form.validate_on_submit():
        senha = generate_password_hash(form.senha.data)
        criacao=datetime.now()
        query = text(
            f"UPDATE user SET password= :senha,updated_at= :data1 WHERE id= :user;"
        )
        db.execute(query,[{
            'senha' : senha,
            'data1' : criacao,
            'user' : usuario
            }]
        )
        db.commit()
        flash('Senha alterada com sucesso!! Faça seu login.','success')
        return redirect(url_for('auth.login'))
    return render_template('auth/lost_changepass.html', form=form, usuario=usuario)
