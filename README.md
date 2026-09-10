# CareerAI – AI Student Career & Placement Analyzer

Full-stack app: React + Vite frontend, FastAPI backend, Supabase PostgreSQL, Gemini AI.

## Architecture
User -> Vercel Frontend -> Render FastAPI Backend -> Gemini API + Supabase Database

## 1. Clone
git clone https://github.com/YOUR_USERNAME/careerai.git && cd careerai

## 2. Install frontend
cd frontend && npm install

## 3. Install backend
cd ../backend
python -m venv .venv && source .venv/bin/activate   (Windows: .venv\Scripts\activate)
pip install -r requirements.txt

## 4. Environment variables
cp backend/.env.example backend/.env          (fill in real values)
cp frontend/.env.example frontend/.env.local  (use http://localhost:8000 locally)

Backend .env: GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY, FRONTEND_URL, DEMO_MODE
Frontend .env.local: VITE_API_URL

## 5. Supabase
1. Create a project at supabase.com
2. SQL Editor -> paste database/schema.sql -> Run
3. Storage -> New bucket -> name it `resumes`, keep private

## 6. Gemini API
Get a key at https://aistudio.google.com/app/apikey -> put it in backend/.env ONLY.
No Gemini key yet? Set DEMO_MODE=true and the whole app works with sample data.

## 7. Run locally
Terminal 1: cd backend && uvicorn app.main:app --reload --port 8000
Terminal 2: cd frontend && npm run dev
Open http://localhost:5173

## 8. Deploy backend to Render
Render -> New Web Service -> this repo -> root dir `backend`, Python
Build: pip install -r requirements.txt
Start: uvicorn app.main:app --host 0.0.0.0 --port $PORT
Env vars: GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY, FRONTEND_URL, DEMO_MODE
Verify: https://YOUR-BACKEND.onrender.com/health

## 9. Deploy frontend to Vercel
Vercel -> Add New Project -> this repo -> root dir `frontend`, framework Vite
Build: npm run build   Output: dist
Env var: VITE_API_URL=https://YOUR-BACKEND.onrender.com

## 10. Connect
Set Render FRONTEND_URL to your Vercel URL, Vercel VITE_API_URL to your Render URL.
Redeploy both. No URLs are hardcoded, so a future custom domain only needs these
two env vars updated.

## Security
Never commit .env files. Never put GEMINI_API_KEY in frontend code.
Render's filesystem is ephemeral -> resumes belong in Supabase Storage.
