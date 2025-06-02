# Climate Action Intelligence Platform - RAG Application

🌍 **An AI-powered Retrieval-Augmented Generation (RAG) system for answering questions about the ClimateIQ project.**

## Overview

This RAG application provides an intelligent question-answering interface for the Climate Action Intelligence Platform project. It uses advanced document processing, vector embeddings, and retrieval techniques to answer questions based on the comprehensive project documentation.

## Features

- 🤖 **Intelligent RAG System**: Advanced retrieval-augmented generation using LangChain and ChromaDB
- 📚 **Comprehensive Knowledge Base**: Built from detailed ClimateIQ project documentation
- 🔍 **Smart Document Retrieval**: Context-aware document chunking and similarity search
- 💬 **Interactive Chat Interface**: User-friendly Streamlit web interface
- 📊 **Source Transparency**: Clear attribution and source tracking for all answers
- 🔧 **Scalable Architecture**: Production-ready components with persistent vector storage

## Architecture

```
climate-rag-app/
├── backend/
│   ├── document_processor.py    # Document loading and chunking
│   ├── rag_system.py           # Core RAG implementation
│   └── __init__.py
├── frontend/
│   └── app.py                  # Streamlit web interface
├── data/
│   └── vectordb/              # Persistent vector database
├── requirements.txt           # Python dependencies
├── run_app.py                # Application startup script
└── README.md                 # This file
```

## Quick Start

### 1. Install Dependencies

```bash
cd climate-rag-app
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python run_app.py
```

The application will be available at: http://localhost:12000

### 3. Ask Questions

Use the web interface to ask questions about the ClimateIQ project, such as:
- "What is ClimateIQ?"
- "How does the RAG system work?"
- "What are the technical components?"
- "How to implement the platform?"
- "What are the competitive advantages?"

## Technical Details

### Document Processing

The system processes the ClimateIQ README document by:
1. **Section Extraction**: Automatically identifies and extracts document sections
2. **Smart Chunking**: Breaks down large sections while preserving context
3. **Metadata Enrichment**: Adds section types, titles, and other metadata
4. **Document Classification**: Categorizes content by type (overview, technical, setup, etc.)

### Vector Storage

- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Vector Database**: ChromaDB with persistent storage
- **Retrieval Strategy**: Maximum Marginal Relevance (MMR) for diverse results
- **Search Parameters**: Configurable k-value for number of retrieved documents

### Answer Generation

The system uses a template-based approach to generate answers:
- **Query Classification**: Identifies question types (what, how, why, technical)
- **Context Assembly**: Combines relevant document chunks
- **Response Generation**: Creates structured answers with source attribution
- **Source Tracking**: Maintains transparency about information sources

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
# Vector Database Configuration
PERSIST_DIRECTORY=./data/vectordb
COLLECTION_NAME=climate_docs

# Embedding Model Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Document Processing Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### Customization Options

- **Chunk Size**: Adjust document chunk size for different granularity
- **Retrieval Count**: Modify number of documents retrieved per query
- **Embedding Model**: Switch to different sentence transformer models
- **Search Strategy**: Configure retrieval algorithms (similarity, MMR, etc.)

## API Usage

### Programmatic Access

```python
from backend.rag_system import ClimateRAGSystem

# Initialize RAG system
rag = ClimateRAGSystem()
rag.initialize_vectorstore()

# Ask a question
result = rag.ask_question("What is ClimateIQ?")
print(result['answer'])
print(f"Sources: {result['num_sources']}")
```

### Document Statistics

```python
from backend.document_processor import ClimateDocumentProcessor

processor = ClimateDocumentProcessor()
documents = processor.create_documents("path/to/README.md")
stats = processor.get_document_stats(documents)
print(stats)
```

## Performance

- **Document Processing**: ~42 documents from README
- **Vector Storage**: Persistent ChromaDB with ~21K characters
- **Query Response**: Sub-second retrieval and generation
- **Memory Usage**: Optimized for CPU-only inference

## Deployment

### Local Development

```bash
python run_app.py
```

### Production Deployment

1. **Docker**: Create containerized deployment
2. **Cloud**: Deploy to cloud platforms (AWS, GCP, Azure)
3. **Scaling**: Use vector database clusters for large-scale deployment

### Docker Example

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["python", "run_app.py"]
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Vector DB Issues**: Delete `./data/vectordb` to rebuild
3. **Memory Issues**: Reduce chunk size or use smaller embedding models
4. **Port Conflicts**: Change port in `run_app.py`

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of the Climate Action Intelligence Platform and follows the same licensing terms.

## Acknowledgments

- **LangChain**: For RAG framework and document processing
- **ChromaDB**: For vector storage and similarity search
- **Streamlit**: For the interactive web interface
- **Sentence Transformers**: For text embeddings
- **Climate Action Community**: For inspiration and domain knowledge

---

🌍 **Built for Climate Action** | Powered by AI for a Sustainable Future