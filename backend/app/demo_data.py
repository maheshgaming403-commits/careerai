"""Realistic sample responses used when DEMO_MODE=true or Gemini is unavailable."""

DEMO_RESUME_ANALYSIS = {
    "overallScore": 78,
    "summary": "Solid foundation with good project experience. Strengthen quantified impact and add certifications.",
    "strengths": [
        "Strong core programming skills (Python, JavaScript)",
        "Hands-on projects with real-world relevance",
        "Clear educational background in Computer Science",
    ],
    "weaknesses": [
        "Limited quantified achievements in projects",
        "No cloud or DevOps experience listed",
        "Missing certifications",
    ],
    "recommendedRoles": ["Full-Stack Developer", "Backend Engineer", "Data Analyst"],
    "skillGaps": ["System Design", "Docker & Kubernetes", "AWS fundamentals"],
}

DEMO_SKILLS_ANALYSIS = {
    "technicalSkills": [
        {"name": "Python", "level": 4},
        {"name": "JavaScript", "level": 3},
        {"name": "SQL", "level": 3},
        {"name": "React", "level": 3},
        {"name": "Git", "level": 4},
    ],
    "softSkills": ["Problem solving", "Team collaboration", "Communication"],
    "topGaps": ["Cloud (AWS)", "Docker", "System Design"],
}

DEMO_JOB_MATCH = {
    "matches": [
        {"title": "Full-Stack Developer", "score": 82,
         "missingSkills": ["Docker", "Redis"],
         "advice": "Add containerization to one of your projects."},
        {"title": "Backend Engineer", "score": 76,
         "missingSkills": ["Message queues", "PostgreSQL tuning"],
         "advice": "Deepen database knowledge with an indexing project."},
        {"title": "Data Analyst", "score": 64,
         "missingSkills": ["Power BI", "Statistics"],
         "advice": "Learn pandas + visualization with a Kaggle dataset."},
    ]
}

DEMO_ROADMAP = {
    "targetRole": "Full-Stack Developer",
    "steps": [
        {"phase": "Months 1-2", "title": "Strengthen Foundations",
         "items": ["Master React hooks & state management", "Learn REST API design", "Practice SQL joins & indexing"]},
        {"phase": "Months 3-4", "title": "Backend & DevOps",
         "items": ["Build a FastAPI + Postgres project", "Containerize it with Docker", "Deploy to a cloud platform"]},
        {"phase": "Months 5-6", "title": "Interview Readiness",
         "items": ["Solve 100 DSA problems", "Do 10 mock interviews", "Build a portfolio with 3 solid projects"]},
    ],
}

DEMO_PROJECTS = {
    "recommendations": [
        {"title": "Real-Time Chat App", "difficulty": "Intermediate",
         "skills": ["WebSockets", "React", "Node.js"],
         "description": "Build a chat app with rooms, typing indicators, and message persistence."},
        {"title": "Dockerized Microservice", "difficulty": "Intermediate",
         "skills": ["Docker", "FastAPI", "PostgreSQL"],
         "description": "Convert a monolith API into a containerized service with docker-compose."},
        {"title": "AWS Serverless URL Shortener", "difficulty": "Advanced",
         "skills": ["AWS Lambda", "API Gateway", "DynamoDB"],
         "description": "Deploy a serverless backend and learn cloud fundamentals hands-on."},
    ]
}

DEMO_INTERVIEW = {
    "questions": [
        "Explain the difference between a list and a tuple in Python. When would you use each?",
        "How does React's virtual DOM improve performance?",
        "A query fetching 100k rows is slow. How would you debug and fix it?",
        "Explain how JWT authentication works and its main security pitfalls.",
        "Design a URL shortener. Walk me through your approach.",
    ],
    "sampleEvaluation": {
        "score": 74,
        "feedback": "Good core understanding. Be more specific about time complexity and mention edge cases such as expired tokens.",
    },
}
