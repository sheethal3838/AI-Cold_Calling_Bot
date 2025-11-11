"""
Script to populate vector database with company knowledge
Run this once to index all your documents
"""

import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.vector_services import vector_store
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Company knowledge chunks for vector DB
# These are smaller, focused pieces of information for semantic search
KNOWLEDGE_CHUNKS = [
    # Company Overview
    {
        "id": "company_intro",
        "text": "Our company is India's premier platform for investing in unlisted shares and pre-IPO opportunities. We provide retail investors exclusive access to high-growth companies before they go public, like Swiggy, PhonePe, and Razorpay.",
        "metadata": {"category": "company", "type": "introduction"}
    },
    {
        "id": "company_mission",
        "text": "Our mission is democratizing access to pre-IPO investments for every Indian investor. We've helped over thousands of investors access unicorns and emerging companies.",
        "metadata": {"category": "company", "type": "mission"}
    },
    {
        "id": "company_benefits",
        "text": "Why choose us: Exclusive access to unicorns before IPO, expert research team, SEBI-compliant operations, transparent pricing with no hidden fees, and dedicated support available 9 AM to 9 PM IST.",
        "metadata": {"category": "company", "type": "benefits"}
    },
    
    # Investment Process
    {
        "id": "process_steps",
        "text": "Investment process: 1) Browse companies on our platform, 2) Complete KYC with PAN and Aadhaar, 3) Review investment details, 4) Place order and pay via UPI or net banking, 5) Get shares in your demat account within 7-10 days.",
        "metadata": {"category": "process", "type": "steps"}
    },
    {
        "id": "process_kyc",
        "text": "KYC requirements: Just 3 documents - PAN Card, Aadhaar Card, and bank account proof. Completely online, no physical documents needed. Completion time is 24-48 hours.",
        "metadata": {"category": "process", "type": "kyc"}
    },
    {
        "id": "process_timeline",
        "text": "Investment timeline: KYC completion takes 24-48 hours, order placement is instant, payment clears immediately with UPI or in 2 days with NEFT, shares allocated within 7-10 business days. Total process: 10-15 days from signup to shares in demat.",
        "metadata": {"category": "process", "type": "timeline"}
    },
    
    # Investment Amounts & Pricing
    {
        "id": "minimum_investment",
        "text": "Minimum investment amounts: Tier 1 unicorn companies require minimum 2 lakhs, Tier 2 emerging companies need 1 lakh minimum, Tier 3 early stage companies start from 50,000 rupees. We recommend starting with 1-2 lakhs.",
        "metadata": {"category": "pricing", "type": "minimum"}
    },
    {
        "id": "pricing_structure",
        "text": "Our pricing: 2% transaction fee on investment amount. No annual maintenance charges, no hidden fees. What you see is what you pay.",
        "metadata": {"category": "pricing", "type": "fees"}
    },
    
    # Available Companies
    {
        "id": "available_fintech",
        "text": "Fintech companies available: PhonePe (payments and financial services), Razorpay (payment gateway), Zerodha (stock brokerage). These are high-growth fintech unicorns before public listing.",
        "metadata": {"category": "companies", "sector": "fintech"}
    },
    {
        "id": "available_ecommerce",
        "text": "E-commerce companies available: Swiggy (food delivery), Meesho (social commerce), Dunzo (quick commerce). Access to fast-growing consumer tech companies.",
        "metadata": {"category": "companies", "sector": "ecommerce"}
    },
    {
        "id": "available_saas",
        "text": "SaaS companies available: Freshworks (customer engagement software), Postman (API platform), Chargebee (subscription management). Indian SaaS companies going global.",
        "metadata": {"category": "companies", "sector": "saas"}
    },
    
    # Returns & Risks
    {
        "id": "returns_expectations",
        "text": "Historical returns: Unlisted pre-IPO investments have delivered 2x to 5x returns over 2-3 years typically. However, past performance doesn't guarantee future returns. Some companies may not perform well.",
        "metadata": {"category": "returns", "type": "expectations"}
    },
    {
        "id": "risk_disclosure",
        "text": "Risk factors: Unlisted shares carry higher risk than listed stocks. Limited liquidity, subjective valuations, limited company information, no daily price discovery, investment locked for 18-36 months. We recommend investing only 5-10% of your equity portfolio.",
        "metadata": {"category": "risk", "type": "disclosure"}
    },
    {
        "id": "holding_period",
        "text": "Investment holding period: Typical holding is 18-36 months until liquidity event. Exit options include IPO, acquisition, secondary sale, or buyback. We provide secondary marketplace for early exit at market prices.",
        "metadata": {"category": "returns", "type": "timeline"}
    },
    
    # Legal & Compliance
    {
        "id": "legality",
        "text": "Legal status: Investing in unlisted shares is 100% legal in India, regulated by SEBI. We are a SEBI-registered investment advisor with full compliance. Your shares are held in your demat account just like listed stocks.",
        "metadata": {"category": "legal", "type": "compliance"}
    },
    {
        "id": "safety_security",
        "text": "Safety and security: Your shares are in YOUR demat account, we don't hold your money or shares. We're an intermediary facilitating transactions. SEBI registered, ISO 27001 certified for data security.",
        "metadata": {"category": "legal", "type": "safety"}
    },
    
    # Comparison & Differentiation
    {
        "id": "vs_mutual_funds",
        "text": "Difference from mutual funds: Mutual funds invest in liquid listed stocks with lower risk and 10-15% annual returns. Unlisted shares are direct company ownership, illiquid, higher risk but potential for 2-5x returns over 2-3 years. Different purposes in portfolio.",
        "metadata": {"category": "comparison", "type": "mutual_funds"}
    },
    {
        "id": "vs_angel_investing",
        "text": "Difference from angel investing: Angel investing and VC typically need 25 lakhs+ per company and accredited investor status. Our platform democratizes this - start with just 50,000 rupees and get similar opportunities.",
        "metadata": {"category": "comparison", "type": "angel_vc"}
    },
    
    # Objection Handling
    {
        "id": "objection_risky",
        "text": "When concerned about risk: Yes, unlisted shares are riskier than listed stocks. That's why we recommend: invest only 5-10% of equity portfolio, diversify across 3-5 companies, have 3-year horizon, use only surplus funds. Higher risk comes with potential for higher returns - early Zomato investors made 5-10x returns.",
        "metadata": {"category": "objection", "type": "risk"}
    },
    {
        "id": "objection_liquidity",
        "text": "When asking about needing money urgently: Unlisted shares are illiquid. If urgent: try our secondary marketplace (30-60 days), accept lower price for quick sale (10-20% discount typical), or wait for funding round/IPO. Invest only surplus funds with 3-year horizon.",
        "metadata": {"category": "objection", "type": "liquidity"}
    },
    {
        "id": "objection_trust",
        "text": "Building trust: We are SEBI registered (verify on SEBI website), ISO 27001 certified, backed by reputable investors, featured in Economic Times and other media, 5000+ successful investors on platform. Happy to connect you with existing customers or provide references.",
        "metadata": {"category": "objection", "type": "trust"}
    },
    
    # Tax Information
    {
        "id": "tax_implications",
        "text": "Tax treatment: Short-term capital gains (STCG) if sold within 24 months, Long-term capital gains (LTCG) if held beyond 24 months. We provide tax computation statements. Recommend consulting your CA for personalized advice.",
        "metadata": {"category": "tax", "type": "implications"}
    },
    
    # Contact & Support
    {
        "id": "contact_support",
        "text": "Customer support: Available 9 AM to 9 PM IST, Monday to Saturday. Contact via phone, email, or WhatsApp. Free consultation with investment advisors. Join our Telegram community of 1000+ investors.",
        "metadata": {"category": "support", "type": "contact"}
    }
]

