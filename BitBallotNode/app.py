from cryptography.exceptions import InvalidSignature
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO

from blockchain import Blockchain
from exceptions import *

app = Flask(__name__)
# app.config['CORS_HEADERS'] = 'Content-Type'
socketio = SocketIO(app, cors_allowed_origins='http://localhost')

bc = Blockchain('approved_uids.sqlite')


@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))


@app.route('/register', methods=['POST'])
def register():
    """ Client-Facing

    Registers a new voter
    """
    ui = request.form['user_id']
    pw = request.form['password']
    try:
        bc.register_user(ui, pw)
    except UserAlreadyExistsError:
        return 'UserAlreadyRegistered'
    except ValueError:
        return 'InvalidKey'
    except UserNotExistError:
        return 'UserNotExist'
    return 'Registered'


@app.route('/vote', methods=['POST'])
def vote():
    """ Client-Facing

    Submits a vote for a candidate
    """
    ui = request.form['user_id']
    pw = request.form['password']
    ch = request.form['choice']
    try:
        bc.cast_vote(ui, pw, ch)
    except InvalidSignature:
        return 'InvalidSignature'
    except UserNotRegisteredError:
        return 'UserNotRegistered'
    socketio.emit('new_vote', get_tally())
    return 'Voted'


@app.route('/get_tally', methods=['GET'])
@cross_origin()
def get_tally():
    return jsonify(bc.get_vote_tally())


@app.route('/sync', methods=['POST'])
def sync():
    """ Internally-Facing

    Recieve new blocks from other nodes
    """
    # TODO: Verify sender's key
    # TODO: Add new block to local blockchain

    new_block = request.form["new_block"]
    return new_block


@app.route('/get_blockchain', methods=['GET'])
@cross_origin()
def get_blockchain():
    return jsonify(bc.__dict__)


if __name__ == '__main__':
    socketio.run(app)
