from pymongo import AsyncMongoClient
from app.core.settings import settings

client = AsyncMongoClient(settings.MONGODB_URI)
db = client.get_database(settings.MONGODB_DB)
