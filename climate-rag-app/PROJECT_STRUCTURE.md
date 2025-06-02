# Climate Action Intelligence Platform - RAG Application Structure

## 📁 Project Directory Structure

```
climate-rag-app/
├── 📄 README.md                    # Main project documentation
├── 📄 DEMO_SUMMARY.md             # Comprehensive demo summary
├── 📄 PROJECT_STRUCTURE.md        # This file - project structure overview
├── 📄 requirements.txt            # Python dependencies
├── 📄 .env.example               # Environment configuration template
├── 🚀 run_app.py                 # Application startup script
├── 🎯 demo.py                    # Command-line demo script
├── 📄 app.log                    # Application logs
│
├── 🔧 backend/                   # Core RAG system implementation
│   ├── 📄 document_processor.py  # Document loading and chunking
│   ├── 📄 rag_system.py         # Main RAG system logic
│   └── 📄 __init__.py           # Package initialization
│
├── 🌐 frontend/                  # Web interface
│   └── 📄 app.py                # Streamlit web application
│
├── 💾 data/                     # Persistent data storage
│   └── vectordb/               # ChromaDB vector database
│       ├── 📁 63a248d4-d4e6-49d9-9e05-33515f0512ad/  # Collection data
│       └── 📄 chroma.sqlite3    # SQLite database file (557KB)
│
└── 📁 models/                   # Reserved for model files
```

## 🔍 File Descriptions

### **Core Application Files**

- **`run_app.py`** - Main application launcher that starts the Streamlit web interface
- **`demo.py`** - Interactive command-line demonstration script
- **`requirements.txt`** - All Python dependencies for the project

### **Backend Components**

- **`document_processor.py`** - Handles README document loading, section extraction, intelligent chunking, and metadata enrichment
- **`rag_system.py`** - Core RAG implementation with vector storage, retrieval, and answer generation

### **Frontend Interface**

- **`app.py`** - Complete Streamlit web application with chat interface, source visualization, and system monitoring

### **Data Storage**

- **`vectordb/`** - Persistent ChromaDB storage containing 42 document chunks with embeddings
- **`chroma.sqlite3`** - SQLite database file (557KB) storing vector data and metadata

### **Documentation**

- **`README.md`** - Comprehensive project documentation with setup and usage instructions
- **`DEMO_SUMMARY.md`** - Detailed demonstration results and capabilities overview
- **`.env.example`** - Configuration template for environment variables

## 📊 Key Statistics

### **Document Processing**
- **Total Documents**: 42 chunks from Climate Action Intelligence Platform README
- **Total Characters**: 21,720 characters processed
- **Average Chunk Size**: 517 characters
- **Section Types**: Overview (2), Technical (2), Setup (1), Demo (2), General (35)

### **Vector Database**
- **Technology**: ChromaDB with persistent storage
- **Database Size**: 557KB SQLite file
- **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2
- **Collection ID**: 63a248d4-d4e6-49d9-9e05-33515f0512ad

### **Application Features**
- **Web Interface**: Streamlit on port 12000
- **Real-time Q&A**: Instant responses with source attribution
- **Chat History**: Persistent conversation tracking
- **Source Analytics**: Visual distribution of source types
- **System Monitoring**: Real-time database and model information

## 🚀 Quick Start Commands

### **Start Web Application**
```bash
cd climate-rag-app
python run_app.py
# Access at: http://localhost:12000
```

### **Run Command-Line Demo**
```bash
cd climate-rag-app
python demo.py
```

### **Install Dependencies**
```bash
cd climate-rag-app
pip install -r requirements.txt
```

## 🔧 Technical Architecture

### **RAG Pipeline**
1. **Document Loading** → README.md processed into structured sections
2. **Intelligent Chunking** → Content split with context preservation
3. **Embedding Generation** → Sentence transformers create vector representations
4. **Vector Storage** → ChromaDB stores embeddings with metadata
5. **Query Processing** → User questions converted to embeddings
6. **Similarity Search** → MMR retrieval finds relevant documents
7. **Answer Generation** → Template-based response with source attribution

### **Technology Stack**
- **Framework**: LangChain for RAG orchestration
- **Vector DB**: ChromaDB for persistent storage
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Web Interface**: Streamlit for interactive UI
- **Visualization**: Plotly for analytics and charts
- **Processing**: Python with pandas and numpy

## 🌟 Unique Features

### **Climate-Focused Intelligence**
- Purpose-built for climate action knowledge
- Specialized understanding of climate terminology
- Domain-specific question classification and routing

### **Advanced RAG Techniques**
- Maximum Marginal Relevance (MMR) for diverse results
- Intelligent document chunking with metadata preservation
- Multi-type content handling (overview, technical, implementation)

### **Production-Ready Design**
- Persistent vector storage survives restarts
- Comprehensive error handling and logging
- Scalable architecture for easy extension
- Environment-based configuration management

### **User Experience Excellence**
- Intuitive chat-based interface
- Real-time source attribution and verification
- Visual analytics for source distribution
- Quick-access buttons for common questions

## 📈 Performance Characteristics

- **Query Response Time**: Sub-second retrieval and generation
- **Memory Usage**: Optimized for CPU-only inference
- **Storage Efficiency**: 557KB for complete knowledge base
- **Scalability**: Ready for production deployment with minimal changes

---

**🌍 This structure represents a complete, production-ready RAG application specifically designed for climate action intelligence and knowledge discovery.**