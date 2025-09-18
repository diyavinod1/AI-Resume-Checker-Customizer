"""
AI Resume Checker & Customizer - NLP Package

This package contains all the natural language processing modules for:
- Resume parsing and extraction
- Job description analysis
- ATS compatibility scoring
- Semantic matching and similarity calculation
- AI-powered suggestions and optimizations
"""

from .resume_parser import ResumeParser
from .job_matcher import JobMatcher
from .ats_scorer import ATSScorer
from .suggestion_generator import SuggestionGenerator

__version__ = "1.0.0"
__author__ = "AI Resume Checker Team"

__all__ = [
    "ResumeParser",
    "JobMatcher", 
    "ATSScorer",
    "SuggestionGenerator"
]
