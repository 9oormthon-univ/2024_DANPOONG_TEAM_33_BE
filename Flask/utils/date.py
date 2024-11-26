from datetime import datetime

def add_d_day_to_companies(company_list):
    """
    회사 리스트에 D-day 값을 추가하고, 날짜 필드를 YYYY-MM-DD 형식으로 변환.

    Args:
        company_list (list): 회사 데이터가 포함된 리스트.

    Returns:
        list: D-day 값이 추가되고 날짜 필드가 변환된 회사 데이터 리스트.
    """

    for company in company_list:
        # MongoDB의 $date에서 실제 날짜 값 추출
        # end_date = extract_date(company.get('hiringPeriodEndDate'))
        # start_date = extract_date(company.get('hiringPeriodStartDate'))

        if 'hiringPeriodEndDate' in company:
            end_date = company.get('hiringPeriodEndDate')
            company["hiringPeriodDday"] = calculate_d_day(str(end_date))
            company['hiringPeriodEndDate'] = format_date_to_yyyy_mm_dd(str(end_date))
            
        if 'hiringPeriodStartDate' in company:
            start_date = company.get('hiringPeriodStartDate')
            company['hiringPeriodStartDate'] = format_date_to_yyyy_mm_dd(str(start_date))

    return company_list


def extract_date(date_field):
    """
    MongoDB의 $date 필드에서 datetime 문자열 추출.

    Args:
        date_field (dict or str): MongoDB의 날짜 데이터.

    Returns:
        str: ISO 8601 형식의 문자열 또는 None.
    """
    if isinstance(date_field, dict) and '$date' in date_field:
        return date_field['$date']
    return None

def calculate_d_day(date_str):
    """
    주어진 날짜 문자열을 날짜 객체로 변환하고 오늘을 기준으로 D-day 계산.
    
    Args:
        date_str (str): 날짜 문자열.

    Returns:
        int: 오늘 기준으로 몇 일 뒤인지 (양수: 미래, 음수: 과거, 0: 오늘).
    """
    date_formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d"
    ]
    
    for date_format in date_formats:
        try:
            target_date = datetime.strptime(date_str, date_format).date()
            break
        except ValueError:
            continue
    else:
        raise ValueError(f"time data '{date_str}' does not match any known format")

    today = datetime.now().date()
    d_day = (target_date - today).days
    return d_day


def format_date_to_yyyy_mm_dd(date_str):
    """
    날짜 문자열을 YYYY-MM-DD 형식으로 변환.

    Args:
        date_str (str): 날짜 문자열.

    Returns:
        str: YYYY-MM-DD 형식의 문자열 또는 None.
    """
    if not date_str:
        return None

    date_formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d"
    ]
    
    for date_format in date_formats:
        try:
            date_obj = datetime.strptime(date_str, date_format)
            return date_obj.strftime("%Y-%m-%d")
        except ValueError:
            continue

    # 변환할 수 없는 경우 None 반환
    return None
