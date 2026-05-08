from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    flash,
    session
)

from app import db
from app.models.models import Client

from app.utils.decorators import (
    login_required
)

dashboard = Blueprint(
    'dashboard',
    __name__
)

# HOME
@dashboard.route('/')
@login_required
def home():

    clients = Client.query.filter_by(
        user_id=session['user_id']
    ).all()

    total = len(clients)

    active = len([
        c for c in clients
        if c.status == 'active'
    ])

    inactive = total - active

    active_pct = (
        round((active / total) * 100)
        if total > 0 else 0
    )

    new_this_week = total

    chart_labels = [
        'Lun',
        'Mar',
        'Mié',
        'Jue',
        'Vie',
        'Sáb',
        'Dom'
    ]

    chart_data = [0, 0, 0, 0, 0, 0, total]

    return render_template(
        'index.html',
        clients=clients,
        total=total,
        active_pct=active_pct,
        inactive=inactive,
        new_this_week=new_this_week,
        chart_labels=chart_labels,
        chart_data=chart_data
    )

# ADD CLIENT
@dashboard.route('/add', methods=['POST'])
@login_required
def add_client():

    new_client = Client(
        name=request.form['name'],
        email=request.form['email'],
        phone=request.form.get('phone'),
        company=request.form.get('company'),
        notes=request.form.get('notes'),
        status='active',
        user_id=session['user_id']
    )

    db.session.add(new_client)

    db.session.commit()

    flash('Cliente agregado 🚀')

    return redirect('/')

# DELETE CLIENT
@dashboard.route('/delete/<int:id>')
@login_required
def delete_client(id):

    client = Client.query.get_or_404(id)

    db.session.delete(client)

    db.session.commit()

    flash('Cliente eliminado 🗑️')

    return redirect('/')

# EDIT CLIENT
@dashboard.route(
    '/edit/<int:id>',
    methods=['GET', 'POST']
)
@login_required
def edit_client(id):

    client = Client.query.get_or_404(id)

    if request.method == 'POST':

        client.name = request.form['name']
        client.email = request.form['email']
        client.phone = request.form.get('phone')
        client.company = request.form.get('company')
        client.notes = request.form.get('notes')
        client.status = request.form.get('status')

        db.session.commit()

        flash('Cliente actualizado ✨')

        return redirect('/')

    return render_template(
        'edit.html',
        client=client
    )
    
# TOGGLE STATUS
@dashboard.route('/toggle-status/<int:id>')
@login_required
def toggle_status(id):

    client = Client.query.get_or_404(id)

    if client.status == 'active':
        client.status = 'inactive'
    else:
        client.status = 'active'

    db.session.commit()

    flash('Estado actualizado ✨')

    return redirect('/')