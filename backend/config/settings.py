"""
Settings configuration for Bolna AI Voice Calling Bot
Updated for Bolna AI + Make.com integration
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
from datetime import time
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # =========================================================================
    # Bolna AI Configuration
    # =========================================================================
    BOLNA_API_KEY: str
    BOLNA_AGENT_ID: str
    BOLNA_API_URL: str = "https://api.bolna.dev"
    BOLNA_PHONE_NUMBER: Optional[str] = None
    BOLNA_WEBHOOK_SECRET: Optional[str] = None
    
    # =========================================================================
    # OpenAI Configuration
    # =========================================================================
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # =========================================================================
    # Pinecone Configuration
    # =========================================================================
    PINECONE_API_KEY: str
    PINECONE_ENVIRONMENT: str = "gcp-starter"
    PINECONE_INDEX_NAME: str = "unlisted-edge-knowledge"
    
    # =========================================================================
    # Make.com Configuration
    # =========================================================================
    MAKE_WEBHOOK_CALL_TRIGGER: Optional[str] = None
    MAKE_WEBHOOK_CALL_ENDED: Optional[str] = None
    MAKE_API_KEY: Optional[str] = None
    
    # =========================================================================
    # Google Sheets Configuration
    # =========================================================================
    GOOGLE_SHEETS_ID: Optional[str] = None
    LEADS_SHEET_NAME: str = "Leads"
    ANALYTICS_SHEET_NAME: str = "Analytics"
    DNC_SHEET_NAME: str = "DNC_List"
    
    # =========================================================================
    # Application Configuration
    # =========================================================================
    APP_NAME: str = "Unlisted Edge Voice Caller"
    ENV: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    API_BASE_URL: Optional[str] = None
    
    # =========================================================================
    # Business Rules & Compliance
    # =========================================================================
    CALLING_HOURS_START: str = "09:00"
    CALLING_HOURS_END: str = "19:00"
    TIMEZONE: str = "Asia/Kolkata"
    
    MAX_CALL_DURATION_MINUTES: int = 10
    MAX_CALLS_PER_LEAD_PER_DAY: int = 3
    RATE_LIMIT_CALLS_PER_HOUR: int = 100
    
    PROFANITY_FILTER_ENABLED: bool = True
    DNC_CHECK_ENABLED: bool = True
    
    # =========================================================================
    # Security
    # =========================================================================
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # =========================================================================
    # Optional: Database Configuration
    # =========================================================================
    MONGODB_URL: Optional[str] = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "unlisted_edge_calls"
    
    # =========================================================================
    # Optional: WhatsApp Configuration
    # =========================================================================
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_WHATSAPP_FROM: Optional[str] = None
    
    # =========================================================================
    # Company Information
    # =========================================================================
    COMPANY_NAME: str = "Unlisted Edge"
    COMPANY_PHONE: Optional[str] = None
    COMPANY_EMAIL: Optional[str] = None
    COMPANY_WEBSITE: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
    def get_calling_hours_range(self) -> tuple:
        """Get calling hours as datetime.time objects"""
        from datetime import datetime
        
        start_time = datetime.strptime(self.CALLING_HOURS_START, "%H:%M").time()
        end_time = datetime.strptime(self.CALLING_HOURS_END, "%H:%M").time()
        
        return start_time, end_time
    
    def is_within_calling_hours(self) -> bool:
        """Check if current time is within calling hours"""
        from datetime import datetime
        import pytz
        
        tz = pytz.timezone(self.TIMEZONE)
        current_time = datetime.now(tz).time()
        start_time, end_time = self.get_calling_hours_range()
        
        return start_time <= current_time <= end_time

# Create settings instance
settings = Settings()