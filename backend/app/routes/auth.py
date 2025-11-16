from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.auth import create_access_token
from app.config import ADMIN_EMAIL

router = APIRouter()


@router.post('/token')
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Demo authentication: accept any user with non-empty username/password
    username = form_data.username
    password = form_data.password
    if not username or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid credentials')

    # simple role assignment: if username matches ADMIN_EMAIL, grant admin
    role = 'admin' if username.lower() == ADMIN_EMAIL.lower() else 'user'

    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": username, "role": role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "role": role}
