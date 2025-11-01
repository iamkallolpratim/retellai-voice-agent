# backend/app/models/schemas.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, Literal
from datetime import datetime
from uuid import UUID

# ==================== Agent Configuration ====================
class AgentConfigBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    scenario_type: Literal["check-in", "emergency"]
    system_prompt: str = Field(..., min_length=10)
    backchanneling: bool = True
    interruption_sensitivity: int = Field(50, ge=0, le=100)
    filler_words: bool = True

class AgentConfigCreate(AgentConfigBase):
    pass

class AgentConfigUpdate(BaseModel):
    name: Optional[str] = None
    scenario_type: Optional[Literal["check-in", "emergency"]] = None
    system_prompt: Optional[str] = None
    backchanneling: Optional[bool] = None
    interruption_sensitivity: Optional[int] = None
    filler_words: Optional[bool] = None

class AgentConfig(AgentConfigBase):
    id: UUID
    retell_agent_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ==================== Call Management ====================
class CallCreate(BaseModel):
    agent_config_id: UUID
    driver_name: str = Field(..., min_length=1, max_length=255)
    phone_number: str = Field(..., min_length=10, max_length=20)
    load_number: str = Field(..., min_length=1, max_length=50)

class CallStatus(BaseModel):
    id: UUID
    status: Literal["pending", "in_progress", "completed", "failed"]
    retell_call_id: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Call(BaseModel):
    id: UUID
    agent_config_id: UUID
    driver_name: str
    phone_number: str
    load_number: str
    retell_call_id: Optional[str] = None
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ==================== Call Results ====================
class DriverCheckinResult(BaseModel):
    call_outcome: Optional[str] = None
    driver_status: Optional[str] = None
    current_location: Optional[str] = None
    eta: Optional[str] = None
    delay_reason: Optional[str] = None
    unloading_status: Optional[str] = None
    pod_reminder_acknowledged: Optional[bool] = None

class EmergencyResult(BaseModel):
    call_outcome: Optional[str] = None
    emergency_type: Optional[str] = None
    safety_status: Optional[str] = None
    injury_status: Optional[str] = None
    emergency_location: Optional[str] = None
    load_secure: Optional[bool] = None
    escalation_status: Optional[str] = None

class CallResultCreate(BaseModel):
    call_id: UUID
    full_transcript: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    call_duration: Optional[int] = None

class CallResult(BaseModel):
    id: UUID
    call_id: UUID
    full_transcript: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    call_duration: Optional[int] = None
    call_summary: Optional[str] = None
    user_sentiment: Optional[str] = None
    call_successful: Optional[bool] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ==================== Retell Webhook Payloads ====================
class RetellWebhookEvent(BaseModel):
    event: str
    call: Dict[str, Any]

class RetellCallStarted(BaseModel):
    event: Literal["call_started"]
    call: Dict[str, Any]

class RetellCallEnded(BaseModel):
    event: Literal["call_ended"]
    call: Dict[str, Any]

class RetellCallAnalyzed(BaseModel):
    event: Literal["call_analyzed"]
    call: Dict[str, Any]

# ==================== Response Models ====================
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

class SuccessResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None