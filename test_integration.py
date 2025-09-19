#!/usr/bin/env python3
"""
Integration test script for Sahay Full-Stack Voice Agent Application
Tests the backend API endpoints and WebSocket connectivity
"""

import requests
import websockets
import json
import asyncio
import sys
from pathlib import Path

class IntegrationTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.ws_url = base_url.replace("http", "ws")

    async def test_health_endpoint(self):
        """Test the health check endpoint"""
        print("🔍 Testing health endpoint...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False

    async def test_voices_endpoint(self):
        """Test the voices API endpoint"""
        print("🔍 Testing voices endpoint...")
        try:
            response = requests.get(f"{self.base_url}/api/voices", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Voices endpoint passed: {data}")
                return True
            else:
                print(f"❌ Voices endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Voices endpoint error: {e}")
            return False

    async def test_websocket_connection(self):
        """Test WebSocket connection"""
        print("🔍 Testing WebSocket connection...")
        try:
            client_id = "test_client"
            uri = f"{self.ws_url}/ws/{client_id}"
            
            async with websockets.connect(uri) as websocket:
                # Send configuration
                config_message = {
                    "type": "config",
                    "config": {
                        "systemPrompt": "You are a test AI assistant.",
                        "voice": "Puck",
                        "googleSearch": False,
                        "allowInterruptions": False
                    }
                }
                
                await websocket.send(json.dumps(config_message))
                print("✅ WebSocket connection established and config sent")
                
                # Wait for a response (with timeout)
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    print(f"✅ Received WebSocket response: {response[:100]}...")
                    return True
                except asyncio.TimeoutError:
                    print("⚠️  WebSocket response timeout (this might be normal)")
                    return True
                    
        except Exception as e:
            print(f"❌ WebSocket connection error: {e}")
            return False

    async def test_frontend_serving(self):
        """Test if frontend is being served"""
        print("🔍 Testing frontend serving...")
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                content = response.text
                if "Sahay" in content or "React" in content or "index.html" in content:
                    print("✅ Frontend serving appears to be working")
                    return True
                else:
                    print("⚠️  Frontend response doesn't look like expected content")
                    return False
            else:
                print(f"❌ Frontend serving failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Frontend serving error: {e}")
            return False

    async def run_all_tests(self):
        """Run all integration tests"""
        print("🧪 Running Sahay Integration Tests")
        print("=" * 50)
        
        tests = [
            ("Health Endpoint", self.test_health_endpoint()),
            ("Voices Endpoint", self.test_voices_endpoint()),
            ("WebSocket Connection", self.test_websocket_connection()),
            ("Frontend Serving", self.test_frontend_serving()),
        ]
        
        results = []
        for test_name, test_coro in tests:
            print(f"\n📋 {test_name}")
            try:
                result = await test_coro
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Test Results Summary:")
        passed = 0
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} {test_name}")
            if result:
                passed += 1
        
        print(f"\n🎯 {passed}/{len(results)} tests passed")
        
        if passed == len(results):
            print("🎉 All tests passed! The integration is working correctly.")
            return True
        else:
            print("⚠️  Some tests failed. Check the backend server and configuration.")
            return False

async def main():
    """Main test function"""
    print("🚀 Starting integration tests...")
    print("Make sure the backend server is running on http://localhost:8000")
    print("You can start it with: cd backend && source venv/bin/activate && python main.py")
    print()
    
    tester = IntegrationTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n✅ Integration test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Integration test failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
