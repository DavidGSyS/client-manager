import os
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    flash, session, jsonify, url_for
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# ──────────────────────────────────────────────
# App Configuration
# ──────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24).hex())
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ──────────────────────────────────────────────
# Models
# ──────────────────────────────────────────────

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    clients = db.relationship(
        'Client', backref='owner', lazy=True, cascade='all, delete-orphan'
    )


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), default='')
    company = db.Column(db.String(100), default='')
    status = db.Column(db.String(20), default='active')
    notes = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# ──────────────────────────────────────────────
# Auth Helpers
# ──────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

# ──────────────────────────────────────────────
# Web Routes
# ──────────────────────────────────────────────

@app.route('/')
@login_required
def home():
    user = get_current_user()
    clients = Client.query.filter_by(user_id=user.id) \
        .order_by(Client.created_at.desc()).all()

    total = len(clients)
    active = sum(1 for c in clients if c.status == 'active')
    active_pct = round((active / total) * 100) if total > 0 else 0

    week_ago = datetime.utcnow() - timedelta(days=7)
    new_this_week = sum(1 for c in clients if c.created_at >= week_ago)

    chart_labels, chart_data = [], []
    for i in range(6, -1, -1):
        day = datetime.utcnow() - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        count = sum(1 for c in clients if day_start <= c.created_at < day_end)
        chart_labels.append(day.strftime('%d %b'))
        chart_data.append(count)

    return render_template(
        'index.html',
        clients=clients, user=user,
        total=total, active=active, inactive=total - active,
        active_pct=active_pct, new_this_week=new_this_week,
        chart_labels=chart_labels, chart_data=chart_data,
    )


@app.route('/add', methods=['POST'])
@login_required
def add_client():
    user = get_current_user()
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    company = request.form.get('company', '').strip()
    notes = request.form.get('notes', '').strip()

    if not name or not email:
        flash('Nombre y correo son obligatorios.', 'error')
        return redirect(url_for('dashboard.home'))

    client = Client(
        name=name, email=email, phone=phone,
        company=company, notes=notes, user_id=user.id
    )
    db.session.add(client)
    db.session.commit()
    flash('Cliente agregado correctamente 🚀', 'success')
    return redirect(url_for('dashboard.home'))


@app.route('/delete/<int:id>')
@login_required
def delete_client(id):
    user = get_current_user()
    client = Client.query.filter_by(id=id, user_id=user.id).first_or_404()
    db.session.delete(client)
    db.session.commit()
    flash('Cliente eliminado 🗑️', 'success')
    return redirect(url_for('dashboard.home'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_client(id):
    user = get_current_user()
    client = Client.query.filter_by(id=id, user_id=user.id).first_or_404()

    if request.method == 'POST':
        client.name = request.form.get('name', '').strip()
        client.email = request.form.get('email', '').strip()
        client.phone = request.form.get('phone', '').strip()
        client.company = request.form.get('company', '').strip()
        client.notes = request.form.get('notes', '').strip()
        client.status = request.form.get('status', 'active')
        db.session.commit()
        flash('Cliente actualizado ✨', 'success')
        return redirect(url_for('dashboard.home'))

    return render_template('edit.html', client=client, user=user)


@app.route('/toggle-status/<int:id>')
@login_required
def toggle_status(id):
    user = get_current_user()
    client = Client.query.filter_by(id=id, user_id=user.id).first_or_404()
    client.status = 'inactive' if client.status == 'active' else 'active'
    db.session.commit()
    flash(f'Estado de {client.name} actualizado.', 'success')
    return redirect(url_for('dashboard.home'))

# ──────────────────────────────────────────────
# Auth Routes
# ──────────────────────────────────────────────

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard.home'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not username or not email or not password:
            flash('Todos los campos son obligatorios.', 'error')
            return redirect(url_for('auth.register'))

        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'error')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash('Ese nombre de usuario ya existe.', 'error')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('Ese correo ya está registrado.', 'error')
            return redirect(url_for('auth.register'))

        user = User(
            username=username, email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        flash('Cuenta creada exitosamente. ¡Inicia sesión! 🚀', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.home'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'¡Bienvenido, {user.username}! 🚀', 'success')
            return redirect(url_for('dashboard.home'))
        else:
            flash('Credenciales incorrectas.', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('auth.login'))

# ──────────────────────────────────────────────
# REST API
# ──────────────────────────────────────────────

@app.route('/api/clients', methods=['GET'])
@login_required
def api_list_clients():
    user = get_current_user()
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '')
    sort = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = Client.query.filter_by(user_id=user.id)

    if search:
        query = query.filter(db.or_(
            Client.name.ilike(f'%{search}%'),
            Client.email.ilike(f'%{search}%'),
            Client.company.ilike(f'%{search}%'),
        ))
    if status in ('active', 'inactive'):
        query = query.filter_by(status=status)

    sort_col = getattr(Client, sort, Client.created_at)
    query = query.order_by(sort_col.asc() if order == 'asc' else sort_col.desc())

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'clients': [{
            'id': c.id, 'name': c.name, 'email': c.email,
            'phone': c.phone, 'company': c.company,
            'status': c.status, 'notes': c.notes,
            'created_at': c.created_at.isoformat(),
        } for c in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': paginated.page,
    })


@app.route('/api/clients', methods=['POST'])
@login_required
def api_create_client():
    user = get_current_user()
    data = request.get_json()
    if not data or not data.get('name') or not data.get('email'):
        return jsonify({'error': 'Nombre y correo son obligatorios'}), 400

    client = Client(
        name=data['name'], email=data['email'],
        phone=data.get('phone', ''), company=data.get('company', ''),
        notes=data.get('notes', ''), user_id=user.id,
    )
    db.session.add(client)
    db.session.commit()
    return jsonify({'id': client.id, 'message': 'Cliente creado'}), 201


@app.route('/api/clients/<int:id>', methods=['PUT'])
@login_required
def api_update_client(id):
    user = get_current_user()
    client = Client.query.filter_by(id=id, user_id=user.id).first()
    if not client:
        return jsonify({'error': 'Cliente no encontrado'}), 404

    data = request.get_json()
    for field in ('name', 'email', 'phone', 'company', 'status', 'notes'):
        if field in data:
            setattr(client, field, data[field])

    db.session.commit()
    return jsonify({'message': 'Cliente actualizado'})


@app.route('/api/clients/<int:id>', methods=['DELETE'])
@login_required
def api_delete_client(id):
    user = get_current_user()
    client = Client.query.filter_by(id=id, user_id=user.id).first()
    if not client:
        return jsonify({'error': 'Cliente no encontrado'}), 404

    db.session.delete(client)
    db.session.commit()
    return jsonify({'message': 'Cliente eliminado'})


@app.route('/api/dashboard', methods=['GET'])
@login_required
def api_dashboard():
    user = get_current_user()
    clients = Client.query.filter_by(user_id=user.id).all()
    total = len(clients)
    active = sum(1 for c in clients if c.status == 'active')
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_week = sum(1 for c in clients if c.created_at >= week_ago)

    labels, data = [], []
    for i in range(6, -1, -1):
        d = datetime.utcnow() - timedelta(days=i)
        s = d.replace(hour=0, minute=0, second=0, microsecond=0)
        e = s + timedelta(days=1)
        labels.append(d.strftime('%d %b'))
        data.append(sum(1 for c in clients if s <= c.created_at < e))

    return jsonify({
        'total': total, 'active': active, 'inactive': total - active,
        'active_pct': round((active / total) * 100) if total else 0,
        'new_this_week': new_week,
        'chart_labels': labels, 'chart_data': data,
    })

# ──────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)