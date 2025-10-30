# backend/app/api/routes/agent.py
from fastapi import APIRouter, HTTPException, status
from typing import List
from uuid import UUID

from app.models.schemas import (
    AgentConfig, AgentConfigCreate, AgentConfigUpdate,
    SuccessResponse, ErrorResponse
)
from app.services.database import db_service
from app.services.retell_service import retell_service
from app.core.exceptions import RetellAPIError
from app.core.config import settings

router = APIRouter(prefix="/agents", tags=["agents"])

@router.post(
    "",
    response_model=AgentConfig,
    status_code=status.HTTP_201_CREATED,
    summary="Create new agent configuration"
)
async def create_agent_config(config: AgentConfigCreate):
    """
    Create a new agent configuration and corresponding Retell AI agent
    with full support for advanced voice settings
    """
    try:
        # Check if RETELL_LLM_ID is configured
        llm_id = getattr(settings, 'RETELL_LLM_ID', None)
        
        # If no pre-configured LLM, create one dynamically with the system prompt
        if not llm_id:
            try:
                llm_response = await retell_service.create_llm(
                    general_prompt=config.system_prompt,
                    begin_message="Hi, this is dispatch calling."
                )
                llm_id = llm_response.get("llm_id")
                print(f"Created dynamic LLM: {llm_id}")
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create LLM: {str(e)}"
                )
        
        # Create agent in Retell AI with full advanced settings
        retell_agent = await retell_service.create_agent(
            agent_name=config.name,
            llm_id=llm_id,
            voice_id="11labs-Adrian",
            language="en-US",
            # Advanced voice settings from config
            enable_backchannel=config.backchanneling,
            interruption_sensitivity=config.interruption_sensitivity,
            responsiveness=0.8,
            # Additional settings
            backchannel_words=["yeah", "uh-huh", "mm-hmm"] if config.filler_words else [],
            reminder_trigger_ms=10000,
            reminder_max_count=2,
            end_call_after_silence_ms=600000,
            normalize_for_speech=True,
        )
        
        # Store configuration in database with Retell agent ID
        config_dict = config.model_dump()
        config_dict["retell_agent_id"] = retell_agent.get("agent_id")
        
        db_config = await db_service.create_agent_config(config_dict)
        
        return AgentConfig(**db_config)
        
    except RetellAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create Retell agent: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create agent configuration: {str(e)}"
        )

@router.get(
    "",
    response_model=List[AgentConfig],
    summary="List all agent configurations"
)
async def list_agent_configs():
    """
    Retrieve all agent configurations
    """
    try:
        configs = await db_service.list_agent_configs()
        return [AgentConfig(**config) for config in configs]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list agent configurations: {str(e)}"
        )

@router.get(
    "/{config_id}",
    response_model=AgentConfig,
    summary="Get agent configuration by ID"
)
async def get_agent_config(config_id: UUID):
    """
    Retrieve a specific agent configuration
    """
    try:
        config = await db_service.get_agent_config(config_id)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent configuration {config_id} not found"
            )
        return AgentConfig(**config)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent configuration: {str(e)}"
        )

@router.patch(
    "/{config_id}",
    response_model=AgentConfig,
    summary="Update agent configuration"
)
async def update_agent_config(config_id: UUID, update: AgentConfigUpdate):
    """
    Update an existing agent configuration
    """
    try:
        # Check if config exists
        existing_config = await db_service.get_agent_config(config_id)
        if not existing_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent configuration {config_id} not found"
            )
        
        # Update in database
        update_dict = update.model_dump(exclude_none=True)
        updated_config = await db_service.update_agent_config(config_id, update_dict)
        
        # Update Retell agent if basic fields changed
        retell_agent_id = existing_config.get("retell_agent_id")
        if retell_agent_id:
            retell_update = {}
            
            if "name" in update_dict:
                retell_update["agent_name"] = update_dict["name"]
            
            if retell_update:
                try:
                    await retell_service.update_agent(retell_agent_id, **retell_update)
                except Exception as e:
                    print(f"Warning: Failed to update Retell agent: {e}")
        
        return AgentConfig(**updated_config)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update agent configuration: {str(e)}"
        )

@router.delete(
    "/{config_id}",
    response_model=SuccessResponse,
    summary="Delete agent configuration"
)
async def delete_agent_config(config_id: UUID):
    """
    Delete an agent configuration and associated Retell agent
    """
    try:
        # Get config to find Retell agent ID
        config = await db_service.get_agent_config(config_id)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent configuration {config_id} not found"
            )
        
        # Delete from Retell AI
        if config.get("retell_agent_id"):
            try:
                await retell_service.delete_agent(config["retell_agent_id"])
            except Exception as e:
                print(f"Warning: Failed to delete Retell agent: {e}")
        
        # Delete from database
        success = await db_service.delete_agent_config(config_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete agent configuration"
            )
        
        return SuccessResponse(
            success=True,
            message=f"Agent configuration {config_id} deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete agent configuration: {str(e)}"
        )