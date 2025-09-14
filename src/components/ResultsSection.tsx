import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { CheckCircle, XCircle, AlertTriangle, Download, Copy, Target, TrendingUp, Users, FileText, Lightbulb, CheckSquare, ArrowLeft } from "lucide-react";
import { AnalysisResult } from "@/services/mockApi";
import { useToast } from "@/hooks/use-toast";

interface ResultsSectionProps {
  result: AnalysisResult;
  onBack: () => void;
}

const ResultsSection = ({ result, onBack }: ResultsSectionProps) => {
  const [activeTab, setActiveTab] = useState("overview");
  const { toast } = useToast();

  const copyToClipboard = async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast({
        title: "Copied!",
        description: `${label} copied to clipboard`,
      });
    } catch (error) {
      toast({
        title: "Copy failed",
        description: "Please select and copy the text manually",
        variant: "destructive",
      });
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "High": return "text-destructive";
      case "Medium": return "text-yellow-600";
      case "Low": return "text-muted-foreground";
      default: return "text-muted-foreground";
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "High": return <XCircle className="h-4 w-4" />;
      case "Medium": return <AlertTriangle className="h-4 w-4" />;
      case "Low": return <CheckCircle className="h-4 w-4" />;
      default: return <CheckCircle className="h-4 w-4" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-muted/30 to-background">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={onBack}
            className="mb-4 text-muted-foreground hover:text-foreground"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Upload
          </Button>
          <div className="text-center space-y-2">
            <h1 className="text-3xl sm:text-4xl font-bold text-gradient-primary">
              Resume Analysis Complete
            </h1>
            <p className="text-xl text-muted-foreground">
              Your comprehensive resume optimization report
            </p>
          </div>
        </div>

        {/* Main Content */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-8">
          <TabsList className="grid w-full grid-cols-3 lg:grid-cols-9 h-auto p-1 bg-muted/50">
            <TabsTrigger value="overview" className="text-xs sm:text-sm">Overview</TabsTrigger>
            <TabsTrigger value="skills" className="text-xs sm:text-sm">Skills</TabsTrigger>
            <TabsTrigger value="fixes" className="text-xs sm:text-sm">Fixes</TabsTrigger>
            <TabsTrigger value="resume" className="text-xs sm:text-sm">Resume</TabsTrigger>
            <TabsTrigger value="bullets" className="text-xs sm:text-sm">Bullets</TabsTrigger>
            <TabsTrigger value="cover" className="text-xs sm:text-sm">Cover Letter</TabsTrigger>
            <TabsTrigger value="linkedin" className="text-xs sm:text-sm">LinkedIn</TabsTrigger>
            <TabsTrigger value="checklist" className="text-xs sm:text-sm">Checklist</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card className="card-gradient card-hover">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Target className="h-5 w-5 text-primary" />
                    ATS Score
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="text-3xl font-bold text-primary">{result.meta.atsScore}/100</div>
                    <Progress value={result.meta.atsScore} className="h-2" />
                    <Badge variant="secondary" className="text-xs">
                      {result.meta.overallRating}
                    </Badge>
                  </div>
                </CardContent>
              </Card>

              <Card className="card-gradient card-hover">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-secondary" />
                    Keywords
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="text-3xl font-bold text-secondary">{result.meta.keywordCoverage}%</div>
                    <Progress value={result.meta.keywordCoverage} className="h-2" />
                    <p className="text-xs text-muted-foreground">Coverage Rate</p>
                  </div>
                </CardContent>
              </Card>

              <Card className="card-gradient card-hover">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5 text-yellow-600" />
                    Risk Areas
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="text-3xl font-bold text-yellow-600">{result.meta.risks.length}</div>
                    <p className="text-xs text-muted-foreground">Items to Address</p>
                  </div>
                </CardContent>
              </Card>

              <Card className="card-gradient card-hover">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Users className="h-5 w-5 text-accent" />
                    Potential
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="text-3xl font-bold text-accent">90+</div>
                    <p className="text-xs text-muted-foreground">Target Score</p>
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card className="card-gradient">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-primary" />
                  Executive Summary
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground leading-relaxed">{result.executiveSummary}</p>
              </CardContent>
            </Card>

            <Card className="card-gradient">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-yellow-600" />
                  Quick Risks Overview
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {result.meta.risks.map((risk, index) => (
                    <div key={index} className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg">
                      <AlertTriangle className="h-4 w-4 text-yellow-600 flex-shrink-0" />
                      <span className="text-sm">{risk}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Skills Matrix Tab */}
          <TabsContent value="skills" className="space-y-6">
            <div className="space-y-6">
              {result.skillsMatrix.map((category, index) => (
                <Card key={index} className="card-gradient">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Target className="h-5 w-5 text-primary" />
                      {category.category}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                      {category.skills.map((skill, skillIndex) => (
                        <div
                          key={skillIndex}
                          className={`flex items-center justify-between p-3 rounded-lg border ${
                            skill.present ? "bg-accent/10 border-accent/20" : "bg-muted/50 border-border"
                          }`}
                        >
                          <div className="flex items-center gap-2">
                            {skill.present ? (
                              <CheckCircle className="h-4 w-4 text-accent" />
                            ) : (
                              <XCircle className="h-4 w-4 text-muted-foreground" />
                            )}
                            <span className={skill.present ? "text-foreground" : "text-muted-foreground"}>
                              {skill.name}
                            </span>
                          </div>
                          <Badge
                            variant={skill.importance === "High" ? "default" : "secondary"}
                            className="text-xs"
                          >
                            {skill.importance}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Red Flags & Fixes Tab */}
          <TabsContent value="fixes" className="space-y-6">
            <div className="space-y-4">
              {result.redFlags.map((flag, index) => (
                <Card key={index} className="card-gradient">
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className={getSeverityColor(flag.severity)}>
                          {getSeverityIcon(flag.severity)}
                        </span>
                        <span className="text-lg">{flag.issue}</span>
                      </div>
                      <Badge 
                        variant={flag.severity === "High" ? "destructive" : flag.severity === "Medium" ? "secondary" : "outline"}
                        className="text-xs"
                      >
                        {flag.severity} Priority
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="bg-muted/50 p-4 rounded-lg">
                      <h4 className="font-semibold text-sm mb-2 flex items-center gap-2">
                        <Lightbulb className="h-4 w-4 text-yellow-500" />
                        Recommended Fix
                      </h4>
                      <p className="text-sm text-muted-foreground">{flag.fix}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Tailored Resume Tab */}
          <TabsContent value="resume" className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              <Card className="card-gradient">
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-primary" />
                    ATS-Optimized Version
                  </CardTitle>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => copyToClipboard(result.tailoredResume.atsPlain, "ATS Resume")}
                  >
                    <Copy className="h-4 w-4 mr-2" />
                    Copy
                  </Button>
                </CardHeader>
                <CardContent>
                  <div className="bg-muted/50 p-4 rounded-lg h-96 overflow-y-auto">
                    <pre className="text-xs whitespace-pre-wrap font-mono">
                      {result.tailoredResume.atsPlain}
                    </pre>
                  </div>
                </CardContent>
              </Card>

              <Card className="card-gradient">
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-secondary" />
                    Markdown Version
                  </CardTitle>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => copyToClipboard(result.tailoredResume.markdown, "Markdown Resume")}
                  >
                    <Copy className="h-4 w-4 mr-2" />
                    Copy
                  </Button>
                </CardHeader>
                <CardContent>
                  <div className="bg-muted/50 p-4 rounded-lg h-96 overflow-y-auto">
                    <pre className="text-xs whitespace-pre-wrap font-mono">
                      {result.tailoredResume.markdown}
                    </pre>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Bullet Upgrades Tab */}
          <TabsContent value="bullets" className="space-y-6">
            <div className="space-y-4">
              {result.bulletUpgrades.map((upgrade, index) => (
                <Card key={index} className="card-gradient">
                  <CardContent className="p-6">
                    <div className="space-y-4">
                      <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                        <h4 className="font-semibold text-sm mb-2 text-red-800">❌ Original</h4>
                        <p className="text-sm text-red-700">{upgrade.original}</p>
                      </div>
                      
                      <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                        <h4 className="font-semibold text-sm mb-2 text-green-800">✅ Improved</h4>
                        <p className="text-sm text-green-700">{upgrade.improved}</p>
                      </div>
                      
                      <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                        <h4 className="font-semibold text-sm mb-2 text-blue-800 flex items-center gap-2">
                          <Lightbulb className="h-4 w-4" />
                          Why This Works
                        </h4>
                        <p className="text-sm text-blue-700">{upgrade.impact}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Cover Letter Tab */}
          <TabsContent value="cover" className="space-y-6">
            <Card className="card-gradient">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-primary" />
                  Tailored Cover Letter
                </CardTitle>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => copyToClipboard(result.coverLetter, "Cover Letter")}
                  >
                    <Copy className="h-4 w-4 mr-2" />
                    Copy
                  </Button>
                  <Button variant="outline" size="sm">
                    <Download className="h-4 w-4 mr-2" />
                    Download
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="bg-muted/50 p-6 rounded-lg">
                  <div className="whitespace-pre-wrap text-sm leading-relaxed">
                    {result.coverLetter}
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* LinkedIn Tab */}
          <TabsContent value="linkedin" className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              <Card className="card-gradient">
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Users className="h-5 w-5 text-primary" />
                    LinkedIn Headline
                  </CardTitle>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => copyToClipboard(result.linkedIn.headline, "LinkedIn Headline")}
                  >
                    <Copy className="h-4 w-4 mr-2" />
                    Copy
                  </Button>
                </CardHeader>
                <CardContent>
                  <div className="bg-muted/50 p-4 rounded-lg">
                    <p className="text-sm">{result.linkedIn.headline}</p>
                  </div>
                </CardContent>
              </Card>

              <Card className="card-gradient">
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-secondary" />
                    About Section
                  </CardTitle>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => copyToClipboard(result.linkedIn.about, "LinkedIn About")}
                  >
                    <Copy className="h-4 w-4 mr-2" />
                    Copy
                  </Button>
                </CardHeader>
                <CardContent>
                  <div className="bg-muted/50 p-4 rounded-lg h-64 overflow-y-auto">
                    <div className="whitespace-pre-wrap text-sm">
                      {result.linkedIn.about}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Checklist Tab */}
          <TabsContent value="checklist" className="space-y-6">
            <div className="space-y-6">
              {result.checklist.map((category, index) => (
                <Card key={index} className="card-gradient">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <CheckSquare className="h-5 w-5 text-primary" />
                      {category.category}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {category.items.map((item, itemIndex) => (
                        <div key={itemIndex} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                          <div className="flex items-center gap-3">
                            {item.completed ? (
                              <CheckCircle className="h-5 w-5 text-accent" />
                            ) : (
                              <div className="h-5 w-5 border-2 border-muted-foreground rounded-full" />
                            )}
                            <span className={item.completed ? "line-through text-muted-foreground" : "text-foreground"}>
                              {item.task}
                            </span>
                          </div>
                          <Badge
                            variant={item.priority === "High" ? "destructive" : item.priority === "Medium" ? "secondary" : "outline"}
                            className="text-xs"
                          >
                            {item.priority}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default ResultsSection;
