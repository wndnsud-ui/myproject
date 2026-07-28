from datetime import datetime
from flask import Blueprint, url_for, request, redirect, render_template, g, flash
from pybo import db
from pybo.models import Question, Answer
from pybo.forms import AnswerForm 
from pybo.views.auth_views import login_required # 데코레이터 임포트 (7/27)

bp = Blueprint('answer', __name__, url_prefix='/answer')

@bp.route('/create/<int:question_id>/', methods=('POST',))
@login_required #인증 유효성 상시 체크 가동 (7/26)*함수명 바로 위에 붙일것 
def create(question_id):
    # 질문번호를 Question테이블에서 조회
    # 있으면 아래코드를 처리 없으면 404에러 
    question = Question.query.get_or_404(question_id)
    form = AnswerForm()
    if form.validate_on_submit():
        content = request.form['content']
        answer = Answer(content=content, create_date=datetime.now(),user=g.user)
        question.answer_set.append(answer)
        db.session.commit()
        return redirect(url_for('question.detail', question_id=question_id))
    return render_template('question/question_detail.html',question=question, form=form)

# 답변수정 라우트 함수 추가 (7/27)
@bp.route('/modify/<int:answer_id>/', methods=('GET','POST'))
@login_required
def modify(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    if g.user != answer.user:
        flash('수정권한이없습니다')
        return redirect(url_for('question.detail', question_id=answer.question.id ))

    if request.method == 'POST':
        form = AnswerForm()
        if form.validate_on_submit():
            form.populate_obj(answer)
            db.session.commit()
            return redirect(url_for('question.detail', question_id=answer.question.id))
    else:
        form = AnswerForm(obj=answer)
    return render_template('answer/answer_form.html', answer=answer, form=form)    

@bp.route('/delete/<int:answer_id>/')
@login_required
def delete(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    question_id = answer.question.id
    if g.user != answer.user:
        flash('삭제권한이 없습니다')
    else:
        db.session.delete(answer)
        db.session.commit()
    return redirect(url_for('question.detail', question_id=question_id))
