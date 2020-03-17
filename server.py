import base64
import datetime
import os

import bmemcached
from flask import Flask, request, make_response, jsonify, redirect

application = Flask(__name__)
application.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', None),
    TOKEN=os.environ.get('TOKEN', None),
    MEMCACHIER_USERNAME=os.environ.get('MEMCACHIER_USERNAME', None),
    MEMCACHIER_SERVERS=os.environ.get('MEMCACHIER_SERVERS', None),
    MEMCACHIER_PASSWORD=os.environ.get('MEMCACHIER_PASSWORD', None),
)


# Data store that holds all the statuses
class DummyDataStore:
    def __init__(self):
        self._data = {}

    def set(self, k, v):
        self._data[k] = v

    def get(self, k, default=None):
        return self._data.get(k, default)


DATA_STORE = DummyDataStore()

# Enable memcached as data store for some persistence
if all([application.config[e] for e in ['MEMCACHIER_USERNAME', 'MEMCACHIER_PASSWORD', 'MEMCACHIER_SERVERS']]):
    print("Memcached enabled. Connecting.")
    DATA_STORE = bmemcached.Client(
        application.config['MEMCACHIER_SERVERS'].split(';'),
        application.config['MEMCACHIER_USERNAME'],
        application.config['MEMCACHIER_PASSWORD']
    )

def verify_token(f):
    def _wrapper(*args, **kwargs):
        if application.config['TOKEN'] != request.args.get('token'):
            return jsonify({}), 403

        return f(*args, **kwargs)

    return _wrapper


@verify_token
def nurture(child):
    """ Writing down the timestamp we last cared for the child """
    DATA_STORE.set(child, {
        'last_cared': datetime.datetime.now()
    })
    return jsonify({}), 204


@verify_token
def status(child):
    """
    @api {GET} /api/v1/status/<child> Child Status
    @apiVersion 1.0.0
    @apiName Child Status
    @apiGroup Child

    @apiDescription     Getting the status of the child.

    @apiParam {String="pixel","json"}       [format=json]       The format in which we should respond. Pixel will be a 1x1 colored image.
    @apiParam {Number}                      [timeout=30]        The number of seconds we accept the child not being cared for.


    @apiSuccessExample Success-Response (Image):
    HTTP/1.1 200 Ok
    {
       "id": 1,
       "name": "Estate 1",
       "office": 1
       "apartment_count": 0,
       "city": "Stockholm",
       "display_image": "https://static.homeq.se/static/img/homeq/placeholder.png",
    }

    @apiSuccessExample Success-Response (Json):
    HTTP/1.1 200 Ok
    {
       "name": "process_1",
       "last_cared": "Estate 1",
       "status": "ok"
    }
    """
    child_data = DATA_STORE.get(child, None)
    format = request.args.get('format', 'json')
    timeout = int(request.args.get('timeout', 30))

    if not child_data:
        return jsonify({}), 412

    if not format in ['json', 'pixel']:
        return jsonify({}), 412

    child_ok = datetime.datetime.now() < child_data['last_cared'] + datetime.timedelta(seconds=timeout)

    if format == 'json':
        return jsonify({
            'name': child,
            'last_cared': child_data['last_cared'].isoformat(),
            'status': 'ok' if child_ok else 'critical'
        }), 200
    elif format == 'pixel':
        color = '00ff00' if child_ok else 'ff0000'
        label = f"{child}+{child_data['last_cared'].strftime('%Y-%m-%d %H:%M')}"
        return redirect(f'https://via.placeholder.com/360x120/{color}?text={label}')


application.add_url_rule('/api/v1/nurture/<child>', 'nurture', nurture, methods=['POST'])
application.add_url_rule('/api/v1/status/<child>', 'status', status, methods=['GET'])


