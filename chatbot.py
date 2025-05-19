# gradio_chatbot.py
import gradio as gr
import os
import requests
import json
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Load environment variables
load_dotenv()

# Configuration
CHROMA_PATH = r"chroma_db"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")
MAX_TOKENS = 14000  # Reduced token limit to stay under your account's limit

# Initialize embeddings and retriever
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
db = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings,
    persist_directory=CHROMA_PATH
)
retriever = db.as_retriever(search_kwargs={'k': 3})  # Reduced from 5 to 3 docs

# Simple function to estimate tokens (very approximate)
def estimate_tokens(text):
    # Roughly 4 characters per token for English text
    return len(text) // 4

def respond(message, history):
    try:
        # Get relevant documents
        docs = retriever.invoke(message)
        
        # Combine and limit knowledge to stay under token limits
        knowledge = ""
        total_tokens = 0
        system_prompt = "You answer questions based only on the provided knowledge."
        user_prompt_template = f"Question: {message}\n\nKnowledge: "
        
        # Calculate approximate tokens already used by prompts
        base_tokens = estimate_tokens(system_prompt) + estimate_tokens(user_prompt_template)
        max_knowledge_tokens = MAX_TOKENS - base_tokens - 1000  # Reserve 1000 tokens for model response
        
        for doc in docs:
            doc_content = doc.page_content
            doc_tokens = estimate_tokens(doc_content)
            
            if total_tokens + doc_tokens <= max_knowledge_tokens:
                knowledge += doc_content + "\n\n"
                total_tokens += doc_tokens
            else:
                # If adding this doc would exceed the limit, skip it
                continue
        
        # Format request for OpenRouter with max_tokens parameter
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Question: {message}\n\nKnowledge: {knowledge}"}
            ],
            "max_tokens": 1000  # Limit response tokens
        }
        
        # Get response
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        # Debug info
        print(f"API Response: {response.status_code}")
        
        response_json = response.json()
        
        # Handle error responses
        if "error" in response_json:
            error_msg = response_json["error"]["message"]
            return f"API Error: {error_msg}"
        
        # Handle successful responses
        if "choices" in response_json and len(response_json["choices"]) > 0:
            if "message" in response_json["choices"][0]:
                answer = response_json["choices"][0]["message"]["content"]
                return answer
        
        return f"Could not parse API response properly."
        
    except Exception as e:
        import traceback
        print(f"Error details: {traceback.format_exc()}")
        return f"Error: {str(e)}"

# Create Gradio interface
demo = gr.ChatInterface(
    respond,
    title="RAG-Powered Chatbot",
    description="Ask questions about the documents in the knowledge base",
    theme="default",
    examples=["What is RAG?", "How does the document ingestion work?"]
)

if __name__ == "__main__":
    print(f"Starting RAG Chatbot with model: {MODEL_NAME}")
    print(f"API Key available: {'Yes' if OPENROUTER_API_KEY else 'No'}")
    print(f"Using token limit: {MAX_TOKENS}")
    demo.launch()