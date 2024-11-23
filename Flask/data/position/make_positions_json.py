import json

# company.json 파일 읽기
with open('Flask/data/company/company.json', 'r', encoding='utf-8') as f:
    company_data = json.load(f)

# position 값을 추출하고 중복을 제거
positions = set()
for item in company_data:
    if 'position' in item:
        positions.add(item['position'])

# positions.json 파일에 저장
with open('Flask/data/position/json/positions.json', 'w', encoding='utf-8') as f:
    json.dump(list(positions), f, ensure_ascii=False, indent=4)

print("positions.json 파일에 position 값이 저장되었습니다.")