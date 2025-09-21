import httpx
import json
from typing import Dict, Any, List, Optional
from ..core.config import settings


class OpenRouterClient:
    def __init__(self):
        self.base_url = settings.openrouter_base_url
        self.api_key = settings.openrouter_api_key
        
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "openai/gpt-3.5-turbo",
        max_tokens: Optional[int] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Send a chat completion request to OpenRouter"""
        if not self.api_key:
            raise Exception("OpenRouter API key not configured")
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://wakanda-mandate.gov",
            "X-Title": "Wakanda Digital Government Platform"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60.0
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
            
            return response.json()
    
    async def get_models(self) -> List[Dict[str, Any]]:
        """Get available models from OpenRouter"""
        if not self.api_key:
            raise Exception("OpenRouter API key not configured")
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
            
            return response.json()["data"]


def calculate_cost(tokens: int, model: str) -> float:
    """Calculate approximate cost based on tokens and model"""
    # Simplified cost calculation - in production, use actual pricing
    cost_per_1k_tokens = {
        "openai/gpt-3.5-turbo": 0.002,
        "openai/gpt-4": 0.03,
        "anthropic/claude-3-haiku": 0.0015,
        "anthropic/claude-3-sonnet": 0.015,
        "meta-llama/llama-3-8b-instruct": 0.001,
    }
    
    base_cost = cost_per_1k_tokens.get(model, 0.002)
    return (tokens / 1000) * base_cost


def extract_tokens_from_response(response: Dict[str, Any]) -> int:
    """Extract token usage from OpenRouter response"""
    usage = response.get("usage", {})
    return usage.get("total_tokens", 0)


def build_government_system_prompt() -> str:
    """Build a system prompt for government AI assistant"""
    return """You are an AI assistant for the Wakanda Digital Government Platform. You help government officials, employees, and citizens with:

1. Government service information and procedures
2. Policy analysis and recommendations
3. Data analysis and insights
4. Administrative assistance
5. Public service guidance

Guidelines:
- Provide accurate, helpful, and politically neutral information
- Respect privacy and confidentiality
- Follow government communication standards
- Be transparent about limitations
- Recommend appropriate human contact when needed
- Focus on efficiency and citizen service improvement

Always maintain professional tone and ensure information is accessible to diverse audiences."""


def build_analysis_prompt(analysis_type: str, content: str, custom_instructions: str = None) -> List[Dict[str, str]]:
    """Build prompt for document/data analysis"""
    system_prompt = build_government_system_prompt()
    
    if analysis_type == "summary":
        user_prompt = f"Please provide a concise summary of the following document:\n\n{content}"
    elif analysis_type == "sentiment":
        user_prompt = f"Analyze the sentiment of the following content and provide insights:\n\n{content}"
    elif analysis_type == "extraction":
        user_prompt = f"Extract key information, dates, numbers, and important entities from:\n\n{content}"
    elif analysis_type == "classification":
        user_prompt = f"Classify the following document by type, topic, and urgency level:\n\n{content}"
    else:
        user_prompt = f"Analyze the following content:\n\n{content}"
    
    if custom_instructions:
        user_prompt += f"\n\nAdditional instructions: {custom_instructions}"
    
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]


def build_recommendation_prompt(context: str, request_type: str, parameters: Dict[str, Any] = None) -> List[Dict[str, str]]:
    """Build prompt for generating recommendations"""
    system_prompt = build_government_system_prompt()
    
    user_prompt = f"""Based on the following context, provide recommendations for {request_type}:

Context: {context}

Please provide:
1. Specific, actionable recommendations
2. Reasoning for each recommendation
3. Implementation steps
4. Potential challenges and mitigation strategies
5. Expected outcomes and benefits

"""
    
    if parameters:
        user_prompt += f"Additional parameters to consider: {json.dumps(parameters, indent=2)}"
    
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]