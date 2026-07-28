from flask import Blueprint, render_template, request, url_for, redirect, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from pybo import db
from pybo.forms import UserCreateForm, UserLoginForm
from pybo.models import User
import functools # 7/26 함수 불러오기

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/signup', methods=('GET', 'POST'))
# 회원등록
def signup():
    form= UserCreateForm()
    if request.method == 'POST' and form.validate_on_submit():
        user =User.query.filter_by(username=form.username.data).first()
        if not user:
            user = User(username=form.username.data,
                        password=generate_password_hash(form.password1.data),
                        email= form.email.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('main.index'))
        else:
            flash('이미 존재하는 사용자입니다.')
    return render_template('auth/signup.html', form=form)

# 로그인
@bp.route('/login/', methods=('GET','POST'))
def login():
    form=UserLoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        error = None
        user =User.query.filter_by(username=form.username.data).first()
        if not user:
            error ='존재하지 않는 사용자입니다.'
        elif not check_password_hash(user.password, form.password.data):
            error ="비밀번호가 올바르지 않습니다."
        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('main.index'))
        flash(error)
    return render_template('auth/login.html', form=form)

# 사용자 로그인 정보를 g.user변수에 저장 

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)
        # g.user = db.session.get(User, user_id) <-- 최신 권장 사항 

@bp.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('main.index'))

def login_required(view): #7/26 질문등록 로그인 안한 상태로 했을때 로그인 화면으로 불러오기
    #Flask의 라우팅, 디버깅, 문서화 등에 필요한 원래 함수의 메타데이터(이름,설명, 모듈, 정보 등)를 보존 
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(*args, **kwargs)
    return wrapped_view

