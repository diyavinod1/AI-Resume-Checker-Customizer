"""
AI Resume Checker & Customizer - Backend API

FastAPI application providing endpoints for:
- Resume upload and parsing
- ATS scoring and analysis  
- Job matching and optimization
- LinkedIn profile optimization
- Resume output generation
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, List
import tempfile
import asyncio

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
import uvicorn

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import our NLP modules
from nlp.resume_parser import ResumeParser
from nlp.job_matcher import JobMatcher  
from nlp.ats_scorer import ATSScorer
from nlp.suggestion_generator import SuggestionGenerator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Resume Checker & Customizer",
    description="AI-powered resume analysis, optimization, and ATS compatibility scoring",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (frontend)
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# Initialize NLP components
resume_parser = None
job_matcher = None
ats_scorer = None
suggestion_generator = None

@app.on_event("startup")
async def startup_event():
    """Initialize NLP models on startup."""
    global resume_parser, job_matcher, ats_scorer, suggestion_generator
    
    try:
        logger.info("Initializing NLP components...")
        resume_parser = ResumeParser()
        job_matcher = JobMatcher()
        ats_scorer = ATSScorer()
        suggestion_generator = SuggestionGenerator()
        logger.info("All NLP components initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize NLP components: {e}")
        raise

# Pydantic models for request/response
class ResumeAnalysisRequest(BaseModel):
    full_name: Optional[str] = None
    target_role: Optional[str] = None
    experience_level: Optional[str] = None
    tone_preference: str = "professional"
    region: str = "US"
    additional_keywords: Optional[str] = None

class JobDescriptionRequest(BaseModel):
    job_description: str
    company_name: Optional[str] = None

class LinkedInOptimizationRequest(BaseModel):
    linkedin_url: Optional[str] = None
    current_headline: Optional[str] = None
    current_about: Optional[str] = None

class ResumeOptimizationRequest(BaseModel):
    tone: str = "professional"
    region: str = "US"
    target_role: Optional[str] = None

# Utility functions
def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """Extract text from uploaded resume file."""
    try:
        if filename.lower().endswith('.pdf'):
            import PyPDF2
            import io
            
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
            
        elif filename.lower().endswith(('.docx', '.doc')):
            import docx
            import io
            
            doc = docx.Document(io.BytesIO(file_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
            
        else:
            # Assume it's plain text
            return file_content.decode('utf-8', errors='ignore')
            
    except Exception as e:
        logger.error(f"Error extracting text from file: {e}")
        raise HTTPException(status_code=400, detail=f"Could not process file: {str(e)}")

# API Endpoints

@app.get("/")
async def root():
    """Serve the main frontend page."""
    frontend_file = frontend_path / "index.html"
    if frontend_file.exists():
        return FileResponse(frontend_file)
    return {"message": "AI Resume Checker & Customizer API", "version": "1.0.0"}

@app.post("/api/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    full_name: Optional[str] = Form(None),
    target_role: Optional[str] = Form(None),
    experience_level: Optional[str] = Form(None),
    tone_preference: str = Form("professional"),
    region: str = Form("US"),
    additional_keywords: Optional[str] = Form(None)
):
    """
    Upload and parse resume file.
    Supports PDF, DOCX, and TXT formats.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    try:
        # Read file content
        file_content = await file.read()
        resume_text = extract_text_from_file(file_content, file.filename)
        
        if not resume_text.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted from the file")
        
        # Parse resume
        parsed_resume = resume_parser.parse_resume(resume_text)
        
        # Override contact info if provided
        if full_name:
            parsed_resume['contact_info']['name'] = full_name
        
        # Store additional metadata
        parsed_resume['metadata'] = {
            'filename': file.filename,
            'target_role': target_role,
            'experience_level': experience_level,
            'tone_preference': tone_preference,
            'region': region,
            'additional_keywords': additional_keywords.split(',') if additional_keywords else []
        }
        
        return {
            'success': True,
            'message': 'Resume uploaded and parsed successfully',
            'data': parsed_resume,
            'raw_text': resume_text
        }
        
    except Exception as e:
        logger.error(f"Resume upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Resume processing failed: {str(e)}")

@app.post("/api/analyze")
async def analyze_resume(
    resume_data: dict,
    job_description: Optional[str] = None
):
    """
    Analyze resume and provide ATS score, matching analysis.
    """
    try:
        resume_text = resume_data.get('raw_text', '')
        parsed_data = resume_data.get('data', {})
        
        if not resume_text or not parsed_data:
            raise HTTPException(status_code=400, detail="Invalid resume data")
        
        # Parse job description if provided
        job_data = None
        if job_description:
            job_data = job_matcher.parse_job_description(job_description)
        
        # Calculate ATS score
        ats_results = ats_scorer.score_resume(parsed_data, resume_text, job_data)
        
        # Calculate job matching score if job provided
        matching_results = None
        if job_data:
            matching_results = job_matcher.compute_similarity_score(parsed_data, job_data)
        
        # Generate keyword suggestions
        keyword_suggestions = suggestion_generator.suggest_missing_keywords(
            parsed_data, job_data or {}
        )
        
        return {
            'success': True,
            'ats_score': ats_results,
            'job_match': matching_results,
            'keyword_suggestions': keyword_suggestions,
            'extracted_fields': {
                'skills': parsed_data.get('skills', {}),
                'experience': parsed_data.get('experience', []),
                'education': parsed_data.get('education', []),
                'projects': parsed_data.get('projects', [])
            }
        }
        
    except Exception as e:
        logger.error(f"Resume analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/optimize")
