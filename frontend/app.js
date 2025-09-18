// AI Resume Checker & Customizer - Frontend JavaScript

// Global state
let currentResumeData = null;
let currentAnalysisData = null;
let currentOptimizationData = null;

// API base URL - adjust for your deployment
const API_BASE_URL = 'http://localhost:8000';

// Navigation functions
function showPanel(panelId, navElement) {
    // Hide all panels
    const panels = document.querySelectorAll('.content-panel');
    panels.forEach(panel => panel.classList.remove('active'));
    
    // Show selected panel
    document.getElementById(panelId).classList.add('active');
    
    // Update navigation
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => link.classList.remove('active'));
    navElement.classList.add('active');
    
    // Close mobile menu if open
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.remove('mobile-open');
}

function toggleMobileMenu() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('mobile-open');
}

// File upload and handling
function handleFileSelect(input) {
    const file = input.files[0];
    if (file) {
        const fileUpload = document.getElementById('fileUpload');
        fileUpload.innerHTML = `
            <div class="file-upload-icon">
                <i class="fas fa-file-check"></i>
            </div>
            <p><strong>${file.name}</strong> selected</p>
            <p>File size: ${(file.size / 1024 / 1024).toFixed(2)} MB</p>
        `;
        fileUpload.style.borderColor = '#48bb78';
        fileUpload.style.backgroundColor = 'rgba(72, 187, 120, 0.05)';
    }
}

// Drag and drop functionality
document.addEventListener('DOMContentLoaded', function() {
    const fileUpload = document.getElementById('fileUpload');
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        fileUpload.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });
    
    // Highlight drop area
    ['dragenter', 'dragover'].forEach(eventName => {
        fileUpload.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        fileUpload.addEventListener(eventName, unhighlight, false);
    });
    
    // Handle dropped files
    fileUpload.addEventListener('drop', handleDrop, false);
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function highlight(e) {
        fileUpload.classList.add('dragover');
    }
    
    function unhighlight(e) {
        fileUpload.classList.remove('dragover');
    }
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            document.getElementById('resumeFile').files = files;
            handleFileSelect({ files: files });
        }
    }
});