def populate_vector_database():
    """Populate Pinecone with company knowledge chunks"""
    
    logger.info("Starting vector database population...")
    logger.info(f"Total chunks to add: {len(KNOWLEDGE_CHUNKS)}")
    
    success_count = 0
    error_count = 0
    
    for chunk in KNOWLEDGE_CHUNKS:
        try:
            success = vector_store.add_document(
                doc_id=chunk["id"],
                text=chunk["text"],
                metadata=chunk["metadata"]
            )
            
            if success:
                success_count += 1
                logger.info(f"✅ Added: {chunk['id']}")
            else:
                error_count += 1
                logger.error(f"❌ Failed: {chunk['id']}")
                
        except Exception as e:
            error_count += 1
            logger.error(f"❌ Error adding {chunk['id']}: {str(e)}")
    
    logger.info("\n" + "="*50)
    logger.info(f"Population complete!")
    logger.info(f"✅ Successful: {success_count}")
    logger.info(f"❌ Failed: {error_count}")
    logger.info("="*50)
    
    # Show stats
    stats = vector_store.get_stats()
    logger.info(f"\nVector Store Stats: {stats}")

def test_search():
    """Test semantic search with sample queries"""
    
    logger.info("\n" + "="*50)
    logger.info("Testing semantic search...")
    logger.info("="*50 + "\n")
    
    test_queries = [
        "What companies are available in fintech?",
        "How much money do I need to invest?",
        "Is this legal and safe?",
        "What are the risks?",
        "How long does the process take?"
    ]
    
    for query in test_queries:
        logger.info(f"\n🔍 Query: {query}")
        results = vector_store.search(query, top_k=2)
        
        for i, result in enumerate(results, 1):
            logger.info(f"\n  Result {i} (score: {result['score']:.3f}):")
            logger.info(f"  {result['text'][:150]}...")

if __name__ == "__main__":
    # Populate database
    populate_vector_database()
    
    # Test searches
    test_search()