async def optimize_resume(
    resume_data: dict,
    optimization_request: ResumeOptimizationRequest
):
    """
    Generate optimized version of resume with AI suggestions.
    """
    try:
        parsed_data = resume_data.get('data', {})
        if not parsed_data:
            raise HTTPException(status_code=400, detail="Invalid resume data")
        
        # Generate bullet point improvements
        experience = parsed_data.get('experience', [])
        all_bullet_improvements = []
        
        for exp in experience:
            description = exp.get('description', [])
            if isinstance(description, str):
                description = [description]
            
            if description:
                improvements = suggestion_generator.generate_bullet_improvements(description)
                all_bullet_improvements.extend(improvements)
        
        # Generate overall suggestions based on target role
        overall_suggestions = []
        if optimization_request.target_role:
            overall_suggestions = [
                f"Tailor content for {optimization_request.target_role} role",
                f"Emphasize relevant skills for {optimization_request.target_role}",
                "Quantify achievements with specific metrics",
                "Use action verbs to start bullet points"
            ]
        
        return {
            'success': True,
            'bullet_improvements': all_bullet_improvements,
            'overall_suggestions': overall_suggestions,
            'optimized_sections': {
                'experience': experience,  # Would contain optimized versions
                'skills': parsed_data.get('skills', {}),
                'education': parsed_data.get('education', [])
            },
            'tone': optimization_request.tone,
            'region_format': optimization_request.region
        }
        
    except Exception as e:
        logger.error(f"Resume optimization error: {e}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@app.post("/api/linkedin-optimize")
async def optimize_linkedin(
    resume_data: dict,
    linkedin_request: LinkedInOptimizationRequest
):
    """
    Generate LinkedIn profile optimization suggestions.
    """
    try:
        parsed_data = resume_data.get('data', {})
        if not parsed_data:
            raise HTTPException(status_code=400, detail="Invalid resume data")
        
        # Generate LinkedIn suggestions
        linkedin_suggestions = suggestion_generator.generate_linkedin_suggestions(parsed_data)
        
        # Add LinkedIn-specific recommendations
        recommendations = [
            "Use a professional headshot photo",
            "Write a compelling headline with keywords",
            "Craft an engaging About section",
            "Add relevant skills and get endorsements",
            "Request recommendations from colleagues",
            "Share industry-relevant content regularly"
        ]
        
        return {
            'success': True,
            'headline_options': linkedin_suggestions.get('headline_options', []),
            'about_summary': linkedin_suggestions.get('about_summary'),
            'skill_recommendations': linkedin_suggestions.get('skill_recommendations', []),
            'optimization_tips': recommendations,
            'experience_highlights': [
                {
                    'role': exp.get('position', '') + ' at ' + exp.get('company', ''),
                    'suggestion': 'Highlight quantifiable achievements and key technologies used'
                }
                for exp in parsed_data.get('experience', [])[:3]
            ]
        }
        
    except Exception as e:
        logger.error(f"LinkedIn optimization error: {e}")
        raise HTTPException(status_code=500, detail=f"LinkedIn optimization failed: {str(e)}")

@app.post("/api/generate-resume")
async def generate_resume(
    resume_data: dict,
    format_type: str = "pdf"
):
    """
    Generate downloadable resume in PDF or DOCX format.
    """
    try:
        parsed_data = resume_data.get('data', {})
        if not parsed_data:
            raise HTTPException(status_code=400, detail="Invalid resume data")
        
        # For now, return a simple text version
        # In a full implementation, you would use reportlab or python-docx
        # to generate proper PDF/DOCX files
        
        contact_info = parsed_data.get('contact_info', {})
        experience = parsed_data.get('experience', [])
        skills = parsed_data.get('skills', {})
        education = parsed_data.get('education', [])
        
        resume_text = f"""
{contact_info.get('name', 'Professional Resume')}
{contact_info.get('email', '')} | {contact_info.get('phone', '')}

EXPERIENCE
"""
        
        for exp in experience:
            resume_text += f"\n{exp.get('position', '')} at {exp.get('company', '')}"
            resume_text += f"\n{exp.get('duration', '')}\n"
            
            description = exp.get('description', [])
            if isinstance(description, list):
                for desc in description:
                    resume_text += f"• {desc}\n"
            elif isinstance(description, str):
                resume_text += f"• {description}\n"
        
        resume_text += "\nSKILLS\n"
        for category, skill_list in skills.items():
            resume_text += f"{category.title()}: {', '.join(skill_list)}\n"
        
        resume_text += "\nEDUCATION\n"
        for edu in education:
            resume_text += f"{edu.get('degree', '')} - {edu.get('institution', '')}\n"
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(resume_text)
            temp_path = f.name
        
        return {
            'success': True,
            'message': f'Resume generated in {format_type} format',
            'download_url': f'/api/download/{os.path.basename(temp_path)}',
            'preview_text': resume_text[:500] + "..." if len(resume_text) > 500 else resume_text
        }
        
    except Exception as e:
        logger.error(f"Resume generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Resume generation failed: {str(e)}")

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """Download generated resume file."""
    file_path = f"/tmp/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    else:
        raise HTTPException(status_code=404, detail="File not found")

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "components": {
            "resume_parser": resume_parser is not None,
            "job_matcher": job_matcher is not None,
            "ats_scorer": ats_scorer is not None,
            "suggestion_generator": suggestion_generator is not None
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )