import os
import random

from flask import Flask, jsonify, request, Blueprint
from flask_restx import Api, Resource, fields
from flask_cors import CORS

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from dotenv import load_dotenv
load_dotenv()

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
########################################################################################################################################################################################################################    
# Utis 함수

from utils.jwt import decode_token
from utils.user import user_certifications_classification_by_essential, calculate_user_score_by_essential, check_user_apply_able, user_certifications_classification_by_additional, calculate_user_score_by_additional
from utils.rate import transfer_score_to_rate_company_info_list, transfer_score_to_rate_company_extra_info_list
from utils.simplify import simplify_certifications_to_list_names
from utils.mysql.user import get_user_certifications_mysql, get_user_applied_company_mysql, get_user_prfreference_mysql
from utils.date import add_d_day_to_companies,format_date_to_yyyy_mm_dd
from utils.company import make_company_title

from data.insert_to_mongodb import insert_more_data
########################################################################################################################################################################################################################    
# MySQL 연결

from utils.mysql.connection import get_db_connection, get_cursor
########################################################################################################################################################################################################################    
# MongoDB 연결

MONGODB_URI = os.environ.get('MONGODB_URI')
MONGODB_DB = os.environ.get('MONGODB_DB')

# MongoDB Collections
COLLECTION_CMI = os.environ.get('COLLECTION_CMI')
COLLECTION_CERT = os.environ.get('COLLECTION_CERT')
COLLECTION_EXTRA_CMI = os.environ.get('COLLECTION_EXTRA_CMI')
COLLECTION_USER = os.environ.get('COLLECTION_USER')
COLLECTION_JOB = os.environ.get('COLLECTION_JOB')

client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
db = client[MONGODB_DB]
########################################################################################################################################################################################################################    
# FLASK 설정

FLASK_PORT = os.environ.get('FLASK_PORT')

app = Flask(__name__)
CORS(app, resources={r'*': {'origins': '*'}})

blueprint = Blueprint('api', __name__, url_prefix='/flask')

