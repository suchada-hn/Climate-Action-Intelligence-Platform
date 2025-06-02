"""
Streamlit frontend for the Climate Action Intelligence Platform RAG Application.
"""

import streamlit as st
import sys
import os
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from rag_system import ClimateRAGSystem


def initialize_session_state():
    """Initialize session state variables."""
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'system_initialized' not in st.session_state:
        st.session_state.system_initialized = False


def load_rag_system():
    """Load and initialize the RAG system."""
    if st.session_state.rag_system is None:
        with st.spinner("Initializing RAG system... This may take a moment."):
            try:
                rag = ClimateRAGSystem()
                rag.initialize_vectorstore()
                st.session_state.rag_system = rag
                st.session_state.system_initialized = True
                st.success("RAG system initialized successfully!")
                return True
            except Exception as e:
                st.error(f"Failed to initialize RAG system: {str(e)}")
                return False
    return True


def display_header():
    """Display the application header."""
    st.set_page_config(
        page_title="Climate Action Intelligence Platform - RAG Assistant",
        page_icon="🌍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🌍 Climate Action Intelligence Platform")
    st.markdown("### AI-Powered RAG Assistant")
    st.markdown("Ask questions about the ClimateIQ project and get intelligent answers based on the comprehensive documentation.")
    
    st.markdown("---")


def display_sidebar():
    """Display the sidebar with system information and controls."""
    with st.sidebar:
        st.header("🔧 System Information")
        
        if st.session_state.system_initialized and st.session_state.rag_system:
            info = st.session_state.rag_system.get_collection_info()
            
            if 'error' not in info:
                st.metric("Documents in Database", info.get('document_count', 'Unknown'))
                st.metric("Embedding Model", info.get('embedding_model', 'Unknown').split('/')[-1])
                st.success("✅ System Ready")
            else:
                st.error(f"❌ System Error: {info['error']}")
        else:
            st.warning("⏳ System Initializing...")
        
        st.markdown("---")
        
        st.header("📚 Quick Questions")
        quick_questions = [
            "What is ClimateIQ?",
            "How does the RAG system work?",
            "What are the technical components?",
            "How to implement the platform?",
            "What are the competitive advantages?",
            "What is the demo strategy?",
            "How to deploy the system?"
        ]
        
        for question in quick_questions:
            if st.button(question, key=f"quick_{question}", use_container_width=True):
                st.session_state.current_question = question
        
        st.markdown("---")
        
        st.header("🔄 System Controls")
        if st.button("Clear Chat History", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
        
        if st.button("Reinitialize System", use_container_width=True):
            st.session_state.rag_system = None
            st.session_state.system_initialized = False
            st.rerun()


def display_chat_interface():
    """Display the main chat interface."""
    st.header("💬 Ask Questions About ClimateIQ")
    
    # Check if there's a quick question to process
    if hasattr(st.session_state, 'current_question'):
        question = st.session_state.current_question
        delattr(st.session_state, 'current_question')
    else:
        # Regular input
        question = st.text_input(
            "Enter your question:",
            placeholder="e.g., What is the ClimateIQ platform and how does it work?",
            key="question_input"
        )
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        ask_button = st.button("🔍 Ask Question", type="primary", use_container_width=True)
    
    with col2:
        k_value = st.slider("Number of sources to retrieve", min_value=1, max_value=10, value=5)
    
    if (ask_button or question) and question and st.session_state.system_initialized:
        process_question(question, k_value)
    elif question and not st.session_state.system_initialized:
        st.warning("Please wait for the system to initialize before asking questions.")


def process_question(question: str, k: int):
    """Process a user question and display the answer."""
    if not st.session_state.rag_system:
        st.error("RAG system not initialized.")
        return
    
    with st.spinner("Searching for relevant information..."):
        try:
            result = st.session_state.rag_system.ask_question(question, k=k)
            
            # Add to chat history
            st.session_state.chat_history.append({
                'timestamp': datetime.now(),
                'question': question,
                'answer': result['answer'],
                'sources': result['sources'],
                'num_sources': result['num_sources']
            })
            
            # Display the answer
            display_answer(result)
            
        except Exception as e:
            st.error(f"Error processing question: {str(e)}")


def display_answer(result: dict):
    """Display the answer and sources."""
    st.markdown("### 🤖 Answer")
    st.markdown(result['answer'])
    
    st.markdown("### 📖 Sources")
    
    # Create tabs for different views of sources
    tab1, tab2 = st.tabs(["📋 Source List", "📊 Source Analysis"])
    
    with tab1:
        for i, source in enumerate(result['sources']):
            with st.expander(f"Source {i+1}: {source['section']}", expanded=i==0):
                st.markdown(f"**Section:** {source['section']}")
                st.markdown(f"**Type:** {source['type']}")
                st.markdown(f"**Content Preview:**")
                st.markdown(source['content_preview'])
    
    with tab2:
        if result['sources']:
            # Create source type distribution
            source_types = [source['type'] for source in result['sources']]
            type_counts = pd.Series(source_types).value_counts()
            
            fig = px.pie(
                values=type_counts.values,
                names=type_counts.index,
                title="Distribution of Source Types"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Source sections
            sections = [source['section'] for source in result['sources']]
            st.markdown("**Sections Referenced:**")
            for section in sections:
                st.markdown(f"• {section}")


def display_chat_history():
    """Display the chat history."""
    if st.session_state.chat_history:
        st.header("📜 Chat History")
        
        for i, chat in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(f"Q{len(st.session_state.chat_history)-i}: {chat['question'][:50]}...", expanded=i==0):
                st.markdown(f"**Question:** {chat['question']}")
                st.markdown(f"**Time:** {chat['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                st.markdown(f"**Answer:** {chat['answer'][:300]}...")
                st.markdown(f"**Sources Used:** {chat['num_sources']}")


def display_project_overview():
    """Display project overview and statistics."""
    st.header("📊 Project Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Project Type", "AI-Powered RAG")
    
    with col2:
        st.metric("Focus Area", "Climate Action")
    
    with col3:
        st.metric("Technology", "LangChain + ChromaDB")
    
    with col4:
        st.metric("Status", "Demo Ready")
    
    # Project highlights
    st.markdown("### 🌟 Key Features")
    
    features = [
        "🤖 **Intelligent RAG System**: Advanced retrieval-augmented generation for climate action queries",
        "📚 **Comprehensive Knowledge Base**: Built from detailed ClimateIQ project documentation",
        "🔍 **Smart Document Retrieval**: Context-aware document chunking and retrieval",
        "💬 **Interactive Chat Interface**: User-friendly Streamlit interface for natural conversations",
        "📊 **Source Transparency**: Clear attribution and source tracking for all answers",
        "🔧 **Scalable Architecture**: Built with production-ready components"
    ]
    
    for feature in features:
        st.markdown(feature)


def main():
    """Main application function."""
    initialize_session_state()
    display_header()
    
    # Initialize RAG system
    if not st.session_state.system_initialized:
        if not load_rag_system():
            st.stop()
    
    # Display sidebar
    display_sidebar()
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📜 History", "📊 Overview"])
    
    with tab1:
        display_chat_interface()
    
    with tab2:
        display_chat_history()
    
    with tab3:
        display_project_overview()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "🌍 **Climate Action Intelligence Platform RAG Assistant** | "
        "Built with Streamlit, LangChain, and ChromaDB | "
        "Powered by AI for Climate Action"
    )


if __name__ == "__main__":
    main()