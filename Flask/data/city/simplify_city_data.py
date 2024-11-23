import pandas as pd
import json

# 엑셀 파일 읽기 (파일 경로에 맞게 수정하세요)
file_path = 'Flask/data/city/전국행정동리스트.xlsx'
df = pd.read_excel(file_path, header=3)  # 데이터가 4행부터 시작하므로 header=3

# 결과를 저장할 리스트
result = []

# 데이터 프레임을 순회하면서 JSON 구조로 변환
for _, row in df.iterrows():
    category = row[0]   # 대분류
    city = row[1]       # 시/군
    district = row[2]   # 구

    # 대분류(예: 서울특별시)가 리스트에 없으면 추가
    region = next((item for item in result if item["region"] == category), None)
    if not region:
        region = {"region": category, "subregion": []}
        result.append(region)

    # 시/군과 구가 모두 없는 경우
    if pd.isna(city) and pd.isna(district):
        continue

    # 구가 있는 경우 "{시/군} {구}" 형식으로 저장
    if not pd.isna(district):
        if pd.isna(city):
            city_district = district
        else:
            city_district = f"{city} {district}"
        if city_district not in region["subregion"]:
            region["subregion"].append(city_district)
    # 구가 없는 경우 "{시/군}"만 저장
    else:
        if city not in region["subregion"]:
            region["subregion"].append(city)

# JSON으로 변환하여 출력 (또는 저장)
json_result = json.dumps(result, ensure_ascii=False, indent=4)
print(json_result)

# JSON 결과를 파일로 저장
with open("Flask/data/city/전국행정동리스트_x.json", "w", encoding="utf-8") as f:
    f.write(json_result)