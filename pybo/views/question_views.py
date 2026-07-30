from flask import Blueprint, render_template, url_for, redirect, request, flash, g, current_app
from pybo.models import Question, Answer, User, question_voter#(추가)
from datetime import datetime
from pybo import db
from pybo.forms import QuestionForm, AnswerForm
from pybo.views.auth_views import login_required # 데코레이터 임포트 (7/27)
from sqlalchemy import func, distinct
import os # 추가(7/30)
from werkzeug.utils import secure_filename # 추가(7/30)
import uuid # 추가(7/30)

bp = Blueprint('question', __name__, url_prefix = '/question')

@bp.route('/list/')
def _list():
    # 현재 페이지 번호 가져오기 (기본값은 1)
    page = request.args.get('page', type=int, default=1)
    # 페이징 기능이 적용된 질문 데이터 조회 (페이지당 10건)
    kw = request.args.get('kw', type=str, default='') # 검색어 추가(7/29)
    so = request.args.get('so', type=str, default='recent') # # 정렬 기준(최근순)(7/29)
    

    # 기본쿼리 (7/29)
    question_list = Question.query

    # 2. 검색 (kw) 조건 처리 (7/29)
    if kw:
        search = '%%{}%%'.format(kw)
        sub_query =(db.session.query(Answer.question_id, Answer.content,User.username)
                    .join(User, Answer.user_id == User.id)
                    .subquery())

        question_list= (question_list\
                        .outerjoin(sub_query, sub_query.c.question_id == Question.id)
                        .filter(Question.subject.ilike(search)|
                                Question.content.ilike(search)|
                                sub_query.c.content.ilike(search)|
                                Question.user.has(User.username.ilike(search))|
                                sub_query.c.username.ilike(search)))

    # 3. 정렬(so) 및 그룹화 처리 
    if so == 'recommend':
            # 매핑 테이블(question_voter)을 직접 outerjoin하고, 그 안의 user_id 개수를 distinct(중복없이) 집계합니다.
            question_list = (question_list 
                .outerjoin(question_voter, Question.id == question_voter.c.question_id) \
                .group_by(Question.id) 
                .order_by(func.count(distinct(question_voter.c.user_id)).desc(), Question.create_date.desc()))

    elif so == 'popular':
        #인기순 정렬(답변수 기준)
        question_list=(question_list
                       .outerjoin(Answer, Answer.question_id == Question.id)
                       .group_by(Question.id)
                       .order_by(func.count(distinct(Answer.id)).desc(), Question.create_date.desc()))

    else: #recent(최신순)
        question_list = (question_list
                         .group_by(Question.id)
                         .order_by(Question.create_date.desc())) 
    # 4. 페이징 및 렌더링
    question_list = question_list.paginate(page=page, per_page=10)

    return render_template('question/question_list.html',
                           question_list=question_list,
                           page=page,
                           kw=kw,
                           so=so)

    #페이징 기능이 적용된 질문데이터 조회(페이지당 10건)
    # question_list = Question.query.order_by(Question.create_date.desc()).paginate(page=page, per_page=10)
    # return render_template('question/question_list.html', question_list=question_list)

@bp.route('/detail/<int:question_id>/')
def detail(question_id):
    form = AnswerForm() #상세 조회 라우터 내부에서 빈 답변 폼 생성 
    question = Question.query.get_or_404(question_id)
    return render_template('question/question_detail.html',question=question, form=form)

# 질문등록 라우트 함수 추가 
@bp.route('/create/',methods=('GET','POST'))
@login_required # 유효성 상시 체크 가동 (7/27)
def create():
    form = QuestionForm()
    if request.method == 'POST' and form.validate_on_submit():
        # 30일 추가부분 시작
        # 이부분은 테스트용 끝나고 지워도 무방 (7/30)

        print("="*50)
        print("request.files :", request.files)
        print("image.data:", form.image.data)
        print("filename:", form.image.data.filename if form.image.data else None)
        print("root_path:",current_app.root_path)
        print("="*50)

        # 폼에서 전송된 이미지 파일 (7/30)
        image_file = form.image.data
        image_path = None

        if image_file:
            # 저장경로 :오늘 날짜로 폴더 생성
            today= datetime.now().strftime('%Y%m%d')
            upload_folder = os.path.join(current_app.root_path, 'static/photo', today)
            os.makedirs(upload_folder, exist_ok=True)

            # 파일 저장
            # 사용자가 업로드한 파일명을 운영체제에서 안전하게 사용할 수 있는 형태로 변환하여, 
            # 경로 조작(Path Traversal) 등의 보안 위험을 줄여 주는 함수
            filename= secure_filename(image_file.filename)
            # 출력해서 만들어진 파일이름을 확인 합니다 
            print("filename ====>", filename)

            ext = os.path.splitext(image_file.filename)[1]
            filename = f"{uuid.uuid4()}{ext}" # 이게 추가  (이름을 난수로 바꿈)
            file_path = os.path.join(upload_folder,filename)
            image_file.save(file_path)

            # DB에 저장할 경로 (static 기준 상대경로)
            image_path = f'photo/{today}/{filename}'
            # 30일 추가부분 끝

        question = Question(subject=form.subject.data, 
                            content=form.content.data, 
                            create_date=datetime.now(), 
                            user=g.user,
                            image_path=image_path) # 이줄만 추가 
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('question._list'))  
    return render_template('question/question_form.html', form=form)
# 질문 수정 라우트 함수 추가(7/27)
@bp.route('/modify/<int:question_id>', methods =('GET', 'POST'))
@login_required
def modify(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('수정권한이 없습니다')
        return redirect(url_for('question.detail', question_id=question_id))

    if request.method == 'POST':
        form = QuestionForm()
        if form.validate_on_submit():
            form.populate_obj(question) # 폼 데이터를 question객체에 동적 복사
            # question.modify_date =datetime.now() # 수정일시 저장
            db.session.commit()
            return redirect(url_for('question.detail', question_id=question_id))
    else:
        #GET요청일 경우 기존 데이터를 폼에 채워서 렌더링
        form = QuestionForm(obj=question)
    return render_template('question/question_form.html', form=form)        

# 질문 삭제 라우트 함수 추가(7/27)
@bp.route('/delete/<int:question_id>/')
@login_required
def delete(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('삭제권한이 없습니다')
        return redirect(url_for('question.detail', question_id=question_id))
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('question._list'))

# 질문 추천 라우팅 함수 (7/28)
@bp.route('/vote/<int:question_id>/')
@login_required
def vote(question_id):
    question = Question.query.get_or_404(question_id)

    # 로그인한 사용자가 본인의 글을 추천하는것을 막음 
    if g.user == question.user:
        flash('본인이 작성한 글은 추천할수 없습니다.')
        return redirect(url_for('question.detail',question_id=question_id))

    # 중복추천 방지 로직 
    if g.user in question.voter:
        flash('이미 추천한 질문입니다')
        return redirect(url_for('question.detail', question_id=question_id))

    # 기존추천 처리 로직
    question.voter.append(g.user)
    db.session.commit()

    return redirect(url_for('question.detail', question_id=question_id))