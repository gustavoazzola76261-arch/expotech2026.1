from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.api_errors import forbidden, unauthorized
from app.core.security import create_access_token, verify_password
from app.models import User
from app.schemas.auth import TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=TokenResponse)
def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> TokenResponse:
    email = (form_data.username or "").lower().strip()
    user = db.scalars(select(User).where(User.email == email)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise unauthorized(log_detail=f"login failed for email={email}")
    if not user.is_active:
        raise forbidden(log_detail=f"inactive user id={user.id}")
    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token, token_type="bearer")
