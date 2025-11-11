"""
Bolna AI Service Helper
Handles all interactions with Bolna API
"""

import httpx
import logging
from typing import Dict, Optional, Any
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import Settings


logger = logging.getLogger(__name__)

class BolnaService:
    """
    Service class for interacting with Bolna AI API
    """
    
    def __init__(self):
        """Initialize Bolna service with API credentials"""
        self.api_key = Settings.BOLNA_API_KEY
        self.api_url = Settings.BOLNA_API_URL
        self.agent_id = Settings.BOLNA_AGENT_ID
        
        if not self.api_key:
            logger.warning("BOLNA_API_KEY not set")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def create_call(
        self,
        phone_number: str,
        customer_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict:
        """
        Initiate an outbound call via Bolna
        
        Args:
            phone_number: Customer phone number (format: +91XXXXXXXXXX)
            customer_name: Optional customer name for personalization
            metadata: Additional data to attach to call
            
        Returns:
            Dict with call_id and status
        """
        try:
            endpoint = f"{self.api_url}/call"
            
            payload = {
                "agent_id": self.agent_id,
                "recipient": {
                    "phone": phone_number,
                    "name": customer_name or "Customer"
                },
                "metadata": metadata or {}
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"Call created successfully: {result.get('call_id')}")
                return result
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error creating call: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error creating call: {str(e)}")
            raise
    
    async def get_call_status(self, call_id: str) -> Dict:
        """
        Get status of a specific call
        
        Args:
            call_id: Bolna call ID
            
        Returns:
            Dict with call status and details
        """
        try:
            endpoint = f"{self.api_url}/call/{call_id}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    endpoint,
                    headers=self.headers,
                    timeout=10.0
                )
                
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Error getting call status: {str(e)}")
            raise
    
    async def end_call(self, call_id: str) -> Dict:
        """
        Manually end an ongoing call
        
        Args:
            call_id: Bolna call ID
            
        Returns:
            Dict with result
        """
        try:
            endpoint = f"{self.api_url}/call/{call_id}/end"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint,
                    headers=self.headers,
                    timeout=10.0
                )
                
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Error ending call: {str(e)}")
            raise
    
    async def create_agent(
        self,
        name: str,
        prompt: str,
        voice_id: Optional[str] = None,
        model: str = "gpt-4o-mini"
    ) -> Dict:
        """
        Create a new Bolna agent (conversation bot)
        
        Args:
            name: Agent name
            prompt: System prompt for agent
            voice_id: Voice ID (Bolna's voice catalog)
            model: LLM model to use
            
        Returns:
            Dict with agent_id
        """
        try:
            endpoint = f"{self.api_url}/agent"
            
            payload = {
                "name": name,
                "prompt": prompt,
                "voice_id": voice_id or "default_indian_male",
                "model": model,
                "language": "en-IN"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"Agent created: {result.get('agent_id')}")
                return result
                
        except Exception as e:
            logger.error(f"Error creating agent: {str(e)}")
            raise
    
    async def update_agent(
        self,
        agent_id: str,
        prompt: Optional[str] = None,
        voice_id: Optional[str] = None
    ) -> Dict:
        """
        Update existing Bolna agent configuration
        
        Args:
            agent_id: Agent ID to update
            prompt: New system prompt (optional)
            voice_id: New voice ID (optional)
            
        Returns:
            Dict with updated agent info
        """
        try:
            endpoint = f"{self.api_url}/agent/{agent_id}"
            
            payload = {}
            if prompt:
                payload["prompt"] = prompt
            if voice_id:
                payload["voice_id"] = voice_id
            
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    endpoint,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Error updating agent: {str(e)}")
            raise
    
    async def list_voices(self) -> Dict:
        """
        Get available voices from Bolna
        
        Returns:
            Dict with available voices
        """
        try:
            endpoint = f"{self.api_url}/voices"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    endpoint,
                    headers=self.headers,
                    timeout=10.0
                )
                
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Error listing voices: {str(e)}")
            raise
    
    def sync_create_call(
        self,
        phone_number: str,
        customer_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict:
        """
        Synchronous version of create_call (for use in non-async contexts)
        """
        import asyncio
        return asyncio.run(
            self.create_call(phone_number, customer_name, metadata)
        )

# Create singleton instance
bolna_service = BolnaService()