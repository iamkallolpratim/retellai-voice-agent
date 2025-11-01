# AI Voice Agent Tool - Logistics Management System

A full-stack web application for configuring, testing, and reviewing AI voice agents for logistics operations, specifically designed for driver check-in and emergency protocol scenarios.

##  Project Overview

This application enables non-technical administrators to:
- Configure adaptive AI voice agents with advanced voice settings
- Trigger and monitor real-time web calls
- Review structured call results with automatic data extraction
- Handle two critical logistics scenarios: Driver Check-in and Emergency Protocol

## 🏗️ Architecture & Design Choices

### **Tech Stack**

**Frontend:**
- **React 18 + TypeScript**: Type-safe component architecture
- **Tailwind CSS**: Utility-first styling with black/white theme
- **Retell Web SDK**: Real-time voice communication
- **Custom Hooks**: Reusable business logic (`useAgentConfigs`, `useCalls`, `useRetellWebCall`)

**Backend:**
- **FastAPI**: High-performance async Python framework
- **Supabase (PostgreSQL)**: Scalable database with JSONB support
- **Retell AI**: Voice agent platform with natural conversation capabilities
- **Google Gemini 1.5**: AI-powered transcript analysis and structured data extraction

### **Key Design Decisions**

#### 1. **Modular Frontend Architecture**
```
src/
├── types/           # TypeScript interfaces
├── services/        # API layer & Retell client
├── hooks/           # Custom React hooks for business logic
├── components/      # Reusable UI components
└── App.tsx          # Main composition
```

**Why:** Separation of concerns enables independent testing, reusability, and easy maintenance. Each layer has a single responsibility.

#### 2. **Custom Hooks Pattern**
- `useAgentConfigs()`: Manages agent CRUD operations
- `useCalls()`: Handles call lifecycle with caching
- `useRetellWebCall()`: Encapsulates WebRTC/audio logic
- `useNotifications()`: Centralized user feedback

**Why:** Business logic is decoupled from UI, making it testable and reusable across components.

#### 3. **Real-time Web Calls vs Phone Calls**
Implemented web call functionality using Retell Web SDK for demo purposes.

**Why:** 
- No phone number requirements (international friendly)
- Instant testing without carrier delays
- Real-time transcript visibility
- Lower cost for development/testing

#### 4. **Webhook-Based Data Processing**
Backend receives Retell webhooks → Processes with Gemini → Stores structured data

**Why:**
- Asynchronous processing doesn't block call completion
- Reliable data extraction even if frontend disconnects
- Enables post-call analysis and quality assurance

#### 5. **Gemini for Structured Extraction**
Used Google Gemini 1.5 Flash for transcript analysis instead of manual parsing.

**Why:**
- Handles natural language variations robustly
- Free tier sufficient for demo (15 req/min)
- Adapts to different conversation flows
- Extracts complex structured data accurately

#### 6. **JSONB for Structured Data**
PostgreSQL JSONB column stores dynamic structured data.

**Why:**
- Flexible schema for different scenarios
- Queryable with PostgreSQL's JSON operators
- No migration needed for new data fields
- Perfect for variable call outcomes

##  Features Implemented

### Core Requirements

#### **Agent Configuration UI**
- Create/edit/delete agent configurations
- Advanced voice settings:
  - Backchanneling toggle (natural acknowledgments)
  - Filler words toggle (um, uh, you know)
  - Interruption sensitivity slider (0-100%)
- Scenario type selection (Check-in vs Emergency)
- Custom system prompts with variable interpolation
- Real-time Retell AI agent creation

#### **Call Triggering & Results**
- Input driver name, phone, and load number
- Web call interface with:
  - Real-time audio streaming
  - Live transcript display
  - Call status indicators
  - Mute/unmute controls
  - Call duration tracking
- Results dashboard with:
  - Call list with status badges
  - Detailed call view
  - Structured data extraction
  - Full transcript display

#### **Backend Logic**
- FastAPI webhook endpoint for Retell events
- Transcript processor using Gemini AI
- Structured data extraction for both scenarios
- Database persistence with Supabase

