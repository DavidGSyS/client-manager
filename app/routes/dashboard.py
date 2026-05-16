import csv
import io
from datetime import datetime, timedelta
from collections import defaultdict

from flask import (
    Blueprint, render_template, request, redirect,
    flash, session, Response, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.models.models import Client, User
from app.utils.decorators import login_required

dashboard = Blueprint('dashboard', __name__)


# ─────────────────────────────────────────────
# HOME / DASHBOARD
# ─────────────────────────────────────────────
@dashboard.route('/')
@login_required
def home():
    clients = Client.query.filter_by(
        user_id=session['user_id'], archived=False
    ).order_by(Client.created_at.desc()).all()

    total = len(clients)
    active = len([c for c in clients if c.status == 'active'])
    inactive = total - active
    active_pct = round((active / total) * 100) if total > 0 else 0

    one_week_ago = datetime.utcnow() - timedelta(days=7)
    new_this_week = len([c for c in clients if c.created_at >= one_week_ago])

    two_weeks_ago = datetime.utcnow() - timedelta(days=14)
    prev_week = len([c for c in clients if two_weeks_ago <= c.created_at < one_week_ago])

    if prev_week > 0:
        growth_pct = round(((new_this_week - prev_week) / prev_week) * 100)
    elif new_this_week > 0:
        growth_pct = 100
    else:
        growth_pct = 0

    day_labels, day_data = [], []
    day_names = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    for i in range(6, -1, -1):
        target_day = datetime.utcnow() - timedelta(days=i)
        day_labels.append(day_names[target_day.weekday()])
        day_data.append(len([c for c in clients if c.created_at.date() == target_day.date()]))

    archived_count = Client.query.filter_by(user_id=session['user_id'], archived=True).count()

    return render_template(
        'index.html',
        clients=clients,
        total=total, active=active, active_pct=active_pct,
        inactive=inactive, new_this_week=new_this_week,
        growth_pct=growth_pct, chart_labels=day_labels, chart_data=day_data,
        archived_count=archived_count
    )


# ─────────────────────────────────────────────
# STATISTICS PAGE
# ─────────────────────────────────────────────
@dashboard.route('/stats')
@login_required
def stats():
    clients = Client.query.filter_by(
        user_id=session['user_id'], archived=False
    ).order_by(Client.created_at.asc()).all()

    total = len(clients)
    active = len([c for c in clients if c.status == 'active'])
    inactive = total - active

    # Top companies
    company_counts = defaultdict(int)
    for c in clients:
        key = c.company or 'Sin empresa'
        company_counts[key] += 1
    top_companies = sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:6]

    # Growth last 30 days (cumulative)
    growth_labels, growth_data = [], []
    base = datetime.utcnow() - timedelta(days=29)
    cumulative = Client.query.filter_by(
        user_id=session['user_id'], archived=False
    ).filter(Client.created_at < base).count()

    for i in range(30):
        target = base + timedelta(days=i)
        day_count = len([c for c in clients if c.created_at.date() == target.date()])
        cumulative += day_count
        growth_labels.append(target.strftime('%d/%m'))
        growth_data.append(cumulative)

    # Registrations per weekday
    weekday_counts = [0] * 7
    for c in clients:
        weekday_counts[c.created_at.weekday()] += 1
    weekday_names = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

    # Monthly trend (last 6 months)
    month_labels, month_data = [], []
    for i in range(5, -1, -1):
        target = datetime.utcnow() - timedelta(days=i * 30)
        label = target.strftime('%b %Y')
        count = len([
            c for c in clients
            if c.created_at.year == target.year and c.created_at.month == target.month
        ])
        month_labels.append(label)
        month_data.append(count)

    return render_template(
        'stats.html',
        total=total, active=active, inactive=inactive,
        top_companies=top_companies,
        growth_labels=growth_labels, growth_data=growth_data,
        weekday_names=weekday_names, weekday_counts=weekday_counts,
        month_labels=month_labels, month_data=month_data,
        active_pct=round((active / total) * 100) if total > 0 else 0
    )


# ─────────────────────────────────────────────
# ADD CLIENT
# ─────────────────────────────────────────────
@dashboard.route('/add', methods=['POST'])
@login_required
def add_client():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    if not name or not email:
        flash('Nombre y email son requeridos')
        return redirect('/')

    new_client = Client(
        name=name, email=email,
        phone=request.form.get('phone', '').strip() or None,
        company=request.form.get('company', '').strip() or None,
        notes=request.form.get('notes', '').strip() or None,
        status='active', archived=False,
        user_id=session['user_id']
    )
    db.session.add(new_client)
    db.session.commit()
    flash('¡Cliente agregado exitosamente! 🚀')
    return redirect('/')


