import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
EXCHANGE_API_KEY = os.getenv('EXCHANGE_API_KEY')
