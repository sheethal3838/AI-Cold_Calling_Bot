# Voice Caller Bot - Unlisted Shares Investment Platform

AI-powered voice assistant for cold calling and lead generation in the financial services sector.

## 🎯 Features

- **Natural Voice Conversations**: Indian accent support with <500ms latency
- **Intelligent Knowledge Base**: Static company info + dynamic vector search
- **Lead Data Collection**: Automated extraction and storage
- **Semantic Search**: Pinecone vector database for contextual responses
- **Real-time Logging**: All call events and interactions logged
- **Webhook Integration**: Vapi.ai integration for production-grade telephony

## 🏗️ Architecture
```
Vapi.ai (Voice Infrastructure)
    ↓
FastAPI Backend (Business Logic)
    ↓
├── Pinecone (Vector Search)
├── OpenAI (Embeddings & LLM)
└── MongoDB (Data Storage - future)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Vapi.ai account
- OpenAI API key
- Pinecone account
- Ngrok (for local development)

### Installation
```bash
# Clone/Navigate to project
cd voice-caller-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r backend/requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Running Locally
```bash
# Terminal 1: Start FastAPI
cd backend/app
python main.py

# Terminal 2: Start Ngrok
ngrok http 8000

# Terminal 3: Populate Vector DB (first time only)
python scripts/populate_vector_db.py
```

### Configuration

1. Update `.env` with your API keys
2. Upload knowledge base files to Vapi dashboard
3. Update Vapi assistant webhook URLs with ngrok URL
4. Test with sample call

## 📁 Project Structure
```
voice-caller-bot/
├── backend/
│   ├── app/
│   │   └── main.py              # FastAPI application
│   ├── config/
│   │   └── settings.py          # Configuration management
│   ├── services/
│   │   └── vector_store.py      # Pinecone integration
│   └── requirements.txt
├── knowledge-base/
│   ├── company_overview.md      # Company information
│   ├── investment_process.md    # Process details
│   └── faqs_and_objections.md   # FAQ content
├── scripts/
│   ├── populate_vector_db.py    # Seed vector database
│   └── test_scenarios.md        # Testing guidelines
├── .env                         # Environment variables (gitignored)
└── README.md
```

## 🔧 API Endpoints

### Health Check
- `GET /` - Basic health check
- `GET /health` - Detailed service status

### Vapi Webhooks
- `POST /webhooks/vapi/function-call` - Handle function calls
- `POST /webhooks/vapi/status` - Call status updates
- `POST /webhooks/vapi/transcript` - Transcript streaming

### Custom Functions
- `POST /functions/search-knowledge` - Vector DB search
- `POST /functions/save-lead-data` - Store lead information

### Testing
- `GET /test/search?query=your_question` - Test vector search

## 📊 Performance Targets

- **Latency**: <500ms for vector search, <800ms total response
- **Accuracy**: >85% speech recognition for Indian English
- **Uptime**: 99%+ (production)
- **Call Success Rate**: >80%

## 🧪 Testing
```bash
# Run test scenarios
# See scripts/test_scenarios.md for detailed test cases

# Test vector search
curl "http://localhost:8000/test/search?query=What+companies+are+available"

# Check health
curl http://localhost:8000/health
```

## 🚀 Deployment

### Railway (Recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

### Environment Variables for Production
```
VAPI_API_KEY=sk_live_...
OPENAI_API_KEY=sk-proj-...
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=gcp-starter
MONGODB_URL=mongodb+srv://...
DEBUG=False
```

## 📝 Customization

### Update Company Information
1. Edit files in `knowledge-base/`
2. Re-upload to Vapi dashboard
3. Re-run `populate_vector_db.py`

### Modify Voice/Personality
1. Vapi Dashboard → Assistants
2. Update System Prompt
3. Change voice settings

### Add New Functions
1. Add function in `backend/app/main.py`
2. Update Vapi assistant with function definition
3. Test with sample call

## 🐛 Troubleshooting

**High Latency:**
- Check ngrok connection
- Verify Pinecone region
- Optimize vector search (reduce top_k)

**Voice Recognition Issues:**
- Switch to Azure STT in Vapi
- Adjust voice settings (speed, clarity)
- Test in quiet environment

**Function Calls Not Working:**
- Verify ngrok URL is public
- Check function definitions in Vapi
- Review FastAPI logs

## 📚 Resources

- [Vapi.ai Documentation](https://docs.vapi.ai)
- [Pinecone Documentation](https://docs.pinecone.io)
- [FastAPI Documentation](https://fastapi.tiangolo.com)

## 🔐 Security Notes

- Never commit `.env` file
- Rotate API keys regularly
- Use HTTPS in production
- Implement rate limiting
- Validate all user inputs

## 📈 Future Enhancements

- [ ] MongoDB integration for persistent storage
- [ ] Make.com automation for CRM sync
- [ ] Analytics dashboard
- [ ] Multi-language support (Hindi, Tamil, etc.)
- [ ] Sentiment analysis
- [ ] Auto-scheduling callbacks
- [ ] WhatsApp integration

## 👥 Team

Built for Unlisted Edge financial services platform.

## 📄 License

Proprietary - All rights reserved