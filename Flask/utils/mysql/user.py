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

def get_user_prfreference_mysql(user_id):
    """
    유저의 프로필 정보를 반환하는 함수.
    """
    career = {"신입": [0], "1~3년": [1, 2, 3], "4~6년": [4, 5, 6], "7년 이상": [7]}

    cursor = get_cursor()

    sql = "SELECT career,region, sub_region, sub_industry FROM user_prfreference WHERE user_id = %s"

    try:
        # SQL 실행
        cursor.execute(sql, (user_id,))
        
        # fetchone으로 값이 존재하는지 확인
        user_preference = cursor.fetchone()

        if user_preference is None:
            return 204
        
    except Exception as e:
        print(e)
        return 500
    
    user_preference_dict = {
        "career": career.get(user_preference[0], []),
        "region": user_preference[1],
        "sub_region": user_preference[2],
        'sub_industry': user_preference[3],
    }
    
    print(user_preference_dict)

    return user_preference_dict