import requests
import xml.etree.ElementTree as ET
import json
import time

url = 'http://openapi.q-net.or.kr/api/service/rest/InquiryListNationalQualifcationSVC/getList'
params = {'serviceKey': '서비스키'}

# 중복 확인을 위한 set과 결과를 저장할 리스트
jmfldnm_set = set()
jmfldnm_list = []

while True:
    response = requests.get(url, params=params)

    # 응답 데이터의 인코딩을 설정
    response.encoding = 'utf-8'

    # XML 데이터 파싱
    root = ET.fromstring(response.content)

    # jmfldnm 필드 추출 및 중복 확인
    for item in root.findall('.//item'):
        jmfldnm = item.find('jmfldnm').text if item.find('jmfldnm') is not None else None
        if jmfldnm and jmfldnm not in jmfldnm_set:
            jmfldnm_set.add(jmfldnm)
            jmfldnm_list.append(jmfldnm)

    # sd.json 파일에 저장
    with open('Flask/data/certification/json/certifications.json', 'w', encoding='utf-8') as f:
        json.dump(jmfldnm_list, f, ensure_ascii=False, indent=4)

    print("certifications.json 파일에 자격증 명 값이 저장되었습니다.")

    # 일정 시간 대기 (예: 30초)
    time.sleep(30)