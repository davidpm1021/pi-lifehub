#\!/usr/bin/env python3
import sys
import os
sys.path.append('/home/davidpm/lifehub')

from google_auth_oauthlib.flow import InstalledAppFlow

# Calendar read-only scope
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_auth_url():
    credentials_path = '/home/davidpm/lifehub/modules/calendar/credentials.json'
    
    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
    # Use localhost redirect for desktop apps
    flow.redirect_uri = 'http://localhost'
    
    auth_url, _ = flow.authorization_url(prompt='consent')
    
    print(f"\n📅 Google Calendar Authentication\n")
    print(f"1. Open this URL in your browser:")
    print(f"   {auth_url}\n")
    print(f"2. Sign in to your Google account")
    print(f"3. Grant calendar permissions")
    print(f"4. After granting permission, you'll be redirected to localhost")
    print(f"5. Copy the ENTIRE URL from your browser address bar")
    print(f"6. Run: python3 complete_auth_fixed.py 'FULL_URL_HERE'\n")

if __name__ == '__main__':
    get_auth_url()
