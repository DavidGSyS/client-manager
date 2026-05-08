from flask import Blueprint, jsonify

from app.models.models import Client

api = Blueprint(
    'api',
    __name__,
    url_prefix='/api'
)

# GET CLIENTS
@api.route('/clients')
def get_clients():

    clients = Client.query.all()

    data = []

    for client in clients:

        data.append({
            'id': client.id,
            'name': client.name,
            'email': client.email
        })

    return jsonify(data)