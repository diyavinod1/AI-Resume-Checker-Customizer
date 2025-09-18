"""
Resume Parser Module

Extracts structured information from resume text using NLP techniques.
Implements Named Entity Recognition (NER) for skills, organizations, roles, and durations.
"""

import re
import spacy
from typing import Dict, List, Set, Optional
import pandas as pd
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeParser:
    def __init__(self, model_name: str = "en_core_web_sm"):
        """Initialize the resume parser with spaCy model."""
        try:
            self.nlp = spacy.load(model_name)
            logger.info(f"Loaded spaCy model: {model_name}")
        except OSError:
            logger.error(f"spaCy model {model_name} not found. Please install with: python -m spacy download {model_name}")
            raise
        
        # Predefined skill categories and keywords
        self.tech_skills = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'go', 'rust', 'swift'],
            'web': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask'],
            'data': ['sql', 'mongodb', 'postgresql', 'mysql', 'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform'],
            'tools': ['git', 'jira', 'confluence', 'slack', 'figma', 'sketch']
        }
        
        # Common section headers
        self.section_patterns = {
            'experience': r'(?:work\s+)?experience|employment|professional\s+experience',
            'education': r'education|academic\s+background|qualifications',
            'skills': r'skills|technical\s+skills|competencies|expertise',
            'projects': r'projects|portfolio|selected\s+projects',
            'contact': r'contact|personal\s+information'
        }
    
    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information from resume text."""
        contact_info = {}
        
        # Email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Phone extraction
        phone_pattern = r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info['phone'] = ''.join(phones[0])
        
        # LinkedIn extraction
        linkedin_pattern = r'linkedin\.com/in/([A-Za-z0-9-]+)'
        linkedin_matches = re.findall(linkedin_pattern, text)
        if linkedin_matches:
            contact_info['linkedin'] = f"linkedin.com/in/{linkedin_matches[0]}"
        
        return contact_info
    
    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract skills from resume text using pattern matching and NER."""
        skills_found = {category: [] for category in self.tech_skills.keys()}
        text_lower = text.lower()
        
        # Pattern-based skill extraction
        for category, skill_list in self.tech_skills.items():
            for skill in skill_list:
                if skill in text_lower:
                    skills_found[category].append(skill.title())
        
        # Additional skills using spaCy NER and custom patterns
        doc = self.nlp(text)
        for token in doc:
            if token.pos_ in ['NOUN', 'PROPN'] and len(token.text) > 2:
                # Check if it's a potential technical skill
                if any(char.isupper() for char in token.text) or token.text.lower() in text_lower:
                    for category, skill_list in self.tech_skills.items():
                        if token.text.lower() in [s.lower() for s in skill_list]:
                            if token.text.title() not in skills_found[category]:
                                skills_found[category].append(token.text.title())
        
        return {k: v for k, v in skills_found.items() if v}
    
    def extract_experience(self, text: str) -> List[Dict[str, str]]:
        """Extract work experience entries from resume text."""
        experiences = []
        doc = self.nlp(text)
        
        # Find organizations using spaCy NER
        organizations = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
        
        # Extract date patterns
        date_patterns = [
            r'(\d{4})\s*[-–—]\s*(\d{4}|\w+)',
            r'(\w+\s+\d{4})\s*[-–—]\s*(\w+\s+\d{4}|\w+)',
            r'(\d{1,2}/\d{4})\s*[-–—]\s*(\d{1,2}/\d{4}|\w+)'
        ]
        
        dates_found = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates_found.extend(matches)
        
        # Try to pair organizations with dates and extract job titles
        sentences = [sent.text for sent in doc.sents]
        
        for i, org in enumerate(organizations[:5]):  # Limit to first 5 organizations
            experience = {
                'company': org,
                'position': 'Not specified',
                'duration': 'Not specified',
                'description': []
            }
            
            # Find the sentence containing the organization
            for sentence in sentences:
                if org in sentence:
                    # Look for job titles (typically capitalized words before the company)
                    words = sentence.split()
                    org_index = next((i for i, word in enumerate(words) if org in word), -1)
                    
                    if org_index > 0:
                        potential_title = ' '.join(words[:org_index]).strip()
                        if potential_title and len(potential_title) < 100:
                            experience['position'] = potential_title
                    break
            
            # Add date if available
            if i < len(dates_found):
                experience['duration'] = f"{dates_found[i][0]} - {dates_found[i][1]}"
            
            experiences.append(experience)
        
        return experiences
    
    def extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education information from resume text."""
        education = []
        doc = self.nlp(text)
        
        # Common degree patterns
        degree_patterns = [
            r'(bachelor\'?s?|ba|bs|b\.a\.|b\.s\.)\s+(of\s+)?([\w\s]+)',
            r'(master\'?s?|ma|ms|m\.a\.|m\.s\.)\s+(of\s+)?([\w\s]+)',
            r'(phd|ph\.d\.|doctorate)\s+(in\s+)?([\w\s]+)',
            r'(associate\'?s?|aa|as)\s+(of\s+)?([\w\s]+)'
        ]
        
        for pattern in degree_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                degree_type = match[0].title()
                field = match[2].strip() if len(match) > 2 else 'Not specified'
                
                education.append({
                    'degree': f"{degree_type} {match[1]}{field}".strip(),
                    'institution': 'Not specified',
                    'year': 'Not specified'
                })
        
        # Extract educational institutions
        educational_keywords = ['university', 'college', 'institute', 'school']
        institutions = []
        
        for ent in doc.ents:
            if ent.label_ == "ORG":
                if any(keyword in ent.text.lower() for keyword in educational_keywords):
                    institutions.append(ent.text)
        
        # Match institutions to degrees
        for i, edu in enumerate(education):
            if i < len(institutions):
                edu['institution'] = institutions[i]
        
        return education
    
    def extract_projects(self, text: str) -> List[Dict[str, str]]:
        """Extract project information from resume text."""
        projects = []
        
        # Look for project section and bullet points
        project_section_match = None
        for section, pattern in self.section_patterns.items():
            if section == 'projects':
                project_section_match = re.search(pattern, text, re.IGNORECASE)
                break
        
        if project_section_match:
            # Extract text after projects section
            project_text = text[project_section_match.end():]
            
            # Find bullet points or numbered items
            bullet_patterns = [
                r'[•▪▫‣⁃]\s*(.+?)(?=[•▪▫‣⁃]|\n\n|\Z)',
                r'[\d]+\.\s*(.+?)(?=[\d]+\.|\n\n|\Z)',
                r'^-\s*(.+?)(?=^-|\n\n|\Z)'
            ]
            
            for pattern in bullet_patterns:
                matches = re.findall(pattern, project_text, re.MULTILINE | re.DOTALL)
                for match in matches[:5]:  # Limit to 5 projects
                    if len(match.strip()) > 20:  # Filter out short matches
                        projects.append({
                            'title': 'Project',
                            'description': match.strip()[:200] + ('...' if len(match.strip()) > 200 else '')
                        })
        
        return projects
    
    def parse_resume(self, text: str) -> Dict:
        """Main method to parse resume text and extract all information."""
        logger.info("Starting resume parsing...")
        
        result = {
            'contact_info': self.extract_contact_info(text),
            'skills': self.extract_skills(text),
            'experience': self.extract_experience(text),
            'education': self.extract_education(text),
            'projects': self.extract_projects(text),
            'raw_text_length': len(text),
            'parsing_timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Parsing complete. Found {len(result['experience'])} experiences, {sum(len(v) for v in result['skills'].values())} skills")
        
        return result

# Usage example and testing
if __name__ == "__main__":
    # Test the resume parser
    sample_resume = """
    John Doe
    Software Engineer
    john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe
    
    EXPERIENCE
    Senior Software Engineer at Google (2020-2023)
    • Developed scalable web applications using Python and React
    • Led a team of 5 engineers in building ML-powered features
    • Improved system performance by 40% through optimization
    
    Software Engineer at Microsoft (2018-2020)
    • Built REST APIs using Django and PostgreSQL
    • Implemented CI/CD pipelines with Jenkins and Docker
    
    EDUCATION
    Bachelor of Science in Computer Science
    Stanford University (2014-2018)
    
    SKILLS
    Programming: Python, JavaScript, Java, C++
    Web Development: React, Angular, Node.js, Django
    Databases: PostgreSQL, MongoDB, Redis
    Cloud: AWS, Docker, Kubernetes
    
    PROJECTS
    • E-commerce Platform: Built a full-stack e-commerce application using React and Django
    • ML Recommendation System: Developed a machine learning system for product recommendations
    """
    
    parser = ResumeParser()
    parsed = parser.parse_resume(sample_resume)
    
    print("Parsed Resume Data:")
    for key, value in parsed.items():
        print(f"{key}: {value}")