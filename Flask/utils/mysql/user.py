from .connection import get_cursor, get_db_connection

def get_user_certifications_mysql(user_id):
    """
    유저가 보유한 자격증 리스트를 반환하는 함수.
    """
    cursor = get_cursor()

    sql = "SELECT certification_name FROM certification WHERE user_id = %s"

    try:
        # SQL 실행
        cursor.execute(sql, (user_id,))
        
        # fetchone으로 값이 존재하는지 확인
        if cursor.fetchone() is None:
            # 값이 없을 경우 빈 리스트 반환
            return []

        # 값이 존재하면 fetchall로 전체 데이터를 가져옴
        cursor.execute(sql, (user_id,))  # 재실행이 필요
        user_certification = cursor.fetchall()
        
    except Exception as e:
        print(e)
        return 500

    # 유저 자격증 리스트화
    user_certification = [cert[0] for cert in user_certification]

    return user_certification

def get_user_applied_company_mysql(user_id):
    """
    유저가 지원한 회사 리스트를 반환하는 함수.
    """
    cursor = get_cursor()

    sql = "SELECT company_id FROM apply WHERE user_id = %s"

    try:
        # SQL 실행
        cursor.execute(sql, (user_id,))
        
        # fetchone으로 값이 존재하는지 확인
        if cursor.fetchone() is None:
            # 값이 없을 경우 빈 리스트 반환
            return []

        # 값이 존재하면 fetchall로 전체 데이터를 가져옴
        cursor.execute(sql, (user_id,))  # 재실행이 필요
        user_applied_company = cursor.fetchall()
        
    except Exception as e:
        print(e)
        return 500

    # 유저 자격증 리스트화
    user_applied_company = [comp[0] for comp in user_applied_company]

    return user_applied_company

    