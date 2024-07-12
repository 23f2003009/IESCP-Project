from flask import Flask
from backend.models import *

app = None #global app initially set to None

def initialize_app():
    app = Flask(__name__)
    app.debug = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///IESCP.sqlite3"
    app.app_context().push()
    db.init_app(app)
    return app

app = initialize_app()
from backend.controllers import *

if __name__ == "__main__":
    app.run()