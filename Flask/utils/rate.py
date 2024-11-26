def transfer_score_to_rate_company_info_list(company_list):
    """
    info : 정보 딕셔너리
    """
    for company in company_list:

        if "userScore" in company:
            if company["userScore"] >= 100:
                company["userRate"] = "A+"
            elif company["userScore"] >= 85:
                company["userRate"] = "A"
            elif company["userScore"] >= 70:
                company["userRate"] = "A-"
            elif company["userScore"] >= 55:
                company["rauserRatete"] = "B+"
            elif company["userScore"] >= 40:
                company["userRate"] = "B"
            elif company["userScore"] >= 25:
                company["userRate"] = "B-"
            else:
                company["userRate"] = "C+"

        # userScoreWithPortfolio에 따른 레이트 계산
        if "userScoreWithPortfolio" in company:
            if company["userScoreWithPortfolio"] >= 100:
                company["userRateWithPortfolio"] = "A+"
            elif company["userScoreWithPortfolio"] >= 85:
                company["userRateWithPortfolio"] = "A"
            elif company["userScoreWithPortfolio"] >= 70:
                company["userRateWithPortfolio"] = "A-"
            elif company["userScoreWithPortfolio"] >= 55:
                company["userRateWithPortfolio"] = "B+"
            elif company["userScoreWithPortfolio"] >= 40:
                company["userRateWithPortfolio"] = "B"
            elif company["userScoreWithPortfolio"] >= 25:
                company["userRateWithPortfolio"] = "B-"
            else:
                company["userRateWithPortfolio"] = "C+"
        if "userScoreWithoutPortfolio" in company:
            if company["userScoreWithoutPortfolio"] >= 100:
                company["userRateWithoutPortfolio"] = "A+"
            elif company["userScoreWithoutPortfolio"] >= 85:
                company["userRateWithoutPortfolio"] = "A"
            elif company["userScoreWithoutPortfolio"] >= 70:
                company["userRateWithoutPortfolio"] = "A-"
            elif company["userScoreWithoutPortfolio"] >= 55:
                company["userRateWithoutPortfolio"] = "B+"
            elif company["userScoreWithoutPortfolio"] >= 40:
                company["userRateWithoutPortfolio"] = "B"
            elif company["userScoreWithoutPortfolio"] >= 25:
                company["userRateWithoutPortfolio"] = "B-"
            else:
                company["userRateWithoutPortfolio"] = "C+"

    return company_list

def transfer_score_to_rate_company_extra_info_list(company_extra_list):

    for company_extra_info in company_extra_list:

        if not company_extra_info["applyAverageScore"]:
            company_extra_info["applyAverageRate"] = "F"
            break

        if company_extra_info["applyAverageScore"] >= 100:
            company_extra_info["applyAverageRate"] = "A+"
        elif company_extra_info["applyAverageScore"] >= 85:
            company_extra_info["applyAverageRate"] = "A"
        elif company_extra_info["applyAverageScore"] >= 70:
            company_extra_info["applyAverageRate"] = "A-"
        elif company_extra_info["applyAverageScore"] >= 55:
            company_extra_info["applyAverageRate"] = "B+"
        elif company_extra_info["applyAverageScore"] >= 40:
            company_extra_info["applyAverageRate"] = "B"
        elif company_extra_info["applyAverageScore"] >= 25:
            company_extra_info["applyAverageRate"] = "B-"
        else:
            company_extra_info["applyAverageRate"] = "C+"

    return company_extra_list