"""
Job Matcher Module

Parses job descriptions and computes semantic similarity with resume data.
Uses TF-IDF and sentence embeddings for matching and scoring.
"""

import re
import numpy as np
from typing import Dict, List, Tuple, Set
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import spacy
import logging

logger = logging.getLogger(__name__)

class JobMatcher:
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        """Initialize job matcher with embedding model."""
        try:
            self.embedding_model = SentenceTransformer(embedding_model)
            self.nlp = spacy.load("en_core_web_sm")
            logger.info(f"Loaded embedding model: {embedding_model}")
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            raise
        
        # Job description section patterns
        self.jd_sections = {
            'requirements': r'(?:requirements|qualifications|skills?\s+required|must\s+have)',
            'responsibilities': r'(?:responsibilities|duties|role|what\s+you\'ll\s+do)',
            'experience': r'(?:experience|background|years?|minimum)',
            'education': r'(?:education|degree|qualification)',
            'nice_to_have': r'(?:nice\s+to\s+have|preferred|bonus|plus)'
        }
        
        # Skill importance weights
        self.skill_weights = {
            'programming': 1.5,
            'web': 1.3,
            'data': 1.4,
            'cloud': 1.2,
            'tools': 1.0
        }
    
    def parse_job_description(self, jd_text: str) -> Dict:
        """Parse job description and extract structured information."""
        doc = self.nlp(jd_text)
        
        # Extract basic information
        result = {
            'title': self._extract_job_title(jd_text),
            'company': self._extract_company(doc),
            'location': self._extract_location(doc),
            'experience_level': self._extract_experience_level(jd_text),
            'required_skills': self._extract_required_skills(jd_text),
            'responsibilities': self._extract_responsibilities(jd_text),
            'education_requirements': self._extract_education_requirements(jd_text),
            'keywords': self._extract_keywords(jd_text),
            'sections': self._split_sections(jd_text)
        }
        
        return result
    
    def _extract_job_title(self, text: str) -> str:
        """Extract job title from job description."""
        # Look for common job title patterns
        title_patterns = [
            r'job\s+title[:\s]+([^\n]+)',
            r'position[:\s]+([^\n]+)',
            r'^([A-Z][A-Za-z\s]+(?:Engineer|Developer|Manager|Analyst|Specialist|Coordinator))',
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()
        
        # Fallback: extract from first line if it looks like a title
        first_line = text.strip().split('\n')[0]
        if len(first_line) < 100 and any(keyword in first_line.lower() for keyword in 
                                        ['engineer', 'developer', 'manager', 'analyst']):
            return first_line.strip()
        
        return "Not specified"
    
    def _extract_company(self, doc) -> str:
        """Extract company name using NER."""
        for ent in doc.ents:
            if ent.label_ == "ORG":
                return ent.text
        return "Not specified"
    
    def _extract_location(self, doc) -> str:
        """Extract location using NER."""
        locations = []
        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC"]:
                locations.append(ent.text)
        
        return ", ".join(locations) if locations else "Not specified"
    
    def _extract_experience_level(self, text: str) -> str:
        """Extract required experience level."""
        experience_patterns = [
            (r'(\d+)\+?\s*years?\s+(?:of\s+)?experience', 'years'),
            (r'entry\s*level|junior', 'entry'),
            (r'senior|lead', 'senior'),
            (r'principal|staff|architect', 'principal')
        ]
        
        text_lower = text.lower()
        
        for pattern, level in experience_patterns:
            match = re.search(pattern, text_lower)
            if match:
                if level == 'years':
                    years = int(match.group(1))
                    if years <= 2:
                        return 'Entry Level (0-2 years)'
                    elif years <= 5:
                        return 'Mid Level (3-5 years)'
                    else:
                        return f'Senior Level ({years}+ years)'
                else:
                    return level.title() + ' Level'
        
        return 'Not specified'
    
    def _extract_required_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract required skills from job description."""
        # Use the same skill categories as resume parser
        tech_skills = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'go', 'rust', 'swift'],
            'web': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask'],
            'data': ['sql', 'mongodb', 'postgresql', 'mysql', 'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform'],
            'tools': ['git', 'jira', 'confluence', 'slack', 'figma', 'sketch']
        }
        
        required_skills = {category: [] for category in tech_skills.keys()}
        text_lower = text.lower()
        
        for category, skill_list in tech_skills.items():
            for skill in skill_list:
                if skill in text_lower:
                    required_skills[category].append(skill.title())
        
        return {k: v for k, v in required_skills.items() if v}
    
    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract key responsibilities from job description."""
        responsibilities = []
        
        # Find responsibilities section
        resp_match = None
        for section, pattern in self.jd_sections.items():
            if section == 'responsibilities':
                resp_match = re.search(pattern, text, re.IGNORECASE)
                break
        
        if resp_match:
            # Extract text after responsibilities section
            resp_text = text[resp_match.end():resp_match.end() + 1000]  # Limit text
            
            # Find bullet points
            bullet_patterns = [
                r'[•▪▫‣⁃]\s*(.+?)(?=[•▪▫‣⁃]|\n\n|\Z)',
                r'[\d]+\.\s*(.+?)(?=[\d]+\.|\n\n|\Z)',
                r'^[-*]\s*(.+?)(?=^[-*]|\n\n|\Z)'
            ]
            
            for pattern in bullet_patterns:
                matches = re.findall(pattern, resp_text, re.MULTILINE | re.DOTALL)
                for match in matches[:5]:  # Limit to 5 responsibilities
                    if len(match.strip()) > 10:
                        responsibilities.append(match.strip()[:150])
        
        return responsibilities
    
    def _extract_education_requirements(self, text: str) -> str:
        """Extract education requirements."""
        edu_patterns = [
            r"bachelor'?s?\s+degree",
            r"master'?s?\s+degree",
            r"phd|doctorate",
            r"high\s+school|hs\s+diploma"
        ]
        
        text_lower = text.lower()
        for pattern in edu_patterns:
            if re.search(pattern, text_lower):
                match = re.search(pattern, text_lower)
                return match.group().title()
        
        return "Not specified"
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords using TF-IDF."""
        # Preprocess text
        doc = self.nlp(text)
        
        # Extract meaningful tokens (nouns, proper nouns, adjectives)
        keywords = []
        for token in doc:
            if (token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and 
                not token.is_stop and 
                not token.is_punct and 
                len(token.text) > 2):
                keywords.append(token.lemma_.lower())
        
        # Use TF-IDF to score keywords
        if keywords:
            tfidf = TfidfVectorizer(max_features=20)
            try:
                tfidf.fit([' '.join(keywords)])
                feature_names = tfidf.get_feature_names_out()
                return list(feature_names)
            except:
                return list(set(keywords))[:20]
        
        return []
    
    def _split_sections(self, text: str) -> Dict[str, str]:
        """Split job description into sections."""
        sections = {}
        
        for section_name, pattern in self.jd_sections.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                start = match.start()
                # Find next section or end of text
                next_section_start = len(text)
                for other_pattern in self.jd_sections.values():
                    other_match = re.search(other_pattern, text[start + 50:], re.IGNORECASE)
                    if other_match:
                        next_section_start = min(next_section_start, start + 50 + other_match.start())
                
                sections[section_name] = text[start:next_section_start].strip()
        
        return sections
    
    def compute_similarity_score(self, resume_data: Dict, job_data: Dict) -> Dict:
        """Compute overall similarity score between resume and job description."""
        
        # 1. Skills matching score
        skills_score = self._compute_skills_score(
            resume_data.get('skills', {}), 
            job_data.get('required_skills', {})
        )
        
        # 2. Experience matching score
        experience_score = self._compute_experience_score(
            resume_data.get('experience', []), 
            job_data.get('responsibilities', [])
        )
        
        # 3. Education matching score
        education_score = self._compute_education_score(
            resume_data.get('education', []), 
            job_data.get('education_requirements', '')
        )
        
        # 4. Semantic similarity score
        semantic_score = self._compute_semantic_similarity(resume_data, job_data)
        
        # Weighted overall score
        overall_score = (
            skills_score * 0.4 +
            experience_score * 0.3 +
            semantic_score * 0.2 +
            education_score * 0.1
        )
        
        return {
            'overall_score': min(100, max(0, overall_score)),
            'skills_match': skills_score,
            'experience_match': experience_score,
            'education_match': education_score,
            'semantic_match': semantic_score,
            'missing_skills': self._get_missing_skills(
                resume_data.get('skills', {}), 
                job_data.get('required_skills', {})
            )
        }
    
    def _compute_skills_score(self, resume_skills: Dict, job_skills: Dict) -> float:
        """Compute skills matching score."""
        if not job_skills:
            return 50.0  # Neutral score if no job skills specified
        
        total_job_skills = sum(len(skills) for skills in job_skills.values())
        if total_job_skills == 0:
            return 50.0
        
        matched_skills = 0
        
        for category, job_skill_list in job_skills.items():
            resume_skill_list = resume_skills.get(category, [])
            resume_skills_lower = [skill.lower() for skill in resume_skill_list]
            
            for job_skill in job_skill_list:
                if job_skill.lower() in resume_skills_lower:
                    # Apply category weight
                    weight = self.skill_weights.get(category, 1.0)
                    matched_skills += weight
        
        # Calculate percentage with weights
        weighted_total = sum(len(skills) * self.skill_weights.get(category, 1.0) 
                           for category, skills in job_skills.items())
        
        score = (matched_skills / weighted_total) * 100 if weighted_total > 0 else 0
        return min(100, score)
    
    def _compute_experience_score(self, resume_experience: List, job_responsibilities: List) -> float:
        """Compute experience matching score using semantic similarity."""
        if not resume_experience or not job_responsibilities:
            return 30.0  # Low score if missing data
        
        # Combine resume experience descriptions
        resume_text = ' '.join([exp.get('description', '') for exp in resume_experience 
                               if isinstance(exp.get('description'), str)])
        
        if not resume_text.strip():
            return 30.0
        
        # Combine job responsibilities
        job_text = ' '.join(job_responsibilities)
        
        try:
            # Use sentence embeddings for semantic similarity
            resume_embedding = self.embedding_model.encode([resume_text])
            job_embedding = self.embedding_model.encode([job_text])
            
            similarity = cosine_similarity(resume_embedding, job_embedding)[0][0]
            return max(0, min(100, similarity * 100))
        except Exception as e:
            logger.error(f"Error computing experience similarity: {e}")
            return 30.0
    
    def _compute_education_score(self, resume_education: List, job_education: str) -> float:
        """Compute education matching score."""
        if not resume_education or job_education == "Not specified":
            return 70.0  # Neutral score
        
        job_education_lower = job_education.lower()
        
        for edu in resume_education:
            degree = edu.get('degree', '').lower()
            
            # Exact match
            if job_education_lower in degree:
                return 100.0
            
            # Degree level matching
            if "bachelor" in job_education_lower and "bachelor" in degree:
                return 90.0
            elif "master" in job_education_lower and "master" in degree:
                return 100.0
            elif "phd" in job_education_lower and "phd" in degree:
                return 100.0
        
        # Partial match for having any degree when degree is required
        if "degree" in job_education_lower and resume_education:
            return 60.0
        
        return 40.0
    
    def _compute_semantic_similarity(self, resume_data: Dict, job_data: Dict) -> float:
        """Compute overall semantic similarity between resume and job description."""
        # Extract text representations
        resume_text = self._create_resume_text(resume_data)
        job_text = self._create_job_text(job_data)
        
        if not resume_text.strip() or not job_text.strip():
            return 30.0
        
        try:
            # Use sentence embeddings
            resume_embedding = self.embedding_model.encode([resume_text])
            job_embedding = self.embedding_model.encode([job_text])
            
            similarity = cosine_similarity(resume_embedding, job_embedding)[0][0]
            return max(0, min(100, similarity * 100))
        except Exception as e:
            logger.error(f"Error computing semantic similarity: {e}")
            return 30.0
    
    def _create_resume_text(self, resume_data: Dict) -> str:
        """Create text representation of resume for embedding."""
        text_parts = []
        
        # Add skills
        skills = resume_data.get('skills', {})
        for category, skill_list in skills.items():
            text_parts.extend(skill_list)
        
        # Add experience
        experience = resume_data.get('experience', [])
        for exp in experience:
            text_parts.append(exp.get('position', ''))
            text_parts.append(exp.get('company', ''))
            if isinstance(exp.get('description'), list):
                text_parts.extend(exp['description'])
            elif isinstance(exp.get('description'), str):
                text_parts.append(exp['description'])
        
        # Add education
        education = resume_data.get('education', [])
        for edu in education:
            text_parts.append(edu.get('degree', ''))
            text_parts.append(edu.get('institution', ''))
        
        return ' '.join([part for part in text_parts if part and part != 'Not specified'])
    
    def _create_job_text(self, job_data: Dict) -> str:
        """Create text representation of job description for embedding."""
        text_parts = []
        
        # Add title and company
        text_parts.append(job_data.get('title', ''))
        text_parts.append(job_data.get('company', ''))
        
        # Add skills
        skills = job_data.get('required_skills', {})
        for category, skill_list in skills.items():
            text_parts.extend(skill_list)
        
        # Add responsibilities
        responsibilities = job_data.get('responsibilities', [])
        text_parts.extend(responsibilities)
        
        # Add keywords
        keywords = job_data.get('keywords', [])
        text_parts.extend(keywords)
        
        return ' '.join([part for part in text_parts if part and part != 'Not specified'])
    
    def _get_missing_skills(self, resume_skills: Dict, job_skills: Dict) -> Dict[str, List[str]]:
        """Identify skills mentioned in job but missing from resume."""
        missing_skills = {}
        
        for category, job_skill_list in job_skills.items():
            resume_skill_list = resume_skills.get(category, [])
            resume_skills_lower = [skill.lower() for skill in resume_skill_list]
            
            missing = []
            for job_skill in job_skill_list:
                if job_skill.lower() not in resume_skills_lower:
                    missing.append(job_skill)
            
            if missing:
                missing_skills[category] = missing
        
        return missing_skills

# Example usage
if __name__ == "__main__":
    # Test job matcher
    sample_job_description = """
    Senior Software Engineer
    TechCorp Inc.
    San Francisco, CA
    
    We are looking for a Senior Software Engineer with 5+ years of experience.
    
    Requirements:
    • Bachelor's degree in Computer Science or related field
    • 5+ years of software development experience
    • Strong proficiency in Python, JavaScript, and React
    • Experience with AWS, Docker, and Kubernetes
    • Knowledge of PostgreSQL and MongoDB
    
    Responsibilities:
    • Design and develop scalable web applications
    • Lead technical discussions and code reviews
    • Mentor junior developers
    • Collaborate with product managers and designers
    """
    
    matcher = JobMatcher()
    parsed_job = matcher.parse_job_description(sample_job_description)
    
    print("Parsed Job Description:")
    for key, value in parsed_job.items():
        print(f"{key}: {value}")