# ─────────────────────────────────────────────
# CLIENT DETAIL
# ─────────────────────────────────────────────
@dashboard.route('/client/<int:id>')
@login_required
def client_detail(id):
    client = Client.query.filter_by(id=id, user_id=session['user_id']).first_or_404()
    return render_template('client_detail.html', client=client)


# ─────────────────────────────────────────────
# EDIT CLIENT
# ─────────────────────────────────────────────
@dashboard.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_client(id):
    client = Client.query.filter_by(id=id, user_id=session['user_id']).first_or_404()

    if request.method == 'POST':
        client.name = request.form['name'].strip()
        client.email = request.form['email'].strip()
        client.phone = request.form.get('phone', '').strip() or None
        client.company = request.form.get('company', '').strip() or None
        client.notes = request.form.get('notes', '').strip() or None
        client.status = request.form.get('status', 'active')
        client.updated_at = datetime.utcnow()
        db.session.commit()
        flash('¡Cliente actualizado correctamente! ✨')
        return redirect('/')

    return render_template('edit.html', client=client)


# ─────────────────────────────────────────────
# ARCHIVE CLIENT (soft delete)
# ─────────────────────────────────────────────
@dashboard.route('/archive/<int:id>')
@login_required
def archive_client(id):
    client = Client.query.filter_by(id=id, user_id=session['user_id']).first_or_404()
    client.archived = True
    client.updated_at = datetime.utcnow()
    db.session.commit()
    flash(f'"{client.name}" fue archivado. Puedes restaurarlo desde Archivados. 🗃️')
    return redirect('/')


# ─────────────────────────────────────────────
# ARCHIVED CLIENTS LIST
# ─────────────────────────────────────────────
@dashboard.route('/archived')
@login_required
def archived_list():
    clients = Client.query.filter_by(
        user_id=session['user_id'], archived=True
    ).order_by(Client.updated_at.desc()).all()
    return render_template('archived.html', clients=clients)


# ─────────────────────────────────────────────
# RESTORE CLIENT
# ─────────────────────────────────────────────
@dashboard.route('/restore/<int:id>')
@login_required
def restore_client(id):
    client = Client.query.filter_by(id=id, user_id=session['user_id']).first_or_404()
    client.archived = False
    client.updated_at = datetime.utcnow()
    db.session.commit()
    flash(f'"{client.name}" fue restaurado exitosamente ✅')
    return redirect('/archived')


# ─────────────────────────────────────────────
# DELETE PERMANENT
# ─────────────────────────────────────────────
@dashboard.route('/delete-permanent/<int:id>')
@login_required
def delete_permanent(id):
    client = Client.query.filter_by(id=id, user_id=session['user_id']).first_or_404()
    name = client.name
    db.session.delete(client)
    db.session.commit()
    flash(f'"{name}" eliminado permanentemente 🗑️')
    return redirect('/archived')


# ─────────────────────────────────────────────
# DELETE CLIENT (legacy — now redirects to archive)
# ─────────────────────────────────────────────
@dashboard.route('/delete/<int:id>')
@login_required
def delete_client(id):
    return redirect(f'/archive/{id}')


# ─────────────────────────────────────────────
# TOGGLE STATUS
# ─────────────────────────────────────────────
@dashboard.route('/toggle-status/<int:id>')
@login_required
def toggle_status(id):
    client = Client.query.filter_by(id=id, user_id=session['user_id']).first_or_404()
    client.status = 'inactive' if client.status == 'active' else 'active'
    client.updated_at = datetime.utcnow()
    db.session.commit()
    flash('Estado actualizado ✨')
    return redirect('/')


# ─────────────────────────────────────────────
# EXPORT CSV
# ─────────────────────────────────────────────
@dashboard.route('/export/csv')
@login_required
def export_csv():
    clients = Client.query.filter_by(
        user_id=session['user_id'], archived=False
    ).order_by(Client.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Nombre', 'Email', 'Teléfono', 'Empresa', 'Estado', 'Notas', 'Fecha de Registro', 'Última Actualización'])
    for c in clients:
        writer.writerow([
            c.id, c.name, c.email,
            c.phone or '', c.company or '',
            'Activo' if c.status == 'active' else 'Inactivo',
            c.notes or '',
            c.created_at.strftime('%Y-%m-%d %H:%M') if c.created_at else '',
            c.updated_at.strftime('%Y-%m-%d %H:%M') if c.updated_at else '',
        ])

    output.seek(0)
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    return Response(
        output.getvalue(), mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=clientes_{timestamp}.csv'}
    )


# ─────────────────────────────────────────────
# CSV TEMPLATE DOWNLOAD
# ─────────────────────────────────────────────
@dashboard.route('/template/csv')
@login_required
def template_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['nombre', 'email', 'telefono', 'empresa', 'notas', 'estado'])
    writer.writerow(['Juan Pérez', 'juan@ejemplo.com', '+57 300 000 0000', 'Mi Empresa SAS', 'Cliente referido', 'active'])
    writer.writerow(['María García', 'maria@empresa.com', '', 'Tech Corp', '', 'active'])
    output.seek(0)
    return Response(
        output.getvalue(), mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=plantilla_clientes.csv'}
    )


