from flask import Flask

app = Flask(__name__)


@app.route('/register')
def register():
    """ Client-Facing

    Registers a new voter
    """
    pass

@app.route('/vote')
def vote():
    """ Client-Facing

    Submits a vote for a candidate
    """
    pass

@app.route('/sync')
def sync():
    """ Internally-Facing

    Recieve new blocks from other nodes
    """
    pass


if __name__ == '__main__':
    app.run()
