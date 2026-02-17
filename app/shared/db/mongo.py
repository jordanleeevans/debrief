from pymongo import AsyncMongoClient
from app.shared.core.settings import settings

client = AsyncMongoClient(settings.MONGODB_URI)
db = client.get_database(settings.MONGODB_DB)
