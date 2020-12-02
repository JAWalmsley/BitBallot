from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/register', methods=['POST'])
def register():
    """ Client-Facing

    Registers a new voter
    """
    user_id = request.form["user_id"]
    return user_id


@app.route('/vote', methods=['POST'])
def vote():
    """ Client-Facing

    Submits a vote for a candidate
    """
    # TODO: Verify user id 
    user_id = request.form["user_id"]
    choice = request.form["choice"]
    return jsonify([user_id, choice])


@app.route('/sync', methods=['POST'])
def sync():
    """ Internally-Facing

    Recieve new blocks from other nodes
    """
    # TODO: Verify sender's key
    # TODO: Add new block to local blockchain

    new_block = request.form["new_block"]
    return new_block


if __name__ == '__main__':
    app.run()