# ─────────────────────────────────────────────
# IMPORT CSV
# ─────────────────────────────────────────────
@dashboard.route('/import/csv', methods=['GET', 'POST'])
@login_required
def import_csv():
    if request.method == 'POST':
        file = request.files.get('csv_file')
        if not file or not file.filename.endswith('.csv'):
            flash('Por favor sube un archivo .csv válido')
            return redirect('/import/csv')

        imported, errors = 0, []
        try:
            content = file.read().decode('utf-8-sig')
            reader = csv.DictReader(io.StringIO(content))

            # Normalize headers
            def norm(k):
                return k.strip().lower().replace(' ', '_').replace('é', 'e').replace('ó', 'o')

            for row_num, row in enumerate(reader, start=2):
                normalized = {norm(k): (v or '').strip() for k, v in row.items()}

                name = normalized.get('nombre') or normalized.get('name') or ''
                email = normalized.get('email') or normalized.get('correo') or ''

                if not name or not email:
                    errors.append(f'Fila {row_num}: nombre o email faltante')
                    continue

                status_val = normalized.get('estado') or normalized.get('status') or 'active'
                if status_val.lower() in ('activo', 'active', '1', 'yes', 'si', 'sí'):
                    status_val = 'active'
                else:
                    status_val = 'inactive'

                client = Client(
                    name=name,
                    email=email,
                    phone=normalized.get('telefono') or normalized.get('phone') or None,
                    company=normalized.get('empresa') or normalized.get('company') or None,
                    notes=normalized.get('notas') or normalized.get('notes') or None,
                    status=status_val,
                    archived=False,
                    user_id=session['user_id']
                )
                db.session.add(client)
                imported += 1

            db.session.commit()

        except Exception as e:
            errors.append(f'Error procesando archivo: {str(e)}')

        return render_template(
            'import_csv.html',
            imported=imported, errors=errors, done=True
        )

    return render_template('import_csv.html', done=False)


# ─────────────────────────────────────────────
# GLOBAL SEARCH API
# ─────────────────────────────────────────────
@dashboard.route('/api/search')
@login_required
def api_search():
    q = request.args.get('q', '').strip().lower()
    if len(q) < 2:
        return jsonify([])

    clients = Client.query.filter_by(
        user_id=session['user_id'], archived=False
    ).all()

    results = []
    for c in clients:
        if (q in c.name.lower() or
                q in c.email.lower() or
                q in (c.company or '').lower() or
                q in (c.phone or '').lower()):
            results.append({
                'id': c.id,
                'name': c.name,
                'email': c.email,
                'company': c.company or '',
                'status': c.status,
                'initials': (c.name[0] + (c.name.split()[-1][0] if len(c.name.split()) > 1 else '')).upper(),
                'url': f'/client/{c.id}'
            })
        if len(results) >= 8:
            break

    return jsonify(results)


# ─────────────────────────────────────────────
# PROFILE
# ─────────────────────────────────────────────
@dashboard.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get_or_404(session['user_id'])

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'change_username':
            new_username = request.form.get('new_username', '').strip()
            if len(new_username) < 3:
                flash('El usuario debe tener al menos 3 caracteres')
                return redirect('/profile')
            existing = User.query.filter_by(username=new_username).first()
            if existing and existing.id != user.id:
                flash('Ese nombre de usuario ya está en uso')
                return redirect('/profile')
            user.username = new_username
            session['username'] = new_username
            db.session.commit()
            flash('¡Nombre de usuario actualizado! ✨')

        elif action == 'change_password':
            current_pw = request.form.get('current_password', '')
            new_pw = request.form.get('new_password', '')
            confirm_pw = request.form.get('confirm_password', '')

            if not check_password_hash(user.password, current_pw):
                flash('La contraseña actual es incorrecta')
                return redirect('/profile')
            if len(new_pw) < 6:
                flash('La nueva contraseña debe tener al menos 6 caracteres')
                return redirect('/profile')
            if new_pw != confirm_pw:
                flash('Las contraseñas no coinciden')
                return redirect('/profile')

            user.password = generate_password_hash(new_pw)
            db.session.commit()
            flash('¡Contraseña actualizada correctamente! 🔒')

        return redirect('/profile')

    total_clients = Client.query.filter_by(user_id=user.id, archived=False).count()
    active_clients = Client.query.filter_by(user_id=user.id, status='active', archived=False).count()

    return render_template(
        'profile.html',
        user=user,
        total_clients=total_clients,
        active_clients=active_clients
    )