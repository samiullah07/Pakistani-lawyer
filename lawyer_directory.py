"""
Lawyer Directory Module - Template System
NOTE: This uses sample data for demonstration. In production, connect to a real lawyer database.
"""

from typing import List, Dict, Optional
import random

class LawyerDirectory:
    def __init__(self):
        # SAMPLE DATA - Replace with real database in production
        self.lawyers_database = {
            "lahore": [
                {
                    "name": "Advocate Muhammad Ahmad Khan",
                    "specialization": "Criminal Law",
                    "experience": "15 years",
                    "email": "ahmad.khan@example.com",
                    "phone": "+92-42-1234567",
                    "bar_council": "Punjab Bar Council",
                    "address": "Mall Road, Lahore",
                    "rating": 4.5
                },
                {
                    "name": "Ms. Fatima Sheikh",
                    "specialization": "Family Law",
                    "experience": "12 years",
                    "email": "fatima.sheikh@example.com",
                    "phone": "+92-42-2345678",
                    "bar_council": "Punjab Bar Council",
                    "address": "Gulberg, Lahore",
                    "rating": 4.7
                },
                {
                    "name": "Advocate Ali Hassan",
                    "specialization": "Civil Law",
                    "experience": "18 years",
                    "email": "ali.hassan@example.com",
                    "phone": "+92-42-3456789",
                    "bar_council": "Punjab Bar Council",
                    "address": "Model Town, Lahore",
                    "rating": 4.6
                },
                {
                    "name": "Barrister Sarah Khan",
                    "specialization": "Corporate Law",
                    "experience": "10 years",
                    "email": "sarah.khan@example.com",
                    "phone": "+92-42-4567890",
                    "bar_council": "Punjab Bar Council",
                    "address": "DHA, Lahore",
                    "rating": 4.8
                },
                {
                    "name": "Advocate Usman Malik",
                    "specialization": "Constitutional Law",
                    "experience": "20 years",
                    "email": "usman.malik@example.com",
                    "phone": "+92-42-5678901",
                    "bar_council": "Punjab Bar Council",
                    "address": "Johar Town, Lahore",
                    "rating": 4.9
                }
            ],
            "karachi": [
                {
                    "name": "Advocate Imran Ahmed",
                    "specialization": "Criminal Law",
                    "experience": "16 years",
                    "email": "imran.ahmed@example.com",
                    "phone": "+92-21-1234567",
                    "bar_council": "Sindh Bar Council",
                    "address": "Clifton, Karachi",
                    "rating": 4.6
                },
                {
                    "name": "Ms. Aisha Siddiqui",
                    "specialization": "Family Law",
                    "experience": "14 years",
                    "email": "aisha.siddiqui@example.com",
                    "phone": "+92-21-2345678",
                    "bar_council": "Sindh Bar Council",
                    "address": "Defence, Karachi",
                    "rating": 4.5
                },
                {
                    "name": "Advocate Tariq Hussain",
                    "specialization": "Commercial Law",
                    "experience": "22 years",
                    "email": "tariq.hussain@example.com",
                    "phone": "+92-21-3456789",
                    "bar_council": "Sindh Bar Council",
                    "address": "I.I. Chundrigar Road, Karachi",
                    "rating": 4.8
                },
                {
                    "name": "Barrister Zara Ali",
                    "specialization": "Corporate Law",
                    "experience": "11 years",
                    "email": "zara.ali@example.com",
                    "phone": "+92-21-4567890",
                    "bar_council": "Sindh Bar Council",
                    "address": "Gulshan, Karachi",
                    "rating": 4.7
                },
                {
                    "name": "Advocate Bilal Shah",
                    "specialization": "Civil Law",
                    "experience": "19 years",
                    "email": "bilal.shah@example.com",
                    "phone": "+92-21-5678901",
                    "bar_council": "Sindh Bar Council",
                    "address": "Saddar, Karachi",
                    "rating": 4.4
                }
            ],
            "islamabad": [
                {
                    "name": "Advocate Kamran Malik",
                    "specialization": "Constitutional Law",
                    "experience": "25 years",
                    "email": "kamran.malik@example.com",
                    "phone": "+92-51-1234567",
                    "bar_council": "Islamabad Bar Council",
                    "address": "Blue Area, Islamabad",
                    "rating": 4.9
                },
                {
                    "name": "Ms. Hina Javed",
                    "specialization": "Criminal Law",
                    "experience": "13 years",
                    "email": "hina.javed@example.com",
                    "phone": "+92-51-2345678",
                    "bar_council": "Islamabad Bar Council",
                    "address": "F-8, Islamabad",
                    "rating": 4.6
                },
                {
                    "name": "Advocate Waqar Ahmad",
                    "specialization": "Corporate Law",
                    "experience": "17 years",
                    "email": "waqar.ahmad@example.com",
                    "phone": "+92-51-3456789",
                    "bar_council": "Islamabad Bar Council",
                    "address": "G-9, Islamabad",
                    "rating": 4.7
                },
                {
                    "name": "Barrister Ayesha Khan",
                    "specialization": "Family Law",
                    "experience": "12 years",
                    "email": "ayesha.khan@example.com",
                    "phone": "+92-51-4567890",
                    "bar_council": "Islamabad Bar Council",
                    "address": "F-10, Islamabad",
                    "rating": 4.8
                },
                {
                    "name": "Advocate Shahid Iqbal",
                    "specialization": "Civil Law",
                    "experience": "21 years",
                    "email": "shahid.iqbal@example.com",
                    "phone": "+92-51-5678901",
                    "bar_council": "Islamabad Bar Council",
                    "address": "G-11, Islamabad",
                    "rating": 4.5
                }
            ],
            "gujranwala": [
                {
                    "name": "Advocate Muhammad Akbar",
                    "specialization": "Criminal Law",
                    "experience": "14 years",
                    "email": "m.akbar@example.com",
                    "phone": "+92-55-1234567",
                    "bar_council": "Gujranwala Bar Association",
                    "address": "Civil Lines, Gujranwala",
                    "rating": 4.4
                },
                {
                    "name": "Ms. Nadia Butt",
                    "specialization": "Family Law",
                    "experience": "9 years",
                    "email": "nadia.butt@example.com",
                    "phone": "+92-55-2345678",
                    "bar_council": "Gujranwala Bar Association",
                    "address": "Model Town, Gujranwala",
                    "rating": 4.3
                },
                {
                    "name": "Advocate Rashid Ali",
                    "specialization": "Civil Law",
                    "experience": "16 years",
                    "email": "rashid.ali@example.com",
                    "phone": "+92-55-3456789",
                    "bar_council": "Gujranwala Bar Association",
                    "address": "Satellite Town, Gujranwala",
                    "rating": 4.5
                },
                {
                    "name": "Advocate Saba Malik",
                    "specialization": "Commercial Law",
                    "experience": "11 years",
                    "email": "saba.malik@example.com",
                    "phone": "+92-55-4567890",
                    "bar_council": "Gujranwala Bar Association",
                    "address": "Peoples Colony, Gujranwala",
                    "rating": 4.2
                },
                {
                    "name": "Advocate Zaheer Abbas",
                    "specialization": "Property Law",
                    "experience": "18 years",
                    "email": "zaheer.abbas@example.com",
                    "phone": "+92-55-5678901",
                    "bar_council": "Gujranwala Bar Association",
                    "address": "Rahwali, Gujranwala",
                    "rating": 4.6
                }
            ],
            "multan": [
                {
                    "name": "Advocate Hassan Raza",
                    "specialization": "Criminal Law",
                    "experience": "15 years",
                    "email": "hassan.raza@example.com",
                    "phone": "+92-61-1234567",
                    "bar_council": "Multan Bar Association",
                    "address": "Cantt, Multan",
                    "rating": 4.5
                },
                {
                    "name": "Ms. Farah Sheikh",
                    "specialization": "Family Law",
                    "experience": "10 years",
                    "email": "farah.sheikh@example.com",
                    "phone": "+92-61-2345678",
                    "bar_council": "Multan Bar Association",
                    "address": "Gulgasht Colony, Multan",
                    "rating": 4.4
                },
                {
                    "name": "Advocate Omar Farooq",
                    "specialization": "Civil Law",
                    "experience": "20 years",
                    "email": "omar.farooq@example.com",
                    "phone": "+92-61-3456789",
                    "bar_council": "Multan Bar Association",
                    "address": "New Multan, Multan",
                    "rating": 4.7
                },
                {
                    "name": "Barrister Amna Khan",
                    "specialization": "Corporate Law",
                    "experience": "8 years",
                    "email": "amna.khan@example.com",
                    "phone": "+92-61-4567890",
                    "bar_council": "Multan Bar Association",
                    "address": "Shah Rukn-e-Alam Colony, Multan",
                    "rating": 4.3
                },
                {
                    "name": "Advocate Junaid Ahmad",
                    "specialization": "Commercial Law",
                    "experience": "13 years",
                    "email": "junaid.ahmad@example.com",
                    "phone": "+92-61-5678901",
                    "bar_council": "Multan Bar Association",
                    "address": "Hussain Agahi, Multan",
                    "rating": 4.6
                }
            ]
        }
        
        # All supported cities
        self.supported_cities = list(self.lawyers_database.keys())
    
    def get_lawyers_by_city(self, city: str, specialization: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get lawyers from a specific city"""
        city_lower = city.lower()
        
        if city_lower not in self.lawyers_database:
            return []
        
        lawyers = self.lawyers_database[city_lower].copy()
        
        # Filter by specialization if provided
        if specialization:
            spec_lower = specialization.lower()
            lawyers = [l for l in lawyers if spec_lower in l['specialization'].lower()]
        
        # Sort by rating (highest first)
        lawyers.sort(key=lambda x: x['rating'], reverse=True)
        
        return lawyers[:limit]
    
    def search_lawyers(self, query: str) -> str:
        """Process lawyer search query"""
        query_lower = query.lower()
        
        # Extract city from query
        detected_city = None
        for city in self.supported_cities:
            if city in query_lower:
                detected_city = city
                break
        
        # Extract specialization from query
        detected_specialization = None
        specializations = ["criminal", "civil", "family", "commercial", "corporate", "constitutional", "property"]
        for spec in specializations:
            if spec in query_lower:
                detected_specialization = spec
                break
        
        if not detected_city:
            return self._ask_for_city()
        
        lawyers = self.get_lawyers_by_city(detected_city, detected_specialization)
        
        if not lawyers:
            return f"Sorry, I don't have lawyer information for {detected_city.title()} city yet."
        
        return self._format_lawyer_list(lawyers, detected_city.title(), detected_specialization)
    
    def _ask_for_city(self) -> str:
        """Ask user to specify city"""
        cities_list = ", ".join([city.title() for city in self.supported_cities])
        return f"Please specify which city you're looking for lawyers in. I have lawyer information for: {cities_list}\\n\\nJust tell me your city and I'll find qualified lawyers for you!"
    
    def _format_lawyer_list(self, lawyers: List[Dict], city: str, specialization: Optional[str] = None) -> str:
        """Format lawyer list for display"""
        if specialization:
            header = f"**{specialization.title()} Lawyers in {city}:**"
        else:
            header = f"**Qualified Lawyers in {city}:**"
        
        response = header + "\\n\\n"
        
        for i, lawyer in enumerate(lawyers, 1):
            response += f"**{i}. {lawyer['name']}**\\n"
            response += f"📚 **Specialization:** {lawyer['specialization']}\\n"
            response += f"⭐ **Experience:** {lawyer['experience']} | **Rating:** {lawyer['rating']}/5.0\\n"
            response += f"📧 **Email:** {lawyer['email']}\\n"
            response += f"📞 **Phone:** {lawyer['phone']}\\n"
            response += f"🏛️ **Bar Council:** {lawyer['bar_council']}\\n"
            response += f"📍 **Address:** {lawyer['address']}\\n"
            response += "---\\n"
        
        response += "\\n**Note:** These are qualified lawyers registered with their respective Bar Councils. Please verify credentials and discuss fees before proceeding."
        
        return response
    
    def get_supported_cities(self) -> List[str]:
        """Get list of supported cities"""
        return [city.title() for city in self.supported_cities]

# Integration function for the main API
def handle_lawyer_search_query(query: str) -> Optional[str]:
    """Check if query is asking for lawyers and handle it"""
    query_lower = query.lower()
    
    lawyer_keywords = [
        "lawyer", "advocate", "attorney", "legal help", "legal representation",
        "wakeel", "qanooni madad", "lawyer chahiye", "advocate chahiye"
    ]
    
    if any(keyword in query_lower for keyword in lawyer_keywords):
        directory = LawyerDirectory()
        return directory.search_lawyers(query)
    
    return None

if __name__ == "__main__":
    # Test the system
    directory = LawyerDirectory()
    
    test_queries = [
        "I need a lawyer in Lahore",
        "Find me a criminal lawyer in Karachi",
        "Family lawyer in Islamabad",
        "Lawyers in Gujranwala",
        "Commercial lawyer in Multan",
        "I need legal help"  # Should ask for city
    ]
    
    for query in test_queries:
        print(f"Query: {query}")
        print(directory.search_lawyers(query))
        print("\\n" + "="*50 + "\\n")
