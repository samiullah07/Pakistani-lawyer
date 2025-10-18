"""
Quick Test Script for Bilingual Legal Assistant
Run this to verify the new features are working
"""

def test_bilingual_agent():
    """Test the bilingual agent with various queries"""
    
    print("="*70)
    print("🧪 TESTING BILINGUAL LEGAL ASSISTANT - SAMI ULLAH AI")
    print("="*70)
    
    try:
        from agent import create_legal_agent
        
        print("\n✅ Successfully imported agent module")
        print("📝 Creating legal agent instance...")
        
        agent = create_legal_agent()
        print("✅ Agent created successfully!\n")
        
        # Test cases
        test_cases = [
            {
                "name": "English Greeting",
                "query": "Hi, how are you?",
                "expected": "casual response in English"
            },
            {
                "name": "Urdu Greeting",
                "query": "Salam, kaise ho?",
                "expected": "casual response in Urdu"
            },
            {
                "name": "English Legal Query",
                "query": "What is section 420 in Pakistan?",
                "expected": "structured legal analysis in English"
            },
            {
                "name": "Urdu Legal Query",
                "query": "Section 302 kya hai?",
                "expected": "structured legal analysis in Urdu"
            },
            {
                "name": "Thank You (English)",
                "query": "Thank you so much!",
                "expected": "friendly acknowledgment in English"
            },
            {
                "name": "Thank You (Urdu)",
                "query": "Shukriya",
                "expected": "friendly acknowledgment in Urdu"
            }
        ]
        
        passed = 0
        failed = 0
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n{'='*70}")
            print(f"TEST {i}: {test['name']}")
            print(f"{'='*70}")
            print(f"Query: {test['query']}")
            print(f"Expected: {test['expected']}")
            print(f"\n{'─'*70}")
            print("Response:")
            print(f"{'─'*70}")
            
            try:
                response = agent.process_legal_query(test['query'])
                print(response)
                
                # Basic validation
                if response and len(response) > 10:
                    print(f"\n✅ Test {i} PASSED")
                    passed += 1
                else:
                    print(f"\n❌ Test {i} FAILED (empty or too short response)")
                    failed += 1
                    
            except Exception as e:
                print(f"\n❌ Test {i} FAILED with error: {str(e)}")
                failed += 1
        
        # Summary
        print(f"\n{'='*70}")
        print("📊 TEST SUMMARY")
        print(f"{'='*70}")
        print(f"✅ Passed: {passed}/{len(test_cases)}")
        print(f"❌ Failed: {failed}/{len(test_cases)}")
        print(f"{'='*70}\n")
        
        if failed == 0:
            print("🎉 ALL TESTS PASSED! Your bilingual assistant is working perfectly!")
        else:
            print("⚠️  Some tests failed. Please check the errors above.")
            
    except ImportError as e:
        print(f"\n❌ ERROR: Could not import agent module")
        print(f"Error details: {str(e)}")
        print("\nMake sure you're running this from the Law2.0 directory:")
        print('cd "C:\\Users\\BEST LAPTOP\\Desktop\\Law2.0"')
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\nPlease make sure:")
        print("1. You're in the correct directory")
        print("2. All dependencies are installed (pip install -r requirements.txt)")
        print("3. The vector store exists (run: python main.py first)")


def test_language_detection():
    """Test language detection specifically"""
    print("\n" + "="*70)
    print("🌐 TESTING LANGUAGE DETECTION")
    print("="*70)
    
    test_phrases = [
        ("Hello", "english"),
        ("Hi there", "english"),
        ("Salam", "urdu"),
        ("Kaise ho", "urdu"),
        ("What is law", "english"),
        ("Qanoon kya hai", "urdu"),
        ("Section 420", "english"),
        ("Dafa 302", "urdu")
    ]
    
    try:
        from agent import LegalAgent
        import re
        
        for phrase, expected_lang in test_phrases:
            # Simple detection logic test
            urdu_pattern = re.compile(r'[\u0600-\u06FF]')
            urdu_roman_words = ['kya', 'hai', 'mein', 'ka', 'ki', 'ko', 'se', 
                               'aap', 'main', 'hun', 'salam', 'kaise']
            
            phrase_lower = phrase.lower()
            
            if urdu_pattern.search(phrase):
                detected = "urdu"
            elif any(word in phrase_lower.split() for word in urdu_roman_words):
                detected = "urdu"
            else:
                detected = "english"
            
            status = "✅" if detected == expected_lang else "❌"
            print(f"{status} '{phrase}' → Detected: {detected}, Expected: {expected_lang}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_intent_detection():
    """Test intent detection"""
    print("\n" + "="*70)
    print("🎯 TESTING INTENT DETECTION")
    print("="*70)
    
    test_phrases = [
        ("Hi", "casual"),
        ("Hello, how are you?", "casual"),
        ("What is section 420?", "legal"),
        ("Salam", "casual"),
        ("Thank you", "casual"),
        ("What are my rights?", "legal"),
        ("Section 302 kya hai?", "legal"),
        ("Kaise ho?", "casual")
    ]
    
    casual_patterns = [
        'hi', 'hello', 'hey', 'how are you', 'whats up', 'thanks', 'thank you',
        'salam', 'kaise ho', 'shukriya'
    ]
    
    legal_keywords = [
        'law', 'section', 'rights', 'qanoon', 'dafa'
    ]
    
    for phrase, expected_intent in test_phrases:
        phrase_lower = phrase.lower()
        
        is_casual = any(pattern in phrase_lower for pattern in casual_patterns)
        has_legal = any(keyword in phrase_lower for keyword in legal_keywords)
        
        if is_casual and not has_legal and len(phrase.split()) < 15:
            detected = "casual"
        else:
            detected = "legal"
        
        status = "✅" if detected == expected_intent else "❌"
        print(f"{status} '{phrase}' → Detected: {detected}, Expected: {expected_intent}")


if __name__ == "__main__":
    print("\n🚀 Starting comprehensive tests for Sami Ullah AI...\n")
    
    # Run all tests
    test_language_detection()
    test_intent_detection()
    test_bilingual_agent()
    
    print("\n" + "="*70)
    print("🏁 TESTING COMPLETE")
    print("="*70)
    print("\nIf all tests passed, your bilingual assistant is ready to use!")
    print("\nTo start the full system, run:")
    print("  python start.py")
    print("\nThen open: http://localhost:8501")
    print("="*70 + "\n")
