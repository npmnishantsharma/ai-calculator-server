from dotenv import load_dotenv
import os
load_dotenv()

SERVER_URL = 'localhost'
PORT = '8900'
ENV = 'dev'
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
SERVER_TYPE = os.getenv("SERVER_TYPE")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
