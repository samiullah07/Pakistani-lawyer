"""
Test conversational features of Pakistan Legal AI
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_conversation():
    """Test various types of conversations"""
    
    test_queries = [
        # Greetings
        ("hi", "Should respond with greeting"),
        ("hello", "Should respond with greeting"),
        ("assalam alaikum", "Should respond with Islamic greeting"),
        
        # Identity questions
        ("who are you?", "Should explain identity as Legal Assistant"),
        ("what are you?", "Should explain capabilities"),
        
        # How are you
        ("how are you?", "Should respond positively and offer help"),
        
        # Capabilities
        ("what can you do?", "Should list legal capabilities"),
        ("how can you help me?", "Should explain legal assistance"),
        
        # Thanks
        ("thank you", "Should acknowledge thanks"),
        ("shukria", "Should acknowledge thanks in Urdu"),
        
        # Legal questions
        ("what is section 420?", "Should provide legal analysis"),
        ("how to file divorce in pakistan?", "Should provide legal guidance"),
        
        # Non-legal questions
        ("what is the weather today?", "Should redirect to legal topics"),
        ("how to cook biryani?", "Should explain out of domain"),
        ("what is 2+2?", "Should redirect to legal expertise"),
    ]
    
    print("🧪 Testing Conversational Features")
    print("=" * 50)
    
    for query, expected in test_queries:
        print(f"\n📝 Query: '{query}'")
        print(f"🎯 Expected: {expected}")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/chat/message",
                json={"query": query},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data['response']
                print(f"✅ Response: {answer[:100]}...")
            else:
                print(f"❌ Error: Status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to API. Make sure 'python api.py' is running")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 30)

if __name__ == "__main__":
    test_conversation()
