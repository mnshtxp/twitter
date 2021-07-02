import os
from flask import Flask
from twitter.routes import main_routes, tweet_routes
from twitter.models import db, migrate


DATABASE_URI = "sqlite:///twitter.sqlite3"

# Factory pattern
def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(main_routes.main_routes)
    app.register_blueprint(tweet_routes.tweet_routes)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
