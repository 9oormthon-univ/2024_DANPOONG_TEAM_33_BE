import jwt
import os
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

from dotenv import load_dotenv
load_dotenv()

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

def decode_token(auth_header):
    """
    JWT 토큰을 서명 검증을 통해 디코딩하여 userId를 반환합니다.
    
    Args:
        JWT_SECRET_KEY (str): JWT 서명 검증에 사용되는 비밀 키.
        token (str): 'Bearer {token}' 형식의 JWT 토큰.
    
    Returns:
        user_id (str): JWT 페이로드에서 추출한 userId 값.
        400: 유효한 userId가 없을 경우.
        401: 토큰이 만료되었거나 유효하지 않은 경우.
    """
    # print(f"Decoded token: {token}")  # 디버깅용 로그

    token = auth_header.split(" ")[1]

    try:
        # JWT 토큰의 서명을 검증하고 페이로드 디코딩
        decoded_payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        # print(f"Decoded payload: {decoded_payload}")  # 디버깅용 로그

        # 디코딩된 페이로드에서 user_id(PK) 추출
        user_id = decoded_payload.get("userId")
        if not user_id:
            return 400

        # 성공적으로 user_id 반환
        return user_id

    except ExpiredSignatureError:
        print("Token has expired")  # 디버깅용 로그
        return 402
    except InvalidTokenError:
        print("Invalid token")  # 디버깅용 로그
        return 401
