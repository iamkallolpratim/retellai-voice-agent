# backend/app/services/database.py
from supabase import create_client, Client
from app.core.config import settings
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class DatabaseService:
    def __init__(self):
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
    
    # ==================== Agent Configuration ====================
    async def create_agent_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new agent configuration"""
        response = self.client.table("agent_configurations").insert(config_data).execute()
        return response.data[0] if response.data else None
    
    async def get_agent_config(self, config_id: UUID) -> Optional[Dict[str, Any]]:
        """Get agent configuration by ID"""
        response = self.client.table("agent_configurations")\
            .select("*")\
            .eq("id", str(config_id))\
            .execute()
        return response.data[0] if response.data else None
    
    async def list_agent_configs(self) -> List[Dict[str, Any]]:
        """List all agent configurations"""
        response = self.client.table("agent_configurations")\
            .select("*")\
            .order("created_at", desc=True)\
            .execute()
        return response.data or []
    
    async def update_agent_config(
        self, 
        config_id: UUID, 
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update agent configuration"""
        update_data["updated_at"] = datetime.utcnow().isoformat()
        response = self.client.table("agent_configurations")\
            .update(update_data)\
            .eq("id", str(config_id))\
            .execute()
        return response.data[0] if response.data else None
    
    async def delete_agent_config(self, config_id: UUID) -> bool:
        """Delete agent configuration"""
        response = self.client.table("agent_configurations")\
            .delete()\
            .eq("id", str(config_id))\
            .execute()
        return len(response.data) > 0
    
    # ==================== Call Management ====================
    async def create_call(self, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new call record"""
        response = self.client.table("calls").insert(call_data).execute()
        return response.data[0] if response.data else None
    
    async def get_call(self, call_id: UUID) -> Optional[Dict[str, Any]]:
        """Get call by ID"""
        response = self.client.table("calls")\
            .select("*")\
            .eq("id", str(call_id))\
            .execute()
        return response.data[0] if response.data else None
    
    async def get_call_by_retell_id(self, retell_call_id: str) -> Optional[Dict[str, Any]]:
        """Get call by Retell call ID"""
        response = self.client.table("calls")\
            .select("*")\
            .eq("retell_call_id", retell_call_id)\
            .execute()
        return response.data[0] if response.data else None
    
    async def update_call(
        self, 
        call_id: UUID, 
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update call record"""
        response = self.client.table("calls")\
            .update(update_data)\
            .eq("id", str(call_id))\
            .execute()
        return response.data[0] if response.data else None
    
    async def list_calls(
        self, 
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List calls with pagination"""
        response = self.client.table("calls")\
            .select("*")\
            .order("created_at", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        return response.data or []
    
    # ==================== Call Results ====================
    async def create_call_result(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create call result"""
        response = self.client.table("call_results").insert(result_data).execute()
        return response.data[0] if response.data else None
    
    async def get_call_result(self, call_id: UUID) -> Optional[Dict[str, Any]]:
        """Get call result by call ID"""
        response = self.client.table("call_results")\
            .select("*")\
            .eq("call_id", str(call_id))\
            .execute()
        return response.data[0] if response.data else None

# Singleton instance
db_service = DatabaseService()