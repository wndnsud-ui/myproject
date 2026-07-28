from flask import Blueprint, redirect, url_for
bp= Blueprint('main',__name__,url_prefix='/')

@bp.route('/hello')
def hello_pbo():
    return 'Hello Pybo~~~'

@bp.route('/')
def index():
    return redirect(url_for('question._list'))

