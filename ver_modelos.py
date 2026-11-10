import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
from google import genai


client = genai.Client()

print("Modelos disponibles para tu API Key:")
for m in client.models.list():
    print(m.name)