# Swagger의 Authorization 설정
authorizations = {
    'BearerAuth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

# API 인스턴스 생성
api = Api(
    blueprint,
    version='1.00',
    title='Onet Flask API',
    description='다음부턴 FAST API 쓰겠습니다..',
    authorizations=authorizations,
    security='BearerAuth',
    doc='/docs'
)

app.register_blueprint(blueprint)
########################################################################################################################################################################################################################    
# 네임스페이스 설정  

user = api.namespace('user', description = '유저 정보 API')
search = api.namespace('search', description = '검색 API')
company_info = api.namespace('company/info', description = '회사 정보 API')
company_list = api.namespace('company/list', description = '회사 리스트 API')
company_apply = api.namespace('company/apply', description = '회사 지원 API') 
ping = api.namespace('ping', description = '상태 확인 API')

# 모델 정의
company_apply_page_2_get_model = api.model('회사 지원 페이지 2', {
    'userScore': fields.Float(required=True, description='유저 점수'),
    'infoNo': fields.Integer(required=True, description='회사 번호')
})

company_list_recent_page_model = api.model('최근 채용 공고 리스트 토글을 모든 토글 기본 0', {
    'page' : fields.Integer(required=True, description='페이지 번호'),
    'limit' : fields.Integer(required=True, description='페이지 당 항목 수'),
    'location' : fields.Integer(required=True, description='지역 토글 0 or 1'),
    'position' : fields.Integer(required=True, description='직군 토글 0 or 1'),
    'career' : fields.Integer(required=True, description='경력 토글 0 or 1'),
    'certification' : fields.Integer(required=True, description='자격증 토글 0 or 1'),
})

insert_company_info_model = api.model("회사 정보 삽입 회사 정보", {
    'position': fields.String(required=True, description='직군'),
    'company_name': fields.String(required=True, description='회사 이름'),
})

insert_more_data_model = api.model('회사 정보 삽입 리스트', {
    'data': fields.List(fields.Nested(insert_company_info_model), required=True, description='삽입할 회사 정보')
})
########################################################################################################################################################################################################################
# 필드 설정
ordinary = {
            '_id': 0,
            }

minimul = {
            '_id': 0,
            'infoNo': 1,
            'companyName': 1, 
            'certificationsEssential': 1,
        }

require_end_date = {
            '_id': 0,
            'infoNo': 1,
            'companyName': 1, 
            'certificationsEssential': 1,
            'hiringPeriodEndDate': 1,
        }

require_company_title = {
            '_id': 0,
            'infoNo': 1,
            'position': 1,
            'companyName': 1,
            'experienceLevel': 1,
            'hiringPeriodEndDate': 1,
            'certificationsEssential': 1,
            'employmentType': 1,
        }
########################################################################################################################################################################################################################
@ping.route('/')
class Ping(Resource):
    @ping.doc('Ping - Pong')
    def get(self):
        return {
            "status": "success",
        }

########################################################################################################################################################################################################################    
@ping.route('/mongo')
class PingMongo(Resource):
    @ping.doc('Ping - MongoDB')
    def get(self):
        return {
            "status": "success",
            "message": db.command("ping")
        }
########################################################################################################################################################################################################################    
@company_list.route('/recent/page/main')
class RecentCompanyListMain(Resource):
    @company_list.header('Authorization', 'JWT 토큰', required = False)
    @company_list.doc(description='JWT 토큰 있으면, 최근 채용 공고에서 요구하는 필수 자격증과 회원이 보유한 자격증 비교.\n 없으면 최근 채용 공고 리스트 반환.')
    
    @company_list.response(402, 'Invalid Token')
    @company_list.response(401, 'Expired Token')
    @company_list.response(500, 'DB Connection Error')

    def get(self) -> str:
        '''최근 채용 공고 기업 메인페이지용'''
        collection = db[COLLECTION_CMI]

        company_list = collection.find({}, minimul).sort("hiringPeriodStartDate", -1).limit(6)
        company_list = list(company_list)

        company_list = simplify_certifications_to_list_names(company_list)

        auth_header = request.headers.get('Authorization')

        # 토큰이 있는 경우
        if auth_header and auth_header.startswith("Bearer "):
            user_id = decode_token(auth_header)

            if user_id == 402:
                return {
                    "status": "fail",
                    "message": "Invalid Token"
                }, 402
            elif user_id == 401:
                return {
                    "status": "fail",
                    "message": "Expired Token"
                }, 401
            else:
                user_certification = get_user_certifications_mysql(user_id)

                if user_certification == 500:
                    return {
                        "status": "fail",
                        "message": "DB Connection Error"
                    }, 500

                # 회사에서 요구하는 자격증 중 회원이 가지고 있는 자격증과 비교하여 분류
                company_list = user_certifications_classification_by_essential(company_list, user_certification)

        return {
            "description": "최근 채용공고 리스트",
            "company_list": company_list
        }, 200

########################################################################################################################################################################################################################
@company_list.route('/certification/page/main')
class SearchCertification(Resource):
    @company_list.header('Authorization', 'JWT 토큰', required=False)
    @company_list.doc(description='JWT 토큰 있으면, 회원이 가지고 있는 자격증을 기반으로 회사 리스트를 반환.\n 없으면 랜덤 자격증을 기반으로 회사 리스트를 반환.')

    @company_list.response(402, 'Invalid Token')
    @company_list.response(401, 'Expired Token')
    @company_list.response(500, 'DB Connection Error')

    def get(self) -> str:
        """@@ 자격증으로 가능한 기업 메인페이지용"""
        
        def no_user_certification():
            collection = db[COLLECTION_CERT]
            certification_list = collection.find({"category": "IT개발·데이터"}, {'_id': 0, 'certifications': 1})
            certification_list = list(certification_list)

            random_certification = random.choice(certification_list)
            random_certification = random.choice(random_certification['certifications'])

            query = {
                'certificationsEssential.name': {'$in': [random_certification]}
            }

            description = "랜덤 필수 자격증 기반 회사 리스트"

            return query, random_certification, description
        
        # 기본 초기화
        query = None
        random_certification = None
        description = None

        auth_header = request.headers.get('Authorization')

        # 로그인 상태가 아니거나 토큰이 없는 경우
        if not auth_header or not auth_header.startswith("Bearer "):
            query, random_certification, description = no_user_certification()
        else:
            user_id = decode_token(auth_header)

            if user_id == 402:
                return {
                    "status": "fail",
                    "message": "Token has expired"
                }, 402
            elif user_id == 401:
                return {
                    "status": "fail",
                    "message": "Invalid token"
                }, 401
            
            else:  # 유저 ID가 정상적으로 반환된 경우 MySQL에서 유저의 자격증 리스트를 가져옴
                user_certification = get_user_certifications_mysql(user_id)
  
                if user_certification == 500:
                    return {
                        "status": "fail",
                        "message": "DB Connection Error"
                    }, 500
                elif not user_certification:
                    query, random_certification, description = no_user_certification()
                else:
                    user_random_certification = random.choice(user_certification)

                    query = {
                        'certificationsEssential.name': {'$in': [user_random_certification]}
                    }

                    description = "유저 보유 자격증 기반 회사 리스트"

        # DB에서 회사 리스트 가져오기
        collection = db[COLLECTION_CMI]
        company_list = collection.find(query, {'_id': 0, 'infoNo': 1, 'companyName': 1, 'hiringPeriodEndDate': 1, "companyImageURL": 1}).limit(10)
        company_list = list(company_list)

        company_list = add_d_day_to_companies(company_list)

        company_list = {
            "description": description,
            "search_certification": random_certification if not auth_header or not user_certification else user_random_certification,
            'company_list': company_list
        }

        return company_list, 200

########################################################################################################################################################################################################################    
@company_list.route('/try/page/<string:page>')
class TryCompanyList(Resource):
    @company_list.header('Authorization', 'JWT 토큰', required = False)
    @company_list.param('page', '페이지 유형 main / try', 'query')
    @company_list.doc(description='JWT가 없으면 401 반환. 유저의 자격증 적합도에 따른 회사 리스트 반환.\n page 가 main 이면 2개, try 이면 4개 반환.')
    
    @company_list.response(400, 'Unauthorized')
    @company_list.response(402, 'Invalid Token')
    @company_list.response(401, 'Expired Token')
    @company_list.response(404, 'Invalid Page')
    @company_list.response(500, 'DB Connection Error')
    @company_list.response(204, 'No User Certification')

    def get(self, page) -> str:
        """유저의 자격증 적합도에 따른 회사 리스트 1Try / 2Try / 3Try"""
        def main_dish(shown_feild):
            collection = db[COLLECTION_CMI]
            company_list = collection.find({}, shown_feild)
            company_list = list(company_list)

            company_list = simplify_certifications_to_list_names(company_list)
            company_list = add_d_day_to_companies(company_list)

            company_extra_list = db[COLLECTION_EXTRA_CMI]
            company_extra_list = list(company_extra_list.find({}, {'_id': 0,'infoNo': 1, 'applyCount': 1}))

            for company in company_list:
                for company_extra in company_extra_list:
                    if company['infoNo'] == company_extra['infoNo']:
                        company['applyCount'] = company_extra['applyCount']
                        break
                
            return company_list

        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith("Bearer "):
            # 토큰 없을 경우 애초에 표시 안함
            return {
                "status": "fail",
                "message": "Unauthorized"
            }, 400

        user_id = decode_token(auth_header)

        if user_id == 402:
            return {
                "status": "fail",
                "message": "Invalid Token"
            }, 402
        elif user_id == 401:
            return {
                "status": "fail",
                "message": "Expired Token"
            }, 401
        
        if page == 'main':
            output_count = 8
            company_list = main_dish(require_end_date)
        elif page == 'try':
            output_count = 12
            company_list = main_dish(require_company_title)
            company_list = make_company_title(company_list)
        else:
            return {
                "status": "fail",
                "message": "Invalid Page"
            }, 404

        user_certification = get_user_certifications_mysql(user_id)

        if not user_certification:
            return {
                "status": "fail",
                "message": "No User Certification"
            }, 204
        elif len(user_certification) < 3:
            return {
                "status": "fail",
                "message": "User Certification is less than 3"
            }, 204
        elif user_certification == 500:
            return {
                "status": "fail",
                "message": "DB Connection Error"
            }, 500

        # 회사에서 요구하는 자격증 중 회원이 가지고 있는 자격증과 비교하여 분류 - have, havent
        company_list = user_certifications_classification_by_essential(company_list, user_certification)

        one_try = []
        two_try = []
        three_try = []
        
        for company in company_list:
            cert_len = len(company["certificationsEssentialUserHavent"])
            if cert_len == 0:
                one_try.append(company)
            elif cert_len == 1:
                two_try.append(company)
            else:
                three_try.append(company)

            del company["certificationsEssential"]

        return {
            "description": "유저의 자격증 적합도에 따른 회사 리스트",
            'one_try': random.sample(one_try, min(len(one_try), output_count)),
            'two_try': random.sample(two_try, min(len(two_try), output_count)),
            'three_try': random.sample(three_try, min(len(three_try), output_count)),
        }, 200

########################################################################################################################################################################################################################
@search.route('/')
class Search(Resource):
    @search.param('page', '페이지 번호', 'query', type=int, required=True)
    @search.param('limit', '페이지 당 항목 수', 'query', type=int, required=False, default=12)
    @search.param('search', '검색', 'query', type=str, required=True)
    @search.header('Authorization', 'JWT 토큰', required = False)
    @search.doc(description='검색어를 바탕으로 페이지네이션을 사용하여 회사 리스트를 반환합니다.')

    def get(self) -> str:
        '''통합 검색'''
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=12, type=int)
        search = request.args.get('search', type=str)
        skip = (page - 1) * limit

        search_fields = ["companyName", "position", "companyLocationRegion", "companyLocationSubregion", "employmentType", "certificationsEssential.name", "experienceLevel"]

        # $or 연산자를 사용하여 각 필드에 대해 $regex 조건을 설정
        query = {
            "$or": [{field: {"$regex": search, "$options": "i"}} for field in search_fields]
        }

        collection = db[COLLECTION_CMI]
        company_list = collection.find(query, require_company_title).skip(skip).limit(limit)
        company_list = list(company_list)

        total_pages = len(company_list) // limit + 1

        company_list = simplify_certifications_to_list_names(company_list)
        company_list = add_d_day_to_companies(company_list)
        # company_list = make_company_title(company_list)

        auth_header = request.headers.get('Authorization')
    
        if auth_header and auth_header.startswith("Bearer "):
            user_id = decode_token(auth_header)

            if user_id == 402:
                return {
                    "status": "fail",
                    "message": "Token has expired"
                }, 402
            elif user_id == 401:
                return {
                    "status": "fail",
                    "message": "Invalid token"
                }, 401
            
            else: # 유저 ID 가 정상적으로 반환된 경우 MySQL에서 유저의 자격증 리스트를 가져옴
                user_certification = get_user_certifications_mysql(user_id)

                if user_certification == 500:
                    return {
                        "status": "fail",
                        "message": "DB Connection Error"
                    }, 500
                
                company_list = user_certifications_classification_by_essential(company_list, user_certification)

        return {
            "description": f"{search} 검색 {page} 페이지",
            "company_list": company_list,
            "total_pages": total_pages,
        }, 200
