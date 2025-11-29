import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv('GROQ_API_KEY')
print(f"API Key loaded: '{api_key}'")
print(f"Length: {len(api_key) if api_key else 0}")
print(f"Starts with gsk_: {api_key.startswith('gsk_') if api_key else False}")


try:
    client = Groq(api_key=api_key.strip())
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # ← UPDATED MODEL
        messages=[{"role": "user", "content": "Say 'API key works!'"}],
        max_tokens=10
    )
    print("✅ SUCCESS! API key is valid!")
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ ERROR: {e}")