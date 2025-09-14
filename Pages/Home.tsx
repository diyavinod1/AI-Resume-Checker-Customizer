"use client";

import React, { useState } from 'react';
import { InvokeLLM } from '@/integrations/Core';
import { ResumeAnalysis } from '@/entities/ResumeAnalysis';
import { useToast } from '@/components/ui/use-toast';
import useAppLevelAuth from '@/hooks/useAppLevelAuth';
import ResumeInputForm from '../components/resume/ResumeInputForm';
import AnalysisResults from '../components/resume/AnalysisResults';
import { Bot, FileText, Sparkles } from 'lucide-react';

const outputSchema = {
  type: "object",
  properties: {
    meta: {
      type: "object",
      properties: {
        ats_score: { type: "number" },
        coverage: {
          type: "object",
          properties: {
            must_have_keywords: { type: "string" },
            nice_to_have: { type: "string" }
          }
        },
        risks: { type: "array", items: { type: "string" } },
        length_ok: { type: "boolean" },
        reading_level: { type: "string" }
      }
    },
    executiveSummary: { type: "array", items: { type: "string" } },
    keywordMatrix: {
      type: "array",
      items: {
        type: "object",
        properties: {
          jdSkill: { type: "string" },
          presentInResume: { type: "string" },
          evidenceSnippet: { type: "string" },
          action: { type: "string" }
        }
      }
    },
    redFlags: {
      type: "array",
      items: {
        type: "object",
        properties: {
          flag: { type: "string" },
          details: { type: "string" },
          fix: { type: "string" }
        }
      }
    },
    resumeAtsPlain: { type: "string" },
    resumeMarkdown: { type: "string" },
    bulletUpgrades: {
      type: "array",
      items: {
        type: "object",
        properties: {
          before: { type: "string" },
          after: { type: "string" }
        }
      }
    },
    coverLetter: { type: "string" },
    linkedinProfile: {
      type: "object",
      properties: {
        headline: { type: "string" },
        about: { type: "string" }
      }
    }
  }
};

export default function HomePage() {
  const { isLoggedIn } = useAppLevelAuth();
  const { toast } = useToast();
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleFormSubmit = async (formData: any) => {
    if (!isLoggedIn) {
      toast({ title: "Authentication Required", description: "Please sign in to analyze your resume.", variant: "destructive" });
      return;
    }

    setIsLoading(true);
    setAnalysisResult(null);

    const masterPrompt = `
      # ROLE & MISSION
      You are an ATS specialist, senior resume writer, and career coach. Your mission is to analyze a candidate's resume against a job description, identify gaps, score the ATS match, and customize the resume, cover letter, and LinkedIn profile. Output only the final, clean, copy-ready documents and analyses as specified in the OUTPUT CONTRACT.

      # INPUTS
      - Candidate Name: ${formData.candidateName}
      - Experience Level: ${formData.experienceLevel}
      - Target Role/Title: ${formData.targetRole}
      - Job Description (JD): ${formData.jobDescription}
      - Original Resume: ${formData.originalResume}
      - Optional Keywords: ${formData.extraKeywords || 'N/A'}
      - Tone Preference: ${formData.tonePreference || 'Confident and impactful'}
      - Region/Spelling: ${formData.region || 'US English'}

      # OUTPUT CONTRACT (Follow this order and format precisely)
      Generate a single JSON object that strictly adheres to the provided schema.

      ## WORKFLOW (Internal Steps)
      1.  **Parse JD**: Extract must-have and nice-to-have skills, tools, domains, certifications, and keywords. Normalize synonyms (e.g., "ML" -> "Machine Learning").
      2.  **Score Resume**: Score keyword coverage and calculate the overall ATS score based on keywords (40%), formatting (20%), impact metrics (20%), readability (10%), and risk penalties (10%).
      3.  **Analyze Gaps**: Create the Keyword & Skills Matrix and identify red flags like missing dates, vague bullets, or passive voice.
      4.  **Rewrite Content**: Rewrite the resume using strong action verbs and quantified, metric-rich bullets (use STAR method). Insert placeholders like [approximate value] if numbers are missing. Customize the summary and skills to mirror the JD's language without making false claims.
      5.  **Generate Documents**: Produce the ATS-Plain and Markdown formatted resumes, a custom cover letter, and a LinkedIn profile.
      6.  **Finalize**: Populate all fields in the JSON output schema.
    `;

    try {
      const result = await InvokeLLM({
        prompt: masterPrompt,
        response_json_schema: outputSchema,
      });

      if (result) {
        const savedAnalysis = await ResumeAnalysis.create({
          ...formData,
          ...result,
        });
        setAnalysisResult(savedAnalysis);
        toast({ title: "Analysis Complete", description: "Your resume has been successfully analyzed and customized." });
      } else {
        throw new Error("AI did not return a valid result.");
      }
    } catch (error) {
      console.error("Error during resume analysis:", error);
      toast({ title: "Analysis Failed", description: "An error occurred while analyzing your resume. Please try again.", variant: "destructive" });
    } finally {
      setIsLoading(false);
    }
  };

  if (!isLoggedIn) {
    return (
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12 text-center">
        <h2 className="text-2xl font-bold text-slate-800">Welcome to ResumeMaster Pro</h2>
        <p className="mt-2 text-slate-600">Please sign in to supercharge your resume with AI.</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 sm:p-6 lg:p-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        <div className="lg:col-span-1 lg:sticky lg:top-24">
          <ResumeInputForm onSubmit={handleFormSubmit} isLoading={isLoading} />
        </div>
        <div className="lg:col-span-2">
          {isLoading && (
            <div className="flex flex-col items-center justify-center h-96 bg-white rounded-xl border border-slate-200 shadow-sm">
              <div className="relative flex items-center justify-center">
                <div className="absolute h-24 w-24 bg-blue-100 rounded-full animate-ping"></div>
                <Bot className="h-12 w-12 text-blue-600" />
              </div>
              <p className="mt-6 text-lg font-semibold text-slate-700">Analyzing your documents...</p>
              <p className="text-sm text-slate-500">This may take a moment. Please wait.</p>
            </div>
          )}
          {analysisResult ? (
            <AnalysisResults result={analysisResult} />
          ) : !isLoading && (
            <div className="flex flex-col items-center justify-center h-96 bg-white rounded-xl border-2 border-dashed border-slate-300">
              <div className="p-5 bg-slate-100 rounded-full mb-4">
                <Sparkles className="h-10 w-10 text-slate-500" />
              </div>
              <h3 className="text-xl font-bold text-slate-800">Ready to Start?</h3>
              <p className="text-slate-600 mt-1 max-w-md text-center">
                Fill out the form to get your AI-powered resume analysis and tailored documents.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
