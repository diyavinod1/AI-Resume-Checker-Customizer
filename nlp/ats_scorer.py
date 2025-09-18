"""
ATS (Applicant Tracking System) Scorer Module

Evaluates resume compatibility with ATS systems using rule-based checks.
Provides detailed scoring breakdown and formatting recommendations.
"""

import re
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class ATSScorer:
    def __init__(self):
        """Initialize ATS scorer with predefined rules and weights."""
        
        # ATS scoring weights (total should sum to 1.0)
        self.scoring_weights = {
            'formatting': 0.25,
            'keywords': 0.30,
            'structure': 0.20,
            'content_quality': 0.15,
            'readability': 0.10
        }
        
        # Common ATS parsing issues
        self.ats_problems = {
            'tables': r'\\begin\{tabular\}|<table|\\hline',
            'text_boxes': r'\\textbox|<div.*position.*absolute',
            'images': r'\\includegraphics|<img|\\image',
            'headers_footers': r'\\header|\\footer|<header|<footer',
            'columns': r'\\begin\{multicols\}|column-count|\\twocolumn',
            'special_chars': r'[^\w\s\-\.\,\;\:\(\)\[\]\/\@\#\$\%\&\*\+\=\!\?]',
            'fancy_fonts': r'\\font|font-family.*script|font-family.*decorative'
        }
    
    def score_resume(self, resume_data: Dict, resume_text: str, job_data: Dict = None) -> Dict:
        """
        Main method to score resume ATS compatibility.
        
        Args:
            resume_data: Parsed resume data from ResumeParser
            resume_text: Raw resume text
            job_data: Optional job description data for keyword matching
        
        Returns:
            Dictionary with detailed ATS score breakdown
        """
        logger.info("Starting ATS scoring analysis...")
        
        # Individual scoring components
        formatting_score = self._score_formatting(resume_text)
        structure_score = self._score_structure(resume_data)
        keyword_score = self._score_keywords(resume_data, job_data) if job_data else 50.0
        content_score = self._score_content_quality(resume_data)
        readability_score = self._score_readability(resume_text)
        
        # Calculate weighted overall score
        overall_score = (
            formatting_score * self.scoring_weights['formatting'] +
            structure_score * self.scoring_weights['structure'] +
            keyword_score * self.scoring_weights['keywords'] +
            content_score * self.scoring_weights['content_quality'] +
            readability_score * self.scoring_weights['readability']
        )
        
        # Generate detailed feedback
        issues = self._identify_issues(resume_text, resume_data)
        recommendations = self._generate_recommendations(issues, resume_data)
        
        result = {
            'overall_score': round(overall_score, 1),
            'score_breakdown': {
                'formatting': round(formatting_score, 1),
                'structure': round(structure_score, 1),
                'keywords': round(keyword_score, 1),
                'content_quality': round(content_score, 1),
                'readability': round(readability_score, 1)
            },
            'issues_found': issues,
            'recommendations': recommendations,
            'ats_friendly_rating': self._get_ats_rating(overall_score)
        }
        
        logger.info(f"ATS scoring complete. Overall score: {overall_score:.1f}")
        return result
    
    def _score_formatting(self, resume_text: str) -> float:
        """Score resume formatting for ATS compatibility."""
        score = 100.0
        
        # Check for problematic formatting
        for issue_type, pattern in self.ats_problems.items():
            if re.search(pattern, resume_text, re.IGNORECASE):
                if issue_type in ['tables', 'text_boxes', 'images']:
                    score -= 20
                elif issue_type in ['headers_footers', 'columns']:
                    score -= 15
                elif issue_type == 'special_chars':
                    char_count = len(re.findall(pattern, resume_text))
                    if char_count > 10:
                        score -= 10
                elif issue_type == 'fancy_fonts':
                    score -= 5
        
        # Check text length
        text_length = len(resume_text.strip())
        if text_length < 500:
            score -= 15
        elif text_length > 8000:
            score -= 10
        
        return max(0, score)
    
    def _score_structure(self, resume_data: Dict) -> float:
        """Score resume structure and section organization."""
        score = 100.0
        
        # Check for essential sections
        essential_sections = ['contact_info', 'experience', 'skills']
        for section in essential_sections:
            if not resume_data.get(section):
                score -= 25
        
        # Check contact information completeness
        contact_info = resume_data.get('contact_info', {})
        if not contact_info.get('email'):
            score -= 15
        if not contact_info.get('phone'):
            score -= 10
        
        # Check experience entries quality
        experience = resume_data.get('experience', [])
        if len(experience) == 0:
            score -= 30
        else:
            for exp in experience:
                if not exp.get('position') or exp.get('position') == 'Not specified':
                    score -= 10
                if not exp.get('company') or exp.get('company') == 'Not specified':
                    score -= 10
        
        # Check skills section
        skills = resume_data.get('skills', {})
        if not skills or sum(len(skill_list) for skill_list in skills.values()) < 3:
            score -= 20
        
        return max(0, score)
    
    def _score_keywords(self, resume_data: Dict, job_data: Dict) -> float:
        """Score keyword optimization against job description."""
        if not job_data:
            return 50.0  # Neutral score when no job data available
        
        score = 0.0
        total_possible = 0
        
        # Compare skills
        job_skills = job_data.get('required_skills', {})
        resume_skills = resume_data.get('skills', {})
        
        for category, job_skill_list in job_skills.items():
            total_possible += len(job_skill_list)
            resume_skill_list = resume_skills.get(category, [])
            resume_skills_lower = [skill.lower() for skill in resume_skill_list]
            
            for job_skill in job_skill_list:
                if job_skill.lower() in resume_skills_lower:
                    score += 1
        
        # Compare with job keywords
        job_keywords = job_data.get('keywords', [])
        resume_text_lower = str(resume_data).lower()
        
        keyword_matches = 0
        for keyword in job_keywords[:10]:  # Check top 10 keywords
            if keyword.lower() in resume_text_lower:
                keyword_matches += 1
        
        total_possible += 10  # Add keywords to total
        score += keyword_matches
        
        # Calculate percentage
        keyword_score = (score / total_possible * 100) if total_possible > 0 else 50
        return min(100, keyword_score)
    
    def _score_content_quality(self, resume_data: Dict) -> float:
        """Score the quality and completeness of resume content."""
        score = 100.0
        
        # Check experience descriptions
        experience = resume_data.get('experience', [])
        if experience:
            total_descriptions = 0
            quality_descriptions = 0
            
            for exp in experience:
                description = exp.get('description', '')
                if isinstance(description, list):
                    total_descriptions += len(description)
                    for desc in description:
                        if isinstance(desc, str) and len(desc) > 20:
                            quality_descriptions += 1
                elif isinstance(description, str) and len(description) > 20:
                    total_descriptions += 1
                    quality_descriptions += 1
            
            if total_descriptions == 0:
                score -= 30
            else:
                quality_ratio = quality_descriptions / total_descriptions
                if quality_ratio < 0.5:
                    score -= 20
        else:
            score -= 40
        
        return max(0, score)
    
    def _score_readability(self, resume_text: str) -> float:
        """Score resume readability and text quality."""
        score = 100.0
        
        # Basic readability checks
        sentences = re.split(r'[.!?]+', resume_text)
        words = resume_text.split()
        
        if len(sentences) > 1 and len(words) > 0:
            avg_words_per_sentence = len(words) / len(sentences)
            
            if avg_words_per_sentence > 25:
                score -= 15  # Too complex
            elif avg_words_per_sentence < 5:
                score -= 10  # Too simple
        
        return max(0, score)
    
    def _identify_issues(self, resume_text: str, resume_data: Dict) -> List[str]:
        """Identify specific ATS compatibility issues."""
        issues = []
        
        # Formatting issues
        for issue_type, pattern in self.ats_problems.items():
            if re.search(pattern, resume_text, re.IGNORECASE):
                issues.append(f"Contains {issue_type.replace('_', ' ')} that may cause ATS parsing issues")
        
        # Structure issues
        if not resume_data.get('contact_info', {}).get('email'):
            issues.append("Missing email address")
        
        if not resume_data.get('contact_info', {}).get('phone'):
            issues.append("Missing phone number")
        
        if not resume_data.get('experience'):
            issues.append("No work experience found")
        
        if not resume_data.get('skills') or sum(len(v) for v in resume_data.get('skills', {}).values()) < 3:
            issues.append("Insufficient skills listed")
        
        return issues
    
    def _generate_recommendations(self, issues: List[str], resume_data: Dict) -> List[str]:
        """Generate actionable recommendations for ATS optimization."""
        recommendations = []
        
        # Address specific issues
        if any('table' in issue.lower() for issue in issues):
            recommendations.append("Remove tables and use simple text formatting instead")
        
        if any('image' in issue.lower() for issue in issues):
            recommendations.append("Remove images, graphics, and logos for better ATS compatibility")
        
        if any('email' in issue.lower() for issue in issues):
            recommendations.append("Add a professional email address in the contact section")
        
        if any('phone' in issue.lower() for issue in issues):
            recommendations.append("Include your phone number in the contact information")
        
        if any('experience' in issue.lower() for issue in issues):
            recommendations.append("Add detailed work experience with job titles, companies, and dates")
        
        if any('skills' in issue.lower() for issue in issues):
            recommendations.append("Expand your skills section with relevant technical and soft skills")
        
        # General recommendations
        recommendations.extend([
            "Use standard section headings (Experience, Education, Skills)",
            "Save resume as both .docx and .pdf formats",
            "Use simple, clean formatting with consistent fonts",
            "Include relevant keywords from the job description",
            "Use bullet points for experience descriptions",
            "Quantify achievements with numbers and metrics where possible"
        ])
        
        return recommendations[:8]  # Limit to top 8 recommendations
    
    def _get_ats_rating(self, score: float) -> str:
        """Convert numerical score to ATS compatibility rating."""
        if score >= 85:
            return "Excellent ATS Compatibility"
        elif score >= 70:
            return "Good ATS Compatibility"
        elif score >= 55:
            return "Fair ATS Compatibility - Needs Improvement"
        elif score >= 40:
            return "Poor ATS Compatibility - Major Issues"
        else:
            return "Very Poor ATS Compatibility - Critical Issues"