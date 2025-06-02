"""
Document processor for the Climate Action Intelligence Platform RAG system.
Handles loading, chunking, and processing of the README document.
"""

import os
import re
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document


class ClimateDocumentProcessor:
    """Process and chunk the Climate Action Intelligence Platform documentation."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
    
    def load_readme(self, readme_path: str) -> str:
        """Load the README file content."""
        with open(readme_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def extract_sections(self, content: str) -> List[Dict[str, Any]]:
        """Extract structured sections from the README content."""
        sections = []
        
        # Split by main headers (# or ##)
        header_pattern = r'^(#{1,2})\s+(.+)$'
        lines = content.split('\n')
        
        current_section = None
        current_content = []
        
        for line in lines:
            header_match = re.match(header_pattern, line)
            
            if header_match:
                # Save previous section
                if current_section:
                    sections.append({
                        'title': current_section,
                        'content': '\n'.join(current_content).strip(),
                        'level': len(header_match.group(1))
                    })
                
                # Start new section
                current_section = header_match.group(2)
                current_content = [line]
            else:
                if current_section:
                    current_content.append(line)
        
        # Add the last section
        if current_section:
            sections.append({
                'title': current_section,
                'content': '\n'.join(current_content).strip(),
                'level': len(header_match.group(1)) if header_match else 1
            })
        
        return sections
    
    def create_documents(self, readme_path: str) -> List[Document]:
        """Create LangChain documents from the README file."""
        content = self.load_readme(readme_path)
        sections = self.extract_sections(content)
        
        documents = []
        
        for section in sections:
            # Create metadata for each section
            metadata = {
                'source': 'Climate Action Intelligence Platform README',
                'section': section['title'],
                'level': section['level'],
                'type': self._classify_section(section['title'])
            }
            
            # Split large sections into smaller chunks
            if len(section['content']) > self.chunk_size:
                chunks = self.text_splitter.split_text(section['content'])
                for i, chunk in enumerate(chunks):
                    chunk_metadata = metadata.copy()
                    chunk_metadata['chunk_id'] = i
                    chunk_metadata['total_chunks'] = len(chunks)
                    documents.append(Document(page_content=chunk, metadata=chunk_metadata))
            else:
                documents.append(Document(page_content=section['content'], metadata=metadata))
        
        return documents
    
    def _classify_section(self, title: str) -> str:
        """Classify section type based on title."""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['overview', 'mission', 'project']):
            return 'overview'
        elif any(word in title_lower for word in ['technical', 'architecture', 'implementation']):
            return 'technical'
        elif any(word in title_lower for word in ['setup', 'installation', 'prerequisites']):
            return 'setup'
        elif any(word in title_lower for word in ['phase', 'step', 'development']):
            return 'implementation_guide'
        elif any(word in title_lower for word in ['demo', 'presentation', 'winning']):
            return 'demo'
        elif any(word in title_lower for word in ['features', 'components']):
            return 'features'
        else:
            return 'general'
    
    def get_document_stats(self, documents: List[Document]) -> Dict[str, Any]:
        """Get statistics about the processed documents."""
        total_docs = len(documents)
        total_chars = sum(len(doc.page_content) for doc in documents)
        
        section_types = {}
        for doc in documents:
            doc_type = doc.metadata.get('type', 'unknown')
            section_types[doc_type] = section_types.get(doc_type, 0) + 1
        
        return {
            'total_documents': total_docs,
            'total_characters': total_chars,
            'average_doc_length': total_chars / total_docs if total_docs > 0 else 0,
            'section_types': section_types
        }


def main():
    """Test the document processor."""
    processor = ClimateDocumentProcessor()
    readme_path = "/workspace/Climate-Action-Intelligence-Platform/README.md"
    
    if os.path.exists(readme_path):
        documents = processor.create_documents(readme_path)
        stats = processor.get_document_stats(documents)
        
        print("Document Processing Results:")
        print(f"Total documents: {stats['total_documents']}")
        print(f"Total characters: {stats['total_characters']}")
        print(f"Average document length: {stats['average_doc_length']:.2f}")
        print(f"Section types: {stats['section_types']}")
        
        # Show first few documents
        print("\nFirst 3 documents:")
        for i, doc in enumerate(documents[:3]):
            print(f"\nDocument {i+1}:")
            print(f"Section: {doc.metadata.get('section', 'Unknown')}")
            print(f"Type: {doc.metadata.get('type', 'Unknown')}")
            print(f"Content preview: {doc.page_content[:200]}...")
    else:
        print(f"README file not found at {readme_path}")


if __name__ == "__main__":
    main()