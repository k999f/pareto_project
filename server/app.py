import json
import os


def configureApp(app):
    with open('configs/db_config.json', 'r') as db:
        db_config = json.load(db)
    app.config['db'] = db_config

    with open('configs/server_config.json', 'r') as db:
        server_config = json.load(db)
    app.config['server'] = server_config

    app.secret_key = os.urandom(16)

    return app
