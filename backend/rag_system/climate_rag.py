"""
RAG (Retrieval-Augmented Generation) system for climate knowledge
"""
import logging
import os
from typing import List, Dict, Any, Tuple
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from backend.watsonx_integration.watsonx_client import WatsonxClient
from config import settings

logger = logging.getLogger(__name__)

class ClimateRAGSystem:
    """RAG system specialized for climate action knowledge"""
    
    def __init__(self):
        self.embeddings = self._setup_embeddings()
        self.vectorstore = None
        self.watsonx_client = WatsonxClient()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
    def _setup_embeddings(self) -> HuggingFaceEmbeddings:
        """Initialize embedding model"""
        return HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'}
        )
    
    def initialize_vectorstore(self, documents: List[Document] = None):
        """Initialize or load the vector database"""
        try:
            if os.path.exists(settings.CHROMA_PERSIST_DIRECTORY):
                # Load existing vectorstore
                self.vectorstore = Chroma(
                    persist_directory=settings.CHROMA_PERSIST_DIRECTORY,
                    embedding_function=self.embeddings
                )
                logger.info("Loaded existing vector database")
            else:
                # Create new vectorstore with sample documents if none provided
                if not documents:
                    documents = self._create_sample_climate_documents()
                
                # Process documents
                chunks = self.text_splitter.split_documents(documents)
                
                # Create vectorstore
                self.vectorstore = Chroma.from_documents(
                    documents=chunks,
                    embedding=self.embeddings,
                    persist_directory=settings.CHROMA_PERSIST_DIRECTORY
                )
                self.vectorstore.persist()
                logger.info("Created new vector database with climate knowledge")
                
        except Exception as e:
            logger.error(f"Error initializing vectorstore: {e}")
            # Create minimal vectorstore for demo
            self._create_minimal_vectorstore()
    
    def _create_sample_climate_documents(self) -> List[Document]:
        """Create sample climate knowledge documents"""
        sample_docs = [
            Document(
                page_content="""
                Climate Change Mitigation Strategies:
                
                1. Energy Efficiency: Improving energy efficiency in buildings can reduce CO2 emissions by 30-50%. 
                Key actions include LED lighting, smart thermostats, insulation, and energy-efficient appliances.
                
                2. Renewable Energy: Solar panels can reduce household emissions by 3-4 tons CO2/year. 
                Wind energy is cost-effective for communities. Geothermal heating reduces emissions by 60%.
                
                3. Transportation: Electric vehicles reduce emissions by 60-70% compared to gasoline cars. 
                Public transit, cycling, and walking are zero-emission alternatives. Carpooling reduces individual impact by 50%.
                """,
                metadata={"source": "IPCC_AR6_Mitigation", "category": "mitigation"}
            ),
            Document(
                page_content="""
                Carbon Footprint Reduction for Households:
                
                Average household carbon footprint: 16 tons CO2/year (US)
                
                High-impact actions:
                - Switch to renewable energy: -3.6 tons CO2/year
                - Improve home insulation: -2.3 tons CO2/year
                - Drive electric vehicle: -2.4 tons CO2/year
                - Reduce meat consumption: -0.8 tons CO2/year
                - Fly less frequently: -1.6 tons CO2/year per avoided round-trip
                
                Medium-impact actions:
                - Energy-efficient appliances: -0.5 tons CO2/year
                - Smart thermostat: -0.3 tons CO2/year
                - LED lighting: -0.1 tons CO2/year
                """,
                metadata={"source": "EPA_Carbon_Calculator", "category": "household"}
            ),
            Document(
                page_content="""
                Business Climate Action Strategies:
                
                Small and Medium Enterprises (SMEs) can reduce emissions through:
                
                1. Energy Management:
                - Energy audits identify 20-30% savings potential
                - Smart building systems reduce consumption by 15-25%
                - Renewable energy procurement cuts emissions by 40-60%
                
                2. Supply Chain Optimization:
                - Local sourcing reduces transport emissions by 30%
                - Sustainable packaging cuts waste by 50%
                - Circular economy practices reduce material footprint by 40%
                
                3. Employee Engagement:
                - Remote work reduces commute emissions by 70%
                - Green commuting programs cut transport emissions by 25%
                - Sustainability training increases participation by 60%
                """,
                metadata={"source": "UN_Global_Compact", "category": "business"}
            ),
            Document(
                page_content="""
                Climate Finance and Incentives:
                
                Government Incentives (US):
                - Federal solar tax credit: 30% of installation cost
                - Electric vehicle tax credit: up to $7,500
                - Energy efficiency rebates: $500-$2,000 per upgrade
                - Heat pump incentives: $2,000-$8,000
                
                Green Financing Options:
                - Green mortgages: 0.25-0.5% interest rate reduction
                - Energy efficiency loans: 2-5% APR
                - Solar financing: $0 down payment options
                - Carbon offset markets: $10-$50 per ton CO2
                
                Return on Investment:
                - Solar panels: 6-10 year payback period
                - Insulation: 2-5 year payback period
                - Heat pumps: 5-8 year payback period
                """,
                metadata={"source": "IEA_Energy_Finance", "category": "finance"}
            ),
            Document(
                page_content="""
                Community Climate Resilience:
                
                Adaptation Strategies:
                1. Urban Heat Island Reduction:
                - Green roofs reduce building temperature by 2-8°F
                - Tree planting lowers ambient temperature by 2-5°F
                - Cool pavements reflect 50-80% more sunlight
                
                2. Water Management:
                - Rain gardens capture 90% of stormwater runoff
                - Permeable pavements reduce flooding by 60%
                - Greywater systems save 30-50% of water usage
                
                3. Food Security:
                - Community gardens increase local food access by 40%
                - Urban farming reduces food miles by 90%
                - Drought-resistant crops maintain yields with 30% less water
                
                4. Emergency Preparedness:
                - Early warning systems reduce climate disaster impacts by 30%
                - Community resilience hubs provide 24/7 emergency support
                """,
                metadata={"source": "UNDRR_Resilience_Guide", "category": "adaptation"}
            )
        ]
        
        return sample_docs
    
    def _create_minimal_vectorstore(self):
        """Create minimal vectorstore for demo purposes"""
        try:
            minimal_docs = [
                Document(
                    page_content="Climate action includes energy efficiency, renewable energy, sustainable transport, and carbon reduction strategies.",
                    metadata={"source": "demo", "category": "general"}
                )
            ]
            
            self.vectorstore = Chroma.from_documents(
                documents=minimal_docs,
                embedding=self.embeddings,
                persist_directory=settings.CHROMA_PERSIST_DIRECTORY
            )
            logger.info("Created minimal vectorstore for demo")
        except Exception as e:
            logger.error(f"Failed to create minimal vectorstore: {e}")
    
    def retrieve_and_generate(self, query: str, location: str = None, user_profile: Dict = None) -> Tuple[str, List[Document]]:
        """Retrieve relevant documents and generate response"""
        try:
            if not self.vectorstore:
                self.initialize_vectorstore()
            
            # Enhance query with context
            enhanced_query = self._enhance_query(query, location, user_profile)
            
            # Retrieve relevant documents
            retriever = self.vectorstore.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 5, "fetch_k": 10}
            )
            
            docs = retriever.get_relevant_documents(enhanced_query)
            
            # Prepare context from retrieved documents
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # Generate response using watsonx
            response = self.watsonx_client.generate_response(query, context)
            
            return response, docs
            
        except Exception as e:
            logger.error(f"Error in retrieve_and_generate: {e}")
            fallback_response = self._generate_fallback_response(query)
            return fallback_response, []
    
    def _enhance_query(self, query: str, location: str = None, user_profile: Dict = None) -> str:
        """Enhance query with contextual information"""
        enhanced_parts = [query]
        
        if location:
            enhanced_parts.append(f"Location context: {location}")
        
        if user_profile:
            lifestyle = user_profile.get('lifestyle', '')
            household_size = user_profile.get('household_size', '')
            if lifestyle:
                enhanced_parts.append(f"Lifestyle: {lifestyle}")
            if household_size:
                enhanced_parts.append(f"Household size: {household_size}")
        
        return " ".join(enhanced_parts)
    
    def _generate_fallback_response(self, query: str) -> str:
        """Generate fallback response when RAG system fails"""
        return f"""I understand you're asking about: {query}

While I'm experiencing some technical difficulties accessing my knowledge base, here are some general climate action recommendations:

1. **Energy Efficiency**: Switch to LED lighting, improve insulation, use programmable thermostats
2. **Transportation**: Consider electric vehicles, public transit, cycling, or walking
3. **Renewable Energy**: Explore solar panels or renewable energy programs in your area
4. **Consumption**: Reduce, reuse, recycle; choose sustainable products
5. **Diet**: Consider reducing meat consumption and choosing local, seasonal foods

For specific advice tailored to your situation, please try asking again or consult local environmental organizations."""
    
    def add_documents(self, documents: List[Document]):
        """Add new documents to the knowledge base"""
        try:
            if not self.vectorstore:
                self.initialize_vectorstore()
            
            # Process and add documents
            chunks = self.text_splitter.split_documents(documents)
            self.vectorstore.add_documents(chunks)
            self.vectorstore.persist()
            
            logger.info(f"Added {len(chunks)} document chunks to knowledge base")
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
    
    def search_knowledge_base(self, query: str, k: int = 5) -> List[Document]:
        """Search the knowledge base for relevant documents"""
        try:
            if not self.vectorstore:
                self.initialize_vectorstore()
            
            docs = self.vectorstore.similarity_search(query, k=k)
            return docs
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []