import json
from typing import Dict, Any
import google.generativeai as genai
from app.core.config import settings
from app.core.exceptions import PostProcessingError, GeminiAPIError

class PostProcessorService:
    """
    Service for post-processing call transcripts into structured data using Google Gemini
    """
    
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        
        # Configure generation settings for consistency
        self.generation_config = {
            "temperature": 0.1,  # Low temperature for consistency
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
    
    async def extract_structured_data(
        self,
        transcript: str,
        scenario_type: str
    ) -> Dict[str, Any]:
        """
        Extract structured data from call transcript using Gemini
        """
        if scenario_type == "driver_checkin":
            return await self._extract_checkin_data(transcript)
        elif scenario_type == "emergency_protocol":
            return await self._extract_emergency_data(transcript)
        else:
            raise PostProcessingError(f"Unknown scenario type: {scenario_type}")
    
    async def _extract_checkin_data(self, transcript: str) -> Dict[str, Any]:
        """
        Extract driver check-in data from transcript using Gemini
        """
        system_instruction = """You are a data extraction assistant. Extract structured information from dispatch call transcripts.

Your task: Analyze the transcript and extract the following fields EXACTLY as specified.

Required fields for driver check-in:
- call_outcome: Must be one of "In-Transit Update", "Arrival Confirmation", or "Delayed"
- driver_status: Must be one of "Driving", "Delayed", "Arrived", or "Unloading"
- current_location: Exact location mentioned by driver (e.g., "I-10 near Indio, CA")
- eta: Expected arrival time if mentioned, otherwise null
- delay_reason: Reason for delay if any, otherwise "None"
- unloading_status: Status if arrived (e.g., "In Door 42", "Waiting for Lumper"), otherwise "N/A"
- pod_reminder_acknowledged: true if driver acknowledged POD reminder, false otherwise

IMPORTANT RULES:
1. Use ONLY information explicitly stated in the transcript
2. Use "N/A" for fields that don't apply to the situation
3. Use null for missing information
4. Extract exact quotes when possible
5. Infer call_outcome from the overall conversation context
6. Be precise with locations and times

Return ONLY valid JSON with these exact field names. No explanation, no markdown, just the JSON object."""

        prompt = f"""Extract structured data from this dispatch call transcript:

{transcript}

Return the data as a JSON object with the required fields."""

        try:
            # Create model with system instruction
            model = genai.GenerativeModel(
                model_name=settings.GEMINI_MODEL,
                generation_config=self.generation_config,
                system_instruction=system_instruction
            )
            
            # Generate response
            response = model.generate_content(prompt)
            
            # Extract text and clean markdown if present
            content = response.text.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]  # Remove ```json
            if content.startswith("```"):
                content = content[3:]  # Remove ```
            if content.endswith("```"):
                content = content[:-3]  # Remove ```
            
            content = content.strip()
            
            # Parse JSON
            structured_data = json.loads(content)
            
            # Validate and fill required fields
            required_fields = [
                "call_outcome", "driver_status", "current_location",
                "eta", "delay_reason", "unloading_status", "pod_reminder_acknowledged"
            ]
            
            for field in required_fields:
                if field not in structured_data:
                    structured_data[field] = "N/A" if field != "pod_reminder_acknowledged" else False
            
            return structured_data
            
        except json.JSONDecodeError as e:
            raise PostProcessingError(f"Failed to parse JSON response from Gemini: {e}")
        except Exception as e:
            raise GeminiAPIError(f"Failed to extract checkin data with Gemini: {e}")
    
    async def _extract_emergency_data(self, transcript: str) -> Dict[str, Any]:
        """
        Extract emergency data from transcript using Gemini
        """
        system_instruction = """You are a data extraction assistant specializing in emergency call analysis.

Your task: Extract critical emergency information from the transcript.

Required fields for emergency calls:
- call_outcome: Must be "Emergency Escalation"
- emergency_type: Must be one of "Accident", "Breakdown", "Medical", or "Other"
- safety_status: Driver's safety confirmation (e.g., "Driver confirmed everyone is safe")
- injury_status: Information about injuries (e.g., "No injuries reported")
- emergency_location: Exact location of emergency (e.g., "I-15 North, Mile Marker 123")
- load_secure: true if load is secure, false otherwise
- escalation_status: Must be "Connected to Human Dispatcher" or similar

IMPORTANT RULES:
1. Extract ONLY factual information from the transcript
2. emergency_type must be inferred from the situation described
3. Be precise with safety and injury information
4. If information is unclear, use descriptive text based on what was said
5. Always set escalation_status if the call indicates escalation

Return ONLY valid JSON with these exact field names. No explanation, no markdown, just the JSON object."""

        prompt = f"""Extract emergency data from this dispatch call transcript:

{transcript}

Return the data as a JSON object with the required fields."""

        try:
            # Create model with system instruction
            model = genai.GenerativeModel(
                model_name=settings.GEMINI_MODEL,
                generation_config=self.generation_config,
                system_instruction=system_instruction
            )
            
            # Generate response
            response = model.generate_content(prompt)
            
            # Extract text and clean markdown if present
            content = response.text.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            content = content.strip()
            
            # Parse JSON
            structured_data = json.loads(content)
            
            # Ensure call_outcome is set correctly
            structured_data["call_outcome"] = "Emergency Escalation"
            
            # Validate and fill required fields
            required_fields = [
                "call_outcome", "emergency_type", "safety_status",
                "injury_status", "emergency_location", "load_secure", "escalation_status"
            ]
            
            for field in required_fields:
                if field not in structured_data:
                    if field == "load_secure":
                        structured_data[field] = False
                    elif field == "escalation_status":
                        structured_data[field] = "Pending Escalation"
                    else:
                        structured_data[field] = "Not specified"
            
            return structured_data
            
        except json.JSONDecodeError as e:
            raise PostProcessingError(f"Failed to parse JSON response from Gemini: {e}")
        except Exception as e:
            raise GeminiAPIError(f"Failed to extract emergency data with Gemini: {e}")
    
    async def calculate_call_duration(
        self,
        start_time: str,
        end_time: str
    ) -> int:
        """
        Calculate call duration in seconds
        """
        from datetime import datetime
        
        try:
            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            duration = (end - start).total_seconds()
            return int(duration)
        except Exception:
            return 0

# Singleton instance
post_processor = PostProcessorService()