########################################################################################################################################################################################################################
@company_list.route('/hot')
class hotCompanyList(Resource):
    @company_list.doc(description='회사 지원 수와 조회수를 더하여 뜨고 있는 기업을 반환')
    @company_list.header('Authorization', 'JWT 토큰', required = False)

    @search.response(401, 'Expired Token')
    @search.response(402, 'Invalid Token')
    @search.response(500, 'DB Connection Error')

    def get(self) -> str:
        '''뜨고 있는 기업'''

        collection = db[COLLECTION_EXTRA_CMI]
        company_list = collection.find({}, {'_id': 0}).sort("viewCount", -1)
        company_list = list(company_list)

        for company in company_list:
            company["hotRate"] = int(company['applyCount']) + int(company['viewCount'])

        # company_list를 hotRate 필드의 값이 가장 큰 순으로 내림차순 정렬
        company_list = sorted(company_list, key=lambda x: x.get('hotRate', 0), reverse=True)

        # 상위 6개의 company["infoNo"]를 발췌
        top_6_infoNos = [company['infoNo'] for company in company_list[:6]]

        # COLLECTION_CMI 테이블에서 해당 infoNo에 대한 정보 가져오기
        collection = db[COLLECTION_CMI]
        company_list = collection.find({'infoNo': {'$in': top_6_infoNos}},require_end_date)
        company_list = list(company_list)

        company_list = simplify_certifications_to_list_names(company_list)
        company_list = add_d_day_to_companies(company_list)

        auth_header = request.headers.get('Authorization')
    
        if auth_header and auth_header.startswith("Bearer "):
            user_id = decode_token(auth_header)

            if user_id == 402:
                return {
                    "status": "fail",
                    "message": "Token has expired"
                }, 402
            elif user_id == 401:
                return {
                    "status": "fail",
                    "message": "Invalid token"
                }, 401
            
            else: # 유저 ID 가 정상적으로 반환된 경우 MySQL에서 유저의 자격증 리스트를 가져옴
                user_certification = get_user_certifications_mysql(user_id)

                if user_certification == 500:
                    return {
                        "status": "fail",
                        "message": "DB Connection Error"
                    }, 500
                
                company_list = user_certifications_classification_by_essential(company_list, user_certification)

        return {
            "description": "뜨고 있는 기업",
            "company_list": company_list
        }, 200
    
