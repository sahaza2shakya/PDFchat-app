#!/usr/bin/env python3
"""
Quick script to check if the backend server is running
"""
import sys
import urllib.request
import json

def check_server():
    try:
        url = "http://localhost:8000/health"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=2) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                print("✅ Backend server is running!")
                print(f"   Status: {data}")
                return True
            else:
                print(f"⚠️  Backend server responded with status {response.status}")
                return False
    except urllib.error.URLError as e:
        if "Connection refused" in str(e) or "Name or service not known" in str(e):
            print("❌ Backend server is NOT running!")
            print("   Please start it with:")
            print("   Mac/Linux: ./start_server.sh")
            print("   Windows: start_server.bat")
            print("   Or manually: uvicorn main:app --reload --port 8000")
        else:
            print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

if __name__ == "__main__":
    success = check_server()
    sys.exit(0 if success else 1)

