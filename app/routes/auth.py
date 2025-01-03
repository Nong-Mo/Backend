from fastapi import APIRouter, HTTPException
from app.models.user import UserCreate, UserLogin
from app.services.auth_service import create_user, login_user

router = APIRouter()


@router.post("/signup", status_code=201)
async def signup(user: UserCreate):
    try:
        await create_user(user)
        return {"message": "User created successfully", "user": user}  # 생성된 사용자 정보 반환
    except HTTPException as e:
        raise e  # create_user에서 발생한 HTTPException을 그대로 전달
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # 예상치 못한 에러는 500 Internal Server Error 반환

@router.post("/signin", status_code=200)
async def login(user: UserLogin):
    try:
        token = await login_user(user)
        return {"message": "Login successful", "token": token}  # 로그인 성공 메시지와 토큰 반환
    except HTTPException as e:
        raise e  # login_user에서 발생한 HTTPException을 그대로 전달
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # 예상치 못한 에러는 500 Internal Server Error 반환