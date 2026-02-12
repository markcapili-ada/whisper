from flask_restx import Api

authorizations = {
    'auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
    }
}

api = Api(authorizations=authorizations)
