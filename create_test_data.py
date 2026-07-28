from datetime import datetime
from pybo import create_app,db
from pybo.models import Question

# 1. Flask 애플리케이션 객체 생성
app= create_app()

# 2. 애플리케이션 컨텍스트 내부에서 데이터베이스 작업 수행
with app.app_context():
    print("테스트 데이터 생성 시작...")

    # 리스트 컴프리헨션을 사용하여 300개의 Question 객체를 메모리에 먼저 생성
    questions = [
        Question(
            subject=f'테스트 데이터입니다:[{i:03d}]',
            content='내용입니다',
            create_date=datetime.now()
        )
        for i in range(300)
    ]
    # bulk_save_objects를 사용하여 300개의 데이터를 한 번에 효율적으로 추가
    db.session.bulk_save_objects(questions)

    # 최종 커밋
    db.session.commit()

    print(f"성공적으로 {len(questions)}개의 대량 데이터가 pybo에 등록되었습니다. ")
