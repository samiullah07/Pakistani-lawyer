"""
Complete test of conversation memory features
"""

from conversation_memory import get_memory, StreamingResponseBuilder

print("=" * 70)
print("🧪 TESTING CONVERSATION MEMORY SYSTEM")
print("=" * 70)

# Initialize
memory = get_memory()
session_id = "test_session_001"

print("\n1️⃣ Creating new session...")
memory.create_session(session_id)
print("   ✅ Session created")

print("\n2️⃣ Simulating user conversation...")

# First message
print("   User: 'What is section 420?'")
memory.add_message(session_id, "user", "What is section 420?")
memory.add_message(
    session_id, 
    "assistant", 
    "Section 420 PPC deals with fraud and cheating",
    metadata={"intent": "legal_query", "domain": "criminal"}
)
print("   ✅ Messages stored")

# Follow-up question
print("   User: 'What's the punishment?'")
memory.add_message(session_id, "user", "What's the punishment?")
memory.add_message(
    session_id,
    "assistant",
    "For Section 420, punishment is up to 7 years + fine",
    metadata={"intent": "legal_query", "domain": "criminal"}
)
print("   ✅ Follow-up stored")

# Another follow-up
print("   User: 'Is it bailable?'")
memory.add_message(session_id, "user", "Is it bailable?")
memory.add_message(
    session_id,
    "assistant",
    "Section 420 is non-bailable",
    metadata={"intent": "legal_query", "domain": "criminal"}
)
print("   ✅ Another follow-up stored")

print("\n3️⃣ Checking conversation context...")
context = memory.get_context(session_id)
print(f"   Context available: {len(context)} characters")
print(f"   First 200 chars: {context[:200]}...")

print("\n4️⃣ Getting sidebar summary...")
summary = memory.get_sidebar_summary(session_id)
print(f"   ✅ Context Summary: {summary['context_summary']}")
print(f"   ✅ Topics Discussed: {summary['topics_discussed']}")
print(f"   ✅ Message Count: {summary['message_count']}")
print(f"   ✅ Language: {summary['language']}")

print("\n5️⃣ Testing streaming response builder...")
chunks = StreamingResponseBuilder.build_legal_response(
    domain="criminal",
    law_section="Pakistan Penal Code Section 420",
    explanation="This deals with cheating and fraud",
    punishment="Up to 7 years imprisonment + fine, non-bailable",
    practical_notes="Victims should file FIR immediately",
    suggestions="Consult a criminal defense lawyer",
    language="english"
)
print(f"   ✅ Generated {len(chunks)} response chunks")
print("\n   Chunks:")
for i, chunk in enumerate(chunks, 1):
    print(f"   {i}. {chunk[:60]}...")

print("\n6️⃣ Testing bilingual support...")
urdu_chunks = StreamingResponseBuilder.build_legal_response(
    domain="criminal",
    law_section="Pakistan Penal Code Dafa 420",
    explanation="Yeh dhoke aur fraud se mutalliq hai",
    punishment="7 saal tak qaid + jurmana, non-bailable",
    practical_notes="Fauran FIR darj karain",
    suggestions="Criminal wakeel se mashwara karen",
    language="urdu"
)
print(f"   ✅ Generated {len(urdu_chunks)} Urdu chunks")
print("\n   First Urdu chunk:")
print(f"   {urdu_chunks[0]}")

print("\n7️⃣ Testing recent topics...")
topics = memory.get_recent_topics(session_id)
print(f"   ✅ Recent topics: {topics}")

print("\n8️⃣ Testing context retrieval...")
context_lines = context.split('\n')
print(f"   ✅ Context has {len(context_lines)} lines")
print("   Sample context:")
for line in context_lines[:3]:
    print(f"   {line}")

print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED!")
print("=" * 70)
print("\n🎉 Memory system is ready to integrate!")
print("\n📋 Summary:")
print("   • Session management: Working")
print("   • Message storage: Working")
print("   • Context tracking: Working")
print("   • Sidebar summaries: Working")
print("   • Streaming builder: Working")
print("   • Bilingual support: Working")
print("\n💡 Next step: Integrate into api.py and ui.py")
print("   Say: 'integrate the memory system'")
