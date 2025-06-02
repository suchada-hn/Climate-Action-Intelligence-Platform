"""
IBM watsonx.ai integration for Climate Action Intelligence Platform
"""
import logging
from typing import Dict, Any, Optional
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.credentials import Credentials
from config import settings

logger = logging.getLogger(__name__)

class WatsonxClient:
    """Client for IBM watsonx.ai foundation models"""
    
    def __init__(self):
        self.credentials = self._setup_credentials()
        self.model = self._setup_model()
    
    def _setup_credentials(self) -> Dict[str, str]:
        """Setup IBM Cloud credentials"""
        return {
            "url": settings.IBM_CLOUD_URL,
            "apikey": settings.IBM_CLOUD_API_KEY
        }
    
    def _setup_model(self) -> Model:
        """Initialize the watsonx foundation model"""
        try:
            model = Model(
                model_id=settings.WATSONX_MODEL_ID,
                params={
                    "decoding_method": "greedy",
                    "max_new_tokens": 1000,
                    "temperature": 0.1,
                    "repetition_penalty": 1.1
                },
                credentials=self.credentials,
                project_id=settings.WATSONX_PROJECT_ID
            )
            logger.info("watsonx.ai model initialized successfully")
            return model
        except Exception as e:
            logger.error(f"Failed to initialize watsonx model: {e}")
            raise
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate response using watsonx.ai"""
        try:
            # Construct the full prompt with context
            full_prompt = self._construct_prompt(prompt, context)
            
            # Generate response
            response = self.model.generate_text(prompt=full_prompt)
            
            logger.info("Successfully generated response from watsonx")
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I apologize, but I'm experiencing technical difficulties. Error: {str(e)}"
    
    def _construct_prompt(self, query: str, context: str = "") -> str:
        """Construct a well-formatted prompt for climate action queries"""
        system_prompt = """You are ClimateIQ, an AI assistant specialized in climate action and environmental sustainability. 
        You provide evidence-based, actionable advice for individuals, businesses, and communities to combat climate change.
        
        Guidelines:
        - Provide specific, actionable recommendations
        - Include quantifiable impact estimates when possible
        - Consider local context and feasibility
        - Reference scientific data and best practices
        - Be encouraging and solution-focused
        """
        
        if context:
            prompt = f"""{system_prompt}

Context Information:
{context}

User Question: {query}

Response:"""
        else:
            prompt = f"""{system_prompt}

User Question: {query}

Response:"""
        
        return prompt
    
    def generate_climate_plan(self, user_profile: Dict[str, Any], context: str = "") -> str:
        """Generate personalized climate action plan"""
        location = user_profile.get('location', 'Unknown')
        lifestyle = user_profile.get('lifestyle', 'Unknown')
        household_size = user_profile.get('household_size', 1)
        
        prompt = f"""Create a personalized climate action plan for:
        - Location: {location}
        - Lifestyle: {lifestyle}
        - Household Size: {household_size}
        
        Please provide:
        1. Top 5 priority actions with estimated CO2 reduction
        2. Implementation timeline
        3. Cost estimates and potential savings
        4. Local resources and incentives
        5. Progress tracking methods
        """
        
        return self.generate_response(prompt, context)
    
    def validate_climate_solution(self, solution_description: str, context: str = "") -> Dict[str, Any]:
        """Validate a community-submitted climate solution"""
        prompt = f"""Evaluate this climate solution for scientific validity and feasibility:

        Solution: {solution_description}
        
        Please assess:
        1. Scientific accuracy (1-10 scale)
        2. Feasibility (1-10 scale)
        3. Potential impact (1-10 scale)
        4. Implementation challenges
        5. Recommendations for improvement
        6. Overall validation (Accept/Needs Review/Reject)
        
        Provide structured feedback in JSON format.
        """
        
        response = self.generate_response(prompt, context)
        
        # Parse response and return structured validation
        try:
            # Simple validation parsing - in production, use more robust JSON parsing
            if "Accept" in response:
                status = "accepted"
            elif "Needs Review" in response:
                status = "needs_review"
            else:
                status = "rejected"
            
            return {
                "status": status,
                "feedback": response,
                "validation_score": self._extract_scores(response)
            }
        except Exception as e:
            logger.error(f"Error parsing validation response: {e}")
            return {
                "status": "needs_review",
                "feedback": response,
                "validation_score": {"overall": 5}
            }
    
    def _extract_scores(self, response: str) -> Dict[str, int]:
        """Extract numerical scores from validation response"""
        # Simple score extraction - in production, use more sophisticated parsing
        scores = {}
        lines = response.split('\n')
        for line in lines:
            if 'accuracy' in line.lower() and any(char.isdigit() for char in line):
                scores['accuracy'] = int(''.join(filter(str.isdigit, line))[:1] or 5)
            elif 'feasibility' in line.lower() and any(char.isdigit() for char in line):
                scores['feasibility'] = int(''.join(filter(str.isdigit, line))[:1] or 5)
            elif 'impact' in line.lower() and any(char.isdigit() for char in line):
                scores['impact'] = int(''.join(filter(str.isdigit, line))[:1] or 5)
        
        return scores