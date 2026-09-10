# CareerAI Deployment Checklist

- [ ] GitHub repository created and code pushed
- [ ] Supabase database created (database/schema.sql executed in SQL Editor)
- [ ] Supabase Storage bucket `resumes` created (private)
- [ ] Gemini API key created at https://aistudio.google.com/app/apikey
- [ ] Backend deployed to Render (start cmd uses $PORT)
- [ ] GET https://YOUR-BACKEND.onrender.com/health returns {"status":"healthy"}
- [ ] Frontend deployed to Vercel (Vite, dist output)
- [ ] Vercel env var VITE_API_URL = Render backend URL
- [ ] Render env var FRONTEND_URL = Vercel frontend URL (CORS)
- [ ] Signup / login working
- [ ] Resume upload (PDF/DOCX, <=5MB) working
- [ ] AI resume analysis working
- [ ] Job matching working
- [ ] Career roadmap working
- [ ] Interview simulator working
- [ ] Demo mode verified (DEMO_MODE=true still returns data)
- [ ] Mobile UI tested
- [ ] Repo scanned: no API keys, no localhost URLs, no secrets