// Main analysis function
async function analyzeResume() {
    const fileInput = document.getElementById('resumeFile');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a resume file first.');
        return;
    }
    
    // Show loading state
    const analyzeBtn = document.getElementById('analyzeBtn');
    const originalText = analyzeBtn.innerHTML;
    analyzeBtn.innerHTML = '<div class="spinner"></div> Processing...';
    analyzeBtn.disabled = true;
    
    try {
        // Prepare form data
        const formData = new FormData();
        formData.append('file', file);
        formData.append('full_name', document.getElementById('fullName').value);
        formData.append('target_role', document.getElementById('targetRole').value);
        formData.append('experience_level', document.getElementById('experienceLevel').value);
        formData.append('tone_preference', document.getElementById('tonePreference').value);
        formData.append('region', document.getElementById('region').value);
        formData.append('additional_keywords', document.getElementById('additionalKeywords').value);
        
        // Upload and parse resume
        const uploadResponse = await fetch(`${API_BASE_URL}/api/upload-resume`, {
            method: 'POST',
            body: formData
        });
        
        if (!uploadResponse.ok) {
            throw new Error(`Upload failed: ${uploadResponse.statusText}`);
        }
        
        const uploadData = await uploadResponse.json();
        currentResumeData = uploadData;
        
        // Analyze resume
        const analysisResponse = await fetch(`${API_BASE_URL}/api/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                resume_data: uploadData,
                job_description: null // Could add job description input later
            })
        });
        
        if (!analysisResponse.ok) {
            throw new Error(`Analysis failed: ${analysisResponse.statusText}`);
        }
        
        const analysisData = await analysisResponse.json();
        currentAnalysisData = analysisData;
        
        // Display results
        displayAnalysisResults(analysisData);
        
        // Switch to analysis results panel
        showPanel('analysis-result', document.querySelector('[href="#analysis-result"]'));
        
        // Generate optimized version
        await generateOptimizedResume();
        
    } catch (error) {
        console.error('Error analyzing resume:', error);
        alert(`Error analyzing resume: ${error.message}`);
    } finally {
        // Reset button
        analyzeBtn.innerHTML = originalText;
        analyzeBtn.disabled = false;
    }
}

function displayAnalysisResults(data) {
    // Display ATS Score
    const atsScore = data.ats_score.overall_score;
    const scoreDisplay = document.getElementById('atsScoreDisplay');
    const ratingText = document.getElementById('atsRating');
    
    scoreDisplay.textContent = Math.round(atsScore);
    ratingText.textContent = data.ats_score.ats_friendly_rating;
    
    // Set score color based on value
    scoreDisplay.className = 'score-display';
    if (atsScore >= 85) {
        scoreDisplay.classList.add('score-excellent');
    } else if (atsScore >= 70) {
        scoreDisplay.classList.add('score-good');
    } else if (atsScore >= 55) {
        scoreDisplay.classList.add('score-fair');
    } else {
        scoreDisplay.classList.add('score-poor');
    }
    
    // Display score breakdown
    const breakdown = data.ats_score.score_breakdown;
    updateProgressBar('keywordsProgress', 'keywordsScore', breakdown.keywords);
    updateProgressBar('formattingProgress', 'formattingScore', breakdown.formatting);
    updateProgressBar('structureProgress', 'structureScore', breakdown.structure);
    updateProgressBar('contentProgress', 'contentScore', breakdown.content_quality);
    
    document.getElementById('scoreBreakdown').style.display = 'block';
    
    // Display extracted fields
    displayExtractedFields(data.extracted_fields);
    
    // Display missing keywords
    displayMissingKeywords(data.keyword_suggestions);
}

function updateProgressBar(progressId, scoreId, value) {
    document.getElementById(progressId).style.width = `${value}%`;
    document.getElementById(scoreId).textContent = `${Math.round(value)}%`;
}

function displayExtractedFields(fields) {
    const container = document.getElementById('extracted-fields');
    
    // Skills
    if (fields.skills && Object.keys(fields.skills).length > 0) {
        let skillsHtml = '<h4>Skills:</h4>';
        for (const [category, skills] of Object.entries(fields.skills)) {
            skillsHtml += `<p><strong>${category.charAt(0).toUpperCase() + category.slice(1)}:</strong> ${skills.join(', ')}</p>`;
        }
        document.getElementById('extractedSkills').innerHTML = skillsHtml;
    }
    
    // Experience
    if (fields.experience && fields.experience.length > 0) {
        let expHtml = '<h4>Experience:</h4>';
        fields.experience.forEach(exp => {
            expHtml += `
                <div class="suggestion-item">
                    <strong>${exp.position || 'Position'} at ${exp.company || 'Company'}</strong>
                    <p>${exp.duration || 'Duration not specified'}</p>
                </div>
            `;
        });
        document.getElementById('extractedExperience').innerHTML = expHtml;
    }
    
    // Education
    if (fields.education && fields.education.length > 0) {
        let eduHtml = '<h4>Education:</h4>';
        fields.education.forEach(edu => {
            eduHtml += `<p>${edu.degree || 'Degree'} - ${edu.institution || 'Institution'}</p>`;
        });
        document.getElementById('extractedEducation').innerHTML = eduHtml;
    }
    
    container.style.display = 'block';
}

function displayMissingKeywords(suggestions) {
    const container = document.getElementById('missing-keywords');
    let html = '';
    
    if (suggestions.high_priority && suggestions.high_priority.length > 0) {
        html += '<h4>High Priority Missing Skills:</h4>';
        suggestions.high_priority.forEach(item => {
            html += `<div class="suggestion-item improvement-item">${item.keyword} - ${item.reason}</div>`;
        });
    }
    
    if (suggestions.medium_priority && suggestions.medium_priority.length > 0) {
        html += '<h4>Recommended Keywords:</h4>';
        suggestions.medium_priority.slice(0, 5).forEach(item => {
            html += `<div class="suggestion-item">${item.keyword} - ${item.reason}</div>`;
        });
    }
    
    if (html) {
        document.getElementById('missingKeywordsList').innerHTML = html;
        container.style.display = 'block';
    }
}

async function generateOptimizedResume() {
    if (!currentResumeData) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/optimize`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                resume_data: currentResumeData,
                optimization_request: {
                    tone: 'professional',
                    region: 'US',
                    target_role: document.getElementById('targetRole').value
                }
            })
        });
        
        if (!response.ok) {
            throw new Error(`Optimization failed: ${response.statusText}`);
        }
        
        const optimizationData = await response.json();
        currentOptimizationData = optimizationData;
        
        // Display bullet point improvements
        if (optimizationData.bullet_improvements && optimizationData.bullet_improvements.length > 0) {
            displayBulletImprovements(optimizationData.bullet_improvements);
        }
        
        // Generate resume preview
        await generateResumePreview();
        
    } catch (error) {
        console.error('Error generating optimized resume:', error);
    }
}

