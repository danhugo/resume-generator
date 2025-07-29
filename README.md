# Resume Generator using LangGraph

An intelligent, iterative resume generator powered by LangGraph that tailors resumes to specific job descriptions by combining a candidate’s background with deep job analysis and multi-pass optimization.

## Overview

This project automates and enhances the resume writing process by simulating a **human-in-the-loop recruiter** workflow. It takes:

- An individual's background (experience, education, skills)
- A target job description (JD)

...and produces a **tailored, ATS-friendly resume**, improving it through **iterative evaluation**, **feedback loops**, and **LLM-guided revisions**.

Built with [LangGraph](https://github.com/langchain-ai/langgraph) to support **stateful multi-step reasoning** and modular decision flows.

---

## Features

- ✅ Parses and understands job descriptions using LLM-based keyword extraction
- ✅ Aligns individual profiles with job requirements using a match matrix
- ✅ Generates resume drafts following STAR/PAR methodology
- ✅ Evaluates keyword coverage, ATS-compatibility, and storytelling clarity
- ✅ Supports multiple feedback loops (LLM feedback + optional human)
- ✅ Simulates ATS testing via integration points
- ✅ Outputs optimized resumes in markdown or plain text (can be exported to PDF/doc)

---

## Architecture

```
User Inputs (Profile + JD)
       │
       ▼
[Step 1-3] LangGraph Nodes:
 - Profile Analyzer
 - JD Parser
 - Match Matrix Builder
       │
       ▼
[Step 4] Resume Generator Node (v1)
       │
       ▼
[Step 5] Evaluation Node (Keyword Match, Clarity, ATS-friendliness)
       │
       ├───▶ Feedback Collector Node (optional: LLM or Human-in-the-loop)
       │         │
       ▼         ▼
[Step 7] Resume Revision Node (v2, v3, ...)
       │
       ▼
[Step 8-9] Final Formatter + Export Node
```

---

## Inputs

### Candidate Profile JSON
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "summary": "Experienced software engineer with a focus on backend systems...",
  "work_experience": [
    {
      "title": "Software Engineer",
      "company": "TechCorp",
      "dates": "2021–2024",
      "responsibilities": ["Built microservices in Python", "Led API architecture redesign"]
    }
  ],
  "skills": ["Python", "Docker", "REST APIs", "PostgreSQL"],
  "education": "B.Sc. in Computer Science, ABC University",
  "certifications": ["AWS Certified Developer"]
}
```

### Job Description (Plain text or structured)

---

## Evaluation Logic

The resume is repeatedly assessed using:

- Keyword relevance (80%+ match goal)
- Role fit and skill alignment
- Use of action verbs, STAR structure
- Measurable achievements
- Clarity and ATS parsing performance

Each round refines content based on feedback until optimal quality is reached.

---

## Running Locally

> Coming soon: LangGraph flow launcher + CLI interface

### Requirements
- Python 3.10+
- `langgraph`, `langchain`, `openai`, `joblib`, `python-docx` (optional)

```bash
pip install -r requirements.txt
```

### Sample usage (CLI)
```bash
python run_generator.py --profile profile.json --jd job_description.txt
```

---

## Future Features

- [ ] PDF export with LaTeX or docx templates
- [ ] Plugin for LinkedIn profile extraction
- [ ] Cover letter generator with style matching
- [ ] Resume benchmarking dashboard

---

## Contributing

We welcome pull requests! You can contribute by:
- Adding new resume templates
- Improving evaluation logic
- Optimizing LangGraph workflows

---
