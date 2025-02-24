from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

# MongoDB configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://mongodb:27017')
DB_NAME = os.getenv('DB_NAME', 'invoice_processor')

# Initialize MongoDB client
client = MongoClient(MONGO_URI)
db = client[DB_NAME] 