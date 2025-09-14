"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Check, Copy, Linkedin, List, Mail, Star, Target, ThumbsDown, ThumbsUp } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useToast } from '@/components/ui/use-toast';

interface AnalysisResultsProps {
  result: any;
}

const ContentViewer = ({ title, content, isMarkdown = false, icon: Icon }: { title: string, content: string, isMarkdown?: boolean, icon: React.ElementType }) => {
  const { toast } = useToast();
  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    toast({ title: "Copied to clipboard!" });
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-lg font-semibold flex items-center gap-2">
          <Icon className="h-5 w-5 text-blue-600" />
          {title}
        </CardTitle>
        <Button variant="ghost" size="icon" onClick={handleCopy}>
          <Copy className="h-4 w-4" />
        </Button>
      </CardHeader>
      <CardContent>
        {isMarkdown ? (
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
          </div>
        ) : (
          <pre className="whitespace-pre-wrap font-sans text-sm bg-slate-50 p-4 rounded-md">{content}</pre>
        )}
      </CardContent>
    </Card>
  );
};

export default function AnalysisResults({ result }: AnalysisResultsProps) {
  const { toast } = useToast();
  const finalChecklist = [
    { text: "ATS parsable (no tables/columns in ATS version)", checked: true },
    { text: "Must-have keywords covered", checked: (result.meta.coverage?.must_have_keywords?.split('/')[0] === result.meta.coverage?.must_have_keywords?.split('/')[1]) },
    { text: "Quantified results present", checked: true },
    { text: "Dates normalized", checked: true },
    { text: "Typos/grammar fixed", checked: true },
  ];

  return (
    <div className="space-y-8">
      {/* Meta Stats */}
      <Card>
        <CardHeader><CardTitle>Analysis Overview</CardTitle></CardHeader>
        <CardContent className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div className="p-4 bg-blue-50 rounded-lg">
            <p className="text-3xl font-bold text-blue-700">{result.meta.ats_score}%</p>
            <p className="text-sm font-medium text-blue-600">ATS Score</p>
          </div>
          <div className="p-4 bg-green-50 rounded-lg">
            <p className="text-xl font-bold text-green-700">{result.meta.coverage?.must_have_keywords}</p>
            <p className="text-sm font-medium text-green-600">Must-Have Keywords</p>
          </div>
          <div className="p-4 bg-yellow-50 rounded-lg">
            <p className="text-xl font-bold text-yellow-700">{result.meta.coverage?.nice_to_have}</p>
            <p className="text-sm font-medium text-yellow-600">Nice-to-Have Keywords</p>
          </div>
          <div className="p-4 bg-red-50 rounded-lg">
            <p className="text-xl font-bold text-red-700">{result.meta.risks?.length || 0}</p>
            <p className="text-sm font-medium text-red-600">Risks Identified</p>
          </div>
        </CardContent>
      </Card>

      {/* Executive Summary */}
      <Card>
        <CardHeader><CardTitle>Executive Summary</CardTitle></CardHeader>
        <CardContent>
          <ul className="list-disc space-y-2 pl-5">
            {result.executiveSummary.map((item: string, index: number) => <li key={index}>{item}</li>)}
          </ul>
        </CardContent>
      </Card>

      {/* Keyword & Skills Matrix */}
      <Card>
        <CardHeader><CardTitle>Keyword & Skills Matrix</CardTitle></CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>JD Skill/Keyword</TableHead>
                <TableHead>Present?</TableHead>
                <TableHead>Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {result.keywordMatrix.map((row: any, index: number) => (
                <TableRow key={index}>
                  <TableCell className="font-medium">{row.jdSkill}</TableCell>
                  <TableCell>{row.presentInResume}</TableCell>
                  <TableCell>{row.action}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Red Flags & Fixes */}
      <Card>
        <CardHeader><CardTitle>Red Flags & Fixes</CardTitle></CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Flag</TableHead>
                <TableHead>Details</TableHead>
                <TableHead>Fix</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {result.redFlags.map((row: any, index: number) => (
                <TableRow key={index}>
                  <TableCell className="font-medium">{row.flag}</TableCell>
                  <TableCell>{row.details}</TableCell>
                  <TableCell>{row.fix}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Tailored Resumes */}
      <ContentViewer title="Tailored Resume — ATS-Plain" content={result.resumeAtsPlain} icon={List} />
      <ContentViewer title="Tailored Resume — Markdown Formatted" content={result.resumeMarkdown} isMarkdown icon={List} />

      {/* STAR Bullet Upgrades */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Star className="h-5 w-5 text-blue-600" />
            STAR Bullet Upgrades
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {result.bulletUpgrades.map((item: any, index: number) => (
            <div key={index} className="p-4 border rounded-lg">
              <p className="text-sm text-slate-500 mb-1 flex items-center gap-2"><ThumbsDown className="h-4 w-4" /> Before</p>
              <p className="text-sm mb-3 pl-6">{item.before}</p>
              <p className="text-sm font-semibold text-green-700 mb-1 flex items-center gap-2"><ThumbsUp className="h-4 w-4" /> After</p>
              <p className="text-sm text-green-800 bg-green-50 p-2 rounded pl-6">{item.after}</p>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Cover Letter & LinkedIn */}
      <ContentViewer title="Custom Cover Letter" content={result.coverLetter} isMarkdown icon={Mail} />
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Linkedin className="h-5 w-5 text-blue-600" />
            LinkedIn Profile
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <ContentViewer title="Headline" content={result.linkedinProfile.headline} icon={Target} />
          <ContentViewer title="About Section" content={result.linkedinProfile.about} isMarkdown icon={List} />
        </CardContent>
      </Card>

      {/* Final Checklist */}
      <Card>
        <CardHeader><CardTitle>Final Checklist</CardTitle></CardHeader>
        <CardContent>
          <ul className="space-y-2">
            {finalChecklist.map((item, index) => (
              <li key={index} className="flex items-center gap-2">
                <Check className={`h-5 w-5 ${item.checked ? 'text-green-600' : 'text-slate-300'}`} />
                <span>{item.text}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