function displayBulletImprovements(improvements) {
    const container = document.getElementById('bullet-suggestions');
    let html = '';
    
    improvements.forEach((improvement, index) => {
        if (improvement.suggestions && improvement.suggestions.length > 0) {
            improvement.suggestions.forEach(suggestion => {
                html += `
                    <div class="suggestion-item improvement-item">
                        <h5>${suggestion.type.replace('_', ' ').toUpperCase()}</h5>
                        <p><strong>Original:</strong> ${suggestion.original}</p>
                        <p><strong>Improved:</strong> ${suggestion.improved}</p>
                        <p><small>${suggestion.explanation}</small></p>
                    </div>
                `;
            });
        }
    });
    
    if (html) {
        document.getElementById('bulletSuggestionsList').innerHTML = html;
        container.style.display = 'block';
    }
}

async function generateResumePreview() {
    if (!currentResumeData) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/generate-resume`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                resume_data: currentResumeData,
                format_type: 'text'
            })
        });
        
        if (!response.ok) {
            throw new Error(`Resume generation failed: ${response.statusText}`);
        }
        
        const data = await response.json();
        document.getElementById('resumePreviewContent').textContent = data.preview_text;
        
    } catch (error) {
        console.error('Error generating resume preview:', error);
    }
}

// LinkedIn optimization
async function optimizeLinkedIn() {
    if (!currentResumeData) {
        alert('Please upload and analyze a resume first.');
        return;
    }
    
    const btn = document.getElementById('optimizeLinkedInBtn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<div class="spinner"></div> Generating...';
    btn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/linkedin-optimize`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                resume_data: currentResumeData,
                linkedin_request: {
                    linkedin_url: document.getElementById('linkedinUrl').value,
                    current_headline: null,
                    current_about: null
                }
            })
        });
        
        if (!response.ok) {
            throw new Error(`LinkedIn optimization failed: ${response.statusText}`);
        }
        
        const data = await response.json();
        displayLinkedInSuggestions(data);
        
    } catch (error) {
        console.error('Error optimizing LinkedIn:', error);
        alert(`Error optimizing LinkedIn: ${error.message}`);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

function displayLinkedInSuggestions(data) {
    // Headlines
    if (data.headline_options && data.headline_options.length > 0) {
        let html = '';
        data.headline_options.forEach((headline, index) => {
            html += `
                <div class="suggestion-item">
                    <strong>Option ${index + 1}:</strong> ${headline}
                </div>
            `;
        });
        document.getElementById('headlineOptions').innerHTML = html;
    }
    
    // About summary
    if (data.about_summary) {
        document.getElementById('aboutSummary').innerHTML = `
            <div class="suggestion-item">
                <pre style="white-space: pre-wrap; font-family: inherit;">${data.about_summary}</pre>
            </div>
        `;
    }
    
    // Skill suggestions
    if (data.skill_recommendations && data.skill_recommendations.length > 0) {
        const skills = data.skill_recommendations.slice(0, 10).join(', ');
        document.getElementById('skillSuggestions').innerHTML = `
            <div class="suggestion-item">
                ${skills}
            </div>
        `;
    }
    
    // Experience highlights
    if (data.experience_highlights && data.experience_highlights.length > 0) {
        let html = '';
        data.experience_highlights.forEach(highlight => {
            html += `
                <div class="suggestion-item">
                    <strong>${highlight.role}:</strong> ${highlight.suggestion}
                </div>
            `;
        });
        document.getElementById('experienceHighlights').innerHTML = html;
    }
    
    document.getElementById('linkedin-suggestions').style.display = 'block';
}

// Toggle functions for resume output
function toggleResumeView(view, element) {
    const buttons = element.parentElement.querySelectorAll('.toggle-btn');
    buttons.forEach(btn => btn.classList.remove('active'));
    element.classList.add('active');
    
    // TODO: Switch between original and optimized view
    console.log('Toggled to', view, 'view');
}

function setTone(tone, element) {
    const buttons = element.parentElement.querySelectorAll('.toggle-btn');
    buttons.forEach(btn => btn.classList.remove('active'));
    element.classList.add('active');
    
    // TODO: Apply tone changes
    console.log('Set tone to', tone);
}

function setRegion(region, element) {
    const buttons = element.parentElement.querySelectorAll('.toggle-btn');
    buttons.forEach(btn => btn.classList.remove('active'));
    element.classList.add('active');
    
    // TODO: Apply region formatting
    console.log('Set region to', region);
}

// Download functions
async function downloadResume(format) {
    if (!currentResumeData) {
        alert('Please upload and analyze a resume first.');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/generate-resume`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                resume_data: currentResumeData,
                format_type: format
            })
        });
        
        if (!response.ok) {
            throw new Error(`Resume generation failed: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // For now, just show the download URL
        // In a full implementation, you'd trigger an actual download
        alert(`Resume ready for download: ${data.download_url}`);
        
    } catch (error) {
        console.error('Error downloading resume:', error);
        alert(`Error downloading resume: ${error.message}`);
    }
}