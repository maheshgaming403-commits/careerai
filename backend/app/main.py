import hashlib
import io
import os
import uuid

from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.demo_data import (
    DEMO_INTERVIEW, DEMO_JOB_MATCH, DEMO_PROJECTS, DEMO_RESUME_ANALYSIS,
    DEMO_ROADMAP, DEMO_SKILLS_ANALYSIS,
)
from app.gemini import ask_gemini

load_dotenv()

app = FastAPI(title="CareerAI API")
@app.get("/")
def read_root():
    return {"status": "Server is awake and running!"}
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # This matches your default Vite frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", # Keep this for local testing
        "https://careerai-z1ew.vercel.app" # Replace with your exact Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- storage (Supabase if configured, in-memory fallback for demo) ----------
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
_sb: Client = create_client(url, key)

try:
    if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"):
        from supabase import create_client
        _sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
except Exception:
    _sb = None


def clean_error(message: str):
    return {"success": False, "message": message}


# ---------- auth ----------
class AuthBody(BaseModel):
    name: str | None = None
    email: EmailStr
    password: str


def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def get_user(authorization: str | None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required.")
    token = authorization.split(" ", 1)[1]
    uid = _sessions.get(token)
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid or expired session.")
    return uid

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        response = _sb.auth.get_user(token)
        return response.user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
@app.post("/api/auth/signup")
def signup(body: AuthBody):
    email = body.email.lower()
    if email in _users:
        return clean_error("An account with this email already exists.")
    uid = str(uuid.uuid4())
    _users[email] = {"id": uid, "name": body.name or email.split("@")[0],
                     "password_hash": hash_pw(body.password)}
    if _sb:
        try:
            _sb.table("users").insert(
                {"id": uid, "email": email, "full_name": body.name}).execute()
        except Exception:
            pass  # persistence failure must not block signup
    token = str(uuid.uuid4())
    _sessions[token] = uid
    return {"success": True, "token": token,
            "user": {"id": uid, "name": _users[email]["name"], "email": email}}


@app.post("/api/auth/login")
def login(body: AuthBody):
    email = body.email.lower()
    user = _users.get(email)
    if not user or user["password_hash"] != hash_pw(body.password):
        return clean_error("Invalid email or password.")
    token = str(uuid.uuid4())
    _sessions[token] = user["id"]
    return {"success": True, "token": token,
            "user": {"id": user["id"], "name": user["name"], "email": email}}


# ---------- health ----------
@app.get("/health")
def health():
    return {"status": "healthy"}


# ---------- helpers ----------
def extract_text(contents: bytes, ext: str) -> str:
    if ext == ".pdf":
        from PyPDF2 import PdfReader
        reader = PdfReader(io.BytesIO(contents))
        return " ".join((p.extract_text() or "") for p in reader.pages)[:10000]
    from docx import Document
    doc = Document(io.BytesIO(contents))
    return "\n".join(p.text for p in doc.paragraphs)[:10000]


def save_result(uid: str, kind: str, result: dict):
    _resumes.setdefault(uid, []).append({"kind": kind, "result": result})
    if _sb:
        try:
            table = {"resume_analysis": "resume_analysis", "roadmap": "career_roadmaps"}.get(kind)
            if table:
                _sb.table(table).insert({"user_id": uid, "roadmap": result} if kind == "roadmap"
                                        else {"user_id": uid, "overall_score": result.get("overallScore", 0)}).execute()
        except Exception:
            pass  # never fail the request because persistence failed


ALLOWED_EXT = {".pdf", ".docx"}
ALLOWED_MIME = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
MAX_SIZE = 5 * 1024 * 1024


# ---------- endpoints ----------
@app.post("/api/resume/analyze")
async def analyze_resume(file: UploadFile = File(...),
                         authorization: str | None = Header(None)):
    uid = get_user(authorization)
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXT:
        return clean_error("Only PDF or DOCX files are allowed.")
    if file.content_type not in ALLOWED_MIME:
        return clean_error("Invalid file type.")
    contents = await file.read()
    if len(contents) > MAX_SIZE:
        return clean_error("File exceeds the 5 MB limit.")
    if not contents:
        return clean_error("File appears to be corrupted or empty.")
    try:
        text = extract_text(contents, ext)
    except Exception:
        return clean_error("Could not read this file. It may be corrupted.")
    if not text.strip():
        return clean_error("No readable text found in the resume.")

    if DEMO_MODE:
        save_result(uid, "resume_analysis", DEMO_RESUME_ANALYSIS)
        return {"success": True, "demo": True, "analysis": DEMO_RESUME_ANALYSIS}
    try:
        result = ask_gemini(
            "You are a career coach AI. Analyze this resume and return ONLY JSON with keys: "
            "overallScore (0-100 int), summary (string), strengths (array of strings), "
            "weaknesses (array), recommendedRoles (array), skillGaps (array). Resume:\n" + text
        )
        save_result(uid, "resume_analysis", result)
        return {"success": True, "analysis": result}
    except Exception:
        return clean_error("AI service is temporarily unavailable. Please try again.")


class SkillsBody(BaseModel):
    skills: str


@app.post("/api/skills/analyze")
def analyze_skills(body: SkillsBody, authorization: str | None = Header(None)):
    get_user(authorization)
    if DEMO_MODE:
        return {"success": True, "demo": True, "result": DEMO_SKILLS_ANALYSIS}
    try:
        return {"success": True, "result": ask_gemini(
            "Assess this skill list. Return ONLY JSON with keys: technicalSkills "
            "(array of {name, level 1-5}), softSkills (array), topGaps (array). Skills:\n"
            + body.skills)}
    except Exception:
        return clean_error("AI service is temporarily unavailable. Please try again.")


class JobBody(BaseModel):
    targetRole: str | None = None
    skills: str | None = None


@app.post("/api/job/match")
def job_match(body: JobBody, authorization: str | None = Header(None)):
    get_user(authorization)
    if DEMO_MODE:
        return {"success": True, "demo": True, "result": DEMO_JOB_MATCH}
    try:
        return {"success": True, "result": ask_gemini(
            "Given this profile, return ONLY JSON with key 'matches': an array of "
            "{title, score 0-100, missingSkills (array), advice}. 3-5 roles. Profile:\n"
            + (body.skills or body.targetRole or "general software student"))}
    except Exception:
        return clean_error("AI service is temporarily unavailable. Please try again.")


class RoadmapBody(BaseModel):
    targetRole: str
    currentSkills: str | None = None


@app.post("/api/roadmap/generate")
def generate_roadmap(body: RoadmapBody, authorization: str | None = Header(None)):
    uid = get_user(authorization)
    if DEMO_MODE:
        save_result(uid, "roadmap", DEMO_ROADMAP)
        return {"success": True, "demo": True, "result": DEMO_ROADMAP}
    try:
        result = ask_gemini(
            f"Create a 6-month learning roadmap to become a {body.targetRole}. "
            "Return ONLY JSON with keys: targetRole, steps (array of "
            "{phase, title, items (array of 3)}). Current skills:\n"
            + (body.currentSkills or "beginner"))
        save_result(uid, "roadmap", result)
        return {"success": True, "result": result}
    except Exception:
        return clean_error("AI service is temporarily unavailable. Please try again.")


class ProjectBody(BaseModel):
    skillGap: str | None = None


@app.post("/api/projects/recommend")
def recommend_projects(body: ProjectBody, authorization: str | None = Header(None)):
    get_user(authorization)
    if DEMO_MODE:
        return {"success": True, "demo": True, "result": DEMO_PROJECTS}
    try:
        return {"success": True, "result": ask_gemini(
            "Recommend 3 portfolio projects to close this skill gap. Return ONLY JSON with "
            "key 'recommendations': array of {title, difficulty, skills (array), description}. "
            "Skill gap:\n" + (body.skillGap or "general software development"))}
    except Exception:
        return clean_error("AI service is temporarily unavailable. Please try again.")


class InterviewBody(BaseModel):
    role: str | None = None
    answer: str | None = None
    questionIndex: int | None = None


@app.post("/api/interview/start")
def interview_start(body: InterviewBody, authorization: str | None = Header(None)):
    get_user(authorization)
    if DEMO_MODE:
        return {"success": True, "demo": True,
                "question": DEMO_INTERVIEW["questions"][0], "questionIndex": 0,
                "totalQuestions": len(DEMO_INTERVIEW["questions"])}
    try:
        result = ask_gemini(
            f"Generate the first interview question for a {body.role or 'software'} role. "
            "Return ONLY JSON: {{\"question\": string}}")
        return {"success": True, "question": result["question"], "questionIndex": 0,
                "totalQuestions": 5}
    except Exception:
        return clean_error("AI service is temporarily unavailable. Please try again.")


@app.post("/api/interview/evaluate")
def interview_evaluate(body: InterviewBody, authorization: str | None = Header(None)):
    get_user(authorization)
    if DEMO_MODE:
        return {"success": True, "demo": True,
                "evaluation": DEMO_INTERVIEW["sampleEvaluation"],
                "question": DEMO_INTERVIEW["questions"][min(
                    (body.questionIndex or 0) + 1,
                    len(DEMO_INTERVIEW["questions"]) - 1)],
                "questionIndex": min((body.questionIndex or 0) + 1, 4),
                "finished": (body.questionIndex or 0) + 1 >= 4}
    try:
        result = ask_gemini(
            f"Evaluate this interview answer. Return ONLY JSON: "
            f"{{\"score\": 0-100 int, \"feedback\": string}}. "
            f"Question: (follow-up #{body.questionIndex}). Answer:\n{body.answer or ''}")
        nxt = None
        if (body.questionIndex or 0) < 4:
            nxt_res = ask_gemini(
                f"Generate interview question #{(body.questionIndex or 0) + 2} for a "
                f"{body.role or 'software'} role. Return ONLY JSON: {{\"question\": string}}")
            nxt = nxt_res["question"]
        return {"success": True, "evaluation": result, "question": nxt,
                "questionIndex": (body.questionIndex or 0) + 1,
                "finished": nxt is None}
    except Exception:
        return clean_error("AI service is temporarily unavailable. Please try again.")


@app.post("/api/interview/next-question")
def interview_next(body: InterviewBody, authorization: str | None = Header(None)):
    # kept for API completeness; evaluate already returns the next question
    get_user(authorization)
    return interview_start(body, authorization)
