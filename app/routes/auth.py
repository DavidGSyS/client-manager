from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    flash,
    session
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from app import db
from app.models.models import User

auth = Blueprint(
    'auth',
    __name__
)

# REGISTER
@auth.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username'].strip()

        if len(username) < 3:
            flash('El usuario debe tener al menos 3 caracteres')
            return redirect('/register')

        password = request.form['password']

        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres')
            return redirect('/register')

        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:
            flash('El usuario ya existe')
            return redirect('/register')

        new_user = User(
            username=username,
            password=generate_password_hash(password)
        )

        db.session.add(new_user)
        db.session.commit()

        flash('¡Cuenta creada correctamente! Inicia sesión 🚀')

        return redirect('/login')

    return render_template('register.html')


# LOGIN
@auth.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username'].strip()
        password = request.form['password']

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(user.password, password):

            session['user_id'] = user.id
            session['username'] = user.username

            flash('¡Bienvenido de vuelta! 🚀')

            return redirect('/')

        else:
            flash('Credenciales incorrectas')

    return render_template('login.html')


# LOGOUT
@auth.route('/logout')
def logout():

    session.pop('user_id', None)
    session.pop('username', None)

    flash('Sesión cerrada correctamente')

    return redirect('/login')