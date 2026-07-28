from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from pybo.filter import format_datetime

import config

db =SQLAlchemy()
migrate = Migrate()

# 애플리케이션 팩토리 함수 정의

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # jinja_env필터에 등록
    app.jinja_env.filters['datetime'] = format_datetime

    # ORM 초기화->데이터 베이스와 관련 (준비 되어있다는 뜻)
    from.import models
    db.init_app(app)
    migrate.init_app(app,db)

    # 블루프린트 등록 -> 애플리케이션의 구조화와 재사용성 (편의성)
    from.views import main_views, question_views, answer_views, auth_views, comment_views #(7/28추가)
    app.register_blueprint(main_views.bp)
    app.register_blueprint(question_views.bp)
    app.register_blueprint(answer_views.bp)
    app.register_blueprint(auth_views.bp)
    app.register_blueprint(comment_views.bp) #(7/28추가)

    return app

