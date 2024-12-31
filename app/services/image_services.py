import os
import uuid
from typing import List
from fastapi import UploadFile, HTTPException, status, Depends, Header
from app.models.image import ImageMetadata, ImageDocument
from app.core.config import NAVER_CLOVA_OCR_API_URL, NAVER_CLOVA_OCR_SECRET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME, SECRET_KEY, ALGORITHM
import boto3
import botocore
import requests
from datetime import datetime
import shutil
from jose import jwt  # JWT 처리 라이브러리
from jose.exceptions import JWTError
from fastapi.security import OAuth2PasswordBearer

s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT 인증 검증 함수
async def verify_jwt(token: str = Header(...)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")  # 사용자 ID 추출
        if user_id is None:
            raise credentials_exception
        # 여기에서 사용자 정보를 가져오는 로직을 추가할 수 있습니다.
        # 예: user = await get_user_by_id(user_id)
    except JWTError:  # JWT 검증 실패 시 예외 처리
        raise credentials_exception
    return user_id  # 사용자 ID 반환


class ImageService:
    async def process_images(self, title: str, files: List[UploadFile], user_id: str = Depends(verify_jwt)):
        file_id = str(uuid.uuid4())
        # 사용자 ID를 포함한 업로드 경로 생성
        upload_dir = f"/tmp/{user_id}/{file_id}"
        os.makedirs(upload_dir, exist_ok=True)

        processed_files = []
        try:
            for file in files:
                file_path = os.path.join(upload_dir, file.filename)
                # 파일을 로컬에 저장
                try:
                    with open(file_path, "wb") as f:
                        content = await file.read()
                        f.write(content)
                except (IOError, ValueError) as e:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to read file: {e}")

                # 네이버 CLOVA OCR 호출 및 결과 처리
                text, pdf_file = self._call_clova_ocr(file_path)

                # S3에 PDF 업로드 (PDF 경로 설정)
                try:
                    s3_key_prefix = f"{file_id}/{file.filename}"
                    s3.upload_file(pdf_file, S3_BUCKET_NAME, f"{s3_key_prefix}.pdf")
                except botocore.exceptions.ClientError as e:
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to upload file to S3: {e}")

                # 이미지 파일 메타데이터 저장
                processed_files.append(ImageMetadata(
                    filename=file.filename,
                    content_type=file.content_type,
                    size=len(content)
                ))

            # 이미지 문서 반환
            image_doc = ImageDocument(
                title=title,
                file_id=file_id,
                processed_files=processed_files,
                created_at=datetime.utcnow().isoformat()
            )
            return image_doc

        except requests.exceptions.RequestException as e:
            # OCR 외부 API에서 오류 발생시 처리
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"External API Error: {str(e)}"
            )
        finally:
            # 업로드 후 임시 디렉토리 삭제
            shutil.rmtree(upload_dir)

    def _call_clova_ocr(self, image_path):
        headers = {'X-OCR-SECRET': NAVER_CLOVA_OCR_SECRET}
        # 이미지 파일을 열어 CLOVA OCR에 전송
        try:
            with open(image_path, 'rb') as file:
                files = {'file': file}
                response = requests.post(NAVER_CLOVA_OCR_API_URL, headers=headers, files=files)
            response.raise_for_status()  # HTTP 에러 발생 시 예외 발생
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:  # API 키 오류 등
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid request to OCR API: {e}")
            else:  # 서버 오류 등
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to call OCR API: {e}")
        except requests.exceptions.RequestException as e:  # 네트워크 오류 등
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to connect to OCR API: {e}")

        data = response.json()

        # OCR 텍스트 및 PDF 반환
        text = " ".join(field['inferText'] for field in data['images'][0]['fields'])
        pdf_file = f"{image_path}.pdf"  # OCR API에서 반환된 PDF 파일 경로
        return text, pdf_file