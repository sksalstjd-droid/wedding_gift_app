from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(100), nullable=False)
    default_side = db.Column(db.String(20), nullable=False, default="신부측")
    memo = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


class Gift(db.Model):
    __tablename__ = "gifts"

    id = db.Column(db.Integer, primary_key=True)

    # 현재는 기본 행사 1개만 사용하지만, 나중을 위해 event_id는 유지합니다.
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)

    # 실제 축의금 봉투에 적은 번호입니다.
    # DB 내부 id와 분리해서 관리합니다.
    envelope_no = db.Column(db.Integer, nullable=False)

    name = db.Column(db.String(100), nullable=False)
    side = db.Column(db.String(20), nullable=False, default="신부측")
    relation = db.Column(db.String(100), nullable=True)

    # DB에는 원 단위로 저장합니다.
    # 화면에서는 만원 단위로 입력받고 app.py에서 * 10000 처리합니다.
    amount = db.Column(db.Integer, nullable=False)

    meal_ticket_count = db.Column(db.Integer, nullable=False, default=1)
    memo = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # 실제 삭제 대신 deleted_at만 기록하는 소프트 삭제 방식입니다.
    deleted_at = db.Column(db.DateTime, nullable=True)