########################################################################################################################################################################################################################
@search.route('/certification/essential')
class SearchCertification(Resource):
    @search.header('Authorization', 'JWT 토큰', required = False)
    @search.doc(description='JWT 토큰 있으면, 검색한 자격증에 회원이 보유한 자격증을 대조하여 반환.\n 없으면 기업이 요구하는 필수 자격증만 반환')
    @search.param('certification', '검색할 자격증 이름', 'query', required = True)

    @search.response(400, 'Invalid certification')
    @search.response(401, 'Expired Token')
    @search.response(402, 'Invalid Token')
    @search.response(500, 'DB Connection Error')

    def get(self) -> str:
        """@@ 자격증으로 가능한 기업 검색용"""    

        certification = request.args.get('certification')

        if certification is None:
            return {
                "status": "fail",
                "message": "Invalid certification"
            }, 400
        
        
        collection = db[COLLECTION_CMI]
        
        query = {
            'certificationsEssential.name': {'$in': [certification]}
        }

        company_list = collection.find(query, require_company_title)
        company_list = list(company_list)

        company_list = simplify_certifications_to_list_names(company_list)
        company_list = add_d_day_to_companies(company_list)
        company_list = make_company_title(company_list)

        auth_header = request.headers.get('Authorization')
    
        if auth_header and auth_header.startswith("Bearer "):
            user_id = decode_token(auth_header)

            if user_id == 402:
                return {
                    "status": "fail",
                    "message": "Token has expired"
                }, 402
            elif user_id == 401:
                return {
                    "status": "fail",
                    "message": "Invalid token"
                }, 401
            
            else: # 유저 ID 가 정상적으로 반환된 경우 MySQL에서 유저의 자격증 리스트를 가져옴
                user_certification = get_user_certifications_mysql(user_id)

                if user_certification == 500:
                    return {
                        "status": "fail",
                        "message": "DB Connection Error"
                    }, 500
                
                company_list = user_certifications_classification_by_essential(company_list, user_certification)

        return {
            "description": f"{certification} 자격증을 요구하는 회사 리스트",
            'company_list': company_list
        }, 200

