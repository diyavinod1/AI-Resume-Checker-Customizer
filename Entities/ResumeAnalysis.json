{
  "name": "ResumeAnalysis",
  "type": "object",
  "properties": {
    "candidateName": {
      "type": "string"
    },
    "targetRole": {
      "type": "string"
    },
    "jobDescription": {
      "type": "string"
    },
    "originalResume": {
      "type": "string"
    },
    "meta": {
      "type": "object",
      "properties": {
        "ats_score": {
          "type": "number"
        },
        "coverage": {
          "type": "object",
          "properties": {
            "must_have_keywords": {
              "type": "string"
            },
            "nice_to_have": {
              "type": "string"
            }
          }
        },
        "risks": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "length_ok": {
          "type": "boolean"
        },
        "reading_level": {
          "type": "string"
        }
      }
    },
    "executiveSummary": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "keywordMatrix": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "jdSkill": {
            "type": "string",
            "description": "JD Skill/Keyword"
          },
          "presentInResume": {
            "type": "string",
            "description": "Present in Resume?"
          },
          "evidenceSnippet": {
            "type": "string"
          },
          "action": {
            "type": "string"
          }
        }
      }
    },
    "redFlags": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "flag": {
            "type": "string"
          },
          "details": {
            "type": "string"
          },
          "fix": {
            "type": "string"
          }
        }
      }
    },
    "resumeAtsPlain": {
      "type": "string"
    },
    "resumeMarkdown": {
      "type": "string"
    },
    "bulletUpgrades": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "before": {
            "type": "string"
          },
          "after": {
            "type": "string"
          }
        }
      }
    },
    "coverLetter": {
      "type": "string"
    },
    "linkedinProfile": {
      "type": "object",
      "properties": {
        "headline": {
          "type": "string"
        },
        "about": {
          "type": "string"
        }
      }
    }
  },
  "required": [
    "candidateName",
    "targetRole",
    "jobDescription",
    "originalResume"
  ],
  "x-accessControl": {
    "permissions": {
      "read": "creator",
      "write": "creator"
    }
  }
}
