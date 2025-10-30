from fastapi import APIRouter, HTTPException, Request, status
from typing import Dict, Any
import hmac
import hashlib

from app.models.schemas import RetellCallEnded, RetellCallStarted
from app.services.database import db_service
from app.services.post_processor import post_processor
from app.core.config import settings
from app.core.exceptions import PostProcessingError
from uuid import UUID

router = APIRouter(prefix="/webhook", tags=["webhook"])

def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """
    Verify webhook signature from Retell AI
    """
    if not settings.WEBHOOK_SECRET:
        return True  # Skip verification in development
    
    expected_signature = hmac.new(
        settings.WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

@router.post(
    "/retell",
    status_code=status.HTTP_200_OK,
    summary="Retell AI webhook endpoint"
)
async def retell_webhook(request: Request):
    """
    Handle webhook events from Retell AI
    
    Events:
    - call_started: Call has been initiated
    - call_ended: Call has completed
    - call_analyzed: Call analysis is ready
    """
    try:
        # Get raw body for signature verification
        body = await request.body()
        signature = request.headers.get("X-Retell-Signature", "")
        
        # Verify signature
        if not verify_webhook_signature(body, signature):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
        
        # Parse payload
        payload = await request.json()
        event_type = payload.get("event")
        
        if event_type == "call_started":
            await handle_call_started(payload)
        elif event_type == "call_ended":
            await handle_call_ended(payload)
        elif event_type == "call_analyzed":
            await handle_call_analyzed(payload)
        else:
            print(f"Unknown event type: {event_type}")
        
        return {"status": "success"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing failed: {str(e)}"
        )

async def handle_call_started(payload: Dict[str, Any]):
    """
    Handle call_started event
    """
    event = RetellCallStarted(**payload)
    
    # Find call by Retell call ID
    call = await db_service.get_call_by_retell_id(event.call_id)
    if call:
        await db_service.update_call(
            UUID(call["id"]),
            {"status": "in_progress"}
        )
        print(f"Call {call['id']} started")

async def handle_call_ended(payload: Dict[str, Any]):
    """
    Handle call_ended event and process transcript
    """
    event = RetellCallEnded(**payload)
    
    # Find call by Retell call ID
    call = await db_service.get_call_by_retell_id(event.call_id)
    if not call:
        print(f"Call not found for Retell ID: {event.call_id}")
        return
    
    # Update call status
    await db_service.update_call(
        UUID(call["id"]),
        {
            "status": "completed",
            "completed_at": event.timestamp.isoformat()
        }
    )
    
    # Process transcript if available
    if event.transcript:
        await process_call_transcript(
            call_id=UUID(call["id"]),
            transcript=event.transcript,
            scenario_type=call.get("scenario_type", "driver_checkin"),
            metadata=payload
        )
    
    print(f"Call {call['id']} ended")

async def handle_call_analyzed(payload: Dict[str, Any]):
    """
    Handle call_analyzed event
    """
    call_id = payload.get("call_id")
    
    # Find call by Retell call ID
    call = await db_service.get_call_by_retell_id(call_id)
    if not call:
        print(f"Call not found for Retell ID: {call_id}")
        return
    
    # Process if not already processed
    existing_result = await db_service.get_call_result(UUID(call["id"]))
    if not existing_result and payload.get("transcript"):
        await process_call_transcript(
            call_id=UUID(call["id"]),
            transcript=payload["transcript"],
            scenario_type=call.get("scenario_type", "driver_checkin"),
            metadata=payload
        )
    
    print(f"Call {call['id']} analyzed")

async def process_call_transcript(
    call_id: UUID,
    transcript: str,
    scenario_type: str,
    metadata: Dict[str, Any]
):
    """
    Process call transcript and extract structured data
    """
    try:
        # Get agent configuration to determine scenario
        call = await db_service.get_call(call_id)
        if not call:
            return
        
        agent_config = await db_service.get_agent_config(
            UUID(call["agent_config_id"])
        )
        
        if agent_config:
            scenario_type = agent_config["scenario_type"]
        
        # Extract structured data using post-processor
        structured_data = await post_processor.extract_structured_data(
            transcript=transcript,
            scenario_type=scenario_type
        )
        
        # Calculate duration
        duration = 0
        if metadata.get("start_time") and metadata.get("end_time"):
            duration = await post_processor.calculate_call_duration(
                metadata["start_time"],
                metadata["end_time"]
            )
        elif metadata.get("call_analysis", {}).get("call_duration_seconds"):
            duration = metadata["call_analysis"]["call_duration_seconds"]
        
        # Store result
        result_data = {
            "call_id": str(call_id),
            "call_outcome": structured_data.get("call_outcome", "Unknown"),
            "structured_data": structured_data,
            "full_transcript": transcript,
            "duration": duration
        }
        
        await db_service.create_call_result(result_data)
        print(f"Processed transcript for call {call_id}")
        
    except PostProcessingError as e:
        print(f"Post-processing error for call {call_id}: {str(e)}")
        # Store raw transcript even if processing fails
        await db_service.create_call_result({
            "call_id": str(call_id),
            "call_outcome": "Processing Failed",
            "structured_data": {"error": str(e)},
            "full_transcript": transcript,
            "duration": 0
        })
    except Exception as e:
        print(f"Error processing transcript for call {call_id}: {str(e)}")