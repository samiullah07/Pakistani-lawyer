"""
Test lawyer directory functionality
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_lawyer_directory():
    """Test lawyer directory queries"""
    
    test_queries = [
        # Basic lawyer search queries
        ("I need a lawyer in Lahore", "Should return Lahore lawyers"),
        ("Find me a lawyer in Karachi", "Should return Karachi lawyers"),
        ("Lawyers in Islamabad", "Should return Islamabad lawyers"),
        ("I need legal help in Gujranwala", "Should return Gujranwala lawyers"),
        ("Advocate in Multan", "Should return Multan lawyers"),
        
        # Specialized lawyer searches
        ("Criminal lawyer in Lahore", "Should return criminal lawyers in Lahore"),
        ("Family lawyer in Karachi", "Should return family lawyers in Karachi"),
        ("Corporate lawyer in Islamabad", "Should return corporate lawyers in Islamabad"),
        ("Civil lawyer in Multan", "Should return civil lawyers in Multan"),
        
        # Urdu queries
        ("Lahore mein wakeel chahiye", "Should return Lahore lawyers"),
        ("Karachi ka advocate", "Should return Karachi lawyers"),
        
        # General requests (should ask for city)
        ("I need a lawyer", "Should ask for city specification"),
        ("Find me legal help", "Should ask for city specification"),
        ("Wakeel chahiye", "Should ask for city specification"),
        
        # Non-lawyer queries (should go to legal analysis)
        ("What is section 420?", "Should provide legal analysis, not lawyer directory")
    ]
    
    print("🧪 Testing Lawyer Directory Feature")
    print("=" * 60)
    
    for i, (query, expected) in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        print(f"   Expected: {expected}")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/chat/message",
                json={"query": query},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data['response']
                
                # Check if response is lawyer directory
                is_lawyer_directory = any(phrase in answer for phrase in [
                    "Qualified Lawyers", "Bar Council:", "Experience:", "Email:", "Phone:",
                    "I have lawyer information for:", "Please specify which city"
                ])
                
                # Check if response is legal analysis
                is_legal_analysis = any(phrase in answer for phrase in [
                    "Legal Analysis:", "Query Domain:", "section", "law", "penalty"
                ])
                
                if "lawyer" in query.lower() or "wakeel" in query.lower() or "advocate" in query.lower():
                    if is_lawyer_directory:
                        print(f"   ✅ CORRECT: Lawyer directory response")
                        
                        # Count lawyers returned
                        lawyer_count = answer.count("**Email:**")
                        print(f"   📊 Lawyers found: {lawyer_count}")
                        
                        # Check if specific city lawyers returned
                        cities = ["Lahore", "Karachi", "Islamabad", "Gujranwala", "Multan"]
                        found_city = None
                        for city in cities:
                            if city.lower() in query.lower() and city in answer:
                                found_city = city
                                break
                        
                        if found_city:
                            print(f"   ✅ City match: {found_city} lawyers returned")
                        elif "specify which city" in answer:
                            print(f"   ✅ Correctly asking for city specification")
                        
                    elif is_legal_analysis:
                        print(f"   ❌ WRONG: Got legal analysis instead of lawyer directory")
                    else:
                        print(f"   ⚠️ UNCLEAR: Response type unknown")
                else:
                    # Non-lawyer query should NOT return lawyer directory
                    if not is_lawyer_directory:
                        print(f"   ✅ CORRECT: Not lawyer directory (as expected)")
                    else:
                        print(f"   ❌ WRONG: Got lawyer directory for non-lawyer query")
                
                print(f"   💬 Response preview: {answer[:150]}...")
                
            else:
                print(f"   ❌ API Error: Status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Cannot connect to API. Make sure 'python api.py' is running")
            break
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("-" * 40)

if __name__ == "__main__":
    test_lawyer_directory()
