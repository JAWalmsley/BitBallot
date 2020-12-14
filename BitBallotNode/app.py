import json

from cryptography.exceptions import InvalidSignature
from flask import Flask, request

from blockchain import Blockchain
from exceptions import *

app = Flask(__name__)
bc = Blockchain()


@app.route('/register', methods=['POST'])
def register():
    """ Client-Facing

    Registers a new voter
    """
    data = json.loads(request.get_data().decode(), strict=False)
    ui = data['user_id']
    pw = data['password']

    try:
        bc.register_user(ui, pw)
    except UserAlreadyExistsError:
        return 'User Already Registered', 409
    except ValueError:
        return 'Invalid Key', 406
    return 'Success', 201


@app.route('/vote', methods=['POST'])
def vote():
    """ Client-Facing

    Submits a vote for a candidate
    """
    data = json.loads(request.get_data().decode(), strict=False)

    ui = data['user_id']
    pw = data['password']
    ch = data['choice']
    try:
        bc.cast_vote(ui, pw, ch)
    except InvalidSignature:
        return 'Invalid Signature', 406
    except UserNotRegisteredError:
        return 'User Not Registered', 409
    return 'Success', 201


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
def get_blockchain():
    pass


if __name__ == '__main__':
    app.run()
