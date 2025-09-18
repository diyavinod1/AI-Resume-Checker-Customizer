"""
AI Suggestion Generator Module

Generates AI-powered suggestions for resume optimization including:
- Bullet point rewrites
- Keyword suggestions  
- Content improvements
- Tone adjustments

Uses both prompt-based approaches and local transformer models.
"""

import re
import random
from typing import Dict, List, Optional, Tuple
from transformers import pipeline, GPT2LMHeadModel, GPT2Tokenizer
import logging

logger = logging.getLogger(__name__)

class SuggestionGenerator:
    def __init__(self):
        """Initialize the suggestion generator with local models and templates."""
        
        # Initialize text generation pipeline
        try:
            self.text_generator = pipeline(
                "text-generation", 
                model="distilgpt2",
                tokenizer="distilgpt2"
            )
            logger.info("Loaded DistilGPT2 model for text generation")
        except Exception as e:
            logger.warning(f"Could not load text generation model: {e}")
            self.text_generator = None
        
        # Action verb categories for bullet point improvements
        self.action_verbs = {
            'leadership': ['led', 'managed', 'directed', 'supervised', 'coordinated', 'oversaw', 'guided', 'mentored'],
            'development': ['developed', 'built', 'created', 'designed', 'implemented', 'engineered', 'programmed', 'coded'],
            'improvement': ['improved', 'optimized', 'enhanced', 'streamlined', 'upgraded', 'modernized', 'refined', 'strengthened'],
            'analysis': ['analyzed', 'evaluated', 'assessed', 'researched', 'investigated', 'examined', 'studied', 'reviewed'],
            'collaboration': ['collaborated', 'partnered', 'worked', 'cooperated', 'liaised', 'coordinated', 'facilitated', 'engaged'],
            'achievement': ['achieved', 'accomplished', 'delivered', 'executed', 'completed', 'attained', 'secured', 'obtained']
        }
        
        # Professional tone templates
        self.tone_templates = {
            'professional': {
                'style': 'formal and business-appropriate',
                'avoid': ['casual', 'slang', 'contractions'],
                'use': ['accomplished', 'demonstrated', 'utilized', 'collaborated']
            },
            'casual': {
                'style': 'friendly and approachable',
                'avoid': ['overly formal', 'jargon'],
                'use': ['worked', 'helped', 'supported', 'contributed']
            }
        }
        
        # Industry-specific keyword suggestions
        self.industry_keywords = {
            'software': ['agile', 'scrum', 'CI/CD', 'microservices', 'API', 'cloud', 'DevOps', 'testing'],
            'data': ['analytics', 'machine learning', 'visualization', 'ETL', 'data mining', 'statistics', 'modeling'],
            'marketing': ['campaign', 'ROI', 'conversion', 'analytics', 'SEO', 'social media', 'brand', 'engagement'],
            'sales': ['revenue', 'targets', 'pipeline', 'CRM', 'prospecting', 'closing', 'relationship building'],
            'finance': ['analysis', 'forecasting', 'budgeting', 'variance', 'reporting', 'compliance', 'audit']
        }
    
    def generate_bullet_improvements(self, bullet_points: List[str], target_role: str = None) -> List[Dict]:
        """Generate improved versions of bullet points."""
        improvements = []
        
        for i, bullet in enumerate(bullet_points):
            if len(bullet.strip()) < 10:
                continue
                
            # Generate multiple improvement suggestions
            suggestions = []
            
            # Method 1: Action verb improvement
            action_improved = self._improve_with_action_verbs(bullet)
            if action_improved != bullet:
                suggestions.append({
                    'type': 'action_verb',
                    'original': bullet,
                    'improved': action_improved,
                    'explanation': 'Strengthened with powerful action verbs'
                })
            
            # Method 2: Quantification suggestion
            quantified = self._add_quantification_suggestion(bullet)
            if quantified:
                suggestions.append({
                    'type': 'quantification',
                    'original': bullet,
                    'improved': quantified,
                    'explanation': 'Added metrics and quantifiable results'
                })
            
            # Method 3: Professional tone adjustment
            tone_improved = self._adjust_tone(bullet, 'professional')
            if tone_improved != bullet:
                suggestions.append({
                    'type': 'tone',
                    'original': bullet,
                    'improved': tone_improved,
                    'explanation': 'Enhanced professional tone and clarity'
                })
            
            # Method 4: AI-generated alternative (if model available)
            if self.text_generator:
                ai_suggestion = self._generate_ai_alternative(bullet)
                if ai_suggestion:
                    suggestions.append({
                        'type': 'ai_rewrite',
                        'original': bullet,
                        'improved': ai_suggestion,
                        'explanation': 'AI-generated professional alternative'
                    })
            
            if suggestions:
                improvements.append({
                    'bullet_index': i,
                    'suggestions': suggestions[:3]  # Limit to top 3 suggestions
                })
        
        return improvements
    
    def suggest_missing_keywords(self, resume_data: Dict, job_data: Dict, industry: str = None) -> Dict:
        """Suggest keywords that should be added to the resume."""
        suggestions = {
            'high_priority': [],
            'medium_priority': [],
            'industry_specific': []
        }
        
        if not job_data:
            return suggestions
        
        # High priority: Job description keywords not in resume
        job_keywords = job_data.get('keywords', [])
        job_skills = job_data.get('required_skills', {})
        resume_text = str(resume_data).lower()
        
        # Check missing job skills
        for category, skill_list in job_skills.items():
            resume_skills = resume_data.get('skills', {}).get(category, [])
            resume_skills_lower = [skill.lower() for skill in resume_skills]
            
            for skill in skill_list:
                if skill.lower() not in resume_skills_lower and skill.lower() not in resume_text:
                    suggestions['high_priority'].append({
                        'keyword': skill,
                        'category': category,
                        'reason': f'Required skill mentioned in job description'
                    })
        
        # Check missing job keywords
        for keyword in job_keywords[:10]:
            if keyword.lower() not in resume_text:
                suggestions['medium_priority'].append({
                    'keyword': keyword,
                    'category': 'general',
                    'reason': 'Important keyword from job description'
                })
        
        # Industry-specific suggestions
        if industry and industry in self.industry_keywords:
            for keyword in self.industry_keywords[industry]:
                if keyword.lower() not in resume_text:
                    suggestions['industry_specific'].append({
                        'keyword': keyword,
                        'category': 'industry',
                        'reason': f'Common {industry} industry term'
                    })
        
        return suggestions
    
    def optimize_section_content(self, section_name: str, content: Dict, target_role: str = None) -> Dict:
        """Optimize specific resume sections with targeted suggestions."""
        optimizations = {'suggestions': [], 'improvements': []}
        
        if section_name == 'experience':
            optimizations = self._optimize_experience_section(content, target_role)
        elif section_name == 'skills':
            optimizations = self._optimize_skills_section(content, target_role)
        elif section_name == 'summary':
            optimizations = self._optimize_summary_section(content, target_role)
        
        return optimizations
    
    def generate_linkedin_suggestions(self, resume_data: Dict, current_headline: str = None, 
                                    current_about: str = None) -> Dict:
        """Generate LinkedIn-specific optimization suggestions."""
        suggestions = {
            'headline_options': [],
            'about_summary': None,
            'skill_recommendations': [],
            'experience_highlights': []
        }
        
        # Generate headline options
        name = resume_data.get('contact_info', {}).get('name', 'Professional')
        experience = resume_data.get('experience', [])
        skills = resume_data.get('skills', {})
        
        if experience:
            latest_role = experience[0].get('position', 'Professional')
            latest_company = experience[0].get('company', '')
            
            headline_templates = [
                f"{latest_role} | Specialized in {self._get_top_skills(skills, 2)}",
                f"{latest_role} at {latest_company} | {self._get_top_skills(skills, 3)} Expert",
                f"Experienced {latest_role} | Driving Results Through {self._get_top_skills(skills, 2)}",
                f"{latest_role} | Passionate About {self._get_top_skills(skills, 2)} & Innovation"
            ]
            
            suggestions['headline_options'] = headline_templates[:3]
        
        # Generate About section
        if experience and skills:
            about_summary = self._generate_linkedin_about(resume_data)
            suggestions['about_summary'] = about_summary
        
        # Skill recommendations for LinkedIn
        all_skills = []
        for category, skill_list in skills.items():
            all_skills.extend(skill_list)
        
        suggestions['skill_recommendations'] = all_skills[:15]  # Top 15 skills
        
        # Experience highlights for LinkedIn
        for exp in experience[:3]:  # Top 3 experiences
            position = exp.get('position', '')
            company = exp.get('company', '')
            if position and company:
                suggestions['experience_highlights'].append({
                    'role': f"{position} at {company}",
                    'suggestion': f"Highlight key achievements and quantifiable results from your {position} role"
                })
        
        return suggestions
    
    def _improve_with_action_verbs(self, bullet_point: str) -> str:
        """Improve bullet point by replacing weak verbs with strong action verbs."""
        bullet = bullet_point.strip()
        
        # Weak verbs to replace
        weak_verbs = {
            'worked on': 'developed',
            'was responsible for': 'managed',
            'helped with': 'contributed to',
            'did': 'executed',
            'made': 'created',
            'used': 'utilized',
            'worked with': 'collaborated with',
            'was part of': 'participated in'
        }
        
        bullet_lower = bullet.lower()
        for weak, strong in weak_verbs.items():
            if weak in bullet_lower:
                # Replace first occurrence, maintaining original case
                pattern = re.compile(re.escape(weak), re.IGNORECASE)
                bullet = pattern.sub(strong, bullet, count=1)
                break
        
        # Ensure bullet starts with action verb
        if not self._starts_with_action_verb(bullet):
            # Try to add an appropriate action verb
            if 'project' in bullet.lower():
                bullet = f"Led {bullet.lower()}"
            elif any(word in bullet.lower() for word in ['system', 'application', 'software']):
                bullet = f"Developed {bullet.lower()}"
            elif any(word in bullet.lower() for word in ['team', 'group', 'people']):
                bullet = f"Managed {bullet.lower()}"
            else:
                bullet = f"Achieved {bullet.lower()}"
        
        return bullet.capitalize()
    
    def _add_quantification_suggestion(self, bullet_point: str) -> Optional[str]:
        """Suggest quantified version of bullet point if metrics are missing."""
        if any(char.isdigit() for char in bullet_point):
            return None  # Already has numbers
        
        # Templates for adding quantification
        quantification_templates = [
            "by X%", "of X+", "worth $X", "for X users", "across X teams", 
            "within X months", "saving X hours", "reducing X%"
        ]
        
        bullet = bullet_point.strip()
        
        # Add contextual quantification suggestions
        if 'improved' in bullet.lower() or 'increased' in bullet.lower():
            return f"{bullet} by [X]%"
        elif 'reduced' in bullet.lower() or 'decreased' in bullet.lower():
            return f"{bullet} by [X]%"
        elif 'managed' in bullet.lower() or 'led' in bullet.lower():
            return f"{bullet} of [X] team members"
        elif 'developed' in bullet.lower() or 'built' in bullet.lower():
            return f"{bullet} for [X]+ users"
        elif 'completed' in bullet.lower():
            return f"{bullet} within [X] timeline"
        else:
            return f"{bullet} resulting in [quantifiable outcome]"
    
    def _adjust_tone(self, text: str, target_tone: str) -> str:
        """Adjust text tone to match target style."""
        if target_tone not in self.tone_templates:
            return text
        
        tone_config = self.tone_templates[target_tone]
        adjusted_text = text
        
        # Replace casual language with professional alternatives
        if target_tone == 'professional':
            replacements = {
                'worked on': 'developed',
                'helped': 'assisted',
                'did': 'executed',
                'got': 'achieved',
                'made': 'created',
                'used': 'utilized'
            }
            
            for casual, professional in replacements.items():
                adjusted_text = re.sub(r'\b' + casual + r'\b', professional, adjusted_text, flags=re.IGNORECASE)
        
        return adjusted_text
    
    def _generate_ai_alternative(self, bullet_point: str) -> Optional[str]:
        """Generate AI alternative using local transformer model."""
        if not self.text_generator:
            return None
        
        try:
            # Create prompt for professional bullet point rewrite
            prompt = f"Rewrite this resume bullet point professionally: {bullet_point}\nProfessional version:"
            
            # Generate text
            result = self.text_generator(
                prompt, 
                max_length=len(prompt.split()) + 20,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=50256
            )
            
            generated_text = result[0]['generated_text']
            
            # Extract the generated part after "Professional version:"
            if "Professional version:" in generated_text:
                alternative = generated_text.split("Professional version:")[-1].strip()
                
                # Clean and validate the alternative
                if len(alternative) > 10 and len(alternative) < 200:
                    return alternative
            
        except Exception as e:
            logger.warning(f"AI text generation failed: {e}")
        
        return None
    
    def _optimize_experience_section(self, experience_data: List[Dict], target_role: str = None) -> Dict:
        """Optimize experience section with role-specific suggestions."""
        suggestions = []
        improvements = []
        
        for exp in experience_data:
            position = exp.get('position', '')
            description = exp.get('description', [])
            
            if isinstance(description, str):
                description = [description]
            
            # Suggest adding quantifiable achievements
            if not any(char.isdigit() for desc in description for char in desc):
                suggestions.append(f"Add quantifiable results for {position} role (metrics, percentages, dollar amounts)")
            
            # Check for action verbs
            weak_starts = sum(1 for desc in description if not self._starts_with_action_verb(desc))
            if weak_starts > 0:
                suggestions.append(f"Start {weak_starts} bullet points with strong action verbs")
            
            # Suggest relevance to target role
            if target_role and position.lower() != target_role.lower():
                suggestions.append(f"Emphasize transferable skills from {position} relevant to {target_role}")
        
        return {'suggestions': suggestions, 'improvements': improvements}
    
    def _optimize_skills_section(self, skills_data: Dict, target_role: str = None) -> Dict:
        """Optimize skills section organization and content."""
        suggestions = []
        improvements = []
        
        total_skills = sum(len(skill_list) for skill_list in skills_data.values())
        
        if total_skills < 8:
            suggestions.append("Add more relevant technical and soft skills (aim for 8-12 total)")
        elif total_skills > 20:
            suggestions.append("Consider condensing to most relevant skills (10-15 recommended)")
        
        # Check for balanced skill categories
        if len(skills_data) < 3:
            suggestions.append("Organize skills into categories (Technical, Tools, Soft Skills)")
        
        # Suggest industry-specific skills
        if target_role:
            role_lower = target_role.lower()
            if 'software' in role_lower or 'developer' in role_lower:
                suggestions.append("Consider adding: version control, testing frameworks, deployment tools")
            elif 'data' in role_lower or 'analyst' in role_lower:
                suggestions.append("Consider adding: data visualization tools, statistical analysis, SQL")
        
        return {'suggestions': suggestions, 'improvements': improvements}
    
    def _optimize_summary_section(self, summary_content: str, target_role: str = None) -> Dict:
        """Optimize professional summary or objective."""
        suggestions = []
        improvements = []
        
        if not summary_content or len(summary_content.strip()) < 50:
            suggestions.append("Add a compelling professional summary (2-3 sentences)")
            
            # Generate sample summary
            if target_role:
                sample = f"Experienced {target_role} with expertise in [key skills]. Proven track record of [key achievements]. Passionate about [industry/technology focus]."
                improvements.append(f"Sample summary: {sample}")
        
        return {'suggestions': suggestions, 'improvements': improvements}
    
    def _starts_with_action_verb(self, text: str) -> bool:
        """Check if text starts with a strong action verb."""
        text = text.strip().lower()
        if not text:
            return False
        
        # Get all action verbs
        all_action_verbs = []
        for verb_list in self.action_verbs.values():
            all_action_verbs.extend(verb_list)
        
        first_word = text.split()[0] if text.split() else ""
        return first_word in all_action_verbs
    
    def _get_top_skills(self, skills_dict: Dict, count: int) -> str:
        """Get top skills as comma-separated string."""
        all_skills = []
        for category, skill_list in skills_dict.items():
            all_skills.extend(skill_list)
        
        top_skills = all_skills[:count]
        return ", ".join(top_skills)
    
    def _generate_linkedin_about(self, resume_data: Dict) -> str:
        """Generate LinkedIn About section based on resume data."""
        experience = resume_data.get('experience', [])
        skills = resume_data.get('skills', {})
        
        if not experience:
            return None
        
        # Build About section
        latest_role = experience[0].get('position', 'Professional')
        top_skills = self._get_top_skills(skills, 3)
        
        about_template = f"""Experienced {latest_role} with expertise in {top_skills}.

I specialize in delivering high-quality results through strategic thinking and technical excellence. My background includes working with diverse teams to achieve measurable outcomes and drive business growth.

Key strengths:
• {top_skills.split(', ')[0] if top_skills else 'Technical expertise'}
• Problem-solving and analytical thinking  
• Cross-functional collaboration
• Continuous learning and adaptation

I'm passionate about leveraging technology to solve complex challenges and create meaningful impact. Always open to connecting with like-minded professionals and exploring new opportunities."""
        
        return about_template

# Example usage and testing
if __name__ == "__main__":
    # Test suggestion generator
    generator = SuggestionGenerator()
    
    # Test bullet point improvements
    sample_bullets = [
        "Worked on software development projects",
        "Was responsible for managing the team",
        "Helped improve system performance",
        "Used Python to build applications"
    ]
    
    improvements = generator.generate_bullet_improvements(sample_bullets, "Software Engineer")
    
    print("Bullet Point Improvements:")
    for improvement in improvements:
        print(f"\nBullet {improvement['bullet_index'] + 1}:")
        for suggestion in improvement['suggestions']:
            print(f"  Original: {suggestion['original']}")
            print(f"  Improved: {suggestion['improved']}")
            print(f"  Reason: {suggestion['explanation']}\n")