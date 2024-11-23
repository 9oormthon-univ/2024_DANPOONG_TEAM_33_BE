import random
from datetime import datetime, timedelta
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
import json

load_dotenv()
MONGODB_URI = os.environ.get('MONGODB_URI')
MONGODB_DB = os.environ.get('MONGODB_DB')
COLLECTION_CMI = os.environ.get('COLLECTION_CMI')
COLLECTION_CITY = os.environ.get('COLLECTION_CITY')
COLLECTION_PS = os.environ.get('COLLECTION_JOB')
COLLECTION_CERT = os.environ.get('COLLECTION_CERT')
COLLECTION_EXTRA_CMI = os.environ.get('COLLECTION_EXTRA_CMI')
IMAGE_URL = os.environ.get('IMAGE_URL')

# 새로운 클라이언트를 생성하고 서버에 연결
client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))

db = client[MONGODB_DB]  # 사용할 데이터베이스 이름

# 전국행정동리스트.json 파일 읽기
with open('Flask/data/datasets/전국행정동리스트.json', 'r', encoding='utf-8') as f:
    location_data = json.load(f)

# 정의된 데이터 목록
with open('Flask/data/datasets/company.json', 'r', encoding='utf-8') as f:
    company_data = json.load(f)

# positions_detail.json 파일 읽기
with open('Flask/data/datasets/positions.json', 'r', encoding='utf-8') as f:
    positions_detail = json.load(f)

# certifications_detail.json 파일 읽기
with open('Flask/data/datasets/certifications.json', 'r', encoding='utf-8') as f:
    certifications_detail = json.load(f)

# 무작위 선택을 위한 학력 수준 및 고용 형태 정의
EDUCATION_LEVELS = ["고등학교 졸업", "전문대 졸업", "대학교 졸업", "석사 이상"]
EMPLOYMENT_TYPES = ["정규직", "계약직", "계약직 (정규직 전환가능)", "인턴직", "해외취업", "인턴직 (정규직 전환가능)", "전문계약직", "기간제"]

def get_random_location(data):
    # 모든 region들 중에서 하나를 랜덤으로 선택
    region_data = random.choice(data)
    region = region_data['region']
    subregion = region_data.get('subregion', [])

    if not subregion:
        # region만 있는 경우
        region = region
        subregion = []
        
    else:
        # region 안에 있는 city들 중에서 하나를 랜덤으로 선택
        subregion = random.choice(subregion)

        region = region
        subregion = subregion

    return region, subregion

def generate_job_data(company, Info_no):
    # 현재 날짜와 종료 날짜 설정
    start_date = datetime.now() - timedelta(days=random.randint(1, 4))
    end_date = datetime.now() + timedelta(days=random.randint(30, 55))

    # 모집 인원 설정
    recruitment_number = random.randint(1, 3)

    # 경험 수준 설정
    experience_level = random.choice(["경력", "신입", "신입 - 경력"])

    # 경험 연수 설정
    if experience_level == "신입":
        required_experience_years = 0
    elif experience_level == "신입 - 경력":
        required_experience_years = random.randint(0, 3)
    else:
        required_experience_years = random.randint(3, 7)

    # 회사 이미지 관련 설정
    image_list = [
        "28.jpg", "27.jpg", "26.jpg", "25.jpg", "24.jpg", "23.jpg",
        "22.jpg", "21.jpg", "20.jpg", "19.jpg", "18.jpg", "17.jpg",
        "16.jpg", "15.jpg", "14.jpg", "13.jpg", "12.jpg", "11.webp",
        "10.webp", "9.jpg", "8.jpg", "7.jpg", "6.webp", "5.webp",
        "4.webp", "3.webp", "2.webp", "1.webp"
    ]

    random_image = random.choice(image_list)

    company_image_url = f"{IMAGE_URL}{random_image}"

    # 학력 및 고용 형태 설정
    required_education = random.choice(EDUCATION_LEVELS)
    employment_type = random.choice(EMPLOYMENT_TYPES)

    # 위치 설정
    region, subregion  = get_random_location(location_data)

    # 자격증 초기화
    essential_certifications = []
    additional_certifications = []

    # 자격증 설정
    print(company)
    position_name = company["position"] 
    category = None

    for detail in positions_detail:
        if position_name in detail["position"]:
            category = detail["category"]  #  기업 데이터 직무와 일치하는 카테고리 찾기
            break

    if not category:        
        print(f"{position_name} 직군이 속한 카테고리가 없습니다.")
        return None
    else:
        for cert_detail in certifications_detail:  
            if cert_detail["category"] == category: # 직군 데이터가 속한 카테고리가 존재할 때 같은 카테고리의 자격증을 찾음
                certifications = cert_detail["certifications"]
                if certifications: # 자격증이 존재할 때
                    essential_certifications = random.sample(certifications, min(len(certifications), 3))
                    additional_certifications = random.sample(
                        [cert for cert in certifications if cert not in essential_certifications],
                        min(len(certifications) - len(essential_certifications), random.randint(3, 5))
                    )
                break

    # 프로필 요구사항 설정
    portfolio_required = random.randint(0,1)

    # 프로필 요구가 있을 시 무작위로 점수 설정, 없으면 0
    if portfolio_required == 1:
        portfolio_score = random.randint(2, 10)
    else:
        portfolio_score = 0

    # 자격증 점수 설정
    essential_certifications_with_scores = [{"name": cert, "score": random.randint(20, 40)} for cert in essential_certifications]
    additional_certifications_with_scores = [{"name": cert, "score": random.randint(5, 15)} for cert in additional_certifications]

    # 총 점수 계산
    total_score = portfolio_score + sum(cert["score"] for cert in essential_certifications_with_scores) + sum(cert["score"] for cert in additional_certifications_with_scores)

    # 총 점수가 100점이 되도록 조정
    if total_score != 100:
        difference = 100 - total_score
        if difference > 0:
            # 점수가 부족한 경우, essential_certifications에 점수 추가
            for cert in essential_certifications_with_scores:
                if difference <= 0:
                    break
                cert["score"] += 1
                difference -= 1
        else:
            # 점수가 초과한 경우, additional_certifications에서 점수 차감
            for cert in additional_certifications_with_scores:
                if difference >= 0:
                    break
                cert["score"] -= 1
                difference += 1

    # 회사 평점 설정
    company_rating = random.choice(["A+", "A", "B+", "B", "C"])

    # 급여 설정
    salary_min = random.choice(range(2400, 3501, 100))
    salary_max = random.choice(range(5100, 7001, 100))
    salary_currency = "KRW"
    salary_unit = "만"

    # 근무 일정 설정
    working_hours = "09:00 - 18:00"
    working_days = ["월", "화", "수", "목", "금"]

    # 직무 데이터 딕셔너리 생성
    job_data = {
       

    "infoNo": Info_no,
    "position": company["position"],
    "companyName": company["company_name"],
    "companyLocationRegion": region,
    "companyLocationSubregion": subregion,
    "companyImageURL": company_image_url,
    "companyRating": company_rating,
    "requiredEducation": required_education,
    "salaryMin": salary_min,
    "salaryMax": salary_max,
    "salaryCurrency": salary_currency,
    "salaryUnit": salary_unit,
    "employmentType": employment_type,
    "workingScheduleWorkingHours": working_hours,
    "workingScheduleWorkingDays": working_days,
    "hiringPeriodStartDate": start_date,
    "hiringPeriodEndDate": end_date,
    "hiringPeriodRecruitmentNumber": recruitment_number,
    "certificationsEssential": essential_certifications_with_scores,
    "certificationsAdditional": additional_certifications_with_scores,
    "portfolioRequired": portfolio_required,
    "portfolioScore": portfolio_score,
    "experienceLevel": experience_level,
    "experienceRequiredYears": required_experience_years
    }

    return job_data

