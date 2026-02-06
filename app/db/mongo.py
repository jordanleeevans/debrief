from pymongo import MongoClient
from app.core.settings import settings

client = MongoClient(settings.MONGODB_URI)
db = client[settings.MONGODB_DB]