### Scenario Implementation

#### **Scenario 1: End-to-End Driver Check-in**
Agent asks open-ended questions and dynamically pivots based on driver status.

**Structured Data Extracted:**
- `call_outcome`: In-Transit Update | Arrival Confirmation
- `driver_status`: Driving | Delayed | Arrived | Unloading
- `current_location`: Geographic location
- `eta`: Estimated arrival time
- `delay_reason`: Cause of delay or None
- `unloading_status`: Current unloading state or N/A
- `pod_reminder_acknowledged`: Boolean

#### **Scenario 2: Dynamic Emergency Protocol**
Agent detects emergency keywords and immediately switches to safety protocol.

**Structured Data Extracted:**
- `call_outcome`: Emergency Escalation
- `emergency_type`: Accident | Breakdown | Medical | Other
- `safety_status`: Safety confirmation details
- `injury_status`: Injury information
- `emergency_location`: Exact location
- `load_secure`: Boolean
- `escalation_status`: Connection to human dispatcher

#### **Task B: Edge Case Handling**
Prompts configured to handle:
- **Uncooperative Driver**: Probing questions, graceful exit
- **Noisy Environment**: Repeat requests with limit
- **Location Conflicts**: Non-confrontational verification

##  Setup & Installation

### **Prerequisites**
- Node.js 18+
- Python 3.10+
- PostgreSQL (via Supabase)
- Retell AI account
- Google AI Studio account (for Gemini API)

### **1. Backend Setup**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://user:password@host:5432/database
RETELL_API_KEY=your_retell_api_key
GEMINI_API_KEY=your_gemini_api_key
RETELL_LLM_ID=your_llm_id  # Optional: pre-configured LLM
EOF

# Run database migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8000
```

### **2. Frontend Setup**
```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cat > .env << EOF
REACT_APP_API_URL=http://localhost:8000/api
EOF

# Start development server
npm start
```

### **3. Configure Retell Webhook**

For local development, use ngrok:
```bash
ngrok http 8000
```

Then in Retell AI Dashboard:
1. Go to Settings → Webhooks
2. Add webhook: `https://YOUR_NGROK_URL.ngrok.io/api/webhooks/retell`
3. Enable events: `call_started`, `call_ended`, `call_analyzed`

### **4. Get API Keys**

**Retell AI:**
1. Sign up at https://retellai.com
2. Get API key from dashboard
3. Create an LLM in the dashboard (optional)

**Google Gemini:**
1. Visit https://aistudio.google.com/app/apikey
2. Create free API key
3. Free tier: 15 requests/minute

**Supabase:**
1. Create project at https://supabase.com
2. Get connection string from Settings → Database
3. Run SQL schema from `backend/migrations/`

##  Project Structure
```
voice-agent/
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── NotificationBanner.tsx
│   │   │   ├── StatusBadge.tsx
│   │   │   ├── ConfigForm.tsx
│   │   │   ├── ConfigList.tsx
│   │   │   ├── CallTriggerForm.tsx
│   │   │   ├── CallList.tsx
│   │   │   ├── CallDetails.tsx
│   │   │   └── WebCallInterface.tsx
│   │   ├── hooks/           # Custom hooks
│   │   │   ├── useAgentConfigs.ts
│   │   │   ├── useCalls.ts
│   │   │   ├── useRetellWebCall.ts
│   │   │   └── useNotifications.ts
│   │   ├── services/        # API & external services
│   │   │   ├── api.ts
│   │   │   └── retellWebClient.ts
│   │   ├── types/           # TypeScript interfaces
│   │   │   └── index.ts
│   │   └── App.tsx          # Main app component
│   ├── package.json
│   └── tailwind.config.js
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── agent.py        # Agent CRUD
│   │   │       ├── calls.py        # Call management
│   │   │       └── webhooks.py     # Retell webhooks
│   │   ├── services/
│   │   │   ├── database.py         # Supabase client
│   │   │   ├── retell_service.py   # Retell AI client
│   │   │   └── transcript_processor.py  # Gemini extraction
│   │   ├── models/
│   │   │   └── schemas.py          # Pydantic models
│   │   ├── core/
│   │   │   ├── config.py           # Settings
│   │   │   └── exceptions.py       # Custom exceptions
│   │   └── main.py                 # FastAPI app
│   ├── requirements.txt
│   └── alembic/                    # Database migrations
│
└── README.md
```

