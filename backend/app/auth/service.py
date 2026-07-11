from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4
import bcrypt
from fastapi import HTTPException
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.config import settings
from app.auth.models import User
from app.auth.schemas import UserRegisterRequest, UserLoginRequest

class AuthService:
    def hash_password(self, plain: str) -> str:
        pwd_bytes = plain.encode('utf-8')[:72]
        hashed_bytes = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt())
        return hashed_bytes.decode('utf-8')

    def verify_password(self, plain: str, hashed: str) -> bool:
        pwd_bytes = plain.encode('utf-8')[:72]
        hashed_bytes = hashed.encode('utf-8')
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)

    def create_access_token(self, user_id: UUID) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
        payload = {
            "sub": str(user_id),
            "type": "access",
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

    def create_refresh_token(self, user_id: UUID) -> tuple[str, UUID]:
        jti = uuid4()
        expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "jti": str(jti),
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        }
        token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
        return token, jti

    async def _email_exists(self, db: AsyncSession, email: str) -> bool:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none() is not None

    async def _username_exists(self, db: AsyncSession, username: str) -> bool:
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none() is not None

    async def _get_by_email(self, db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def register(self, db: AsyncSession, data: UserRegisterRequest) -> User:
        if await self._email_exists(db, data.email.lower()):
            raise HTTPException(400, "Email already registered")
        if await self._username_exists(db, data.username):
            raise HTTPException(400, "Username already taken")
        user = User(
            email=data.email.lower(),
            username=data.username,
            hashed_password=self.hash_password(data.password)
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def authenticate(self, db: AsyncSession, data: UserLoginRequest) -> User:
        user = await self._get_by_email(db, data.email.lower())
        if not user or not self.verify_password(data.password, user.hashed_password):
            raise HTTPException(401, "Incorrect email or password")
        if not user.is_active:
            raise HTTPException(403, "Account is deactivated")
        return user

auth_service = AuthService()
