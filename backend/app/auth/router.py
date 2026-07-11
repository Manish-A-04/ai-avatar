from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from sqlalchemy.future import select
from app.database import get_db
from app.config import settings
from app.auth.schemas import UserRegisterRequest, UserLoginRequest, TokenResponse, TokenRefreshRequest, UserMeResponse
from app.auth.service import auth_service
from app.auth.dependencies import get_current_user
from app.auth.models import User, TokenBlocklist

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserMeResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await auth_service.register(db, data)
    return user

@router.post("/login", response_model=TokenResponse)
async def login(data: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    user = await auth_service.authenticate(db, data)
    access_token = auth_service.create_access_token(user.id)
    refresh_token, jti = auth_service.create_refresh_token(user.id)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: TokenRefreshRequest, db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(data.refresh_token, settings.secret_key, algorithms=[settings.algorithm])
        user_id_str: str = payload.get("sub")
        token_type: str = payload.get("type")
        jti_str: str = payload.get("jti")
        if user_id_str is None or token_type != "refresh" or jti_str is None:
            raise credentials_exception
        result = await db.execute(select(TokenBlocklist).where(TokenBlocklist.jti == jti_str))
        if result.scalar_one_or_none():
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    access_token = auth_service.create_access_token(user_id_str)
    new_refresh_token, new_jti = auth_service.create_refresh_token(user_id_str)
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.access_token_expire_minutes * 60
    )

@router.get("/me", response_model=UserMeResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    data: TokenRefreshRequest, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        payload = jwt.decode(data.refresh_token, settings.secret_key, algorithms=[settings.algorithm])
        jti_str: str = payload.get("jti")
        user_id_str: str = payload.get("sub")
        exp = payload.get("exp")
        if str(current_user.id) != user_id_str:
            raise HTTPException(status_code=403, detail="Invalid token for user")
        blocklist_entry = TokenBlocklist(
            jti=jti_str,
            user_id=current_user.id,
            expires_at=datetime.fromtimestamp(exp, tz=timezone.utc)
        )
        db.add(blocklist_entry)
        await db.commit()
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
