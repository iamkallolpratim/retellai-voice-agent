import json
from typing import Dict, Any
import google.generativeai as genai
from app.core.config import settings

class TranscriptProcessor:
    def __init__(self):
        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')  # Fast and free
        # or use 'gemini-1.5-pro' for better quality
    
    async def extract_check_in_data(self, transcript: str) -> Dict[str, Any]:
        """Extract structured data for check-in scenario"""
        
        prompt = f"""
        Analyze this driver check-in call transcript and extract structured data.
        
        Transcript:
        {transcript}
        
        Extract the following information in JSON format:
        {{
            "call_outcome": "In-Transit Update" or "Arrival Confirmation",
            "driver_status": "Driving" or "Delayed" or "Arrived" or "Unloading",
            "current_location": "exact location mentioned or Unknown",
            "eta": "estimated arrival time or Unknown",
            "delay_reason": "reason for delay or None",
            "unloading_status": "status or N/A",
            "pod_reminder_acknowledged": true or false
        }}
        
        Rules:
        - If information is not mentioned in transcript, use "Unknown" or "N/A"
        - Return ONLY valid JSON, no markdown, no explanation, no other text
        - Ensure all fields are present
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # Clean response (remove markdown if present)
            result_text = response.text.strip()
            if result_text.startswith("```json"):
                result_text = result_text.replace("```json", "").replace("```", "").strip()
            
            return json.loads(result_text)
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {e}")
            print(f"Response was: {response.text}")
            # Return default structure
            return {
                "call_outcome": "Unknown",
                "driver_status": "Unknown",
                "current_location": "Unknown",
                "eta": "Unknown",
                "delay_reason": "None",
                "unloading_status": "N/A",
                "pod_reminder_acknowledged": False
            }
        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            raise
    
    async def extract_emergency_data(self, transcript: str) -> Dict[str, Any]:
        """Extract structured data for emergency scenario"""
        
        prompt = f"""
        Analyze this emergency call transcript and extract structured data.
        
        Transcript:
        {transcript}
        
        Extract the following information in JSON format:
        {{
            "call_outcome": "Emergency Escalation",
            "emergency_type": "Accident" or "Breakdown" or "Medical" or "Other",
            "safety_status": "description of safety status",
            "injury_status": "description of injuries or None reported",
            "emergency_location": "exact location or Unknown",
            "load_secure": true or false,
            "escalation_status": "Connected to Human Dispatcher" or "Pending"
        }}
        
        Rules:
        - If information is not mentioned, use "Unknown" or reasonable defaults
        - Return ONLY valid JSON, no markdown, no explanation
        - Ensure all fields are present
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # Clean response
            result_text = response.text.strip()
            if result_text.startswith("```json"):
                result_text = result_text.replace("```json", "").replace("```", "").strip()
            
            return json.loads(result_text)
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {e}")
            print(f"Response was: {response.text}")
            # Return default emergency structure
            return {
                "call_outcome": "Emergency Escalation",
                "emergency_type": "Other",
                "safety_status": "Unknown",
                "injury_status": "Unknown",
                "emergency_location": "Unknown",
                "load_secure": False,
                "escalation_status": "Pending"
            }
        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            raise
    
    async def detect_scenario_type(self, transcript: str) -> str:
        """Detect if this is an emergency or regular check-in"""
        
        emergency_keywords = [
            'emergency', 'accident', 'crash', 'breakdown', 'blowout',
            'medical', 'injured', 'help', 'urgent', 'ambulance'
        ]
        
        transcript_lower = transcript.lower()
        
        # Simple keyword detection
        for keyword in emergency_keywords:
            if keyword in transcript_lower:
                return "emergency"
        
        return "check-in"


# Usage function
async def extract_structured_data(
    transcript: str, 
    call_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Main function to extract structured data from call transcript
    """
    processor = TranscriptProcessor()
    
    # Get scenario type from metadata or detect it
    scenario_type = call_data.get("metadata", {}).get("scenario_type")
    
    if not scenario_type:
        scenario_type = await processor.detect_scenario_type(transcript)
    
    print(f"📊 Processing {scenario_type} scenario")
    
    if scenario_type == "emergency":
        return await processor.extract_emergency_data(transcript)
    else:
        return await processor.extract_check_in_data(transcript)