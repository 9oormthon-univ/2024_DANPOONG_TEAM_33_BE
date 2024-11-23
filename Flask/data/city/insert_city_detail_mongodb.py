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
COLLECTION = os.environ.get('COLLECTION_CITY')

# Create a new client and connect to the server
client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))

db = client[MONGODB_DB]  # 사용할 데이터베이스 이름
collection = db[COLLECTION]  # 사용할 컬렉션 이름

# 정의된 데이터 목록
with open('Flask/data/city/전국행정동리스트.json', 'r', encoding='utf-8') as f:
    positions = json.load(f)

for position in positions:
    collection.insert_one(position)