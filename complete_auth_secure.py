#\!/usr/bin/env python3
"""
Secure Google OAuth Authentication
Uses environment variables instead of hardcoded credentials
"""
import sys
import os
sys.path.append('/home/davidpm/lifehub')

from google_auth_oauthlib.flow import InstalledAppFlow
from config.env_config import get_oauth_config, Config
import logging

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def complete_auth(auth_code: str) -> dict:
    """
    Complete OAuth flow with authorization code
    
    Args:
        auth_code: Authorization code from OAuth callback
        
    Returns:
        Token dictionary with credentials
    """
    try:
        # Get OAuth config from environment variables
        oauth_config = get_oauth_config()
        
        # Create flow from config
        flow = InstalledAppFlow.from_client_config(
            oauth_config,
            SCOPES
        )
        
        # Set redirect URI
        flow.redirect_uri = Config.GOOGLE_REDIRECT_URI
        
        # Exchange authorization code for tokens
        flow.fetch_token(code=auth_code)
        
        # Get credentials
        credentials = flow.credentials
        
        # Return token info
        token_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        logger.info("OAuth authentication completed successfully")
        return token_data
        
    except Exception as e:
        logger.error(f"OAuth authentication failed: {e}")
        raise

if __name__ == "__main__":
    if len(sys.argv) \!= 2:
        print("Usage: python complete_auth_secure.py <authorization_code>")
        sys.exit(1)
        
    auth_code = sys.argv[1]
    try:
        token_data = complete_auth(auth_code)
        print("✅ Authentication successful\!")
        print("Token data saved securely.")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        sys.exit(1)
EOF < /dev/null
