"""
Test language matching and response preservation
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_language_matching():
    """Test language-specific responses and content preservation"""
    
    test_cases = [
        # English queries -> English responses
        {
            "query": "hello",
            "expected_lang": "english",
            "should_contain": ["Hello!", "I'm your Legal Assistant", "specialized in Pakistani law"],
            "test_type": "greeting"
        },
        {
            "query": "how are you?",
            "expected_lang": "english", 
            "should_contain": ["I'm doing great", "thank you for asking", "criminal law", "civil matters"],
            "test_type": "how_are_you"
        },
        {
            "query": "who are you?",
            "expected_lang": "english",
            "should_contain": ["I'm your Legal Assistant", "AI-powered legal guidance", "Constitution", "Penal Code"],
            "test_type": "identity"
        },
        
        # Urdu queries -> Urdu responses
        {
            "query": "salam",
            "expected_lang": "urdu",
            "should_contain": ["Salam!", "Main aap ka Legal Assistant hun", "Pakistani qanoon"],
            "test_type": "greeting"
        },
        {
            "query": "ap kaise ho?",
            "expected_lang": "urdu",
            "should_contain": ["Main bilkul theek hun", "shukria", "Criminal law", "kya janna chahte hain"],
            "test_type": "how_are_you"
        },
        {
            "query": "ap kaun ho?", 
            "expected_lang": "urdu",
            "should_contain": ["Main aap ka Legal Assistant hun", "Pakistani qanoon mein mahir", "Constitution"],
            "test_type": "identity"
        },
        
        # Legal questions - should preserve full content
        {
            "query": "section 402 or 220 kya ha?",
            "expected_lang": "mixed",
            "should_contain": ["Section 402", "Section 220", "Criminal Procedure", "Pakistan Penal Code"],
            "test_type": "legal_analysis",
            "min_length": 500  # Should be a long detailed response
        },
        {
            "query": "what is section 420?",
            "expected_lang": "english",
            "should_contain": ["420", "cheating", "fraud", "imprisonment"],
            "test_type": "legal_analysis",
            "min_length": 300
        }
    ]
    
    print("🧪 Testing Language Matching & Response Preservation")
    print("=" * 60)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\\n{i}. Testing: '{case['query']}'")
        print(f"   Expected: {case['expected_lang']} response")
        print(f"   Type: {case['test_type']}")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/chat/message",
                json={"query": case["query"]},
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data['response']
                
                # Check language matching
                lang_match = True
                for expected_phrase in case["should_contain"]:
                    if expected_phrase not in answer:
                        lang_match = False
                        print(f"   ❌ Missing expected phrase: '{expected_phrase}'")
                
                if lang_match:
                    print(f"   ✅ Language matching: PASSED")
                else:
                    print(f"   ❌ Language matching: FAILED")
                
                # Check response length for legal queries
                if case.get("min_length"):
                    if len(answer) >= case["min_length"]:
                        print(f"   ✅ Content preservation: PASSED ({len(answer)} chars)")
                    else:
                        print(f"   ❌ Content preservation: FAILED ({len(answer)} chars, expected >{case['min_length']})")
                        print(f"   Response was: {answer[:200]}...")
                
                # Check if it's conversational vs legal
                is_conversational = any(phrase in answer.lower() for phrase in [
                    "salam!", "hello!", "main bilkul theek hun", "i'm doing great",
                    "main aap ka legal assistant hun"
                ])
                
                if case["test_type"] in ["greeting", "how_are_you", "identity"]:
                    if is_conversational:
                        print(f"   ✅ Response type: CONVERSATIONAL (correct)")
                    else:
                        print(f"   ❌ Response type: Should be conversational")
                else:
                    if not is_conversational:
                        print(f"   ✅ Response type: LEGAL ANALYSIS (correct)")
                    else:
                        print(f"   ❌ Response type: Should be legal analysis")
                        
            else:
                print(f"   ❌ API Error: Status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Cannot connect to API. Make sure 'python api.py' is running")
            break
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("-" * 30)

if __name__ == "__main__":
    test_language_matching()
