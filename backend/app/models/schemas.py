# backend/app/models/schemas.py
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, Literal
from datetime import datetime
from uuid import UUID

# ==================== Agent Configuration ====================
class AgentConfigBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    scenario_type: Literal["driver_checkin", "emergency_protocol"]
    system_prompt: str = Field(..., min_length=10)
    backchanneling: bool = True
    interruption_sensitivity: float = Field(0.7, ge=0.0, le=1.0)
    filler_words: bool = True

class AgentConfigCreate(AgentConfigBase):
    pass

class AgentConfigUpdate(BaseModel):
    name: Optional[str] = None
    scenario_type: Optional[Literal["driver_checkin", "emergency_protocol"]] = None
    system_prompt: Optional[str] = None
    backchanneling: Optional[bool] = None
    interruption_sensitivity: Optional[float] = None
    filler_words: Optional[bool] = None

class AgentConfig(AgentConfigBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ==================== Call Management ====================
class CallCreate(BaseModel):
    agent_config_id: UUID
    driver_name: str = Field(..., min_length=1, max_length=255)
    phone_number: str = Field(..., pattern=r'^\+?1?\d{10,15}$')
    load_number: str = Field(..., min_length=1, max_length=50)
    
    @validator('phone_number')
    def format_phone(cls, v):
        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, v))
        # Ensure it starts with country code
        if not v.startswith('+'):
            digits = '1' + digits if len(digits) == 10 else digits
        return '+' + digits

class CallStatus(BaseModel):
    id: UUID
    status: Literal["pending", "in_progress", "completed", "failed"]
    retell_call_id: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

class Call(BaseModel):
    id: UUID
    agent_config_id: UUID
    driver_name: str
    phone_number: str
    load_number: str
    retell_call_id: Optional[str]
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# ==================== Call Results ====================
class DriverCheckinResult(BaseModel):
    call_outcome: Literal["In-Transit Update", "Arrival Confirmation", "Delayed"]
    driver_status: Literal["Driving", "Delayed", "Arrived", "Unloading"]
    current_location: str
    eta: Optional[str] = None
    delay_reason: Optional[str] = "None"
    unloading_status: str = "N/A"
    pod_reminder_acknowledged: bool

class EmergencyResult(BaseModel):
    call_outcome: Literal["Emergency Escalation"]
    emergency_type: Literal["Accident", "Breakdown", "Medical", "Other"]
    safety_status: str
    injury_status: str
    emergency_location: str
    load_secure: bool
    escalation_status: str = "Connected to Human Dispatcher"

class CallResultCreate(BaseModel):
    call_id: UUID
    call_outcome: str
    structured_data: Dict[str, Any]
    full_transcript: str
    duration: int  # in seconds

class CallResult(CallResultCreate):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== Retell Webhook Payloads ====================
class RetellWebhookEvent(BaseModel):
    event: str
    call_id: str
    timestamp: datetime

class RetellCallStarted(RetellWebhookEvent):
    event: Literal["call_started"]
    agent_id: str

class RetellCallEnded(RetellWebhookEvent):
    event: Literal["call_ended"]
    transcript: str
    recording_url: Optional[str] = None
    call_analysis: Optional[Dict[str, Any]] = None
    end_reason: Optional[str] = None

class RetellCallAnalyzed(RetellWebhookEvent):
    event: Literal["call_analyzed"]
    transcript: str
    call_analysis: Dict[str, Any]

# ==================== Response Models ====================
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

class SuccessResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None