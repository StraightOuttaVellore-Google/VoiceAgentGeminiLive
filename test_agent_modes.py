#!/usr/bin/env python3
"""
Test script to verify both study and wellness agent modes work correctly
"""

import requests
import json

def test_agent_modes():
    """Test that both agent modes are properly configured"""
    print("🧪 Testing Agent Modes Configuration")
    print("=" * 50)
    
    try:
        # Test the agent modes endpoint
        response = requests.get("http://localhost:8000/api/agent-modes")
        if response.status_code != 200:
            print(f"❌ Failed to get agent modes: {response.status_code}")
            return False
        
        data = response.json()
        modes = data.get("modes", {})
        
        # Check if both modes exist
        if "wellness" not in modes:
            print("❌ Wellness mode not found")
            return False
        
        if "study" not in modes:
            print("❌ Study mode not found")
            return False
        
        print("✅ Both agent modes found")
        
        # Test wellness mode configuration
        wellness = modes["wellness"]
        print(f"\n🌱 Wellness Mode:")
        print(f"   Name: {wellness.get('name')}")
        print(f"   Description: {wellness.get('description')}")
        print(f"   Icon: {wellness.get('icon')}")
        print(f"   Color: {wellness.get('color')}")
        print(f"   System Prompt: {wellness.get('systemPrompt', '')[:100]}...")
        
        # Test study mode configuration
        study = modes["study"]
        print(f"\n📚 Study Mode:")
        print(f"   Name: {study.get('name')}")
        print(f"   Description: {study.get('description')}")
        print(f"   Icon: {study.get('icon')}")
        print(f"   Color: {study.get('color')}")
        print(f"   System Prompt: {study.get('systemPrompt', '')[:100]}...")
        
        # Verify system prompts are different
        wellness_prompt = wellness.get('systemPrompt', '')
        study_prompt = study.get('systemPrompt', '')
        
        if wellness_prompt == study_prompt:
            print("❌ System prompts are identical - they should be different!")
            return False
        
        print("\n✅ System prompts are different for each mode")
        
        # Check for key differences in prompts
        wellness_keywords = ['wellness', 'mindfulness', 'emotional', 'support', 'meditation']
        study_keywords = ['study', 'learning', 'productivity', 'academic', 'education']
        
        wellness_has_keywords = any(keyword in wellness_prompt.lower() for keyword in wellness_keywords)
        study_has_keywords = any(keyword in study_prompt.lower() for keyword in study_keywords)
        
        if not wellness_has_keywords:
            print("⚠️  Wellness prompt may not contain expected keywords")
        
        if not study_has_keywords:
            print("⚠️  Study prompt may not contain expected keywords")
        
        print("\n🎉 Agent modes test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing agent modes: {e}")
        return False

def test_health():
    """Test backend health"""
    print("\n🔍 Testing Backend Health")
    print("-" * 30)
    
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy: {data}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking backend health: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Sahay Dual Agent Modes")
    print("=" * 50)
    
    # Test backend health first
    if not test_health():
        print("\n❌ Backend is not running. Please start it first:")
        print("   cd backend && source venv/bin/activate && python main.py")
        return
    
    # Test agent modes
    if test_agent_modes():
        print("\n✅ All tests passed! Both study and wellness agent modes are working correctly.")
        print("\n📋 Next steps:")
        print("1. Start the frontend: cd frontend && npm run dev")
        print("2. Open http://localhost:5173 in your browser")
        print("3. Test both agent modes in the UI")
    else:
        print("\n❌ Some tests failed. Check the configuration.")

if __name__ == "__main__":
    main()
