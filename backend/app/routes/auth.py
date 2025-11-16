from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
import logging

from app.auth import create_access_token, get_current_user
from app.config import ADMIN_EMAIL, FRONTEND_URL
from app.services.oauth_service import oauth_service
from app.db import SessionLocal, User

logger = logging.getLogger(__name__)
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


@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.get("/oauth/{provider}")
async def oauth_login(provider: str):
    """Initiate OAuth login with provider (google, github)"""
    try:
        redirect_uri = f"{FRONTEND_URL}/auth/callback/{provider}"
        result = oauth_service.get_authorization_url(provider, redirect_uri)
        
        return {
            "authorization_url": result["authorization_url"],
            "state": result["state"]
        }
    except Exception as e:
        logger.exception(f"OAuth login failed for {provider}")
        raise HTTPException(400, f"OAuth login failed: {str(e)}")

@router.get("/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    code: str = Query(...),
    state: str = Query(...),
    error: str = Query(None)
):
    """Handle OAuth callback"""
    if error:
        logger.error(f"OAuth error: {error}")
        return RedirectResponse(f"{FRONTEND_URL}/auth/error?error={error}")
    
    try:
        # Handle OAuth callback
        user_data = await oauth_service.handle_callback(provider, code, state)
        
        # Create or update user in database
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == user_data['email']).first()
            
            if not user:
                # Create new user
                user = User(
                    email=user_data['email'],
                    name=user_data['name'],
                    provider=user_data['provider'],
                    provider_id=user_data['provider_id'],
                    picture=user_data.get('picture'),
                    verified_email=user_data.get('verified_email', False)
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            else:
                # Update existing user
                user.name = user_data['name']
                user.picture = user_data.get('picture')
                user.verified_email = user_data.get('verified_email', False)
                db.commit()
        
        finally:
            db.close()
        
        # Create JWT token
        role = "admin" if user.email == ADMIN_EMAIL else "user"
        access_token_expires = timedelta(minutes=60)
        access_token = create_access_token(
            data={"sub": user.email, "role": role, "user_id": user.id},
            expires_delta=access_token_expires
        )
        
        # Redirect to frontend with token
        return RedirectResponse(f"{FRONTEND_URL}/auth/success?token={access_token}")
        
    except Exception as e:
        logger.exception(f"OAuth callback failed for {provider}")
        return RedirectResponse(f"{FRONTEND_URL}/auth/error?error=callback_failed")

@router.post("/logout")
async def logout():
    """Logout user (client-side token removal)"""
    return {"message": "Logged out successfully"}
