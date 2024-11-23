def user_certifications_classification_by_essential(company_list, user_certifications, del_esstential = 0):
    """
    company_list: 기업이 요구하는 자격증 리스트 (문자열의 리스트 형식)
    user_certifications: 유저가 보유한 자격증 리스트 (문자열의 리스트 형식)
    """

    for company in company_list:
        have = []
        havent = []

        for company_cert in company["certificationsEssential"]:
            if company_cert in user_certifications:
                have.append(company_cert)
            else:
                havent.append(company_cert)

        company["certificationsEssentialUserHave"] = have
        company["certificationsEssentialUserHavent"] = havent

        if del_esstential == 1:
            del company["certificationsEssential"]

    return company_list

def calculate_user_score_by_essential(company_list, user_certifications):
    """
    company_info: 기업 데이터
    user_certifications: 유저가 보유한 자격증 리스트 (문자열의 리스트 형식)
    """

    # 유저가 가진 자격증의 총 점수 합산을 위한 변수

    # 기업이 요구하는 필수 자격증 리스트

    # job_data의 자격증과 유저의 자격증 비교 및 점수 합산
    for company in company_list:
    
        user_score_sum = 0

        for required_cert in company["certificationsEssential"]:
            if required_cert["name"] in user_certifications:
                user_score_sum += int(required_cert["score"]) * 1.03  # 필수 자격증은 가산점 3% 적용

                # user_score_rate를 job_data에 추가
                company["userScore"] = user_score_sum

        if user_score_sum == 0:
            company["userScore"] = 0

    return company_list

def check_user_apply_able(company_list):

    for company in company_list:
        # 지원 가능 여부 확인
        if len(company["certificationsEssentialUserHavent"]) == 0:
            company["userApplyAble"] = 1
        else:
            company["userApplyAble"] = 0
    
    return company_list