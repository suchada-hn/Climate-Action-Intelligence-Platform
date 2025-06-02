"""
RAG System for Climate Action Intelligence Platform.
Handles document retrieval and answer generation.
"""

import os
import json
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

from document_processor import ClimateDocumentProcessor


class ClimateRAGSystem:
    """RAG system for answering questions about the Climate Action Intelligence Platform."""
    
    def __init__(self, 
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
                 persist_directory: str = "./data/vectordb",
                 collection_name: str = "climate_docs"):
        
        self.embedding_model_name = embedding_model
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Initialize vector store
        self.vectorstore = None
        self.retriever = None
        
        # Document processor
        self.doc_processor = ClimateDocumentProcessor()
        
        # Create persist directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
    
    def initialize_vectorstore(self, documents: List[Document] = None, force_rebuild: bool = False):
        """Initialize or load the vector store."""
        
        # Check if vectorstore already exists
        vectorstore_exists = os.path.exists(os.path.join(self.persist_directory, "chroma.sqlite3"))
        
        if vectorstore_exists and not force_rebuild:
            print("Loading existing vector store...")
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name=self.collection_name
            )
        else:
            if documents is None:
                # Load documents from README
                readme_path = "/workspace/Climate-Action-Intelligence-Platform/README.md"
                if os.path.exists(readme_path):
                    print("Processing README document...")
                    documents = self.doc_processor.create_documents(readme_path)
                else:
                    raise FileNotFoundError(f"README file not found at {readme_path}")
            
            print(f"Creating new vector store with {len(documents)} documents...")
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=self.persist_directory,
                collection_name=self.collection_name
            )
            self.vectorstore.persist()
        
        # Initialize retriever
        self.retriever = self.vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 5, "fetch_k": 10}
        )
    
    def retrieve_documents(self, query: str, k: int = 5) -> List[Document]:
        """Retrieve relevant documents for a query."""
        if self.retriever is None:
            raise ValueError("Vector store not initialized. Call initialize_vectorstore() first.")
        
        # Update retriever parameters
        self.retriever.search_kwargs["k"] = k
        
        # Retrieve documents
        docs = self.retriever.get_relevant_documents(query)
        return docs
    
    def generate_answer(self, query: str, retrieved_docs: List[Document]) -> str:
        """Generate an answer using retrieved documents (simple template-based approach)."""
        
        # Create context from retrieved documents
        context_parts = []
        for i, doc in enumerate(retrieved_docs):
            section = doc.metadata.get('section', 'Unknown Section')
            content = doc.page_content
            context_parts.append(f"[Source {i+1} - {section}]\n{content}")
        
        context = "\n\n".join(context_parts)
        
        # Simple template-based response generation
        # In a production system, you would use an LLM here
        answer = self._generate_template_answer(query, context, retrieved_docs)
        
        return answer
    
    def _generate_template_answer(self, query: str, context: str, docs: List[Document]) -> str:
        """Generate answer using template-based approach."""
        
        query_lower = query.lower()
        
        # Identify query type and generate appropriate response
        if any(word in query_lower for word in ['what is', 'what are', 'describe', 'explain']):
            return self._generate_descriptive_answer(query, context, docs)
        elif any(word in query_lower for word in ['how to', 'how do', 'steps', 'implement']):
            return self._generate_how_to_answer(query, context, docs)
        elif any(word in query_lower for word in ['why', 'benefits', 'advantages']):
            return self._generate_why_answer(query, context, docs)
        elif any(word in query_lower for word in ['technical', 'architecture', 'components']):
            return self._generate_technical_answer(query, context, docs)
        else:
            return self._generate_general_answer(query, context, docs)
    
    def _generate_descriptive_answer(self, query: str, context: str, docs: List[Document]) -> str:
        """Generate descriptive answer."""
        relevant_sections = [doc.metadata.get('section', '') for doc in docs]
        
        answer = f"Based on the Climate Action Intelligence Platform documentation:\n\n"
        
        # Extract key information from context
        if 'climateiq' in query.lower() or 'platform' in query.lower():
            answer += "ClimateIQ is an AI-powered Climate Action Accelerator that democratizes climate action by providing personalized, data-driven solutions for individuals, businesses, and communities to combat climate change effectively.\n\n"
        
        # Add relevant content from retrieved documents
        for i, doc in enumerate(docs[:3]):  # Limit to top 3 most relevant
            section = doc.metadata.get('section', f'Section {i+1}')
            content = doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content
            answer += f"**{section}:**\n{content}\n\n"
        
        return answer
    
    def _generate_how_to_answer(self, query: str, context: str, docs: List[Document]) -> str:
        """Generate how-to answer."""
        answer = "Here's how to proceed based on the documentation:\n\n"
        
        # Look for implementation steps or phases
        implementation_docs = [doc for doc in docs if 'implementation' in doc.metadata.get('type', '').lower() 
                              or 'phase' in doc.metadata.get('section', '').lower()]
        
        if implementation_docs:
            for i, doc in enumerate(implementation_docs[:3]):
                section = doc.metadata.get('section', f'Step {i+1}')
                answer += f"**{section}:**\n{doc.page_content[:400]}...\n\n"
        else:
            # Use general relevant documents
            for i, doc in enumerate(docs[:3]):
                section = doc.metadata.get('section', f'Step {i+1}')
                answer += f"**{section}:**\n{doc.page_content[:300]}...\n\n"
        
        return answer
    
    def _generate_why_answer(self, query: str, context: str, docs: List[Document]) -> str:
        """Generate why/benefits answer."""
        answer = "Here are the key reasons and benefits:\n\n"
        
        # Look for overview or benefits sections
        benefit_docs = [doc for doc in docs if any(word in doc.metadata.get('section', '').lower() 
                       for word in ['value', 'benefit', 'advantage', 'why', 'competitive'])]
        
        if benefit_docs:
            for doc in benefit_docs[:2]:
                section = doc.metadata.get('section', 'Benefits')
                answer += f"**{section}:**\n{doc.page_content[:400]}...\n\n"
        else:
            # Extract benefits from general content
            for doc in docs[:3]:
                if any(word in doc.page_content.lower() for word in ['benefit', 'advantage', 'value']):
                    section = doc.metadata.get('section', 'Key Points')
                    answer += f"**{section}:**\n{doc.page_content[:300]}...\n\n"
        
        return answer
    
    def _generate_technical_answer(self, query: str, context: str, docs: List[Document]) -> str:
        """Generate technical answer."""
        answer = "Technical details from the documentation:\n\n"
        
        # Look for technical sections
        tech_docs = [doc for doc in docs if doc.metadata.get('type') == 'technical']
        
        if tech_docs:
            for doc in tech_docs[:3]:
                section = doc.metadata.get('section', 'Technical Details')
                answer += f"**{section}:**\n{doc.page_content[:400]}...\n\n"
        else:
            # Use most relevant documents
            for i, doc in enumerate(docs[:3]):
                section = doc.metadata.get('section', f'Technical Aspect {i+1}')
                answer += f"**{section}:**\n{doc.page_content[:300]}...\n\n"
        
        return answer
    
    def _generate_general_answer(self, query: str, context: str, docs: List[Document]) -> str:
        """Generate general answer."""
        answer = "Based on the available documentation:\n\n"
        
        for i, doc in enumerate(docs[:3]):
            section = doc.metadata.get('section', f'Relevant Information {i+1}')
            content = doc.page_content[:350] + "..." if len(doc.page_content) > 350 else doc.page_content
            answer += f"**{section}:**\n{content}\n\n"
        
        return answer
    
    def ask_question(self, question: str, k: int = 5) -> Dict[str, Any]:
        """Ask a question and get an answer with sources."""
        
        # Retrieve relevant documents
        retrieved_docs = self.retrieve_documents(question, k=k)
        
        # Generate answer
        answer = self.generate_answer(question, retrieved_docs)
        
        # Prepare sources
        sources = []
        for doc in retrieved_docs:
            sources.append({
                'section': doc.metadata.get('section', 'Unknown'),
                'type': doc.metadata.get('type', 'general'),
                'content_preview': doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            })
        
        return {
            'question': question,
            'answer': answer,
            'sources': sources,
            'num_sources': len(sources)
        }
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the vector store collection."""
        if self.vectorstore is None:
            return {"error": "Vector store not initialized"}
        
        try:
            collection = self.vectorstore._collection
            count = collection.count()
            
            return {
                'collection_name': self.collection_name,
                'document_count': count,
                'embedding_model': self.embedding_model_name
            }
        except Exception as e:
            return {"error": f"Could not get collection info: {str(e)}"}


def main():
    """Test the RAG system."""
    rag = ClimateRAGSystem()
    
    print("Initializing RAG system...")
    rag.initialize_vectorstore()
    
    print("Collection info:", rag.get_collection_info())
    
    # Test questions
    test_questions = [
        "What is ClimateIQ?",
        "How do I implement the RAG system?",
        "What are the technical components?",
        "Why should this project win?",
        "What are the phases of development?"
    ]
    
    for question in test_questions:
        print(f"\n{'='*50}")
        print(f"Question: {question}")
        print('='*50)
        
        result = rag.ask_question(question)
        print(f"Answer: {result['answer']}")
        print(f"\nSources used: {result['num_sources']}")


if __name__ == "__main__":
    main()