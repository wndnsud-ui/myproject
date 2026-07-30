from pybo import db 
from sqlalchemy import Table

# 중간테이블 정의 (7/28)
question_voter =Table(
    'question_voter', # 데이터베이스에 생성될 중간 테이블의 실제 이름
    db.metadata, # 테이블 메타데이터 정보 연결
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('question_id', db.Integer, db.ForeignKey('question.id', ondelete='CASCADE'), primary_key=True)
)
answer_voter = Table(
    'answer_voter',
    db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('answer_id', db.Integer, db.ForeignKey('answer.id', ondelete='CASCADE'),primary_key=True)
)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)
    # 이미지 저장경로 필드 추가 (7/30)
    image_path=db.Column(db.String(200), nullable=True)

    

    # 글쓴이 외래키 및 관계 설정 추가 (기존 데이터 고려 nullable=True 우선허용)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    user = db.relationship('User', backref=db.backref('question_set'))
    # 추천인 (다대다)(7/28)
    voter = db.relationship('User', # 연결할 대상 모델 (사용자)
                            secondary=question_voter, #연결 매개체로 사용할 중간 테이블
                            backref=db.backref('question_voter_set', #User객체에서 역참조할 이름 
                                               lazy='dynamic')) #역참조 시 쿼리 객체 반환(메모리 절약 및 추가 필터링/count 가능)
    


class Answer(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id', ondelete='CASCADE'))
    question = db.relationship('Question',backref=db.backref('answer_set',cascade='all, delete-orphan'))
    content = db.Column(db.Text(), nullable=False)
    create_date=db.Column(db.DateTime(),nullable=False)
    voter =db.relationship('User', secondary=answer_voter,
                           backref=db.backref('answer_voter_set',lazy='dynamic'))

   # 글쓴이 외래키 및 관계 설정 추가 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    user = db.relationship('User', backref=db.backref('answer_set'))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

# Comment 데이터 모델 정의(7/27)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', backref=db.backref('comment_set'))
    content = db.Column(db.Text(), nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)
    modify_date = db.Column(db.DateTime())
    # 질문 테이블 및 답변 테이블과의 다대일(N:1) 관계 외래키 매핑
    question_id= db.Column(db.Integer, db.ForeignKey('question.id', ondelete='CASCADE'), nullable=True)
    question = db.relationship('Question', backref=db.backref('comment_set'))
    answer_id = db.Column(db.Integer, db.ForeignKey('answer.id', ondelete='CASCADE'), nullable=True)
    answer= db.relationship('Answer', backref=db.backref('comment_set'))