##  Testing the Application

### **1. Create Agent Configuration**

**For Check-in Scenario:**
```
Name: Standard Check-in Agent
Scenario: End-to-End Driver Check-in
System Prompt:
"You are a professional logistics dispatcher. Start with: 'Hi {driver_name}, this is Dispatch with a check call on load {load_number}. Can you give me an update on your status?' 

Based on their response, ask follow-up questions about location, ETA, or unloading status. Always remind them to submit their POD. If they mention any emergency, immediately switch to safety protocol."

Settings:
- Backchanneling: ON
- Filler Words: ON  
- Interruption Sensitivity: 50%
```

**For Emergency Scenario:**
```
Name: Emergency Protocol Agent
Scenario: Dynamic Emergency Protocol
System Prompt:
"You are a dispatcher trained for emergencies. If the driver mentions accident, breakdown, medical issue, or any emergency:
1. Ask: 'Are you safe? Is anyone injured?'
2. Ask: 'What's your exact location?'
3. Ask: 'Is your load secure?'
4. Say: 'I'm connecting you to a human dispatcher right away.'"

Settings:
- Backchanneling: ON
- Filler Words: OFF
- Interruption Sensitivity: 80%
```

### **2. Trigger Test Call**

1. Navigate to "Trigger Call" tab
2. Select an agent configuration
3. Enter test data:
   - Driver Name: Mike Johnson
   - Phone: +1234567890 (not used for web calls)
   - Load Number: 7891-B
4. Click "Start Web Call (Demo)"
5. Allow microphone access
6. Have a conversation with the agent

### **3. Test Scenarios**

**Test Check-in (In-Transit):**
- Agent: "Hi Mike, this is Dispatch with a check call on load 7891-B. Can you give me an update?"
- You: "I'm on I-10 near Indio, should be there tomorrow at 8 AM"
- Expected: Agent asks about delays, mentions POD

**Test Check-in (Arrived):**
- You: "I just arrived, waiting to get into Door 42"
- Expected: Agent asks about unloading status

**Test Emergency:**
- You: "I just had a tire blowout, I'm pulling over"
- Expected: Agent immediately asks safety questions, mentions dispatcher

### **4. Review Results**

1. Go to "View Results" tab
2. Click on completed call
3. Verify structured data extracted correctly
4. Check full transcript

##  Design Choices Rationale

### **Black & White Theme**
Professional, accessible, high-contrast design suitable for admin dashboards. Reduces cognitive load and focuses attention on data.

### **Component-Based Architecture**
Each component has single responsibility:
- `ConfigForm`: Agent configuration logic
- `CallTriggerForm`: Call initiation
- `WebCallInterface`: Real-time call UI
- `CallList` + `CallDetails`: Results display

### **Optimistic UI Updates**
Frontend updates immediately, then syncs with backend. Provides instant feedback and smooth UX.

### **Auto-refresh for Active Calls**
Polls backend every 3 seconds for in-progress calls. Shows real-time status without WebSocket complexity.

### **Error Boundaries**
Comprehensive error handling at each layer:
- API service catches network errors
- Hooks handle data errors
- Components show user-friendly messages

##  Security Considerations

- API keys stored in environment variables
- CORS configured for specific origins
- Input validation with Pydantic models
- SQL injection prevention with parameterized queries
- No sensitive data in client-side code

##  Known Limitations

1. **Web calls only**: Phone calling requires additional Twilio integration
2. **No authentication**: Add Auth0/Clerk for production
3. **Single tenant**: Multi-tenancy requires organization/user models
4. **Limited call history**: Add pagination for large datasets
5. **No call recording playback**: Only transcript available


