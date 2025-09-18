# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is an AI-powered resume analysis and optimization system built with FastAPI (backend), vanilla JavaScript (frontend), and sophisticated NLP processing using spaCy, sentence transformers, and scikit-learn. The application provides ATS scoring, job matching, resume parsing, and AI-powered suggestions for optimization.

## Common Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install dependencies  
pip install -r requirements.txt

# Download required NLP models
python -m spacy download en_core_web_sm
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Development Server
```bash
# Start FastAPI development server (with auto-reload)
python backend/main.py

# Alternative with uvicorn directly
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing and Demo
```bash
# Run complete NLP pipeline demonstration
python nlp/demo.py

# Test with custom files
python nlp/demo.py /path/to/resume.pdf /path/to/job.txt

# API health check
curl http://localhost:8000/api/health

# Test resume upload
curl -X POST -F "file=@resume.pdf" -F "target_role=Software Engineer" http://localhost:8000/api/upload-resume
```

### Production Deployment  
```bash
# Install production server
pip install gunicorn

# Run with Gunicorn (4 workers)
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Core Architecture

### High-Level System Design
The system follows a clean 3-tier architecture:

1. **Frontend Layer** (`frontend/`): Vanilla JavaScript SPA with modern UI
2. **API Layer** (`backend/main.py`): FastAPI REST API with async endpoints
3. **NLP Processing Layer** (`nlp/`): Modular NLP pipeline with 4 core components

### NLP Pipeline Architecture
The heart of the application is a sophisticated 4-component NLP pipeline:

**1. Resume Parser** (`nlp/resume_parser.py`)
- Uses spaCy NER for entity extraction (organizations, skills, dates)
- Pattern-based extraction for contact info, skills categorization
- Section-aware parsing for experience, education, projects
- Handles multiple resume formats (PDF/DOCX via PyPDF2/python-docx)

**2. Job Matcher** (`nlp/job_matcher.py`)  
- Sentence-BERT embeddings for semantic similarity (`all-MiniLM-L6-v2`)
- TF-IDF vectorization with cosine similarity for keyword matching
- Experience level extraction using regex patterns
- Company/location extraction via spaCy NER

**3. ATS Scorer** (`nlp/ats_scorer.py`)
- Rule-based scoring with weighted components (formatting 25%, keywords 30%, structure 20%, content 15%, readability 10%)
- Detects ATS parsing issues (tables, images, special characters)
- Validates resume structure completeness
- Keyword density analysis against job requirements

**4. Suggestion Generator** (`nlp/suggestion_generator.py`)
- Local DistilGPT2 model for text generation
- Action verb categorization and improvement suggestions  
- Industry-specific keyword recommendations
- Professional tone adjustments and quantification suggestions

### Data Flow
```
Resume Upload → Text Extraction → NLP Parsing → Parallel Processing:
├── ATS Scoring (formatting, structure, keywords)
├── Job Matching (if job description provided)  
└── AI Suggestions (bullet improvements, keywords, tone)
→ Results Aggregation → Frontend Display
```

### API Design Patterns
- All endpoints follow RESTful conventions with `/api/` prefix
- Consistent error handling with HTTP status codes
- Request/response models defined with Pydantic
- Async/await patterns for non-blocking operations
- File uploads handled with multipart form data

## Key Technical Details

### Model Loading Strategy
- All NLP models are loaded once at FastAPI startup (`@app.on_event("startup")`)
- Models are cached in global variables for reuse across requests
- Graceful fallbacks if models fail to load
- Memory-efficient sentence transformer usage

### File Processing Pipeline
1. **Upload**: Multipart form handling with file validation
2. **Text Extraction**: Format-specific extraction (PDF: PyPDF2, DOCX: python-docx)
3. **NLP Processing**: spaCy document processing with custom skill patterns
4. **Error Handling**: Graceful fallbacks and detailed error messages

### Frontend State Management
- Global state variables for resume data, analysis results, optimization data
- Event-driven UI updates with async/await API calls
- Progressive enhancement with loading states and error handling
- Mobile-responsive sidebar navigation with toggle functionality

### Skill Categorization System
Skills are organized into weighted categories:
- `programming`: Python, Java, JavaScript, etc. (weight: 1.5)
- `web`: HTML, CSS, React, Angular, etc. (weight: 1.3) 
- `data`: SQL, pandas, TensorFlow, etc. (weight: 1.4)
- `cloud`: AWS, Docker, Kubernetes, etc. (weight: 1.2)
- `tools`: Git, Jira, etc. (weight: 1.0)

## Development Patterns

### Adding New NLP Features
1. Create new module in `nlp/` following existing patterns
2. Add module import to `nlp/__init__.py`
3. Initialize in `backend/main.py` startup event
4. Create API endpoint following existing patterns
5. Update frontend with new UI components

### Error Handling Strategy
- NLP modules use try/catch with logging
- API endpoints return structured error responses
- Frontend displays user-friendly error messages
- Model loading failures are caught at startup

### Performance Considerations
- Models are loaded once and reused (not per-request)
- Text processing is chunked for large documents
- Sentence transformers use efficient batch processing
- API responses include progress indicators for long operations

### File Structure Conventions
- `nlp/`: All NLP processing logic
- `backend/`: FastAPI application and API endpoints
- `frontend/`: Static HTML/CSS/JS files
- `sample_data/`: Test files for development
- `models/`: Custom model storage (not tracked in git)

## Testing Approach

The demo script (`nlp/demo.py`) serves as both example and integration test:
1. Loads sample data or accepts custom file paths
2. Runs complete pipeline end-to-end  
3. Displays detailed progress and results
4. Validates all components work together

For API testing, use the health check endpoint to verify all models loaded correctly.

## Common Troubleshooting

**Model Loading Issues**: Ensure spaCy and sentence-transformers models are downloaded. Check startup logs for initialization errors.

**PDF Parsing Failures**: Install additional dependencies (`pdfplumber`) or check if PDF is text-based vs image-based.

**Memory Issues**: NLP models require 4GB+ RAM. Restart application if memory usage grows over time.

**CORS Issues**: Update CORS settings in `backend/main.py` for production deployment.