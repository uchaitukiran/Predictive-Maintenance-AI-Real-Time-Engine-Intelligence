import os
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from src.rag.config import PINECONE_API_KEY, INDEX_NAME

# Load Env
load_dotenv()

# 1. Setup Embeddings
print("Loading Embedding Model...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 2. Connect to Pinecone
print("Connecting to Pinecone Index...")
vector_store = PineconeVectorStore(
    index_name=INDEX_NAME,
    embedding=embeddings,
    pinecone_api_key=PINECONE_API_KEY
)

# 3. Setup LLM
GROQ_KEY = os.getenv("GROQ_API_KEY")  # <--- MAKE SURE THIS LINE EXISTS

llm = ChatGroq(
    groq_api_key=GROQ_KEY,
    model_name="llama-3.1-8b-instant",
    temperature=0.0,
    max_tokens=150
)
# 4. Setup Prompt
prompt = ChatPromptTemplate.from_template(
    """Answer the question based on the context below. Be concise.

Context:
{context}

Question: {input}"""
)

# 5. Setup Retriever
retriever = vector_store.as_retriever(search_kwargs={"k": 1}) # Reduced k=2 for speed

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# --- OPTIMIZATION: Define Chain Globally ---
def prepare_context(inputs):
    query = inputs["input"]
    live_context = inputs.get("live_context")
    
    # A. Retrieve from PDFs
    docs = retriever.invoke(query)
    context_text = format_docs(docs)
    
    # B. Inject Live Data
    if live_context:
        live_data_str = f"""
        CURRENT STATUS: {live_context.get('state')} | RUL: {live_context.get('rul'):.0f} | Temp: {live_context.get('temperature'):.0f} | Pres: {live_context.get('pressure'):.0f} | Vib: {live_context.get('vibration'):.0f}
        """
        context_text = live_data_str + "\n" + context_text
    
    return {"context": context_text, "input": query}

# Build the chain ONCE
rag_chain = (
    RunnableLambda(prepare_context)  # 1. Get Context (PDF + Live)
    | prompt                         # 2. Format Prompt
    | llm                            # 3. Send to Groq
    | StrOutputParser()              # 4. Parse Output
)

def ask_question(query, live_context=None):
    """
    Fast invocation.
    """
    print(f"Searching for: {query}")
    
    # Invoke the pre-built chain
    answer = rag_chain.invoke({"input": query, "live_context": live_context})
    
    # Get sources separately (fast)
    docs = retriever.invoke(query)
    sources = list(set([doc.metadata.get("source", "Unknown") for doc in docs]))
            
    return answer, sources