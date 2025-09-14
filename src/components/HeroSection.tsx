import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Upload, Zap, Target, Award } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import heroImage from "@/assets/hero-image.jpg";

interface HeroSectionProps {
  onAnalyze: (resume: string, jobDescription: string) => void;
}

const HeroSection = ({ onAnalyze }: HeroSectionProps) => {
  const [resume, setResume] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!resume.trim() || !jobDescription.trim()) {
      toast({
        title: "Missing Information",
        description: "Please provide both your resume and the job description.",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    
    // Simulate API delay
    setTimeout(() => {
      onAnalyze(resume, jobDescription);
      setIsLoading(false);
    }, 2000);
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === "text/plain") {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        setResume(content);
      };
      reader.readAsText(file);
    } else {
      toast({
        title: "Invalid File",
        description: "Please upload a text file (.txt) containing your resume.",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="relative min-h-[90vh] flex items-center justify-center bg-gradient-to-br from-background via-muted/30 to-background">
      {/* Background Image */}
      <div className="absolute inset-0 z-0 overflow-hidden">
        <img
          src={heroImage}
          alt="AI Resume Analysis"
          className="w-full h-full object-cover opacity-10"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-background/90 via-background/70 to-background/90" />
      </div>

      <div className="relative z-10 container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Column - Hero Content */}
          <div className="text-center lg:text-left space-y-8">
            <div className="space-y-4">
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold leading-tight">
                <span className="text-gradient-primary">AI-Powered</span>
                <br />
                Resume Optimization
              </h1>
              <p className="text-xl text-muted-foreground max-w-2xl">
                Get instant feedback on your resume with our advanced AI. 
                Increase your ATS score, fix red flags, and land more interviews.
              </p>
            </div>

            {/* Feature Highlights */}
            <div className="flex flex-wrap gap-6 justify-center lg:justify-start">
              <div className="flex items-center gap-2 text-sm font-medium">
                <Target className="h-5 w-5 text-primary" />
                <span>ATS Optimization</span>
              </div>
              <div className="flex items-center gap-2 text-sm font-medium">
                <Zap className="h-5 w-5 text-secondary" />
                <span>Instant Analysis</span>
              </div>
              <div className="flex items-center gap-2 text-sm font-medium">
                <Award className="h-5 w-5 text-accent" />
                <span>Expert Recommendations</span>
              </div>
            </div>
          </div>

          {/* Right Column - Form */}
          <Card className="card-gradient card-hover border-0 shadow-xl">
            <CardContent className="p-8">
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="text-center mb-6">
                  <h2 className="text-2xl font-semibold mb-2">
                    Analyze Your Resume
                  </h2>
                  <p className="text-muted-foreground">
                    Upload or paste your resume and job description
                  </p>
                </div>

                <div className="space-y-4">
                  <div>
                    <Label htmlFor="resume" className="text-base font-medium">
                      Your Resume
                    </Label>
                    <div className="mt-2 space-y-3">
                      <div className="flex items-center justify-center w-full">
                        <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-border rounded-lg cursor-pointer hover:bg-muted/50 transition-colors">
                          <div className="flex flex-col items-center justify-center pt-5 pb-6">
                            <Upload className="w-8 h-8 mb-2 text-muted-foreground" />
                            <p className="mb-2 text-sm text-muted-foreground">
                              <span className="font-semibold">Click to upload</span> or drag and drop
                            </p>
                            <p className="text-xs text-muted-foreground">TXT files only</p>
                          </div>
                          <input
                            type="file"
                            accept=".txt"
                            onChange={handleFileUpload}
                            className="hidden"
                          />
                        </label>
                      </div>
                      <div className="text-center text-sm text-muted-foreground">or</div>
                      <Textarea
                        id="resume"
                        placeholder="Paste your resume content here..."
                        value={resume}
                        onChange={(e) => setResume(e.target.value)}
                        className="min-h-32 resize-none"
                      />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="job-description" className="text-base font-medium">
                      Job Description
                    </Label>
                    <Textarea
                      id="job-description"
                      placeholder="Paste the job description you're applying for..."
                      value={jobDescription}
                      onChange={(e) => setJobDescription(e.target.value)}
                      className="mt-2 min-h-32 resize-none"
                    />
                  </div>
                </div>

                <Button
                  type="submit"
                  disabled={isLoading}
                  className="w-full btn-gradient-primary text-lg h-12"
                >
                  {isLoading ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2" />
                      Analyzing Resume...
                    </>
                  ) : (
                    <>
                      <Zap className="mr-2 h-5 w-5" />
                      Analyze Resume
                    </>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default HeroSection;
