# Workflow Documentation: OpenRouter RAG Chatbot System

## Overview

This document explains the complete workflow for implementing and using the OpenRouter RAG Chatbot system, from setup to operation. This workflow is designed to create a chatbot that can answer questions based on your own documents using Retrieval-Augmented Generation (RAG) technology without any OpenAI dependencies.

## System Architecture

![RAG Chatbot Architecture](https://i.imgur.com/placeholder.png)

The system uses the following components:
- **Document Processing**: Ingests PDF documents and splits them into chunks
- **Embedding Generation**: Creates vector embeddings using HuggingFace's sentence-transformers
- **Vector Database**: Stores document chunks and embeddings in ChromaDB
- **Retrieval System**: Identifies relevant document chunks for each query
- **Language Model**: Generates answers via OpenRouter's API gateway
- **User Interface**: Presents an interactive chatbot using Gradio

## Complete Workflow

### Phase 1: Setup and Installation

1. **Environment Preparation**:
   - Clone the repository
   - Create and activate a Python virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
   - Install required packages
   ```bash
   pip install -r requirements.txt
   ```

2. **API Configuration**:
   - Register for an OpenRouter account at [openrouter.ai](https://openrouter.ai)
   - Generate an API key from your OpenRouter dashboard
   - Copy `.env.example` to `.env`
   - Add your OpenRouter API key to the `.env` file
   ```
   OPENROUTER_API_KEY=your_api_key_here
   OPENROUTER_MODEL=openai/gpt-4o-mini  # Or your preferred model
   ```

### Phase 2: Document Ingestion

1. **Prepare Your Documents**:
   - Place PDF documents in the `data` folder
   - Ensure documents are readable and not password-protected

2. **Run Document Ingestion**:
   - Execute the ingestion script
   ```bash
   python ingest_database.py
   ```
   - This process:
     * Loads all PDFs from the data directory
     * Splits documents into manageable chunks (300 characters with 100 character overlap)
     * Generates embeddings for each chunk using HuggingFace's sentence-transformers model
     * Stores chunks and embeddings in ChromaDB
     * Creates a persistent database in the `chroma_db` directory

### Phase 3: Running the Chatbot

1. **Launch the Application**:
   ```bash
   python chatbot.py
   ```

2. **Access the Interface**:
   - Open your web browser to the URL shown in the terminal (typically http://127.0.0.1:7860)
   - You'll see the chatbot interface ready to answer questions

### Phase 4: Chatbot Operation Flow

For each user interaction, the system follows this workflow:

1. **Query Processing**:
   - User enters a question in the interface
   - The query is sent to the retrieval system

2. **Document Retrieval**:
   - The system converts the user's question into an embedding vector
   - It searches ChromaDB for the most relevant document chunks (top 5 by default)
   - Relevant document chunks are extracted and combined

3. **Response Generation**:
   - The system creates a prompt combining:
     * The user's question
     * Conversation history
     * Retrieved document chunks
   - This prompt is sent to the LLM via OpenRouter API
   - The response is streamed back to the interface in real-time

4. **User Interaction**:
   - The user receives the answer based on their documents
   - The conversation history is maintained for context in further questions
   - The user can continue asking follow-up questions

## Technical Workflow Details

### Embedding Generation Process

```
User Query → HuggingFace Embedding Model → Vector Representation
↓
Document Chunks → HuggingFace Embedding Model → Vector Representations in DB
↓
Vector Similarity Search → Top 5 Most Relevant Chunks
```

### Response Generation Process

```
User Query + Retrieved Chunks + Chat History → RAG Prompt Construction
↓
OpenRouter API Request (with streaming enabled)
↓
LLM Processes Prompt and Generates Response
↓
Streamed Response Displayed to User
```

### Underlying Components Interaction

1. **Vector Store Interaction**:
   - ChromaDB uses a local persistent database to store embeddings
   - Similarity search uses cosine similarity by default
   - Results are ranked by relevance score

2. **LLM Integration**:
   - Custom OpenRouterChatModel class handles API communication
   - Streaming implementation processes SSE (Server-Sent Events) data
   - Error handling catches and displays any API issues

## Common Workflow Scenarios

### Adding New Documents

1. Place new PDF files in the `data` folder
2. Re-run the ingestion script:
   ```bash
   python ingest_database.py
   ```
3. The vector database will be updated with the new content
4. Restart the chatbot application to use the updated database

### Changing LLM Model

1. Edit your `.env` file to specify a different model:
   ```
   OPENROUTER_MODEL=anthropic/claude-3-opus-20240229
   ```
2. Restart the chatbot application to use the new model
3. No changes to the vector database are needed

### Troubleshooting Workflow

If you encounter issues:

1. **Connection Problems**:
   - Check your internet connection
   - Verify your OpenRouter API key is correct
   - Ensure OpenRouter service is operational

2. **Document Retrieval Issues**:
   - Check if the `chroma_db` directory exists and contains data
   - Verify documents were properly added to the `data` folder
   - Try re-running the ingest script

3. **Model Response Problems**:
   - Check for any error messages in the terminal
   - Try a different model in your `.env` file
   - Verify your OpenRouter account has sufficient credits

## Performance Optimization Workflow

For larger document collections:

1. **Embedding Optimization**:
   - Adjust chunk size in `ingest_database.py` (larger chunks = fewer vectors)
   ```python
   chunk_size=500,  # Increased from 300
   chunk_overlap=150,  # Increased from 100
   ```

2. **Retrieval Optimization**:
   - Adjust the number of retrieved chunks in `chatbot.py`:
   ```python
   num_results = 3  # Decreased from 5 for more focused responses
   ```

3. **Interface Optimization**:
   - For public deployments, add IP access restrictions:
   ```python
   demo.launch(share=False, server_name="0.0.0.0", server_port=7860)
   ```

## Extending the Workflow

### Adding Support for More Document Types

1. Replace the PyPDFDirectoryLoader with appropriate loaders:
   ```python
   # For DOCX files
   from langchain_community.document_loaders import DirectoryLoader
   from langchain_community.document_loaders import UnstructuredWordDocumentLoader
   
   loader = DirectoryLoader(DATA_PATH, glob="*.docx", loader_cls=UnstructuredWordDocumentLoader)
   ```

2. Run the modified ingest script to process the new document types

### Implementing User Authentication

1. Add Gradio authentication to `chatbot.py`:
   ```python
   demo.launch(auth=("username", "password"))
   ```

2. For more complex authentication, integrate with a proper authentication system

## Conclusion

This workflow provides a complete pipeline for creating a document-based chatbot system without dependency on OpenAI services. By following these steps, you can create, customize, and deploy a RAG-powered chatbot that can answer questions based on your own document collection.
