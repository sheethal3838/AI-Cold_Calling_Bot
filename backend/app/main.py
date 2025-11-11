"""
FastAPI Backend for Unlisted Edge Voice Calling Bot
Updated for Bolna AI + Make.com Integration
"""

from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
import sys
import os
import hmac
import hashlib
from typing import Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
# from services.vector_store import vector_store

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Voice AI Backend for Cold Calling with Bolna AI",
    version="2.0.0",
    debug=settings.DEBUG
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def verify_bolna_webhook(payload: bytes, signature: str) -> bool:
    """
    Verify Bolna webhook signature for security
    """
    if not settings.BOLNA_WEBHOOK_SECRET:
        logger.warning("BOLNA_WEBHOOK_SECRET not set, skipping verification")
        return True
    
    expected_signature = hmac.new(
        settings.BOLNA_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

# ============================================================================
# HEALTH CHECK ROUTES
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "2.0.0",
        "platform": "Bolna AI",
        "timestamp": datetime.now().isoformat(),
        "message": "Unlisted Edge Voice Caller Bot API is running!"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "api": "operational",
            "bolna_configured": bool(settings.BOLNA_API_KEY),
            "openai_configured": bool(settings.OPENAI_API_KEY),
            "pinecone_configured": bool(settings.PINECONE_API_KEY),
            "make_configured": bool(settings.MAKE_WEBHOOK_CALL_TRIGGER)
        },
        "calling_hours": {
            "start": settings.CALLING_HOURS_START,
            "end": settings.CALLING_HOURS_END,
            "currently_allowed": settings.is_within_calling_hours()
        },
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# BOLNA WEBHOOK ENDPOINTS
# ============================================================================

@app.post("/webhooks/bolna/call-started")
async def bolna_call_started(
    request: Request,
    x_bolna_signature: Optional[str] = Header(None)
):
    """
    Handle call started event from Bolna
    """
    try:
        body = await request.body()
        
        # Verify webhook signature (if configured)
        if x_bolna_signature and not verify_bolna_webhook(body, x_bolna_signature):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        data = await request.json()
        logger.info(f"Call started: {data}")
        
        call_id = data.get("call_id")
        customer_number = data.get("customer_number")
        agent_id = data.get("agent_id")
        
        # Log call start
        logger.info(f"Call {call_id} started with customer {customer_number}")
        
        # TODO: Store in database if needed
        
        return {"status": "received", "call_id": call_id}
        
    except Exception as e:
        logger.error(f"Error processing call started webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhooks/bolna/call-ended")
async def bolna_call_ended(
    request: Request,
    x_bolna_signature: Optional[str] = Header(None)
):
    """
    Handle call ended event from Bolna
    Forwards data to Make.com for Google Sheets update
    """
    try:
        body = await request.body()
        
        # Verify webhook signature
        if x_bolna_signature and not verify_bolna_webhook(body, x_bolna_signature):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        data = await request.json()
        logger.info(f"Call ended: {data}")
        
        # Extract key information
        call_data = {
            "call_id": data.get("call_id"),
            "customer_number": data.get("customer_number"),
            "duration_seconds": data.get("duration"),
            "status": data.get("status"),  # completed, failed, no-answer, etc.
            "transcript": data.get("transcript", ""),
            "recording_url": data.get("recording_url"),
            "collected_data": data.get("collected_data", {}),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Processed call data: {call_data}")
        
        # Forward to Make.com webhook (if configured)
        if settings.MAKE_WEBHOOK_CALL_ENDED:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.MAKE_WEBHOOK_CALL_ENDED,
                    json=call_data,
                    timeout=10.0
                )
                logger.info(f"Forwarded to Make.com: {response.status_code}")
        
        return {"status": "processed", "call_id": call_data["call_id"]}
        
    except Exception as e:
        logger.error(f"Error processing call ended webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhooks/bolna/transcript")
async def bolna_transcript(
    request: Request,
    x_bolna_signature: Optional[str] = Header(None)
):
    """
    Receive real-time transcript from Bolna
    """
    try:
        body = await request.body()
        
        if x_bolna_signature and not verify_bolna_webhook(body, x_bolna_signature):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        data = await request.json()
        logger.info(f"Transcript update: {data.get('text', '')[:100]}...")
        
        # Store transcript chunks if needed
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Error processing transcript: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# CUSTOM FUNCTION ENDPOINTS (Called by Bolna during conversation)
# ============================================================================

# @app.post("/functions/search-knowledge")
# async def search_knowledge(request: Request):
#     """
#     Semantic search in company knowledge base
#     Called by Bolna when customer asks complex questions
#     """
#     try:
#         data = await request.json()
#         logger.info(f"Knowledge search request: {data}")
        
#         # Extract query (Bolna format may differ from Vapi)
#         query = data.get("query") or data.get("parameters", {}).get("query", "")
        
#         if not query:
#             return {
#                 "error": "No query provided",
#                 "result": "I need a specific question to help you with."
#             }
        
#         # Search vector database
#         results = vector_store.search(query, top_k=3)
        
#         if not results:
#             return {
#                 "result": "I don't have specific information about that. Let me connect you with our investment advisor for detailed information."
#             }
        
#         # Format results for natural conversation
#         answer_parts = []
#         for result in results:
#             if result['score'] > 0.75:  # Only use high-confidence results
#                 answer_parts.append(result['text'])
        
