from pathlib import Path # 경로 처리를 위한 기본 라이브러리
from flask import Flask 
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app() :

    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY="sksms12qkqh34dpdy",
        SQLALCHEMY_DATABASE_URI=
        f"sqlite:///{Path(__file__).parent.parent / 'local.sqlite'}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    db.init_app(app)
    Migrate(app, db)

    from apps.crud import views as crud_views

    app.register_blueprint(crud_views.crud, url_prefix="/crud")

    return app