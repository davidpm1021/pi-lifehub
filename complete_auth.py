#\!/usr/bin/env python3
import sys
import os
sys.path.append('/home/davidpm/lifehub')

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def complete_auth(auth_code):
    credentials_path = '/home/davidpm/lifehub/modules/calendar/credentials.json'
    token_path = '/home/davidpm/lifehub/modules/calendar/token.json'
    
    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
    flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
    
    try:
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        
        # Save credentials
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        
        print(f"\n✅ Success\! Google Calendar authentication completed.")
        print(f"Token saved to: {token_path}")
        print(f"\nRestart the lifehub service to use the calendar:")
        print(f"sudo systemctl restart lifehub.service\n")
        
    except Exception as e:
        print(f"\n❌ Authentication failed: {e}\n")

if __name__ == '__main__':
    if len(sys.argv) \!= 2:
        print("Usage: python3 complete_auth.py <authorization_code>")
        sys.exit(1)
    
    complete_auth(sys.argv[1])
