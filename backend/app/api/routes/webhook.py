from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any
from app.services.database import db_service
from app.services.transcript_processor import extract_structured_data
import uuid

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("/retell")
async def retell_webhook(request: Request):
    """
    Handle Retell AI webhooks for real-time call updates
    """
    try:
        data = await request.json()
        event_type = data.get("event")
        retell_call_id = data.get("call_id")
        
        print(f"📞 Webhook received: {event_type} for call {retell_call_id}")
        
        # Handle different event types
        if event_type == "call_started":
            await handle_call_started(retell_call_id, data)
        elif event_type == "call_ended":
            await handle_call_ended(retell_call_id, data)
        elif event_type == "call_analyzed":
            await handle_call_analyzed(retell_call_id, data)
        
        return {"status": "success"}
        
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def handle_call_started(retell_call_id: str, data: Dict[str, Any]):
    """Update call status to in_progress"""
    try:
        # Find call by retell_call_id
        call = await db_service.get_call_by_retell_id(retell_call_id)
        if call:
            await db_service.update_call(
                uuid.UUID(call["id"]),
                {"status": "in_progress"}
            )
            print(f"✅ Call {retell_call_id} marked as in_progress")
    except Exception as e:
        print(f"❌ Error updating call status: {e}")


async def handle_call_ended(retell_call_id: str, data: Dict[str, Any]):
    """Process completed call and extract structured data"""
    try:
        # Find call by retell_call_id
        call = await db_service.get_call_by_retell_id(retell_call_id)
        if not call:
            print(f"⚠️ Call not found: {retell_call_id}")
            return
        
        call_id = uuid.UUID(call["id"])
        transcript = data.get("transcript", "")
        
        print(f"📝 Processing transcript for call {retell_call_id}")
        
        # Update call status
        await db_service.update_call(call_id, {
            "status": "completed",
            "completed_at": data.get("end_timestamp")
        })
        
        # Extract structured data using Gemini
        structured_data = await extract_structured_data(transcript, data)
        
        print(f"✅ Extracted structured data: {structured_data}")
        
        # Save call result with structured data
        await db_service.create_call_result({
            "call_id": str(call_id),
            "transcript": transcript,
            "structured_data": structured_data,
            "call_duration": data.get("duration_ms", 0) // 1000
        })
        
        print(f"✅ Call result saved for {retell_call_id}")
        
    except Exception as e:
        print(f"❌ Error processing call end: {e}")
        import traceback
        traceback.print_exc()


async def handle_call_analyzed(retell_call_id: str, data: Dict[str, Any]):
    """Handle post-call analysis from Retell"""
    try:
        call = await db_service.get_call_by_retell_id(retell_call_id)
        if not call:
            return
        
        call_id = uuid.UUID(call["id"])
        analysis = data.get("call_analysis", {})
        
        # Update call result with Retell's analysis
        result = await db_service.get_call_result(call_id)
        if result:
            await db_service.update_call_result(call_id, {
                "call_summary": analysis.get("call_summary"),
                "user_sentiment": analysis.get("user_sentiment"),
                "call_successful": analysis.get("call_successful")
            })
            print(f"✅ Analysis saved for {retell_call_id}")
            
    except Exception as e:
        print(f"❌ Error processing analysis: {e}")