"""
OAuth Service for Google, GitHub, and other providers
Supports social login with secure token handling
"""
import logging
from typing import Dict, Optional
import httpx
from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException
import secrets

from app.config import (
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET,
    GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET,
    SECRET_KEY
)

logger = logging.getLogger(__name__)

class OAuthService:
    def __init__(self):
        self.oauth = OAuth()
        self.setup_providers()
        self._active_states = {}  # Store CSRF states
        
    def setup_providers(self):
        """Configure OAuth providers"""
        if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
            self.oauth.register(
                name='google',
                client_id=GOOGLE_CLIENT_ID,
                client_secret=GOOGLE_CLIENT_SECRET,
                server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
                client_kwargs={
                    'scope': 'openid email profile'
                }
            )
            
        if GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET:
            self.oauth.register(
                name='github',
                client_id=GITHUB_CLIENT_ID,
                client_secret=GITHUB_CLIENT_SECRET,
                access_token_url='https://github.com/login/oauth/access_token',
                authorize_url='https://github.com/login/oauth/authorize',
                api_base_url='https://api.github.com/',
                client_kwargs={'scope': 'user:email'},
            )
    
    def get_authorization_url(self, provider: str, redirect_uri: str) -> Dict[str, str]:
        """Generate OAuth authorization URL with CSRF protection"""
        if provider not in ['google', 'github']:
            raise HTTPException(400, f"Unsupported provider: {provider}")
            
        state = secrets.token_urlsafe(32)
        self._active_states[state] = provider
        
        client = getattr(self.oauth, provider)
        redirect_uri = client.authorize_redirect_uri(redirect_uri, state=state)
        
        return {
            "authorization_url": redirect_uri,
            "state": state
        }
    
    async def handle_callback(self, provider: str, code: str, state: str) -> Dict[str, any]:
        """Handle OAuth callback and extract user information"""
        # Validate CSRF state
        if state not in self._active_states or self._active_states[state] != provider:
            raise HTTPException(400, "Invalid state parameter")
            
        # Clean up state
        del self._active_states[state]
        
        try:
            if provider == 'google':
                return await self._handle_google_callback(code)
            elif provider == 'github':
                return await self._handle_github_callback(code)
        except Exception as e:
            logger.exception(f"OAuth callback failed for {provider}")
            raise HTTPException(400, f"Authentication failed: {str(e)}")
    
    async def _handle_google_callback(self, code: str) -> Dict[str, any]:
        """Handle Google OAuth callback"""
        async with httpx.AsyncClient() as client:
            # Exchange code for token
            token_response = await client.post(
                'https://oauth2.googleapis.com/token',
                data={
                    'client_id': GOOGLE_CLIENT_ID,
                    'client_secret': GOOGLE_CLIENT_SECRET,
                    'code': code,
                    'grant_type': 'authorization_code',
                    'redirect_uri': 'http://localhost:3000/auth/callback/google'
                }
            )
            
            if token_response.status_code != 200:
                raise HTTPException(400, "Failed to exchange code for token")
                
            token_data = token_response.json()
            access_token = token_data.get('access_token')
            
            # Get user info
            user_response = await client.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            if user_response.status_code != 200:
                raise HTTPException(400, "Failed to get user information")
                
            user_data = user_response.json()
            
            return {
                'provider': 'google',
                'provider_id': user_data.get('id'),
                'email': user_data.get('email'),
                'name': user_data.get('name'),
                'picture': user_data.get('picture'),
                'verified_email': user_data.get('verified_email', False)
            }
    
    async def _handle_github_callback(self, code: str) -> Dict[str, any]:
        """Handle GitHub OAuth callback"""
        async with httpx.AsyncClient() as client:
            # Exchange code for token
            token_response = await client.post(
                'https://github.com/login/oauth/access_token',
                data={
                    'client_id': GITHUB_CLIENT_ID,
                    'client_secret': GITHUB_CLIENT_SECRET,
                    'code': code
                },
                headers={'Accept': 'application/json'}
            )
            
            if token_response.status_code != 200:
                raise HTTPException(400, "Failed to exchange code for token")
                
            token_data = token_response.json()
            access_token = token_data.get('access_token')
            
            # Get user info
            user_response = await client.get(
                'https://api.github.com/user',
                headers={'Authorization': f'token {access_token}'}
            )
            
            if user_response.status_code != 200:
                raise HTTPException(400, "Failed to get user information")
                
            user_data = user_response.json()
            
            # Get primary email
            email_response = await client.get(
                'https://api.github.com/user/emails',
                headers={'Authorization': f'token {access_token}'}
            )
            
            emails = email_response.json() if email_response.status_code == 200 else []
            primary_email = next((email['email'] for email in emails if email.get('primary')), None)
            
            return {
                'provider': 'github',
                'provider_id': str(user_data.get('id')),
                'email': primary_email or user_data.get('email'),
                'name': user_data.get('name') or user_data.get('login'),
                'picture': user_data.get('avatar_url'),
                'verified_email': any(email.get('verified') for email in emails)
            }

# Global OAuth service instance
oauth_service = OAuthService()
