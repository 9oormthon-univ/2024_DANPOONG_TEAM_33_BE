def simplify_certifications_to_list_names(company_list):
    """
    주어진 데이터에서 'essential' 및 'additional' 필드를 리스트로 단순화.

    Args:
        company_list (list): 각 데이터 항목이 포함된 리스트.

    Returns:
        list: 필드가 단순화된 데이터 리스트.
    """
    for company in company_list:
        
        # 'certificationsEssential' 필드 변환
        if "certificationsEssential" in company and isinstance(company['certificationsEssential'], list):
            company['certificationsEssential'] = [cert.get("name", "") for cert in company['certificationsEssential']]
        
        # 'certificationsAdditional' 필드 변환
        if "certificationsAdditional" in company and isinstance(company['certificationsAdditional'], list):
            company['certificationsAdditional'] = [cert.get("name", "") for cert in company['certificationsAdditional']]

    return company_list