import os
from dotenv import load_dotenv
import requests

load_dotenv()
key = os.getenv('GROQ_API_KEY')
r = requests.get('https://api.groq.com/openai/v1/models', headers={'Authorization': f'Bearer {key}'})
data = r.json()
print([m['id'] for m in data.get('data', [])])