########################################################################################################################################################################################################################
@company_apply.route('/page/1')
class ApplyPageOne(Resource):
    @company_apply.header('Authorization', 'JWT 토큰', required=False)
    @company_apply.param('infoNo', '회사 번호', required=True, type=int)

    def get(self) -> str:
        """회사 지원 페이지 1"""

        infoNo = int(request.args.get('infoNo'))

        if not infoNo:
            return {
                "status": "fail",
                "message": "Missing required parameter: infoNo"
            }, 400

        # 조회수 증가
        collection = db[COLLECTION_EXTRA_CMI]
        result = collection.update_one(
            {'infoNo': infoNo},
            {'$inc': {'viewCount': 1}}
        )
        if result.matched_count == 0:
            return {
                "status": "fail",
                "message": f"No extra info found for company with infoNo: {infoNo}"
            }, 404

        # 토큰 확인
        auth_header = request.headers.get('Authorization')
    
        if auth_header and auth_header.startswith("Bearer "):
            user_id = decode_token(auth_header)

            if user_id == 402:
                return {
                    "status": "fail",
                    "message": "Token has expired"
                }, 402
            elif user_id == 401:
                return {
                    "status": "fail",
                    "message": "Invalid token"
                }, 401
            
            # 유저의 데이터가 DB에 있는지 확인하고, 없다면 추가
            collection = db[COLLECTION_USER]
            find_user = collection.find_one({'userID': user_id}, {})
            if not find_user:

                data = {
                    'userID': user_id,
                    'recentlyViewed': [infoNo]
                }

                collection.insert_one(data)
            else:
                # 유저가 최근 본 기업에 추가
                collection.update_one(
                    {'userID': user_id},
                    {'$push': {'recentlyViewed': infoNo}}
                )

            # 유저 ID가 정상적으로 반환된 경우 MySQL에서 유저의 자격증 리스트를 가져옴
            user_certification = get_user_certifications_mysql(user_id)

            # 유저 자격증 리스트가 없을 경우 빈 리스트로 처리
            if not user_certification:
                user_certification = []

            elif user_certification == 500:
                return {
                    "status": "fail",
                    "message": "DB Connection Error"
                }, 500
            
            # 회사 기본 정보 조회
            collection = db[COLLECTION_CMI]
            company_list = list(collection.find({}, {'_id': 0}))

            # 회사 추가 정보 조회
            collection = db[COLLECTION_EXTRA_CMI]
            company_extra_list = list(collection.find({}, {'_id': 0}))

            # D-day와 제목 관련 데이터 처리
            company_list = add_d_day_to_companies(company_list)
            company_list = make_company_title(company_list, 0)

            # 회사 추가 정보에 지원 평균 점수를 레이트로 변환
            company_extra_list = transfer_score_to_rate_company_extra_info_list(company_extra_list)

            # 자격증 기반 유저 점수 계산
            company_list = calculate_user_score_by_essential(company_list, user_certification)
            # 유저 점수로 레이팅 부여
            company_list = transfer_score_to_rate_company_info_list(company_list)
            # 회사 필수 자격증 리스트화
            company_list = simplify_certifications_to_list_names(company_list)
            # 유저가 가진 자격증과 회사가 요구하는 자격증 비교
            company_list = user_certifications_classification_by_essential(company_list, user_certification)
            # 지원 가능 여부 확인
            company_list = check_user_apply_able(company_list)
            # 파라미터로 받은 infoNo에 대한 회사 정보만 추출
            company_info = [company for company in company_list if company['infoNo'] == infoNo][0]

            company_extra_info = [company for company in company_extra_list if company['infoNo'] == infoNo][0]

            # 조건문에 필요한 변수
            company_certifications = company_info['certificationsEssential']
            user_score = company_info['userScore']
            user_rate = company_info['userRate']

            print(company_certifications, user_rate, user_score)

            # company_extra_info에서의 applyAverageRate와 같은 등급을 가진 회사 리스트 추출
            same_rate_company_list = []

            for company in company_list:
                if company['userApplyAble'] == 1 and company['infoNo'] != infoNo:
                    for company_extra in company_extra_list:
                        if company_extra['infoNo'] == company['infoNo'] and company_extra_info['applyAverageRate'] == company_extra['applyAverageRate']:
                            data = {
                                "infoNo": company['infoNo'],
                                "companyName": company['companyName'],
                                "hiringPeriodEndDate": company['hiringPeriodEndDate'],
                                "userRate": company['userRate'],
                                "applyCount": company_extra['applyCount'],
                            }

                            same_rate_company_list.append(data)
                            break
                        elif not user_certification and company_extra['infoNo'] == company['infoNo'] and company_extra_info['applyAverageRate'] == company_extra['applyAverageRate']:
                            data = {
                                "infoNo": company['infoNo'],
                                "companyName": company['companyName'],
                                "hiringPeriodEndDate": company['hiringPeriodEndDate'],
                                "userRate": company['userRate'],
                                "applyCount": company_extra['applyCount'],
                            }

                            same_rate_company_list.append(data)
                            break

                if len(same_rate_company_list) == 2:
                    break        

            # company_extra_info에서의 applyAverageRate와 보다 높은 등급을 가진 회사 리스트 추출
            upper_rate_company_list = []

            for company in company_list:
                # 지원이 가능해야하고, infoNo가 같지 않아야하며, userRate가 높고, 필수 자격증에 교집합이 있어야함.
                if company['userApplyAble'] == 1 and company['infoNo'] != infoNo and company['userRate'] != user_rate and company['userScore'] > user_score and list(set(company_certifications) & set(company['certificationsEssential'])):
                        for company_extra in company_extra_list:
                            if company_extra['infoNo'] == company['infoNo']:
                                data = {
                                    "infoNo": company['infoNo'],
                                    "companyName": company['companyName'],
                                    "hiringPeriodEndDate": company['hiringPeriodEndDate'],
                                    "userRate": company['userRate'],
                                    "applyCount": company_extra['applyCount'],
                                }

                            upper_rate_company_list.append(data)
                            break

                if len(upper_rate_company_list) == 2:
                    break      

            if not upper_rate_company_list:
                upper_rate_company_list = None

            return {
                "description": f"{infoNo} 회사 정보 및 같은 등급 기업 리스트, 높은 등급 기업 리스트",
                "company_info": company_info,
                "company_extra_info": company_extra_info,
                "sameRateCompany": same_rate_company_list,
                "upperRateCompany": upper_rate_company_list
            }, 200

        else:  # 토큰이 없는 경우
            collection = db[COLLECTION_CMI]
            company_info = list(collection.find({'infoNo': infoNo}, {'_id': 0}))

            collection = db[COLLECTION_EXTRA_CMI]
            company_extra_list = list(collection.find({}, {'_id': 0}))

            company_info = simplify_certifications_to_list_names(company_info)

            company_info = add_d_day_to_companies(company_info)

            company_extra_list = transfer_score_to_rate_company_extra_info_list(company_extra_list)

            company_extra_info = [company for company in company_extra_list if company['infoNo'] == infoNo][0]

            # company_extra_info에서의 applyAverageRate와 같은 등급을 가진 회사 리스트 추출
            same_rate_company_list = []

            for company_extra in company_extra_list:
                if company_extra['applyAverageRate'] == company_extra_info['applyAverageRate']:
                    infoNo_ex = company_extra['infoNo']

                    collection = db[COLLECTION_CMI]
                    company = list(collection.find({'infoNo': infoNo_ex}, {'_id': 0, 'companyName': 1, 'hiringPeriodEndDate': 1}))
                    company = add_d_day_to_companies(company)
                    company = company[0]

                    # print(type(company['hiringPeriodEndDate'])) 

                    if company:  # 데이터 검증 후 추가
                        data = {
                            "infoNo": infoNo_ex,
                            "companyName": company['companyName'],
                            "hiringPeriodEndDate": company['hiringPeriodEndDate'],
                            "applyAverageRate": company_extra['applyAverageRate'],
                            "applyCount": company_extra['applyCount'],
                        }

                        same_rate_company_list.append(data)
                
                if len(same_rate_company_list) == 2:
                    break

            return {
                "description": f"{infoNo} 회사 정보 및 같은 등급 기업 리스트, 높은 등급 기업 리스트",
                "company_info": company_info,
                "company_extra_info": company_extra_info,
                "sameRateCompany": same_rate_company_list,
                "upperRateCompany": None
            }, 200

