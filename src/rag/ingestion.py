import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from src.rag.config import PINECONE_API_KEY, INDEX_NAME

# 1. Setup Pinecone Connection
print("Connecting to Pinecone...")
pc = Pinecone(api_key=PINECONE_API_KEY)
# We don't need to initialize index object manually, PineconeVectorStore handles it

# 2. Setup Embedding Model (Free & Local)
print("Loading Embedding Model...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 3. Define Knowledge Base Path
KB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../knowledge_base"))

def ingest_data():
    documents = []
    
    print(f"Reading files from: {KB_PATH}")
    
    # Load all PDFs and TXTs
    for file in os.listdir(KB_PATH):
        file_path = os.path.join(KB_PATH, file)
        
        if file.endswith(".pdf"):
            print(f"Loading PDF: {file}")
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())
            
        elif file.endswith(".txt"):
            print(f"Loading Text: {file}")
            loader = TextLoader(file_path)
            documents.extend(loader.load())

    if not documents:
        print("⚠️ No documents found!")
        return

    print(f"Total documents loaded: {len(documents)}")

    # 4. Split Text into Chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(documents)
    print(f"Split into {len(splits)} chunks.")

    # 5. Upload to Pinecone
    print("Uploading to Pinecone... (This may take a minute)")
    
    # This automatically creates embeddings and uploads
    PineconeVectorStore.from_documents(
        documents=splits,
        embedding=embeddings,
        index_name=INDEX_NAME,
        pinecone_api_key=PINECONE_API_KEY
    )
    
    print("✅ SUCCESS: Data uploaded to Pinecone!")

if __name__ == "__main__":
    ingest_data()