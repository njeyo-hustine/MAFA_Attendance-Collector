from datetime import datetime

from flask import Flask

import config
import db as database
from auth import auth_bp, admin
from public import public_bp
from admin_routes import admin_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    @app.context_processor
    def common():
        return {"me": admin(), "year": datetime.now().year}

    return app


app = create_app()
database.init_db()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=config.PORT,
        debug=config.DEBUG,
    )
