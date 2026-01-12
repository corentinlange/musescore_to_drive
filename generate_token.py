#!/usr/bin/env python3
"""
Generate OAuth 2.0 token for Google Drive access

This script helps you authenticate with Google Drive using OAuth 2.0.
It will open your browser and ask you to grant permissions.

Prerequisites:
  - credentials.json (download from Google Cloud Console)
  - pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client

Usage:
  python generate_token.py
"""

import os
import json

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
except ImportError:
    print("❌ Error: Required packages not installed")
    print("\nInstall with:")
    print("  pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    exit(1)

SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    creds = None
    
    # Check if token already exists
    if os.path.exists('token.json'):
        print("⚠️  token.json already exists")
        response = input("Do you want to regenerate it? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Aborted.")
            return
        os.remove('token.json')
        print("✓ Deleted existing token.json")
    
    # Check if credentials.json exists
    if not os.path.exists('credentials.json'):
        print("❌ Error: credentials.json not found")
        print("\nHow to get credentials.json:")
        print("  1. Go to Google Cloud Console")
        print("  2. APIs & Services → Credentials")
        print("  3. Create OAuth 2.0 Client ID (Desktop app)")
        print("  4. Download JSON and save as 'credentials.json'")
        print("\nSee SETUP.md for detailed instructions")
        return
    
    print("\n🔐 Starting OAuth 2.0 authentication flow...")
    print("   Your browser will open shortly")
    print("   Please sign in and grant permissions\n")
    
    try:
        # Run OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Save token
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        
        print("\n" + "="*60)
        print("✅ SUCCESS! token.json created")
        print("="*60)
        print("\nNext steps:")
        print("  1. Encode token.json to base64:")
        print("     • Linux/Mac: cat token.json | base64 -w 0")
        print("     • Windows: see SETUP.md for PowerShell command")
        print("\n  2. Add to GitHub Secrets:")
        print("     • Settings → Secrets → New secret")
        print("     • Name: GDRIVE_TOKEN")
        print("     • Value: <base64 string>")
        print("\n⚠️  IMPORTANT:")
        print("  • Never commit token.json to Git")
        print("  • Keep it secret - it allows full Drive access")
        print("  • Delete after encoding if you want")
        
    except Exception as e:
        print(f"\n❌ Error during authentication: {e}")
        print("\nTroubleshooting:")
        print("  • Make sure you're using the correct Google account")
        print("  • Check that OAuth consent screen is configured")
        print("  • Verify your email is added as a test user")

if __name__ == '__main__':
    main()
