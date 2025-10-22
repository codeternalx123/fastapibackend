from supabase import create_client, Client
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class SupabaseConfig:
    """Supabase configuration and client"""
    
    def __init__(self):
        self.url: str = os.getenv("SUPABASE_URL", "")
        self.key: str = os.getenv("SUPABASE_KEY", "")
        self.service_role_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        self._client: Optional[Client] = None
        self._admin_client: Optional[Client] = None
    
    @property
    def client(self) -> Client:
        """Get Supabase client with anon key"""
        if self._client is None:
            self._client = create_client(self.url, self.key)
        return self._client
    
    @property
    def admin_client(self) -> Client:
        """Get Supabase client with service role key (for admin operations)"""
        if self._admin_client is None:
            if not self.service_role_key:
                raise ValueError("SUPABASE_SERVICE_ROLE_KEY not set")
            self._admin_client = create_client(self.url, self.service_role_key)
        return self._admin_client

# Global instance
supabase_config = SupabaseConfig()

def get_supabase_client() -> Client:
    """Get Supabase client"""
    return supabase_config.client

def get_supabase_admin_client() -> Client:
    """Get Supabase admin client"""
    return supabase_config.admin_client
