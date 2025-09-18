#!/usr/bin/env python3
"""
AI Resume Checker & Customizer - Demo Script

Demonstrates the complete NLP pipeline:
1. Resume parsing and extraction
2. Job description analysis  
3. ATS compatibility scoring
4. Semantic matching and similarity
5. AI-powered suggestions
6. LinkedIn optimization

Usage:
    python demo.py [resume_file] [job_description_file]
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from nlp.resume_parser import ResumeParser
from nlp.job_matcher import JobMatcher
from nlp.ats_scorer import ATSScorer
from nlp.suggestion_generator import SuggestionGenerator

def load_sample_data():
    """Load sample resume and job description for demonstration."""
    sample_dir = Path(__file__).parent.parent / "sample_data"
    
    # Load sample resume
    resume_file = sample_dir / "resume1.txt"
    if resume_file.exists():
        with open(resume_file, 'r') as f:
            resume_text = f.read()
    else:
        resume_text = """
        John Doe
        Software Engineer
        john.doe@email.com | (555) 123-4567
        
        EXPERIENCE
        Software Engineer at TechCorp (2020-2023)
        • Developed web applications using Python and React
        • Improved system performance by 30%
        
        SKILLS
        Python, JavaScript, React, Node.js, SQL
        """
    
    # Load sample job description
    job_file = sample_dir / "job_description1.txt"
    if job_file.exists():
        with open(job_file, 'r') as f:
            job_text = f.read()
    else:
        job_text = """
        Senior Frontend Developer
        TechCorp Inc.
        
        Requirements:
        • 5+ years of software development experience
        • Strong proficiency in JavaScript, React, and TypeScript
        • Experience with REST APIs and GraphQL
        • Knowledge of responsive design
        """
    
    return resume_text, job_text

def demonstrate_pipeline(resume_text, job_text):
    """Run the complete NLP pipeline demonstration."""
    print("=" * 60)
    print("AI RESUME CHECKER & CUSTOMIZER - DEMO")
    print("=" * 60)
    
    # Initialize components
    print("\n1. Initializing NLP components...")
    try:
        parser = ResumeParser()
        matcher = JobMatcher()
        scorer = ATSScorer()
        generator = SuggestionGenerator()
        print("✓ All components initialized successfully")
    except Exception as e:
        print(f"✗ Error initializing components: {e}")
        return
    
    # Step 1: Parse Resume
    print("\n2. Parsing resume...")
    try:
        parsed_resume = parser.parse_resume(resume_text)
        print("✓ Resume parsed successfully")
        print(f"   Contact: {parsed_resume.get('contact_info', {})}")
        print(f"   Skills found: {sum(len(v) for v in parsed_resume.get('skills', {}).values())} total")
        print(f"   Experience entries: {len(parsed_resume.get('experience', []))}")
        print(f"   Education entries: {len(parsed_resume.get('education', []))}")
    except Exception as e:
        print(f"✗ Error parsing resume: {e}")
        return
    
    # Step 2: Parse Job Description
    print("\n3. Analyzing job description...")
    try:
        parsed_job = matcher.parse_job_description(job_text)
        print("✓ Job description analyzed successfully")
        print(f"   Job title: {parsed_job.get('title')}")
        print(f"   Company: {parsed_job.get('company')}")
        print(f"   Required skills: {sum(len(v) for v in parsed_job.get('required_skills', {}).values())} total")
        print(f"   Experience level: {parsed_job.get('experience_level')}")
    except Exception as e:
        print(f"✗ Error analyzing job description: {e}")
        return
    
    # Step 3: Calculate ATS Score
    print("\n4. Calculating ATS compatibility score...")
    try:
        ats_results = scorer.score_resume(parsed_resume, resume_text, parsed_job)
        print("✓ ATS analysis completed")
        print(f"   Overall ATS Score: {ats_results['overall_score']:.1f}/100")
        print(f"   Rating: {ats_results['ats_friendly_rating']}")
        print("   Score Breakdown:")
        for component, score in ats_results['score_breakdown'].items():
            print(f"     {component.title()}: {score:.1f}/100")
    except Exception as e:
        print(f"✗ Error calculating ATS score: {e}")
        return
    
    # Step 4: Job Matching Analysis
    print("\n5. Performing job matching analysis...")
    try:
        matching_results = matcher.compute_similarity_score(parsed_resume, parsed_job)
        print("✓ Job matching analysis completed")
        print(f"   Overall Match Score: {matching_results['overall_score']:.1f}/100")
        print(f"   Skills Match: {matching_results['skills_match']:.1f}/100")
        print(f"   Experience Match: {matching_results['experience_match']:.1f}/100")
        print(f"   Education Match: {matching_results['education_match']:.1f}/100")
        
        # Show missing skills
        missing_skills = matching_results.get('missing_skills', {})
        if missing_skills:
            print("   Missing Skills:")
            for category, skills in missing_skills.items():
                print(f"     {category.title()}: {', '.join(skills[:3])}{'...' if len(skills) > 3 else ''}")
    except Exception as e:
        print(f"✗ Error in job matching analysis: {e}")
        return
    
    # Step 5: Generate AI Suggestions
    print("\n6. Generating AI-powered suggestions...")
    try:
        # Get experience bullet points for improvement
        experience = parsed_resume.get('experience', [])
        if experience:
            # Get first experience entry's description
            first_exp = experience[0]
            description = first_exp.get('description', [])
            if isinstance(description, str):
                description = [description]
            elif not description:
                description = ["Worked on software development projects"]
            
            improvements = generator.generate_bullet_improvements(description[:3])  # Limit to first 3
            
            if improvements:
                print("✓ Bullet point improvements generated")
                for improvement in improvements:
                    print(f"   Bullet {improvement['bullet_index'] + 1} suggestions:")
                    for suggestion in improvement['suggestions'][:2]:  # Show first 2 suggestions
                        print(f"     {suggestion['type'].title()}: {suggestion['explanation']}")
                        print(f"       Original: {suggestion['original'][:80]}...")
                        print(f"       Improved: {suggestion['improved'][:80]}...")
            else:
                print("   No improvements generated for current bullet points")
        
        # Generate keyword suggestions
        keyword_suggestions = generator.suggest_missing_keywords(parsed_resume, parsed_job)
        if any(keyword_suggestions.values()):
            print("✓ Keyword suggestions generated")
            for priority, keywords in keyword_suggestions.items():
                if keywords:
                    print(f"   {priority.replace('_', ' ').title()}: {len(keywords)} suggestions")
        
    except Exception as e:
        print(f"✗ Error generating suggestions: {e}")
        # Continue with demo even if suggestions fail
    
    # Step 6: LinkedIn Optimization
    print("\n7. Generating LinkedIn optimization suggestions...")
    try:
        linkedin_suggestions = generator.generate_linkedin_suggestions(parsed_resume)
        print("✓ LinkedIn suggestions generated")
        
        if linkedin_suggestions.get('headline_options'):
            print(f"   Headline options: {len(linkedin_suggestions['headline_options'])} generated")
            print(f"     Example: {linkedin_suggestions['headline_options'][0][:60]}...")
        
        if linkedin_suggestions.get('about_summary'):
            print("   About summary: Generated")
            summary_preview = linkedin_suggestions['about_summary'][:100].replace('\n', ' ')
            print(f"     Preview: {summary_preview}...")
        
        if linkedin_suggestions.get('skill_recommendations'):
            skills_count = len(linkedin_suggestions['skill_recommendations'])
            print(f"   Skill recommendations: {skills_count} skills suggested")
            
    except Exception as e:
        print(f"✗ Error generating LinkedIn suggestions: {e}")
    
    # Step 7: Summary
    print("\n8. DEMO SUMMARY")
    print("-" * 40)
    if 'ats_results' in locals() and 'matching_results' in locals():
        print(f"ATS Score: {ats_results['overall_score']:.1f}/100 - {ats_results['ats_friendly_rating']}")
        print(f"Job Match: {matching_results['overall_score']:.1f}/100")
        
        # Recommendations
        print("\nTop Recommendations:")
        if ats_results['overall_score'] < 70:
            print("• Improve ATS compatibility by addressing formatting issues")
        if matching_results['skills_match'] < 70:
            print("• Add missing skills relevant to the job description")
        if matching_results['experience_match'] < 70:
            print("• Emphasize experience that aligns with job requirements")
        
        print("\n✓ Demo completed successfully!")
        print("\nNext steps:")
        print("• Upload your own resume and job description")
        print("• Run the web application: python backend/main.py")
        print("• Open http://localhost:8000 in your browser")
    else:
        print("Demo completed with some errors. Check the output above.")

def main():
    """Main demo function."""
    # Check for command line arguments
    if len(sys.argv) == 3:
        resume_file = sys.argv[1]
        job_file = sys.argv[2]
        
        try:
            with open(resume_file, 'r') as f:
                resume_text = f.read()
            with open(job_file, 'r') as f:
                job_text = f.read()
            print(f"Loaded custom files: {resume_file} and {job_file}")
        except Exception as e:
            print(f"Error loading files: {e}")
            print("Using sample data instead...")
            resume_text, job_text = load_sample_data()
    else:
        resume_text, job_text = load_sample_data()
        print("Using sample data for demonstration")
    
    # Run the demonstration
    demonstrate_pipeline(resume_text, job_text)

if __name__ == "__main__":
    main()