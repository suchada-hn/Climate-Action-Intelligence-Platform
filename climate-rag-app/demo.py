#!/usr/bin/env python3
"""
Demo script for the Climate Action Intelligence Platform RAG Application.
Showcases the capabilities of the RAG system with example queries.
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from rag_system import ClimateRAGSystem


def print_separator(title=""):
    """Print a formatted separator."""
    print("\n" + "="*80)
    if title:
        print(f" {title} ".center(80, "="))
        print("="*80)
    print()


def demo_question(rag_system, question, description=""):
    """Demo a single question."""
    print(f"🤔 **Question:** {question}")
    if description:
        print(f"📝 **Context:** {description}")
    print()
    
    try:
        result = rag_system.ask_question(question, k=3)
        
        print("🤖 **Answer:**")
        print(result['answer'])
        print()
        
        print(f"📚 **Sources Used:** {result['num_sources']}")
        for i, source in enumerate(result['sources'], 1):
            print(f"   {i}. {source['section']} ({source['type']})")
        
    except Exception as e:
        print(f"❌ **Error:** {str(e)}")
    
    print("\n" + "-"*80)


def main():
    """Run the RAG system demo."""
    
    print_separator("Climate Action Intelligence Platform - RAG Demo")
    
    print("🌍 Welcome to the ClimateIQ RAG System Demo!")
    print("This demonstration showcases how our AI-powered system can answer")
    print("questions about the Climate Action Intelligence Platform project.")
    print()
    
    # Initialize RAG system
    print("🔧 Initializing RAG system...")
    try:
        rag = ClimateRAGSystem()
        rag.initialize_vectorstore()
        
        # Get system info
        info = rag.get_collection_info()
        print(f"✅ System initialized successfully!")
        print(f"   📊 Documents in database: {info.get('document_count', 'Unknown')}")
        print(f"   🧠 Embedding model: {info.get('embedding_model', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Failed to initialize RAG system: {str(e)}")
        return
    
    print_separator("Demo Questions")
    
    # Demo questions with context
    demo_questions = [
        {
            "question": "What is ClimateIQ?",
            "description": "Basic overview question to understand the project"
        },
        {
            "question": "How does the RAG system work in this platform?",
            "description": "Technical question about the core AI component"
        },
        {
            "question": "What are the main technical components?",
            "description": "Architecture and technology stack inquiry"
        },
        {
            "question": "Why should this project win a hackathon?",
            "description": "Value proposition and competitive advantages"
        },
        {
            "question": "How do I implement the climate action planner?",
            "description": "Implementation guidance for specific features"
        },
        {
            "question": "What are the phases of development?",
            "description": "Project timeline and development strategy"
        },
        {
            "question": "How does the impact tracking work?",
            "description": "Understanding the measurement and analytics features"
        }
    ]
    
    for i, demo in enumerate(demo_questions, 1):
        print(f"Demo {i}/{len(demo_questions)}")
        demo_question(rag, demo["question"], demo["description"])
    
    print_separator("Interactive Mode")
    
    print("🎯 Now you can ask your own questions!")
    print("Type 'quit', 'exit', or 'q' to end the demo.")
    print()
    
    while True:
        try:
            question = input("❓ Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q', '']:
                break
            
            print()
            demo_question(rag, question)
            
        except KeyboardInterrupt:
            print("\n\n👋 Demo ended by user.")
            break
        except EOFError:
            break
    
    print_separator("Demo Complete")
    
    print("🎉 Thank you for trying the ClimateIQ RAG System!")
    print()
    print("🌐 To use the full web interface, run:")
    print("   python run_app.py")
    print()
    print("📖 For more information, see README.md")
    print()
    print("🌍 Together, we can build AI for climate action!")


if __name__ == "__main__":
    main()