# app/routes/llm.py
from fastapi import APIRouter, Depends, Body
from app.services.llm_service import LLMService
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.database import get_database
from app.services.image_services import verify_jwt
from pydantic import BaseModel

router = APIRouter()


# Response 모델 정의
class LLMResponse(BaseModel):
    response: str


# Request 모델 정의
class LLMQuery(BaseModel):
    query: str


async def get_llm_service(db: AsyncIOMotorClient = Depends(get_database)):
    return LLMService(mongodb_client=db)


@router.post("/query", response_model=LLMResponse)
async def process_llm_query(
        query_data: LLMQuery = Body(...),
        user_id: str = Depends(verify_jwt),
        llm_service: LLMService = Depends(get_llm_service)
):
    """
    사용자의 질의를 처리하여 저장된 파일들에서 답변을 찾습니다.

    Args:
        query_data: LLMQuery 모델로 정의된 사용자의 질문
        user_id: JWT에서 추출한 사용자 ID
        llm_service: LLM 서비스 인스턴스

    Returns:
        LLMResponse: LLM의 응답
    """
    response = await llm_service.process_query(user_id, query_data.query)
    return LLMResponse(response=response)