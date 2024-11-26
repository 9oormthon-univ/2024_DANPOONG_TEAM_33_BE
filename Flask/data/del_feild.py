import json

# company.json 파일 읽기
with open('Flask/data/datasets/company.json', 'r', encoding='utf-8') as f:
    company_data = json.load(f)

# 특정 필드를 삭제
for item in company_data:
    if 'location' in item:
        del item['location']
    if 'portfolio_required' in item:
        del item['portfolio_required']
    if 'certifications' in item:
        del item['certifications']

# 수정된 데이터를 다시 JSON 파일에 저장
with open("Flask/data/datasets/company.json", "w", encoding="utf-8") as f:
    json.dump(company_data, f, ensure_ascii=False, indent=4)