import os
from dotenv import load_dotenv
            
load_dotenv()

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
            # cls._instance.MONGODB_URL = os.getenv("MONGODB_URL")
            # cls._instance.DATABASE_NAME = os.getenv("DATABASE_NAME")
            # cls._instance.COLLECTION_NAME = os.getenv("COLLECTION_NAME")
            # cls._instance.SESSION_COLLECTION_NAME = os.getenv("SESSION_COLLECTION_NAME")

        return cls._instance