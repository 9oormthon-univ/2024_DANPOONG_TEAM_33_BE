def make_company_title(company_list, del_keys = 1):
    """
    회사 리스트에서 회사명만 추출하여 리스트로 반환.

    Args:
        company_list (list): 회사 데이터가 포함된 리스트.

    Returns:
        list: 회사명만 추출된 리스트.
    """

    for company in company_list:

        title = ""
        title = title + company['companyName'] + " "
        title = title + company['position'] + " "
        title = title + company['experienceLevel']

        company['title'] = title

        if del_keys == 1:
            del company['companyName']
            del company['position']
            del company['experienceLevel']

    return company_list