def generate_job_extra_data(info_no):
    data = {
        'infoNo': info_no,
        'applyCount': random.randint(1, 100),
        'applyAverageScore': random.randint(50, 92),
        'viewCount': random.randint(1200, 2200),
    }
    
    return data

def count_db():
    collection = db[COLLECTION_CMI]
    count = int(collection.count_documents({}))

    return count
# client.drop_database(MONGODB_DB)  # 데이터베이스 초기화
# print("데이터베이스가 초기화되었습니다.")

# Info_no = 1 # 최초 데이터 삽입 시 1로 설정
with open('Flask/data/datasets/company_more.json', 'r', encoding='utf-8') as f:
        company_data = json.load(f)

def insert_more_data(company_data):
    Info_no = count_db()  
    Info_no += 1  #데이터 추가 삽입시

    collection_job = db[COLLECTION_CMI] 
    collection_job_extra = db[COLLECTION_EXTRA_CMI]
    for company in company_data:
        doc = generate_job_data(company, Info_no)
        if doc:  # doc이 None이 아닌 경우에만 삽입

            try:
                collection_job.insert_one(doc)
            
                extra_data = generate_job_extra_data(Info_no)
                collection_job_extra.insert_one(extra_data)
                Info_no += 1
            except Exception as e:
                print(f"데이터 삽입 중 오류 발생: {e}")
                return 500
            finally: return 201

    print("회사 데이터가 MongoDB에 삽입되었습니다.")

# Loc_no = 1

# # 지역 데이터 MongoDB에 삽입
# collection = db[COLLECTION_CITY]
# for location in location_data:
#     location = {
#         "loc_no": Loc_no,
#         "region": location["region"],
#         "subregion": location["subregion"],
#     }
#     collection.insert_one(location)
#     Loc_no += 1

# print("지역 데이터가 MongoDB에 삽입되었습니다.")

# # 직군 데이터 MongoDB에 삽입
# collection = db[COLLECTION_PS]
# for position in positions_detail:
#     collection.insert_one(position)

# print("직군 데이터가 MongoDB에 삽입되었습니다.")

# # 자격증 데이터 MongoDB에 삽입
# collection = db[COLLECTION_CERT]
# for certification in certifications_detail:
#     collection.insert_one(certification)

# print("자격증 데이터가 MongoDB에 삽입되었습니다.")

# with open('data/city/전국행정동리스트_test.json', 'w', encoding='utf-8') as f:
#             json.dump(location_data, f, ensure_ascii=False, indent=4)