from cryptography.exceptions import InvalidSignature
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS, cross_origin

from blockchain import Blockchain
from exceptions import *

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

bc = Blockchain()


@app.route('/register', methods=['POST'])
def register():
    """ Client-Facing

    Registers a new voter
    """
    ui = request.form['user_id']
    pw = request.form['password']
    redir = request.form['redirect']
    try:
        bc.register_user(ui, pw)
    except UserAlreadyExistsError:
        return redirect(redir + "?status=UserAlreadyRegistered")
    except ValueError:
        return redirect(redir + "?status=InvalidKey")
    return redirect(redir + "?status=Registered")


@app.route('/vote', methods=['POST'])
def vote():
    """ Client-Facing

    Submits a vote for a candidate
    """
    ui = request.form['user_id']
    pw = request.form['password']
    ch = request.form['choice']
    redir = request.form['redirect']
    try:
        bc.cast_vote(ui, pw, ch)
    except InvalidSignature:
        return redirect(redir + "?status=InvalidSignature")
    except UserNotRegisteredError:
        return redirect(redir + "?status=UserNotRegistered")
    return redirect(redir + "?status=Voted")


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
    return jsonify(bc.__dict__())


if __name__ == '__main__':
    app.run(host='192.168.2.242')
