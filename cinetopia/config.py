import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Database
DB_NAME = os.getenv('DB_NAME', 'projt_commun')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')

# Weather API
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
WEATHER_API_HOST = os.getenv('WEATHER_API_HOST', 'weatherapi-com.p.rapidapi.com')