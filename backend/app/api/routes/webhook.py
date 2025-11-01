# backend/app/api/routes/webhooks.py
from fastapi import APIRouter, Request, Header
from typing import Dict, Any, Optional
from datetime import datetime
from app.services.database import db_service
from app.services.transcript_processor import extract_structured_data
import uuid

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def timestamp_to_iso(timestamp_ms: int) -> str:
    """Convert Unix timestamp (milliseconds) to ISO format"""
    if not timestamp_ms:
        return datetime.utcnow().isoformat()
    try:
        # Convert milliseconds to seconds
        timestamp_sec = timestamp_ms / 1000
        dt = datetime.utcfromtimestamp(timestamp_sec)
        return dt.isoformat()
    except:
        return datetime.utcnow().isoformat()


@router.post("/retell")
async def retell_webhook(
    request: Request,
    x_retell_signature: Optional[str] = Header(None)
):
    """Handle Retell AI webhooks"""
    try:
        data = await request.json()
        event_type = data.get("event")
        call_data = data.get("call", {})
        retell_call_id = call_data.get("call_id")
        
        print(f"\n{'='*60}")
        print(f"📞 Webhook Event: {event_type}")
        print(f"🆔 Call ID: {retell_call_id}")
        print(f"{'='*60}\n")
        
        if not retell_call_id:
            print("⚠️ No call_id in webhook payload")
            return {"status": "success", "message": "No call_id provided"}
        
        # Handle different event types - NO await
        if event_type == "call_started":
            handle_call_started(retell_call_id, call_data)
        elif event_type == "call_ended":
            await handle_call_ended(retell_call_id, call_data)
        elif event_type == "call_analyzed":
            handle_call_analyzed(retell_call_id, call_data)
        else:
            print(f"⚠️ Unknown event type: {event_type}")
        
        return {"status": "success", "event": event_type}
        
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}


def handle_call_started(retell_call_id: str, call_data: Dict[str, Any]):
    """Handle call_started event"""
    try:
        print(f"🟢 Processing call_started for {retell_call_id}")
        
        call = db_service.get_call_by_retell_id(retell_call_id)
        
        if not call:
            print(f"⚠️ Call not found in database: {retell_call_id}")
            return
        
        db_service.update_call(
            uuid.UUID(call["id"]),
            {"status": "in_progress"}
        )
        
        print(f"✅ Call {retell_call_id} marked as in_progress")
        
    except Exception as e:
        print(f"❌ Error in handle_call_started: {e}")
        import traceback
        traceback.print_exc()


async def handle_call_ended(retell_call_id: str, call_data: Dict[str, Any]):
    """Handle call_ended event"""
    try:
        print(f"🔴 Processing call_ended for {retell_call_id}")
        
        call = db_service.get_call_by_retell_id(retell_call_id)
        
        if not call:
            print(f"⚠️ Call not found in database: {retell_call_id}")
            return
        
        call_id = uuid.UUID(call["id"])
        transcript = call_data.get("transcript", "")
        
        print(f"📝 Transcript length: {len(transcript)} characters")
        
        # Convert timestamp
        end_timestamp = call_data.get("end_timestamp")
        completed_at = timestamp_to_iso(end_timestamp) if end_timestamp else None
        
        # Update call status
        update_data = {"status": "completed"}
        if completed_at:
            update_data["completed_at"] = completed_at
        
        db_service.update_call(call_id, update_data)
        print(f"✅ Call {retell_call_id} marked as completed")
        
        # Extract structured data
        if transcript:
            print(f"🤖 Extracting structured data with Gemini...")
            
            structured_data = await extract_structured_data(transcript, call_data)
            print(f"✅ Structured data: {structured_data}")
            
            # Calculate duration
            duration_ms = call_data.get("duration_ms")
            if duration_ms:
                duration_seconds = duration_ms // 1000
            else:
                start = call_data.get("start_timestamp", 0)
                end = call_data.get("end_timestamp", 0)
                duration_seconds = (end - start) // 1000 if start and end else 0
            
            # Use full_transcript instead of transcript
            db_service.create_call_result({
                "call_id": str(call_id),
                "full_transcript": transcript,  # Changed from "transcript" to "full_transcript"
                "structured_data": structured_data,
                "call_duration": duration_seconds
            })
            
            print(f"✅ Call result saved for {retell_call_id}")
        else:
            print(f"⚠️ No transcript available, creating result with empty transcript")
            # If no transcript, create with empty string to satisfy NOT NULL constraint
            db_service.create_call_result({
                "call_id": str(call_id),
                "full_transcript": "",  # Empty string instead of null
                "structured_data": {},
                "call_duration": 0
            })
        
    except Exception as e:
        print(f"❌ Error in handle_call_ended: {e}")
        import traceback
        traceback.print_exc()


def handle_call_analyzed(retell_call_id: str, call_data: Dict[str, Any]):
    """Handle call_analyzed event"""
    try:
        print(f"📊 Processing call_analyzed for {retell_call_id}")
        
        call = db_service.get_call_by_retell_id(retell_call_id)
        
        if not call:
            print(f"⚠️ Call not found: {retell_call_id}")
            return
        
        call_id = uuid.UUID(call["id"])
        analysis = call_data.get("call_analysis", {})
        
        if not analysis:
            print(f"⚠️ No call_analysis in payload")
            return
        
        print(f"📊 Analysis: {analysis.get('call_summary', '')[:100]}...")
        
        result = db_service.get_call_result(call_id)
        
        if result:
            # Only update fields that exist in your table
            update_data = {}
            
            if analysis.get("call_summary"):
                update_data["call_summary"] = analysis.get("call_summary")
            
            if analysis.get("user_sentiment"):
                update_data["user_sentiment"] = analysis.get("user_sentiment")
            
            # Only add if column exists in your table
            # if analysis.get("call_successful") is not None:
            #     update_data["call_successful"] = analysis.get("call_successful")
            
            if update_data:
                db_service.update_call_result(call_id, update_data)
                print(f"✅ Analysis updated for {retell_call_id}")
        else:
            print(f"⚠️ No call result found for {retell_call_id}")
        
    except Exception as e:
        print(f"❌ Error in handle_call_analyzed: {e}")
        import traceback
        traceback.print_exc()


@router.get("/retell/health")
async def webhook_health():
    """Health check"""
    return {"status": "healthy", "message": "Webhook ready"}