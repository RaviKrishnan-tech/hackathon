# Mavericks AI-Powered Learning Platform - Backend

A comprehensive AI-driven platform for skill assessment, personalized learning, and 24/7 AI mentoring. This backend system uses real AI integration with no mock data, providing dynamic and intelligent learning experiences.

## 🚀 Features

### Core AI Capabilities
- **AI-Powered Resume Parsing**: Uses Gemini AI to extract skills, experience, education, and projects from resumes
- **Dynamic Assessment Generation**: AI-generated questions based on extracted skills with difficulty levels
- **Real-Time Skill Analysis**: Categorizes skills as strong, weak, or medium using AI analysis
- **Personalized Learning Paths**: AI-generated learning modules tailored to individual skill gaps
- **24/7 AI Mentor**: Context-aware AI mentor providing personalized guidance and code reviews

### Real-Time Analytics
- **Comprehensive Activity Tracking**: Tracks all user interactions and learning progress
- **Dynamic Admin Dashboard**: Real-time analytics with no mock data
- **Skill Progress Monitoring**: Tracks improvement over time with detailed analytics
- **Learning Analytics**: Module completion rates and engagement metrics

### Advanced Features
- **WebSocket Support**: Real-time chat with AI mentor
- **Code Review System**: AI-powered code analysis and suggestions
- **Debug Assistance**: AI help with error resolution and debugging
- **Career Recommendations**: Personalized career guidance based on skill analysis

## 🏗️ Architecture

```
backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── routes/                 # API route modules
│   ├── resume.py          # AI-powered resume parsing
│   ├── assessment.py      # Dynamic assessment generation
│   ├── recommend.py       # AI learning path generation
│   ├── mentor.py          # 24/7 AI mentor system
│   ├── admin.py           # Real-time admin dashboard
│   ├── progress.py        # User progress tracking
│   └── hackathon.py       # Event management
├── utils/                  # AI utilities and services
│   ├── enhanced_resume_parser.py    # Gemini AI resume analysis
│   ├── skill_analyzer.py            # AI skill strength analysis
│   ├── ai_mentor.py                 # AI mentor system
│   ├── user_activity_tracker.py     # Real-time activity tracking
│   ├── qg_model.py                  # Question generation model
│   └── skill_extraction.py          # Basic skill extraction
└── services/              # Additional services
    └── parser.py          # Document parsing utilities
```

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mavericks/backend
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the backend directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Run the application**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## 📡 API Endpoints

### Resume Processing
- `POST /resume/process` - Upload and analyze resume with AI
- `GET /resume/{user_id}/analysis` - Get detailed resume analysis

### Assessment System
- `POST /assessment/generate` - Generate AI-powered assessments
- `POST /assessment/submit` - Submit assessment and get analysis
- `GET /assessment/{user_id}/history` - Get assessment history
- `GET /assessment/{user_id}/progress` - Get skill progress over time

### Learning Recommendations
- `POST /recommend/learning-path` - Generate personalized learning path
- `POST /recommend/modules` - Generate detailed learning modules
- `GET /recommend/{user_id}/progress` - Get learning progress
- `POST /recommend/{user_id}/complete-module` - Mark module as completed

### AI Mentor System
- `POST /mentor/chat` - Chat with AI mentor
- `GET /mentor/{user_id}/sessions` - Get mentor session history
- `GET /mentor/{user_id}/conversation-history` - Get conversation history
- `POST /mentor/{user_id}/learning-guidance` - Get learning guidance
- `POST /mentor/{user_id}/code-review` - Get AI code review
- `POST /mentor/{user_id}/debug-help` - Get debugging assistance
- `GET /mentor/{user_id}/recommendations` - Get personalized recommendations
- `WS /mentor/ws/{user_id}` - Real-time WebSocket chat

### Admin Dashboard
- `GET /admin/dashboard` - Get comprehensive dashboard data
- `GET /admin/users` - Get all users with profiles
- `GET /admin/users/{user_id}` - Get detailed user information
- `GET /admin/analytics/skills` - Get skills analytics
- `GET /admin/analytics/mentor` - Get mentor usage analytics
- `GET /admin/analytics/learning` - Get learning analytics
- `GET /admin/reports/activity` - Get activity reports
- `GET /admin/system/health` - Get system health status

### User Progress
- `GET /user/{user_id}/progress` - Get user progress data

## 🤖 AI Integration Details

### Gemini AI Usage
- **Resume Analysis**: Comprehensive skill extraction and career analysis
- **Assessment Generation**: Dynamic question creation with explanations
- **Skill Analysis**: AI-powered skill strength categorization
- **Learning Path Generation**: Personalized curriculum creation
- **AI Mentor**: Context-aware responses and guidance

### Real-Time Processing
- **No Mock Data**: All responses are generated using real AI
- **Dynamic Content**: Content adapts based on user interactions
- **Context Awareness**: AI responses consider user's learning history
- **Personalization**: Tailored recommendations based on skill analysis

## 📊 Data Flow

1. **Resume Upload** → AI Analysis → Skill Extraction → Assessment Plan
2. **Assessment Generation** → AI Questions → User Responses → Skill Analysis
3. **Skill Analysis** → Strong/Weak/Medium Categorization → Learning Path Generation
4. **Learning Path** → AI-Generated Modules → Progress Tracking → Mentor Guidance
5. **AI Mentor** → Context-Aware Responses → Session Logging → Analytics

## 🔧 Configuration

### Environment Variables
- `GEMINI_API_KEY`: Required for AI functionality
- `CORS_ORIGINS`: Frontend domains (for production)

### AI Model Configuration
- **Gemini Pro**: Used for all AI interactions
- **Hugging Face Models**: Used for skill extraction and question generation
- **Custom Prompts**: Optimized for educational content generation

## 📈 Analytics & Monitoring

### Real-Time Metrics
- User engagement tracking
- Skill assessment statistics
- Learning module completion rates
- AI mentor usage analytics
- System performance metrics

### Admin Dashboard Features
- Live user activity monitoring
- Skill distribution analysis
- Learning progress tracking
- Mentor session analytics
- System health monitoring

## 🚀 Deployment

### Production Setup
1. Set up environment variables
2. Configure CORS for production domains
3. Set up database for persistent storage
4. Configure logging and monitoring
5. Deploy using uvicorn or gunicorn

### Docker Deployment
```bash
docker build -t mavericks-backend .
docker run -p 8000:8000 mavericks-backend
```

## 🔒 Security Considerations

- API key management for AI services
- Input validation and sanitization
- Rate limiting for AI endpoints
- Secure file upload handling
- CORS configuration for production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the API documentation at `/docs` when running the server

---

**Note**: This system uses real AI integration with no mock data. All responses are generated dynamically using Gemini AI and other AI services for a truly intelligent learning experience.
