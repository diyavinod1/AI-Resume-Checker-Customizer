# AI Resume Checker & Customizer

**A comprehensive AI-powered application for analyzing, optimizing, and customizing resumes with ATS compatibility scoring and LinkedIn profile optimization.**

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)
![spaCy](https://img.shields.io/badge/spaCy-3.7.2-orange.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🚀 Features

### Core AI & NLP Functionality
- **🔍 Resume Parsing**: Advanced NER for extracting skills, experience, education, and projects
- **📊 ATS Scoring**: Comprehensive 0-100 scoring with detailed breakdown
- **🧠 Smart Optimization**: AI-powered bullet point rewrites and keyword suggestions  
- **💼 LinkedIn Integration**: Profile optimization with headline and summary generation
- **📄 Multi-format Support**: PDF/DOCX upload and download with regional formatting
- **🎨 Modern UI**: Clean, mobile-friendly interface with Base44-style design

### Technical Highlights
- **Semantic Matching**: Cosine similarity using sentence embeddings
- **Rule-based ATS Checks**: Font sizes, section order, formatting compatibility
- **Local AI Models**: No external API dependencies for core functionality
- **RESTful API**: Complete FastAPI backend with comprehensive endpoints
- **Responsive Design**: Mobile-first UI with exact sidebar navigation

## 📁 Project Structure

```
ai-resume-checker/
├── 🎨 frontend/              # Web UI (HTML/CSS/JS)
│   ├── index.html            # Main application page
│   └── app.js               # Frontend JavaScript logic
├── ⚡ backend/               # FastAPI server and endpoints
│   └── main.py              # Main API application
├── 🧠 nlp/                  # Core NLP processing modules
│   ├── __init__.py          # Package initialization
│   ├── resume_parser.py     # Resume text extraction and parsing
│   ├── job_matcher.py       # Job description analysis and matching
│   ├── ats_scorer.py        # ATS compatibility scoring
│   ├── suggestion_generator.py # AI-powered optimization suggestions
│   ├── resume_generator.py  # Multi-format resume output generation
│   └── demo.py             # Complete pipeline demonstration
├── 📦 models/               # Model files and weights
├── 📋 sample_data/          # Test resumes and job descriptions
│   ├── resume1.txt          # Sample software engineer resume
│   └── job_description1.txt # Sample job posting
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore rules
└── README.md               # This comprehensive guide
```

## ⚡ Quick Start

### Prerequisites
- Python 3.8 or higher
- 4GB+ RAM (for NLP models)
- Modern web browser

### 1. Setup Environment
```bash
# Navigate to project directory (you should already be here)
cd ai-resume-checker

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 2. Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm

# Download sentence transformer model (this may take a few minutes)
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### 3. Test Installation
```bash
# Run the demonstration script
python nlp/demo.py

# You should see:
# ============================================================
# AI RESUME CHECKER & CUSTOMIZER - DEMO
# ============================================================
```

### 4. Launch Application
```bash
# Start the FastAPI server
python backend/main.py

# Server will start on http://localhost:8000
# Open this URL in your browser
```

### 5. Use the Application
1. **Upload Resume**: Drag & drop or select your PDF/DOCX resume
2. **Fill Details**: Add target role, experience level, preferences
3. **Analyze**: Click "Analyze & Optimize Resume" button
4. **Review Results**: Check ATS score, extracted fields, suggestions
5. **Optimize**: View bullet point improvements and missing keywords
6. **Download**: Generate optimized resume in PDF/DOCX format
7. **LinkedIn**: Get LinkedIn profile optimization suggestions

## 🔧 API Reference

### Core Endpoints

#### Upload and Parse Resume
```http
POST /api/upload-resume
Content-Type: multipart/form-data

Parameters:
- file: Resume file (PDF/DOCX/TXT)
- full_name: Candidate full name (optional)
- target_role: Desired job title (optional)
- experience_level: entry|mid|senior|executive (optional)
- tone_preference: professional|casual
- region: US|UK|India
- additional_keywords: Comma-separated keywords

Response:
{
    "success": true,
    "data": { ... },  // Parsed resume data
    "raw_text": "...",  // Extracted text
    "message": "Resume uploaded and parsed successfully"
}
```

#### Analyze Resume
```http
POST /api/analyze
Content-Type: application/json

Body:
{
    "resume_data": { ... },  // From upload response
    "job_description": "..."  // Optional job description text
}

Response:
{
    "success": true,
    "ats_score": {
        "overall_score": 85.2,
        "ats_friendly_rating": "Good ATS Compatibility",
        "score_breakdown": {
            "formatting": 90.0,
            "structure": 85.0,
            "keywords": 80.0,
            "content_quality": 88.0,
            "readability": 92.0
        },
        "issues_found": [...],
        "recommendations": [...]
    },
    "job_match": { ... },  // If job description provided
    "keyword_suggestions": { ... },
    "extracted_fields": { ... }
}
```

#### Generate Optimized Resume
```http
POST /api/optimize
Content-Type: application/json

Body:
{
    "resume_data": { ... },
    "optimization_request": {
        "tone": "professional",
        "region": "US",
        "target_role": "Software Engineer"
    }
}

Response:
{
    "success": true,
    "bullet_improvements": [...],
    "overall_suggestions": [...],
    "optimized_sections": { ... }
}
```

#### LinkedIn Optimization
```http
POST /api/linkedin-optimize
Content-Type: application/json

Body:
{
    "resume_data": { ... },
    "linkedin_request": {
        "linkedin_url": "https://linkedin.com/in/profile",  // Optional
        "current_headline": "...",  // Optional
        "current_about": "..."  // Optional
    }
}

Response:
{
    "success": true,
    "headline_options": [...],
    "about_summary": "...",
    "skill_recommendations": [...],
    "optimization_tips": [...]
}
```

## 🧠 NLP Pipeline Deep Dive

The application implements a sophisticated NLP pipeline:

### 1. Resume Parsing (`nlp/resume_parser.py`)
- **NER Extraction**: Uses spaCy for identifying skills, organizations, roles
- **Contact Detection**: Email, phone, LinkedIn profile extraction
- **Section Parsing**: Experience, education, skills, projects identification
- **Date Parsing**: Employment duration and education timeline extraction

### 2. Job Description Analysis (`nlp/job_matcher.py`)
- **Requirement Extraction**: Skills, experience level, education requirements
- **Semantic Matching**: Sentence-BERT embeddings for similarity scoring
- **TF-IDF Analysis**: Keyword importance scoring
- **Experience Matching**: Cosine similarity between job and resume content

### 3. ATS Compatibility Scoring (`nlp/ats_scorer.py`)
- **Formatting Rules**: Font size, margins, section order compliance
- **Parsing Issues**: Tables, images, headers/footers detection
- **Structure Analysis**: Essential sections presence and quality
- **Content Quality**: Experience descriptions, quantification, readability

### 4. AI-Powered Suggestions (`nlp/suggestion_generator.py`)
- **Action Verb Enhancement**: Weak verb identification and replacement
- **Quantification Suggestions**: Metric addition recommendations
- **Professional Tone**: Language formality adjustments
- **Keyword Optimization**: Missing skill identification

### 5. Resume Generation (`nlp/resume_generator.py`)
- **Multi-format Output**: PDF, DOCX, TXT generation
- **Regional Formatting**: US, UK, India phone/date formats
- **Tone Application**: Professional vs. casual language
- **Layout Optimization**: ATS-friendly structure

## 📊 Sample Output

Running the demo script produces detailed analysis:

```
============================================================
AI RESUME CHECKER & CUSTOMIZER - DEMO
============================================================

1. Initializing NLP components...
✓ All components initialized successfully

2. Parsing resume...
✓ Resume parsed successfully
   Contact: {'email': 'sarah.johnson@email.com', 'phone': '555-123-4567'}
   Skills found: 15 total
   Experience entries: 3
   Education entries: 1

3. Analyzing job description...
✓ Job description analyzed successfully
   Job title: Senior Frontend Developer
   Company: TechCorp Inc.
   Required skills: 12 total
   Experience level: Senior Level (5+ years)

4. Calculating ATS compatibility score...
✓ ATS analysis completed
   Overall ATS Score: 82.5/100
   Rating: Good ATS Compatibility
   Score Breakdown:
     Formatting: 85.0/100
     Keywords: 78.0/100
     Structure: 90.0/100
     Content Quality: 85.0/100
     Readability: 88.0/100

5. Performing job matching analysis...
✓ Job matching analysis completed
   Overall Match Score: 76.3/100
   Skills Match: 72.0/100
   Experience Match: 85.0/100
   Education Match: 90.0/100
   Missing Skills:
     Web: TypeScript, GraphQL, Cypress
     Cloud: GCP

6. Generating AI-powered suggestions...
✓ Bullet point improvements generated
✓ Keyword suggestions generated

7. Generating LinkedIn optimization suggestions...
✓ LinkedIn suggestions generated
   Headline options: 3 generated
   About summary: Generated
   Skill recommendations: 15 skills suggested

8. DEMO SUMMARY
----------------------------------------
ATS Score: 82.5/100 - Good ATS Compatibility
Job Match: 76.3/100

Top Recommendations:
• Add missing skills relevant to the job description

✓ Demo completed successfully!
```

## 🧪 Advanced Usage

### Custom Resume Analysis
```bash
# Analyze your own resume and job description
python nlp/demo.py /path/to/your/resume.pdf /path/to/job/description.txt
```

### API Testing with curl
```bash
# Health check
curl http://localhost:8000/api/health

# Upload resume
curl -X POST -F "file=@resume.pdf" \
     -F "target_role=Software Engineer" \
     -F "experience_level=senior" \
     http://localhost:8000/api/upload-resume
```

### Integration Examples
```python
# Python integration
import requests

# Upload and analyze resume
with open('resume.pdf', 'rb') as f:
    response = requests.post('http://localhost:8000/api/upload-resume', 
                           files={'file': f},
                           data={'target_role': 'Data Scientist'})
    
resume_data = response.json()
print(f"ATS Score: {resume_data['ats_score']['overall_score']}")
```

## 🔧 Development Guide

### Project Architecture
- **Frontend**: Vanilla JavaScript with modern ES6+ features
- **Backend**: FastAPI with async/await patterns
- **NLP**: spaCy + HuggingFace Transformers + Sentence Transformers
- **Data**: JSON-based data structures throughout

### Adding New Features

#### 1. New NLP Module
```python
# nlp/new_module.py
class NewAnalyzer:
    def __init__(self):
        # Initialize your analyzer
        pass
    
    def analyze(self, text: str) -> Dict:
        # Your analysis logic
        return {"analysis_result": "..."}

# Add to nlp/__init__.py
from .new_module import NewAnalyzer
```

#### 2. New API Endpoint
```python
# backend/main.py
@app.post("/api/new-endpoint")
async def new_endpoint(data: dict):
    # Your endpoint logic
    return {"success": True, "result": "..."}
```

#### 3. Frontend Enhancement
```javascript
// frontend/app.js
async function newFeature() {
    const response = await fetch('/api/new-endpoint', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    
    const result = await response.json();
    displayResults(result);
}
```

### Performance Optimization

- **Model Caching**: Models are loaded once on startup
- **Async Processing**: Non-blocking API endpoints
- **Chunked Processing**: Large documents processed in chunks
- **Memory Management**: Efficient text processing and cleanup

### Error Handling

- **Graceful Fallbacks**: PDF parsing falls back to OCR if needed
- **Model Fallbacks**: Local models used if external APIs fail
- **Input Validation**: Comprehensive request validation
- **Logging**: Detailed error logging for debugging

## 🚀 Deployment

### Local Development
```bash
# Development server with auto-reload
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Deployment
```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker Deployment
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm
COPY . .
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🧪 Testing

### Unit Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=nlp --cov-report=html
```

### Integration Tests
```bash
# Test API endpoints
pytest tests/test_api.py -v

# Test NLP pipeline
pytest tests/test_nlp.py -v
```

## 🐛 Troubleshooting

### Common Issues

#### "spaCy model not found"
```bash
python -m spacy download en_core_web_sm
```

#### "Sentence transformer download fails"
```bash
# Manual download
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

#### "PDF parsing fails"
```bash
# Install additional dependencies
pip install pdfplumber PyPDF2
```

#### "DOCX generation fails"
```bash
# Install document libraries
pip install python-docx reportlab
```

### Performance Issues

- **Slow model loading**: Models are cached after first load
- **High memory usage**: Restart application periodically
- **Slow text processing**: Use shorter text samples for testing

## 📚 Model Information

### Required Models
- **spaCy**: `en_core_web_sm` (50MB) - English language model
- **Sentence Transformers**: `all-MiniLM-L6-v2` (90MB) - Semantic embeddings
- **Optional**: Local GPT model for advanced text generation

### Model Storage
```
~/.cache/spacy/          # spaCy models
~/.cache/huggingface/    # HuggingFace models
models/                  # Custom model files
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run tests: `pytest`
5. Commit your changes: `git commit -m 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

### Code Style
- Follow PEP 8 for Python code
- Use type hints where appropriate
- Add docstrings for all functions
- Keep functions focused and small

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- spaCy team for excellent NLP tools
- HuggingFace for transformer models
- FastAPI team for the amazing web framework
- All contributors and users of this project

---

**Ready to optimize your resume with AI? Start by running the demo script!**

```bash
python nlp/demo.py
```