########################################################################################################################################################################################################################
@company_apply.route('/page/2')
class ApplyPageTwo(Resource):
    @company_apply.header('Authorization', 'JWT 토큰', required=False)
    @company_apply.expect(company_apply_page_2_get_model)

    def get(self) -> str:
        """회사 지원 페이지 2"""
        # 토큰 확인
        auth_header = request.headers.get('Authorization')
    
        if auth_header and auth_header.startswith("Bearer "):
            user_id = decode_token(auth_header)

            if user_id == 402:
                return {
                    "status": "fail",
                    "message": "Token has expired"
                }, 402
            elif user_id == 401:
                return {
                    "status": "fail",
                    "message": "Invalid token"
                }, 401
            
            data = request.json
            user_score = data['userScore']
            infoNo = data['infoNo']
    
            if not user_score or not infoNo:
                return {
                    "status": "fail",
                    "message": "Missing required parameter: userScore or infoNo"
                }, 400
    
            # 유저 ID가 정상적으로 반환된 경우 MySQL에서 유저의 자격증 리스트를 가져옴
            user_certification = get_user_certifications_mysql(user_id)

            if user_certification == 500:
                return {
                    "status": "fail",
                    "message": "DB Connection Error"
                }, 500
            
            # 회사 기본 정보 조회
            collection = db[COLLECTION_CMI]
            company_info = list(collection.find({'infoNo': infoNo}, {'_id': 0, 'certificationsAdditional': 1,'hiringPeriodEndDate': 1, 'comapnyName': 1, 'portfolioRequired': 1, 'portfolioScore': 1}))
            if len(company_info) == 1:
                company_info = calculate_user_score_by_additional(company_info, user_certification)
                company_info = simplify_certifications_to_list_names(company_info)
                company_info = user_certifications_classification_by_additional(company_info, user_certification)
                
                company_info = company_info[0]
                company_info['userScoreWithoutPortfolio'] = user_score + company_info['userScore']  # 페이지 1에서 받은 필수 자격증 기반 점수와 추가 자격증 점수를 더하여 저장

                company_info['hiringPeriodEndDate'] = format_date_to_yyyy_mm_dd(str(company_info['hiringPeriodEndDate']))
                
                if company_info['portfolioRequired'] == 1: # 회사가 포트폴리오를 요구할 때
                    company_info['userScoreWithPortfolio'] = company_info['userScoreWithoutPortfolio'] + company_info['portfolioScore'] * 1.02
                else:
                    company_info['userScoreWithPortfolio'] = company_info['userScoreWithoutPortfolio']

                del company_info['userScore']
                del company_info['portfolioRequired']
                del company_info['portfolioScore']

                company_info = transfer_score_to_rate_company_info_list([company_info])
                company_info = company_info[0]

            else:
                return {
                    "status": "fail",
                    "message": "Somethings wrong"
                }, 500

            collection = db[COLLECTION_EXTRA_CMI]
            company_extra_info = list(collection.find({'infoNo': infoNo}, {'_id': 0, 'applyCount': 1, 'applyAverageScore': 1}))
            
            if len(company_extra_info) == 1:
                company_extra_info = transfer_score_to_rate_company_extra_info_list(company_extra_info)
                company_extra_info = company_extra_info[0]
            else:
                return {
                    "status": "fail",
                    "message": "Somethings wrong"
                }, 500
            
            return{
                "description": f"{infoNo} 회사 정보 및 추가 정보",
                "company_info": {**company_info, **company_extra_info},
            }, 200

########################################################################################################################################################################################################################    
@user.route('/applied/company')
class UserAppliedCompany(Resource):
    @user.header('Authorization', 'JWT 토큰', required=True)
    @user.doc(description='회원이 지원한 회사 리스트의 infoNo 와 IMG 만 반환')

    @user.response(400, 'Unauthorized')
    @user.response(401, 'Invalid Token')
    @user.response(402, 'Expired Token')
    @user.response(204, '유저가 지원한 회사가 없습니다')
    @user.response(500, 'DB Connection Error')

    def get(self) -> str:
        '''회원이 지원한 회사 리스트 반환'''
        auth_header = request.headers.get('Authorization')
    
        if not auth_header or not auth_header.startswith("Bearer "):
            # 토큰 없을 경우 애초에 표시 안함
            return {
                "status": "fail",
                "message": "Unauthorized"
            }, 400

        user_id = decode_token(auth_header)

        if user_id == 402:
            return {
                "status": "fail",
                "message": "Token has expired"
            }, 402
        elif user_id == 401:
            return {
                "status": "fail",
                "message": "Invalid token"
            }, 401

        user_applied_company = get_user_applied_company_mysql(user_id)

        if not user_applied_company:
            return {
                "description": "유저가 지원한 회사가 없습니다",
                "company_list": []
            }, 204
        elif user_applied_company == 500:
            return {
                "description": "fail",
                "message": "DB Connection Error"
            }, 500
        else: 
            collection = db[COLLECTION_CMI]
            company_list = collection.find({'infoNo': {'$in': user_applied_company}}, {'_id': 0, 'infoNo': 1, 'companyImageURL': 1})
            company_list = list(company_list)

        return {
            "description": "회원이 지원한 회사 리스트",
            "company_list": company_list
        }, 200
########################################################################################################################################################################################################################
@user.route('/viewed/company')
class UserViewedCompany(Resource):
    @user.header('Authorization', 'JWT 토큰', required=True)
    @user.doc(description='회원보유한 자격증과 회사가 요구하는 자격증을 비교하여 회사 리스트 반환')

    @user.response(400, 'Unauthorized')
    @user.response(401, 'Invalid Token')
    @user.response(402, 'Expired Token')
    @user.response(500, 'DB Connection Error')
    def get(self) -> str:
        '''최근에 본 기업공고 '''

        auth_header = request.headers.get('Authorization')
    
        if not auth_header or not auth_header.startswith("Bearer "):
            # 토큰 없을 경우 애초에 표시 안함
            return {
                "status": "fail",
                "message": "Unauthorized"
            }, 400

        user_id = decode_token(auth_header)

        if user_id == 402:
            return {
                "status": "fail",
                "message": "Token has expired"
            }, 402
        elif user_id == 401:
            return {
                "status": "fail",
                "message": "Invalid token"
            }, 401
        
        # 유저의 데이터가 DB에 있는지 확인하고, 없다면 추가
        collection = db[COLLECTION_USER]
        find_user = collection.find_one({'userID': user_id}, {})
        if not find_user:

            data = {
                'userID': user_id,
                'recentlyViewed': []
            }

            collection.insert_one(data)

        user_recently_viewed = collection.find_one({'userID': user_id}, {'recentlyViewed': 1, '_id': 0})
        user_recently_viewed = user_recently_viewed['recentlyViewed']

        collection = db[COLLECTION_CMI]
        company_list = collection.find({'infoNo': {'$in': user_recently_viewed}}, require_end_date)
        company_list = list(company_list)

        company_list = simplify_certifications_to_list_names(company_list)
        company_list = add_d_day_to_companies(company_list)
        
        user_certification = get_user_certifications_mysql(user_id)

        if user_certification == 500:
            return {
                "status": "fail",
                "message": "DB Connection Error"
            }, 500

        company_list = user_certifications_classification_by_essential(company_list, user_certification, 1)

        return {
            "description": "최근에 본 기업공고",
            "company_list": company_list
        }, 200

