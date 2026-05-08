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

        username = request.form['username']

        password = generate_password_hash(
            request.form['password']
        )

        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:

            flash('El usuario ya existe')

            return redirect('/register')

        new_user = User(
            username=username,
            password=password
        )

        db.session.add(new_user)

        db.session.commit()

        flash('Usuario registrado correctamente 🚀')

        return redirect('/login')

    return render_template('register.html')


# LOGIN
@auth.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            session['user_id'] = user.id

            flash('Bienvenido 🚀')

            return redirect('/')

        else:

            flash('Credenciales incorrectas')

    return render_template('login.html')


# LOGOUT
@auth.route('/logout')
def logout():

    session.pop('user_id', None)

    flash('Sesión cerrada')

    return redirect('/login')