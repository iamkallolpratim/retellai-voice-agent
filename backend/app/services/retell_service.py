# backend/app/services/retell_service.py
from typing import Dict, Any, Optional, List
from retell import Retell
import httpx
from app.core.config import settings
from app.core.exceptions import RetellAPIError


class RetellService:
    """
    Service for interacting with Retell AI API
    Handles agent creation, web calls, phone calls, and LLM management
    """
    
    def __init__(self):
        self.client = Retell(api_key=settings.RETELL_API_KEY)
        self.api_key = settings.RETELL_API_KEY
        self.base_url = "https://api.retellai.com"
    
    # ==================== Agent Management ====================
    
    async def create_agent(
        self,
        agent_name: str,
        llm_id: str,
        voice_id: str = "11labs-Adrian",
        language: str = "en-US",
        enable_backchannel: bool = True,
        interruption_sensitivity: float = 1.0,
        responsiveness: float = 1.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new Retell AI agent with full configuration support
        
        Uses direct HTTP API call to support all agent parameters that
        the Python SDK doesn't expose.
        
        Args:
            agent_name: Display name for the agent
            llm_id: ID of the LLM configuration to use
            voice_id: Voice provider and voice ID (default: 11labs-Adrian)
            language: Language code (default: en-US)
            enable_backchannel: Enable "uh-huh" type responses (default: True)
            interruption_sensitivity: 0-1, higher = more interruptible (default: 1.0)
            responsiveness: 0-1, higher = faster responses (default: 1.0)
            **kwargs: Additional configuration options
            
        Returns:
            Dict with agent_id, agent_name, voice_id, and llm_id
        """
        try:
            if not llm_id:
                raise RetellAPIError("llm_id is required to create an agent")
            
            # Build comprehensive agent configuration
            agent_config = {
                "agent_name": agent_name,
                "voice_id": voice_id,
                "language": language,
                "response_engine": {
                    "type": "retell-llm",
                    "llm_id": llm_id,
                },
                # Voice quality settings
                "voice_temperature": kwargs.get("voice_temperature", 1),
                "voice_speed": kwargs.get("voice_speed", 1),
                "volume": kwargs.get("volume", 1),
                # Conversation behavior
                "responsiveness": responsiveness,
                "interruption_sensitivity": interruption_sensitivity,
                "enable_backchannel": enable_backchannel,
                "backchannel_frequency": kwargs.get("backchannel_frequency", 0.9),
                "backchannel_words": kwargs.get("backchannel_words", ["yeah", "uh-huh"]),
                # Call management
                "reminder_trigger_ms": kwargs.get("reminder_trigger_ms", 10000),
                "reminder_max_count": kwargs.get("reminder_max_count", 2),
                "end_call_after_silence_ms": kwargs.get("end_call_after_silence_ms", 600000),
                "max_call_duration_ms": kwargs.get("max_call_duration_ms", 3600000),
                # Audio processing
                "normalize_for_speech": kwargs.get("normalize_for_speech", True),
                # Data and features
                "boosted_keywords": kwargs.get("boosted_keywords", []),
                "data_storage_setting": kwargs.get("data_storage_setting", "everything"),
            }
            
            # Add optional ambient sound
            if kwargs.get("ambient_sound"):
                agent_config["ambient_sound"] = kwargs["ambient_sound"]
                agent_config["ambient_sound_volume"] = kwargs.get("ambient_sound_volume", 1)
            
            # Add webhook URL
            if kwargs.get("webhook_url"):
                agent_config["webhook_url"] = kwargs["webhook_url"]
            
            # Add voicemail handling
            if kwargs.get("voicemail_message"):
                agent_config["voicemail_option"] = {
                    "action": {
                        "type": "static_text",
                        "text": kwargs["voicemail_message"]
                    }
                }
            
            # Make HTTP request to create agent
            async with httpx.AsyncClient() as http_client:
                response = await http_client.post(
                    f"{self.base_url}/create-agent",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=agent_config,
                    timeout=30.0
                )
                
                if response.status_code not in [200, 201]:
                    raise RetellAPIError(f"Failed to create agent: {response.text}")
                
                result = response.json()
                
                return {
                    "agent_id": result.get("agent_id"),
                    "agent_name": agent_name,
                    "voice_id": voice_id,
                    "llm_id": llm_id
                }
            
        except httpx.HTTPError as e:
            raise RetellAPIError(f"HTTP error creating agent: {str(e)}")
        except Exception as e:
            raise RetellAPIError(f"Failed to create agent: {str(e)}")
    
    async def update_agent(self, agent_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update an existing Retell agent
        
        Note: Only basic fields like agent_name can be updated via SDK
        """
        try:
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            
            if not update_data:
                return {"agent_id": agent_id, "updated": False}
            
            agent_response = self.client.agent.update(
                agent_id=agent_id,
                **update_data
            )
            
            return {
                "agent_id": agent_response.agent_id,
                "updated": True
            }
            
        except Exception as e:
            raise RetellAPIError(f"Failed to update agent: {str(e)}")
    
    async def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Retrieve agent details by ID"""
        try:
            agent_response = self.client.agent.retrieve(agent_id=agent_id)
            return {
                "agent_id": agent_response.agent_id,
                "agent_name": getattr(agent_response, 'agent_name', None),
                "voice_id": getattr(agent_response, 'voice_id', None),
            }
        except Exception as e:
            raise RetellAPIError(f"Failed to get agent: {str(e)}")
    
    async def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent"""
        try:
            self.client.agent.delete(agent_id=agent_id)
            return True
        except Exception as e:
            raise RetellAPIError(f"Failed to delete agent: {str(e)}")
    
    # ==================== Web Call Management ====================
    
    async def create_web_call(
        self,
        agent_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        retell_llm_dynamic_variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a web call (browser-based voice call)
        
        Web calls don't require phone numbers and are perfect for:
        - Testing and development
        - Browser-based demos
        - Web applications with voice interfaces
        
        Args:
            agent_id: The Retell agent ID to use
            metadata: Optional metadata to attach to the call
            retell_llm_dynamic_variables: Dynamic variables for LLM personalization
            
        Returns:
            Dict containing:
            - access_token: Token for frontend to initiate the call
            - call_id: Unique call identifier
            - sample_rate: Audio sample rate (typically 24000)
            - agent_id: Echo of the agent ID used
        """
        try:
            payload = {"agent_id": agent_id}
            
            if metadata:
                payload["metadata"] = metadata
            
            if retell_llm_dynamic_variables:
                payload["retell_llm_dynamic_variables"] = retell_llm_dynamic_variables
            
            async with httpx.AsyncClient() as http_client:
                response = await http_client.post(
                    f"{self.base_url}/v2/create-web-call",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code not in [200, 201]:
                    raise RetellAPIError(f"Failed to create web call: {response.text}")
                
                result = response.json()
                
                return {
                    "access_token": result.get("access_token"),
                    "call_id": result.get("call_id"),
                    "sample_rate": result.get("sample_rate", 24000),
                    "agent_id": agent_id
                }
            
        except httpx.HTTPError as e:
            raise RetellAPIError(f"HTTP error creating web call: {str(e)}")
        except Exception as e:
            raise RetellAPIError(f"Failed to create web call: {str(e)}")
    
    # ==================== Phone Call Management ====================
    
    async def create_phone_call(
        self,
        agent_id: str,
        to_number: str,
        from_number: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        retell_llm_dynamic_variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Initiate an outbound phone call
        
        Note: Requires a phone number configured in your Retell account
        
        Args:
            agent_id: The Retell agent ID to use
            to_number: Destination phone number (E.164 format)
            from_number: Caller ID number (optional if default is set)
            metadata: Optional metadata to attach to the call
            retell_llm_dynamic_variables: Dynamic variables for LLM personalization
            
        Returns:
            Dict with call_id, agent_id, to_number, and status
        """
        try:
            call_config = {
                "agent_id": agent_id,
                "to_number": to_number,
            }
            
            # Handle from_number requirement
            if from_number:
                call_config["from_number"] = from_number
            else:
                default_from = getattr(settings, 'RETELL_FROM_NUMBER', None)
                if default_from:
                    call_config["from_number"] = default_from
                else:
                    raise RetellAPIError(
                        "from_number is required for phone calls. "
                        "Either pass it in the request or set RETELL_FROM_NUMBER "
                        "in environment variables."
                    )
            
            if metadata:
                call_config["metadata"] = metadata
            
            if retell_llm_dynamic_variables:
                call_config["retell_llm_dynamic_variables"] = retell_llm_dynamic_variables
            
            call_response = self.client.call.create_phone_call(**call_config)
            
            return {
                "call_id": call_response.call_id,
                "agent_id": agent_id,
                "to_number": to_number,
                "status": getattr(call_response, 'call_status', 'initiated')
            }
            
        except Exception as e:
            raise RetellAPIError(f"Failed to create phone call: {str(e)}")
    
    async def get_call(self, call_id: str) -> Dict[str, Any]:
        """
        Retrieve call details including transcript and recording
        
        Args:
            call_id: The call ID to retrieve
            
        Returns:
            Dict with call details, status, transcript, and recording URL
        """
        try:
            call_response = self.client.call.retrieve(call_id=call_id)
            
            return {
                "call_id": call_response.call_id,
                "agent_id": getattr(call_response, 'agent_id', None),
                "call_status": getattr(call_response, 'call_status', None),
                "start_timestamp": getattr(call_response, 'start_timestamp', None),
                "end_timestamp": getattr(call_response, 'end_timestamp', None),
                "transcript": getattr(call_response, 'transcript', None),
                "recording_url": getattr(call_response, 'recording_url', None),
            }
            
        except Exception as e:
            raise RetellAPIError(f"Failed to get call: {str(e)}")
    
    async def list_calls(
        self,
        limit: int = 50,
        sort_order: str = "descending"
    ) -> Dict[str, Any]:
        """
        List recent calls with pagination
        
        Args:
            limit: Number of calls to return (max 50)
            sort_order: "ascending" or "descending" by date
            
        Returns:
            Dict with list of calls
        """
        try:
            calls_response = self.client.call.list(
                limit=limit,
                sort_order=sort_order
            )
            
            return {
                "calls": [
                    {
                        "call_id": call.call_id,
                        "agent_id": getattr(call, 'agent_id', None),
                        "call_status": getattr(call, 'call_status', None),
                        "start_timestamp": getattr(call, 'start_timestamp', None),
                    }
                    for call in calls_response
                ]
            }
            
        except Exception as e:
            raise RetellAPIError(f"Failed to list calls: {str(e)}")
    
    # ==================== LLM Management ====================
    
    async def create_llm(
        self,
        general_prompt: str,
        begin_message: Optional[str] = None,
        general_tools: Optional[List] = None,
        states: Optional[List] = None,
        starting_state: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a Retell LLM configuration
        
        The LLM defines the conversation logic, prompts, and behavior
        
        Args:
            general_prompt: Main system prompt for the LLM
            begin_message: Optional first message from agent
            general_tools: Optional list of tools/functions for the LLM
            states: Optional conversation states for complex flows
            starting_state: Optional starting state name
            **kwargs: Additional LLM configuration options
            
        Returns:
            Dict with llm_id
        """
        try:
            llm_config = {"general_prompt": general_prompt}
            
            if begin_message:
                llm_config["begin_message"] = begin_message
            
            if general_tools:
                llm_config["general_tools"] = general_tools
            
            if states:
                llm_config["states"] = states
                
            if starting_state:
                llm_config["starting_state"] = starting_state
            
            # Add any additional configuration
            llm_config.update(kwargs)
            
            llm_response = self.client.llm.create(**llm_config)
            
            return {"llm_id": llm_response.llm_id}
            
        except Exception as e:
            raise RetellAPIError(f"Failed to create LLM: {str(e)}")


# Singleton instance for application-wide use
retell_service = RetellService()