#         if not answer_parts:
#             return {
#                 "result": "I found some related information, but I'd recommend speaking with our advisor for accurate details."
#             }
        
#         # Combine top results
#         combined_answer = " ".join(answer_parts[:2])  # Use top 2 results
        
#         logger.info(f"Returning answer from {len(answer_parts)} results")
        
#         return {
#             "result": combined_answer,
#             "confidence": results[0]['score'] if results else 0,
#             "sources_used": len(answer_parts)
#         }
        
#     except Exception as e:
#         logger.error(f"Error in knowledge search: {str(e)}")
#         return {
#             "error": str(e),
#             "result": "I'm having trouble accessing that information right now. Let me note your question and have an advisor call you back."
#         }

@app.post("/functions/save-lead-data")
async def save_lead_data(request: Request):
    """
    Save customer information collected during call
    Called by Bolna when collecting lead information
    """
    try:
        data = await request.json()
        logger.info(f"Saving lead data: {data}")
        
        # Extract lead information (adapt to Bolna's format)
        parameters = data.get("parameters", {})
        
        lead_data = {
            "name": parameters.get("name"),
            "phone": parameters.get("phone"),
            "email": parameters.get("email"),
            "interest_level": parameters.get("interest_level", "unknown"),
            "budget": parameters.get("budget"),
            "preferred_sectors": parameters.get("sectors", []),
            "questions": parameters.get("questions", []),
            "timestamp": datetime.now().isoformat(),
            "call_id": data.get("call_id")
        }
        
        # Log the data
        logger.info(f"Lead data collected: {lead_data}")
        
        # TODO: Save to MongoDB or forward to Make.com
        # For now, just acknowledge
        
        return {
            "result": "Thank you! I've noted all your details. Our investment advisor will contact you within 24 hours.",
            "lead_id": lead_data.get("call_id"),
            "status": "saved"
        }
        
    except Exception as e:
        logger.error(f"Error saving lead data: {str(e)}")
        return {
            "error": str(e),
            "result": "I've noted your interest. We'll follow up with you soon."
        }

@app.post("/functions/check-compliance")
async def check_compliance(request: Request):
    """
    Check compliance rules: DNC list, calling hours, profanity
    Called by Bolna before/during calls
    """
    try:
        data = await request.json()
        parameters = data.get("parameters", {})
        
        phone = parameters.get("phone")
        text = parameters.get("text", "")
        
        # Check 1: Calling hours
        if not settings.is_within_calling_hours():
            return {
                "action": "end_call",
                "safe": False,
                "reason": "outside_calling_hours",
                "response": "I apologize, but we're calling outside our business hours. We'll call you back between 9 AM and 7 PM IST. Thank you."
            }
        
        # Check 2: DNC list (placeholder - implement with actual DNC storage)
        # TODO: Check against actual DNC list in database/Google Sheets
        dnc_list = []  # Load from database/sheets
        if phone in dnc_list:
            return {
                "action": "end_call",
                "safe": False,
                "reason": "dnc_list",
                "response": "I see you've requested not to be contacted. We'll remove your number. Apologies for the inconvenience."
            }
        
        # Check 3: Profanity filter
        if settings.PROFANITY_FILTER_ENABLED:
            profane_words = ["fuck", "shit", "damn", "bastard"]  # Add more
            if any(word in text.lower() for word in profane_words):
                return {
                    "action": "end_politely",
                    "safe": False,
                    "reason": "profanity_detected",
                    "response": "I understand you're upset. If you'd prefer not to continue, that's completely fine. Have a good day."
                }
        
        # All checks passed
        return {
            "action": "continue",
            "safe": True,
            "reason": "all_checks_passed"
        }
        
    except Exception as e:
        logger.error(f"Error in compliance check: {str(e)}")
        return {
            "action": "continue",
            "safe": True,
            "error": str(e)
        }

# ============================================================================
# TESTING ENDPOINTS
# ============================================================================

# @app.get("/test/search")
# async def test_search_endpoint(query: str):
#     """
#     Test endpoint for vector search (for debugging)
#     Usage: /test/search?query=your question here
#     """
#     try:
#         results = vector_store.search(query, top_k=3)
#         return {
#             "query": query,
#             "results": results,
#             "count": len(results)
#         }
#     except Exception as e:
#         logger.error(f"Error in test search: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


@app.post("/test/webhook")
async def test_webhook(request: Request):
    """
    Test webhook endpoint to verify Make.com integration
    """
    try:
        data = await request.json()
        logger.info(f"Test webhook received: {data}")
        return {
            "status": "received",
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )

# ============================================================================
# STARTUP/SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info(f"Starting {settings.APP_NAME}...")
    logger.info(f"Version: 2.0.0 (Bolna AI)")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Bolna configured: {bool(settings.BOLNA_API_KEY)}")
    logger.info(f"OpenAI configured: {bool(settings.OPENAI_API_KEY)}")
    logger.info(f"Pinecone configured: {bool(settings.PINECONE_API_KEY)}")
    logger.info(f"Make.com configured: {bool(settings.MAKE_WEBHOOK_CALL_TRIGGER)}")
    logger.info(f"Calling hours: {settings.CALLING_HOURS_START} - {settings.CALLING_HOURS_END} {settings.TIMEZONE}")

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info(f"Shutting down {settings.APP_NAME}...")

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )