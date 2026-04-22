import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Keys (FIXED Typo)
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENVIRONMENT")
INDEX_NAME = "engine-rag"