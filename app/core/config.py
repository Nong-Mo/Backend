from datetime import timedelta
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# .env 파일에서 환경 변수 로드
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
if not MONGO_URL:
    raise ValueError("MONGO_URL 환경 변수가 설정되지 않았습니다.")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# JWT 관련 설정 값
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise ValueError("SECRET_KEY must be at least 32 characters long")

ALGORITHM = "HS256" 
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# JWT 관련 추가 설정
JWT_MIN_LENGTH = 32
JWT_MAX_AGE = timedelta(days=7)

# Naver CLOVA OCR API 설정
NAVER_CLOVA_OCR_SECRET = os.getenv("NAVER_CLOVA_OCR_SECRET")
NAVER_CLOVA_OCR_API_URL = os.getenv("NAVER_CLOVA_OCR_API_URL")

# Naver CLOVA Receipt OCR API 설정
NAVER_CLOVA_RECEIPT_OCR_SECRET = os.getenv("NAVER_CLOVA_RECEIPT_OCR_SECRET")
NAVER_CLOVA_RECEIPT_OCR_API_URL = os.getenv("NAVER_CLOVA_RECEIPT_OCR_API_URL")

# AWS 자격 증명
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_REGION_NAME = os.getenv("S3_REGION_NAME")

# Naver Cloud Platfrom API key
NCP_CLIENT_ID = os.getenv("NCP_CLIENT_ID")
NCP_CLIENT_SECRET = os.getenv("NCP_CLIENT_SECRET")

# TTS API URL
NCP_TTS_API_URL = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"

# GOOGLE API KEY
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")