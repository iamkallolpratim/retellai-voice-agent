# backend/app/api/routes/calls.py
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from uuid import UUID

from app.models.schemas import (
    CallCreate, Call, CallStatus, CallResult,
    SuccessResponse
)
from app.services.database import db_service
from app.services.retell_service import retell_service
from app.services.agent_service import agent_prompt_service
from app.core.exceptions import RetellAPIError

router = APIRouter(prefix="/calls", tags=["calls"])

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Trigger a new web call"
)
async def create_call(call_data: CallCreate):
    """
    Create a new web call session
    
    Returns an access_token that the frontend can use to initiate the call
    """
    try:
        # Get agent configuration
        agent_config = await db_service.get_agent_config(call_data.agent_config_id)
        if not agent_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent configuration {call_data.agent_config_id} not found"
            )
        
        # Get the Retell agent ID
        retell_agent_id = agent_config.get("retell_agent_id")
        if not retell_agent_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Agent configuration does not have a Retell agent ID"
            )
        
        # Prepare dynamic variables for the LLM
        retell_llm_dynamic_variables = {
            "driver_name": call_data.driver_name,
            "load_number": call_data.load_number,
        }
        
        # Create web call via Retell FIRST to get the call_id
        retell_web_call = await retell_service.create_web_call(
            agent_id=retell_agent_id,
            metadata={
                "driver_name": call_data.driver_name,
                "load_number": call_data.load_number,
                "scenario_type": agent_config["scenario_type"]
            },
            retell_llm_dynamic_variables=retell_llm_dynamic_variables
        )
        
        # Now create call record in database with the Retell call_id
        call_dict = {
            "agent_config_id": str(call_data.agent_config_id),
            "driver_name": call_data.driver_name,
            "phone_number": call_data.phone_number,  # Keep for reference
            "load_number": call_data.load_number,
            "retell_call_id": retell_web_call.get("call_id"),
            "status": "pending"  # Use valid status from constraint
        }
        db_call = await db_service.create_call(call_dict)
        
        # Return call details with access_token for frontend
        return {
            **Call(**db_call).model_dump(),
            "access_token": retell_web_call.get("access_token"),
            "sample_rate": retell_web_call.get("sample_rate")
        }
        
    except HTTPException:
        raise
    except RetellAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate web call: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create call: {str(e)}"
        )

@router.get(
    "",
    response_model=List[Call],
    summary="List all calls"
)
async def list_calls(limit: int = 50, offset: int = 0):
    """
    Retrieve all calls with pagination
    """
    try:
        calls = await db_service.list_calls(limit=limit, offset=offset)
        return [Call(**call) for call in calls]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list calls: {str(e)}"
        )

@router.get(
    "/{call_id}",
    response_model=Call,
    summary="Get call by ID"
)
async def get_call(call_id: UUID):
    """
    Retrieve a specific call
    """
    try:
        call = await db_service.get_call(call_id)
        if not call:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Call {call_id} not found"
            )
        return Call(**call)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get call: {str(e)}"
        )

@router.get(
    "/{call_id}/status",
    response_model=CallStatus,
    summary="Get call status"
)
async def get_call_status(call_id: UUID):
    """
    Get the current status of a call
    """
    try:
        call = await db_service.get_call(call_id)
        if not call:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Call {call_id} not found"
            )
        
        # If call has Retell ID, get live status from Retell
        if call.get("retell_call_id"):
            try:
                retell_call = await retell_service.get_call(call["retell_call_id"])
                call_status = retell_call.get("call_status")
                
                # Map Retell status to our database status
                status_mapping = {
                    "registered": "pending",
                    "ongoing": "in_progress",
                    "ended": "completed",
                    "error": "failed"
                }
                
                mapped_status = status_mapping.get(call_status, call["status"])
                
                # Update database if status changed
                if mapped_status != call["status"]:
                    update_data = {"status": mapped_status}
                    if mapped_status == "completed":
                        update_data["completed_at"] = retell_call.get("end_timestamp")
                    
                    await db_service.update_call(call_id, update_data)
                    call["status"] = mapped_status
                    
            except Exception as e:
                print(f"Warning: Failed to get live call status: {e}")
                # Continue with database status if Retell API fails
        
        return CallStatus(**call)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get call status: {str(e)}"
        )

@router.get(
    "/{call_id}/result",
    response_model=CallResult,
    summary="Get call result"
)
async def get_call_result(call_id: UUID):
    """
    Retrieve the structured result of a completed call
    """
    try:
        result = await db_service.get_call_result(call_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Call result for {call_id} not found"
            )
        return CallResult(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get call result: {str(e)}"
        )