########################################################################################################################################################################################################################
@company_info.route('/insert')
class InsertCompanyInfo(Resource):
    @company_info.expect(insert_more_data_model)
    @company_info.doc(description='회사 정보 삽입 리스트형')

    def post(self) -> str:
        '''기업 데이터 삽입'''

        company_data = request.json
        company_data =  company_data['data']

        status = insert_more_data(company_data)

        if status == 500:
            return {
                "status": "fail",
                "message": "DB Connection Error"
            }, 500
        elif status == 201:
            return {
                "status": "success",
                "message": "Data Inserted"
            }, 201
########################################################################################################################################################################################################################
@company_list.route('/recent/page')
class RecentCompanyList(Resource):
    @company_list.header('Authorization', 'JWT 토큰', required = False)
    @company_list.expect(company_list_recent_page_model)
    
    def get(self) -> str:
        '''토글을 사용한 최근 채용 공고 기업'''
        # EDUCATION_LEVELS = {"고졸": "고등학교 졸업","2~3년제" : "전문대 졸업","4년제 이상": ["대학교 졸업", "석사 이상"]}

        def get_user_data(auth_header):
            user_id = decode_token(auth_header)

            if user_id == 402:
                return {
                    "status": "fail",
                    "message": "Token has expired"
                }, 402
            elif user_id == 401:
                return {
                    "status": "fail",
                    "message": "Invalid token"
                }, 401
            
            user_certification = get_user_certifications_mysql(user_id)
            user_prfreference = get_user_prfreference_mysql(user_id)

            if user_certification or user_prfreference == 500:
                return {
                    "status": "fail",
                    "message": "DB Connection Error"
                }, 500
            
            if user_prfreference == 204:
                return {
                    "status": "fail",
                    "message": "온보딩이 필요합니다."
                }, 204

            return user_certification, user_prfreference
        
        def manufacture_company_list(company_list):
            company_list = list(company_list)
            company_list = simplify_certifications_to_list_names(company_list)
            company_list = add_d_day_to_companies(company_list)
            company_list = make_company_title(company_list)

            total_pages = len(company_list) // limit + 1

            return company_list, total_pages
        
        # def get_location_filter(user_prfreference):
        #     """
        #     지역 필터 조건을 생성합니다.
        #     - sub_region 값이 없으면 region으로 검색.
        #     - sub_region 값이 있으면 sub_region만으로 검색.
        #     """
        #     if user_prfreference['sub_region']:
        #         return {"companyLocationSubregion": user_prfreference['sub_region']}
        #     return {"companyLocationRegion": user_prfreference['region']}
        
        auth_header = request.headers.get('Authorization')
        
        data = request.json

        page  = data['page']
        limit = data['limit']
        skip = (page - 1) * limit

        location_togel = data['location'] if auth_header or auth_header.startswith("Bearer ") else 0
        position_togel = data['position'] if auth_header or auth_header.startswith("Bearer ") else 0
        career_togel = data['career'] if auth_header or auth_header.startswith("Bearer ") else 0
        certification_togel = data['certification'] if auth_header or auth_header.startswith("Bearer ") else 0

        collection_cmi = db[COLLECTION_CMI]
        collection_extra_cmi = db[COLLECTION_EXTRA_CMI]
        collection_job = db[COLLECTION_JOB]
        
        # 메인 로직
        if location_togel == 0 and position_togel == 0 and career_togel == 0 and certification_togel == 0:
            # 모든 토글이 비활성화일 때 (조건 없음)
            if auth_header and auth_header.startswith("Bearer "):
                user_certification, user_prfreference = get_user_data(auth_header)
                if user_prfreference in [204, 401, 402, 500]:
                    return user_certification, user_prfreference
                
            company_list = collection_cmi.find({}, require_company_title).sort("hiringPeriodStartDate", -1).limit(limit).skip(skip)
            company_list, total_pages = manufacture_company_list(company_list)

        elif location_togel == 1 and position_togel == 0 and career_togel == 0 and certification_togel == 0:
            # 지역 토글 활성화
            if auth_header and auth_header.startswith("Bearer "):
                user_certification, user_prfreference = get_user_data(auth_header)
                if user_prfreference in [204, 401, 402, 500]:
                    return user_certification, user_prfreference

                # location_filter = get_location_filter(user_prfreference)
                company_list = collection_cmi.find({"companyLocationRegion": user_prfreference['region']}, require_company_title).sort("hiringPeriodStartDate", -1).limit(limit).skip(skip)
                company_list, total_pages = manufacture_company_list(company_list)

        elif location_togel == 1 and position_togel == 1 and career_togel == 0 and certification_togel == 0:
            # 지역 + 직무 토글 활성화
            if auth_header and auth_header.startswith("Bearer "):
                user_certification, user_prfreference = get_user_data(auth_header)
                if user_prfreference in [204, 401, 402, 500]:
                    return user_certification, user_prfreference

                # location_filter = get_location_filter(user_prfreference)
                company_list = collection_cmi.find({
                    "$and": [
                        {"position": user_prfreference['sub_industry']},
                        {"companyLocationRegion": user_prfreference['region']}
                    ]
                }, require_company_title).sort("hiringPeriodStartDate", -1).limit(limit).skip(skip)
                company_list, total_pages = manufacture_company_list(company_list)

        elif location_togel == 1 and position_togel == 1 and career_togel == 1 and certification_togel == 0:
            # 지역 + 직무 + 경력 토글 활성화
            if auth_header and auth_header.startswith("Bearer "):
                user_certification, user_prfreference = get_user_data(auth_header)
                if user_prfreference in [204, 401, 402, 500]:
                    return user_certification, user_prfreference

                # location_filter = get_location_filter(user_prfreference)
                company_list = collection_cmi.find({
                    "$and": [
                        {"position": user_prfreference['sub_industry']},
                        {"companyLocationRegion": user_prfreference['region']},
                        {"experienceRequiredYears": {"$in": user_prfreference['career']}}
                    ]
                }, require_company_title).sort("hiringPeriodStartDate", -1).limit(limit).skip(skip)
                company_list, total_pages = manufacture_company_list(company_list)

        elif location_togel == 1 and position_togel == 1 and career_togel == 1 and certification_togel == 1:
            # 지역 + 직무 + 경력 + 자격증 토글 활성화
            if auth_header and auth_header.startswith("Bearer "):
                user_certification, user_prfreference = get_user_data(auth_header)
                if user_prfreference in [204, 401, 402, 500]:
                    return user_certification, user_prfreference

                # location_filter = get_location_filter(user_prfreference)
                company_list = collection_cmi.find({
                    "$and": [
                        {"position": user_prfreference['sub_industry']},
                        {"companyLocationRegion": user_prfreference['region']},
                        {"experienceRequiredYears": {"$in": user_prfreference['career']}},
                        {"certificationsEssential.name": {"$in": user_certification}}
                    ]
                }, require_company_title).sort("hiringPeriodStartDate", -1).limit(limit).skip(skip)
                company_list, total_pages = manufacture_company_list(company_list)

        elif location_togel == 0 and position_togel == 1 and career_togel == 0 and certification_togel == 0:
            # 직무 토글 활성화
            if auth_header and auth_header.startswith("Bearer "):
                user_certification, user_prfreference = get_user_data(auth_header)
                if user_prfreference in [204, 401, 402, 500]:
                    return user_certification, user_prfreference

                company_list = collection_cmi.find({
                    "position": user_prfreference['sub_industry']
                }, require_company_title).sort("hiringPeriodStartDate", -1).limit(limit).skip(skip)
                company_list, total_pages = manufacture_company_list(company_list)

        elif location_togel == 0 and position_togel == 1 and career_togel == 1 and certification_togel == 0:
            # 직무 + 경력 토글 활성화
            if auth_header and auth_header.startswith("Bearer "):
                user_certification, user_prfreference = get_user_data(auth_header)
                if user_prfreference in [204, 401, 402, 500]:
                    return user_certification, user_prfreference

                company_list = collection_cmi.find({
                    "$and": [
                        {"position": user_prfreference['sub_industry']},
                        {"experienceRequiredYears": {"$in": user_prfreference['career']}}
                    ]
                }, require_company_title).sort("hiringPeriodStartDate", -1).limit(limit).skip(skip)
                company_list, total_pages = manufacture_company_list(company_list)

        elif location_togel == 0 and position_togel == 1 and career_togel == 1 and certification_togel == 1:
            # 직무 + 경력 + 자격증 토글 활성화
            if auth_header and auth_header.startswith("Bearer "):
                user_certification, user_prfreference = get_user_data(auth_header)
                if user_prfreference in [204, 401, 402, 500]:
                    return user_certification, user_prfreference

                company_list = collection_cmi.find({
                    "$and": [
                        {"position": user_prfreference['sub_industry']},
                        {"experienceRequiredYears": {"$in": user_prfreference['career']}},
                        {"certificationsEssential.name": {"$in": user_certification}}
                    ]
                }, require_company_title).sort("hiringPeriodStartDate", -1).limit(limit).skip(skip)
                company_list, total_pages = manufacture_company_list(company_list)
        
        elif location_togel == 0 and position_togel == 0 and career_togel == 1 and certification_togel == 0:
            # 직무 + 경력 + 자격증 토글 활성화
            if auth_header and auth_header.startswith("Bearer "):
                user_certification, user_prfreference = get_user_data(auth_header)
                if user_prfreference in [204, 401, 402, 500]:
                    return user_certification, user_prfreference

                company_list = collection_cmi.find({
                    "experienceRequiredYears": {"$in": user_prfreference['career']}
                }, require_company_title).sort("hiringPeriodStartDate", -1).limit(limit).skip(skip)
                company_list, total_pages = manufacture_company_list(company_list)
        
        elif location_togel == 0 and position_togel == 0 and career_togel == 1 and certification_togel == 1:
            # 직무 + 경력 + 자격증 토글 활성화
            if auth_header and auth_header.startswith("Bearer "):
                user_certification, user_prfreference = get_user_data(auth_header)
                if user_prfreference in [204, 401, 402, 500]:
                    return user_certification, user_prfreference

                company_list = collection_cmi.find({
                    "$and": [
                        {"experienceRequiredYears": {"$in": user_prfreference['career']}},
                        {"certificationsEssential.name": {"$in": user_certification}}
                    ]
                }, require_company_title).sort("hiringPeriodStartDate", -1).limit(limit).skip(skip)
                company_list, total_pages = manufacture_company_list(company_list)
        
        elif location_togel == 0 and position_togel == 0 and career_togel == 0 and certification_togel == 1:
            # 직무 + 경력 + 자격증 토글 활성화
            if auth_header and auth_header.startswith("Bearer "):
                user_certification, user_prfreference = get_user_data(auth_header)
                if user_prfreference in [204, 401, 402, 500]:
                    return user_certification, user_prfreference

                company_list = collection_cmi.find({
                    "certificationsEssential.name": {"$in": user_certification}
                }, require_company_title).sort("hiringPeriodStartDate", -1).limit(limit).skip(skip)
                company_list, total_pages = manufacture_company_list(company_list)

        if user_prfreference:
            company_list = user_certifications_classification_by_essential(company_list, user_certification, 1)

        return {
            "description": "토글을 사용한 최근 채용 공고 기업",
            "company_list": company_list,
            "total_pages": total_pages
        }, 200

########################################################################################################################################################################################################################
# App Run
if __name__ == '__main__':
    app.run(debug=True, port=FLASK_PORT, host='0.0.0.0')