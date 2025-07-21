#\!/usr/bin/env python3
import sys
import os
from urllib.parse import urlparse, parse_qs
sys.path.append('/home/davidpm/lifehub')

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def complete_auth(redirect_url):
    credentials_path = '/home/davidpm/lifehub/modules/calendar/credentials.json'
    token_path = '/home/davidpm/lifehub/modules/calendar/token.json'
    
    # Parse the authorization code from the redirect URL
    parsed_url = urlparse(redirect_url)
    query_params = parse_qs(parsed_url.query)
    
    if 'code' not in query_params:
        print('No authorization code found in URL.')
        return
    
    auth_code = query_params['code'][0]
    print(f'Found authorization code: {auth_code[:20]}...')
    
    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
    flow.redirect_uri = 'http://localhost'
    
    try:
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        
        # Save credentials
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        
        print('✅ Success\! Google Calendar authentication completed.')
        print(f'Token saved to: {token_path}')
        print('Restart the lifehub service to use the calendar:')
        print('sudo systemctl restart lifehub.service')
        
    except Exception as e:
        print(f'❌ Authentication failed: {e}')

if __name__ == '__main__':
    if len(sys.argv) \!= 2:
        print('Usage: python3 complete_auth_final.py http://localhost/?code=...')
        sys.exit(1)
    
    complete_auth(sys.argv[1])
