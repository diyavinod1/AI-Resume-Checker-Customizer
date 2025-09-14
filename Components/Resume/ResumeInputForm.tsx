"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2, Wand2 } from 'lucide-react';

interface ResumeInputFormProps {
  onSubmit: (data: any) => void;
  isLoading: boolean;
}

export default function ResumeInputForm({ onSubmit, isLoading }: ResumeInputFormProps) {
  const [formData, setFormData] = useState({
    candidateName: '',
    experienceLevel: '',
    targetRole: '',
    jobDescription: '',
    originalResume: '',
    extraKeywords: '',
    tonePreference: 'Confident, concise, impactful',
    region: 'US English',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { id, value } = e.target;
    setFormData(prev => ({ ...prev, [id]: value }));
  };

  const handleSelectChange = (id: string, value: string) => {
    setFormData(prev => ({ ...prev, [id]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <Card className="shadow-lg border-slate-200">
      <CardHeader>
        <CardTitle className="text-2xl font-bold text-slate-800">Resume Details</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="candidateName">Candidate Name</Label>
            <Input id="candidateName" value={formData.candidateName} onChange={handleChange} required />
          </div>
          <div className="space-y-2">
            <Label htmlFor="experienceLevel">Experience Level</Label>
            <Input id="experienceLevel" placeholder="e.g., Fresher or 5 years" value={formData.experienceLevel} onChange={handleChange} required />
          </div>
          <div className="space-y-2">
            <Label htmlFor="targetRole">Target Role / Title</Label>
            <Input id="targetRole" value={formData.targetRole} onChange={handleChange} required />
          </div>
          <div className="space-y-2">
            <Label htmlFor="jobDescription">Job Description (JD)</Label>
            <Textarea id="jobDescription" value={formData.jobDescription} onChange={handleChange} required rows={6} placeholder="Paste the full job description here..." />
          </div>
          <div className="space-y-2">
            <Label htmlFor="originalResume">Original Resume</Label>
            <Textarea id="originalResume" value={formData.originalResume} onChange={handleChange} required rows={8} placeholder="Paste your resume content here (plain text)..." />
          </div>
          <div className="space-y-2">
            <Label htmlFor="extraKeywords">Optional Keywords</Label>
            <Input id="extraKeywords" value={formData.extraKeywords} onChange={handleChange} placeholder="e.g., data science, agile, scrum" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="tonePreference">Tone</Label>
              <Select value={formData.tonePreference} onValueChange={(value) => handleSelectChange('tonePreference', value)}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="Confident, concise, impactful">Impactful</SelectItem>
                  <SelectItem value="Professional and formal">Formal</SelectItem>
                  <SelectItem value="Creative and engaging">Creative</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="region">Region</Label>
              <Select value={formData.region} onValueChange={(value) => handleSelectChange('region', value)}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="US English">US English</SelectItem>
                  <SelectItem value="UK English">UK English</SelectItem>
                  <SelectItem value="IN English">IN English</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <Button type="submit" disabled={isLoading} className="w-full text-lg py-6">
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Wand2 className="mr-2 h-5 w-5" />
                Analyze & Customize
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
